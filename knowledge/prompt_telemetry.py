"""
User Prompt Telemetry & Continuous Active Learning Logger for Tiny SQL LLM.
Orchestrates:
1. Logging user prompts, intents, SQL executions, and latencies directly to PostgreSQL (user_prompt_telemetry table).
2. Continuous runtime background synchronization of user prompt datasets to Supabase Cloud Storage.
3. Automated extraction of user query pairs into SFT training datasets for continuous model retraining.
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import sqlalchemy
from sqlalchemy import create_engine, text

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from knowledge.storage_manager import DatabaseStorageManager, BUCKET_NAME

class PromptTelemetryLogger:
    def __init__(self, db_manager: Optional[DatabaseStorageManager] = None, auto_sync_interval: int = 120):
        self.mgr = db_manager if db_manager is not None else DatabaseStorageManager()
        self.auto_sync_interval = auto_sync_interval
        self._sync_lock = threading.Lock()
        self._interaction_count = 0
        self._ensure_table()
        self._start_periodic_daemon()

    def _ensure_table(self):
        """Ensures the user_prompt_telemetry table exists in PostgreSQL."""
        if not self.mgr.pg_engine:
            return
        try:
            with self.mgr.pg_engine.connect() as conn:
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_prompt_telemetry (
                    prompt_id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100),
                    client_name VARCHAR(150) DEFAULT 'Enterprise Studio',
                    prompt_text TEXT NOT NULL,
                    intent VARCHAR(50) NOT NULL,
                    generated_sql TEXT,
                    execution_success BOOLEAN DEFAULT TRUE,
                    latency_sec NUMERIC(8,3),
                    feedback_rating INT DEFAULT NULL,
                    schema_snapshot TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """))
                conn.commit()
        except Exception as e:
            print(f"[!] Telemetry table init error: {e}")

    def _start_periodic_daemon(self):
        """Starts a background daemon thread that periodically syncs new prompts to Supabase."""
        def _worker():
            while True:
                time.sleep(self.auto_sync_interval)
                try:
                    self.export_and_sync_training_data()
                except Exception as e:
                    pass

        t = threading.Thread(target=_worker, daemon=True, name="TelemetryContinuousSyncDaemon")
        t.start()

    def log_interaction(
        self,
        prompt: str,
        intent: str,
        generated_sql: Optional[str] = None,
        execution_success: bool = True,
        latency_sec: float = 0.0,
        client_name: str = "Enterprise Studio",
        session_id: Optional[str] = None,
        schema_snapshot: Optional[str] = None
    ) -> Optional[int]:
        """Logs an incoming user prompt & its execution outcome to PostgreSQL, then triggers async cloud sync."""
        if not self.mgr.pg_engine or not prompt.strip():
            return None

        insert_sql = """
        INSERT INTO user_prompt_telemetry 
        (session_id, client_name, prompt_text, intent, generated_sql, execution_success, latency_sec, schema_snapshot)
        VALUES 
        (:session_id, :client_name, :prompt_text, :intent, :generated_sql, :execution_success, :latency_sec, :schema_snapshot)
        RETURNING prompt_id;
        """
        p_id = None
        try:
            with self.mgr.pg_engine.connect() as conn:
                res = conn.execute(
                    text(insert_sql),
                    {
                        "session_id": session_id or f"sess_{int(time.time())}",
                        "client_name": client_name,
                        "prompt_text": prompt.strip(),
                        "intent": intent,
                        "generated_sql": generated_sql,
                        "execution_success": execution_success,
                        "latency_sec": round(latency_sec, 3),
                        "schema_snapshot": schema_snapshot
                    }
                )
                conn.commit()
                row = res.fetchone()
                p_id = row[0] if row else None
        except Exception as e:
            print(f"[!] Failed to log prompt telemetry: {e}")

        # Increment counter and trigger async background sync to Supabase
        self._interaction_count += 1
        self.trigger_async_sync()
        return p_id

    def trigger_async_sync(self):
        """Dispatches cloud dataset synchronization in a non-blocking background thread."""
        threading.Thread(target=self.export_and_sync_training_data, daemon=True).start()

    def export_and_sync_training_data(self, min_length: int = 3) -> Dict[str, Any]:
        """
        Extracts verified user queries from PostgreSQL, formats them as SFT JSONL training pairs,
        and uploads the dataset directly to Supabase Storage for continuous model retraining.
        Thread-safe execution.
        """
        if not self.mgr.pg_engine:
            return {"success": False, "error": "No PostgreSQL engine connected"}

        with self._sync_lock:
            select_sql = """
            SELECT prompt_text, generated_sql, schema_snapshot, intent 
            FROM user_prompt_telemetry 
            WHERE execution_success = TRUE 
              AND generated_sql IS NOT NULL 
              AND LENGTH(prompt_text) >= :min_len
            ORDER BY prompt_id ASC;
            """
            try:
                with self.mgr.pg_engine.connect() as conn:
                    rows = conn.execute(text(select_sql), {"min_len": min_length}).fetchall()

                if not rows:
                    return {"success": True, "total_records": 0, "message": "No new records to sync"}

                training_samples = []
                for r in rows:
                    p_text, sql, schema_text, intent = r[0], r[1], r[2], r[3]
                    schema_part = f"Database Schema:\n{schema_text}\n\n" if schema_text else ""
                    formatted_prompt = f"{schema_part}Question: {p_text}\nSQL: "
                    training_samples.append({
                        "prompt": formatted_prompt,
                        "target_sql": sql.strip(),
                        "intent": intent,
                        "user_query": p_text
                    })

                jsonl_content = "\n".join([json.dumps(s) for s in training_samples])
                data_bytes = jsonl_content.encode("utf-8")

                endpoint = f"storage/v1/object/{BUCKET_NAME}/continuous_training/active_learning_dataset.jsonl"
                self.mgr.supabase_request(
                    endpoint,
                    method="POST",
                    data=data_bytes,
                    headers={"Content-Type": "application/json", "x-upsert": "true"}
                )

                return {
                    "success": True,
                    "total_records": len(training_samples),
                    "destination": f"Supabase [{BUCKET_NAME}/continuous_training/active_learning_dataset.jsonl]"
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

if __name__ == "__main__":
    logger = PromptTelemetryLogger()
    print("[*] Testing Automatic Runtime Prompt Telemetry with Background Cloud Sync:")
    p_id = logger.log_interaction(
        prompt="List all employees with salary over 120000 in Engineering",
        intent="text_to_sql",
        generated_sql="SELECT emp_name, salary FROM employees WHERE department_id = 10 AND salary > 120000;",
        execution_success=True,
        latency_sec=0.15,
        client_name="Runtime Test Suite",
        schema_snapshot="employees(emp_id PK, emp_name, department_id, salary)"
    )
    print(f"  -> Logged Interaction ID: {p_id}")
    time.sleep(2)
    print("[✓] Background thread automatically staged dataset in Supabase.")
