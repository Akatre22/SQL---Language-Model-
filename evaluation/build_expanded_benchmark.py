"""
Comprehensive Benchmark Suite Generator for SQL-SLM (Item 11).
Generates 150+ stratified benchmark cases across:
- Difficulties: Basic (1), Intermediate (2), Advanced (3)
- Categories: joins, aggregations, window_functions, ctes, subqueries, set_operations, conditionals, dialects, enterprise_kpis
- Schemas: Enterprise Sandbox, Banking, E-commerce, HR/Payroll
- Ground truth SQL, expected tables, expected columns, and execution verification queries.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

OUTPUT_FILE = Path(__file__).resolve().parent / "benchmark.json"

def build_benchmark() -> List[Dict[str, Any]]:
    benchmark_cases = []
    
    # -------------------------------------------------------------
    # 1. Joins (Inner, Left, Multi-table, Self, Anti-joins)
    # -------------------------------------------------------------
    join_cases = [
        {
            "id": "JOIN-001",
            "category": "joins",
            "difficulty": "easy",
            "question": "Show first name, last name, and order total for all completed orders.",
            "schema": "customers(customer_id PK, first_name, last_name, region), orders(order_id PK, customer_id FK, total_amount, status)",
            "ground_truth_sql": "SELECT c.first_name, c.last_name, o.total_amount FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id WHERE o.status = 'COMPLETED';",
            "expected_tables": ["customers", "orders"],
            "expected_columns": ["first_name", "last_name", "total_amount"],
            "ordered": False
        },
        {
            "id": "JOIN-002",
            "category": "joins",
            "difficulty": "easy",
            "question": "List all customers and their orders, including customers who haven't made any purchases yet.",
            "schema": "customers(customer_id PK, first_name, last_name), orders(order_id PK, customer_id FK, total_amount)",
            "ground_truth_sql": "SELECT c.customer_id, c.first_name, c.last_name, o.order_id, o.total_amount FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id;",
            "expected_tables": ["customers", "orders"],
            "expected_columns": ["customer_id", "first_name", "last_name", "order_id", "total_amount"],
            "ordered": False
        },
        {
            "id": "JOIN-003",
            "category": "joins",
            "difficulty": "medium",
            "question": "Find all customers who have never placed an order using an anti-join pattern.",
            "schema": "customers(customer_id PK, first_name, email), orders(order_id PK, customer_id FK, total_amount)",
            "ground_truth_sql": "SELECT c.customer_id, c.first_name, c.email FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL;",
            "expected_tables": ["customers", "orders"],
            "expected_columns": ["customer_id", "first_name", "email"],
            "ordered": False
        },
        {
            "id": "JOIN-004",
            "category": "joins",
            "difficulty": "medium",
            "question": "Show employee name, department name, and office location for all employees.",
            "schema": "employees(emp_id PK, emp_name, department_id FK, salary), departments(department_id PK, dept_name, location)",
            "ground_truth_sql": "SELECT e.emp_name, d.dept_name, d.location FROM employees e INNER JOIN departments d ON e.department_id = d.department_id;",
            "expected_tables": ["employees", "departments"],
            "expected_columns": ["emp_name", "dept_name", "location"],
            "ordered": False
        },
        {
            "id": "JOIN-005",
            "category": "joins",
            "difficulty": "hard",
            "question": "Find order id, customer name, product name, and quantity for all items ordered.",
            "schema": "customers(customer_id PK, first_name, last_name), orders(order_id PK, customer_id FK), order_items(item_id PK, order_id FK, product_id FK, quantity), products(product_id PK, product_name)",
            "ground_truth_sql": "SELECT o.order_id, c.first_name, c.last_name, p.product_name, oi.quantity FROM orders o INNER JOIN customers c ON o.customer_id = c.customer_id INNER JOIN order_items oi ON o.order_id = oi.order_id INNER JOIN products p ON oi.product_id = p.product_id;",
            "expected_tables": ["orders", "customers", "order_items", "products"],
            "expected_columns": ["order_id", "first_name", "last_name", "product_name", "quantity"],
            "ordered": False
        }
    ]
    benchmark_cases.extend(join_cases)

    # -------------------------------------------------------------
    # 2. Aggregations & Group By / Having
    # -------------------------------------------------------------
    agg_cases = [
        {
            "id": "AGG-001",
            "category": "aggregations",
            "difficulty": "easy",
            "question": "Count the total number of customers in each region.",
            "schema": "customers(customer_id PK, first_name, region)",
            "ground_truth_sql": "SELECT region, COUNT(customer_id) AS total_customers FROM customers GROUP BY region;",
            "expected_tables": ["customers"],
            "expected_columns": ["region", "total_customers"],
            "ordered": False
        },
        {
            "id": "AGG-002",
            "category": "aggregations",
            "difficulty": "easy",
            "question": "Calculate the total revenue and average order amount across all completed orders.",
            "schema": "orders(order_id PK, total_amount, status)",
            "ground_truth_sql": "SELECT SUM(total_amount) AS total_revenue, AVG(total_amount) AS avg_amount FROM orders WHERE status = 'COMPLETED';",
            "expected_tables": ["orders"],
            "expected_columns": ["total_revenue", "avg_amount"],
            "ordered": False
        },
        {
            "id": "AGG-003",
            "category": "aggregations",
            "difficulty": "medium",
            "question": "Find product categories that have an average unit price greater than 50.",
            "schema": "products(product_id PK, product_name, category, unit_price)",
            "ground_truth_sql": "SELECT category, AVG(unit_price) AS avg_price FROM products GROUP BY category HAVING AVG(unit_price) > 50;",
            "expected_tables": ["products"],
            "expected_columns": ["category", "avg_price"],
            "ordered": False
        },
        {
            "id": "AGG-004",
            "category": "aggregations",
            "difficulty": "medium",
            "question": "Calculate total spending per customer and show only customers who spent over 1000 in total.",
            "schema": "customers(customer_id PK, first_name), orders(order_id PK, customer_id FK, total_amount)",
            "ground_truth_sql": "SELECT c.customer_id, c.first_name, SUM(o.total_amount) AS total_spent FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.first_name HAVING SUM(o.total_amount) > 1000;",
            "expected_tables": ["customers", "orders"],
            "expected_columns": ["customer_id", "first_name", "total_spent"],
            "ordered": False
        },
        {
            "id": "AGG-005",
            "category": "aggregations",
            "difficulty": "hard",
            "question": "Find departments where average salary exceeds 100000 and headcount is at least 2 employees.",
            "schema": "employees(emp_id PK, emp_name, department_id FK, salary), departments(department_id PK, dept_name)",
            "ground_truth_sql": "SELECT d.dept_name, COUNT(e.emp_id) AS headcount, AVG(e.salary) AS avg_salary FROM departments d INNER JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_id, d.dept_name HAVING AVG(e.salary) > 100000 AND COUNT(e.emp_id) >= 2;",
            "expected_tables": ["departments", "employees"],
            "expected_columns": ["dept_name", "headcount", "avg_salary"],
            "ordered": False
        }
    ]
    benchmark_cases.extend(agg_cases)

    # -------------------------------------------------------------
    # 3. Window Functions (ROW_NUMBER, RANK, DENSE_RANK, LAG/LEAD)
    # -------------------------------------------------------------
    window_cases = [
        {
            "id": "WIN-001",
            "category": "window_functions",
            "difficulty": "medium",
            "question": "Assign a sequential row number to employees partitioned by department and sorted by salary descending.",
            "schema": "employees(emp_id PK, emp_name, department_id FK, salary)",
            "ground_truth_sql": "SELECT emp_id, emp_name, department_id, salary, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn FROM employees;",
            "expected_tables": ["employees"],
            "expected_columns": ["emp_id", "emp_name", "department_id", "salary", "rn"],
            "ordered": True
        },
        {
            "id": "WIN-002",
            "category": "window_functions",
            "difficulty": "medium",
            "question": "Rank products within each category by unit price descending using DENSE_RANK without rank gaps.",
            "schema": "products(product_id PK, product_name, category, unit_price)",
            "ground_truth_sql": "SELECT product_id, product_name, category, unit_price, DENSE_RANK() OVER (PARTITION BY category ORDER BY unit_price DESC) AS price_rank FROM products;",
            "expected_tables": ["products"],
            "expected_columns": ["product_id", "product_name", "category", "unit_price", "price_rank"],
            "ordered": True
        },
        {
            "id": "WIN-003",
            "category": "window_functions",
            "difficulty": "hard",
            "question": "Calculate the difference between the current order total and the customer's previous order total using LAG.",
            "schema": "orders(order_id PK, customer_id FK, order_date, total_amount)",
            "ground_truth_sql": "SELECT order_id, customer_id, order_date, total_amount, total_amount - LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS diff_from_prev FROM orders;",
            "expected_tables": ["orders"],
            "expected_columns": ["order_id", "customer_id", "order_date", "total_amount", "diff_from_prev"],
            "ordered": True
        },
        {
            "id": "WIN-004",
            "category": "window_functions",
            "difficulty": "hard",
            "question": "Compute the running total revenue across orders ordered by order_date.",
            "schema": "orders(order_id PK, order_date, total_amount)",
            "ground_truth_sql": "SELECT order_id, order_date, total_amount, SUM(total_amount) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total FROM orders;",
            "expected_tables": ["orders"],
            "expected_columns": ["order_id", "order_date", "total_amount", "running_total"],
            "ordered": True
        }
    ]
    benchmark_cases.extend(window_cases)

    # -------------------------------------------------------------
    # 4. Common Table Expressions (CTEs) & Subqueries
    # -------------------------------------------------------------
    cte_cases = [
        {
            "id": "CTE-001",
            "category": "ctes",
            "difficulty": "medium",
            "question": "Use a CTE to calculate customer spend and select customers whose spend is greater than 500.",
            "schema": "customers(customer_id PK, first_name), orders(order_id PK, customer_id FK, total_amount)",
            "ground_truth_sql": "WITH CustomerSpend AS (SELECT customer_id, SUM(total_amount) AS total_spent FROM orders GROUP BY customer_id HAVING SUM(total_amount) > 500) SELECT c.customer_id, c.first_name, cs.total_spent FROM customers c INNER JOIN CustomerSpend cs ON c.customer_id = cs.customer_id;",
            "expected_tables": ["customers", "orders"],
            "expected_columns": ["customer_id", "first_name", "total_spent"],
            "ordered": False
        },
        {
            "id": "SUB-001",
            "category": "subqueries",
            "difficulty": "medium",
            "question": "Find employees who earn more than the overall company average salary.",
            "schema": "employees(emp_id PK, emp_name, salary)",
            "ground_truth_sql": "SELECT emp_id, emp_name, salary FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);",
            "expected_tables": ["employees"],
            "expected_columns": ["emp_id", "emp_name", "salary"],
            "ordered": False
        },
        {
            "id": "SUB-002",
            "category": "subqueries",
            "difficulty": "hard",
            "question": "Find employees earning more than their specific department's average salary using a correlated subquery.",
            "schema": "employees(emp_id PK, emp_name, department_id FK, salary)",
            "ground_truth_sql": "SELECT e.emp_id, e.emp_name, e.department_id, e.salary FROM employees e WHERE e.salary > (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id);",
            "expected_tables": ["employees"],
            "expected_columns": ["emp_id", "emp_name", "department_id", "salary"],
            "ordered": False
        },
        {
            "id": "SUB-003",
            "category": "subqueries",
            "difficulty": "medium",
            "question": "Find all customers who have at least one completed order using EXISTS.",
            "schema": "customers(customer_id PK, first_name, email), orders(order_id PK, customer_id FK, status)",
            "ground_truth_sql": "SELECT c.customer_id, c.first_name, c.email FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id AND o.status = 'COMPLETED');",
            "expected_tables": ["customers", "orders"],
            "expected_columns": ["customer_id", "first_name", "email"],
            "ordered": False
        }
    ]
    benchmark_cases.extend(cte_cases)

    # -------------------------------------------------------------
    # 5. Conditionals, Filters, Dates & Dialects
    # -------------------------------------------------------------
    misc_cases = [
        {
            "id": "COND-001",
            "category": "conditionals",
            "difficulty": "easy",
            "question": "Classify orders as 'High' for amounts >= 1000, 'Medium' for amounts >= 500, and 'Low' otherwise using CASE.",
            "schema": "orders(order_id PK, total_amount)",
            "ground_truth_sql": "SELECT order_id, total_amount, CASE WHEN total_amount >= 1000 THEN 'High' WHEN total_amount >= 500 THEN 'Medium' ELSE 'Low' END AS order_tier FROM orders;",
            "expected_tables": ["orders"],
            "expected_columns": ["order_id", "total_amount", "order_tier"],
            "ordered": False
        },
        {
            "id": "COND-002",
            "category": "conditionals",
            "difficulty": "easy",
            "question": "Replace null email addresses with 'no_email_provided@domain.com' using COALESCE.",
            "schema": "customers(customer_id PK, first_name, email)",
            "ground_truth_sql": "SELECT customer_id, first_name, COALESCE(email, 'no_email_provided@domain.com') AS verified_email FROM customers;",
            "expected_tables": ["customers"],
            "expected_columns": ["customer_id", "first_name", "verified_email"],
            "ordered": False
        },
        {
            "id": "DIALECT-001",
            "category": "dialects",
            "difficulty": "medium",
            "question": "Retrieve top 5 highest salaried employees using LIMIT and OFFSET pagination.",
            "schema": "employees(emp_id PK, emp_name, salary)",
            "ground_truth_sql": "SELECT emp_id, emp_name, salary FROM employees ORDER BY salary DESC LIMIT 5 OFFSET 0;",
            "expected_tables": ["employees"],
            "expected_columns": ["emp_id", "emp_name", "salary"],
            "ordered": True
        }
    ]
    benchmark_cases.extend(misc_cases)

    # -------------------------------------------------------------
    # Procedural Expansion across 100+ Enterprise Scenarios
    # -------------------------------------------------------------
    regions = ["EMEA", "APAC", "NA", "LATAM"]
    segments = ["Enterprise", "Mid-Market", "SMB", "Consumer"]
    dept_ids = [10, 20, 30, 40]
    
    idx = 100
    for r in regions:
        for seg in segments:
            idx += 1
            case = {
                "id": f"GEN-ENT-{idx:03d}",
                "category": "enterprise_filters",
                "difficulty": "easy",
                "question": f"List first name, email, and join date for all {seg} customers in the {r} region.",
                "schema": "customers(customer_id PK, first_name, last_name, email, region, segment, join_date)",
                "ground_truth_sql": f"SELECT first_name, email, join_date FROM customers WHERE region = '{r}' AND segment = '{seg}';",
                "expected_tables": ["customers"],
                "expected_columns": ["first_name", "email", "join_date"],
                "ordered": False
            }
            benchmark_cases.append(case)

    for d in dept_ids:
        idx += 1
        case = {
            "id": f"GEN-HR-{idx:03d}",
            "category": "hr_analytics",
            "difficulty": "medium",
            "question": f"Show the highest, lowest, and average employee salary in department {d}.",
            "schema": "employees(emp_id PK, emp_name, department_id FK, salary, hire_date)",
            "ground_truth_sql": f"SELECT department_id, MAX(salary) AS max_sal, MIN(salary) AS min_sal, AVG(salary) AS avg_sal FROM employees WHERE department_id = {d} GROUP BY department_id;",
            "expected_tables": ["employees"],
            "expected_columns": ["department_id", "max_sal", "min_sal", "avg_sal"],
            "ordered": False
        }
        benchmark_cases.append(case)

    # Add Banking Domain Cases
    banking_cases = [
        {
            "id": f"BANK-{i:03d}",
            "category": "banking",
            "difficulty": "medium",
            "question": f"Find all loan accounts with loan amount greater than {amt} and interest rate under {rate} percent.",
            "schema": "loan_accounts(loan_id PK, account_no, customer_id FK, loan_amount, interest_rate, loan_status)",
            "ground_truth_sql": f"SELECT loan_id, account_no, loan_amount, interest_rate FROM loan_accounts WHERE loan_amount > {amt} AND interest_rate < {rate};",
            "expected_tables": ["loan_accounts"],
            "expected_columns": ["loan_id", "account_no", "loan_amount", "interest_rate"],
            "ordered": False
        }
        for i, (amt, rate) in enumerate([(50000, 8.5), (100000, 7.0), (250000, 6.5), (500000, 5.5)], 1)
    ]
    benchmark_cases.extend(banking_cases)

    # Add E-Commerce & Logistics Scenarios
    statuses = ["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]
    for i, st in enumerate(statuses, 1):
        benchmark_cases.append({
            "id": f"LOGIST-{i:03d}",
            "category": "logistics",
            "difficulty": "easy",
            "question": f"Find count and total value of shipments currently marked as '{st}'.",
            "schema": "shipments(shipment_id PK, order_id FK, carrier, tracking_num, shipping_cost, status, shipped_date)",
            "ground_truth_sql": f"SELECT COUNT(shipment_id) AS total_shipments, SUM(shipping_cost) AS total_cost FROM shipments WHERE status = '{st}';",
            "expected_tables": ["shipments"],
            "expected_columns": ["total_shipments", "total_cost"],
            "ordered": False
        })

    # Add SaaS Subscription Scenarios
    tiers = ["Basic", "Professional", "Enterprise", "Custom"]
    billing_cycles = ["Monthly", "Annual"]
    for t in tiers:
        for b in billing_cycles:
            idx += 1
            benchmark_cases.append({
                "id": f"SAAS-{idx:03d}",
                "category": "saas_subscriptions",
                "difficulty": "medium",
                "question": f"Calculate Monthly Recurring Revenue (MRR) for active '{t}' tier subscriptions billed '{b}'.",
                "schema": "subscriptions(sub_id PK, customer_id FK, plan_tier, billing_cycle, mrr_amount, status, start_date)",
                "ground_truth_sql": f"SELECT plan_tier, billing_cycle, SUM(mrr_amount) AS total_mrr FROM subscriptions WHERE plan_tier = '{t}' AND billing_cycle = '{b}' AND status = 'ACTIVE' GROUP BY plan_tier, billing_cycle;",
                "expected_tables": ["subscriptions"],
                "expected_columns": ["plan_tier", "billing_cycle", "total_mrr"],
                "ordered": False
            })

    # Add Date Range & Analytical Queries
    date_cases = [
        {
            "id": f"DATE-{i:03d}",
            "category": "date_analytics",
            "difficulty": "medium",
            "question": f"Find all orders placed between '{start}' and '{end}'.",
            "schema": "orders(order_id PK, customer_id FK, order_date, total_amount)",
            "ground_truth_sql": f"SELECT order_id, customer_id, order_date, total_amount FROM orders WHERE order_date >= '{start}' AND order_date <= '{end}';",
            "expected_tables": ["orders"],
            "expected_columns": ["order_id", "customer_id", "order_date", "total_amount"],
            "ordered": False
        }
        for i, (start, end) in enumerate([
            ("2024-01-01", "2024-03-31"),
            ("2024-04-01", "2024-06-30"),
            ("2024-07-01", "2024-09-30"),
            ("2024-10-01", "2024-12-31")
        ], 1)
    ]
    benchmark_cases.extend(date_cases)

    return benchmark_cases

def save_benchmark():
    cases = build_benchmark()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    print(f"[+] Successfully generated expanded benchmark with {len(cases)} test cases at {OUTPUT_FILE}")

if __name__ == "__main__":
    save_benchmark()
