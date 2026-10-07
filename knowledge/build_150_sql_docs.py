"""
Comprehensive 150+ SQL Knowledge Base Builder for Tiny SQL LLM.
Generates 150+ unique, exhaustive, and properly formatted SQL reference documents.
"""

import json
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "documents.json"

docs = [
    # -------------------------------------------------------------------------
    # 1. ROADMAPS & STUDY GUIDES (5 docs)
    # -------------------------------------------------------------------------
    {
        "id": "DOC-SQL-ROADMAP",
        "domain": "sql",
        "topic": "roadmap",
        "title": "Complete SQL Learning Roadmap & Step-by-Step Study Guide",
        "tags": ["roadmap", "road map", "learning path", "learn sql", "how to learn", "study plan", "syllabus", "curriculum", "beginner", "where to start", "practice guide", "write sequence to learn sql", "learning sequence"],
        "content": "A structured step-by-step roadmap to master SQL from absolute beginner to senior database engineer:\n\n1) Phase 1 — SQL Fundamentals (Beginner):\n- Relational concepts: Tables, Rows, Columns, Primary Keys, Foreign Keys.\n- Basic queries: SELECT, DISTINCT, WHERE, AND/OR/NOT, IN, BETWEEN, LIKE, IS NULL.\n- Sorting & Limiting: ORDER BY, LIMIT, OFFSET, TOP.\n- Basic calculations: COUNT, SUM, AVG, MIN, MAX.\n\n2) Phase 2 — Intermediate SQL (Data Analysis & Manipulation):\n- Table Joins: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN, CROSS JOIN, Self Joins.\n- Aggregations: GROUP BY, HAVING clause, COUNT(DISTINCT).\n- Subqueries: Scalar subqueries, multi-row subqueries (IN, ANY, ALL), correlated subqueries (EXISTS).\n- Set Operations: UNION, UNION ALL, INTERSECT, EXCEPT.\n- Conditional logic: CASE WHEN ... THEN ... ELSE ... END.\n- DDL & DML: CREATE TABLE, ALTER TABLE, DROP TABLE, INSERT, UPDATE, DELETE, TRUNCATE.\n\n3) Phase 3 — Advanced SQL (Analytics & Data Engineering):\n- Window Functions: ROW_NUMBER(), RANK(), DENSE_RANK(), NTILE(), LAG(), LEAD(), Cumulative Running Totals, Moving Averages.\n- Common Table Expressions (CTEs): Non-recursive CTEs and Recursive CTEs for hierarchical tree structures.\n- Date & Time manipulation: DATE_TRUNC, EXTRACT, INTERVAL arithmetic, timezone handling.\n- String & Regex functions: CONCAT, SUBSTRING, COALESCE, NULLIF, regex matching.\n\n4) Phase 4 — Database Internals & Performance Tuning (Expert):\n- Indexing Strategies: B-Tree, Hash, Composite Indexes, Covering Indexes (INCLUDE), Clustered vs Non-Clustered.\n- Query Optimization: EXPLAIN / EXPLAIN ANALYZE execution plans, SARGable predicates, eliminating full table scans.\n- Database Objects: Stored Procedures (SP), User-Defined Functions (UDF), Standard Views, Materialized Views, Triggers.\n- Concurrency & Transactions: ACID properties, isolation levels (Read Committed, Repeatable Read, Serializable), locking mechanisms.\n- Database Normalization: 1NF, 2NF, 3NF, BCNF, denormalization tradeoffs.",
        "source": "Master SQL Engineering Roadmap"
    },
    {
        "id": "DOC-SQL-PRACTICE-TOPICS",
        "domain": "sql",
        "topic": "practice_topics",
        "title": "Essential SQL Topics & Practice Checklist for Interviews & Projects",
        "tags": ["practice topics", "topics to practice", "sql topics", "list of topics", "practice", "interview questions", "checklist", "exercises", "topic of sql to start practice"],
        "content": "Top SQL topics to practice systematically for real-world mastery and technical interviews:\n\n1) Filtering & Basic Retrieval:\n- Filtering with multiple AND/OR logic, NOT IN with NULL caveats, wildcard search with LIKE '%abc%'.\n- Handling NULL values properly with IS NULL / IS NOT NULL and COALESCE().\n\n2) Relational Joins:\n- Joining 3+ tables with foreign keys.\n- Identifying missing records using LEFT JOIN ... WHERE right.id IS NULL (Anti-Join).\n- Many-to-many relationship queries using associative junction tables.\n\n3) Aggregation & Group Filtering:\n- Calculating metrics grouped by multiple columns.\n- Filtering aggregated groups using HAVING (e.g. customers with total spend > $10,000).\n- Conditional aggregation using SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END).\n\n4) Subqueries & Set Theory:\n- Correlated subqueries: finding employees earning more than their department average.\n- EXISTS vs IN performance on large datasets.\n- Combining result sets using UNION vs UNION ALL.\n\n5) Window Functions:\n- Top N records per category using ROW_NUMBER() or DENSE_RANK() with PARTITION BY.\n- Calculating Month-over-Month growth rate using (current_month - LAG(current_month, 1)) / LAG(current_month, 1).\n- Running cumulative totals using SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING).\n\n6) CTEs & Hierarchies:\n- Refactoring complex nested subqueries into readable WITH clauses.\n- Querying organizational manager-employee hierarchies using WITH RECURSIVE.\n\n7) Schema Design & Optimization:\n- Designing tables with PRIMARY KEY, FOREIGN KEY (ON DELETE CASCADE), UNIQUE, and CHECK constraints.\n- Creating B-Tree indexes on filtered and joined columns.\n- Analyzing EXPLAIN output to verify index usage.",
        "source": "SQL Practice & Interview Guide"
    },
    {
        "id": "DOC-SQL-INTERVIEW-CHEATSHEET",
        "domain": "sql",
        "topic": "practice_topics",
        "title": "SQL Interview Cheatsheet: Top 25 Rapid-Fire Architectural Concepts",
        "tags": ["cheatsheet", "interview cheatsheet", "rapid fire sql", "sql interview tips", "quick review"],
        "content": "Quick architectural reference for technical SQL interviews:\n\n1) Execution Order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> DISTINCT -> ORDER BY -> LIMIT.\n2) WHERE vs HAVING: WHERE filters rows before grouping; HAVING filters aggregated buckets.\n3) UNION vs UNION ALL: UNION removes duplicates (slow sort); UNION ALL concatenates (fast).\n4) DELETE vs TRUNCATE: DELETE is DML (logged per row, rollbackable); TRUNCATE is DDL (deallocates pages, resets identity).\n5) Clustered vs Non-Clustered Index: Clustered determines physical table sort order (1 per table); Non-clustered is a secondary pointer tree.\n6) SARGable: Avoid wrapping columns in functions inside WHERE (e.g. use `date >= '2025-01-01'` instead of `YEAR(date) = 2025`).\n7) Stored Procedure vs Function: Procedure uses CALL, executes DML, manages transactions; Function uses SELECT, returns a value, no transactions.",
        "source": "SQL Interview Master Guide"
    },
    {
        "id": "DOC-SQL-BEGINNER-GUIDE",
        "domain": "sql",
        "topic": "roadmap",
        "title": "SQL Beginner Guide: Relational Model, Tables, Rows, and Data Types",
        "tags": ["beginner guide", "sql for beginners", "relational model", "tables rows columns", "what is sql"],
        "content": "An introduction to relational database systems for beginners:\n\n1) Relational Database Concepts: Data is organized into structured two-dimensional tables (relations) comprising rows (records/tuples) and columns (attributes/fields).\n2) Primary Key: Ensures every row has a unique identifier.\n3) Foreign Key: Establishes connections between related tables (e.g. linking order records to customer records).\n4) Declarative Nature: In SQL, you declare WHAT data you want, and the database query engine determines HOW to retrieve it efficiently.",
        "source": "SQL Beginner Handbook"
    },
    {
        "id": "DOC-SQL-PERFORMANCE-CHECKLIST",
        "domain": "sql",
        "topic": "optimization",
        "title": "Production SQL Performance Optimization Checklist",
        "tags": ["performance checklist", "optimization checklist", "slow query checklist", "tuning guide"],
        "content": "10-point checklist for auditing and accelerating slow production SQL queries:\n\n1) Eliminate SELECT * — Project only required columns to reduce memory buffer usage.\n2) Check SARGability — Ensure WHERE predicates do not wrap indexed columns in functions.\n3) Verify Index Usage — Run EXPLAIN ANALYZE to ensure Index Seeks instead of Sequential Table Scans.\n4) Avoid Redundant Sorting — Use UNION ALL instead of UNION when duplicates are impossible.\n5) Replace Correlated Subqueries — Refactor into JOINs or CTEs with window functions where applicable.\n6) Check Join Key Data Types — Mismatched join types prevent index usage (e.g. INT vs VARCHAR).\n7) Filter Early — Apply WHERE filters before joining large intermediate tables.\n8) Use Keyset Pagination — Replace deep `OFFSET 1000000` with `WHERE id > last_seen_id`.\n9) Update Statistics — Ensure the Cost-Based Optimizer has fresh table statistics (`ANALYZE table`).\n10) Add Covering Indexes — Use `INCLUDE` to create Index-Only Scans for high-frequency queries.",
        "source": "Database Performance Tuning"
    }
]

# Helper function to add structured documents easily
def add_doc(doc_id, domain, topic, title, tags, content, source="SQL Reference Manual"):
    docs.append({
        "id": doc_id,
        "domain": domain,
        "topic": topic,
        "title": title,
        "tags": tags,
        "content": content,
        "source": source
    })

# -------------------------------------------------------------------------
# 2. CORE QUERY CLAUSES & SYNTAX (15 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-SELECT-DEEP", "sql", "clauses", "SELECT Statement: Projection, Mathematical Expressions, and Aliasing",
    ["select", "select statement", "column projection", "aliasing", "as keyword", "select columns"],
    "The SELECT statement specifies the column projections and scalar calculations returned by a query:\n\n1) Column Projection: Project specific columns to reduce I/O.\n2) Aliasing (AS): Rename columns or table references.\n3) Expressions: Compute mathematical, string, or conditional expressions inline.\n\n```sql\nSELECT emp_id, first_name || ' ' || last_name AS full_name, salary * 1.10 AS next_year_salary FROM employees;\n```")

add_doc("DOC-SQL-DISTINCT-DEEP", "sql", "clauses", "SELECT DISTINCT: Multi-Column Deduplication and Execution Cost",
    ["distinct", "select distinct", "deduplication", "unique rows", "eliminate duplicates"],
    "SELECT DISTINCT removes duplicate rows across all projected columns:\n\n1) Multi-Column Scope: Uniqueness is evaluated across the combined tuple of all SELECT columns.\n2) Cost: Incurs an implicit sorting or hashing step in memory/tempdb.\n\n```sql\nSELECT DISTINCT department_id, job_title FROM employees;\n```")

add_doc("DOC-SQL-WHERE-DEEP", "sql", "filtering", "WHERE Clause: Row-Level Filtering, Predicates, and Comparison Operators",
    ["where", "where clause", "row filtering", "predicates", "filter rows", "comparison operators"],
    "WHERE filters individual table records before grouping and aggregation:\n\n1) Operators: `=`, `<>`, `!=`, `<`, `<=`, `>`, `>=`, `BETWEEN`, `IN`, `LIKE`, `IS NULL`.\n2) Logical Combining: `AND`, `OR`, `NOT`.\n\n```sql\nSELECT * FROM orders WHERE status = 'COMPLETED' AND total_amount >= 500;\n```")

add_doc("DOC-SQL-AND-OR-NOT-DEEP", "sql", "filtering", "Boolean Logic: AND, OR, NOT Precedence and Parentheses Grouping",
    ["and", "or", "not", "boolean logic", "operator precedence", "compound conditions"],
    "Boolean operator precedence rules:\n\n1) Hierarchy: `NOT` evaluates first, `AND` second, `OR` third.\n2) Always use parentheses `()` to avoid logic bugs with mixed `AND` / `OR` conditions.\n\n```sql\nSELECT * FROM accounts WHERE (account_type = 'PREMIUM' OR balance > 50000) AND is_active = TRUE;\n```")

add_doc("DOC-SQL-IN-NOT-IN", "sql", "filtering", "IN and NOT IN Operators: List Membership and the NULL Trap",
    ["in", "not in", "in operator", "not in operator", "null in not in", "membership test"],
    "IN tests if a value matches any element in a list or subquery:\n\n1) NOT IN with NULLs: If the subquery contains ANY NULL, `NOT IN` returns 0 rows (evaluates to UNKNOWN). Use `NOT EXISTS` or filter `WHERE col IS NOT NULL`.\n\n```sql\nSELECT * FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders WHERE customer_id IS NOT NULL);\n```")

add_doc("DOC-SQL-BETWEEN-DEEP", "sql", "filtering", "BETWEEN Operator: Inclusive Range Filtering on Numbers and Dates",
    ["between", "between operator", "inclusive range", "not between", "date ranges"],
    "BETWEEN tests whether a value falls within an inclusive boundary ($low \\le val \\le high$):\n\n1) Inclusivity: Both boundary values are included.\n2) Timestamp Caution: For timestamps, use `>= '2025-01-01' AND < '2025-02-01'` to avoid missing partial days.\n\n```sql\nSELECT * FROM products WHERE unit_price BETWEEN 50 AND 200;\n```")

add_doc("DOC-SQL-LIKE-WILDCARDS", "sql", "filtering", "LIKE, ILIKE and Wildcards (%, _) with ESCAPE Sequences",
    ["like", "ilike", "wildcards", "pattern matching", "case insensitive like", "percent wildcard", "underscore wildcard"],
    "Text pattern matching:\n\n1) `%`: Matches zero or more characters.\n2) `_`: Matches exactly one character.\n3) `ILIKE`: Case-insensitive matching (PostgreSQL).\n4) Indexing: SARGable prefix search (`LIKE 'abc%'`) uses B-Tree indexes; leading wildcards (`LIKE '%abc'`) force full table scans.\n\n```sql\nSELECT * FROM employees WHERE email LIKE '%@company.com';\n```")

add_doc("DOC-SQL-IS-NULL-DEEP", "sql", "null_handling", "IS NULL and IS NOT NULL: Three-Valued Logic and Predicate Evaluation",
    ["is null", "is not null", "null check", "null comparison", "three valued logic"],
    "NULL represents missing or unknown information:\n\n1) Rule: Never use `= NULL` or `!= NULL` (always evaluates to UNKNOWN). Use `IS NULL` or `IS NOT NULL`.\n\n```sql\nSELECT emp_name FROM employees WHERE manager_id IS NULL;\n```")

add_doc("DOC-SQL-ORDER-BY-DEEP", "sql", "sorting", "ORDER BY Clause: Multi-Column Sorting, ASC/DESC, and NULLS FIRST/LAST",
    ["order by", "sorting", "asc", "desc", "nulls first", "nulls last", "sort order"],
    "ORDER BY sorts query result rows:\n\n1) Direction: `ASC` (default) or `DESC`.\n2) Multi-Column: Evaluated left-to-right.\n3) NULL Ordering: Control NULL placement using `NULLS FIRST` or `NULLS LAST`.\n\n```sql\nSELECT emp_name, department_id, salary FROM employees ORDER BY department_id ASC, salary DESC NULLS LAST;\n```")

add_doc("DOC-SQL-LIMIT-OFFSET-DEEP", "sql", "pagination", "LIMIT and OFFSET: Pagination Mechanics and Keyset Pagination",
    ["limit", "offset", "pagination", "limit offset", "keyset pagination", "page size"],
    "LIMIT and OFFSET paginate query rows:\n\n1) Mechanics: `LIMIT n OFFSET m` skips `m` rows and returns `n` rows.\n2) Keyset Optimization: Avoid deep `OFFSET 1000000` by filtering on indexed IDs: `WHERE id > last_id ORDER BY id ASC LIMIT 10`.\n\n```sql\nSELECT * FROM products ORDER BY product_id ASC LIMIT 20 OFFSET 40;\n```")

add_doc("DOC-SQL-CASE-WHEN-DEEP", "sql", "conditional_logic", "CASE WHEN: Searched CASE, Simple CASE, and Conditional Aggregation",
    ["case when", "case expression", "if else in sql", "conditional logic", "searched case", "simple case"],
    "CASE WHEN provides conditional IF-THEN-ELSE evaluation:\n\n1) Searched CASE: Evaluates boolean expressions in order.\n2) Placement: Usable in SELECT, WHERE, ORDER BY, and inside aggregates for pivoting.\n\n```sql\nSELECT emp_name, salary, CASE WHEN salary >= 80000 THEN 'Senior' ELSE 'Junior' END AS seniority_tier FROM employees;\n```")

add_doc("DOC-SQL-COALESCE-DEEP", "sql", "null_handling", "COALESCE: Fallback Selection and Short-Circuiting",
    ["coalesce", "null replacement", "coalesce function", "fallback values", "default value for null"],
    "COALESCE evaluates arguments left-to-right and returns the first non-NULL expression:\n\n```sql\nSELECT customer_id, COALESCE(phone, mobile, email, 'No Contact') AS primary_contact FROM customers;\n```")

add_doc("DOC-SQL-NULLIF-DEEP", "sql", "null_handling", "NULLIF: Preventing Division by Zero and Blank Value Handling",
    ["nullif", "division by zero", "nullif function", "prevent divide by zero", "empty string to null"],
    "NULLIF(a, b) returns NULL if a = b; otherwise returns a:\n\n1) Division Safety: `total_cost / NULLIF(item_count, 0)` returns NULL instead of throwing a divide-by-zero exception.\n\n```sql\nSELECT dept_id, revenue / NULLIF(headcount, 0) AS revenue_per_head FROM departments;\n```")

add_doc("DOC-SQL-CAST-CONVERT-DEEP", "sql", "data_types", "CAST and CONVERT: Explicit Data Type Conversion Syntax",
    ["cast", "convert", "type casting", "data type conversion", "cast syntax", "convert syntax"],
    "Type conversion operators in SQL:\n\n1) ANSI CAST: `CAST(val AS target_type)`.\n2) PostgreSQL shorthand: `val::target_type`.\n3) SQL Server: `CONVERT(target_type, val, [style])`.\n\n```sql\nSELECT CAST('2025-01-01' AS DATE), CAST(150.5 AS INT);\n```")

add_doc("DOC-SQL-EXECUTION-ORDER-DEEP", "sql", "execution_order", "Logical SQL Query Processing & Execution Sequence",
    ["execution order", "query processing order", "logical order", "sql order of execution", "how sql executes", "processing sequence", "what is execution order in sql"],
    "The 8-step logical execution order of SQL queries:\n\n1. FROM & JOIN\n2. WHERE\n3. GROUP BY\n4. HAVING\n5. SELECT\n6. DISTINCT\n7. ORDER BY\n8. LIMIT / OFFSET\n\n💡 Consequence: Aliases created in SELECT cannot be used in WHERE because WHERE executes in Step 2 before SELECT in Step 5.")

# -------------------------------------------------------------------------
# 3. RELATIONAL JOINS (15 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-JOINS-INNER-DEEP", "sql", "joins", "INNER JOIN: Syntax, Equi-Joins, and Multi-Table Join Paths",
    ["inner join", "equi join", "non equi join", "join tables", "inner join syntax"],
    "INNER JOIN returns rows where matching keys exist in both tables:\n\n```sql\nSELECT e.emp_name, d.dept_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id;\n```")

add_doc("DOC-SQL-JOINS-LEFT-DEEP", "sql", "joins", "LEFT JOIN: Preserving Left Records, Outer Matches, and NULL Filters",
    ["left join", "left outer join", "outer join", "preserve left table", "left join syntax"],
    "LEFT JOIN returns all rows from the left table with matched right rows (or NULL if unmatched):\n\n```sql\nSELECT c.first_name, o.order_id FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id;\n```")

add_doc("DOC-SQL-JOINS-RIGHT-DEEP", "sql", "joins", "RIGHT JOIN: Preserving Right Records and Left Join Equivalence",
    ["right join", "right outer join", "right join syntax", "right vs left join"],
    "RIGHT JOIN preserves all right table rows. `A RIGHT JOIN B` is equivalent to `B LEFT JOIN A`.")

add_doc("DOC-SQL-JOINS-FULL-OUTER-DEEP", "sql", "joins", "FULL OUTER JOIN: Complete Bidirectional Outer Joins",
    ["full outer join", "full join", "outer join", "full outer join syntax", "bidirectional join"],
    "FULL OUTER JOIN combines LEFT and RIGHT outer joins, returning all rows from both tables filled with NULLs where unmatched.\n\n```sql\nSELECT e.emp_name, d.dept_name FROM employees e FULL OUTER JOIN departments d ON e.department_id = d.department_id;\n```")

add_doc("DOC-SQL-JOINS-CROSS-DEEP", "sql", "joins", "CROSS JOIN: Cartesian Products ($M \\times N$) and Matrix Generation",
    ["cross join", "cartesian product", "cross join syntax", "matrix generation", "all combinations"],
    "CROSS JOIN pairs every left row with every right row ($M \\times N$ rows). Used for calendar matrices and permutations.\n\n```sql\nSELECT p.product_name, s.size_label FROM products p CROSS JOIN product_sizes s;\n```")

add_doc("DOC-SQL-JOINS-NATURAL", "sql", "joins", "NATURAL JOIN: Implicit Join by Matching Column Names & Risks",
    ["natural join", "implicit join", "natural join syntax", "natural join risks"],
    "NATURAL JOIN automatically joins tables on all columns sharing identical names. Incurring high maintenance risk if column names change; explicit `ON` clauses are strongly preferred in production.")

add_doc("DOC-SQL-JOINS-SELF-DEEP", "sql", "joins", "SELF JOIN: Joining a Table to Itself for Hierarchies and Graph Edges",
    ["self join", "joining table to itself", "manager employee join", "table alias self join"],
    "SELF JOIN joins a table with itself using distinct aliases:\n\n```sql\nSELECT e.emp_name AS employee, m.emp_name AS manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.emp_id;\n```")

add_doc("DOC-SQL-JOINS-ANTI-DEEP", "sql", "joins", "ANTI-JOIN: Finding Unmatched Rows via LEFT JOIN IS NULL and NOT EXISTS",
    ["anti join", "anti-join", "unmatched rows", "left join where null", "not exists anti join", "find missing records"],
    "ANTI-JOIN returns left rows with NO matching right rows:\n\n```sql\nSELECT c.customer_id FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.customer_id IS NULL;\n```")

add_doc("DOC-SQL-JOINS-SEMI-DEEP", "sql", "joins", "SEMI-JOIN: Existence Filtering via EXISTS without Multiplying Rows",
    ["semi join", "semi-join", "exists semi join", "filter without duplicate rows", "in semi join"],
    "SEMI-JOIN checks existence in a secondary table without duplicating left rows:\n\n```sql\nSELECT * FROM departments d WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.department_id);\n```")

add_doc("DOC-SQL-JOINS-LATERAL-DEEP", "sql", "joins", "LATERAL JOIN & CROSS APPLY: Correlated Table Expressions in FROM",
    ["lateral join", "cross apply", "outer apply", "lateral", "correlated from clause"],
    "LATERAL (or CROSS APPLY) allows a subquery in FROM to reference preceding columns (for-each evaluation):\n\n```sql\nSELECT c.customer_id, o.total_amount FROM customers c CROSS JOIN LATERAL (SELECT total_amount FROM orders WHERE customer_id = c.customer_id ORDER BY order_date DESC LIMIT 1) o;\n```")

add_doc("DOC-SQL-JOINS-OUTER-APPLY", "sql", "joins", "OUTER APPLY: Left Outer Correlated Subqueries in SQL Server / Oracle",
    ["outer apply", "cross apply vs outer apply", "left join lateral", "outer apply syntax"],
    "OUTER APPLY functions like a LEFT JOIN to a correlated table expression, preserving outer rows even if the inner subquery returns 0 rows.")

add_doc("DOC-SQL-NON-EQUI-JOIN", "sql", "joins", "Non-Equi Joins: Range Joins, Inequality Joins, and Banding",
    ["non equi join", "range join", "between join", "inequality join", "salary grade join"],
    "Non-equi joins join tables using `<`, `<=`, `>`, `>=`, or `BETWEEN`:\n\n```sql\nSELECT e.emp_name, e.salary, g.grade_level FROM employees e JOIN salary_grades g ON e.salary BETWEEN g.min_salary AND g.max_salary;\n```")

add_doc("DOC-SQL-JOIN-ALGORITHMS", "sql", "joins", "Join Physical Algorithms: Nested Loops, Hash Join, and Merge Join",
    ["join algorithms", "nested loop join", "hash join", "merge join", "physical join operators"],
    "Database physical join algorithms:\n\n1) Nested Loops: Iterates outer rows and performs index seek on inner table. Best for small outer sets.\n2) Hash Join: Builds hash table of smaller table in memory and scans larger table. Best for large unsorted sets.\n3) Merge Join: Merges two pre-sorted inputs. Extremely fast when inputs are already sorted by join key.")

add_doc("DOC-SQL-SET-OPERATIONS-DEEP", "sql", "set_operations", "SQL Set Operations: UNION, UNION ALL, INTERSECT, and EXCEPT",
    ["set operations", "union", "union all", "intersect", "except", "minus", "union vs union all"],
    "Set operations combine rows from compatible SELECT queries:\n\n1) UNION: Eliminates duplicates.\n2) UNION ALL: Retains all duplicates with maximum speed.\n3) INTERSECT: Returns common rows.\n4) EXCEPT: Returns rows in query 1 not in query 2.\n\n```sql\nSELECT city FROM customers UNION ALL SELECT city FROM suppliers;\n```")

add_doc("DOC-SQL-SET-RULES", "sql", "set_operations", "Set Operations Rules: Column Counts, Data Type Compatibility, and ORDER BY",
    ["set operations rules", "union requirements", "column compatibility union", "order by in union"],
    "Rules for set operations (UNION, INTERSECT, EXCEPT):\n\n1) Identical Column Count: All queries must select the exact same number of columns.\n2) Compatible Types: Corresponding columns must have compatible types in positional order.\n3) Single ORDER BY: ORDER BY is placed once at the very end of the final query.")

# -------------------------------------------------------------------------
# 4. AGGREGATIONS & GROUPING (15 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-AGGREGATES-CORE", "sql", "aggregations", "Aggregate Functions: COUNT, SUM, AVG, MIN, MAX and NULL Handling",
    ["aggregations", "count", "sum", "avg", "min", "max", "aggregate functions", "nulls in aggregates"],
    "Aggregate functions summarize multiple values into a single scalar value. Note: SUM, AVG, MIN, MAX automatically ignore NULL values; COUNT(*) counts all rows including NULLs.")

add_doc("DOC-SQL-GROUP-BY-DEEP", "sql", "aggregations", "GROUP BY Clause: Grouping Keys and Aggregation Semantics",
    ["group by", "grouping", "aggregate functions", "group by clause", "group by multiple columns"],
    "GROUP BY groups rows sharing identical grouping keys into summary records:\n\n```sql\nSELECT department_id, COUNT(*) AS headcount, AVG(salary) AS avg_sal FROM employees GROUP BY department_id;\n```")

add_doc("DOC-SQL-HAVING-DEEP", "sql", "aggregations", "HAVING Clause: Post-Aggregation Group Filtering",
    ["having", "having clause", "filter groups", "aggregate filtering", "having with sum"],
    "HAVING filters aggregated groups after GROUP BY:\n\n```sql\nSELECT customer_id, SUM(total_amount) AS total_spent FROM orders GROUP BY customer_id HAVING SUM(total_amount) > 10000;\n```")

add_doc("DOC-SQL-WHERE-VS-HAVING-DEEP", "sql", "filtering", "WHERE vs HAVING Clause: Execution Phase, Filtering Level, and Rules",
    ["where vs having", "difference between where and having", "where clause", "having clause", "group by having", "filtering"],
    "WHERE filters raw rows before aggregation; HAVING filters aggregated group metrics after aggregation.\n\n```sql\nSELECT department_id, AVG(salary) FROM employees WHERE status = 'ACTIVE' GROUP BY department_id HAVING AVG(salary) > 75000;\n```")

add_doc("DOC-SQL-COUNT-DISTINCT", "sql", "aggregations", "COUNT(DISTINCT col): Counting Unique Non-Null Values",
    ["count distinct", "count(distinct)", "unique count", "distinct count performance"],
    "COUNT(DISTINCT col) counts unique non-NULL values in a column. Incurs hash table allocation or sorting in query execution.")

add_doc("DOC-SQL-ROLLUP-DEEP", "sql", "aggregations", "ROLLUP: Hierarchical Subtotals and Grand Total Generation",
    ["rollup", "subtotals", "grand total", "hierarchical aggregation"],
    "ROLLUP generates hierarchical subtotals and grand totals:\n\n```sql\nSELECT region, department_id, SUM(salary) FROM employees GROUP BY ROLLUP (region, department_id);\n```")

add_doc("DOC-SQL-CUBE-DEEP", "sql", "aggregations", "CUBE: Multidimensional Aggregations Across All Dimension Permutations",
    ["cube", "multidimensional aggregation", "all subtotals", "cube clause"],
    "CUBE computes subtotals for all $2^N$ combinations of grouping columns:\n\n```sql\nSELECT region, category, SUM(sales) FROM sales_data GROUP BY CUBE (region, category);\n```")

add_doc("DOC-SQL-GROUPING-SETS-DEEP", "sql", "aggregations", "GROUPING SETS: Custom Granular Multi-Level Grouping Combinations",
    ["grouping sets", "custom grouping", "selective subtotals"],
    "GROUPING SETS specifies explicit subtotal combinations in a single query pass without UNION ALL:\n\n```sql\nSELECT region, department_id, SUM(sales) FROM sales_data GROUP BY GROUPING SETS ((region, department_id), (region), ());\n```")

add_doc("DOC-SQL-STRING-AGG-DEEP", "sql", "aggregations", "STRING_AGG, GROUP_CONCAT, and LISTAGG: Delimited String Aggregation",
    ["string_agg", "group_concat", "listagg", "concatenate strings group", "string aggregation"],
    "Concatenates text values across grouped rows into a delimited string:\n\n```sql\n-- PostgreSQL:\nSELECT department_id, STRING_AGG(emp_name, ', ' ORDER BY salary DESC) AS team FROM employees GROUP BY department_id;\n```")

add_doc("DOC-SQL-ARRAY-AGG", "sql", "aggregations", "ARRAY_AGG: Aggregating Column Values into Native SQL Arrays",
    ["array_agg", "aggregate to array", "sql arrays", "postgres array_agg"],
    "ARRAY_AGG collects grouped values into a native array (PostgreSQL / BigQuery):\n\n```sql\nSELECT department_id, ARRAY_AGG(emp_id ORDER BY hire_date) AS emp_ids FROM employees GROUP BY department_id;\n```")

add_doc("DOC-SQL-CONDITIONAL-AGG", "sql", "aggregations", "Conditional Aggregation: Pivoting Rows to Columns via SUM(CASE WHEN)",
    ["conditional aggregation", "pivot", "sum case when", "count case when", "pivot rows to columns"],
    "Computes multiple category totals in a single table scan:\n\n```sql\nSELECT region, SUM(CASE WHEN status = 'COMPLETED' THEN amount ELSE 0 END) AS completed_rev, SUM(CASE WHEN status = 'REFUNDED' THEN amount ELSE 0 END) AS refund_rev FROM orders GROUP BY region;\n```")

add_doc("DOC-SQL-PIVOT-UNPIVOT", "sql", "aggregations", "PIVOT and UNPIVOT: Native Matrix Transposition Syntax",
    ["pivot", "unpivot", "matrix transpose", "sql server pivot", "oracle pivot"],
    "PIVOT rotates rows into columns; UNPIVOT rotates columns back into rows (supported natively in SQL Server and Oracle).")

add_doc("DOC-SQL-STATISTICAL-AGGS", "sql", "aggregations", "Statistical Aggregates: STDDEV_SAMP, VAR_SAMP, CORR, and MEDIAN",
    ["stddev", "variance", "median", "statistical functions", "var_samp", "stddev_samp"],
    "Standard statistical functions in SQL: `STDDEV_SAMP()` (sample standard deviation), `VAR_SAMP()` (sample variance), `CORR(y, x)` (Pearson correlation coefficient).")

add_doc("DOC-SQL-GROUPING-FUNCTION", "sql", "aggregations", "GROUPING() and GROUPING_ID(): Identifying Subtotal Rows",
    ["grouping()", "grouping_id", "identify subtotal rows", "distinguish nulls from subtotals"],
    "GROUPING(col) returns 1 if the row represents an aggregate subtotal generated by ROLLUP/CUBE, and 0 if it is a standard grouped row.")

add_doc("DOC-SQL-AGGREGATE-FILTER-CLAUSE", "sql", "aggregations", "FILTER Clause on Aggregates: ANSI Standard Conditional Aggregation",
    ["filter clause", "aggregate filter", "count filter", "sum filter", "postgres filter clause"],
    "ANSI SQL standard FILTER clause (supported in PostgreSQL and SQLite 3.30+):\n\n```sql\nSELECT department_id, COUNT(*) FILTER (WHERE salary > 80000) AS high_earners FROM employees GROUP BY department_id;\n```")

# -------------------------------------------------------------------------
# 5. WINDOW FUNCTIONS & ANALYTICAL SQL (15 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-WINDOWS-OVER-CLAUSE", "sql", "window_functions", "Anatomy of Window Functions: OVER, PARTITION BY, and ORDER BY",
    ["window function", "window functions", "windows function", "over clause", "partition by", "windowing", "what is windows function"],
    "Window functions perform calculations across a partition of rows related to the current row without collapsing rows:\n\n`FUNCTION() OVER (PARTITION BY part_col ORDER BY sort_col [frame])`\n\n```sql\nSELECT emp_name, salary, AVG(salary) OVER (PARTITION BY department_id) AS dept_avg FROM employees;\n```")

add_doc("DOC-SQL-ROW-NUMBER-DEEP", "sql", "window_functions", "ROW_NUMBER(): Sequential Row Indexing, Deduplication, and Top-N",
    ["row_number", "row number", "row_number()", "sequential numbers", "top n per group", "deduplication with row_number"],
    "Assigns a unique sequential integer (1, 2, 3, ...) per partition with no ties. Used for Top-N per group and deduplication.")

add_doc("DOC-SQL-RANK-DEEP", "sql", "window_functions", "RANK(): Ranking with Gaps on Tied Values",
    ["rank", "rank()", "ranking with ties", "rank with gaps", "competition ranking"],
    "Assigns identical rank to ties, skipping subsequent numbers (1, 2, 2, 4).")

add_doc("DOC-SQL-DENSE-RANK-DEEP", "sql", "window_functions", "DENSE_RANK(): Ranking Without Gaps on Tied Values",
    ["dense_rank", "dense_rank()", "ranking without gaps", "consecutive ranking"],
    "Assigns identical rank to ties without skipping subsequent numbers (1, 2, 2, 3).")

add_doc("DOC-SQL-RANK-VS-DENSE-RANK-DEEP", "sql", "window_functions", "RANK vs DENSE_RANK: Tie-Handling Differences and Leaderboards",
    ["rank vs dense_rank", "rank", "dense_rank", "difference between rank and dense_rank", "ranking ties"],
    "RANK leaves gaps (1, 2, 2, 4); DENSE_RANK leaves no gaps (1, 2, 2, 3).")

add_doc("DOC-SQL-NTILE-DEEP", "sql", "window_functions", "NTILE(n): Dividing Data into Quartiles, Deciles, and Percentiles",
    ["ntile", "ntile function", "quartile", "decile", "percentile", "bucket", "ntile in detail", "ntile example"],
    "NTILE(n) divides ordered rows into 'n' equal buckets (1 to n):\n\n```sql\nSELECT emp_name, salary, NTILE(4) OVER (ORDER BY salary DESC) AS quartile FROM employees;\n```")

add_doc("DOC-SQL-LAG-DEEP", "sql", "window_functions", "LAG(): Fetching Previous Row Values and Day-over-Day Growth",
    ["lag", "lag function", "previous row", "day over day", "prior period"],
    "LAG(col, offset, default) retrieves values from preceding rows:\n\n```sql\nSELECT order_date, revenue, LAG(revenue, 1) OVER (ORDER BY order_date) AS prev_rev FROM daily_sales;\n```")

add_doc("DOC-SQL-LEAD-DEEP", "sql", "window_functions", "LEAD(): Fetching Subsequent Future Row Values and Churn Analysis",
    ["lead", "lead function", "next row", "future period", "subsequent row"],
    "LEAD(col, offset, default) retrieves values from subsequent future rows.")

add_doc("DOC-SQL-FIRST-LAST-VALUE", "sql", "window_functions", "FIRST_VALUE() and LAST_VALUE(): Partition Boundary Values",
    ["first_value", "last_value", "boundary values", "partition first", "partition last"],
    "FIRST_VALUE(col) and LAST_VALUE(col) return the first or last value in the window frame.")

add_doc("DOC-SQL-NTH-VALUE", "sql", "window_functions", "NTH_VALUE(): Accessing Specific Row Positions in Window Partitions",
    ["nth_value", "nth row in window", "second highest in partition", "nth_value()"],
    "NTH_VALUE(col, n) returns the value from the n-th row of the window frame.")

add_doc("DOC-SQL-CUME-DIST-PERCENT-RANK", "sql", "window_functions", "CUME_DIST() and PERCENT_RANK(): Cumulative Distribution & Percentiles",
    ["cume_dist", "percent_rank", "cumulative distribution", "percentile rank", "statistical ranking"],
    "CUME_DIST() computes the relative rank of a value ($row\\_num / total\\_rows$); PERCENT_RANK() computes relative percentage ($(rank - 1) / (total - 1)$).")

add_doc("DOC-SQL-ROWS-VS-RANGE", "sql", "window_functions", "ROWS vs RANGE BETWEEN: Physical Row Frames vs Logical Value Frames",
    ["rows between", "range between", "window frames", "rolling average", "running total", "unbounded preceding"],
    "ROWS defines frames by physical row count; RANGE defines frames by logical value intervals based on ORDER BY.")

add_doc("DOC-SQL-RUNNING-TOTAL", "sql", "window_functions", "Cumulative Running Totals: Syntax and Execution Efficiency",
    ["running total", "cumulative sum", "cumulative total", "running sum"],
    "Calculates cumulative totals using `SUM(col) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`.")

add_doc("DOC-SQL-MOVING-AVERAGE", "sql", "window_functions", "Rolling Moving Averages: 7-Day, 30-Day, and Centered Moving Averages",
    ["moving average", "rolling average", "7 day moving average", "rolling window"],
    "Calculates moving averages: `AVG(sales) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.")

add_doc("DOC-SQL-WINDOWED-AGGREGATES", "sql", "window_functions", "Aggregate Window Functions: SUM(), AVG(), COUNT() with OVER()",
    ["aggregate window functions", "sum over", "avg over", "count over", "window aggregation"],
    "Using standard aggregate functions with `OVER()` computes partition summaries without collapsing row details.")

# -------------------------------------------------------------------------
# 6. COMMON TABLE EXPRESSIONS (CTEs) (10 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-CTE-STANDARD", "sql", "cte", "Common Table Expressions (CTEs): WITH Clause, Modularity, and Readability",
    ["cte", "ctes", "with clause", "common table expression", "query modularity"],
    "A CTE defines a temporary named result set within a single SQL statement using `WITH`:\n\n```sql\nWITH HighEarners AS (SELECT * FROM employees WHERE salary > 80000) SELECT * FROM HighEarners;\n```")

add_doc("DOC-SQL-CTE-RECURSIVE-DEEP", "sql", "cte", "WITH RECURSIVE: Tree Hierarchies, Anchor/Recursive Members, and Graphs",
    ["recursive cte", "with recursive", "hierarchical queries", "tree traversal", "parent child hierarchy"],
    "Recursive CTEs iterate over parent-child hierarchies using an Anchor Member, UNION ALL, and a Recursive Member.\n\n```sql\nWITH RECURSIVE Tree AS (SELECT id, parent_id, 1 AS level FROM nodes WHERE parent_id IS NULL UNION ALL SELECT n.id, n.parent_id, t.level + 1 FROM nodes n JOIN Tree t ON n.parent_id = t.id) SELECT * FROM Tree;\n```")

add_doc("DOC-SQL-CTE-CHAINED", "sql", "cte", "Chained Multiple CTEs: Multi-Stage Data Transformation Pipelines",
    ["multiple ctes", "chained ctes", "multi stage cte", "data pipeline in sql"],
    "Multiple CTEs can be defined in a single WITH statement separated by commas:\n\n```sql\nWITH Step1 AS (SELECT ...), Step2 AS (SELECT ... FROM Step1) SELECT * FROM Step2;\n```")

add_doc("DOC-SQL-CTE-VS-SUBQUERY-DEEP", "sql", "cte", "CTE vs Subquery vs Temporary Table vs View Comparison",
    ["cte vs subquery", "cte vs temp table", "cte vs view", "when to use cte", "subquery vs cte"],
    "CTEs enhance statement readability; Subqueries evaluate inline; Temp Tables persist intermediate data across statements; Views permanently store query definitions.")

add_doc("DOC-SQL-CTE-DEDUPLICATION", "sql", "cte", "Deduplicating Data with CTEs and ROW_NUMBER()",
    ["deduplication with cte", "delete duplicates cte", "remove duplicate rows"],
    "Identify duplicate records using a CTE with ROW_NUMBER() and delete where `row_num > 1`.\n\n```sql\nWITH Ranked AS (SELECT ctid, ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) as r FROM users) DELETE FROM users WHERE ctid IN (SELECT ctid FROM Ranked WHERE r > 1);\n```")

add_doc("DOC-SQL-CTE-MUTATING-DML", "sql", "cte", "Data-Modifying CTEs: INSERT, UPDATE, DELETE with RETURNING in CTEs",
    ["modifying cte", "cte insert returning", "cte delete returning", "postgres writable cte"],
    "PostgreSQL allows DML statements with `RETURNING` inside CTEs, moving deleted/inserted rows into audit tables in a single atomic transaction.")

add_doc("DOC-SQL-CTE-MATERIALIZED", "sql", "cte", "MATERIALIZED vs NOT MATERIALIZED CTEs (PostgreSQL 12+ Optimization)",
    ["materialized cte", "not materialized cte", "cte inlining", "cte optimization fence"],
    "PostgreSQL 12+ automatically inlines CTEs unless specified as `WITH cte AS MATERIALIZED (...)` to force a materialization fence.")

add_doc("DOC-SQL-CTE-GRAPH-PATHS", "sql", "cte", "Graph Path Finding & Cycle Detection in Recursive CTEs",
    ["graph path finding", "cycle detection cte", "infinite loop prevention", "shortest path sql"],
    "Track visited node arrays (`ARRAY[id]`) in recursive CTEs to prevent infinite loops in cyclic graphs.")

add_doc("DOC-SQL-CTE-PAGINATION", "sql", "cte", "Windowed Pagination and Total Count in a Single CTE Query",
    ["pagination cte", "total count pagination", "single pass pagination"],
    "Compute total row count and paginated rows in a single query pass using CTEs with `COUNT(*) OVER()`.")

add_doc("DOC-SQL-CTE-PITFALLS", "sql", "cte", "CTE Performance Pitfalls: Optimization Fences and TempDB Overhead",
    ["cte pitfalls", "cte performance issues", "tempdb cte", "slow cte"],
    "Older database versions treat CTEs as strict optimization fences, preventing predicate pushdown. Verify query plans.")

# -------------------------------------------------------------------------
# 7. SUBQUERIES & OPERATORS (12 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-SCALAR-SUBQUERY", "sql", "subqueries", "Scalar Subqueries: Single-Value Subqueries in SELECT and WHERE",
    ["scalar subquery", "single value subquery", "subquery in select", "scalar subquery rules"],
    "A scalar subquery returns exactly one row and one column. If it returns 0 rows, it evaluates to NULL; if >1 row, it throws a runtime error.")

add_doc("DOC-SQL-MULTI-ROW-SUBQUERY", "sql", "subqueries", "Multi-Row Subqueries: IN, ANY, ALL, and SOME Operators",
    ["multi row subquery", "any operator", "all operator", "some operator", "subquery in where"],
    "Multi-row subqueries return a single column with multiple rows for evaluation with `IN`, `ANY` (true if any match), and `ALL` (true only if all match).")

add_doc("DOC-SQL-CORRELATED-SUBQUERY-DEEP", "sql", "subqueries", "Correlated Subqueries: Row-by-Row Outer References",
    ["correlated subquery", "subqueries", "outer reference", "correlated query", "subquery in where"],
    "Correlated subqueries reference outer query columns and evaluate once per candidate row.\n\n```sql\nSELECT * FROM employees e1 WHERE salary > (SELECT AVG(salary) FROM employees e2 WHERE e2.dept_id = e1.dept_id);\n```")

add_doc("DOC-SQL-EXISTS-VS-IN-DEEP", "sql", "subqueries", "EXISTS vs IN: Short-Circuiting, Subquery Optimization, and Performance",
    ["exists vs in", "difference between exists and in", "exists", "in operator", "subquery optimization"],
    "EXISTS terminates on the first match (short-circuiting); IN materializes the entire set into memory.")

add_doc("DOC-SQL-NOT-EXISTS-VS-NOT-IN", "sql", "subqueries", "NOT EXISTS vs NOT IN: The NULL Hazard and Performance Differences",
    ["not exists vs not in", "not exists", "not in null hazard", "anti join comparison"],
    "NOT IN fails if the subquery returns any NULL; NOT EXISTS is completely immune to NULL hazards and executes faster.")

add_doc("DOC-SQL-DERIVED-TABLES", "sql", "subqueries", "Derived Tables: Inline Subqueries in FROM Clauses and Mandatory Aliasing",
    ["derived table", "subquery in from", "inline view", "derived table alias"],
    "A subquery placed in the FROM clause acts as a temporary in-memory table. In standard SQL, derived tables MUST have an explicit alias.")

add_doc("DOC-SQL-ANY-ALL-OPERATORS", "sql", "subqueries", "ANY, SOME, and ALL Operators in Subquery Comparisons",
    ["any", "all", "some", "greater than any", "greater than all"],
    "`> ANY (subquery)` is true if greater than the minimum value; `> ALL (subquery)` is true only if greater than the maximum value.")

add_doc("DOC-SQL-SUBQUERY-SELECT", "sql", "subqueries", "Subqueries in SELECT List: Column-Level Lookup Patterns",
    ["subquery in select", "computed column subquery", "correlated select subquery"],
    "Evaluate lookup metrics per row without explicit joins:\n\n```sql\nSELECT customer_id, (SELECT MAX(order_date) FROM orders o WHERE o.customer_id = c.customer_id) AS latest_order FROM customers c;\n```")

add_doc("DOC-SQL-SUBQUERY-HAVING", "sql", "subqueries", "Subqueries in HAVING Clauses: Dynamic Aggregate Thresholds",
    ["subquery in having", "having subquery", "dynamic group filter"],
    "Compare group aggregates against dynamic thresholds:\n\n```sql\nSELECT dept_id, AVG(salary) FROM employees GROUP BY dept_id HAVING AVG(salary) > (SELECT AVG(salary) FROM employees);\n```")

add_doc("DOC-SQL-SUBQUERY-DML", "sql", "subqueries", "Subqueries in DML: INSERT INTO SELECT, UPDATE with Subqueries, DELETE Subqueries",
    ["insert into select", "update with subquery", "delete with subquery", "dml subqueries"],
    "Using subqueries to drive bulk inserts, updates, and deletes across relational tables.")

add_doc("DOC-SQL-SUBQUERY-UNNESTING", "sql", "subqueries", "Subquery Unnesting & Decorrelation in Modern Query Optimizers",
    ["subquery unnesting", "decorrelation", "optimizer transform subquery", "subquery to join"],
    "Modern query optimizers automatically transform correlated subqueries into semi-joins or hash joins to avoid nested loops.")

add_doc("DOC-SQL-INLINE-VIEWS", "sql", "subqueries", "Inline Views vs CTEs: Readability and Scope",
    ["inline views", "inline views vs ctes", "nested subqueries"],
    "Inline views define temporary tables in FROM; CTEs provide equivalent capability with top-down readability.")

# -------------------------------------------------------------------------
# 8. DATABASE DDL, SCHEMAS & CONSTRAINTS (15 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-PRIMARY-KEY-DEEP", "sql", "schema_design", "Primary Key (PK): Definition, Characteristics, and Entity Integrity",
    ["primary key", "pk", "primary", "entity integrity", "composite primary key", "surrogate key", "natural key"],
    "A Primary Key uniquely identifies each row (Unique + NOT NULL, 1 per table, clustered index by default).")

add_doc("DOC-SQL-FOREIGN-KEY-DEEP", "sql", "schema_design", "Foreign Key (FK): Definition, Referential Integrity, and Cascade Actions",
    ["foreign key", "fk", "foreign", "referential integrity", "cascade", "on delete cascade", "on update cascade"],
    "A Foreign Key enforces Referential Integrity between child and parent tables (`ON DELETE CASCADE / RESTRICT / SET NULL`).")

add_doc("DOC-SQL-KEYS-PK-VS-FK-DEEP", "sql", "schema_design", "Primary Key vs Foreign Key: Entity Integrity vs Referential Integrity",
    ["difference between primary and foreign key", "primary vs foreign key", "pk vs fk", "primary key vs foreign key", "what us difference between primary and foreign key"],
    "Primary Key guarantees row uniqueness within a table; Foreign Key guarantees data consistency across related tables.")

add_doc("DOC-SQL-CONSTRAINTS-CHECK-DEEP", "sql", "constraints", "CHECK Constraints: Domain Validation and Multi-Column Rules",
    ["check constraint", "check", "domain validation", "table constraints", "add check constraint"],
    "CHECK constraints validate column values on INSERT/UPDATE:\n\n```sql\nALTER TABLE products ADD CONSTRAINT check_positive_price CHECK (unit_price > 0);\n```")

add_doc("DOC-SQL-CONSTRAINTS-UNIQUE-DEEP", "sql", "constraints", "UNIQUE Constraint: Uniqueness Enforcement, Indexes, and NULLs",
    ["unique constraint", "unique", "unique key", "primary key vs unique", "unique index"],
    "UNIQUE ensures column values are distinct. Unlike PKs, multiple UNIQUE constraints can exist per table, and NULLs are allowed.")

add_doc("DOC-SQL-CONSTRAINTS-NOT-NULL", "sql", "constraints", "NOT NULL Constraint: Enforcing Mandatory Field Values",
    ["not null", "not null constraint", "mandatory column", "nullability"],
    "NOT NULL prevents missing or unassigned values from being stored in a column.")

add_doc("DOC-SQL-CONSTRAINTS-DEFAULT", "sql", "constraints", "DEFAULT Constraint: Automatic Column Value Insertion",
    ["default constraint", "default value", "default current_timestamp", "automatic values"],
    "DEFAULT supplies an initial value when no value is specified in an INSERT statement:\n\n```sql\nALTER TABLE orders ALTER COLUMN status SET DEFAULT 'PENDING';\n```")

add_doc("DOC-SQL-AUTO-INCREMENT-SERIAL", "sql", "schema_design", "AUTO_INCREMENT, SERIAL, IDENTITY, and SEQUENCES",
    ["auto_increment", "serial", "identity", "sequences", "surrogate key generation", "nextval"],
    "System-generated surrogate primary keys: `AUTO_INCREMENT` (MySQL), `SERIAL` / `GENERATED ALWAYS AS IDENTITY` (PostgreSQL), `IDENTITY(1,1)` (SQL Server), `SEQUENCE.NEXTVAL` (Oracle).")

add_doc("DOC-SQL-ALTER-TABLE-DEEP", "sql", "ddl", "ALTER TABLE: Adding, Dropping, Renaming Columns and Constraints",
    ["alter table", "add column", "drop column", "rename column", "modify column"],
    "DDL command for schema evolution:\n\n```sql\nALTER TABLE users ADD COLUMN phone VARCHAR(20), DROP COLUMN fax_number;\n```")

add_doc("DOC-SQL-DROP-VS-TRUNCATE", "sql", "ddl_dml", "DROP TABLE vs TRUNCATE TABLE: Complete Destruction vs Bulk Data Purge",
    ["drop vs truncate", "difference between drop and truncate", "drop table", "truncate table"],
    "DROP TABLE destroys the table structure, metadata, constraints, and data; TRUNCATE preserves schema structure and empties data pages instantly.")

add_doc("DOC-SQL-DELETE-TRUNCATE-DROP-DEEP", "sql", "ddl_dml", "DELETE vs TRUNCATE vs DROP: Logging, Rollbacks, and Resets",
    ["delete vs truncate", "delete vs truncate vs drop", "truncate table", "delete from", "drop table", "ddl vs dml", "what is the difference between delete, truncate and drop"],
    "DELETE is DML (row logged, rollbackable, fires triggers); TRUNCATE is DDL (page deallocated, fast, resets identity); DROP is DDL (destroys table structure).")

add_doc("DOC-SQL-SCHEMAS-NAMESPACES", "sql", "schema_design", "Database Schemas & Namespaces: Organizing Tables & Security",
    ["schemas", "database schema", "public schema", "search_path", "schema namespaces"],
    "Schemas organize database objects into distinct logical namespaces (`sales.orders`, `hr.employees`) for multi-tenant isolation and security permissions.")

add_doc("DOC-SQL-TEMP-TABLES", "sql", "schema_design", "Temporary Tables: Local (#temp), Global (##temp), and pg_temp",
    ["temporary tables", "temp table", "#temp", "global temp table", "pg_temp"],
    "Temporary tables persist data only during the current session or transaction, supporting custom indexes for heavy intermediate computations.")

add_doc("DOC-SQL-PARTITIONING-DEEP", "sql", "partitioning", "Table Partitioning: Range, List, Hash Partitioning & Pruning",
    ["partitioning", "table partitioning", "range partitioning", "list partitioning", "hash partitioning", "partition pruning"],
    "Partition massive tables into physically separate chunks based on date ranges, regions, or hash buckets, enabling Partition Pruning during queries.")

add_doc("DOC-SQL-TABLE-CONSTRAINTS-CASCADE", "sql", "constraints", "Cascading Referential Actions: CASCADE, RESTRICT, SET NULL",
    ["cascade", "on delete cascade", "on update cascade", "set null", "restrict", "no action"],
    "Define what happens to child records when parent records are deleted or updated:\n\n```sql\nFOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE\n```")

# -------------------------------------------------------------------------
# 9. DML MUTATION OPERATIONS (10 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-INSERT-DEEP", "sql", "dml", "INSERT Statement: Single-Row, Multi-Row, and Default Value Inserts",
    ["insert", "insert into", "multi row insert", "insert syntax"],
    "Insert new records into tables:\n\n```sql\nINSERT INTO products (product_name, unit_price) VALUES ('Widget A', 19.99), ('Widget B', 29.99);\n```")

add_doc("DOC-SQL-INSERT-SELECT", "sql", "dml", "INSERT INTO SELECT: Bulk Data Migration and Table Population",
    ["insert into select", "bulk insert", "copy data table", "insert from select"],
    "Populates a table directly from query results:\n\n```sql\nINSERT INTO archive_orders SELECT * FROM orders WHERE order_date < '2024-01-01';\n```")

add_doc("DOC-SQL-UPDATE-DEEP", "sql", "dml", "UPDATE Statement: Modifying Rows, WHERE Safeguards, and Calculated Updates",
    ["update", "update statement", "update where", "modify rows", "update salary"],
    "Modifies existing records. Always include a WHERE clause to prevent updating all rows across the entire table!\n\n```sql\nUPDATE employees SET salary = salary * 1.05 WHERE department_id = 10;\n```")

add_doc("DOC-SQL-UPDATE-WITH-JOIN", "sql", "dml", "UPDATE with JOIN: Cross-Table Updates across Relational Datasets",
    ["update with join", "update from", "cross table update", "update join syntax"],
    "Update columns based on joined tables:\n\n```sql\n-- PostgreSQL / SQLite UPDATE FROM:\nUPDATE products p SET unit_price = p.unit_price * 1.1 FROM suppliers s WHERE p.supplier_id = s.supplier_id AND s.region = 'EMEA';\n```")

add_doc("DOC-SQL-DELETE-DEEP", "sql", "dml", "DELETE Statement: Removing Specific Rows and Transaction Safeguards",
    ["delete", "delete from", "delete statement", "delete where", "remove rows"],
    "Removes records matching WHERE criteria. Logs individual row deletions in transaction logs, enabling ROLLBACK.")

add_doc("DOC-SQL-DELETE-WITH-JOIN", "sql", "dml", "DELETE with JOIN: Removing Child Records Based on Parent Joins",
    ["delete with join", "delete using", "delete from join"],
    "Delete records based on relational join filters (e.g. `DELETE FROM orders USING customers WHERE ...`).")

add_doc("DOC-SQL-UPSERT-MERGE-DEEP", "sql", "dml", "UPSERT & MERGE: ON CONFLICT DO UPDATE and ON DUPLICATE KEY UPDATE",
    ["upsert", "merge", "on conflict do update", "on duplicate key update", "insert or update"],
    "Conditional insert/update syntax: `ON CONFLICT (id) DO UPDATE` in PostgreSQL/SQLite; `ON DUPLICATE KEY UPDATE` in MySQL; `MERGE` in SQL Server/Oracle.")

add_doc("DOC-SQL-RETURNING-OUTPUT-DEEP", "sql", "dml", "RETURNING and OUTPUT: Returning Modified Rows Directly from DML",
    ["returning", "output clause", "returning clause", "insert returning id", "get generated id"],
    "Returns newly generated keys or updated data immediately without extra SELECT queries:\n\n```sql\nINSERT INTO users (username) VALUES ('alice') RETURNING user_id, created_at;\n```")

add_doc("DOC-SQL-BULK-OPERATIONS", "sql", "dml", "Bulk Data Loading: COPY FROM, BULK INSERT, and LOAD DATA INFILE",
    ["bulk insert", "copy from", "load data infile", "csv import sql", "high speed insert"],
    "High-speed binary and CSV ingestion methods bypassing standard statement parsing overhead.")

add_doc("DOC-SQL-SELECT-INTO", "sql", "dml", "SELECT INTO: Creating and Populating New Tables in One Step",
    ["select into", "create table as select", "ctas", "copy table structure"],
    "Create and populate a new table from query results (`SELECT INTO new_table FROM old_table` or `CREATE TABLE new_table AS SELECT ...`).")

# -------------------------------------------------------------------------
# 10. TRANSACTIONS, LOCKING & CONCURRENCY (12 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-ACID-OVERVIEW", "sql", "transactions", "ACID Properties: Atomicity, Consistency, Isolation, and Durability",
    ["acid", "transactions", "atomicity", "consistency", "isolation", "durability", "acid properties"],
    "Relational transaction guarantees: Atomicity (All or nothing), Consistency (Preserves constraints), Isolation (No concurrent corruption), Durability (Persisted to disk/WAL).")

add_doc("DOC-SQL-ISOLATION-LEVELS", "sql", "transactions", "SQL Isolation Levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable",
    ["isolation levels", "dirty read", "non repeatable read", "phantom read", "read committed", "repeatable read", "serializable"],
    "Transaction isolation levels from lowest to highest strictness:\n\n1) Read Uncommitted (Allows dirty reads)\n2) Read Committed (Default in Postgres/Oracle)\n3) Repeatable Read (Default in MySQL InnoDB)\n4) Serializable (Strictest, full isolation)")

add_doc("DOC-SQL-DIRTY-READS", "sql", "transactions", "Dirty Reads: Reading Uncommitted Data in Concurrency",
    ["dirty read", "dirty reads", "read uncommitted dirty read", "concurrency anomaly"],
    "A Dirty Read occurs when Transaction A reads data modified by Transaction B that has NOT yet been committed (and could be rolled back).")

add_doc("DOC-SQL-NON-REPEATABLE-READS", "sql", "transactions", "Non-Repeatable Reads: Value Changes Between Consecutive Queries",
    ["non repeatable read", "fuzzy read", "repeatable read isolation", "row value changes"],
    "A Non-Repeatable Read occurs when Transaction A reads a row, Transaction B updates that row and commits, and Transaction A re-reads the row to find changed values.")

add_doc("DOC-SQL-PHANTOM-READS", "sql", "transactions", "Phantom Reads: New Row Insertions in Range Queries",
    ["phantom read", "phantom reads", "range concurrency anomaly", "serializable phantom"],
    "A Phantom Read occurs when Transaction A queries a range of rows (e.g. `salary > 50000`), Transaction B inserts a new matching row and commits, and Transaction A re-runs the query to find new 'phantom' rows.")

add_doc("DOC-SQL-LOCKING-MECHANISMS", "sql", "locks_concurrency", "Database Locks: Shared (S) vs Exclusive (X) and Lock Granularity",
    ["locks", "locking", "shared lock", "exclusive lock", "row lock", "table lock"],
    "Shared (S) locks allow concurrent readers; Exclusive (X) locks give sole write access, blocking all other readers and writers.")

add_doc("DOC-SQL-DEADLOCKS", "sql", "locks_concurrency", "Deadlocks: Detection, Victim Selection, and Prevention Strategies",
    ["deadlock", "deadlocks", "deadlock detection", "deadlock victim", "deadlock prevention"],
    "A Deadlock occurs when two transactions wait for locks held by each other. Databases detect cycles and abort one transaction as the 'victim'. Prevent by acquiring locks in consistent order.")

add_doc("DOC-SQL-MVCC-DEEP", "sql", "locks_concurrency", "Multi-Version Concurrency Control (MVCC) Internals",
    ["mvcc", "multi version concurrency control", "snapshot isolation", "readers do not block writers", "xmin xmax"],
    "MVCC ensures Readers do not block Writers, and Writers do not block Readers by maintaining row version timestamps (xmin/xmax).")

add_doc("DOC-SQL-TRANSACTION-CONTROL", "sql", "transactions", "TCL Commands: BEGIN TRANSACTION, COMMIT, ROLLBACK, SAVEPOINT",
    ["tcl", "commit", "rollback", "savepoint", "begin transaction", "transaction control language"],
    "Explicit transaction management commands to guarantee atomicity and partial rollback points (`SAVEPOINT sp1`).")

add_doc("DOC-SQL-WAL-DURABILITY", "sql", "transactions", "Write-Ahead Logging (WAL) and Durability Architecture",
    ["wal", "write ahead logging", "durability", "redo log", "checkpointing"],
    "WAL writes transaction changes sequentially to an append-only log on disk BEFORE modifying table data pages, ensuring instant crash recovery.")

add_doc("DOC-SQL-PESSIMISTIC-OPTIMISTIC", "sql", "locks_concurrency", "Pessimistic Locking (SELECT FOR UPDATE) vs Optimistic Locking (Version Check)",
    ["pessimistic locking", "optimistic locking", "select for update", "version column locking"],
    "Pessimistic locking locks rows explicitly (`SELECT ... FOR UPDATE`); Optimistic locking checks version numbers upon update without holding locks.")

add_doc("DOC-SQL-TWO-PHASE-COMMIT", "sql", "transactions", "Two-Phase Commit (2PC): Distributed Transaction Coordination",
    ["2pc", "two phase commit", "distributed transactions", "prepare commit", "distributed acid"],
    "Coordinates atomic transactions across multiple distinct physical databases using Prepare and Commit phases.")

# -------------------------------------------------------------------------
# 11. INDEXES & PERFORMANCE OPTIMIZATION (12 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-INDEX-BTREE-DEEP", "sql", "indexes", "B-Tree Index Architecture: Balanced Tree Traversal and Range Lookups",
    ["b-tree", "btree index", "balanced tree", "range scan index", "default index"],
    "B-Tree indexes maintain sorted balanced tree structures supporting O(log N) lookups for equality and ranges (`=, <, >, BETWEEN, LIKE 'abc%'`).")

add_doc("DOC-SQL-INDEX-CLUSTERED-NONCLUSTERED", "sql", "indexes", "Clustered vs Non-Clustered Indexes: Physical Storage and Pointers",
    ["clustered index", "non-clustered index", "clustered vs non clustered", "heap table", "index pointers"],
    "A Clustered Index determines the physical sort order of rows on disk (1 per table, typically PK). Non-Clustered indexes are secondary trees holding row pointers.")

add_doc("DOC-SQL-INDEX-COMPOSITE-LEFTMOST", "sql", "indexes", "Composite Multi-Column Indexes and the Leftmost Prefix Rule",
    ["composite index", "multi column index", "leftmost prefix rule", "composite index order"],
    "An index on `(A, B, C)` can serve queries filtering on `(A)`, `(A, B)`, or `(A, B, C)`, but CANNOT serve queries filtering on `(B)` or `(C)` alone.")

add_doc("DOC-SQL-INDEX-COVERING-INCLUDE", "sql", "indexes", "Covering Indexes: The INCLUDE Clause and Index-Only Scans",
    ["covering index", "include clause", "index only scan", "covering index syntax"],
    "Covering indexes store extra columns in leaf pages via `INCLUDE`, fulfilling queries entirely from the index without reading table pages:\n\n```sql\nCREATE INDEX idx_cust ON orders (customer_id) INCLUDE (order_date, total_amount);\n```")

add_doc("DOC-SQL-INDEX-FILTERED-PARTIAL", "sql", "indexes", "Filtered and Partial Indexes: Indexing Specific Table Subsets",
    ["filtered index", "partial index", "index with where clause", "selective index"],
    "Index only rows matching a WHERE predicate to save disk space:\n\n```sql\nCREATE INDEX idx_active_orders ON orders (customer_id) WHERE status = 'PENDING';\n```")

add_doc("DOC-SQL-INDEX-EXPRESSION-FUNCTIONAL", "sql", "indexes", "Expression & Function-Based Indexes: Indexing Computed Columns",
    ["expression index", "functional index", "function based index", "index on upper", "index on date"],
    "Index computed expressions to accelerate non-SARGable queries:\n\n```sql\nCREATE INDEX idx_lower_email ON users (LOWER(email));\n```")

add_doc("DOC-SQL-INDEX-SEEK-SCAN-DEEP", "sql", "indexes", "Index Seek vs Index Scan vs Sequential Table Scan Comparison",
    ["index seek", "index scan", "table scan", "index seek vs index scan", "sequential scan"],
    "Index Seek navigates directly to matching keys (O(log N)); Index Scan reads all leaf pages; Table Scan reads all raw data blocks.")

add_doc("DOC-SQL-OPTIMIZATION-SARGABLE-DEEP", "sql", "optimization", "SARGable Query Design: Writing Index-Friendly Predicates",
    ["sargable", "sargable queries", "sargable predicates", "query tuning", "avoid full table scan", "how does sargable query optimization work"],
    "Avoid wrapping indexed columns in functions in WHERE clauses. Use range bounds rather than `YEAR(date)` or `DATE(date)`.")

add_doc("DOC-SQL-EXPLAIN-ANALYZE-DEEP", "sql", "optimization", "EXPLAIN & EXPLAIN ANALYZE: Interpreting Query Cost and Memory Buffers",
    ["explain", "explain analyze", "execution plan", "query plan", "cost based optimizer", "query cost"],
    "EXPLAIN shows estimated optimizer plans; EXPLAIN ANALYZE runs the query to measure actual millisecond latency and buffer hits.")

add_doc("DOC-SQL-COLUMN-PRUNING", "sql", "optimization", "Column Pruning: Avoiding SELECT * and Reducing Disk I/O",
    ["column pruning", "avoid select *", "projection optimization", "reduce io"],
    "Projecting only necessary columns reduces RAM cache consumption, network serialization, and enables Index-Only Scans.")

add_doc("DOC-SQL-INDEX-MAINTENANCE", "sql", "indexes", "Index Maintenance: Fragmentation, Page Splits, and REINDEX / REORGANIZE",
    ["index fragmentation", "reindex", "reorganize index", "fill factor", "page splits"],
    "Frequent inserts/updates cause index page fragmentation. Reorganize or rebuild fragmented indexes to restore sequential read performance.")

add_doc("DOC-SQL-STATISTICS-CBO", "sql", "optimization", "Cost-Based Optimizer (CBO), Statistics, Histograms, and ANALYZE",
    ["cost based optimizer", "cbo", "statistics", "histograms", "analyze table", "cardinality estimation"],
    "The CBO relies on column histograms and data distribution statistics to estimate row cardinality and choose optimal join algorithms.")

# -------------------------------------------------------------------------
# 12. DATABASE OBJECTS: PROCEDURES, FUNCTIONS, TRIGGERS & VIEWS (15 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-STORED-PROCEDURES-FULL", "sql", "stored_procedures", "Stored Procedures (SP): Complete Architecture, Parameters, and Syntax",
    ["stored procedure", "storedprocedure", "storeprocedure", "sp", "sprocs", "procedures", "create procedure", "call procedure", "plsql", "tsql", "help me to learn storeprocedure"],
    "Precompiled procedural code modules executed with `CALL` supporting loops, conditionals, transaction control, and parameter modes (`IN`, `OUT`, `INOUT`).")

add_doc("DOC-SQL-FUNCTIONS-UDF-FULL", "sql", "functions", "User-Defined Functions (UDF): Scalar vs Table-Valued Functions (TVF)",
    ["functions", "udf", "user defined function", "scalar function", "table valued function", "tvf", "deterministic function", "udf vs sp", "function vs procedure", "explain udf vs sp"],
    "Reusable computational routines called inside queries (`SELECT my_func(col)`). Must return a value; cannot manage transactions.")

add_doc("DOC-SQL-VIEWS-FULL", "sql", "views", "Standard Views: Virtual Table Abstractions and Security Encapsulation",
    ["views", "view", "create view", "virtual table", "view abstraction"],
    "A virtual saved query definition that does not store physical data on disk. Simplifies joins and provides column masking.")

add_doc("DOC-SQL-MATERIALIZED-VIEWS-FULL", "sql", "views", "Materialized Views: Physical Caching and Refresh Strategies",
    ["materialized view", "mv", "refresh materialized view", "cached query results", "materialized views"],
    "Physically persists query results on disk as a table for ultra-fast analytical reads. Requires explicit refresh (`REFRESH MATERIALIZED VIEW`).")

add_doc("DOC-SQL-TRIGGERS-FULL", "sql", "triggers", "Database Triggers: BEFORE, AFTER, INSTEAD OF, and Audit Logging",
    ["triggers", "trigger", "create trigger", "before trigger", "after trigger", "instead of trigger", "audit log", "event driven"],
    "Event-driven procedures executed automatically on INSERT, UPDATE, or DELETE, with access to `OLD` and `NEW` records.")

add_doc("DOC-SQL-UPDATABLE-VIEWS", "sql", "views", "Updatable Views and the WITH CHECK OPTION Clause",
    ["updatable view", "with check option", "update view", "view constraints"],
    "Single-table views without aggregates can accept INSERT/UPDATE. `WITH CHECK OPTION` enforces that modified rows satisfy the view WHERE filter.")

add_doc("DOC-SQL-CURSORS", "sql", "stored_procedures", "Database Cursors: Row-by-Row Iteration, Fetching, and Performance Caveats",
    ["cursor", "cursors", "fetch next from cursor", "row by row processing", "cursor vs set based"],
    "Cursors iterate row-by-row through result sets. Slow in relational databases; set-based SQL operations should always be preferred.")

add_doc("DOC-SQL-DYNAMIC-SQL", "sql", "stored_procedures", "Dynamic SQL: EXECUTE, sp_executesql, and SQL Injection Defenses",
    ["dynamic sql", "sp_executesql", "execute immediate", "sql injection defense", "parameterized dynamic sql"],
    "Constructing SQL strings dynamically at runtime. Always use parameterized execution (`sp_executesql` / `EXECUTE ... USING`) to prevent SQL injection.")

add_doc("DOC-SQL-PACKAGES-MODULES", "sql", "stored_procedures", "Database Packages and Modules: Grouping Procedures & Functions in Oracle / DB2",
    ["packages", "package body", "package specification", "plsql packages", "modular database code"],
    "Oracle PL/SQL packages encapsulate related procedures, functions, types, and variables into a single schema object.")

add_doc("DOC-SQL-LIMIT-TOP-FULL", "sql", "pagination", "LIMIT vs TOP vs FETCH FIRST: Syntax and Dialect Differences",
    ["limit vs top", "difference between limit and top", "limit", "top", "offset", "fetch next", "fetch first", "pagination", "row limiting"],
    "Row limiting syntax: `LIMIT n` in PostgreSQL/MySQL/SQLite; `TOP (n)` in SQL Server; `FETCH FIRST n ROWS ONLY` in ANSI/Oracle.")

add_doc("DOC-SQL-INDEXED-VIEWS", "sql", "views", "Indexed Views (SQL Server) & Schema Binding",
    ["indexed view", "schema binding", "clustered index on view", "sql server indexed view"],
    "SQL Server allows creating a Clustered Index directly on a view with `WITH SCHEMABINDING`, physically persisting view data on disk.")

add_doc("DOC-SQL-STORED-PROCEDURE-ERROR-HANDLING", "sql", "stored_procedures", "Error Handling in Stored Procedures: TRY-CATCH and EXCEPTION Blocks",
    ["error handling", "try catch sql", "exception block", "rollback on error", "sqlexception"],
    "Structured exception handling inside procedures to catch errors and safely execute `ROLLBACK`.")

add_doc("DOC-SQL-TRIGGERS-AUDIT-LOGGING", "sql", "triggers", "Building Automated Audit Trail Tables with Triggers",
    ["audit trail", "audit logging trigger", "track changes trigger", "change history table"],
    "Using AFTER UPDATE/DELETE triggers to insert previous values (`OLD.*`) and timestamps into dedicated audit tables.")

add_doc("DOC-SQL-UDF-DETERMINISM", "sql", "functions", "Deterministic vs Non-Deterministic Functions in Query Optimization",
    ["deterministic function", "non deterministic function", "deterministic vs non deterministic", "function caching"],
    "Deterministic functions always return the same result for identical inputs, allowing the optimizer to cache results or build functional indexes.")

add_doc("DOC-SQL-TABLE-VALUED-FUNCTIONS", "sql", "functions", "Table-Valued Functions (TVF): Inline vs Multi-Statement TVFs",
    ["table valued function", "tvf", "inline tvf", "multi statement tvf", "table function"],
    "Functions returning a table result set that can be joined in FROM clauses like a parameterized view.")

# -------------------------------------------------------------------------
# 13. DATA TYPES, STRINGS, DATES & JSON (15 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-NUMERIC-TYPES", "sql", "data_types", "Numeric Data Types: INT, BIGINT, DECIMAL vs FLOAT",
    ["numeric types", "integer", "bigint", "decimal", "numeric", "float vs decimal", "exact precision"],
    "`INT`/`BIGINT` for whole numbers; `DECIMAL(p,s)` for exact fixed-point financial currency; `FLOAT` for approximate scientific floating point.")

add_doc("DOC-SQL-STRING-TYPES", "sql", "data_types", "String Types: CHAR vs VARCHAR vs TEXT vs NVARCHAR",
    ["char", "varchar", "text", "nvarchar", "char vs varchar", "string data types"],
    "`CHAR(n)` is fixed-width padded with spaces; `VARCHAR(n)` is variable length; `TEXT` is unbounded string; `NVARCHAR` stores UTF-16 Unicode.")

add_doc("DOC-SQL-DATE-TIME-TYPES", "sql", "data_types", "Date & Time Types: DATE, TIME, TIMESTAMP, and TIMESTAMPTZ",
    ["date", "time", "timestamp", "timestamptz", "timezone offset", "temporal data types"],
    "`DATE` stores calendar day; `TIME` stores time-of-day; `TIMESTAMP` stores date+time; `TIMESTAMPTZ` stores timezone offsets.")

add_doc("DOC-SQL-DATE-FUNCTIONS-DEEP", "sql", "date_functions", "Date Functions: DATE_TRUNC, EXTRACT, DATEDIFF, and DATEADD",
    ["date functions", "date_trunc", "extract", "datediff", "dateadd", "intervals", "current_timestamp"],
    "Manipulate dates: `DATE_TRUNC('month', dt)` truncates timestamp; `EXTRACT(YEAR FROM dt)` extracts integer parts; `dt + INTERVAL '7 days'` adds intervals.")

add_doc("DOC-SQL-STRING-FUNCTIONS", "sql", "string_functions", "String Functions: CONCAT, SUBSTRING, REPLACE, TRIM, and UPPER/LOWER",
    ["string functions", "concat", "substring", "replace", "trim", "upper lower", "string manipulation"],
    "Core string manipulation functions: `CONCAT()`, `SUBSTRING(str, start, len)`, `REPLACE(str, from, to)`, `TRIM()`, `UPPER()`, `LOWER()`.")

add_doc("DOC-SQL-REGEX-MATCHING", "sql", "string_functions", "Regular Expressions: REGEXP_LIKE, SIMILAR TO, and Regex Functions",
    ["regex", "regexp_like", "regex matching", "similar to", "regular expressions in sql"],
    "Regex search in SQL: `WHERE col ~ '^[A-Z]{3}-[0-9]{4}$'` (PostgreSQL) or `WHERE REGEXP_LIKE(col, pattern)` (MySQL/Oracle).")

add_doc("DOC-SQL-JSON-JSONB-DEEP", "sql", "json", "JSON & JSONB in SQL: Query Operators (->, ->>), Indexing, and Search",
    ["json", "jsonb", "json querying", "json operators", "gin index json", "json_extract"],
    "PostgreSQL JSONB binary format supports `->` (returns JSON), `->>` (returns text), and GIN indexing for fast nested key lookups.")

add_doc("DOC-SQL-JSON-CREATION", "sql", "json", "JSON Aggregation: JSON_BUILD_OBJECT, JSON_AGG, and JSON_ARRAY",
    ["json_build_object", "json_agg", "json_object", "create json in sql", "serialize json"],
    "Serialize relational rows directly into nested JSON structures using `JSON_BUILD_OBJECT()` and `JSON_AGG()`.")

add_doc("DOC-SQL-UUID-GUID", "sql", "data_types", "UUID / GUID Generation: UUIDv4 vs Sequential UUIDv7 in Primary Keys",
    ["uuid", "guid", "gen_random_uuid", "uuidv4", "uuidv7", "distributed primary key"],
    "UUIDs provide globally unique IDs for distributed systems. `UUIDv7` (time-ordered) prevents B-Tree index fragmentation compared to random `UUIDv4`.")

add_doc("DOC-SQL-ENUM-TYPES", "sql", "data_types", "ENUM Data Types: Static Value Sets and Schema Evolution",
    ["enum", "enum data type", "custom enum", "enum vs check constraint"],
    "ENUM defines a static discrete list of allowed string values (e.g. `CREATE TYPE order_status AS ENUM ('PENDING', 'PAID', 'SHIPPED')`).")

add_doc("DOC-SQL-BOOLEAN-LOGIC-TYPES", "sql", "data_types", "Boolean Data Types: Truth Tables and NULL UNKNOWN Semantics",
    ["boolean", "true false unknown", "boolean type", "tri state logic"],
    "Boolean logic in SQL: `TRUE AND UNKNOWN = UNKNOWN`, `FALSE AND UNKNOWN = FALSE`, `TRUE OR UNKNOWN = TRUE`.")

add_doc("DOC-SQL-BLOB-BYTEA", "sql", "data_types", "BLOB and BYTEA: Storing Binary Files, Images, and Documents",
    ["blob", "bytea", "binary data", "store files in database", "binary large object"],
    "`BLOB` / `BYTEA` stores raw binary bytes. Best practice is storing file paths on cloud object storage (S3) rather than massive binary in tables.")

add_doc("DOC-SQL-COLLATIONS", "sql", "string_functions", "Collations: Character Sets, Case Sensitivity, and Accent Sensitivity",
    ["collation", "collate", "case sensitive collation", "utf8mb4", "accent sensitivity"],
    "Collations govern sorting and comparison rules (e.g. `COLLATE utf8mb4_general_ci` for case-insensitive comparisons).")

add_doc("DOC-SQL-INTERVAL-ARITHMETIC", "sql", "date_functions", "Interval Data Types and Temporal Arithmetic",
    ["interval", "date interval", "interval arithmetic", "add days interval"],
    "Using native interval types for time arithmetic: `SELECT CURRENT_DATE + INTERVAL '3 months 2 days'`.")

add_doc("DOC-SQL-DATA-TYPE-PRECEDENCE", "sql", "data_types", "Implicit Type Conversion and Data Type Precedence Hazards",
    ["implicit conversion", "type precedence", "implicit cast index loss"],
    "When comparing columns of different types (e.g. VARCHAR = INT), databases implicitly cast one side, which can disable B-Tree index usage.")

# -------------------------------------------------------------------------
# 14. NORMALIZATION & DATA MODELING (10 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-1NF", "sql", "schema_design", "First Normal Form (1NF): Atomic Attributes and Primary Key Identity",
    ["1nf", "first normal form", "atomic values", "no repeating groups", "normalization 1nf"],
    "1NF requires that all column values are atomic (indivisible), each table has a Primary Key, and no repeating group columns exist.")

add_doc("DOC-SQL-2NF", "sql", "schema_design", "Second Normal Form (2NF): Eliminating Partial Functional Dependencies",
    ["2nf", "second normal form", "partial dependency", "composite key dependency"],
    "2NF requires 1NF + all non-key attributes must depend on the ENTIRE composite Primary Key, eliminating partial dependencies.")

add_doc("DOC-SQL-3NF", "sql", "schema_design", "Third Normal Form (3NF): Eliminating Transitive Dependencies",
    ["3nf", "third normal form", "transitive dependency", "non key dependencies"],
    "3NF requires 2NF + non-key attributes must depend ONLY on the Primary Key, eliminating transitive dependencies ($X \\to Y \\to PK$).")

add_doc("DOC-SQL-BCNF", "sql", "schema_design", "Boyce-Codd Normal Form (BCNF): Determinant Candidate Keys",
    ["bcnf", "boyce codd normal form", "candidate keys", "strict 3nf"],
    "BCNF is a stricter version of 3NF where every determinant (left side of functional dependency) MUST be a candidate key.")

add_doc("DOC-SQL-4NF-5NF", "sql", "schema_design", "Fourth (4NF) and Fifth Normal Form (5NF): Multi-Valued & Join Dependencies",
    ["4nf", "5nf", "multi valued dependency", "join dependency", "advanced normalization"],
    "4NF eliminates multi-valued dependencies; 5NF eliminates join dependencies where tables cannot be split further without losing data.")

add_doc("DOC-SQL-DENORMALIZATION", "sql", "schema_design", "Denormalization: Tradeoffs for High-Read Data Warehouses and Reporting",
    ["denormalization", "star schema", "snowflake schema", "olap modeling", "read optimization"],
    "Denormalization intentionally introduces redundancy in analytical warehouses (Star Schema) to eliminate expensive joins during OLAP reporting.")

add_doc("DOC-SQL-RELATIONSHIP-TYPES", "sql", "schema_design", "Entity Relationships: One-to-One, One-to-Many, and Many-to-Many",
    ["relationships", "one to one", "one to many", "many to many", "junction table", "associative table"],
    "1:1 uses shared PK or unique FK; 1:N uses Foreign Key in child table; M:N requires an associative junction table holding composite FKs.")

add_doc("DOC-SQL-SURROGATE-VS-NATURAL-KEYS", "sql", "schema_design", "Surrogate Keys vs Natural Keys: Design Architecture and Tradeoffs",
    ["surrogate key", "natural key", "surrogate vs natural key", "primary key design"],
    "Natural keys use real-world data (ISBN, SSN); Surrogate keys use artificial numbers/UUIDs. Surrogate keys insulate database schemas from business changes.")

add_doc("DOC-SQL-DIMENSIONAL-MODELING", "sql", "schema_design", "Dimensional Modeling: Fact Tables vs Dimension Tables (Star Schema)",
    ["star schema", "fact table", "dimension table", "dimensional modeling", "data warehouse modeling"],
    "Fact tables store quantitative business metrics (sales, revenue); Dimension tables store contextual descriptive filters (customers, dates, stores).")

add_doc("DOC-SQL-SCD-SLOWLY-CHANGING-DIMENSIONS", "sql", "schema_design", "Slowly Changing Dimensions (SCD Type 1, Type 2, Type 3)",
    ["scd", "slowly changing dimensions", "scd type 1", "scd type 2", "historical tracking"],
    "SCD Type 1 overwrites old values; SCD Type 2 preserves historical versions with start/end date timestamps; SCD Type 3 adds previous-value columns.")

# -------------------------------------------------------------------------
# 15. SECURITY, DCL & PERMISSIONS (8 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-DCL-GRANT-REVOKE", "sql", "security", "GRANT and REVOKE: Data Control Language (DCL) Permissions",
    ["grant", "revoke", "dcl", "database permissions", "data control language", "grant select"],
    "Manage database privileges:\n\n```sql\nGRANT SELECT, INSERT ON TABLE orders TO analyst_role;\nREVOKE DELETE ON TABLE orders FROM analyst_role;\n```")

add_doc("DOC-SQL-RBAC-ROLES", "sql", "security", "Role-Based Access Control (RBAC): Creating and Assigning Roles",
    ["rbac", "roles", "create role", "role based access control", "database security"],
    "Create roles to aggregate permissions and assign roles to users instead of granting direct permissions to individual accounts.")

add_doc("DOC-SQL-ROW-LEVEL-SECURITY", "sql", "security", "Row-Level Security (RLS): Enforcing Multi-Tenant Row Isolation",
    ["rls", "row level security", "multi tenant security", "create policy", "row security"],
    "PostgreSQL Row-Level Security restricts which rows a user can see based on security policies (e.g. `tenant_id = CURRENT_USER`).")

add_doc("DOC-SQL-INJECTION-DEFENSE", "sql", "security", "SQL Injection Defense: Parameterized Queries and Prepared Statements",
    ["sql injection", "sqli defense", "parameterized queries", "prepared statements", "prevent sql injection"],
    "SQL injection occurs when unescaped user inputs are concatenated into SQL strings. Always use Parameterized Queries / Prepared Statements.")

add_doc("DOC-SQL-COLUMN-MASKING", "sql", "security", "Dynamic Data Masking (DDM): Obscuring Sensitive PII Data",
    ["dynamic data masking", "data masking", "masking pii", "column masking"],
    "Obscure sensitive data (e.g. masking credit card numbers `XXXX-XXXX-XXXX-1234`) for non-privileged user queries.")

add_doc("DOC-SQL-DATABASE-AUDITING", "sql", "security", "Database Auditing: Tracking Schema Changes and DDL Events",
    ["database auditing", "ddl triggers", "audit log", "pgaudit", "compliance audit"],
    "Track all DDL operations and administrative logins for SOC2 and GDPR compliance.")

add_doc("DOC-SQL-ENCRYPTION-TDE", "sql", "security", "Transparent Data Encryption (TDE) and Data-at-Rest Protection",
    ["tde", "transparent data encryption", "encryption at rest", "database encryption"],
    "TDE encrypts underlying database data pages and log files on disk transparently to protect against stolen physical backups.")

add_doc("DOC-SQL-BACKUPS-PITR", "sql", "security", "Database Backups & Point-in-Time Recovery (PITR) with WAL",
    ["pitr", "point in time recovery", "database backups", "wal archiving", "disaster recovery"],
    "Combine full base backups with continuous WAL archiving to restore database state to any specific microsecond in the past.")

# -------------------------------------------------------------------------
# 16. DIALECTS & ENGINE INTERNALS (10 docs)
# -------------------------------------------------------------------------
add_doc("DOC-SQL-DIALECTS-COMPARISON", "sql", "dialects", "SQL Dialects: PostgreSQL vs MySQL vs SQLite vs SQL Server vs Oracle",
    ["dialects", "postgresql", "mysql", "sqlite", "sql server", "tsql", "oracle", "plsql", "dialect differences"],
    "Cross-platform comparisons of pagination, string concatenation, upsert statements, and procedural languages.")

add_doc("DOC-SQL-POSTGRES-FEATURES", "sql", "dialects", "PostgreSQL Advanced Capabilities: JSONB, Arrays, RETURNING, and Extensions",
    ["postgresql", "postgres features", "jsonb", "pg_stat_statements", "postgres extensions"],
    "PostgreSQL features: Native JSONB, array types, `RETURNING` clauses, custom extensions (PostGIS, pgvector), and full ACID compliance.")

add_doc("DOC-SQL-MYSQL-FEATURES", "sql", "dialects", "MySQL & InnoDB: Storage Engines, Clustered Keys, and Locking Semantics",
    ["mysql", "innodb", "myisam", "mysql features", "mysql architecture"],
    "MySQL InnoDB engine uses clustered primary keys, Next-Key locking to prevent phantom reads, and doublewrite buffers.")

add_doc("DOC-SQL-SQLITE-FEATURES", "sql", "dialects", "SQLite Architecture: Serverless, Single-File, Dynamic Typing & WAL Mode",
    ["sqlite", "serverless database", "sqlite wal mode", "type affinity sqlite"],
    "SQLite is an in-process, serverless, self-contained relational database engine with dynamic type affinity and lightweight zero-config storage.")

add_doc("DOC-SQL-SQLSERVER-TSQL", "sql", "dialects", "Microsoft SQL Server & T-SQL: TOP, CROSS APPLY, Indexed Views, and TempDB",
    ["sql server", "tsql", "t-sql", "cross apply", "indexed views", "tempdb"],
    "T-SQL extensions: `CROSS APPLY`, `TOP (n) WITH TIES`, table variables (`@table`), global temporary tables (`##temp`), and `MERGE`.")

add_doc("DOC-SQL-ORACLE-PLSQL", "sql", "dialects", "Oracle Database & PL/SQL: Packages, Sequences, DUAL Table, and NVL",
    ["oracle", "plsql", "dual table", "nvl", "oracle database"],
    "Oracle features: `DUAL` dummy table, `NVL()` null replacement, `ROWNUM`, `CONNECT BY` hierarchical queries, and robust PL/SQL packages.")

add_doc("DOC-SQL-OLTP-VS-OLAP", "sql", "dialects", "OLTP vs OLAP Systems: Transaction Processing vs Analytical Warehouses",
    ["oltp vs olap", "oltp", "olap", "row oriented vs column oriented", "data warehouse vs database"],
    "OLTP systems (PostgreSQL, MySQL) optimize for high-concurrency small row transactions; OLAP systems (Snowflake, BigQuery, ClickHouse) optimize for massive columnar scans.")

add_doc("DOC-SQL-ROW-VS-COLUMNAR", "sql", "dialects", "Row-Oriented vs Columnar Storage Engines: I/O and Compression",
    ["row oriented", "columnar storage", "column oriented", "data compression", "parquet vs postgres"],
    "Row-oriented engines store entire rows contiguously (great for single-row lookups); Columnar engines store individual columns contiguously (great for aggregating billions of numbers).")

add_doc("DOC-SQL-ANSI-STANDARDS", "sql", "dialects", "ANSI / ISO SQL Standards: SQL-92, SQL:1999, SQL:2003, SQL:2023",
    ["ansi sql", "iso sql", "sql-92", "sql:1999", "sql standards"],
    "Historical progression of SQL standards: SQL-92 (Joins), SQL:1999 (CTEs, Triggers), SQL:2003 (Window Functions), SQL:2023 (Property Graphs).")

add_doc("DOC-SQL-STORAGE-PAGE-INTERNALS", "sql", "dialects", "Database Storage Engine Internals: 8KB Pages, Slotted Pages, and Row Headers",
    ["storage pages", "slotted page architecture", "row header", "heap file", "database buffer pool"],
    "Databases read and write data in fixed-size blocks/pages (typically 8KB in Postgres/SQL Server, 16KB in InnoDB) with slotted page offset arrays.")

# Save to documents.json
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(docs, f, indent=2)

print(f"[+] Successfully compiled and saved {len(docs)} exhaustive SQL domain knowledge documents to {OUTPUT_FILE}")
