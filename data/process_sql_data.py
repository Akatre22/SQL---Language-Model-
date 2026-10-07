"""
Comprehensive SQL Data Processing Pipeline.
Extracts, cleans, formats, and integrates data from 7 GitHub repositories and synthetic SQL generators.

Produces:
- data/train.jsonl (90% split for fine-tuning / instruction tuning)
- data/val.jsonl (10% split for validation)
- data/corpus.txt (full raw corpus for tokenizer training)
"""

import os
import re
import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Set

# Fix windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEED = 42
random.seed(SEED)

DATA_DIR = Path(__file__).resolve().parent
RAW_REPOS_DIR = DATA_DIR / "raw_repos"
TRAIN_FILE = DATA_DIR / "train.jsonl"
VAL_FILE = DATA_DIR / "val.jsonl"
CORPUS_FILE = DATA_DIR / "corpus.txt"

from data_generator import generate_synthetic_sql_samples
from process_pdf_1 import generate_pdf_1_samples
from process_pdf_2 import generate_pdf_2_samples
from process_pdf_3 import generate_pdf_3_samples
from process_pdf_4 import generate_pdf_4_samples
from process_pdf_5 import generate_pdf_5_samples

def clean_sql(query: str) -> str:
    """Normalize whitespace and strip inline comments."""
    lines = []
    for line in query.split("\n"):
        line_str = line.strip()
        if line_str.startswith("--") or line_str.startswith("//"):
            continue
        if line_str:
            lines.append(line)
    return "\n".join(lines).strip()

def extract_from_markdown(md_text: str, file_path: str) -> List[Dict[str, str]]:
    """Extract SQL snippets and explanations from markdown tutorials."""
    samples = []
    # Match markdown headers followed by optional text and ```sql ... ```
    pattern = re.compile(r'(#{1,4}\s+[^\n]+)([\s\S]*?)```sql\s*([\s\S]*?)```', re.IGNORECASE)
    
    for match in pattern.finditer(md_text):
        header = match.group(1).strip("# \t\r\n")
        context = match.group(2).strip()
        sql_code = match.group(3).strip()
        
        # Filter out trivial or excessively long snippets
        if len(sql_code) < 12 or len(sql_code) > 1800:
            continue
            
        clean_ctx = re.sub(r'\s+', ' ', context).strip()
        if len(clean_ctx) > 250:
            clean_ctx = clean_ctx[:250] + "..."
            
        # 1. Text-to-SQL
        prompt_t2s = f"Write a SQL query for: {header}."
        if clean_ctx:
            prompt_t2s += f" Context: {clean_ctx}"
            
        res_t2s = f"```sql\n{sql_code}\n```"
        samples.append({
            "instruction": prompt_t2s,
            "response": res_t2s,
            "output": res_t2s,
            "domain": "sql",
            "task": "text_to_sql",
            "source": Path(file_path).name
        })
        
        # 2. SQL Explanation
        prompt_exp = f"Explain the logic of this SQL query:\n```sql\n{sql_code}\n```"
        explanation = f"### Purpose: {header}\n\n"
        if clean_ctx:
            explanation += f"{clean_ctx}\n\n"
        explanation += "### SQL Breakdown:\n"
        sql_upper = sql_code.upper()
        if "JOIN" in sql_upper:
            explanation += "- Merges data across relational tables using JOIN conditions.\n"
        if "GROUP BY" in sql_upper:
            explanation += "- Aggregates dataset records using GROUP BY and summary functions.\n"
        if "OVER" in sql_upper:
            explanation += "- Evaluates analytical computations using Window Functions.\n"
        if "WHERE" in sql_upper:
            explanation += "- Applies filtering predicates to narrow the row selection.\n"
        if "ORDER BY" in sql_upper:
            explanation += "- Sorts the final result set according to specified ordering columns.\n"
        if "WITH" in sql_upper:
            explanation += "- Employs Common Table Expressions (CTEs) for modular query execution.\n"
            
        samples.append({
            "instruction": prompt_exp,
            "response": explanation.strip(),
            "output": explanation.strip(),
            "domain": "sql",
            "task": "sql_explanation",
            "source": Path(file_path).name
        })

    return samples

def extract_from_sql_file(sql_text: str, file_path: str) -> List[Dict[str, str]]:
    """Extract individual statements and commentary from .sql files."""
    samples = []
    statements = sql_text.split(";")
    
    for stmt in statements:
        stmt_clean = stmt.strip()
        if not stmt_clean:
            continue
            
        lines = stmt_clean.split("\n")
        comments = []
        code_lines = []
        
        for l in lines:
            ls = l.strip()
            if ls.startswith("--"):
                comments.append(ls.lstrip("- \t"))
            else:
                code_lines.append(l)
                
        code = "\n".join(code_lines).strip()
        comment_desc = " ".join(comments).strip()
        
        if 15 <= len(code) <= 1500:
            target_desc = comment_desc if comment_desc else f"Execute SQL operations from {Path(file_path).stem.replace('_', ' ')}"
            samples.append({
                "instruction": f"Provide the SQL query to {target_desc}.",
                "response": f"```sql\n{code};\n```",
                "output": f"```sql\n{code};\n```",
                "domain": "sql",
                "task": "text_to_sql",
                "source": Path(file_path).name
            })
            
    return samples

def collect_repo_samples(raw_dir: Path) -> List[Dict[str, str]]:
    all_samples = []
    if not raw_dir.exists():
        print(f"[!] Directory {raw_dir} does not exist.")
        return all_samples
        
    for path in raw_dir.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file():
            suffix = path.suffix.lower()
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if suffix in [".md", ".markdown"]:
                    all_samples.extend(extract_from_markdown(content, str(path)))
                elif suffix == ".sql":
                    all_samples.extend(extract_from_sql_file(content, str(path)))
            except Exception:
                pass
                
    return all_samples

def build_pure_sql_dataset():
    print("[*] Starting pure SQL dataset consolidation...")
    
    # 1. Collect from 7 GitHub Repos
    repo_samples = collect_repo_samples(RAW_REPOS_DIR)
    print(f"[+] Collected {len(repo_samples)} samples from 7 cloned GitHub repos.")
    
    # 2. Collect Synthetic SQL Data
    synthetic_samples = generate_synthetic_sql_samples(count=4000)
    for s in synthetic_samples:
        if "response" not in s and "output" in s:
            s["response"] = s["output"]
    print(f"[+] Generated {len(synthetic_samples)} synthetic SQL samples.")
    
    # 3. Collect PDF Samples
    pdf1_samples = generate_pdf_1_samples()
    pdf2_samples = generate_pdf_2_samples()
    pdf3_samples = generate_pdf_3_samples()
    pdf4_samples = generate_pdf_4_samples()
    pdf5_samples = generate_pdf_5_samples()
    print(f"[+] Loaded {len(pdf1_samples)} structured samples from PDF 1 (Sanjeev RDBMS/SQL).")
    print(f"[+] Loaded {len(pdf2_samples)} structured samples from PDF 2 (365 Data Science SQL Basics).")
    print(f"[+] Loaded {len(pdf3_samples)} structured samples from PDF 3 (NCERT SQL & RDBMS keip108).")
    print(f"[+] Loaded {len(pdf4_samples)} structured samples from PDF 4 (IBM Enterprise SQL rbafy).")
    print(f"[+] Loaded {len(pdf5_samples)} structured samples from PDF 5 (McGraw-Hill SQL Complete Reference).")
    
    # 4. Merge & Deduplicate
    all_samples = repo_samples + synthetic_samples + pdf1_samples + pdf2_samples + pdf3_samples + pdf4_samples + pdf5_samples
    random.shuffle(all_samples)
    
    seen: Set[str] = set()
    unique_samples = []
    for item in all_samples:
        inst = item["instruction"].strip().lower()
        if inst not in seen and len(inst) > 5:
            seen.add(inst)
            unique_samples.append(item)
            
    total = len(unique_samples)
    print(f"[✓] Total unique pure SQL samples: {total}")
    
    # 4. Split 90% Train / 10% Val
    split_idx = int(total * 0.90)
    train_data = unique_samples[:split_idx]
    val_data = unique_samples[split_idx:]
    
    # Write train.jsonl
    with open(TRAIN_FILE, "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    # Write val.jsonl
    with open(VAL_FILE, "w", encoding="utf-8") as f:
        for item in val_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    # Write corpus.txt
    with open(CORPUS_FILE, "w", encoding="utf-8") as f:
        for item in unique_samples:
            f.write(f"### Question:\n{item['instruction']}\n\n### Answer:\n{item['response']}\n\n<|endoftext|>\n\n")
            
    print(f"[SUCCESS] Dataset exported:")
    print(f"  - Train: {TRAIN_FILE} ({len(train_data)} records)")
    print(f"  - Val:   {VAL_FILE} ({len(val_data)} records)")
    print(f"  - Corpus: {CORPUS_FILE} ({os.path.getsize(CORPUS_FILE) / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    build_pure_sql_dataset()
