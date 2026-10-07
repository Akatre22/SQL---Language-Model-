"""
Enterprise SQL Sandbox Database for Tiny LLM SQL Agent.
Provides schema inspection and safe execution of analytics queries on realistic enterprise data.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
import sqlalchemy
from sqlalchemy import create_engine, text, inspect

DB_PATH = Path(__file__).resolve().parent / "enterprise_sandbox.db"

class EnterpriseDBSandbox:
    def __init__(self, db_path: Optional[Union[str, Path]] = None, connection_uri: Optional[str] = None):
        self.connection_uri = connection_uri
        self.db_type = "sqlite"
        self.engine = None

        if connection_uri:
            self.db_path = None
            if connection_uri.startswith("postgresql") or connection_uri.startswith("postgres"):
                self.db_type = "postgresql"
            elif connection_uri.startswith("mssql"):
                self.db_type = "mssql"
            elif connection_uri.startswith("sqlite"):
                self.db_type = "sqlite"
            else:
                self.db_type = "generic"
            self.engine = create_engine(connection_uri)
        else:
            self.db_path = Path(db_path) if db_path else DB_PATH
            self.db_type = "sqlite"
            self._init_db()
            self.engine = create_engine(f"sqlite:///{str(self.db_path).replace('\\', '/')}")

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        """Initializes tables and populates sample enterprise datasets."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.executescript("""
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
            FOREIGN KEY (department_id) REFERENCES departments(department_id)
        );

        CREATE TABLE IF NOT EXISTS sales_reps (
            rep_id INTEGER PRIMARY KEY,
            rep_name TEXT NOT NULL,
            region TEXT NOT NULL,
            commission_rate REAL NOT NULL,
            annual_target REAL NOT NULL
        );
        """)

        # Populate customers if empty
        cursor.execute("SELECT COUNT(*) FROM customers;")
        if cursor.fetchone()[0] == 0:
            cursor.executescript("""
            INSERT INTO customers VALUES
            (1, 'Alice', 'Smith', 'alice.smith@acme.com', 'EMEA', 'Enterprise', '2023-01-15'),
            (2, 'Bob', 'Jones', 'bob.jones@techcorp.com', 'APAC', 'Mid-Market', '2023-03-20'),
            (3, 'Charlie', 'Brown', 'charlie.b@fintech.io', 'NA', 'Enterprise', '2023-05-10'),
            (4, 'Diana', 'Prince', 'diana.p@cloudscale.net', 'EMEA', 'SMB', '2023-08-01'),
            (5, 'Evan', 'Wright', 'evan.w@globaldata.com', 'APAC', 'Enterprise', '2023-09-12'),
            (6, 'Fiona', 'Gallagher', 'fiona.g@retailhub.com', 'NA', 'Mid-Market', '2024-01-05');
            """)

        # Populate departments if empty
        cursor.execute("SELECT COUNT(*) FROM departments;")
        if cursor.fetchone()[0] == 0:
            cursor.executescript("""
            INSERT INTO departments VALUES
            (10, 'Engineering', 'San Francisco', 1200000.0),
            (20, 'Data & AI', 'New York', 950000.0),
            (30, 'Sales & Marketing', 'London', 750000.0),
            (40, 'Finance', 'Tokyo', 600000.0);
            """)

        # Populate employees if empty
        cursor.execute("SELECT COUNT(*) FROM employees;")
        if cursor.fetchone()[0] == 0:
            cursor.executescript("""
            INSERT INTO employees VALUES
            (101, 'Sarah Connor', 20, 145000.0, '2021-03-15', 'Principal Data Architect'),
            (102, 'John Miller', 20, 120000.0, '2022-06-01', 'Senior SQL Engineer'),
            (103, 'Elena Rostova', 10, 160000.0, '2020-01-10', 'VP of Engineering'),
            (104, 'David Kim', 10, 135000.0, '2021-09-20', 'Staff Software Engineer'),
            (105, 'Rachel Green', 30, 110000.0, '2022-11-15', 'Enterprise Sales Lead'),
            (106, 'Carlos Silva', 30, 95000.0, '2023-04-10', 'Account Executive'),
            (107, 'Mei Ling', 40, 128000.0, '2021-08-05', 'Senior Financial Analyst'),
            (108, 'Alex Becker', 20, 98000.0, '2023-10-01', 'Junior Data Engineer');
            """)

        # Populate sales_reps if empty
        cursor.execute("SELECT COUNT(*) FROM sales_reps;")
        if cursor.fetchone()[0] == 0:
            cursor.executescript("""
            INSERT INTO sales_reps VALUES
            (1, 'Marcus Vance', 'EMEA', 0.08, 150000.0),
            (2, 'Priya Sharma', 'APAC', 0.09, 180000.0),
            (3, 'Alex Mercer', 'NA', 0.075, 200000.0);
            """)

        conn.commit()
        conn.close()

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
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema = {}
            for t in tables:
                cursor.execute(f"PRAGMA table_info({t});")
                cols = [f"{row[1]} ({row[2]})" for row in cursor.fetchall()]
                schema[t] = cols
                
            conn.close()
            return schema
        return {}

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

        # 2. Extract referenced tables
        tables = []
        for tbl in parsed.find_all(exp.Table):
            if tbl.name:
                t_name = tbl.name.lower()
                if t_name not in tables:
                    tables.append(t_name)

        # 3. RBAC / Table authorization check
        if allowed_tables is not None:
            allowed_set = {t.lower() for t in allowed_tables}
            unauthorized = [t for t in tables if t not in allowed_set]
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
