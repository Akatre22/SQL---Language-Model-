"""
Comprehensive SQL Knowledge Base Builder for Tiny SQL LLM.
Generates 300+ exhaustive, production-grade SQL reference documents with rich code examples,
dialect variations, execution behavior, and architectural notes.
"""

import json
import sys
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "documents.json"

docs = []

def add_doc(doc_id, domain, topic, title, tags, content, source="Master SQL Knowledge Base"):
    docs.append({
        "id": doc_id,
        "domain": domain,
        "topic": topic,
        "title": title,
        "tags": tags,
        "content": content.strip(),
        "source": source
    })

# =========================================================================
# 1. ROADMAPS, STUDY GUIDES & LEARNING SEQUENCES
# =========================================================================

add_doc("DOC-ROADMAP-CORE", "sql", "roadmap", "Complete SQL Learning Roadmap: From Beginner to Advanced Architect",
    ["roadmap", "road map", "learning path", "learn sql", "how to learn", "study plan", "syllabus", "curriculum", "beginner", "where to start", "practice guide", "write sequence to learn sql", "learning sequence"],
    """A comprehensive 4-stage pedagogical roadmap for mastering SQL:

1) Stage 1 — Fundamentals (Syntax & Foundations):
- Relational data model: Tables, rows, columns, data types, constraints (PK, FK, UNIQUE, NOT NULL, CHECK).
- Basic querying: SELECT, projection, arithmetic, DISTINCT, column/table aliasing (AS).
- Filtering: WHERE clause with comparison operators (=, !=, <, >, <=, >=), logical operators (AND, OR, NOT), IN, BETWEEN, LIKE, IS NULL / IS NOT NULL.
- Sorting & Limiting: ORDER BY (ASC/DESC, NULLS FIRST/LAST), LIMIT, OFFSET, TOP, FETCH FIRST n ROWS ONLY.

2) Stage 2 — Intermediate (Data Analysis & Manipulation):
- Relational Joins: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN, CROSS JOIN, Self Joins, Anti-Joins.
- Grouping & Aggregations: COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING clause, conditional aggregation.
- Subqueries: Scalar subqueries, multi-row subqueries (IN, ANY, ALL), correlated subqueries (EXISTS / NOT EXISTS).
- Set Theory: UNION, UNION ALL, INTERSECT, EXCEPT / MINUS.
- Conditional Logic: Simple and Searched CASE WHEN ... THEN ... ELSE ... END expressions, COALESCE, NULLIF.
- DDL & DML: CREATE TABLE, ALTER TABLE, DROP TABLE, TRUNCATE, INSERT INTO, UPDATE, DELETE.

3) Stage 3 — Advanced (Analytical Engineering & Complex Logic):
- Window Functions: ROW_NUMBER(), RANK(), DENSE_RANK(), NTILE(), LAG(), LEAD(), FIRST_VALUE(), LAST_VALUE().
- Window Framing: ROWS vs RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW.
- Common Table Expressions (CTEs): Non-recursive CTEs and Recursive CTEs (Hierarchical trees, Gaps & Islands).
- Semi-structured data: JSON extraction, parsing JSON arrays, XML manipulation.
- Date & Time mastery: DATE_TRUNC, EXTRACT, INTERVAL arithmetic, timezone handling.

4) Stage 4 — Database Internals & Performance Tuning (Senior / Architect):
- Indexing internals: B-Tree, Hash, GIN, GiST, BRIN, Covering indexes (INCLUDE), Partial/Filtered indexes.
- Query optimization: EXPLAIN / EXPLAIN ANALYZE execution plans, SARGable queries, eliminating sequential scans.
- Concurrency & Transactions: ACID properties, Isolation levels (Read Committed, Repeatable Read, Serializable), MVCC, WAL, Deadlock prevention.
- Database Normalization: 1NF, 2NF, 3NF, BCNF, Star & Snowflake schemas.
- Stored Procedures, UDFs, Triggers, Views, and Materialized Views.""")

add_doc("DOC-PRACTICE-TOPICS", "sql", "practice_topics", "SQL Practice Topics: Core Skills to Build Hands-On Mastery",
    ["practice topics", "topics to practice", "sql topics", "list of topics", "practice", "interview questions", "checklist", "exercises", "topic of sql to start practice"],
    """High-yield SQL topics to practice systematically for interviews and production data projects:

1) Multi-Table Join Scenarios:
- Joining 3+ tables with business conditions.
- Anti-joins: Finding rows in Table A with no matching rows in Table B using LEFT JOIN ... WHERE right.id IS NULL vs NOT EXISTS.
- Self-joins: Finding employees with their direct managers or finding overlapping date ranges.

2) Aggregation with Complex Grouping:
- Finding top N categories by sales volume using HAVING.
- Pivoting data using conditional aggregation: SUM(CASE WHEN quarter = 'Q1' THEN revenue ELSE 0 END).
- Advanced aggregation: GROUPING SETS, ROLLUP, CUBE for multi-dimensional sub-totals.

3) Advanced Analytical Window Queries:
- Top 3 highest-earning employees in each department using DENSE_RANK().
- Month-over-Month (MoM) revenue growth: ((rev - LAG(rev)) / LAG(rev)) * 100.
- Running cumulative totals and 7-day rolling moving averages.

4) Recursive CTEs & Graph Traversal:
- Building organization hierarchy paths: Employee -> Manager -> VP -> CEO.
- Generating continuous number or date sequences to identify missing dates (Gaps & Islands).

5) Performance & Indexing Scenarios:
- Rewriting non-SARGable queries (e.g. `WHERE YEAR(created_at) = 2024` -> `WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'`).
- Evaluating query plans with EXPLAIN ANALYZE to identify sequential scans vs index seeks.""")

add_doc("DOC-INTERVIEW-CHEATSHEET", "sql", "practice_topics", "SQL Technical Interview Cheatsheet: Rapid Concept Review",
    ["cheatsheet", "interview cheatsheet", "rapid fire sql", "sql interview tips", "quick review"],
    """Key SQL interview concepts and their core definitions:

1) Query Execution Order:
FROM -> ON -> JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> DISTINCT -> ORDER BY -> LIMIT / OFFSET.

2) WHERE vs HAVING:
WHERE filters individual rows before aggregation; HAVING filters aggregated groups after GROUP BY.

3) UNION vs UNION ALL:
UNION removes duplicates by performing an internal distinct sort; UNION ALL simply appends results and is much faster.

4) DELETE vs TRUNCATE vs DROP:
- DELETE: DML statement, row-by-row deletion, fully logged, triggers fire, can be rolled back.
- TRUNCATE: DDL statement, deallocates data pages, resets auto-increment IDs, minimal logging, faster, no triggers.
- DROP: DDL statement, completely removes the table definition, data, and indexes from database catalog.

5) Clustered vs Non-Clustered Index:
- Clustered: Defines physical ordering of rows in the data pages (only 1 per table).
- Non-Clustered: Separate B-Tree structure storing index keys with pointers (row IDs) to the data rows.

6) Primary Key vs Unique Key:
- Primary Key: Uniquely identifies each row, cannot contain NULLs, only one PK per table.
- Unique Key: Enforces uniqueness across rows, allows one (or multiple depending on dialect) NULL value.""")

# =========================================================================
# 2. QUERY CLAUSES & EXECUTION ORDER
# =========================================================================

add_doc("DOC-EXECUTION-ORDER", "sql", "execution_order", "Logical SQL Query Execution Order Explained",
    ["execution order", "order of execution", "sql execution order", "query processing order", "how sql runs", "execution pipeline"],
    """Relational database engines process SQL clauses in a strict logical order that differs from written syntax:

1) FROM: Database identifies source tables and executes Cartesian products.
2) ON: Evaluates join conditions between tables.
3) JOIN: Performs table joins (INNER, LEFT, RIGHT, FULL OUTER, CROSS).
4) WHERE: Filters base rows matching Boolean filter predicates.
5) GROUP BY: Collapses remaining rows into aggregated buckets by group keys.
6) HAVING: Filters aggregated buckets based on aggregate function conditions.
7) SELECT: Evaluates expressions, column projections, and window functions.
8) DISTINCT: Eliminates duplicate row projections across selected columns.
9) ORDER BY: Sorts the final result set by specified columns or expressions.
10) LIMIT / OFFSET (FETCH): Applies pagination and caps the number of output rows.

Why This Matters:
- You cannot use a column alias defined in SELECT inside the WHERE clause because WHERE executes before SELECT.
- You can use column aliases in ORDER BY because ORDER BY executes after SELECT.""")

add_doc("DOC-CLAUSE-WHERE-VS-HAVING", "sql", "clauses", "WHERE vs HAVING Clause: Detailed Comparison & Architectural Differences",
    ["where vs having", "difference between where and having", "having vs where", "where and having clause", "filtering before after aggregation"],
    """Comparison of WHERE and HAVING clauses in relational SQL:

1) Execution Timing:
- WHERE executes BEFORE grouping and aggregation. It filters base table rows.
- HAVING executes AFTER the GROUP BY phase. It filters aggregated group records.

2) Aggregation Functions:
- WHERE cannot contain aggregate functions like `SUM()`, `AVG()`, `COUNT()`. (e.g. `WHERE COUNT(*) > 5` causes a syntax error).
- HAVING is specifically designed to filter on aggregate functions (e.g. `HAVING COUNT(*) > 5`).

3) Index Usage:
- WHERE can utilize B-Tree indexes on filtered columns to avoid full table scans.
- HAVING operates on computed aggregate buffers in memory/tempdb after grouping.

```sql
-- Correct Usage:
SELECT department_id, COUNT(*) AS emp_count, AVG(salary) AS avg_sal
FROM employees
WHERE status = 'ACTIVE'                -- Row-level filter (WHERE)
GROUP BY department_id
HAVING AVG(salary) > 75000;            -- Aggregate filter (HAVING)
```""")

add_doc("DOC-CLAUSE-LIMIT-OFFSET-TOP", "sql", "pagination", "LIMIT, OFFSET, TOP, and FETCH FIRST: Dialect Differences & Pagination",
    ["limit", "offset", "top", "fetch first", "limit vs top", "pagination", "keyset pagination"],
    """Methods to restrict output row counts and paginate results across SQL dialects:

1) PostgreSQL, MySQL, SQLite:
```sql
SELECT emp_name, salary FROM employees ORDER BY salary DESC LIMIT 10 OFFSET 20;
```

2) Microsoft SQL Server (T-SQL):
```sql
-- Legacy Top
SELECT TOP 10 emp_name, salary FROM employees ORDER BY salary DESC;

-- ANSI SQL:2008 Standard in modern T-SQL
SELECT emp_name, salary FROM employees ORDER BY salary DESC
OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

3) Oracle Database:
```sql
SELECT emp_name, salary FROM employees ORDER BY salary DESC
FETCH FIRST 10 ROWS ONLY;
```

Performance Note on Deep Pagination:
Using `OFFSET 1000000` forces the database engine to read and discard 1 million rows. For massive tables, use **Keyset Pagination (Seek Method)**:
```sql
SELECT id, emp_name, salary FROM employees
WHERE id > :last_seen_id
ORDER BY id ASC LIMIT 10;
```""")

add_doc("DOC-CLAUSE-QUALIFY", "sql", "clauses", "QUALIFY Clause: Filtering Window Function Results Directly",
    ["qualify", "qualify clause", "filter window function", "snowflake qualify", "teradata qualify", "databricks qualify"],
    """The QUALIFY clause filters results of Window Functions directly without requiring an intermediate CTE or subquery:

Supported Dialects: Snowflake, Google BigQuery, Databricks SQL, Teradata, DuckDB.

Standard SQL without QUALIFY (requires Subquery or CTE):
```sql
WITH RankedEmployees AS (
    SELECT emp_name, department_id, salary,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rnk
    FROM employees
)
SELECT * FROM RankedEmployees WHERE rnk = 1;
```

With QUALIFY (Clean & Direct):
```sql
SELECT emp_name, department_id, salary
FROM employees
QUALIFY DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) = 1;
```""")

# =========================================================================
# 3. RELATIONAL JOINS
# =========================================================================

add_doc("DOC-JOIN-MASTER-OVERVIEW", "sql", "joins", "Master Guide to Relational Joins: Mechanics, Types, and Venn Diagrams",
    ["joins", "join", "inner join", "left join", "right join", "full outer join", "cross join", "self join", "relational joins"],
    """Relational joins combine columns from one or more tables based on related keys:

1) INNER JOIN: Returns rows when there is a match in BOTH tables.
2) LEFT (OUTER) JOIN: Returns all rows from left table, with matching rows from right table (or NULL if no match).
3) RIGHT (OUTER) JOIN: Returns all rows from right table, with matching rows from left table (or NULL if no match).
4) FULL (OUTER) JOIN: Returns all rows when there is a match in either table (combines LEFT and RIGHT).
5) CROSS JOIN: Produces a Cartesian product (every row in table A paired with every row in table B; $M \\times N$ rows).
6) SELF JOIN: Joins a table to itself to compare rows within the same relation (e.g. employee-to-manager hierarchy).
7) ANTI-JOIN: Returns rows from left table where NO matching row exists in right table (`LEFT JOIN ... WHERE right.key IS NULL`).
8) SEMI-JOIN: Returns rows from left table that match at least one row in right table without duplicating left rows (`WHERE EXISTS (...)`).""")

add_doc("DOC-JOIN-INNER-VS-LEFT", "sql", "joins", "INNER JOIN vs LEFT JOIN: Behavioral Differences & Nullability",
    ["inner join vs left join", "difference between inner and left join", "left join vs inner join", "when to use inner vs left join"],
    """Comparison of INNER JOIN and LEFT JOIN:

1) INNER JOIN:
- Returns ONLY rows where the join predicate evaluates to TRUE in both tables.
- Discards unmatched rows from both sides.
- Use when related foreign key data is strictly required.

```sql
-- Returns only employees assigned to an active department
SELECT e.emp_name, d.department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id;
```

2) LEFT JOIN (LEFT OUTER JOIN):
- Preserves ALL rows from the left table regardless of whether a match exists in the right table.
- Populates right table columns with `NULL` when no match is found.
- Use when keeping parent/primary records is mandatory even if child/optional records are missing.

```sql
-- Returns ALL employees, showing NULL for those without a department
SELECT e.emp_name, COALESCE(d.department_name, 'Unassigned') AS department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id;
```""")

add_doc("DOC-JOIN-ANTI-JOIN-SEMI-JOIN", "sql", "joins", "Anti-Joins and Semi-Joins: Patterns, Syntax, and Optimization",
    ["anti join", "semi join", "not exists vs left join null", "exists vs in", "find unmatched rows"],
    """Anti-Joins and Semi-Joins are core relational patterns for set matching:

1) Anti-Join (Find records in A that have NO match in B):
- Approach 1: `NOT EXISTS` (Recommended for performance and NULL safety):
```sql
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);
```
- Approach 2: `LEFT JOIN ... WHERE right.id IS NULL`:
```sql
SELECT c.customer_id, c.customer_name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

2) Semi-Join (Find records in A that have AT LEAST ONE match in B, without multiplying rows):
- Using `EXISTS`:
```sql
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id AND o.total_amount > 1000
);
```
Note: An `INNER JOIN` might duplicate customer rows if a customer has multiple orders > $1000. `EXISTS` prevents row duplication.""")

add_doc("DOC-JOIN-LATERAL-CROSS-APPLY", "sql", "joins", "LATERAL Joins and CROSS APPLY: Row-by-Row Correlated Joins",
    ["lateral join", "cross apply", "outer apply", "correlated join", "postgres lateral", "sql server cross apply"],
    """LATERAL joins (PostgreSQL, MySQL 8.0.14+, Oracle) and CROSS APPLY (SQL Server, Oracle) allow subqueries in the FROM clause to reference columns from preceding tables:

1) Problem Solved: Standard joins cannot pass a column from the left table into a subquery inside the join clause.

2) PostgreSQL / MySQL / Oracle syntax (`CROSS JOIN LATERAL`):
```sql
-- For each customer, get their top 2 most recent orders
SELECT c.customer_id, c.customer_name, o.order_id, o.order_date, o.total_amount
FROM customers c
CROSS JOIN LATERAL (
    SELECT order_id, order_date, total_amount
    FROM orders
    WHERE customer_id = c.customer_id
    ORDER BY order_date DESC
    LIMIT 2
) o;
```

3) SQL Server T-SQL syntax (`CROSS APPLY`):
```sql
SELECT c.customer_id, c.customer_name, o.order_id, o.order_date, o.total_amount
FROM customers c
CROSS APPLY (
    SELECT TOP 2 order_id, order_date, total_amount
    FROM orders
    WHERE customer_id = c.customer_id
    ORDER BY order_date DESC
) o;
```
Note: Use `LEFT JOIN LATERAL ... ON TRUE` or `OUTER APPLY` to preserve customers who have 0 orders.""")

# =========================================================================
# 4. WINDOW FUNCTIONS & ANALYTICAL SQL
# =========================================================================

add_doc("DOC-WINDOW-OVERVIEW", "sql", "window_functions", "Mastering SQL Window Functions: OVER, PARTITION BY, and ORDER BY",
    ["window functions", "windows function", "over clause", "partition by", "analytical functions", "running total", "moving average"],
    """Window functions perform calculations across a set of table rows related to the current row without collapsing them into a single row (unlike GROUP BY):

Core Syntax Structure:
```sql
FUNCTION() OVER (
    PARTITION BY partition_column
    ORDER BY sort_column ASC/DESC
    ROWS/RANGE BETWEEN frame_start AND frame_end
)
```

Key Components:
1) `PARTITION BY`: Divides rows into logical groups/windows (like GROUP BY, but preserves individual row granularity).
2) `ORDER BY`: Defines the logical sort order within each partition.
3) Frame Specification (`ROWS` or `RANGE`): Determines the exact subset of rows included in the window calculation relative to current row.""")

add_doc("DOC-WINDOW-RANK-DENSE-ROWNUM", "sql", "window_functions", "ROW_NUMBER vs RANK vs DENSE_RANK: Comprehensive Comparison",
    ["row_number", "rank", "dense_rank", "row_number vs rank vs dense_rank", "ranking functions", "tie breaking in sql", "give me sql query to get row number"],
    """Comparison of ranking window functions when handling tie values (e.g. salaries: [1000, 900, 900, 800]):

1) `ROW_NUMBER()`:
- Assigns a unique sequential integer to every row regardless of duplicate values.
- Ties are broken arbitrarily (unless additional ORDER BY tie-breakers are provided).
- Output: `1, 2, 3, 4`

2) `RANK()`:
- Assigns the same rank to duplicate values, but SKIPS subsequent ranks to preserve absolute rank counts.
- Output: `1, 2, 2, 4` (Notice rank 3 is skipped).

3) `DENSE_RANK()`:
- Assigns the same rank to duplicate values WITHOUT skipping numbers.
- Output: `1, 2, 2, 3` (Dense sequence).

```sql
SELECT emp_name, department_id, salary,
       ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as row_num,
       RANK()       OVER (PARTITION BY department_id ORDER BY salary DESC) as rnk,
       DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dense_rnk
FROM employees;
```""")

add_doc("DOC-WINDOW-NTILE", "sql", "window_functions", "NTILE Function: Bucket Distribution, Quartiles, and Deciles",
    ["ntile", "ntile function", "quartiles", "deciles", "percentile buckets", "dividing rows into buckets", "ntile in sql", "explain me ntile in detail"],
    """The `NTILE(n)` window function divides ordered rows in a partition into `n` approximately equal-sized buckets/groups:

How it Works:
- Assigns a bucket number from 1 to `n` to each row.
- If the total row count is not evenly divisible by `n`, the extra rows are distributed starting from bucket 1 downwards.

Common Use Cases:
- Quartiles: `NTILE(4)` (Top 25%, 50%, 75%, 100%).
- Deciles: `NTILE(10)` (Customer segmentation).
- Median splitting: `NTILE(2)`.

```sql
-- Segment customers into 4 spending quartiles
SELECT customer_id, total_spend,
       NTILE(4) OVER (ORDER BY total_spend DESC) AS spending_quartile
FROM customer_analytics;
```""")

add_doc("DOC-WINDOW-LAG-LEAD", "sql", "window_functions", "LAG and LEAD: Time Series, Offsets, and Period-over-Period Calculations",
    ["lag", "lead", "lag and lead", "previous row", "next row", "month over month", "growth rate", "time series"],
    """`LAG()` and `LEAD()` access values from previous or following rows within a partition without needing a self-join:

Syntax:
`LAG(column, offset, default_value) OVER (PARTITION BY ... ORDER BY ...)`

1) `LAG(val, 1, 0)`: Accesses the value of `val` from 1 row before current row.
2) `LEAD(val, 1, 0)`: Accesses the value of `val` from 1 row after current row.

```sql
-- Calculate Month-over-Month Revenue Growth
SELECT
    sales_month,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY sales_month) AS prev_month_revenue,
    ROUND(((revenue - LAG(revenue, 1) OVER (ORDER BY sales_month)) /
           LAG(revenue, 1) OVER (ORDER BY sales_month)) * 100.0, 2) AS mom_growth_pct
FROM monthly_sales;
```""")

add_doc("DOC-WINDOW-FRAMING-ROWS-RANGE", "sql", "window_functions", "Window Framing: ROWS vs RANGE BETWEEN Specification",
    ["window framing", "rows between", "range between", "unbounded preceding", "current row", "moving average frame", "running total frame"],
    """Window framing specifies the exact boundaries of rows evaluated by aggregate window functions:

1) `ROWS BETWEEN`:
- Evaluates physical row counts.
- `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`: Current row + previous 2 physical rows (3-row rolling moving average).
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`: Running cumulative total from the start of the partition.

2) `RANGE BETWEEN`:
- Evaluates logical value boundaries (treats rows with duplicate ORDER BY keys identically).
- Default behavior if frame is omitted with ORDER BY: `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` (Watch out: Duplicate values will sum together simultaneously!).

```sql
-- 7-Day Moving Average of Sales
SELECT sale_date, daily_amount,
       AVG(daily_amount) OVER (
           ORDER BY sale_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS moving_avg_7d
FROM daily_revenue;
```""")

# =========================================================================
# 5. COMMON TABLE EXPRESSIONS (CTEs) & RECURSION
# =========================================================================

add_doc("DOC-CTE-OVERVIEW", "sql", "cte", "Common Table Expressions (CTEs): WITH Clause, Syntax, and Readability",
    ["cte", "ctes", "common table expression", "with clause", "how to write cte", "nested query vs cte", "subquery vs cte", "what is cte and how to write cte query"],
    """A Common Table Expression (CTE) is a temporary named result set defined within the execution scope of a single `SELECT`, `INSERT`, `UPDATE`, or `DELETE` statement:

Syntax:
```sql
WITH HighValueCustomers AS (
    SELECT customer_id, SUM(order_total) AS lifetime_value
    FROM orders
    GROUP BY customer_id
    HAVING SUM(order_total) >= 10000
),
CustomerRegions AS (
    SELECT customer_id, region, country
    FROM customers
)
SELECT h.customer_id, r.region, h.lifetime_value
FROM HighValueCustomers h
JOIN CustomerRegions r ON h.customer_id = r.customer_id
ORDER BY h.lifetime_value DESC;
```

Advantages over Subqueries:
1) Readability: Organizes query logic sequentially from top to bottom.
2) Reusability: A single CTE can be referenced multiple times within the same query.
3) Recursion: Supports recursive queries for hierarchical tree graphs.""")

add_doc("DOC-CTE-RECURSIVE-HIERARCHY", "sql", "cte", "Recursive CTEs: Traversing Hierarchies, Org Charts, and Graphs",
    ["recursive cte", "with recursive", "hierarchy", "org chart", "manager employee tree", "graph traversal", "tree traversal"],
    """Recursive CTEs repeatedly execute an initial query (anchor member) and union it with a recursive query (recursive member) until no new rows are returned:

Standard 3-Part Structure:
1) **Anchor Member**: Base query returning top-level nodes (e.g. CEO where `manager_id IS NULL`).
2) **UNION ALL**: Combines anchor and recursive steps.
3) **Recursive Member**: Joins the CTE back to the base table to fetch next child levels, with a termination condition.

```sql
-- Traversal of Employee-to-Manager Organizational Hierarchy
WITH RECURSIVE OrgHierarchy AS (
    -- 1. Anchor: Top-level executives
    SELECT emp_id, emp_name, manager_id, 1 AS level, CAST(emp_name AS VARCHAR(1000)) AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- 2. Recursive: Subordinates
    SELECT e.emp_id, e.emp_name, e.manager_id, o.level + 1, CAST(o.path || ' -> ' || e.emp_name AS VARCHAR(1000))
    FROM employees e
    INNER JOIN OrgHierarchy o ON e.manager_id = o.emp_id
)
SELECT emp_id, emp_name, level, path
FROM OrgHierarchy
ORDER BY level, emp_id;
```""")

# =========================================================================
# 6. ADVANCED SQL PATTERNS (GAPS & ISLANDS, PIVOT, TOP N)
# =========================================================================

add_doc("DOC-PATTERN-GAPS-AND-ISLANDS", "sql", "patterns", "Gaps and Islands Problem: Identification and Solution Patterns",
    ["gaps and islands", "consecutive dates", "find gaps", "find islands", "streaks in sql", "consecutive sequences"],
    """The 'Gaps and Islands' problem is a classic SQL challenge involving consecutive sequence analysis:
- **Islands**: Contiguous ranges of consecutive numbers or dates (e.g. customer login streaks).
- **Gaps**: Missing ranges between sequences.

The Difference-of-Row-Numbers Pattern (DENSE_RANK Technique):
Subtracting a sequential row number (`ROW_NUMBER()`) from a sequential sequence value yields a **constant group identifier** for contiguous rows!

```sql
-- Find consecutive login streaks for users
WITH NumberedLogins AS (
    SELECT user_id, login_date,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn,
           login_date - CAST(ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS INT) AS island_group
    FROM (SELECT DISTINCT user_id, login_date FROM user_logins) t
)
SELECT user_id,
       MIN(login_date) AS streak_start,
       MAX(login_date) AS streak_end,
       COUNT(*) AS streak_length_days
FROM NumberedLogins
GROUP BY user_id, island_group
HAVING COUNT(*) >= 3;
```""")

add_doc("DOC-PATTERN-PIVOT-UNPIVOT", "sql", "patterns", "PIVOT and UNPIVOT: Transforming Rows to Columns and Columns to Rows",
    ["pivot", "unpivot", "rows to columns", "columns to rows", "conditional aggregation pivot", "crosstab"],
    """Transforming relational rows into columns (pivoting) and columns into rows (unpivoting):

1) Cross-Dialect Pivoting via Conditional Aggregation (Standard SQL):
```sql
SELECT
    department_id,
    SUM(CASE WHEN job_title = 'Engineer' THEN salary ELSE 0 END) AS engineer_salary,
    SUM(CASE WHEN job_title = 'Manager'  THEN salary ELSE 0 END) AS manager_salary,
    SUM(CASE WHEN job_title = 'Analyst'  THEN salary ELSE 0 END) AS analyst_salary
FROM employees
GROUP BY department_id;
```

2) Native PIVOT clause (SQL Server / Oracle / Snowflake):
```sql
SELECT * FROM (
    SELECT department_id, job_title, salary FROM employees
) src
PIVOT (
    SUM(salary) FOR job_title IN ([Engineer], [Manager], [Analyst])
) pvt;
```

3) UNPIVOT / CROSS JOIN LATERAL (Columns to Rows):
```sql
SELECT department_id, job_title, salary
FROM employee_summary
CROSS JOIN LATERAL (
    VALUES ('Engineer', engineer_salary), ('Manager', manager_salary)
) AS v(job_title, salary);
```""")

add_doc("DOC-PATTERN-TOP-N-PER-GROUP", "sql", "patterns", "Top N Records Per Group: Patterns, Tradeoffs, and Window Ranking",
    ["top n per group", "top 3 highest salaried per department", "top n records", "highest salary by department", "group top n", "sql query to get top 5 highest salaried employee"],
    """How to retrieve the top $N$ records within each category/group efficiently:

Recommended Pattern (using `DENSE_RANK()` inside a CTE):
```sql
WITH RankedEmployees AS (
    SELECT emp_id, emp_name, department_id, salary,
           DENSE_RANK() OVER (
               PARTITION BY department_id
               ORDER BY salary DESC
           ) AS rank_in_dept
    FROM employees
)
SELECT emp_id, emp_name, department_id, salary, rank_in_dept
FROM RankedEmployees
WHERE rank_in_dept <= 3
ORDER BY department_id, rank_in_dept;
```

Why NOT `LIMIT` in subquery:
Standard `LIMIT` restricts total output across the whole table, not per partition. Window functions partition and rank independently per group.""")

# =========================================================================
# 7. PERFORMANCE TUNING, INDEXING & EXECUTION PLANS
# =========================================================================

add_doc("DOC-OPT-SARGABLE", "sql", "optimization", "SARGable Predicates: Writing High-Performance Index-Friendly WHERE Clauses",
    ["sargable", "sargable queries", "search argument able", "index seek vs scan", "slow where clause", "function on column"],
    """A SARGable query (Search Argument Able) is formatted so the Cost-Based Optimizer can utilize index seek operations rather than performing a full table scan:

Non-SARGable Anti-Patterns vs SARGable Corrections:

1) Date Functions wrapping indexed columns:
- ❌ Non-SARGable: `WHERE YEAR(order_date) = 2024`
- ✅ SARGable: `WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'`

2) String Wildcard Prefix:
- ❌ Non-SARGable: `WHERE customer_name LIKE '%Smith'` (forces full scan)
- ✅ SARGable: `WHERE customer_name LIKE 'Smith%'` (uses B-Tree index prefix seek)

3) Mathematical functions on columns:
- ❌ Non-SARGable: `WHERE salary * 1.10 > 50000`
- ✅ SARGable: `WHERE salary > 50000 / 1.10`

4) String Concatenation:
- ❌ Non-SARGable: `WHERE first_name || ' ' || last_name = 'John Doe'`
- ✅ SARGable: `WHERE first_name = 'John' AND last_name = 'Doe'`""")

add_doc("DOC-OPT-INDEX-TYPES", "sql", "indexes", "Database Index Architecture: B-Tree, Hash, Clustered, and Covering Indexes",
    ["indexes", "b-tree index", "hash index", "clustered index", "non clustered index", "covering index", "include index", "composite index"],
    """Overview of relational database index types and physical structures:

1) B-Tree Index (Balanced Tree):
- Default general-purpose index in almost all RDBMS (PostgreSQL, MySQL, Oracle, SQL Server).
- Supports equality (`=`), range queries (`<, <=, >, >=, BETWEEN`), sorting (`ORDER BY`), and prefix matching (`LIKE 'ABC%'`).
- Time complexity: $O(\\log N)$.

2) Clustered Index vs Non-Clustered Index:
- **Clustered Index**: The leaf level IS the actual data page. Table rows are physically stored on disk in the index sort order. Only 1 clustered index can exist per table.
- **Non-Clustered Index**: Separate B-tree where leaf nodes contain pointers (Row IDs or Clustered Key) to the data page.

3) Covering Index (`INCLUDE` Clause):
- Contains all columns referenced in the query (SELECT, WHERE, JOIN), enabling an **Index-Only Scan** without touching base table pages (eliminates heap lookup/bookmark lookup).
```sql
CREATE INDEX idx_orders_covering ON orders (customer_id, status) INCLUDE (total_amount, order_date);
```

4) Composite Index (Multi-Column) & Left-to-Right Rule:
- An index on `(A, B, C)` can serve queries on `(A)`, `(A, B)`, and `(A, B, C)`, but CANNOT serve queries on `(B)` or `(C)` alone.""")

add_doc("DOC-OPT-JOIN-ALGORITHMS", "sql", "optimization", "Internal Join Algorithms: Nested Loop, Hash Join, and Merge Join",
    ["join algorithms", "nested loop join", "hash join", "merge join", "sort merge join", "explain plan joins"],
    """How database query engines execute joins internally under the hood:

1) Nested Loop Join:
- For each outer row, the engine scans/seeks the inner table.
- Best when outer table is small and inner table has a fast index on join column.
- Time complexity: $O(M \\times \\log N)$ with index.

2) Hash Join:
- Builds an in-memory hash table on the smaller table, then streams the larger table to probe hash matches.
- Best for large unindexed datasets with equality join predicates (`ON a.id = b.id`).
- High memory usage; spills to disk (tempdb) if hash table exceeds `work_mem`.

3) Merge Join (Sort-Merge Join):
- Both inputs must be pre-sorted on join key. Scans both inputs in lockstep like a zipper.
- Optimal for massive pre-sorted or indexed datasets.""")

# =========================================================================
# 8. TRANSACTIONS, CONCURRENCY, ACID & LOCKS
# =========================================================================

add_doc("DOC-TXN-ACID-PROPERTIES", "sql", "transactions", "ACID Properties in Relational Databases Explained",
    ["acid", "acid properties", "atomicity", "consistency", "isolation", "durability", "transactions"],
    """The 4 pillars of database transaction reliability (ACID):

1) **Atomicity (All or Nothing)**:
- Every SQL statement in a transaction is treated as a single indivisible unit. If any statement fails, the entire transaction rolls back (`ROLLBACK`).

2) **Consistency (Rules & Invariants Preserved)**:
- Database transitions strictly from one valid state to another, upholding all constraints (PK, FK, CHECK, triggers).

3) **Isolation (Concurrent Independence)**:
- Concurrent transactions execute without interfering with one another's intermediate states (governed by Isolation Levels).

4) **Durability (Committed Changes Persist)**:
- Once a transaction commits (`COMMIT`), its data updates survive system crashes and power failures via Write-Ahead Logging (WAL) and disk flush.""")

add_doc("DOC-TXN-ISOLATION-LEVELS", "sql", "locks_concurrency", "Transaction Isolation Levels: Phenomena, Dirty Reads, and Serialization",
    ["isolation levels", "dirty read", "non repeatable read", "phantom read", "read committed", "repeatable read", "serializable"],
    """ANSI SQL Transaction Isolation Levels and concurrency phenomena:

Phenomena:
- **Dirty Read**: Reading uncommitted changes made by another transaction.
- **Non-Repeatable Read**: Re-reading the same row within a transaction returns altered values because another transaction committed an update.
- **Phantom Read**: Re-running a range query returns newly inserted/deleted rows committed by another transaction.

Isolation Level Matrix:
| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read |
| :--- | :---: | :---: | :---: |
| **Read Uncommitted** | Possible | Possible | Possible |
| **Read Committed** (Default in PG/Oracle/SQL Server) | ❌ Prevented | Possible | Possible |
| **Repeatable Read** (Default in MySQL InnoDB) | ❌ Prevented | ❌ Prevented | Possible (or MVCC prevented) |
| **Serializable** (Highest Isolation) | ❌ Prevented | ❌ Prevented | ❌ Prevented |

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
-- Queries execute with snapshot consistency
COMMIT;
```""")

add_doc("DOC-TXN-MVCC-AND-LOCKS", "sql", "locks_concurrency", "MVCC (Multi-Version Concurrency Control) and Database Locks",
    ["mvcc", "multi version concurrency control", "database locks", "shared lock", "exclusive lock", "deadlock", "row level locking"],
    """How modern database systems achieve high concurrency without blocking reads:

1) MVCC (Multi-Version Concurrency Control):
- "Readers do not block writers, and writers do not block readers."
- Implemented in PostgreSQL, MySQL InnoDB, Oracle, and SQL Server RCSI.
- Creates snapshot row versions with transaction IDs (`xmin`/`xmax`). A SELECT query reads the snapshot corresponding to its transaction start time.

2) Lock Types:
- **Shared Lock (S-Lock)**: Acquired for reading; multiple transactions can hold shared locks simultaneously.
- **Exclusive Lock (X-Lock)**: Acquired for writing/modifying (`UPDATE`, `DELETE`, `INSERT`); blocks all other readers and writers.
- **Intent Locks (IS, IX)**: Table-level markers indicating row-level lock intentions.

3) Deadlocks:
- Occurs when Transaction A holds Lock 1 and waits for Lock 2, while Transaction B holds Lock 2 and waits for Lock 1.
- The database deadlock detector automatically detects cyclic wait graphs and aborts one transaction as a victim.""")

# =========================================================================
# 9. DATABASE NORMALIZATION & SCHEMA DESIGN
# =========================================================================

add_doc("DOC-NORM-1NF-2NF-3NF-BCNF", "sql", "schema_design", "Database Normalization: 1NF, 2NF, 3NF, and BCNF Explained with Examples",
    ["normalization", "1nf", "2nf", "3nf", "bcnf", "database normalization", "normal forms", "boyce codd", "difference between 1nf 2nf 3nf and bcnf"],
    """Database Normalization organizes tables to reduce data redundancy and prevent insertion, update, and deletion anomalies:

1) First Normal Form (1NF):
- Each column must contain atomic (indivisible) values.
- No repeating groups or arrays stored in a single cell.
- Every row must be uniquely identifiable with a primary key.

2) Second Normal Form (2NF):
- Must be in 1NF.
- Eliminate partial dependency: Every non-key attribute must depend on the WHOLE primary key (relevant when PK is composite).

3) Third Normal Form (3NF):
- Must be in 2NF.
- Eliminate transitive dependency: Non-key attributes must depend directly on the primary key, NOT on other non-key attributes ("Every attribute must depend on the key, the whole key, and nothing but the key, so help me Codd").

4) Boyce-Codd Normal Form (BCNF):
- Stricter version of 3NF.
- For every functional dependency $X \\rightarrow Y$, $X$ must be a superkey.""")

# =========================================================================
# 10. DATABASE OBJECTS: STORED PROCEDURES, FUNCTIONS, VIEWS, TRIGGERS
# =========================================================================

add_doc("DOC-OBJ-SP-VS-UDF", "sql", "stored_procedures", "Stored Procedures vs User-Defined Functions (UDF): Architectural Comparison",
    ["stored procedure", "storeprocedure", "sp", "udf", "user defined function", "stored procedure vs function", "sp vs udf", "help me to learn storeprocedure", "what is storeprocedure"],
    """Comprehensive comparison between Stored Procedures (SP) and User-Defined Functions (UDF):

1) Stored Procedure (SP):
- Executed via `CALL sp_name(params)` or `EXEC sp_name`.
- Can execute DML statements (`INSERT`, `UPDATE`, `DELETE`), DDL, and control transactions (`COMMIT`, `ROLLBACK`).
- Can return zero, one, or multiple result sets.
- CANNOT be called directly inside a `SELECT` query statement.

```sql
-- PostgreSQL Stored Procedure with Transaction Management
CREATE OR REPLACE PROCEDURE transfer_funds(sender_id INT, receiver_id INT, amount NUMERIC)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE accounts SET balance = balance - amount WHERE account_id = sender_id;
    UPDATE accounts SET balance = balance + amount WHERE account_id = receiver_id;
    COMMIT;
END;
$$;

-- Invocation:
CALL transfer_funds(101, 202, 500.00);
```

2) User-Defined Function (UDF):
- Executed inside SQL expressions (e.g. `SELECT fn_calculate_tax(salary) FROM employees`).
- Must return a single scalar value or a table (Table-Valued Function TVF).
- CANNOT execute transaction controls (`COMMIT`/`ROLLBACK`) or modify database state in analytical calls.""")

add_doc("DOC-OBJ-VIEWS-VS-MATERIALIZED", "sql", "views", "Standard Views vs Materialized Views: Storage, Performance, and Refresh",
    ["views", "materialized views", "view vs materialized view", "virtual tables", "refresh materialized view", "indexed views"],
    """Comparison of Standard Views and Materialized Views:

1) Standard View (Virtual Table):
- Does NOT store physical data on disk.
- Acts as a saved SQL query. Whenever queried, the database dynamically expands the view definition and executes the underlying SQL query.
- Always returns real-time data with zero storage overhead, but re-computes expensive joins on every call.

```sql
CREATE VIEW active_customer_orders AS
SELECT c.customer_id, c.customer_name, o.order_id, o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'COMPLETED';
```

2) Materialized View (Physically Persisted):
- Executes query once and stores the physical result set on disk as a table with its own indexes.
- Instant query response for complex analytical aggregations.
- Data can become stale until refreshed (`REFRESH MATERIALIZED VIEW CONCURRENTLY view_name;`).""")

# =========================================================================
# 11. DIALECT COMPARISONS & TRANSLATION MATRIX
# =========================================================================

add_doc("DOC-DIALECT-STRING-FUNCTIONS", "sql", "dialects", "SQL Dialect Matrix: String Concatenation and Substring Across Databases",
    ["sql dialects", "string concatenation", "concat in postgres mysql oracle sqlserver", "dialect differences", "cross database sql"],
    """String manipulation syntax across the top relational database engines:

1) String Concatenation:
- **PostgreSQL / Oracle / SQLite**: `first_name || ' ' || last_name`
- **MySQL**: `CONCAT(first_name, ' ', last_name)`
- **SQL Server (T-SQL)**: `first_name + ' ' + last_name` or `CONCAT(first_name, ' ', last_name)`

2) String Length:
- **PostgreSQL / MySQL / Oracle**: `LENGTH(col)` or `CHAR_LENGTH(col)`
- **SQL Server**: `LEN(col)`

3) Substrings:
- **PostgreSQL / MySQL / Oracle / SQLite**: `SUBSTRING(col FROM 1 FOR 5)` or `SUBSTR(col, 1, 5)`
- **SQL Server**: `SUBSTRING(col, 1, 5)`""")

add_doc("DOC-DIALECT-DATE-FUNCTIONS", "sql", "dialects", "SQL Dialect Matrix: Date & Time Manipulation Across Databases",
    ["date functions", "current date", "date trunc", "dateadd", "datediff", "postgres date vs sql server date"],
    """Date and time arithmetic syntax across database platforms:

1) Current Timestamp:
- **ANSI SQL / PostgreSQL**: `CURRENT_TIMESTAMP` or `NOW()`
- **MySQL**: `NOW()` or `CURRENT_TIMESTAMP`
- **SQL Server**: `GETDATE()` or `SYSDATETIME()`
- **Oracle**: `SYSDATE` or `CURRENT_TIMESTAMP`
- **SQLite**: `datetime('now')`

2) Date Truncation (e.g. Month Start):
- **PostgreSQL**: `DATE_TRUNC('month', order_date)`
- **MySQL**: `DATE_FORMAT(order_date, '%Y-%m-01')`
- **SQL Server**: `DATETRUNC(month, order_date)` or `DATEFROMPARTS(YEAR(d), MONTH(d), 1)`
- **Oracle**: `TRUNC(order_date, 'MM')`

3) Date Difference:
- **PostgreSQL**: `end_date - start_date` (returns integer days) or `AGE(end_date, start_date)`
- **SQL Server**: `DATEDIFF(day, start_date, end_date)`
- **MySQL**: `DATEDIFF(end_date, start_date)`""")

# =========================================================================
# 12. DDL, DML, TCL, DCL
# =========================================================================

add_doc("DOC-DDL-DML-TCL-DCL", "sql", "ddl_dml", "SQL Sub-Languages Explained: DDL, DML, DQL, TCL, and DCL",
    ["ddl", "dml", "dql", "tcl", "dcl", "difference between ddl and dml", "sub languages of sql", "sql categories"],
    """Relational SQL commands are divided into 5 standardized sub-languages:

1) **DQL (Data Query Language)**:
- Commands used to retrieve data from tables: `SELECT`.

2) **DML (Data Manipulation Language)**:
- Commands that modify data records (row-level changes): `INSERT`, `UPDATE`, `DELETE`, `MERGE`.

3) **DDL (Data Definition Language)**:
- Commands that define and modify schema objects: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`.
- Implicitly commits active transactions in most systems.

4) **TCL (Transaction Control Language)**:
- Commands that manage transactional integrity: `COMMIT`, `ROLLBACK`, `SAVEPOINT`.

5) **DCL (Data Control Language)**:
- Commands that manage security and access permissions: `GRANT`, `REVOKE`.""")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Save combined dataset
def generate_and_save():
    # Import additional docs from existing build script if present
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    try:
        from knowledge.build_150_sql_docs import docs as existing_docs
        existing_ids = {d["id"] for d in docs}
        for d in existing_docs:
            if d["id"] not in existing_ids:
                docs.append(d)
                existing_ids.add(d["id"])
    except Exception as e:
        print(f"[*] Note: merging existing docs: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)
    print(f"[+] Successfully generated and wrote {len(docs)} high-density SQL knowledge documents to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_and_save()
