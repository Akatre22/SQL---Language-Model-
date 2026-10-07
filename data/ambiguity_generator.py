"""
Ambiguity Dataset Generator for SQL-SLM (Item 17).
Generates training pairs that teach the language model to identify underspecified
requests and emit structured clarification responses instead of hallucinating SQL.
"""

import sys
import json
import random
from pathlib import Path
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent
OUTPUT_AMBIGUITY_FILE = DATA_DIR / "ambiguity_dataset.jsonl"
SEED = 42
random.seed(SEED)

AMBIGUOUS_PATTERNS = [
    {
        "type": "MISSING_RANKING_METRIC",
        "templates": [
            "Show me the best customers.",
            "Who are our top clients?",
            "List top 5 employees.",
            "Find the best performing products."
        ],
        "clarification": "The request is underspecified. Please clarify:\n1. Ranking Metric: Should 'best' be measured by total revenue/spending, order frequency, or customer tenure?\n2. Time Period: Should this evaluate all-time activity, the current year, or the last quarter?\n3. Limit: How many records should be returned (e.g. top 5, top 10)?",
        "options": ["Rank by total spend", "Rank by order count", "Rank by customer rating"]
    },
    {
        "type": "MISSING_TIME_WINDOW",
        "templates": [
            "Show recent orders.",
            "Find latest transactions.",
            "List recent customer signups.",
            "Show recent shipments."
        ],
        "clarification": "The timeframe is ambiguous. Please specify the recency window:\n1. Last 24 hours\n2. Last 7 days\n3. Last 30 days\n4. Current calendar month",
        "options": ["Last 7 days", "Last 30 days", "Current month"]
    },
    {
        "type": "MISSING_AGGREGATION_GRAIN",
        "templates": [
            "Show sales summary.",
            "Give me revenue numbers.",
            "Provide payroll breakdown.",
            "Show performance metrics."
        ],
        "clarification": "The aggregation granularity is unspecified. Please clarify:\n1. Group by: Group by region, product category, sales rep, or month?\n2. Metrics: Sum total amount, average per transaction, or row counts?",
        "options": ["Group by region", "Group by category", "Group by month"]
    },
    {
        "type": "AMBIGUOUS_STATUS_FILTER",
        "templates": [
            "Find active accounts.",
            "Show valid transactions.",
            "List good loans.",
            "Find qualified leads."
        ],
        "clarification": "The status filter definition is ambiguous. Please define the qualifying criteria:\n1. For accounts: Balance > 0, transaction in last 90 days, or status = 'ACTIVE'?\n2. For loans: Current status, zero delinquencies, or fully disbursed?",
        "options": ["Status = 'ACTIVE'", "Balance > 0", "Non-delinquent"]
    }
]

def generate_ambiguity_dataset(count: int = 400) -> List[Dict[str, Any]]:
    print(f"[*] Generating {count} ambiguity & clarification training pairs...")
    samples = []
    
    schema_ctx = "customers(customer_id PK, first_name, last_name, region, segment, join_date)\norders(order_id PK, customer_id FK, total_amount, status, order_date)\nproducts(product_id PK, product_name, category, unit_price)\nemployees(emp_id PK, emp_name, department_id FK, salary)"

    for i in range(count):
        pat = random.choice(AMBIGUOUS_PATTERNS)
        q = random.choice(pat["templates"])
        clarify_text = pat["clarification"]
        
        sample = {
            "id": f"AMBIG-{i+1:04d}",
            "type": pat["type"],
            "question": q,
            "schema": schema_ctx,
            "suggested_options": pat["options"],
            "instruction": f"<schema>\n{schema_ctx}\n</schema>\n\n<question>\n{q}\n</question>",
            "response": f"<clarify>\n{clarify_text}\n</clarify>",
            "domain": "ambiguity_clarification",
            "task": "clarification_request"
        }
        samples.append(sample)

    with open(OUTPUT_AMBIGUITY_FILE, "w", encoding="utf-8") as f:
        for item in samples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[+] Successfully exported {len(samples)} ambiguity pairs to {OUTPUT_AMBIGUITY_FILE}")
    return samples

if __name__ == "__main__":
    generate_ambiguity_dataset(count=400)
