import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import URL

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

def _load_env():
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

import urllib.parse
from urllib.parse import urlparse, parse_qs, quote_plus

def normalize_connection_uri(raw: str) -> Tuple[str, str]:
    """
    Universal connection string parser and normalizer.
    Supports:
    - Snowflake (ODBC, JDBC, Go Driver DSN, .NET Driver, SQLAlchemy)
    - PostgreSQL (psycopg2, jdbc:postgresql://, postgresql://)
    - MySQL (mysql://, jdbc:mysql://)
    - Microsoft SQL Server (mssql+pyodbc://, jdbc:sqlserver://, ODBC DSN)
    - SQLite (sqlite:///)
    """
    if not raw or not isinstance(raw, str):
        return raw, "generic"

    cleaned = raw.strip()
    c_lower = cleaned.lower()

    # 1. JDBC Snowflake: jdbc:snowflake://<account>.snowflakecomputing.com/?user=...&password=...&db=...&schema=...&warehouse=...&role=...
    if c_lower.startswith("jdbc:snowflake://"):
        url_part = cleaned[len("jdbc:snowflake://"):]
        if "?" in url_part:
            host_part, query_part = url_part.split("?", 1)
        else:
            host_part, query_part = url_part, ""
        
        account = host_part.split(".snowflakecomputing.com")[0].rstrip("/")
        qs = parse_qs(query_part)
        user = qs.get("user", [""])[0]
        password = qs.get("password", [""])[0]
        db = qs.get("db", [""])[0] or qs.get("database", [""])[0]
        schema = qs.get("schema", ["PUBLIC"])[0]
        wh = qs.get("warehouse", [""])[0]
        role = qs.get("role", [""])[0]
        auth = qs.get("authenticator", [""])[0]
        token = qs.get("token", [""])[0]
        
        if password:
            uri = f"snowflake://{quote_plus(user)}:{quote_plus(password)}@{account}/{db}/{schema}"
        else:
            uri = f"snowflake://{quote_plus(user)}@{account}/{db}/{schema}"

        params = []
        if auth: params.append(f"authenticator={quote_plus(auth)}")
        if token: params.append(f"token={quote_plus(token)}")
        if wh: params.append(f"warehouse={quote_plus(wh)}")
        if role: params.append(f"role={quote_plus(role)}")
        if params: uri += "?" + "&".join(params)
        return uri, "snowflake"

    # 2. ODBC / .NET Key-Value Connection String (Snowflake or MSSQL)
    if ";" in cleaned and ("=" in cleaned):
        kv = {}
        for item in cleaned.split(";"):
            if "=" in item:
                k, v = item.split("=", 1)
                kv[k.strip().lower()] = v.strip()
        
        driver = kv.get("driver", "").lower()
        server = kv.get("server", "") or kv.get("host", "")
        is_snowflake = "snowflake" in driver or "snowflake" in server or "account" in kv
        
        if is_snowflake:
            account = kv.get("account", "")
            if not account and server:
                account = server.split(".snowflakecomputing.com")[0]
            user = kv.get("uid") or kv.get("user") or kv.get("username") or ""
            password = kv.get("pwd") or kv.get("password") or ""
            db = kv.get("database") or kv.get("db") or ""
            schema = kv.get("schema") or "PUBLIC"
            wh = kv.get("warehouse") or ""
            role = kv.get("role") or ""
            auth = kv.get("authenticator") or ""
            token = kv.get("token") or ""
            
            if password:
                uri = f"snowflake://{quote_plus(user)}:{quote_plus(password)}@{account}/{db}/{schema}"
            else:
                uri = f"snowflake://{quote_plus(user)}@{account}/{db}/{schema}"

            params = []
            if auth: params.append(f"authenticator={quote_plus(auth)}")
            if token: params.append(f"token={quote_plus(token)}")
            if wh: params.append(f"warehouse={quote_plus(wh)}")
            if role: params.append(f"role={quote_plus(role)}")
            if params: uri += "?" + "&".join(params)
            return uri, "snowflake"

        # Check MSSQL ODBC
        if "sql server" in driver or "odbc" in driver or "mssql" in driver:
            user = kv.get("uid") or kv.get("user") or ""
            password = kv.get("pwd") or kv.get("password") or ""
            database = kv.get("database") or kv.get("db") or ""
            driver_enc = quote_plus(kv.get("driver", "ODBC Driver 17 for SQL Server"))
            uri = f"mssql+pyodbc://{quote_plus(user)}:{quote_plus(password)}@{server}/{database}?driver={driver_enc}"
            return uri, "mssql"

    # 3. Standard URL Schemes
    if c_lower.startswith(("postgresql", "postgres")):
        return cleaned, "postgresql"

    if c_lower.startswith("mysql"):
        return cleaned, "mysql"

    if c_lower.startswith("sqlite"):
        return cleaned, "sqlite"

    if c_lower.startswith("mssql"):
        return cleaned, "mssql"

    if c_lower.startswith("snowflake://"):
        return cleaned, "snowflake"

    # 4. Go Snowflake DSN: user:pass@account.snowflakecomputing.com/db/schema?warehouse=...&role=...
    if "@" in cleaned:
        try:
            parsed = urlparse("dummy://" + cleaned)
            account = parsed.hostname.split(".snowflakecomputing.com")[0] if parsed.hostname else ""
            user = parsed.username or ""
            password = parsed.password or ""
            path_parts = [p for p in parsed.path.split("/") if p]
            db = path_parts[0] if len(path_parts) > 0 else ""
            schema = path_parts[1] if len(path_parts) > 1 else "PUBLIC"
            qs = parse_qs(parsed.query)
            wh = qs.get("warehouse", [""])[0]
            role = qs.get("role", [""])[0]
            auth = qs.get("authenticator", [""])[0]
            
            if password:
                uri = f"snowflake://{quote_plus(user)}:{quote_plus(password)}@{account}/{db}/{schema}"
            else:
                uri = f"snowflake://{quote_plus(user)}@{account}/{db}/{schema}"

            params = []
            if auth: params.append(f"authenticator={quote_plus(auth)}")
            if wh: params.append(f"warehouse={quote_plus(wh)}")
            if role: params.append(f"role={quote_plus(role)}")
            if params: uri += "?" + "&".join(params)
            return uri, "snowflake"
        except Exception:
            pass

    return cleaned, "generic"

_load_env()

class EnterpriseDBSandbox:
    def __init__(self, db_path: Optional[Union[str, Path]] = None, connection_uri: Optional[str] = None):
        self.raw_connection_uri = connection_uri
        self.connection_uri = connection_uri
        self.db_type = "postgresql"
        self.engine = None
        self.db_path = None

        if connection_uri:
            normalized_uri, detected_type = normalize_connection_uri(connection_uri)
            self.connection_uri = normalized_uri
            self.db_type = detected_type
            self.engine = create_engine(normalized_uri)
        else:
            # Default to PostgreSQL database 'SQL- Language Model'
            pg_host = os.getenv("POSTGRES_HOST", "localhost")
            pg_port = int(os.getenv("POSTGRES_PORT", "5432"))
            pg_db = os.getenv("POSTGRES_DB", "SQL- Language Model")
            pg_user = os.getenv("POSTGRES_USER", "postgres")
            pg_pass = os.getenv("POSTGRES_PASSWORD", "Nice123")

            try:
                db_url = URL.create(
                    drivername="postgresql+psycopg2",
                    username=pg_user,
                    password=pg_pass,
                    host=pg_host,
                    port=pg_port,
                    database=pg_db
                )
                self.engine = create_engine(db_url)
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.db_type = "postgresql"
            except Exception as e:
                # Fallback to in-memory SQLite if PostgreSQL is unreachable
                self.db_type = "sqlite"
                self.engine = create_engine("sqlite:///:memory:")
                self._init_in_memory_db()

    def _init_in_memory_db(self):
        """Initializes sample enterprise schema if running in-memory fallback."""
        with self.engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                region TEXT NOT NULL,
                segment TEXT NOT NULL,
                join_date DATE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY,
                dept_name TEXT NOT NULL,
                location TEXT NOT NULL,
                budget REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS employees (
                emp_id INTEGER PRIMARY KEY,
                emp_name TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                salary REAL NOT NULL,
                hire_date DATE NOT NULL,
                job_title TEXT NOT NULL,
                status TEXT DEFAULT 'ACTIVE',
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                item_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
            """))
            conn.commit()

    def get_schema_summary(self) -> Dict[str, List[str]]:
        """Returns dictionary of table names and their column names."""
        if self.engine is not None:
            try:
                insp = inspect(self.engine)
                schema = {}
                for t in insp.get_table_names():
                    cols = insp.get_columns(t)
                    schema[t] = [f"{c['name']} ({c.get('type', 'TEXT')})" for c in cols]
                return schema
            except Exception:
                pass

        if self.db_path:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                tables = [row[0] for row in cursor.fetchall()]
                
                schema = {}
                for t in tables:
                    cursor.execute(f"PRAGMA table_info({t});")
                    cols = cursor.fetchall()
                    schema[t] = [f"{c[1]} ({c[2]})" for c in cols]
                return schema
            except Exception:
                pass
        return {}

    def get_table_row_count(self, table_name: str) -> int:
        """Returns total row count for a table."""
        if self.engine is not None:
            try:
                with self.engine.connect() as conn:
                    res = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                    row = res.fetchone()
                    return int(row[0]) if row else 0
            except Exception:
                try:
                    with self.engine.connect() as conn:
                        res = conn.execute(text(f'SELECT COUNT(*) FROM {table_name}'))
                        row = res.fetchone()
                        return int(row[0]) if row else 0
                except Exception:
                    return 0
        elif self.db_path:
            try:
                conn = self._get_connection()
                cur = conn.cursor()
                cur.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                row = cur.fetchone()
                return int(row[0]) if row else 0
            except Exception:
                return 0
        return 0

    def get_sample_rows(self, table_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Returns sample rows for a table as list of dicts."""
        if self.engine is not None:
            try:
                with self.engine.connect() as conn:
                    try:
                        res = conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT {limit}'))
                    except Exception:
                        res = conn.execute(text(f'SELECT * FROM {table_name} LIMIT {limit}'))
                    cols = list(res.keys())
                    return [dict(zip(cols, [str(v) if v is not None else "NULL" for v in r])) for r in res.fetchall()]
            except Exception:
                return []
        elif self.db_path:
            try:
                conn = self._get_connection()
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
                cols = [desc[0] for desc in cur.description] if cur.description else []
                return [dict(zip(cols, [str(v) if v is not None else "NULL" for v in r])) for r in cur.fetchall()]
            except Exception:
                return []
        return []

    def validate_ast_safety(self, sql_query: str, allowed_tables: Optional[List[str]] = None) -> Tuple[bool, Optional[str], List[str]]:
        """
        AST-level SQL Safety Guard using sqlglot.
        - Enforces strictly read-only statements (SELECT / CTEs / UNION).
        - Blocks DDL, DML mutations, and administrative commands.
        - Identifies all referenced tables for RBAC authorization.
        """
        import sqlglot
        from sqlglot import exp

        cleaned = sql_query.strip()
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()

        dialect = "postgres" if self.db_type == "postgresql" else ("tsql" if self.db_type == "mssql" else "sqlite")
        try:
            # Parse AST
            parsed = sqlglot.parse_one(cleaned, read=dialect)
        except Exception:
            try:
                parsed = sqlglot.parse_one(cleaned)
            except Exception as e:
                return False, f"AST Parse Error: {str(e)}", []

        if parsed is None:
            return False, "Empty SQL statement", []

        # 1. Enforce read-only statement types
        disallowed_types = (
            exp.Drop, exp.Delete, exp.Update, exp.Insert,
            exp.Create, exp.Alter, exp.Command
        )
        if isinstance(parsed, disallowed_types):
            return False, f"Security Violation: '{parsed.key.upper()}' operations are prohibited in read-only sandbox mode.", []

        for node in parsed.walk():
            if isinstance(node, disallowed_types):
                return False, f"Security Violation: Nested mutation '{node.key.upper()}' detected.", []

        # Extract CTE aliases so they are not mistaken for physical tables
        cte_aliases = set()
        for cte in parsed.find_all(exp.CTE):
            if cte.alias:
                cte_aliases.add(cte.alias.lower())
            elif hasattr(cte, "this") and isinstance(cte.this, exp.TableAlias) and cte.this.name:
                cte_aliases.add(cte.this.name.lower())
            elif cte.name:
                cte_aliases.add(cte.name.lower())

        # 2. Extract referenced physical tables
        tables = []
        for tbl in parsed.find_all(exp.Table):
            if tbl.name:
                t_name = tbl.name.lower()
                if t_name not in cte_aliases and t_name not in tables:
                    tables.append(t_name)

        # 3. RBAC / Table authorization check
        if allowed_tables is not None:
            allowed_set = {t.lower() for t in allowed_tables}
            unauthorized = [t for t in tables if t not in allowed_set and t not in cte_aliases]
            if unauthorized:
                return False, f"Access Denied: Role not authorized to access table(s): {', '.join(unauthorized)}", tables

        return True, None, tables

    def execute_query(
        self,
        sql_query: str,
        role: Optional[str] = None,
        allowed_tables: Optional[List[str]] = None,
        row_limit: int = 500
    ) -> Dict[str, Any]:
        """
        Validates AST safety policies and executes read-only SQL against sandbox database.
        """
        cleaned_sql = sql_query.strip()
        if cleaned_sql.endswith(";"):
            cleaned_sql = cleaned_sql[:-1]

        # 1. AST Safety & Authorization Guard
        is_safe, sec_err, tables_accessed = self.validate_ast_safety(cleaned_sql, allowed_tables=allowed_tables)
        if not is_safe:
            return {
                "success": False,
                "safety_passed": False,
                "tables_accessed": tables_accessed,
                "error": sec_err,
                "columns": [],
                "rows": [],
                "row_count": 0
            }

        # 2. Database Execution via SQLAlchemy
        if self.engine is not None:
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(cleaned_sql))
                    columns = list(result.keys()) if result.returns_rows else []
                    rows = [list(r) for r in result.fetchmany(row_limit)] if result.returns_rows else []
                    return {
                        "success": True,
                        "safety_passed": True,
                        "tables_accessed": tables_accessed,
                        "error": None,
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows)
                    }
            except Exception as e:
                return {
                    "success": False,
                    "safety_passed": True,
                    "tables_accessed": tables_accessed,
                    "error": str(e),
                    "columns": [],
                    "rows": [],
                    "row_count": 0
                }

        # Fallback to direct SQLite connection
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(cleaned_sql)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchmany(row_limit)
            conn.close()
            return {
                "success": True,
                "safety_passed": True,
                "tables_accessed": tables_accessed,
                "error": None,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
        except Exception as e:
            conn.close()
            return {
                "success": False,
                "safety_passed": True,
                "tables_accessed": tables_accessed,
                "error": str(e),
                "columns": [],
                "rows": [],
                "row_count": 0
            }
            conn.close()
            return {
                "success": False,
                "safety_passed": True,
                "tables_accessed": tables_accessed,
                "error": str(e),
                "columns": [],
                "rows": [],
                "row_count": 0
            }

if __name__ == "__main__":
    sandbox = EnterpriseDBSandbox()
    print("[*] Enterprise Sandbox Schema:")
    for tbl, cols in sandbox.get_schema_summary().items():
        print(f"  - {tbl}: {cols}")

    print("\n[*] Testing AST Safety Policy:")
    # Test valid query
    valid_res = sandbox.execute_query("SELECT customer_id, first_name FROM customers WHERE region = 'EMEA';")
    print("Valid SELECT test -> success:", valid_res["success"], "| tables:", valid_res["tables_accessed"])

    # Test malicious DROP query
    drop_res = sandbox.execute_query("DROP TABLE customers;")
    print("DROP TABLE test -> success:", drop_res["success"], "| error:", drop_res["error"])

    # Test RBAC table restriction
    rbac_res = sandbox.execute_query("SELECT * FROM employees;", allowed_tables=["customers", "orders"])
    print("RBAC restricted test -> success:", rbac_res["success"], "| error:", rbac_res["error"])
