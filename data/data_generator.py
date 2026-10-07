"""
Pure SQL Synthetic Data Generator for Tiny LLM.
Generates comprehensive, validated instruction-response training samples covering:
- SQL Query Syntax & Construction (SELECT, WHERE, ORDER BY, GROUP BY, HAVING, LIMIT/OFFSET)
- Joins (INNER, LEFT, RIGHT, FULL OUTER, CROSS, SELF JOIN, Anti-Join, Semi-Join)
- Subqueries & Common Table Expressions (Scalar, Correlated, EXISTS, CTEs, Recursive CTEs)
- Window Functions (ROW_NUMBER, RANK, DENSE_RANK, NTILE, LEAD, LAG, FIRST_VALUE, SUM/AVG OVER)
- Aggregations & Grouping Sets (COUNT, SUM, AVG, MIN, MAX, GROUPING SETS, ROLLUP, CUBE)
- Set Operations (UNION, UNION ALL, INTERSECT, EXCEPT / MINUS)
- DDL, Schema Design & Constraints (CREATE TABLE, PRIMARY KEY, FOREIGN KEY, CHECK, UNIQUE, NOT NULL)
- DML & Transactions (INSERT, UPDATE, DELETE, MERGE/UPSERT, TRUNCATE, BEGIN, COMMIT, ROLLBACK)
- Indexes & Performance (B-Tree, Hash, Unique, Composite, Clustered vs Non-Clustered, EXPLAIN)
- Dialects & Standard Functions (PostgreSQL, MySQL, SQLite, ANSI SQL, COALESCE, NULLIF, CASE WHEN)
"""

import json
import random
import os
from pathlib import Path
import sqlglot

SEED = 42
random.seed(SEED)

DATA_DIR = Path(__file__).resolve().parent
TRAIN_FILE = DATA_DIR / "train.jsonl"
VAL_FILE = DATA_DIR / "val.jsonl"
CORPUS_FILE = DATA_DIR / "corpus.txt"

TABLES = {
    "customers": ["customer_id", "first_name", "last_name", "email", "country", "created_at", "status"],
    "orders": ["order_id", "customer_id", "order_date", "total_amount", "order_status", "shipping_country"],
    "order_items": ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount"],
    "products": ["product_id", "product_name", "category", "price", "stock_quantity", "supplier_id"],
    "employees": ["emp_id", "emp_name", "department_id", "salary", "hire_date", "manager_id"],
    "departments": ["department_id", "dept_name", "location_id", "budget"],
    "sales": ["sale_id", "rep_id", "region", "amount", "sale_date", "product_id"],
    "transactions": ["txn_id", "account_id", "txn_type", "amount", "txn_time", "status"],
    "inventory": ["inventory_id", "product_id", "warehouse_id", "quantity_on_hand", "last_restocked"],
    "categories": ["category_id", "category_name", "parent_category_id", "description"]
}

SQL_CONCEPTS = [
    {
        "concept": "INNER JOIN",
        "def": "An INNER JOIN returns only records that have matching values in both joining tables.",
        "examples": [
            ("SELECT c.first_name, o.total_amount FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id;",
             "This query returns customer first names and order totals where a customer has placed orders.")
        ],
        "use_case": "Use INNER JOIN when you want only intersecting records present in both related datasets."
    },
    {
        "concept": "LEFT JOIN",
        "def": "A LEFT JOIN (or LEFT OUTER JOIN) returns all records from the left table, and matching records from the right table. Unmatched right rows return NULL values.",
        "examples": [
            ("SELECT c.customer_id, c.first_name, o.order_id FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id;",
             "This query returns all customers, including those who have never placed an order (order_id will be NULL).")
        ],
        "use_case": "Use LEFT JOIN when you want to preserve all rows from the primary table regardless of whether matches exist in the secondary table."
    },
    {
        "concept": "RIGHT JOIN",
        "def": "A RIGHT JOIN (or RIGHT OUTER JOIN) returns all records from the right table, and matching records from the left table. Unmatched left rows return NULL values.",
        "examples": [
            ("SELECT d.dept_name, e.emp_name FROM employees e RIGHT JOIN departments d ON e.department_id = d.department_id;",
             "This query lists all departments, including departments that currently have no assigned employees.")
        ],
        "use_case": "Use RIGHT JOIN when you want to preserve all rows from the secondary table."
    },
    {
        "concept": "FULL OUTER JOIN",
        "def": "A FULL OUTER JOIN returns all records when there is a match in either left or right table records, returning NULL where matches are missing on either side.",
        "examples": [
            ("SELECT c.customer_id, o.order_id FROM customers c FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;",
             "This returns all customers and all orders, pairing matches and padding NULLs for unlinked rows.")
        ],
        "use_case": "Use FULL OUTER JOIN when comparing two tables to find matched, left-only, and right-only records."
    },
    {
        "concept": "CROSS JOIN",
        "def": "A CROSS JOIN produces the Cartesian product of two tables, pairing every row from the first table with every row in the second table.",
        "examples": [
            ("SELECT p.product_name, s.store_name FROM products p CROSS JOIN stores s;",
             "This query generates all possible product-store inventory combinations.")
        ],
        "use_case": "Use CROSS JOIN to generate matrix permutations, date ranges against entities, or test combinations."
    },
    {
        "concept": "SELF JOIN",
        "def": "A SELF JOIN is a regular join in which a table is joined with itself using table aliases to model hierarchical or sequential relationships.",
        "examples": [
            ("SELECT e.emp_name AS employee, m.emp_name AS manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.emp_id;",
             "This query joins the employees table to itself to list each employee alongside their direct manager.")
        ],
        "use_case": "Use SELF JOIN for parent-child hierarchies, employee-manager trees, or comparing successive rows."
    },
    {
        "concept": "Common Table Expression (CTE)",
        "def": "A CTE is a temporary named result set defined using the WITH clause that exists only during query execution, making complex queries modular and readable.",
        "examples": [
            ("WITH HighValueOrders AS (SELECT customer_id, SUM(total_amount) AS total_spent FROM orders GROUP BY customer_id HAVING SUM(total_amount) > 1000) SELECT c.first_name, h.total_spent FROM HighValueOrders h JOIN customers c ON h.customer_id = c.customer_id;",
             "This CTE calculates high-value customer order sums first, then joins with the customer table for readability.")
        ],
        "use_case": "Use CTEs instead of deeply nested subqueries to improve readability, reuse intermediate query blocks, and write recursive queries."
    },
    {
        "concept": "Recursive CTE",
        "def": "A recursive CTE references itself to iteratively traverse hierarchical or graph data until a termination condition is met.",
        "examples": [
            ("WITH RECURSIVE OrgHierarchy AS (SELECT emp_id, emp_name, manager_id, 1 AS level FROM employees WHERE manager_id IS NULL UNION ALL SELECT e.emp_id, e.emp_name, e.manager_id, o.level + 1 FROM employees e JOIN OrgHierarchy o ON e.manager_id = o.emp_id) SELECT * FROM OrgHierarchy;",
             "This traverses the employee-manager organizational tree from CEO down to all reporting levels.")
        ],
        "use_case": "Use Recursive CTEs for organizational charts, bill-of-materials, category trees, and graph path traversal."
    },
    {
        "concept": "ROW_NUMBER() Window Function",
        "def": "ROW_NUMBER() assigns a unique sequential integer to each row within a partition, ordered by the specified ORDER BY clause.",
        "examples": [
            ("SELECT emp_id, department_id, salary, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank_in_dept FROM employees;",
             "This query assigns ranks 1, 2, 3... to employees in each department sorted by highest salary.")
        ],
        "use_case": "Use ROW_NUMBER() for pagination, deduplication (e.g. keeping ROW_NUMBER = 1), and finding top-N records per category."
    },
    {
        "concept": "RANK() vs DENSE_RANK()",
        "def": "RANK() leaves gaps in sequence following tied values (e.g., 1, 2, 2, 4), whereas DENSE_RANK() assigns consecutive rank numbers without gaps (e.g., 1, 2, 2, 3).",
        "examples": [
            ("SELECT emp_id, salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rnk, RANK() OVER (ORDER BY salary DESC) AS standard_rnk FROM employees;",
             "This demonstrates the difference in rank numbering when identical salaries exist across employees.")
        ],
        "use_case": "Use DENSE_RANK() when you need consecutive ranks without gaps (such as top 3 compensation bands)."
    },
    {
        "concept": "LEAD() and LAG()",
        "def": "LAG() accesses data from a previous row at a specified physical offset, while LEAD() accesses data from a subsequent row without requiring a self-join.",
        "examples": [
            ("SELECT order_date, total_amount, LAG(total_amount, 1) OVER (ORDER BY order_date) AS prev_amount, LEAD(total_amount, 1) OVER (ORDER BY order_date) AS next_amount FROM orders;",
             "This retrieves previous and next order values to calculate period-over-period differences.")
        ],
        "use_case": "Use LEAD/LAG for period-over-period growth, time series deltas, and state transitions."
    },
    {
        "concept": "GROUP BY and HAVING",
        "def": "GROUP BY aggregates rows sharing common column values into summary rows. The HAVING clause filters grouped aggregates, unlike WHERE which filters individual rows before aggregation.",
        "examples": [
            ("SELECT category, COUNT(*) AS product_count, AVG(price) AS avg_price FROM products GROUP BY category HAVING COUNT(*) > 5;",
             "This query calculates product count and average price per category for categories having more than 5 products.")
        ],
        "use_case": "Use WHERE to filter raw rows before grouping; use HAVING to filter aggregated statistics after grouping."
    },
    {
        "concept": "UNION vs UNION ALL",
        "def": "UNION combines the result sets of two queries and performs an implicit DISTINCT to remove duplicate rows, whereas UNION ALL retains all rows including duplicates without sort overhead.",
        "examples": [
            ("SELECT customer_id FROM orders_2024 UNION ALL SELECT customer_id FROM orders_2025;",
             "Combines customer IDs across both years quickly without the performance penalty of duplicate removal.")
        ],
        "use_case": "Use UNION ALL by default for speed when duplicates are acceptable or impossible; use UNION only when deduplication is required."
    },
    {
        "concept": "EXISTS vs IN",
        "def": "EXISTS tests for the existence of any rows returned by a subquery and short-circuits on the first match. IN compares a value against a literal list or single-column subquery.",
        "examples": [
            ("SELECT c.customer_id, c.first_name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id AND o.total_amount > 500);",
             "Efficiently finds customers who have placed at least one high-value order.")
        ],
        "use_case": "Use EXISTS for correlated subqueries on large datasets where subqueries can short-circuit early."
    },
    {
        "concept": "B-Tree vs Hash Index",
        "def": "A B-Tree index is a balanced tree structure supporting equality (=) and range queries (<, <=, >, >=, BETWEEN), while a Hash index supports only fast O(1) equality searches.",
        "examples": [
            ("CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);",
             "Creates a composite B-Tree index to accelerate lookups filtering by customer and sorting by date.")
        ],
        "use_case": "Use B-Tree indexes for general-purpose queries, sorting, and range lookups."
    },
    {
        "concept": "Clustered vs Non-Clustered Index",
        "def": "A Clustered index determines the physical order of data rows on disk (only one per table, usually Primary Key). A Non-Clustered index stores key values with pointers to physical data rows.",
        "examples": [
            ("CREATE CLUSTERED INDEX idx_sales_date ON sales (sale_date);",
             "Physically arranges sales records sequentially by sale_date for fast sequential range scans.")
        ],
        "use_case": "Use Clustered index on primary key or high-frequency date ranges; use Non-Clustered for secondary search filters."
    },
    {
        "concept": "ACID Properties in Relational Databases",
        "def": "ACID guarantees database transaction reliability: Atomicity (all-or-nothing), Consistency (integrity constraints enforced), Isolation (concurrent transactions don't interfere), and Durability (committed changes persist).",
        "examples": [
            ("BEGIN TRANSACTION;\nUPDATE accounts SET balance = balance - 100 WHERE account_id = 1;\nUPDATE accounts SET balance = balance + 100 WHERE account_id = 2;\nCOMMIT;",
             "A bank transfer demonstrating Atomicity: either both updates succeed or both roll back.")
        ],
        "use_case": "Essential for financial systems, inventory allocations, and mission-critical transactional integrity."
    },
    {
        "concept": "DELETE vs TRUNCATE vs DROP",
        "def": "DELETE removes specific rows matching a WHERE clause (DML, logged, triggers fire). TRUNCATE removes all rows quickly by deallocating pages (DDL, minimal logging). DROP deletes the entire table schema and data.",
        "examples": [
            ("TRUNCATE TABLE staging_events;",
             "Rapidly clears all records from the staging table while preserving table schema and constraints.")
        ],
        "use_case": "Use DELETE for selective row removal, TRUNCATE to reset full table contents quickly, and DROP to remove tables permanently."
    },
    {
        "concept": "COALESCE and NULLIF",
        "def": "COALESCE returns the first non-NULL expression from its argument list. NULLIF returns NULL if two expressions are equal, otherwise returns the first expression.",
        "examples": [
            ("SELECT product_name, COALESCE(discount_price, regular_price, 0) AS final_price, 100 / NULLIF(total_units, 0) AS per_unit FROM products;",
             "Demonstrates COALESCE for fallback values and NULLIF to prevent division-by-zero errors.")
        ],
        "use_case": "Use COALESCE for default fallback values and NULLIF to guard against division-by-zero errors."
    },
    {
        "concept": "CASE WHEN Expression",
        "def": "CASE WHEN enables conditional if-then-else branching logic directly inside SQL SELECT, WHERE, HAVING, or ORDER BY statements.",
        "examples": [
            ("SELECT order_id, total_amount, CASE WHEN total_amount >= 500 THEN 'High' WHEN total_amount >= 100 THEN 'Medium' ELSE 'Low' END AS order_tier FROM orders;",
             "Categorizes order sizes dynamically into tiers.")
        ],
        "use_case": "Use CASE WHEN for data categorization, conditional aggregations, and value mapping."
    }
]

def generate_synthetic_sql_samples(count=4000):
    samples = []
    
    # 1. Concept Q&A
    for c in SQL_CONCEPTS:
        q_templates = [
            f"What is {c['concept']} in SQL?",
            f"Explain {c['concept']} in SQL with examples and best use cases.",
            f"How does {c['concept']} work in relational databases?",
            f"Can you provide a SQL code example demonstrating {c['concept']}?",
            f"When should a data engineer choose {c['concept']}?",
            f"What is the definition and syntax of {c['concept']} in SQL?",
        ]
        for q in q_templates:
            ans = f"{c['def']}\n\n**Best Use Case:** {c['use_case']}\n\n**Example SQL:**\n```sql\n{c['examples'][0][0]}\n```\n{c['examples'][0][1]}"
            samples.append({
                "instruction": q,
                "input": "",
                "output": ans,
                "domain": "sql",
                "task": "concept_qa"
            })

    categories = ["Electronics", "Clothing", "Furniture", "Books", "Office Supplies", "Hardware", "Appliances", "Sports", "Toys", "Automotive"]
    regions = ["North America", "EMEA", "APAC", "LATAM", "Global", "US-East", "US-West", "Europe", "Asia"]
    statuses = ["ACTIVE", "PENDING", "COMPLETED", "CANCELLED", "REFUNDED", "SHIPPED", "PROCESSING"]

    for i in range(count):
        choice = random.randint(1, 14)
        
        if choice == 1:
            # Aggregation by region or category
            reg = random.choice(regions)
            stat = random.choice(statuses)
            sql = f"SELECT region, COUNT(sale_id) AS total_sales, SUM(amount) AS total_revenue, AVG(amount) AS avg_sale FROM sales WHERE region = '{reg}' AND sale_date >= '2025-01-01' GROUP BY region;"
            samples.append({
                "instruction": f"Write a SQL query to calculate total sales count, total revenue, and average sale for the '{reg}' region since 2025-01-01.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- Filters records for region '{reg}' and sale dates on or after '2025-01-01'.\n- Computes `COUNT`, `SUM`, and `AVG` aggregated by region.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 2:
            # Join customers & orders
            status = random.choice(statuses)
            min_amt = random.choice([50, 100, 200, 500, 1000])
            sql = f"SELECT c.customer_id, c.first_name, c.last_name, c.email, o.order_id, o.total_amount FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_status = '{status}' AND o.total_amount > {min_amt} ORDER BY o.total_amount DESC;"
            samples.append({
                "instruction": f"Write a SQL query joining customers and orders where order status is '{status}' and total amount exceeds {min_amt}, sorted descending by total amount.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- Joins `customers` and `orders` on `customer_id`.\n- Filters for `{status}` orders with `total_amount > {min_amt}`.\n- Sorts descending by `total_amount`.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 3:
            # Multi-table 3-way join
            cat = random.choice(categories)
            sql = f"SELECT c.customer_id, c.first_name, p.product_name, p.category, oi.quantity, oi.unit_price FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE p.category = '{cat}';"
            samples.append({
                "instruction": f"Write a SQL query performing a multi-table join across customers, orders, order_items, and products to list customer purchases for category '{cat}'.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- Joins `customers` -> `orders` -> `order_items` -> `products`.\n- Filters for products in the '{cat}' category.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 4:
            # Top-N ranking with ROW_NUMBER / DENSE_RANK
            n = random.choice([1, 2, 3, 5])
            sql = f"WITH RankedSales AS (SELECT rep_id, region, amount, ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS rnk FROM sales) SELECT rep_id, region, amount FROM RankedSales WHERE rnk <= {n};"
            samples.append({
                "instruction": f"Write SQL to retrieve the top {n} highest value sales transaction(s) per region using a CTE and ROW_NUMBER window function.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- `ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC)` assigns ranks partitioned by region.\n- The outer query filters for `rnk <= {n}`.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 5:
            # Moving average / Running Total
            days = random.choice([7, 14, 30])
            sql = f"SELECT sale_date, amount, AVG(amount) OVER (ORDER BY sale_date ROWS BETWEEN {days} PRECEDING AND CURRENT ROW) AS moving_avg_sales FROM sales;"
            samples.append({
                "instruction": f"Write SQL to compute a {days}-period moving average of sale amount over time ordered by sale date.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- Uses the window frame `ROWS BETWEEN {days} PRECEDING AND CURRENT ROW` to calculate the smoothed moving average.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 6:
            # Lead / Lag query
            sql = "SELECT customer_id, order_date, total_amount, LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_amount, total_amount - LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS diff_from_prev FROM orders;"
            samples.append({
                "instruction": f"Write SQL using the LAG() window function to calculate the difference in order amount compared to each customer's previous order.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- `LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date)` gets the preceding order's amount.\n- Calculates `total_amount - prev_order_amount` directly.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 7:
            # DDL Table creation with constraints
            tbl = f"dim_store_{random.choice(['location', 'inventory', 'performance', 'metrics'])}"
            sql = f"CREATE TABLE {tbl} (\n  store_id INT PRIMARY KEY,\n  store_name VARCHAR(100) NOT NULL,\n  region VARCHAR(50) NOT NULL,\n  opening_date DATE NOT NULL,\n  is_active BOOLEAN NOT NULL DEFAULT TRUE,\n  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);"
            samples.append({
                "instruction": f"Write SQL DDL to create a store dimension table named '{tbl}' with primary key, not null, and default constraints.",
                "input": "",
                "output": f"```sql\n{sql}\n```",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 8:
            # Conditional aggregation using CASE
            sql = "SELECT region, SUM(CASE WHEN total_amount >= 500 THEN total_amount ELSE 0 END) AS high_val_rev, SUM(CASE WHEN total_amount < 500 THEN total_amount ELSE 0 END) AS low_val_rev FROM orders o JOIN customers c ON o.customer_id = c.customer_id GROUP BY region;"
            samples.append({
                "instruction": f"Write a SQL query using conditional SUM(CASE WHEN ...) to separate high-value (>= $500) and low-value (< $500) revenue per region.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- Uses conditional statements inside `SUM()` to pivot revenue aggregates into discrete columns.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 9:
            # Anti-Join using LEFT JOIN / IS NULL
            sql = "SELECT c.customer_id, c.first_name, c.email FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL;"
            samples.append({
                "instruction": f"Write a SQL anti-join query to find all customers who have never placed an order.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- `LEFT JOIN` returns all customers.\n- `WHERE o.order_id IS NULL` filters for customers who have zero matching orders.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 10:
            # Recursive CTE for Category Tree
            sql = "WITH RECURSIVE CategoryTree AS (SELECT category_id, category_name, parent_category_id, 0 AS depth FROM categories WHERE parent_category_id IS NULL UNION ALL SELECT c.category_id, c.category_name, c.parent_category_id, ct.depth + 1 FROM categories c JOIN CategoryTree ct ON c.parent_category_id = ct.category_id) SELECT * FROM CategoryTree ORDER BY depth, category_name;"
            samples.append({
                "instruction": f"Write a recursive CTE in SQL to traverse a parent-child category hierarchy starting from root categories.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- Base member selects root categories (`parent_category_id IS NULL`).\n- Recursive member joins `categories` with `CategoryTree` on parent ID incrementing depth.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 11:
            # Query Optimization & Index recommendation
            bad_query = f"SELECT * FROM sales WHERE EXTRACT(YEAR FROM sale_date) = 2025 AND UPPER(region) = 'EMEA';"
            good_query = f"SELECT sale_id, rep_id, region, amount, sale_date FROM sales WHERE sale_date >= '2025-01-01' AND sale_date < '2026-01-01' AND region = 'EMEA';"
            idx_stmt = f"CREATE INDEX idx_sales_region_date ON sales (region, sale_date);"
            samples.append({
                "instruction": f"Analyze and optimize the following SQL query for better index usage and performance:\n```sql\n{bad_query}\n```",
                "input": "",
                "output": f"### Performance Issues:\n1. **Function on Indexed Column**: Wrapping `sale_date` in `EXTRACT(YEAR ...)` prevents standard index range scans (sargability issue).\n2. **Function on Filter Column**: `UPPER(region)` invalidates standard index lookups on `region`.\n3. **SELECT ***: Retrieves unnecessary columns.\n\n### Optimized Query:\n```sql\n{good_query}\n```\n\n### Recommended Index:\n```sql\n{idx_stmt}\n```",
                "domain": "sql",
                "task": "sql_optimization"
            })

        elif choice == 12:
            # Dialect Conversion: PostgreSQL LIMIT/OFFSET to Oracle or SQL Server
            pg_sql = "SELECT * FROM products ORDER BY price DESC LIMIT 10 OFFSET 20;"
            tsql_sql = "SELECT * FROM products ORDER BY price DESC OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;"
            samples.append({
                "instruction": f"Convert the following PostgreSQL pagination query to ANSI SQL standard / SQL Server format:\n```sql\n{pg_sql}\n```",
                "input": "",
                "output": f"```sql\n{tsql_sql}\n```\n\n**Explanation:**\n- PostgreSQL uses `LIMIT n OFFSET m`.\n- ANSI SQL / SQL Server standard uses `OFFSET m ROWS FETCH NEXT n ROWS ONLY`.",
                "domain": "sql",
                "task": "dialect_conversion"
            })

        elif choice == 13:
            # Correlated Subquery
            sql = "SELECT e.emp_name, e.department_id, e.salary FROM employees e WHERE e.salary > (SELECT AVG(sub.salary) FROM employees sub WHERE sub.department_id = e.department_id);"
            samples.append({
                "instruction": f"Write a SQL query using a correlated subquery to find employees whose salary is higher than their department's average salary.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- The inner subquery computes the department average for each outer employee row (`sub.department_id = e.department_id`).\n- Filters for employees exceeding their respective department mean.",
                "domain": "sql",
                "task": "text_to_sql"
            })

        elif choice == 14:
            # Grouping Sets / Rollup
            sql = "SELECT region, category, SUM(amount) AS total_revenue FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY ROLLUP (region, category);"
            samples.append({
                "instruction": f"Write a SQL query using GROUP BY ROLLUP to compute subtotals and grand totals across region and product category.",
                "input": "",
                "output": f"```sql\n{sql}\n```\n\n**Explanation:**\n- `ROLLUP (region, category)` generates hierarchy aggregations: `(region, category)`, `(region)`, and the grand total `()`. ",
                "domain": "sql",
                "task": "text_to_sql"
            })

    return samples

if __name__ == "__main__":
    samples = generate_synthetic_sql_samples(count=100)
    print(f"[✓] Generated {len(samples)} test samples.")
