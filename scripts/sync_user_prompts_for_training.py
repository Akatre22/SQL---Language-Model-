"""
User Prompt Active Learning & Training Data Pipeline.
1. Extracts logged user interactions from PostgreSQL (user_prompt_telemetry).
2. Synthesizes schema-conditioned SFT training pairs from successful user queries.
3. Automatically syncs and persists active learning datasets to Supabase Cloud Storage.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from knowledge.prompt_telemetry import PromptTelemetryLogger
from knowledge.storage_manager import DatabaseStorageManager
from sqlalchemy import text

def run_continuous_learning_sync():
    print("=" * 70)
    print("🧠 CONTINUOUS LEARNING: USER PROMPTS -> TRAINING DATASET SYNC")
    print("=" * 70)

    mgr = DatabaseStorageManager()
    logger = PromptTelemetryLogger(db_manager=mgr)

    if not mgr.pg_engine:
        print("[!] Error: PostgreSQL is not connected.")
        return

    # 1. Fetch telemetry statistics
    with mgr.pg_engine.connect() as conn:
        total_logged = conn.execute(text("SELECT COUNT(*) FROM user_prompt_telemetry;")).scalar()
        total_successful = conn.execute(text("SELECT COUNT(*) FROM user_prompt_telemetry WHERE execution_success = TRUE;")).scalar()
        intent_breakdown = conn.execute(text("SELECT intent, COUNT(*) FROM user_prompt_telemetry GROUP BY intent;")).fetchall()

    print(f"\n📊 Telemetry Database Status (PostgreSQL):")
    print(f"  • Total User Interactions Logged: {total_logged}")
    print(f"  • Successful Executions / Answers: {total_successful}")
    print(f"  • Breakdown by Intent:")
    for intent_name, count in intent_breakdown:
        print(f"     - {intent_name}: {count} queries")

    # 2. Export & Sync SFT Dataset to Supabase Cloud
    print("\n📦 Generating Active Learning Dataset & Syncing to Supabase...")
    sync_res = logger.export_and_sync_training_data(min_length=3)

    if sync_res.get("success"):
        print(f"  [✓] Successfully synced {sync_res.get('total_records')} training pairs to:")
        print(f"      {sync_res.get('destination')}")
    else:
        print(f"  [!] Sync failed: {sync_res.get('error')}")

    print("\n" + "=" * 70)
    print("🎉 Pipeline Sync Complete! All user data is now staged for model retraining.")
    print("=" * 70)

if __name__ == "__main__":
    run_continuous_learning_sync()
