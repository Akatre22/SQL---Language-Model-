"""
Hard-Negative SQL Generator (Item 14).
Procedurally generates syntactically plausible but semantically flawed queries
with structured error analysis and correction targets.
Perturbation Types:
1. WRONG_JOIN_KEY: Mismatched foreign keys in join predicates.
2. MISSING_GROUP_BY: Aggregate queries missing necessary grouping keys.
3. INVERTED_FILTER: Inverted comparison operators (< vs >) or wrong literal filters.
4. WRONG_AGGREGATION: Confusion between COUNT, SUM, and AVG.
5. WRONG_TABLE_SELECTION: Querying an adjacent table with similar column names.
"""

import sys
import json
import random
from pathlib import Path
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent
OUTPUT_NEGATIVES_FILE = DATA_DIR / "hard_negatives.jsonl"
SEED = 42
random.seed(SEED)

def generate_hard_negatives(count: int = 600) -> List[Dict[str, Any]]:
    print(f"[*] Generating {count} hard-negative training pairs with error critiques...")
    negatives = []

    schema_sales = "customers(customer_id PK, first_name, last_name, region, segment)\norders(order_id PK, customer_id FK, total_amount, status, order_date)\nproducts(product_id PK, product_name, category, unit_price)\norder_items(item_id PK, order_id FK, product_id FK, quantity)"
    schema_hr = "employees(emp_id PK, emp_name, department_id FK, salary, hire_date)\ndepartments(department_id PK, dept_name, location, budget)"
    schema_bank = "accounts(account_id PK, customer_id FK, account_type, balance, status)\ntransactions(txn_id PK, account_id FK, amount, txn_type, status, txn_date)"

    regions = ["EMEA", "APAC", "NA", "LATAM"]
    amounts = [500, 1000, 2500, 5000]

    for i in range(count):
        ptype = random.randint(1, 5)
        r = random.choice(regions)
        amt = random.choice(amounts)

        if ptype == 1:
            # 1. WRONG_JOIN_KEY
            q = f"Show customer first name and order amount for all orders."
            correct_sql = "SELECT c.first_name, o.total_amount FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id;"
            bad_sql = "SELECT c.first_name, o.total_amount FROM customers c INNER JOIN orders o ON c.customer_id = o.order_id;"
            error_reason = "Semantic Flaw: Incorrect join predicate. Joining customer_id with order_id causes Cartesian corruption; should join on o.customer_id."
            flaw_type = "WRONG_JOIN_KEY"
            schema = schema_sales

        elif ptype == 2:
            # 2. WRONG_AGGREGATION (COUNT vs SUM)
            q = f"Calculate total revenue generated from completed orders."
            correct_sql = "SELECT SUM(total_amount) AS total_revenue FROM orders WHERE status = 'COMPLETED';"
            bad_sql = "SELECT COUNT(total_amount) AS total_revenue FROM orders WHERE status = 'COMPLETED';"
            error_reason = "Semantic Flaw: Used COUNT() instead of SUM(). COUNT() returns the number of rows, not the monetary total revenue."
            flaw_type = "WRONG_AGGREGATION"
            schema = schema_sales

        elif ptype == 3:
            # 3. INVERTED_FILTER (< vs >)
            q = f"Find all high-earning employees with salary exceeding {amt * 20}."
            sal_target = amt * 20
            correct_sql = f"SELECT emp_id, emp_name, salary FROM employees WHERE salary > {sal_target};"
            bad_sql = f"SELECT emp_id, emp_name, salary FROM employees WHERE salary < {sal_target};"
            error_reason = f"Semantic Flaw: Inverted filter operator. The query requests employees with salary greater than {sal_target}, but used '<' instead of '>'."
            flaw_type = "INVERTED_FILTER"
            schema = schema_hr

        elif ptype == 4:
            # 4. MISSING_GROUP_BY
            q = f"Calculate total spending per customer for completed orders."
            correct_sql = "SELECT customer_id, SUM(total_amount) AS total_spent FROM orders WHERE status = 'COMPLETED' GROUP BY customer_id;"
            bad_sql = "SELECT customer_id, SUM(total_amount) AS total_spent FROM orders WHERE status = 'COMPLETED';"
            error_reason = "Semantic Flaw: Missing GROUP BY customer_id. Aggregating SUM(total_amount) alongside an unaggregated customer_id produces invalid SQL in ANSI SQL."
            flaw_type = "MISSING_GROUP_BY"
            schema = schema_sales

        else:
            # 5. WRONG_TABLE_SELECTION
            q = f"Find the total balance across all active savings accounts."
            correct_sql = "SELECT SUM(balance) AS total_balance FROM accounts WHERE account_type = 'SAVINGS' AND status = 'ACTIVE';"
            bad_sql = "SELECT SUM(amount) AS total_balance FROM transactions WHERE txn_type = 'SAVINGS' AND status = 'ACTIVE';"
            error_reason = "Semantic Flaw: Incorrect table selection. Query searched the 'transactions' table instead of the 'accounts' table."
            flaw_type = "WRONG_TABLE_SELECTION"
            schema = schema_bank

        sample = {
            "id": f"HARD-NEG-{i+1:04d}",
            "flaw_type": flaw_type,
            "schema": schema,
            "question": q,
            "flawed_sql": bad_sql,
            "error_analysis": error_reason,
            "correct_sql": correct_sql,
            "instruction": f"<schema>\n{schema}\n</schema>\n\n<question>\n{q}\n</question>\n\n<critique>\nFlawed SQL: {bad_sql}\nIssue: {error_reason}\n</critique>",
            "response": f"<sql>\n{correct_sql}\n</sql>",
            "domain": "hard_negatives",
            "task": "error_correction"
        }
        negatives.append(sample)

    with open(OUTPUT_NEGATIVES_FILE, "w", encoding="utf-8") as f:
        for item in negatives:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[+] Successfully exported {len(negatives)} hard-negative correction pairs to {OUTPUT_NEGATIVES_FILE}")
    return negatives

if __name__ == "__main__":
    generate_hard_negatives(count=600)
