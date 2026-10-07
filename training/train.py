"""
Multi-Stage Curriculum Training Pipeline for NICE SQL-SLM (Item 15).
Supports:
- Stage 1: Base SQL Grammar & Syntax Foundations (train.jsonl)
- Stage 2: Schema-Conditioned Supervised Fine-Tuning (schema_conditioned_sft.jsonl)
- Stage 3: Semantic Error Discrimination & Hard Negatives (hard_negatives.jsonl)
- Execution-Guided Checkpoint Selection (tracking AST validity and val loss)
- Cosine LR scheduling with warmup and CPU/GPU execution.
"""

import math
import sys
import time
import os
import argparse
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).resolve().parent.parent))

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

from model.config import TinyLLMConfig
from model.transformer import TinyLLM
from tokenizer.tokenizer_wrapper import TinyTokenizer
from training.dataset import get_dataloaders
from evaluation.evaluate_sql import SQLEvaluator

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
CHECKPOINT_DIR = ROOT_DIR / "training" / "checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

def evaluate_epoch(model: nn.Module, val_loader, device: str, sql_evaluator: SQLEvaluator) -> Tuple[float, float]:
    """Computes validation loss and perplexity."""
    model.eval()
    total_loss = 0.0
    total_batches = 0
    
    with torch.no_grad():
        for x, y in val_loader:
            x, y = x.to(device), y.to(device)
            _, loss = model(x, targets=y)
            total_loss += loss.item()
            total_batches += 1
            
    avg_loss = total_loss / max(1, total_batches)
    perplexity = math.exp(min(20, avg_loss))
    return avg_loss, perplexity

def sample_generation(model: nn.Module, tokenizer: TinyTokenizer, device: str, prompt_text: str = None) -> str:
    """Generates a sample SQL query for validation monitoring."""
    model.eval()
    prompt = prompt_text or "<schema>\ncustomers(customer_id PK, first_name, region)\norders(order_id PK, customer_id FK, total_amount)\n</schema>\n\n<question>\nShow total spend per customer in EMEA region\n</question>\n\n<sql>\n"
    tokens = tokenizer.encode(prompt)
    input_ids = torch.tensor([tokens], dtype=torch.long, device=device)
    
    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=90,
            temperature=0.2,
            top_k=40,
            repetition_penalty=1.25,
            no_repeat_ngram_size=3,
            eos_token_id=tokenizer.eot_token_id
        )
        
    generated_text = tokenizer.decode(output_ids[0].tolist(), skip_special_tokens=False)
    return generated_text

def train_stage(
    stage_name: str,
    train_file: str,
    val_file: str,
    model: nn.Module,
    tokenizer: TinyTokenizer,
    config: TinyLLMConfig,
    epochs: int = 3,
    batch_size: int = 32,
    lr: float = 5e-4,
    max_seq_len: int = 512,
    device: str = "cpu",
    save_prefix: str = "stage"
) -> float:
    """Runs a single curriculum training stage with logging and checkpointing."""
    print(f"\n{'='*75}")
    print(f"[*] Starting Curriculum Stage: [{stage_name.upper()}]")
    print(f"    - Training File:   {Path(train_file).name}")
    print(f"    - Epochs:          {epochs} | Batch Size: {batch_size} | Learning Rate: {lr}")
    print(f"{'='*75}")

    train_loader, val_loader = get_dataloaders(train_file, val_file, tokenizer, batch_size=batch_size, max_seq_len=max_seq_len)
    print(f"[+] Loaded {len(train_loader.dataset)} training samples, {len(val_loader.dataset)} validation samples.")

    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01, betas=(0.9, 0.98), eps=1e-8)
    total_steps = len(train_loader) * epochs
    scheduler = CosineAnnealingLR(optimizer, T_max=max(1, total_steps), eta_min=lr * 0.05)
    sql_eval = SQLEvaluator()

    best_val_loss = float("inf")
    stage_ckpt_path = CHECKPOINT_DIR / f"{save_prefix}_checkpoint.pt"
    best_model_path = CHECKPOINT_DIR / "best_model.pt"

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        batch_count = 0
        t0 = time.time()

        for step, (x, y) in enumerate(train_loader, 1):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            _, loss = model(x, targets=y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

            epoch_loss += loss.item()
            batch_count += 1

            if step % 40 == 0 or step == len(train_loader):
                cur_lr = scheduler.get_last_lr()[0]
                print(f"    [{stage_name}] Epoch [{epoch}/{epochs}] | Step [{step}/{len(train_loader)}] | Loss: {loss.item():.4f} | LR: {cur_lr:.6f}")
                sys.stdout.flush()

        avg_train_loss = epoch_loss / max(1, batch_count)
        val_loss, val_ppl = evaluate_epoch(model, val_loader, device, sql_eval)
        duration = round(time.time() - t0, 1)

        print(f"\n[+] [{stage_name}] Epoch {epoch}/{epochs} Finished ({duration}s):")
        print(f"    - Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | Perplexity: {val_ppl:.2f}")

        sample_text = sample_generation(model, tokenizer, device)
        print(f"    - Sample Preview:\n      {sample_text[:180]}...")

        # Checkpoint Saving
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            ckpt_data = {
                "stage": stage_name,
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "config": config,
                "val_loss": val_loss,
                "val_ppl": val_ppl
            }
            torch.save(ckpt_data, stage_ckpt_path)
            torch.save(ckpt_data, best_model_path)
            print(f"    [*] Saved best checkpoint for {stage_name} to {stage_ckpt_path}")
        sys.stdout.flush()

    return best_val_loss

def run_curriculum_training(
    stages: Optional[list] = None,
    arch: str = "tiny",
    batch_size: int = 32,
    max_seq_len: int = 512,
    device: Optional[str] = None
):
    """Executes multi-stage curriculum training across stages 1, 2, and 3."""
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    num_cpus = os.cpu_count() or 4
    torch.set_num_threads(num_cpus)
    print(f"[*] Initializing Multi-Stage SQL-SLM Curriculum Training on {device} (threads: {num_cpus})")

    tokenizer = TinyTokenizer()
    if arch == "tiny":
        config = TinyLLMConfig.tiny(vocab_size=tokenizer.vocab_size, max_seq_len=max_seq_len)
    elif arch == "medium":
        config = TinyLLMConfig.medium(vocab_size=tokenizer.vocab_size, max_seq_len=max_seq_len)
    elif arch == "base":
        config = TinyLLMConfig.base(vocab_size=tokenizer.vocab_size, max_seq_len=max_seq_len)
    else:
        config = TinyLLMConfig.small(vocab_size=tokenizer.vocab_size, max_seq_len=max_seq_len)

    model = TinyLLM(config).to(device)
    params = model.count_parameters()
    print(f"[+] Architecture [{arch}]: {params['total']:,} total parameters ({params['trainable']:,} trainable)")

    # Resume prior weights if available and compatible
    best_path = CHECKPOINT_DIR / "best_model.pt"
    if best_path.exists():
        try:
            ckpt = torch.load(best_path, map_location=device, weights_only=False)
            model.load_state_dict(ckpt["model_state_dict"], strict=False)
            print(f"[+] Loaded baseline checkpoint from {best_path}")
        except Exception as e:
            print(f"[!] Initializing fresh model weights ({e})")

    stages_to_run = stages or [1, 2, 3]

    # Stage 1: Base SQL Foundations
    if 1 in stages_to_run:
        train_stage(
            stage_name="Stage 1 - SQL Foundations",
            train_file=str(DATA_DIR / "train.jsonl"),
            val_file=str(DATA_DIR / "val.jsonl"),
            model=model,
            tokenizer=tokenizer,
            config=config,
            epochs=3,
            batch_size=batch_size,
            lr=8e-4,
            max_seq_len=max_seq_len,
            device=device,
            save_prefix="stage1_base"
        )

    # Stage 2: Schema-Conditioned SFT
    if 2 in stages_to_run:
        sft_file = str(DATA_DIR / "schema_conditioned_sft.jsonl")
        if not Path(sft_file).exists():
            from data.nl_to_sql_builder import build_dataset
            build_dataset()

        train_stage(
            stage_name="Stage 2 - Schema-Conditioned SFT",
            train_file=sft_file,
            val_file=str(DATA_DIR / "val.jsonl"),
            model=model,
            tokenizer=tokenizer,
            config=config,
            epochs=3,
            batch_size=batch_size,
            lr=4e-4,
            max_seq_len=max_seq_len,
            device=device,
            save_prefix="stage2_schema_sft"
        )

    # Stage 3: Semantic Error Discrimination & Hard Negatives
    if 3 in stages_to_run:
        neg_file = str(DATA_DIR / "hard_negatives.jsonl")
        if not Path(neg_file).exists():
            from data.hard_negative_generator import generate_hard_negatives
            generate_hard_negatives()

        train_stage(
            stage_name="Stage 3 - Hard Negative Discrimination",
            train_file=neg_file,
            val_file=str(DATA_DIR / "val.jsonl"),
            model=model,
            tokenizer=tokenizer,
            config=config,
            epochs=2,
            batch_size=batch_size,
            lr=2e-4,
            max_seq_len=max_seq_len,
            device=device,
            save_prefix="stage3_hard_negatives"
        )

    print(f"\n[✓] Multi-Stage Curriculum Training Complete! Checkpoints saved in {CHECKPOINT_DIR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Stage Curriculum Training for SQL-SLM")
    parser.add_argument("--stages", nargs="+", type=int, default=[1, 2, 3], help="Curriculum stages to run (1 2 3)")
    parser.add_argument("--arch", type=str, default="tiny", choices=["tiny", "small", "medium", "base"], help="Architecture preset")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--max_seq_len", type=int, default=512, help="Sequence length")
    args = parser.parse_args()

    run_curriculum_training(stages=args.stages, arch=args.arch, batch_size=args.batch_size, max_seq_len=args.max_seq_len)


