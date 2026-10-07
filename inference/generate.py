"""
Inference & Text Generation Engine for Tiny SQL LLM
Supports loading modern RoPE + SwiGLU + GQA checkpoints,
Execution-Guided Multi-Candidate Generation (Best-of-N),
and Self-Consistency Consensus Scoring (Item 19).
"""

import sys
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.append(str(Path(__file__).resolve().parent.parent))

import torch
import sqlglot
from model.config import TinyLLMConfig
from model.transformer import TinyLLM
from tokenizer.tokenizer_wrapper import TinyTokenizer

def get_default_checkpoint_path() -> Path:
    ckpt_dir = Path(__file__).resolve().parent.parent / "training" / "checkpoints"
    for candidate in [
        "stage3_hard_negatives_checkpoint.pt",
        "stage2_schema_sft_checkpoint.pt",
        "stage1_base_checkpoint.pt",
        "best_model.pt"
    ]:
        cand_path = ckpt_dir / candidate
        if cand_path.exists():
            return cand_path
    return ckpt_dir / "best_model.pt"

CHECKPOINT_PATH = get_default_checkpoint_path()

class TinyLLMInference:
    def __init__(self, checkpoint_path: str = None, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        ckpt_path = Path(checkpoint_path) if checkpoint_path else CHECKPOINT_PATH
        self.tokenizer = TinyTokenizer()
        
        # Default modern architecture config
        self.config = TinyLLMConfig.small(vocab_size=self.tokenizer.vocab_size, max_seq_len=512)
        self.model = TinyLLM(self.config).to(self.device)

        # Stop tokens: <|endoftext|> and </sql>
        sql_close_tok = self.tokenizer.encode("</sql>")
        self.stop_token_ids = [self.tokenizer.eot_token_id]
        if sql_close_tok:
            self.stop_token_ids.append(sql_close_tok[0])

        if ckpt_path.exists():
            print(f"[*] Loading model checkpoint from {ckpt_path} on {self.device}...")
            try:
                checkpoint = torch.load(ckpt_path, map_location=self.device, weights_only=False)
                if "config" in checkpoint and hasattr(checkpoint["config"], "d_model"):
                    self.config = checkpoint["config"]
                    self.model = TinyLLM(self.config).to(self.device)
                self.model.load_state_dict(checkpoint["model_state_dict"], strict=False)
                print(f"[+] Model successfully loaded (Epoch {checkpoint.get('epoch', '?')}, Val Loss {checkpoint.get('val_loss', 0.0):.4f})")
            except Exception as e:
                print(f"[!] Warning: Initializing modern weights ({e})")
        else:
            print(f"[!] Checkpoint not found, initializing fresh weights.")
            
        self.model.eval()

    def extract_sql(self, text: str) -> str:
        """Extracts SQL from structured XML tags, markdown blocks, or raw query text."""
        if not text:
            return ""
        # 1. If text has </sql>, extract content before </sql>
        if "</sql>" in text:
            extracted = text.split("</sql>")[0].replace("<sql>", "").strip()
            if extracted:
                return extracted
        # 2. <sql> ... </sql>
        match = re.search(r"<sql>\s*(.*?)\s*(?:</sql>|<\|endoftext\|>|$)", text, re.DOTALL | re.IGNORECASE)
        if match and match.group(1).strip():
            return match.group(1).strip()
        # 3. Markdown ```sql ... ```
        if "```" in text:
            match_code = re.search(r"```(?:sql)?\s*([\s\S]*?)```", text, re.IGNORECASE)
            if match_code and match_code.group(1).strip():
                return match_code.group(1).strip()
        # 4. Standard SQL string terminating with semicolon or end-of-text
        text_clean = text.replace("<|endoftext|>", "").strip()
        if ";" in text_clean:
            return text_clean.split(";")[0].strip() + ";"
        return text_clean

    def generate_structured(
        self,
        question: str,
        schema: str = None,
        dialect: str = None,
        max_new_tokens: int = 150,
        temperature: float = 0.0,
        top_k: int = 40,
        top_p: float = 0.9,
        repetition_penalty: float = 1.25,
        no_repeat_ngram_size: int = 3
    ) -> dict:
        """
        Structured generation returning rich metadata, SQL extraction, and latency metrics.
        Supports temperature=0 fast greedy decoding.
        """
        t0 = time.time()
        
        if schema:
            dialect_tag = f"<dialect>{dialect}</dialect>\n" if dialect else ""
            prompt = f"{dialect_tag}<schema>\n{schema.strip()}\n</schema>\n\n<question>\n{question.strip()}\n</question>\n\n<sql>\n"
        else:
            prompt = f"### Question:\n{question.strip()}\n\n### Answer:\n"
            
        tokens = self.tokenizer.encode(prompt)
        input_ids = torch.tensor([tokens], dtype=torch.long, device=self.device)
        
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                no_repeat_ngram_size=no_repeat_ngram_size,
                eos_token_id=self.stop_token_ids
            )
            
        latency = round(time.time() - t0, 4)
        new_token_ids = output_ids[0][len(tokens):].tolist()
        raw_output = self.tokenizer.decode(new_token_ids, skip_special_tokens=False)
        
        sql_candidate = self.extract_sql(raw_output)
        clean_response = self.tokenizer.decode(new_token_ids, skip_special_tokens=True).strip()

        return {
            "question": question,
            "schema_provided": bool(schema),
            "dialect": dialect or "ansi/sqlite",
            "sql": sql_candidate,
            "raw_text": clean_response,
            "tokens_generated": len(new_token_ids),
            "latency_sec": latency,
            "deterministic": (temperature == 0.0)
        }

    def generate_candidates(
        self,
        question: str,
        schema: Optional[str] = None,
        dialect: Optional[str] = None,
        k: int = 4,
        temperature: float = 0.7,
        max_new_tokens: int = 150,
        db_sandbox = None
    ) -> Dict[str, Any]:
        """
        Execution-Guided Multi-Candidate Generation (Item 19).
        Samples K candidates (1 deterministic greedy + K-1 temperature-sampled),
        evaluates AST validity and sandbox execution, clusters equivalent results,
        and returns the consensus-ranked best candidate.
        """
        t0 = time.time()
        candidates: List[Dict[str, Any]] = []

        # Candidate 0: Greedy deterministic baseline
        temps = [0.0] + [temperature] * max(0, k - 1)
        temps = temps[:k]

        for i, temp in enumerate(temps):
            gen_res = self.generate_structured(
                question=question,
                schema=schema,
                dialect=dialect,
                max_new_tokens=max_new_tokens,
                temperature=temp,
                top_p=0.9 if temp > 0 else 1.0,
                top_k=40 if temp > 0 else 1
            )
            sql_str = gen_res["sql"]
            
            # Syntax validation via sqlglot
            ast_valid = False
            normalized_sql = sql_str
            ast_error = None
            try:
                if sql_str:
                    parsed = sqlglot.parse_one(sql_str, read="sqlite")
                    normalized_sql = parsed.sql(dialect="sqlite")
                    ast_valid = True
            except Exception as ex:
                ast_error = str(ex)

            # Sandbox trial execution
            exec_res = None
            exec_success = False
            exec_rows = []
            exec_cols = []
            exec_error = None
            exec_signature = None

            if db_sandbox is not None and sql_str:
                exec_res = db_sandbox.execute_query(sql_str)
                exec_success = exec_res.get("success", False)
                exec_rows = exec_res.get("rows", [])
                exec_cols = exec_res.get("columns", [])
                exec_error = exec_res.get("error")
                if exec_success:
                    # Deterministic hash of output shape and values
                    exec_signature = f"{len(exec_cols)}_{len(exec_rows)}_{str(exec_rows[:3])}"

            cand_record = {
                "candidate_idx": i,
                "temperature": temp,
                "sql": sql_str,
                "normalized_sql": normalized_sql,
                "ast_valid": ast_valid,
                "ast_error": ast_error,
                "exec_success": exec_success,
                "row_count": len(exec_rows),
                "columns": exec_cols,
                "exec_error": exec_error,
                "exec_signature": exec_signature,
                "latency_sec": gen_res["latency_sec"]
            }
            candidates.append(cand_record)

        # ------------------------------------------------------------------
        # Multi-Candidate Ranking & Consensus Aggregation
        # ------------------------------------------------------------------
        # Cluster by execution signature or normalized SQL
        clusters: Dict[str, List[int]] = {}
        for idx, c in enumerate(candidates):
            key = c["exec_signature"] if c["exec_signature"] else (c["normalized_sql"] if c["ast_valid"] else f"invalid_{idx}")
            clusters.setdefault(key, []).append(idx)

        def score_candidate(c: Dict[str, Any]) -> float:
            score = 0.0
            # 1. Execution Success
            if c["exec_success"]:
                score += 100.0
                # Non-empty results bonus
                if c["row_count"] > 0:
                    score += 20.0
            # 2. AST Validity
            if c["ast_valid"]:
                score += 30.0
            # 3. Consensus Cluster Size
            key = c["exec_signature"] if c["exec_signature"] else (c["normalized_sql"] if c["ast_valid"] else f"invalid_{c['candidate_idx']}")
            cluster_size = len(clusters.get(key, []))
            score += cluster_size * 10.0
            # 4. Greedy deterministic bias (tie-breaker)
            if c["temperature"] == 0.0:
                score += 2.0
            # 5. Brevity penalty for overly verbose hallucinations
            score -= len(c["sql"]) * 0.01
            return score

        # Rank candidates
        ranked_candidates = sorted(candidates, key=score_candidate, reverse=True)
        best_candidate = ranked_candidates[0] if ranked_candidates else candidates[0]
        
        # Calculate consensus confidence
        best_key = best_candidate["exec_signature"] if best_candidate["exec_signature"] else (best_candidate["normalized_sql"] if best_candidate["ast_valid"] else "invalid")
        consensus_count = len(clusters.get(best_key, [0]))
        consensus_confidence = round(consensus_count / max(1, k), 2)

        return {
            "question": question,
            "total_candidates": k,
            "best_sql": best_candidate["sql"],
            "best_candidate": best_candidate,
            "consensus_confidence": consensus_confidence,
            "ranked_candidates": ranked_candidates,
            "total_time_sec": round(time.time() - t0, 3)
        }

    def answer(
        self,
        question: str,
        max_new_tokens: int = 150,
        temperature: float = 0.3,
        top_k: int = 40,
        top_p: float = 0.9,
        repetition_penalty: float = 1.25,
        no_repeat_ngram_size: int = 3
    ) -> str:
        prompt = f"### Question:\n{question.strip()}\n\n### Answer:\n"
        tokens = self.tokenizer.encode(prompt)
        input_ids = torch.tensor([tokens], dtype=torch.long, device=self.device)
        
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                no_repeat_ngram_size=no_repeat_ngram_size,
                eos_token_id=self.stop_token_ids
            )
            
        raw_output = self.tokenizer.decode(output_ids[0].tolist(), skip_special_tokens=True)
        
        if "### Answer:" in raw_output:
            response = raw_output.split("### Answer:")[1].strip()
        else:
            response = raw_output.strip()
            
        return response

if __name__ == "__main__":
    bot = TinyLLMInference()
    print("[*] Testing structured generation:")
    struct_res = bot.generate_structured("Show customers from EMEA region", schema="customers(customer_id, first_name, region)")
    print(struct_res)

