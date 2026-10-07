"""
Unseen Schema Banking Challenge Suite (Item 16).
Completely isolated multi-table Core Banking Sandbox and Challenge Benchmark.
Evaluates zero-shot generalization of SQL-SLM on relational schemas never seen during training.
"""

import sys
import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from inference.generate import TinyLLMInference
from evaluation.evaluate_sql import SQLEvaluator
from agent_engine.schema_formatter import SchemaFormatter, DatabaseCatalog

BANKING_DB_PATH = Path(__file__).resolve().parent / "banking_challenge_sandbox.db"

def init_banking_database() -> sqlite3.Connection:
    """Initializes and populates a realistic Core Banking SQLite database."""
    conn = sqlite3.connect(str(BANKING_DB_PATH))
    cursor = conn.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS wire_transactions;
    DROP TABLE IF EXISTS card_accounts;
    DROP TABLE IF EXISTS loan_contracts;
    DROP TABLE IF EXISTS deposit_accounts;
    DROP TABLE IF EXISTS bank_customers;

    CREATE TABLE bank_customers (
        customer_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        kyc_status TEXT NOT NULL,
        credit_score INTEGER NOT NULL,
        risk_tier TEXT NOT NULL,
        city TEXT NOT NULL,
        onboard_date DATE NOT NULL
    );

    CREATE TABLE deposit_accounts (
        account_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        account_type TEXT NOT NULL,
        current_balance REAL NOT NULL,
        available_balance REAL NOT NULL,
        currency TEXT NOT NULL,
        opened_at DATE NOT NULL,
        account_status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES bank_customers(customer_id)
    );

    CREATE TABLE loan_contracts (
        loan_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        principal_amount REAL NOT NULL,
        interest_rate REAL NOT NULL,
        monthly_emi REAL NOT NULL,
        tenure_months INTEGER NOT NULL,
        outstanding_balance REAL NOT NULL,
        loan_status TEXT NOT NULL,
        disbursed_date DATE NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES bank_customers(customer_id)
    );

    CREATE TABLE card_accounts (
        card_id INTEGER PRIMARY KEY,
        account_id INTEGER NOT NULL,
        card_type TEXT NOT NULL,
        credit_limit REAL NOT NULL,
        utilized_amount REAL NOT NULL,
        apr REAL NOT NULL,
        expiry_date DATE NOT NULL,
        card_status TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES deposit_accounts(account_id)
    );

    CREATE TABLE wire_transactions (
        txn_id INTEGER PRIMARY KEY,
        from_account_id INTEGER NOT NULL,
        to_account_id INTEGER NOT NULL,
        txn_timestamp DATETIME NOT NULL,
        amount REAL NOT NULL,
        currency TEXT NOT NULL,
        txn_type TEXT NOT NULL,
        channel TEXT NOT NULL,
        is_flagged INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (from_account_id) REFERENCES deposit_accounts(account_id)
    );

    -- Insert Realistic Sample Records
    INSERT INTO bank_customers VALUES
    (101, 'Alexander Vance', 'VERIFIED', 780, 'LOW', 'New York', '2021-03-15'),
    (102, 'Elena Rostova', 'VERIFIED', 810, 'LOW', 'London', '2020-07-20'),
    (103, 'Marcus Sterling', 'PENDING', 620, 'HIGH', 'Zurich', '2023-01-10'),
    (104, 'Priya Sharma', 'VERIFIED', 740, 'MEDIUM', 'Singapore', '2022-09-05'),
    (105, 'David Kim', 'VERIFIED', 690, 'MEDIUM', 'Tokyo', '2023-05-18'),
    (106, 'Fatima Al-Mansoor', 'VERIFIED', 825, 'LOW', 'Dubai', '2019-11-30'),
    (107, 'Carlos Mendez', 'SUSPENDED', 540, 'HIGH', 'Madrid', '2024-02-01');

    INSERT INTO deposit_accounts VALUES
    (201, 101, 'CHECKING', 45000.0, 44200.0, 'USD', '2021-03-16', 'ACTIVE'),
    (202, 101, 'SAVINGS', 185000.0, 185000.0, 'USD', '2021-03-20', 'ACTIVE'),
    (203, 102, 'PREMIUM_SAVINGS', 620000.0, 620000.0, 'GBP', '2020-07-21', 'ACTIVE'),
    (204, 103, 'CHECKING', 12500.0, 11800.0, 'USD', '2023-01-11', 'ACTIVE'),
    (205, 104, 'BUSINESS_CHECKING', 340000.0, 335000.0, 'SGD', '2022-09-06', 'ACTIVE'),
    (206, 105, 'CHECKING', 8900.0, 8900.0, 'USD', '2023-05-19', 'ACTIVE'),
    (207, 106, 'PRIVATE_WEALTH', 1450000.0, 1450000.0, 'USD', '2019-12-01', 'ACTIVE'),
    (208, 107, 'CHECKING', 1200.0, 500.0, 'EUR', '2024-02-02', 'FROZEN');

    INSERT INTO loan_contracts VALUES
    (301, 101, 500000.0, 4.25, 2450.0, 360, 420000.0, 'CURRENT', '2021-04-01'),
    (302, 103, 75000.0, 8.50, 1850.0, 48, 62000.0, 'DELINQUENT', '2023-02-15'),
    (303, 104, 1200000.0, 5.10, 8900.0, 240, 1050000.0, 'CURRENT', '2022-10-01'),
    (304, 107, 35000.0, 11.25, 950.0, 36, 33000.0, 'DEFAULTED', '2024-02-10');

    INSERT INTO card_accounts VALUES
    (401, 201, 'PLATINUM', 50000.0, 12400.0, 14.5, '2027-05-01', 'ACTIVE'),
    (402, 203, 'INFINITE', 100000.0, 8500.0, 11.9, '2028-08-01', 'ACTIVE'),
    (403, 204, 'STANDARD', 10000.0, 9200.0, 22.4, '2026-03-01', 'ACTIVE'),
    (404, 206, 'GOLD', 25000.0, 21500.0, 18.0, '2026-11-01', 'ACTIVE');

    INSERT INTO wire_transactions VALUES
    (501, 201, 202, '2024-01-15 10:30:00', 10000.0, 'USD', 'INTERNAL_TRANSFER', 'ONLINE_BANKING', 0),
    (502, 203, 205, '2024-02-01 14:15:00', 75000.0, 'USD', 'CROSS_BORDER_WIRE', 'SWIFT', 0),
    (503, 204, 208, '2024-02-10 09:00:00', 55000.0, 'USD', 'HIGH_RISK_WIRE', 'MOBILE_APP', 1),
    (504, 207, 201, '2024-03-05 16:45:00', 120000.0, 'USD', 'DIVIDEND_PAYOUT', 'TREASURY', 0),
    (505, 208, 204, '2024-03-12 11:20:00', 8500.0, 'EUR', 'PEER_TO_PEER', 'MOBILE_APP', 1);
    """)

    conn.commit()
    return conn

# ----------------------------------------------------------------------
# Held-Out Zero-Shot Banking Challenge Test Cases
# ----------------------------------------------------------------------
BANKING_CHALLENGES = [
    {
        "id": "BANK-UNSEEN-001",
        "category": "kyc_risk",
        "question": "Find customer full name, city, and credit score for verified customers with risk tier 'LOW'.",
        "ground_truth_sql": "SELECT full_name, city, credit_score FROM bank_customers WHERE kyc_status = 'VERIFIED' AND risk_tier = 'LOW';",
        "ordered": False
    },
    {
        "id": "BANK-UNSEEN-002",
        "category": "multi_table_join",
        "question": "Show customer full name, account type, and current balance for all active deposit accounts.",
        "ground_truth_sql": "SELECT c.full_name, a.account_type, a.current_balance FROM bank_customers c INNER JOIN deposit_accounts a ON c.customer_id = a.customer_id WHERE a.account_status = 'ACTIVE';",
        "ordered": False
    },
    {
        "id": "BANK-UNSEEN-003",
        "category": "fraud_compliance",
        "question": "Find all wire transactions that have been flagged for compliance review (is_flagged = 1) with amount greater than 10000.",
        "ground_truth_sql": "SELECT txn_id, from_account_id, amount, currency, channel FROM wire_transactions WHERE is_flagged = 1 AND amount > 10000;",
        "ordered": False
    },
    {
        "id": "BANK-UNSEEN-004",
        "category": "credit_risk",
        "question": "Find card accounts where credit utilization exceeds 80% (utilized_amount > 0.8 * credit_limit).",
        "ground_truth_sql": "SELECT card_id, account_id, credit_limit, utilized_amount, (utilized_amount / credit_limit) AS utilization_rate FROM card_accounts WHERE utilized_amount > (0.8 * credit_limit);",
        "ordered": False
    },
    {
        "id": "BANK-UNSEEN-005",
        "category": "aggregations",
        "question": "Calculate total deposit balance and average balance grouped by customer risk tier.",
        "ground_truth_sql": "SELECT c.risk_tier, COUNT(a.account_id) AS account_count, SUM(a.current_balance) AS total_balance, AVG(a.current_balance) AS avg_balance FROM bank_customers c INNER JOIN deposit_accounts a ON c.customer_id = a.customer_id GROUP BY c.risk_tier;",
        "ordered": False
    },
    {
        "id": "BANK-UNSEEN-006",
        "category": "delinquent_loans",
        "question": "List customer full name, loan principal, and outstanding balance for delinquent or defaulted loans.",
        "ground_truth_sql": "SELECT c.full_name, l.principal_amount, l.outstanding_balance, l.loan_status FROM bank_customers c INNER JOIN loan_contracts l ON c.customer_id = l.customer_id WHERE l.loan_status IN ('DELINQUENT', 'DEFAULTED');",
        "ordered": False
    },
    {
        "id": "BANK-UNSEEN-007",
        "category": "window_ranking",
        "question": "Rank deposit accounts within each currency by current balance descending using DENSE_RANK.",
        "ground_truth_sql": "SELECT account_id, customer_id, currency, current_balance, DENSE_RANK() OVER (PARTITION BY currency ORDER BY current_balance DESC) AS balance_rank FROM deposit_accounts WHERE account_status = 'ACTIVE';",
        "ordered": True
    },
    {
        "id": "BANK-UNSEEN-008",
        "category": "ctes",
        "question": "Use a CTE to find high balance accounts with current_balance >= 100000 and select customer name and account type.",
        "ground_truth_sql": "WITH HighBalance AS (SELECT account_id, customer_id, account_type, current_balance FROM deposit_accounts WHERE current_balance >= 100000) SELECT c.full_name, hb.account_type, hb.current_balance FROM bank_customers c INNER JOIN HighBalance hb ON c.customer_id = hb.customer_id;",
        "ordered": False
    }
]

class BankingChallengeEvaluator:
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.conn = init_banking_database()
        self.sql_evaluator = SQLEvaluator(custom_conn=self.conn)
        self.bot = TinyLLMInference(checkpoint_path=checkpoint_path)
        self.catalog = SchemaFormatter.extract_from_sqlite(self.conn)
        self.schema_str = SchemaFormatter.to_compact(self.catalog)

    def run_challenge(self) -> Dict[str, Any]:
        print("\n" + "=" * 80)
        print("          UNSEEN SCHEMA BANKING CHALLENGE BENCHMARK (ZERO-SHOT)")
        print("=" * 80)
        print(f"[*] Unseen Schema Under Test:\n{self.schema_str}\n")
        print(f"[*] Executing {len(BANKING_CHALLENGES)} unseen challenge test cases...\n")

        results = []
        syntax_passes = 0
        exec_passes = 0
        semantic_passes = 0
        table_precisions = []
        col_precisions = []

        for idx, item in enumerate(BANKING_CHALLENGES, 1):
            q_id = item["id"]
            cat = item["category"]
            question = item["question"]
            gt_sql = item["ground_truth_sql"]
            ordered = item.get("ordered", False)

            # Generate SQL conditioned on the completely unseen banking schema
            gen_res = self.bot.generate_structured(
                question=question,
                schema=self.schema_str,
                dialect="sqlite",
                temperature=0.0
            )
            gen_sql = gen_res["sql"]
            latency = gen_res["latency_sec"]

            # Evaluate semantic equivalence
            sem_res = self.sql_evaluator.evaluate_semantic_equivalence(
                generated_sql=gen_sql,
                ground_truth_sql=gt_sql,
                ordered=ordered
            )

            if sem_res["syntax_valid"]:
                syntax_passes += 1
            if sem_res["executable"]:
                exec_passes += 1
            if sem_res["result_equivalent"]:
                semantic_passes += 1

            table_precisions.append(sem_res.get("table_precision", 0.0))
            col_precisions.append(sem_res.get("column_precision", 0.0))

            status_str = "[SEMANTIC PASS]" if sem_res["result_equivalent"] else ("[SYNTAX OK]" if sem_res["syntax_valid"] else "[FAIL]")
            print(f"[{idx:02d}/{len(BANKING_CHALLENGES):02d}] {q_id} ({cat}) -> {status_str} ({latency:.2f}s)")
            print(f"       Generated SQL: {gen_sql}")
            if not sem_res["result_equivalent"]:
                print(f"       Expected SQL:  {gt_sql}")
                if sem_res.get("error"):
                    print(f"       Error:         {sem_res['error']}")
            print("-" * 80)

            results.append({
                "id": q_id,
                "category": cat,
                "question": question,
                "generated_sql": gen_sql,
                "ground_truth_sql": gt_sql,
                "eval": sem_res
            })

        total = len(BANKING_CHALLENGES)
        report = {
            "total_unseen_cases": total,
            "syntax_validity_pct": round((syntax_passes / total) * 100, 2),
            "execution_pass_pct": round((exec_passes / total) * 100, 2),
            "semantic_equivalence_pct": round((semantic_passes / total) * 100, 2),
            "avg_table_precision_pct": round((sum(table_precisions) / max(1, len(table_precisions))) * 100, 2),
            "avg_column_precision_pct": round((sum(col_precisions) / max(1, len(col_precisions))) * 100, 2),
            "results": results
        }

        print("\n" + "=" * 80)
        print("                 UNSEEN BANKING CHALLENGE SUMMARY")
        print("=" * 80)
        print(f"Zero-Shot Semantic Equivalence:  {report['semantic_equivalence_pct']}%")
        print(f"Zero-Shot Execution Pass Rate:   {report['execution_pass_pct']}%")
        print(f"Zero-Shot Syntax Validity:       {report['syntax_validity_pct']}%")
        print(f"Average Table Precision:         {report['avg_table_precision_pct']}%")
        print(f"Average Column Precision:        {report['avg_column_precision_pct']}%")
        print("=" * 80 + "\n")
        return report

if __name__ == "__main__":
    evaluator = BankingChallengeEvaluator()
    evaluator.run_challenge()
