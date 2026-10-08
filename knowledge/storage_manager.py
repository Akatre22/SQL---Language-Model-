"""
Storage & Database Manager for Tiny SQL LLM.
Orchestrates:
1. PostgreSQL for structured enterprise data & operational execution.
2. Supabase Storage for unstructured datasets, PDF textbooks, and raw documents.
3. Vector Management (PgVector / ChromaDB / Supabase Vectors).
"""

import os
import sys
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import URL

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

def load_env():
    """Loads environment variables from .env file."""
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

load_env()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "SQL- Language Model")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xuijiuimspzeavdytoee.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET", "sql-unstructured-knowledge")

class DatabaseStorageManager:
    def __init__(self):
        self.pg_engine = None
        self._init_postgres()

    def _init_postgres(self):
        try:
            db_url = URL.create(
                drivername="postgresql+psycopg2",
                username=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB
            )
            self.pg_engine = create_engine(db_url)
            with self.pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print(f"[OK] Connected to PostgreSQL Database: '{POSTGRES_DB}'")
        except Exception as e:
            print(f"[!] Warning: PostgreSQL connection failed: {e}")

    def sync_enterprise_schema_to_postgres(self):
        """Creates standard enterprise tables in PostgreSQL if they do not exist."""
        if not self.pg_engine:
            return False

        ddl = """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE,
            region VARCHAR(50) NOT NULL,
            segment VARCHAR(50) NOT NULL,
            join_date DATE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(150) NOT NULL,
            category VARCHAR(50) NOT NULL,
            unit_price NUMERIC(10,2) NOT NULL,
            stock_quantity INT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS departments (
            department_id SERIAL PRIMARY KEY,
            dept_name VARCHAR(100) NOT NULL,
            location VARCHAR(100) NOT NULL,
            budget NUMERIC(15,2) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS employees (
            emp_id SERIAL PRIMARY KEY,
            emp_name VARCHAR(150) NOT NULL,
            department_id INT REFERENCES departments(department_id),
            salary NUMERIC(12,2) NOT NULL,
            hire_date DATE NOT NULL,
            job_title VARCHAR(100) NOT NULL,
            status VARCHAR(20) DEFAULT 'ACTIVE'
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES customers(customer_id),
            order_date DATE NOT NULL,
            total_amount NUMERIC(12,2) NOT NULL,
            status VARCHAR(30) NOT NULL,
            payment_method VARCHAR(50) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            item_id SERIAL PRIMARY KEY,
            order_id INT REFERENCES orders(order_id),
            product_id INT REFERENCES products(product_id),
            quantity INT NOT NULL,
            item_price NUMERIC(10,2) NOT NULL
        );
        """
        try:
            with self.pg_engine.connect() as conn:
                conn.execute(text(ddl))
                conn.commit()
                print("[OK] PostgreSQL enterprise schema verified and synchronized.")
            return True
        except Exception as e:
            print(f"[!] PostgreSQL schema sync error: {e}")
            return False

    def list_postgres_tables(self) -> List[str]:
        """Returns list of public tables in PostgreSQL."""
        if not self.pg_engine:
            return []
        try:
            inspector = inspect(self.pg_engine)
            return inspector.get_table_names(schema="public")
        except Exception as e:
            print(f"[!] Failed to list PostgreSQL tables: {e}")
            return []

    # Supabase Unstructured Storage Operations
    def supabase_request(self, endpoint: str, method: str = "GET", data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        """Sends authenticated HTTP request to Supabase API."""
        url = f"{SUPABASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        req_headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY}"
        }
        if headers:
            req_headers.update(headers)

        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            if content:
                try:
                    return json.loads(content.decode("utf-8"))
                except Exception:
                    return content
            return None

    def ensure_supabase_bucket(self, bucket_name: str = "sql-unstructured-knowledge") -> bool:
        """Ensures that the target unstructured storage bucket exists in Supabase."""
        try:
            buckets = self.supabase_request("storage/v1/bucket")
            existing_names = [b.get("id") or b.get("name") for b in (buckets or [])]
            if bucket_name not in existing_names:
                payload = json.dumps({"id": bucket_name, "name": bucket_name, "public": True}).encode("utf-8")
                self.supabase_request("storage/v1/bucket", method="POST", data=payload, headers={"Content-Type": "application/json"})
                print(f"[OK] Created Supabase Storage Bucket: '{bucket_name}'")
            else:
                print(f"[OK] Supabase Storage Bucket '{bucket_name}' already exists.")
            return True
        except Exception as e:
            print(f"[!] Supabase bucket check error: {e}")
            return False

    def upload_unstructured_document(self, bucket_name: str, file_path: Path, remote_file_name: Optional[str] = None) -> bool:
        """Uploads a local unstructured file (PDF, TXT, JSON, MD) to Supabase Storage."""
        if not file_path.exists():
            print(f"[!] File not found: {file_path}")
            return False

        remote_name = remote_file_name or file_path.name
        content_type = "application/octet-stream"
        if file_path.suffix == ".pdf":
            content_type = "application/pdf"
        elif file_path.suffix in [".json", ".jsonl"]:
            content_type = "application/json"
        elif file_path.suffix in [".txt", ".md"]:
            content_type = "text/plain"

        try:
            with open(file_path, "rb") as f:
                data = f.read()

            endpoint = f"storage/v1/object/{bucket_name}/{remote_name}"
            self.supabase_request(endpoint, method="POST", data=data, headers={"Content-Type": content_type, "x-upsert": "true"})
            print(f"[OK] Uploaded '{file_path.name}' to Supabase Storage [{bucket_name}].")
            return True
        except Exception as e:
            print(f"[!] Failed to upload '{file_path.name}' to Supabase: {e}")
            return False

if __name__ == "__main__":
    mgr = DatabaseStorageManager()
    mgr.sync_enterprise_schema_to_postgres()
    tables = mgr.list_postgres_tables()
    print(f"Current PostgreSQL Tables: {tables}")
    mgr.ensure_supabase_bucket("sql-unstructured-knowledge")
