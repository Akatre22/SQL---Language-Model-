"""
End-to-End Schema Adaptation and Fine-Tuning Pipeline for Tiny SQL LLM.
Workflow:
1. Connects to the user's database URI & introspects full schema metadata.
2. Builds an isolated Shadow Replica Sandbox database for safe AST verification.
3. Synthesizes 100+ domain-specific Q&A pairs covering all tables, columns, and foreign keys.
4. Ingests schema DDL and query templates into ChromaDB vector memory.
5. Runs a rapid micro fine-tuning cycle on Tiny SLM weights.
6. Saves the adapted checkpoint and verifies real data querying on the live database.
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import torch
from torch.utils.data import DataLoader
from agent_engine.schema_adapter import SchemaAdapter
from tokenizer.tokenizer_wrapper import TinyTokenizer
from model.config import TinyLLMConfig
from model.transformer import TinyLLM
from training.dataset import InstructionDataset

def adapt_and_train_on_schema(
    db_uri: str,
    epochs: int = 2,
    batch_size: int = 4,
    learning_rate: float = 3e-4,
    checkpoint_in: Optional[str] = None,
    checkpoint_out: Optional[str] = None,
    device: Optional[str] = None
):
    t_global_start = time.time()
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    
    print("\n" + "=" * 70)
    print("🚀 TINY SQL LLM: AUTOMATED SCHEMA ADAPTATION & TRAINING PIPELINE")
    print("=" * 70)
    print(f"[*] Target Database URI: {db_uri}")
    print(f"[*] Compute Device: {device}")

    # 1. Initialize Schema Adapter & Connect
    print("\n[Step 1/5] Introspecting database schema and relationships...")
    adapter = SchemaAdapter(connection_uri=db_uri)
    catalog = adapter.catalog
    if not catalog or not catalog.tables:
        print("[!] Error: No tables found in target database.")
        return False

    print(f"[+] Successfully introspected database: '{catalog.database_name}'")
    print(f"[+] Discovered {len(catalog.tables)} tables:")
    for tname, tmeta in catalog.tables.items():
        print(f"    - {tname} ({len(tmeta.columns)} cols, {len(tmeta.foreign_keys)} FKs)")

    # 2. Build Shadow Replica Sandbox
    print("\n[Step 2/5] Creating isolated Shadow Replica Sandbox with synthetic seed data...")
    replica_box, replica_path = adapter.build_replica_sandbox()
    print(f"[+] Replica Sandbox created at: {replica_path}")

    # 3. Synthesize 100+ Schema-Specific Training Pairs
    print("\n[Step 3/5] Synthesizing schema-conditioned training dataset...")
    synthetic_pairs = adapter.synthesize_training_pairs(samples_per_table=15)
    print(f"[+] Generated {len(synthetic_pairs)} verified SQL training pairs.")

    # Save to staging JSONL file
    staged_data_dir = PROJECT_ROOT / "data" / "schema_staged"
    os.makedirs(staged_data_dir, exist_ok=True)
    staged_file = staged_data_dir / f"training_pairs_{catalog.database_name.replace(' ', '_')}.jsonl"
    
    with open(staged_file, "w", encoding="utf-8") as f:
        for p in synthetic_pairs:
            f.write(json.dumps(p) + "\n")
    print(f"[+] Staged training data written to: {staged_file}")

    # 4. Ingest into ChromaDB Vector Store
    print("\n[Step 4/5] Ingesting schema DDL into ChromaDB Vector Knowledge...")
    ingested_count = adapter.ingest_into_vector_knowledge()
    print(f"[+] Upserted {ingested_count} schema documents into ChromaDB.")

    # 5. Micro Fine-Tuning SLM on Schema Vocabulary
    print("\n[Step 5/5] Fine-tuning Tiny SLM on new schema vocabulary...")
    
    # Load tokenizer
    tokenizer = TinyTokenizer()
    
    # Load base checkpoint
    if checkpoint_in is None:
        checkpoint_in = str(PROJECT_ROOT / "training" / "checkpoints" / "stage3_hard_negatives_checkpoint.pt")
        
    print(f"[*] Loading base model weights from: {checkpoint_in}")
    ckpt = torch.load(checkpoint_in, map_location=device, weights_only=False)
    
    cfg_dict = ckpt.get("config", {
        "vocab_size": 4096,
        "max_seq_len": 512,
        "d_model": 256,
        "num_heads": 8,
        "num_layers": 8,
        "d_ff": 1024,
        "dropout": 0.05
    })
    
    if isinstance(cfg_dict, dict):
        config = TinyLLMConfig(**cfg_dict)
    elif hasattr(cfg_dict, "__dict__"):
        config = cfg_dict
    else:
        config = TinyLLMConfig()
        
    model = TinyLLM(config).to(device)
    state_dict = ckpt.get("model_state_dict", ckpt)
    model.load_state_dict(state_dict)
    model.train()

    # Create dataset and dataloader
    dataset = InstructionDataset(str(staged_file), tokenizer=tokenizer, max_seq_len=config.max_seq_len)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)

    print(f"[*] Training for {epochs} epoch(s), batch_size={batch_size}, total batches={len(dataloader)}...")
    for epoch in range(1, epochs + 1):
        epoch_loss = 0.0
        batches = 0
        t_epoch_start = time.time()
        for x, y in dataloader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            _, loss = model(x, targets=y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            epoch_loss += loss.item()
            batches += 1

        avg_loss = epoch_loss / max(1, batches)
        dur = round(time.time() - t_epoch_start, 2)
        print(f"    [Epoch {epoch}/{epochs}] Average Loss: {avg_loss:.4f} ({dur}s)")

    # Save adapted checkpoint
    if checkpoint_out is None:
        ckpt_dir = PROJECT_ROOT / "training" / "checkpoints"
        os.makedirs(ckpt_dir, exist_ok=True)
        checkpoint_out = str(ckpt_dir / "stage4_adapted_schema_checkpoint.pt")

    torch.save({
        "epoch": epochs,
        "model_state_dict": model.state_dict(),
        "config": config.__dict__ if hasattr(config, "__dict__") else config,
        "adapted_database": catalog.database_name,
        "num_adapted_tables": len(catalog.tables),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }, checkpoint_out)
    
    print(f"[+] Saved Adapted Checkpoint to: {checkpoint_out}")

    # Verify live query execution
    print("\n" + "=" * 70)
    print("✅ SCHEMA ADAPTATION COMPLETE")
    print("=" * 70)
    print(f"Total Adaptation Time: {round(time.time() - t_global_start, 2)}s")
    
    # Test dual query on live database
    sample_table = list(catalog.tables.keys())[0]
    test_sql = f"SELECT * FROM {sample_table} LIMIT 3;"
    print(f"\n[*] Testing Dual-Execution on Live DB: '{test_sql}'")
    dual_res = adapter.execute_dual(test_sql)
    print(f"    - Replica Pre-flight Check: {'PASSED ✓' if dual_res.get('replica_verified') else 'FAILED'}")
    print(f"    - Live Execution Status: {'SUCCESS ✓' if dual_res.get('success') else 'FAILED'}")
    print(f"    - Live Row Count Returned: {dual_res.get('row_count', 0)}")
    print(f"    - Live Query Latency: {dual_res.get('latency_ms', 0)}ms")
    if dual_res.get("rows"):
        print(f"    - Sample Row 1: {dual_res['rows'][0]}")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Schema Adaptation and Fine-Tuning for Tiny SQL LLM")
    parser.add_argument("--db-uri", type=str, default="postgresql://postgres:Nice123@localhost:5432/SQL- Language Model", help="Connection URI for the target database")
    parser.add_argument("--epochs", type=int, default=2, help="Number of micro fine-tuning epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Training batch size")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    args = parser.parse_args()

    adapt_and_train_on_schema(
        db_uri=args.db_uri,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )
