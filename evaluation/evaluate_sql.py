"""
SQL Syntax, AST & Semantic Result Evaluator for NICE Tiny LLM.
Evaluates generated SQL against ground truth queries via:
1. AST validation and clause breakdown (Tables, Columns, Joins, Aggregations).
2. Sandbox database execution.
3. Full result-set semantic equivalence (order-sensitive, order-insensitive, and schema matching).
"""

import re
import sqlite3
from typing import Dict, Any, Optional, List, Tuple, Set
import sqlglot
from sqlglot import exp

class SQLEvaluator:
    def __init__(self, custom_conn: Optional[sqlite3.Connection] = None):
        self.conn = custom_conn or sqlite3.connect(":memory:")
        if custom_conn is None:
            self._init_sandbox_schema()

    def _init_sandbox_schema(self):
        """Initializes a standard enterprise schema with mock data for query testing."""
        cursor = self.conn.cursor()
        
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            region TEXT,
            created_at DATE
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date DATE,
            total_amount REAL,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price REAL,
            stock_quantity INTEGER
        );

        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY,
            product_id INTEGER,
            customer_id INTEGER,
            sale_date DATE,
            amount REAL,
            region TEXT,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE IF NOT EXISTS employees (
            emp_id INTEGER PRIMARY KEY,
            emp_name TEXT,
            department TEXT,
            salary REAL,
            hire_date DATE
        );

        -- Insert Sample Rows if empty
        INSERT OR IGNORE INTO customers VALUES
        (1, 'Alice', 'Smith', 'alice@example.com', 'EMEA', '2023-01-15'),
        (2, 'Bob', 'Jones', 'bob@example.com', 'APAC', '2023-03-20'),
        (3, 'Charlie', 'Brown', 'charlie@example.com', 'NA', '2023-05-10'),
        (4, 'Diana', 'Prince', 'diana@example.com', 'EMEA', '2023-08-01');

        INSERT OR IGNORE INTO orders VALUES
        (101, 1, '2024-01-10', 1250.00, 'COMPLETED'),
        (102, 1, '2024-02-15', 450.00, 'COMPLETED'),
        (103, 2, '2024-03-01', 3200.00, 'PENDING'),
        (104, 3, '2024-03-05', 850.00, 'COMPLETED'),
        (105, 4, '2024-04-12', 2100.00, 'COMPLETED');

        INSERT OR IGNORE INTO products VALUES
        (1, 'Cloud Data Lake', 'Software', 5000.0, 100),
        (2, 'Analytics Dashboard', 'BI', 1500.0, 50),
        (3, 'Data Warehouse Connector', 'ETL', 800.0, 200);

        INSERT OR IGNORE INTO sales VALUES
        (1, 1, 1, '2024-01-15', 5000.0, 'EMEA'),
        (2, 2, 2, '2024-02-20', 1500.0, 'APAC'),
        (3, 3, 3, '2024-03-10', 800.0, 'NA'),
        (4, 1, 4, '2024-04-05', 5000.0, 'EMEA');

        INSERT OR IGNORE INTO employees VALUES
        (1, 'Sarah Connor', 'Engineering', 95000.0, '2021-06-01'),
        (2, 'John Doe', 'Sales', 72000.0, '2022-01-15'),
        (3, 'Jane Smith', 'Engineering', 110000.0, '2020-03-10');
        """)
        self.conn.commit()

    def extract_sql(self, text: str) -> Optional[str]:
        """Extracts SQL code block or raw query from model generation."""
        if not text:
            return None
        # 1. Match <sql> ... </sql>
        match = re.search(r"<sql>\s*(.*?)\s*(?:</sql>|<\|endoftext\|>|$)", text, re.DOTALL | re.IGNORECASE)
        if match and match.group(1).strip():
            return match.group(1).strip()
        # 2. Match ```sql ... ```
        match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if match and match.group(1).strip():
            return match.group(1).strip()
        # 3. Match generic ``` ... ``` with SELECT / WITH
        match = re.search(r"```\s*((?:WITH|SELECT)[\s\S]*?)```", text, re.DOTALL | re.IGNORECASE)
        if match and match.group(1).strip():
            return match.group(1).strip()
        # 4. Match raw SELECT statement
        match = re.search(r"\b((?:WITH\s+[\s\S]+?SELECT|SELECT)\s+[\s\S]*?;?)", text, re.IGNORECASE)
        if match:
            sql_candidate = match.group(1).split("\n\n")[0].strip()
            return sql_candidate
            
        return text.strip() if ("SELECT" in text.upper() or "WITH" in text.upper()) else None

    def extract_ast_features(self, sql_query: str) -> Dict[str, Any]:
        """Extracts structural AST features (tables, columns, joins, aggregations)."""
        features = {
            "tables": set(),
            "columns": set(),
            "has_join": False,
            "has_group_by": False,
            "has_having": False,
            "has_order_by": False,
            "has_limit": False,
            "has_window": False,
            "has_cte": False
        }
        cleaned = sql_query.strip().rstrip(";")
        try:
            parsed = sqlglot.parse_one(cleaned, read="sqlite")
            if parsed is None:
                return features

            for tbl in parsed.find_all(exp.Table):
                if tbl.name:
                    features["tables"].add(tbl.name.lower())

            for col in parsed.find_all(exp.Column):
                if col.name:
                    features["columns"].add(col.name.lower())

            features["has_join"] = bool(list(parsed.find_all(exp.Join)))
            features["has_group_by"] = bool(parsed.find(exp.Group))
            features["has_having"] = bool(parsed.find(exp.Having))
            features["has_order_by"] = bool(parsed.find(exp.Order))
            features["has_limit"] = bool(parsed.find(exp.Limit))
            features["has_window"] = bool(list(parsed.find_all(exp.Window)))
            features["has_cte"] = bool(parsed.find(exp.With))
        except Exception:
            pass

        return features

    def execute_raw(self, sql_query: str) -> Tuple[bool, List[str], List[Tuple], Optional[str]]:
        """Executes a SQL query safely and returns (success, columns, rows, error)."""
        cleaned = sql_query.strip()
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1]

        cursor = self.conn.cursor()
        try:
            cursor.execute(cleaned)
            cols = [d[0] for d in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return True, cols, rows, None
        except Exception as e:
            return False, [], [], str(e)

    def evaluate_semantic_equivalence(
        self,
        generated_sql: str,
        ground_truth_sql: str,
        ordered: bool = False
    ) -> Dict[str, Any]:
        """
        Comprehensive Semantic Result Evaluation:
        Compares execution outputs of generated SQL vs ground-truth SQL.
        """
        gen_clean = generated_sql.strip()
        gt_clean = ground_truth_sql.strip()

        # 1. AST Feature Comparison
        gen_ast = self.extract_ast_features(gen_clean)
        gt_ast = self.extract_ast_features(gt_clean)

        # Precision & Recall for tables
        gt_tables = gt_ast["tables"]
        gen_tables = gen_ast["tables"]
        table_intersection = gen_tables.intersection(gt_tables)
        table_precision = len(table_intersection) / max(1, len(gen_tables)) if gen_tables else 0.0
        table_recall = len(table_intersection) / max(1, len(gt_tables)) if gt_tables else 1.0

        # Precision & Recall for columns
        gt_cols = gt_ast["columns"]
        gen_cols = gen_ast["columns"]
        col_intersection = gen_cols.intersection(gt_cols)
        col_precision = len(col_intersection) / max(1, len(gen_cols)) if gen_cols else 0.0
        col_recall = len(col_intersection) / max(1, len(gt_cols)) if gt_cols else 1.0

        # 2. Execute Ground Truth
        gt_ok, gt_cols_list, gt_rows, gt_err = self.execute_raw(gt_clean)
        if not gt_ok:
            return {
                "generated_sql": gen_clean,
                "ground_truth_sql": gt_clean,
                "syntax_valid": False,
                "executable": False,
                "result_equivalent": False,
                "exact_match": (gen_clean.lower() == gt_clean.lower()),
                "error": f"Ground truth query failed: {gt_err}"
            }

        # 3. Execute Generated Query
        gen_ok, gen_cols_list, gen_rows, gen_err = self.execute_raw(gen_clean)
        if not gen_ok:
            return {
                "generated_sql": gen_clean,
                "ground_truth_sql": gt_clean,
                "syntax_valid": False,
                "executable": False,
                "result_equivalent": False,
                "exact_match": False,
                "error": f"Generated SQL error: {gen_err}",
                "table_precision": round(table_precision, 3),
                "table_recall": round(table_recall, 3),
                "column_precision": round(col_precision, 3),
                "column_recall": round(col_recall, 3)
            }

        # 4. Result Equivalence Check
        exact_match = (gen_clean.lower() == gt_clean.lower())
        row_count_match = (len(gen_rows) == len(gt_rows))

        # Check order-sensitive equivalence
        order_match = (gen_rows == gt_rows)

        # Check order-insensitive set equivalence (comparing multiset/sorted rows)
        try:
            set_match = (sorted([str(r) for r in gen_rows]) == sorted([str(r) for r in gt_rows]))
        except Exception:
            set_match = False

        result_equivalent = order_match if ordered else set_match

        return {
            "generated_sql": gen_clean,
            "ground_truth_sql": gt_clean,
            "syntax_valid": True,
            "executable": True,
            "result_equivalent": result_equivalent,
            "order_equivalent": order_match,
            "exact_match": exact_match,
            "row_count_match": row_count_match,
            "generated_rows_count": len(gen_rows),
            "ground_truth_rows_count": len(gt_rows),
            "table_precision": round(table_precision, 3),
            "table_recall": round(table_recall, 3),
            "column_precision": round(col_precision, 3),
            "column_recall": round(col_recall, 3),
            "ast_features_match": {
                "join_match": (gen_ast["has_join"] == gt_ast["has_join"]),
                "group_by_match": (gen_ast["has_group_by"] == gt_ast["has_group_by"]),
                "order_by_match": (gen_ast["has_order_by"] == gt_ast["has_order_by"])
            },
            "error": None
        }

    def evaluate_response(self, model_response: str) -> Dict[str, Any]:
        """Evaluates single response for SQL extraction and basic execution."""
        extracted = self.extract_sql(model_response)
        if not extracted:
            return {
                "has_sql": False,
                "sql": None,
                "syntax_valid": False,
                "executable": False,
                "error": "No SQL found in output"
            }
        
        ok, cols, rows, err = self.execute_raw(extracted)
        return {
            "has_sql": True,
            "sql": extracted,
            "syntax_valid": ok,
            "executable": ok,
            "row_count": len(rows),
            "sample_rows": [list(r) for r in rows[:5]],
            "error": err
        }

if __name__ == "__main__":
    evaluator = SQLEvaluator()
    print("[*] Testing Semantic Result Evaluator:")

    gt_query = "SELECT customer_id, first_name FROM customers WHERE region = 'EMEA' ORDER BY customer_id;"
    gen_query = "SELECT c.customer_id, c.first_name FROM customers c WHERE c.region = 'EMEA' ORDER BY c.customer_id;"

    res = evaluator.evaluate_semantic_equivalence(gen_query, gt_query, ordered=True)
    print("Semantic Equivalence Result:")
    for k, v in res.items():
        print(f"  - {k}: {v}")

