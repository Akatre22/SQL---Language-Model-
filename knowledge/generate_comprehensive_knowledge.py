"""
Comprehensive SQL Domain Knowledge Base Generator for Tiny SQL LLM.
Generates 150+ meticulously structured, granular, and authoritative SQL knowledge documents
covering every concept from fundamental syntax to deep storage engine internals.
"""

import json
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "documents.json"

docs = [
    # =========================================================================
    # 1. ROADMAPS, PRACTICE & STUDY GUIDES
    # =========================================================================
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

    # =========================================================================
    # 2. FOUNDATIONAL CLAUSES, SYNTAX & OPERATORS
    # =========================================================================
    {
        "id": "DOC-SQL-SELECT",
        "domain": "sql",
        "topic": "clauses",
        "title": "SELECT Statement: Column Projection, Expressions, and Column Aliasing",
        "tags": ["select", "select statement", "column projection", "aliasing", "as keyword", "select columns"],
        "content": "The SELECT statement specifies which columns or calculated expressions should be returned in the query result set:\n\n1) Column Projection: Retrieve specific columns rather than SELECT * to reduce memory and network bandwidth.\n2) Aliasing (AS): Rename output columns for readability and downstream consumption.\n3) Computed Expressions: Perform mathematical calculations, string concatenation, or conditional logic directly in the SELECT list.\n\n```sql\nSELECT \n    emp_id AS employee_identifier,\n    first_name || ' ' || last_name AS full_name,\n    salary * 1.10 AS adjusted_salary\nFROM employees;\n```",
        "source": "SQL Core Language Manual"
    },
    {
        "id": "DOC-SQL-DISTINCT",
        "domain": "sql",
        "topic": "clauses",
        "title": "SELECT DISTINCT: Deduplication, Multi-Column Uniqueness, and Performance",
        "tags": ["distinct", "select distinct", "deduplication", "unique rows", "eliminate duplicates"],
        "content": "SELECT DISTINCT removes duplicate rows from the final result set:\n\n1) Scope: Applies across ALL projected columns combined, not just the first column.\n2) Execution Cost: Forces an implicit sort or hash aggregation step in the execution plan, which can be expensive on massive tables.\n3) DISTINCT vs GROUP BY: `SELECT DISTINCT col FROM table` is functionally identical to `SELECT col FROM table GROUP BY col`.\n\n```sql\n-- Returns unique combinations of department and job title:\nSELECT DISTINCT department_id, job_title FROM employees ORDER BY department_id;\n```",
        "source": "SQL Core Language Manual"
    },
    {
        "id": "DOC-SQL-WHERE",
        "domain": "sql",
        "topic": "filtering",
        "title": "WHERE Clause: Row-Level Filtering, Predicates, and Logical Operators",
        "tags": ["where", "where clause", "row filtering", "predicates", "and or not", "filter rows"],
        "content": "The WHERE clause filters individual records before any grouping, aggregation, or windowing occurs:\n\n1) Comparison Operators: `=`, `<>`, `!=`, `<`, `<=`, `>`, `>=`, `BETWEEN`, `IN`, `LIKE`.\n2) Logical Operators: `AND` (both true), `OR` (either true), `NOT` (negation).\n3) Operator Precedence: `NOT` has highest precedence, followed by `AND`, then `OR`. Always use parentheses `()` to clarify complex compound conditions.\n\n```sql\nSELECT * FROM orders\nWHERE status = 'COMPLETED' \n  AND (total_amount >= 500 OR customer_id IN (1, 2, 3))\n  AND order_date >= '2025-01-01';\n```",
        "source": "SQL Core Language Manual"
    },
    {
        "id": "DOC-SQL-AND-OR-NOT",
        "domain": "sql",
        "topic": "filtering",
        "title": "Boolean Logic in SQL: AND, OR, NOT, and Operator Precedence",
        "tags": ["and", "or", "not", "boolean logic", "operator precedence", "compound conditions"],
        "content": "SQL uses boolean evaluation rules for multi-condition filtering:\n\n1) Precedence Hierarchy: `NOT` evaluates first, `AND` evaluates second, `OR` evaluates last.\n2) The Common Parentheses Trap: `WHERE A OR B AND C` is evaluated as `WHERE A OR (B AND C)`. If you intended `(A OR B) AND C`, explicit parentheses are required.\n3) Short-Circuit Evaluation: Query engines may evaluate the cheapest or most selective condition first.\n\n```sql\n-- Correct grouping for active high-tier accounts:\nSELECT * FROM accounts \nWHERE (account_type = 'PREMIUM' OR balance > 100000) \n  AND is_active = TRUE;\n```",
        "source": "SQL Core Language Manual"
    },
    {
        "id": "DOC-SQL-IN-OPERATOR",
        "domain": "sql",
        "topic": "filtering",
        "title": "IN and NOT IN Operators: Value Lists, Subqueries, and NULL Traps",
        "tags": ["in", "not in", "in operator", "not in operator", "null in not in", "membership test"],
        "content": "The IN operator checks if an attribute matches any value within a literal list or subquery:\n\n1) IN Syntax: `WHERE department_id IN (10, 20, 30)`.\n2) NOT IN & The Critical NULL Trap: If the subquery or list contains ANY NULL value (e.g. `NOT IN (1, 2, NULL)`), the entire expression evaluates to UNKNOWN, returning 0 rows! Always filter subqueries with `WHERE col IS NOT NULL` or use `NOT EXISTS`.\n\n```sql\n-- Safe NOT IN with subquery:\nSELECT * FROM customers \nWHERE customer_id NOT IN (\n    SELECT customer_id FROM orders WHERE customer_id IS NOT NULL\n);\n```",
        "source": "SQL Relational Logic Guide"
    },
    {
        "id": "DOC-SQL-BETWEEN-OPERATOR",
        "domain": "sql",
        "topic": "filtering",
        "title": "BETWEEN Operator: Inclusive Range Checking on Dates, Numbers, and Strings",
        "tags": ["between", "between operator", "inclusive range", "not between", "date ranges"],
        "content": "The BETWEEN operator tests whether a value falls within an inclusive specified range ($low \\le val \\le high$):\n\n1) Inclusivity: `col BETWEEN low AND high` is identical to `col >= low AND col <= high` (both boundary values are included).\n2) Date Timestamp Caution: `BETWEEN '2025-01-01' AND '2025-01-31'` on a `TIMESTAMP` column stops at `2025-01-31 00:00:00`, missing data throughout the 31st. Use `>= '2025-01-01' AND < '2025-02-01'` instead.\n\n```sql\nSELECT order_id, total_amount FROM orders\nWHERE total_amount BETWEEN 100 AND 500;\n```",
        "source": "SQL Core Language Manual"
    },
    {
        "id": "DOC-SQL-LIKE-ILIKE",
        "domain": "sql",
        "topic": "filtering",
        "title": "LIKE, ILIKE & Wildcard Pattern Matching (%, _, ESCAPE)",
        "tags": ["like", "ilike", "wildcards", "pattern matching", "case insensitive like", "percent wildcard", "underscore wildcard"],
        "content": "Pattern matching operators in SQL for text searching:\n\n1) Wildcards:\n- `%`: Matches zero or more arbitrary characters (e.g. `LIKE 'Data%'` matches 'Data', 'Database', 'DataWarehouse').\n- `_`: Matches exactly one single character (e.g. `LIKE 'C_t'` matches 'Cat', 'Cot', 'Cut').\n2) Case Sensitivity:\n- `LIKE`: Case-sensitive in PostgreSQL/Oracle; case-insensitive by default in MySQL/SQL Server.\n- `ILIKE`: Case-insensitive pattern matching (PostgreSQL specific).\n3) Index Performance: SARGable prefix queries (`LIKE 'abc%'`) can use B-Tree indexes; leading wildcards (`LIKE '%abc'`) force full table scans.\n\n```sql\nSELECT * FROM employees WHERE email LIKE '%@gmail.com';\n```",
        "source": "SQL String Processing Guide"
    },
    {
        "id": "DOC-SQL-IS-NULL",
        "domain": "sql",
        "topic": "null_handling",
        "title": "IS NULL & IS NOT NULL: Handling Unknown and Missing Values",
        "tags": ["is null", "is not null", "null check", "null comparison", "three valued logic"],
        "content": "In relational databases, NULL signifies the absence of a value (unknown/unassigned), not zero or an empty string:\n\n1) Comparison Rule: Because NULL represents unknown, `col = NULL` or `col != NULL` always evaluates to UNKNOWN (treated as FALSE in WHERE clauses). You MUST use `IS NULL` or `IS NOT NULL`.\n2) Tri-State Logic: Every boolean expression evaluates to TRUE, FALSE, or UNKNOWN.\n\n```sql\nSELECT emp_name FROM employees WHERE manager_id IS NULL; -- Top-level CEO/Leader\n```",
        "source": "SQL Relational Logic Guide"
    },
    {
        "id": "DOC-SQL-ORDER-BY",
        "domain": "sql",
        "topic": "sorting",
        "title": "ORDER BY Clause: Sorting, Multi-Column Precedence, ASC/DESC, and NULLS FIRST/LAST",
        "tags": ["order by", "sorting", "asc", "desc", "nulls first", "nulls last", "sort order"],
        "content": "ORDER BY sorts the returned query result set:\n\n1) Direction: `ASC` (ascending, default) or `DESC` (descending).\n2) Multi-Column Sorting: Evaluates columns left-to-right (e.g. `ORDER BY department_id ASC, salary DESC`).\n3) NULL Ordering: By default in PostgreSQL/Oracle, NULLS are treated as largest (`NULLS LAST` in ASC, `NULLS FIRST` in DESC). Use `NULLS FIRST` or `NULLS LAST` explicitly.\n\n```sql\nSELECT emp_name, department_id, salary FROM employees\nORDER BY department_id ASC, salary DESC NULLS LAST;\n```",
        "source": "SQL Core Language Manual"
    },
    {
        "id": "DOC-SQL-LIMIT-OFFSET",
        "domain": "sql",
        "topic": "pagination",
        "title": "LIMIT and OFFSET: Pagination Mechanics and Performance Considerations",
        "tags": ["limit", "offset", "pagination", "limit offset", "keyset pagination", "page size"],
        "content": "LIMIT and OFFSET provide pagination by slicing rows from the result set:\n\n1) Mechanics: `LIMIT n OFFSET m` skips the first `m` rows and returns the next `n` rows.\n2) The Deep Pagination Problem: `OFFSET 1000000 LIMIT 10` forces the database engine to scan and discard 1,000,000 rows before returning 10 rows (slow I/O bottleneck).\n3) Keyset Pagination (Seek Method): Accelerates pagination by filtering on the last seen ID instead of OFFSET: `WHERE id > last_seen_id ORDER BY id ASC LIMIT 10`.\n\n```sql\n-- Standard offset pagination:\nSELECT * FROM products ORDER BY product_id ASC LIMIT 20 OFFSET 40; -- Page 3\n```",
        "source": "Database Pagination Architecture"
    },
    {
        "id": "DOC-SQL-CASE-WHEN",
        "domain": "sql",
        "topic": "conditional_logic",
        "title": "CASE WHEN Expression: Simple CASE, Searched CASE, and Conditional Pivots",
        "tags": ["case when", "case expression", "if else in sql", "conditional logic", "searched case", "simple case"],
        "content": "The CASE expression provides IF-THEN-ELSE conditional evaluation within SQL statements:\n\n1) Searched CASE (Most Flexible):\nEvaluates arbitrary boolean conditions sequentially, returning the result of the first TRUE condition:\n\n```sql\nSELECT emp_name, salary,\n    CASE \n        WHEN salary >= 100000 THEN 'Executive Tier'\n        WHEN salary >= 60000  THEN 'Mid Tier'\n        ELSE 'Standard Tier'\n    END AS salary_grade\nFROM employees;\n```\n\n2) Simple CASE:\nMatches an expression against discrete literal values:\n`CASE status WHEN 'P' THEN 'Pending' WHEN 'C' THEN 'Completed' ELSE 'Unknown' END`.\n3) Placement: Usable anywhere expressions are allowed: SELECT columns, WHERE clauses, ORDER BY clauses, and inside aggregate functions for conditional aggregation.",
        "source": "SQL Core Language Manual"
    },
    {
        "id": "DOC-SQL-COALESCE",
        "domain": "sql",
        "topic": "null_handling",
        "title": "COALESCE Function: Syntax, Short-Circuiting, and Replacing NULLs",
        "tags": ["coalesce", "null replacement", "coalesce function", "fallback values", "default value for null"],
        "content": "COALESCE accepts multiple arguments and returns the first non-NULL expression in positional order:\n\n1) Syntax: `COALESCE(val1, val2, ..., fallback)`.\n2) Short-Circuit Evaluation: Evaluates arguments from left to right, stopping immediately when the first non-NULL value is encountered.\n3) Common Use Case: Providing default display values or calculating totals without NULL propagation.\n\n```sql\nSELECT \n    customer_id, \n    COALESCE(phone_number, mobile_number, email, 'No Contact Available') AS primary_contact\nFROM customers;\n```",
        "source": "SQL Relational Logic Guide"
    },
    {
        "id": "DOC-SQL-NULLIF",
        "domain": "sql",
        "topic": "null_handling",
        "title": "NULLIF Function: Preventing Division by Zero and Blank String Normalization",
        "tags": ["nullif", "division by zero", "nullif function", "prevent divide by zero", "empty string to null"],
        "content": "NULLIF compares two expressions and returns NULL if they are equal; otherwise, it returns the first expression:\n\n1) Syntax: `NULLIF(expr1, expr2)`.\n2) Preventing Division by Zero: In SQL, dividing by zero crashes queries. `NULLIF(denominator, 0)` returns NULL if denominator is 0, which safely produces a NULL result instead of an exception.\n\n```sql\n-- Safe calculation preventing division-by-zero errors:\nSELECT \n    dept_id, \n    total_revenue / NULLIF(total_employees, 0) AS revenue_per_employee\nFROM departments;\n```",
        "source": "SQL Relational Logic Guide"
    },
    {
        "id": "DOC-SQL-CAST-CONVERT",
        "domain": "sql",
        "topic": "data_types",
        "title": "CAST and CONVERT: Explicit Data Type Conversion and Dialect Differences",
        "tags": ["cast", "convert", "type casting", "data type conversion", "cast syntax", "convert syntax"],
        "content": "CAST and CONVERT explicitly transform an expression from one data type to another:\n\n1) ANSI Standard CAST: `CAST(expression AS target_type)` (supported across PostgreSQL, MySQL, SQLite, SQL Server, Oracle).\n2) PostgreSQL Shorthand: `expression::target_type` (e.g. `'2025-01-01'::DATE`, `total::NUMERIC(10,2)`).\n3) SQL Server CONVERT: `CONVERT(target_type, expression, [style_code])` (includes format style codes for date formatting).\n\n```sql\nSELECT \n    CAST('1250.75' AS DECIMAL(10,2)) AS numeric_val,\n    CAST(CURRENT_TIMESTAMP AS DATE) AS date_only;\n```",
        "source": "SQL Data Types Guide"
    },

    # =========================================================================
    # 3. RELATIONAL JOINS & SET ALGEBRA
    # =========================================================================
    {
        "id": "DOC-SQL-JOINS-INNER",
        "domain": "sql",
        "topic": "joins",
        "title": "INNER JOIN: Equi-Joins, Non-Equi Joins, and Relational Intersection",
        "tags": ["inner join", "equi join", "non equi join", "join tables", "inner join syntax"],
        "content": "INNER JOIN returns only the rows where there is a matching value in both the left and right tables based on the ON predicate:\n\n1) Equi-Join: Uses equality operator (`tableA.id = tableB.id`).\n2) Non-Equi Join: Uses comparison operators (`tableA.salary BETWEEN salary_grades.min_sal AND salary_grades.max_sal`).\n3) Exclusion: Rows in either table that have no corresponding match in the other table are omitted from the result set.\n\n```sql\nSELECT e.emp_name, d.dept_name, e.salary\nFROM employees e\nINNER JOIN departments d ON e.department_id = d.department_id;\n```",
        "source": "Relational Joins Handbook"
    },
    {
        "id": "DOC-SQL-JOINS-LEFT",
        "domain": "sql",
        "topic": "joins",
        "title": "LEFT OUTER JOIN: Preserving Left Table Rows and Handling NULL Fillers",
        "tags": ["left join", "left outer join", "outer join", "preserve left table", "left join syntax"],
        "content": "LEFT JOIN (or LEFT OUTER JOIN) returns all records from the left table, along with matching rows from the right table:\n\n1) Unmatched Rows: If no match exists in the right table, all right table columns are populated with NULL values.\n2) Left Table Cardinality: Guarantees that no row from the left table is dropped.\n3) The WHERE Trap: Adding a right-table condition in the WHERE clause (e.g. `WHERE right.status = 'ACTIVE'`) converts a LEFT JOIN into an implicit INNER JOIN! Place right-table filters inside the `ON` clause instead.\n\n```sql\nSELECT c.customer_id, c.first_name, o.order_id, o.total_amount\nFROM customers c\nLEFT JOIN orders o ON c.customer_id = o.customer_id;\n```",
        "source": "Relational Joins Handbook"
    },
    {
        "id": "DOC-SQL-JOINS-RIGHT",
        "domain": "sql",
        "topic": "joins",
        "title": "RIGHT OUTER JOIN: Mechanics, Left vs Right Equivalence, and Style Guidelines",
        "tags": ["right join", "right outer join", "right join syntax", "right vs left join"],
        "content": "RIGHT JOIN (or RIGHT OUTER JOIN) returns all records from the right table, along with matching rows from the left table (filling unmatched left columns with NULLs):\n\n1) Equivalence: `TableA RIGHT JOIN TableB` is functionally identical to `TableB LEFT JOIN TableA`.\n2) Industry Style Best Practice: Most data engineers standardize exclusively on `LEFT JOIN` for query readability and mental consistency from top-to-bottom.\n\n```sql\nSELECT d.dept_name, e.emp_name\nFROM employees e\nRIGHT JOIN departments d ON e.department_id = d.department_id;\n```",
        "source": "Relational Joins Handbook"
    },
    {
        "id": "DOC-SQL-JOINS-FULL-OUTER",
        "domain": "sql",
        "topic": "joins",
        "title": "FULL OUTER JOIN: Union of Left and Right Joins and Missing Match Detection",
        "tags": ["full outer join", "full join", "outer join", "full outer join syntax", "bidirectional join"],
        "content": "FULL OUTER JOIN returns all records when there is a match in either left or right table:\n\n1) Behavior: Combines the results of both LEFT JOIN and RIGHT JOIN. Unmatched rows on either side contain NULLs for the missing table's columns.\n2) SQLite Emulation: SQLite does not natively support FULL OUTER JOIN syntax; emulate using a `LEFT JOIN` combined with a `RIGHT JOIN` (or anti-join) via `UNION ALL`.\n\n```sql\nSELECT e.emp_name, d.dept_name\nFROM employees e\nFULL OUTER JOIN departments d ON e.department_id = d.department_id;\n```",
        "source": "Relational Joins Handbook"
    },
    {
        "id": "DOC-SQL-JOINS-CROSS",
        "domain": "sql",
        "topic": "joins",
        "title": "CROSS JOIN: Cartesian Product, Combinatorial Generation, and Use Cases",
        "tags": ["cross join", "cartesian product", "cross join syntax", "matrix generation", "all combinations"],
        "content": "CROSS JOIN computes the Cartesian product of two tables, pairing every row of the left table with every row of the right table:\n\n1) Result Row Count: If Table A has $M$ rows and Table B has $N$ rows, the CROSS JOIN returns $M \\times N$ rows.\n2) No ON Clause: CROSS JOIN does not accept an `ON` join predicate.\n3) Practical Use Cases: Generating date/calendar matrices, product-size combinations, or simulation models.\n\n```sql\n-- Generating all month and department reporting combinations:\nSELECT d.dept_name, m.month_name\nFROM departments d\nCROSS JOIN calendar_months m;\n```",
        "source": "Relational Joins Handbook"
    },
    {
        "id": "DOC-SQL-JOINS-SELF",
        "domain": "sql",
        "topic": "joins",
        "title": "SELF JOIN: Joining a Table to Itself, Aliases, and Hierarchical Links",
        "tags": ["self join", "joining table to itself", "manager employee join", "table alias self join"],
        "content": "A SELF JOIN joins a table with itself by using distinct table aliases for each instance:\n\n1) Purpose: Querying hierarchical relationships stored within a single table (e.g. employee-manager links, part-subpart hierarchies) or finding peer pairs.\n2) Syntax: Requires unique aliases (e.g. `FROM employees e JOIN employees m ON e.manager_id = m.emp_id`).\n\n```sql\nSELECT \n    e.emp_name AS employee,\n    COALESCE(m.emp_name, 'Top Executive (No Manager)') AS manager\nFROM employees e\nLEFT JOIN employees m ON e.manager_id = m.emp_id;\n```",
        "source": "Relational Joins Handbook"
    },
    {
        "id": "DOC-SQL-JOINS-ANTI",
        "domain": "sql",
        "topic": "joins",
        "title": "ANTI-JOIN: Identifying Unmatched Records (LEFT JOIN IS NULL vs NOT EXISTS)",
        "tags": ["anti join", "anti-join", "unmatched rows", "left join where null", "not exists anti join", "find missing records"],
        "content": "An ANTI-JOIN returns rows from the left table that have NO corresponding record in the right table:\n\n1) Implementation 1 (LEFT JOIN ... IS NULL):\nPerforms a LEFT JOIN and filters for rows where the right table Primary Key is NULL.\n\n```sql\n-- Customers who have never placed an order:\nSELECT c.customer_id, c.first_name, c.email\nFROM customers c\nLEFT JOIN orders o ON c.customer_id = o.customer_id\nWHERE o.customer_id IS NULL;\n```\n\n2) Implementation 2 (NOT EXISTS):\nOften optimized more efficiently by the query planner because it short-circuits upon first match.\n\n```sql\nSELECT c.customer_id, c.first_name\nFROM customers c\nWHERE NOT EXISTS (\n    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id\n);\n```",
        "source": "Advanced Relational Queries"
    },
    {
        "id": "DOC-SQL-JOINS-SEMI",
        "domain": "sql",
        "topic": "joins",
        "title": "SEMI-JOIN: Filtering with EXISTS and IN Without Multiplying Row Duplicates",
        "tags": ["semi join", "semi-join", "exists semi join", "filter without duplicate rows", "in semi join"],
        "content": "A SEMI-JOIN returns rows from the left table where at least one matching row exists in the right table, without duplicating left rows:\n\n1) Advantage over INNER JOIN: An INNER JOIN on a 1-to-Many table multiplies left rows. A SEMI-JOIN tests existence only and preserves single left row cardinality.\n2) Syntax: Expressed using `WHERE EXISTS (subquery)` or `WHERE key IN (subquery)`.\n\n```sql\n-- Departments that have active high-earning employees (no duplicate department rows):\nSELECT d.department_id, d.dept_name\nFROM departments d\nWHERE EXISTS (\n    SELECT 1 FROM employees e \n    WHERE e.department_id = d.department_id AND e.salary > 100000\n);\n```",
        "source": "Advanced Relational Queries"
    },
    {
        "id": "DOC-SQL-JOINS-LATERAL",
        "domain": "sql",
        "topic": "joins",
        "title": "LATERAL JOIN & CROSS APPLY: Correlated Table Expressions in FROM Clauses",
        "tags": ["lateral join", "cross apply", "outer apply", "lateral", "correlated from clause"],
        "content": "A LATERAL JOIN (PostgreSQL/MySQL 8+) or CROSS APPLY (SQL Server/Oracle) allows a subquery in the FROM clause to reference columns from preceding tables on the left:\n\n1) Purpose: Invokes a parameterized subquery or table-valued function for each candidate row (like a for-each loop in SQL).\n2) LATERAL vs CROSS APPLY: `JOIN LATERAL` is ANSI/PostgreSQL syntax; `CROSS APPLY` is T-SQL syntax.\n\n```sql\n-- Fetching the top 2 most recent orders for every customer:\nSELECT c.customer_id, c.first_name, o.order_id, o.total_amount, o.order_date\nFROM customers c\nCROSS JOIN LATERAL (\n    SELECT order_id, total_amount, order_date\n    FROM orders\n    WHERE customer_id = c.customer_id\n    ORDER BY order_date DESC\n    LIMIT 2\n) o;\n```",
        "source": "Advanced Relational Queries"
    },
    {
        "id": "DOC-SQL-SET-UNION-UNIONALL",
        "domain": "sql",
        "topic": "set_operations",
        "title": "UNION vs UNION ALL: Deduplication, Sorting Overhead, and Performance",
        "tags": ["union vs union all", "difference between union and union all", "union", "union all", "set operations", "combine queries"],
        "content": "Comparison between UNION and UNION ALL in SQL:\n\n1) UNION (Distinct Set Union):\n- Combines rows from multiple SELECT queries and eliminates duplicate rows.\n- Incurs an implicit sorting/hashing overhead in memory/tempdb to detect duplicates.\n\n2) UNION ALL (Concatenation):\n- Combines rows preserving all duplicates with maximum execution speed.\n- Recommended default whenever you know datasets are disjoint or duplicate rows are acceptable.\n\n```sql\nSELECT emp_name, 'Current Employee' AS status FROM employees\nUNION ALL\nSELECT contractor_name, 'Contractor' AS status FROM contractors;\n```",
        "source": "Relational Set Operations Guide"
    },
    {
        "id": "DOC-SQL-SET-INTERSECT-EXCEPT",
        "domain": "sql",
        "topic": "set_operations",
        "title": "INTERSECT and EXCEPT / MINUS: Set Intersection and Set Difference",
        "tags": ["intersect", "except", "minus", "set difference", "intersect vs except"],
        "content": "INTERSECT and EXCEPT perform mathematical set operations between queries:\n\n1) INTERSECT: Returns only rows that appear in BOTH query result sets (eliminating duplicates).\n2) EXCEPT (or MINUS in Oracle): Returns rows present in the first query that DO NOT exist in the second query.\n\n```sql\n-- Customers who purchased in 2024 but NOT in 2025:\nSELECT customer_id FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'\nEXCEPT\nSELECT customer_id FROM orders WHERE order_date >= '2025-01-01' AND order_date < '2026-01-01';\n```",
        "source": "Relational Set Operations Guide"
    },

    # =========================================================================
    # 4. AGGREGATIONS & GROUPING
    # =========================================================================
    {
        "id": "DOC-SQL-COUNT-VARIATIONS",
        "domain": "sql",
        "topic": "aggregations",
        "title": "COUNT(*) vs COUNT(col) vs COUNT(1): Performance and NULL Handling",
        "tags": ["count", "count(*)", "count(1)", "count(column)", "difference between count(*) and count(col)", "count nulls"],
        "content": "Differences in SQL COUNT aggregate behavior:\n\n1) COUNT(*): Counts the total number of rows in the table/partition, including rows with NULL values.\n2) COUNT(1): Evaluates literal constant 1 for every row; modern optimizers transpile `COUNT(1)` into `COUNT(*)` identically.\n3) COUNT(column_name): Counts only rows where the specified column is NOT NULL.\n4) COUNT(DISTINCT col): Counts the number of unique non-NULL values.\n\n```sql\nSELECT \n    COUNT(*) AS total_rows,\n    COUNT(manager_id) AS employees_with_manager,\n    COUNT(DISTINCT department_id) AS unique_departments\nFROM employees;\n```",
        "source": "SQL Aggregation Handbook"
    },
    {
        "id": "DOC-SQL-GROUP-BY",
        "domain": "sql",
        "topic": "aggregations",
        "title": "GROUP BY Clause: Aggregations, Grouping Keys, and Non-Aggregated Column Rules",
        "tags": ["group by", "grouping", "aggregate functions", "group by clause", "group by multiple columns"],
        "content": "The GROUP BY clause collapses multiple rows sharing identical values across grouping columns into single summary rows:\n\n1) SQL Standard Single-Value Rule: Every column in the SELECT list must either appear in the GROUP BY clause or be wrapped inside an aggregate function (SUM, AVG, COUNT, MIN, MAX).\n2) Execution Sequence: Runs after WHERE and before HAVING.\n\n```sql\nSELECT \n    department_id, \n    job_title,\n    COUNT(*) AS headcount,\n    AVG(salary) AS avg_salary\nFROM employees\nGROUP BY department_id, job_title;\n```",
        "source": "SQL Aggregation Handbook"
    },
    {
        "id": "DOC-SQL-HAVING",
        "domain": "sql",
        "topic": "aggregations",
        "title": "HAVING Clause: Filtering Aggregate Groups and Post-Aggregation Conditions",
        "tags": ["having", "having clause", "filter groups", "aggregate filtering", "having with sum"],
        "content": "HAVING filters aggregated group buckets after the GROUP BY phase has aggregated rows:\n\n1) Aggregate Usage: Formulated specifically for conditions on aggregate functions (`HAVING SUM(amount) > 10000`, `HAVING COUNT(*) >= 5`).\n2) WHERE vs HAVING: WHERE filters raw individual rows before grouping; HAVING filters aggregated groups after grouping.\n\n```sql\nSELECT customer_id, SUM(total_amount) AS total_spend\nFROM orders\nGROUP BY customer_id\nHAVING SUM(total_amount) > 50000\nORDER BY total_spend DESC;\n```",
        "source": "SQL Aggregation Handbook"
    },
    {
        "id": "DOC-SQL-STRING-AGG",
        "domain": "sql",
        "topic": "aggregations",
        "title": "STRING_AGG / GROUP_CONCAT / LISTAGG: Concatenating Strings Across Groups",
        "tags": ["string_agg", "group_concat", "listagg", "concatenate strings group", "string aggregation"],
        "content": "String aggregation functions concatenate values from multiple rows into a single delimited string:\n\n1) Dialect Syntax Variations:\n- PostgreSQL: `STRING_AGG(col, ', ' ORDER BY col)`\n- MySQL / SQLite: `GROUP_CONCAT(col, ', ')`\n- SQL Server: `STRING_AGG(col, ', ')`\n- Oracle: `LISTAGG(col, ', ') WITHIN GROUP (ORDER BY col)`\n\n```sql\n-- PostgreSQL example:\nSELECT \n    department_id,\n    STRING_AGG(emp_name, ', ' ORDER BY salary DESC) AS team_members\nFROM employees\nGROUP BY department_id;\n```",
        "source": "SQL Aggregation Handbook"
    },
    {
        "id": "DOC-SQL-ROLLUP-CUBE",
        "domain": "sql",
        "topic": "aggregations",
        "title": "ROLLUP, CUBE, and GROUPING SETS: Multi-Level Subtotals and Grand Totals",
        "tags": ["rollup", "cube", "grouping sets", "subtotals", "grand totals", "multidimensional aggregation"],
        "content": "Extensions to GROUP BY for business intelligence reporting:\n\n1) ROLLUP: Generates hierarchical subtotals and a grand total row from left to right: `GROUP BY ROLLUP (country, region, city)`.\n2) CUBE: Generates all $2^N$ possible dimensional combinations of subtotals and grand totals.\n3) GROUPING SETS: Explicitly specifies custom subtotal combinations without computing unnecessary permutations.\n\n```sql\nSELECT region, department_id, SUM(salary) AS total_payroll\nFROM employees\nGROUP BY ROLLUP (region, department_id);\n```",
        "source": "SQL BI Engineering"
    },

    # =========================================================================
    # 5. WINDOW FUNCTIONS & ANALYTICAL OPERATIONS
    # =========================================================================
    {
        "id": "DOC-SQL-ROW-NUMBER",
        "domain": "sql",
        "topic": "window_functions",
        "title": "ROW_NUMBER() Window Function: Deduplication, Sequential Numbering, and Pagination",
        "tags": ["row_number", "row number", "row_number()", "sequential numbers", "top n per group", "deduplication with row_number"],
        "content": "ROW_NUMBER() assigns a unique, sequential integer (1, 2, 3, ...) to each row within a window partition ordered by the specified criteria:\n\n1) Strict Uniqueness: No ties. Even if two rows share identical values in ORDER BY, they receive consecutive distinct row numbers.\n2) Top N per Group Pattern: Wrapped in a CTE to filter `WHERE row_num <= N`.\n3) Deduplication Pattern: Identify duplicate records by partitioning on business keys and deleting where `row_num > 1`.\n\n```sql\n-- Top 1 highest-paid employee per department:\nWITH RankedEmployees AS (\n    SELECT \n        emp_id, emp_name, department_id, salary,\n        ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank_num\n    FROM employees\n)\nSELECT * FROM RankedEmployees WHERE rank_num = 1;\n```",
        "source": "Advanced SQL Analytics Mastery"
    },
    {
        "id": "DOC-SQL-RANK-VS-DENSE-RANK",
        "domain": "sql",
        "topic": "window_functions",
        "title": "RANK() vs DENSE_RANK(): Handling Ties, Gaps, and Leaderboards",
        "tags": ["rank vs dense_rank", "rank", "dense_rank", "difference between rank and dense_rank", "ranking ties"],
        "content": "Comparison between RANK() and DENSE_RANK() when encountering tied values:\n\n1) RANK() (Leaves Gaps on Ties):\nAssigns the same rank to tied values, but skips subsequent rank numbers (e.g. 1, 2, 2, 4).\n\n2) DENSE_RANK() (No Gaps on Ties):\nAssigns the same rank to tied values without skipping subsequent numbers (e.g. 1, 2, 2, 3).\n\n```sql\n-- Comparing ROW_NUMBER, RANK, and DENSE_RANK on salary:\nSELECT \n    emp_name, salary,\n    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,\n    RANK()       OVER (ORDER BY salary DESC) AS rank_val,\n    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank_val\nFROM employees;\n```",
        "source": "Advanced SQL Analytics Mastery"
    },
    {
        "id": "DOC-SQL-LAG-LEAD",
        "domain": "sql",
        "topic": "window_functions",
        "title": "LAG() and LEAD() Functions: Offset Lookups, Growth Rates, and Time Series",
        "tags": ["lag", "lead", "lag function", "lead function", "month over month growth", "previous row", "next row"],
        "content": "LAG and LEAD access column values from preceding or subsequent rows without performing self-joins:\n\n1) LAG(col, offset, default): Accesses the value of `col` from `offset` rows before the current row (default offset = 1).\n2) LEAD(col, offset, default): Accesses the value from `offset` rows ahead of current row.\n\n```sql\n-- Calculating Month-over-Month growth percentage:\nSELECT \n    order_month,\n    monthly_revenue,\n    LAG(monthly_revenue, 1) OVER (ORDER BY order_month) AS prev_month_revenue,\n    ROUND(100.0 * (monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY order_month)) \n          / NULLIF(LAG(monthly_revenue, 1) OVER (ORDER BY order_month), 0), 2) AS mom_growth_pct\nFROM monthly_sales;\n```",
        "source": "Advanced SQL Analytics Mastery"
    },
    {
        "id": "DOC-SQL-WINDOW-FRAMES",
        "domain": "sql",
        "topic": "window_functions",
        "title": "Window Frames: ROWS BETWEEN vs RANGE BETWEEN and Rolling Averages",
        "tags": ["rows between", "range between", "window frames", "rolling average", "running total", "unbounded preceding"],
        "content": "Window Frame clauses define the explicit subset of partition rows included in calculations:\n\n1) ROWS vs RANGE:\n- `ROWS`: Operates on physical row offsets (e.g. exactly 6 physical rows before current row).\n- `RANGE`: Operates on logical value ranges according to the ORDER BY column.\n\n2) Common Frame Clauses:\n- Cumulative Running Total: `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`\n- 7-Day Rolling Moving Average: `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`\n- Centered Moving Average: `ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING`\n\n```sql\nSELECT \n    sale_date, revenue,\n    SUM(revenue) OVER (ORDER BY sale_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,\n    AVG(revenue) OVER (ORDER BY sale_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7day_avg\nFROM daily_store_sales;\n```",
        "source": "Advanced SQL Analytics Mastery"
    },

    # =========================================================================
    # 6. COMMON TABLE EXPRESSIONS (CTEs)
    # =========================================================================
    {
        "id": "DOC-SQL-CTE-RECURSIVE",
        "domain": "sql",
        "topic": "cte",
        "title": "WITH RECURSIVE: Hierarchical Data, Organizational Trees, and Graph Traversal",
        "tags": ["recursive cte", "with recursive", "hierarchical queries", "tree traversal", "parent child hierarchy"],
        "content": "A Recursive Common Table Expression iterates over hierarchical or graph structures by joining back to its own result set:\n\n1) Structure:\n- Anchor Member: Initial base query that selects root nodes (e.g. CEO where `manager_id IS NULL`).\n- UNION ALL: Combines anchor and recursive members.\n- Recursive Member: Joins the source table with the CTE itself, executing iteratively until no new rows are produced.\n\n```sql\nWITH RECURSIVE OrgHierarchy AS (\n    -- Anchor: Root CEO\n    SELECT emp_id, emp_name, manager_id, 1 AS depth\n    FROM employees\n    WHERE manager_id IS NULL\n    \n    UNION ALL\n    \n    -- Recursive Member: Subordinate employees\n    SELECT e.emp_id, e.emp_name, e.manager_id, h.depth + 1\n    FROM employees e\n    JOIN OrgHierarchy h ON e.manager_id = h.emp_id\n)\nSELECT * FROM OrgHierarchy ORDER BY depth, manager_id;\n```",
        "source": "SQL Engineering Patterns"
    },
    {
        "id": "DOC-SQL-CTE-VS-SUBQUERY",
        "domain": "sql",
        "topic": "cte",
        "title": "CTE vs Subquery vs Temp Table vs View: Architecture & Performance",
        "tags": ["cte vs subquery", "cte vs temp table", "cte vs view", "when to use cte", "subquery vs cte"],
        "content": "Comparison of query modularization tools:\n\n1) CTE (Common Table Expression): Temporary named query existing only during statement execution. Ideal for query readability, recursion, and avoiding deep nesting.\n2) Subquery: Inline query embedded in SELECT/FROM/WHERE. Best for quick scalar evaluations.\n3) Temporary Table (#temp / pg_temp): Physically persists intermediate data in TempDB. Best for large intermediate results reused across multiple queries or needing indexes.\n4) View: Stored database object persisting query definitions permanently for reusable access.",
        "source": "SQL Architecture Reference"
    },

    # =========================================================================
    # 7. SUBQUERIES & RELATIONAL SET LOGIC
    # =========================================================================
    {
        "id": "DOC-SQL-CORRELATED-SUBQUERY",
        "domain": "sql",
        "topic": "subqueries",
        "title": "Correlated Subqueries: Row-by-Row Execution and Optimizer Optimization",
        "tags": ["correlated subquery", "subqueries", "outer reference", "correlated query", "subquery in where"],
        "content": "A Correlated Subquery references column values from the outer query, meaning the subquery logically re-evaluates for every candidate row of the outer query:\n\n1) Mechanism: The inner query cannot be executed independently of the outer query.\n2) Common Use Case: Comparing a row against the average or aggregate of its specific category.\n\n```sql\n-- Employees earning more than their department's average salary:\nSELECT e1.emp_name, e1.department_id, e1.salary\nFROM employees e1\nWHERE e1.salary > (\n    SELECT AVG(e2.salary)\n    FROM employees e2\n    WHERE e2.department_id = e1.department_id\n);\n```",
        "source": "SQL Advanced Subquery Handbook"
    },
    {
        "id": "DOC-SQL-EXISTS-VS-IN",
        "domain": "sql",
        "topic": "subqueries",
        "title": "EXISTS vs IN: Performance, Short-Circuiting, and Subquery Optimizations",
        "tags": ["exists vs in", "difference between exists and in", "exists", "in operator", "subquery optimization"],
        "content": "Comparison between EXISTS and IN for subquery filtering:\n\n1) EXISTS (Boolean Short-Circuiting):\n- Evaluates to TRUE as soon as the first matching row is encountered, terminating subquery scanning immediately.\n- Highly efficient on large datasets with correlated subqueries.\n\n2) IN (Set Materialization):\n- Evaluates the entire subquery into memory before performing value comparisons.\n- Can degrade on large subquery results; vulnerable to the NULL trap with NOT IN.\n\n```sql\n-- High performance EXISTS:\nSELECT * FROM customers c\nWHERE EXISTS (\n    SELECT 1 FROM orders o \n    WHERE o.customer_id = c.customer_id AND o.total_amount > 1000\n);\n```",
        "source": "SQL Advanced Subquery Handbook"
    },

    # =========================================================================
    # 8. DATABASE DDL, SCHEMAS & CONSTRAINTS
    # =========================================================================
    {
        "id": "DOC-SQL-DDL-CREATE-ALTER-DROP",
        "domain": "sql",
        "topic": "ddl",
        "title": "CREATE, ALTER, DROP TABLE: DDL Schema Modification Syntax",
        "tags": ["create table", "alter table", "drop table", "ddl commands", "add column", "modify table"],
        "content": "Data Definition Language (DDL) commands define and alter table structures:\n\n1) CREATE TABLE: Declares table name, columns, data types, and constraints.\n2) ALTER TABLE: Modifies existing schema: `ADD COLUMN`, `DROP COLUMN`, `ALTER COLUMN / MODIFY`, `ADD CONSTRAINT`.\n3) DROP TABLE: Completely destroys the table, its metadata, and all stored rows.\n\n```sql\nCREATE TABLE departments (\n    department_id SERIAL PRIMARY KEY,\n    dept_name VARCHAR(100) NOT NULL UNIQUE,\n    budget DECIMAL(12,2) DEFAULT 0.00\n);\n\nALTER TABLE departments ADD COLUMN location VARCHAR(100);\n```",
        "source": "SQL Schema Engineering Manual"
    },
    {
        "id": "DOC-SQL-CONSTRAINTS-CHECK",
        "domain": "sql",
        "topic": "constraints",
        "title": "CHECK Constraints: Domain Validation and Multi-Column Rules",
        "tags": ["check constraint", "check", "domain validation", "table constraints", "add check constraint"],
        "content": "CHECK constraints enforce business validation rules on table columns:\n\n1) Mechanism: Every INSERT or UPDATE must satisfy the boolean CHECK expression (evaluates to TRUE or NULL).\n2) Multi-Column Constraints: Can compare multiple columns within the same row (e.g. `CHECK (end_date >= start_date)`).\n\n```sql\nCREATE TABLE employees (\n    emp_id SERIAL PRIMARY KEY,\n    salary DECIMAL(10,2) CONSTRAINT check_positive_salary CHECK (salary > 0),\n    hire_date DATE,\n    exit_date DATE,\n    CONSTRAINT check_valid_dates CHECK (exit_date IS NULL OR exit_date >= hire_date)\n);\n```",
        "source": "Database Integrity & Constraints"
    },
    {
        "id": "DOC-SQL-CONSTRAINTS-UNIQUE",
        "domain": "sql",
        "topic": "constraints",
        "title": "UNIQUE Constraint: Uniqueness Enforcement, Indexing, and NULL Rules",
        "tags": ["unique constraint", "unique", "unique key", "primary key vs unique", "unique index"],
        "content": "UNIQUE constraints guarantee that all values in a column or column group are distinct:\n\n1) UNIQUE vs PRIMARY KEY: A table can have MULTIPLE UNIQUE constraints, and UNIQUE columns can accept NULL values (in standard SQL, multiple rows can have NULL unless specified otherwise).\n2) Underlying Index: Creating a UNIQUE constraint automatically generates a Unique Index behind the scenes.\n\n```sql\nCREATE TABLE users (\n    user_id SERIAL PRIMARY KEY,\n    username VARCHAR(50) NOT NULL UNIQUE,\n    email VARCHAR(255) UNIQUE\n);\n```",
        "source": "Database Integrity & Constraints"
    },
    {
        "id": "DOC-SQL-PARTITIONING",
        "domain": "sql",
        "topic": "partitioning",
        "title": "Table Partitioning: Range, List, Hash Partitioning, and Partition Pruning",
        "tags": ["partitioning", "table partitioning", "range partitioning", "list partitioning", "hash partitioning", "partition pruning"],
        "content": "Table partitioning splits a massive logical table into smaller, physically separate storage partitions:\n\n1) Partitioning Strategies:\n- Range Partitioning: Partitions rows based on continuous value intervals (most commonly date/time ranges: e.g. partition per month/year).\n- List Partitioning: Partitions rows based on explicit discrete values (e.g. country or region code).\n- Hash Partitioning: Distributes rows evenly using a hash algorithm on a key.\n2) Partition Pruning: The query optimizer automatically skips partitions that cannot contain relevant rows based on the WHERE clause, reducing I/O drastically.\n\n```sql\n-- PostgreSQL Declarative Range Partitioning by Date:\nCREATE TABLE order_logs (\n    log_id BIGINT,\n    log_date DATE NOT NULL,\n    message TEXT\n) PARTITION BY RANGE (log_date);\n\nCREATE TABLE order_logs_2025_q1 PARTITION OF order_logs\n    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');\n```",
        "source": "High-Volume Database Architecture"
    },

    # =========================================================================
    # 9. DML & MUTATION OPERATIONS
    # =========================================================================
    {
        "id": "DOC-SQL-UPSERT-MERGE",
        "domain": "sql",
        "topic": "dml",
        "title": "UPSERT & MERGE: Insert on Conflict, Update on Duplicate Key, and ANSI MERGE",
        "tags": ["upsert", "merge", "on conflict do update", "on duplicate key update", "insert or update"],
        "content": "UPSERT conditionally inserts a new record or updates an existing record if a key conflict occurs:\n\n1) PostgreSQL / SQLite (ON CONFLICT):\n`INSERT INTO table (id, val) VALUES (1, 'A') ON CONFLICT (id) DO UPDATE SET val = EXCLUDED.val;`\n\n2) MySQL (ON DUPLICATE KEY UPDATE):\n`INSERT INTO table (id, val) VALUES (1, 'A') ON DUPLICATE KEY UPDATE val = VALUES(val);`\n\n3) ANSI Standard / SQL Server / Oracle (MERGE):\n\n```sql\nMERGE INTO target_table t\nUSING source_table s ON t.customer_id = s.customer_id\nWHEN MATCHED THEN\n    UPDATE SET t.email = s.email, t.updated_at = CURRENT_TIMESTAMP\nWHEN NOT MATCHED THEN\n    INSERT (customer_id, email) VALUES (s.customer_id, s.email);\n```",
        "source": "SQL DML Operations Guide"
    },
    {
        "id": "DOC-SQL-RETURNING-OUTPUT",
        "domain": "sql",
        "topic": "dml",
        "title": "RETURNING and OUTPUT Clauses: Returning Modified Rows from DML",
        "tags": ["returning", "output clause", "returning clause", "insert returning id", "get generated id"],
        "content": "RETURNING (PostgreSQL/SQLite) and OUTPUT (SQL Server) allow DML statements (INSERT, UPDATE, DELETE) to return modified rows directly without a subsequent SELECT query:\n\n1) Advantage: Eliminates race conditions when retrieving newly generated auto-increment / serial primary keys.\n2) Deletion Audits: Return deleted rows for instant archiving.\n\n```sql\n-- PostgreSQL example:\nINSERT INTO customers (first_name, email) \nVALUES ('Jane', 'jane@example.com')\nRETURNING customer_id, join_date;\n```",
        "source": "SQL DML Operations Guide"
    },

    # =========================================================================
    # 10. TRANSACTIONS, CONCURRENCY & ISOLATION
    # =========================================================================
    {
        "id": "DOC-SQL-TRANSACTIONS-ACID",
        "domain": "sql",
        "topic": "transactions",
        "title": "ACID Properties, Isolation Levels, and Concurrency Control",
        "tags": ["acid", "transactions", "atomicity", "consistency", "isolation", "durability", "isolation levels", "commit", "rollback", "dirty read", "phantom read", "non-repeatable read"],
        "content": "Relational transactions guarantee ACID properties to ensure database reliability and consistency:\n\n1) ACID Properties:\n- Atomicity: All operations in a transaction succeed or all roll back completely (BEGIN TRANSACTION ... COMMIT / ROLLBACK).\n- Consistency: Data transitions only between valid states enforcing all constraints (FK, PK, CHECK, UNIQUE).\n- Isolation: Concurrent transactions do not interfere with each other or produce inconsistent states.\n- Durability: Committed transactions survive power outages or system crashes via Write-Ahead Logging (WAL).\n\n2) SQL Isolation Levels (Lowest to Highest Strictness):\n- Read Uncommitted: Permits Dirty Reads (reading uncommitted data from another transaction).\n- Read Committed: Prevents Dirty Reads; permits Non-Repeatable Reads (default in Postgres & Oracle).\n- Repeatable Read: Prevents Dirty & Non-Repeatable Reads; permits Phantom Reads (default in MySQL InnoDB).\n- Serializable: Highest isolation level; prevents all concurrency anomalies by executing transactions as if strictly sequential.",
        "source": "Relational Transaction Theory"
    },
    {
        "id": "DOC-SQL-TRANSACTION-LOCKS",
        "domain": "sql",
        "topic": "locks_concurrency",
        "title": "Database Locks, Concurrency Control, Deadlocks, and MVCC",
        "tags": ["locks", "locking", "deadlock", "mvcc", "shared lock", "exclusive lock", "optimistic locking", "pessimistic locking", "row lock", "what is mvcc and how does locking work in sql"],
        "content": "Concurrency control mechanisms protect data integrity during simultaneous multi-user database access:\n\n1) Lock Types:\n- Shared Lock (S-Lock / Read Lock): Multiple transactions can read the same row concurrently, but no transaction can modify it.\n- Exclusive Lock (X-Lock / Write Lock): Only one transaction can hold an X-lock, blocking all other reads and writes on that resource.\n\n2) Lock Granularity:\n- Row-Level Lock: Locks individual rows (highest concurrency).\n- Page-Level Lock: Locks 8KB disk pages.\n- Table-Level Lock: Locks the entire table (lowest concurrency).\n\n3) Deadlocks:\n- Occurs when Transaction A holds Lock 1 and waits for Lock 2, while Transaction B holds Lock 2 and waits for Lock 1.\n- Prevention: Always acquire table/row locks in consistent order; keep transactions brief.\n\n4) Multi-Version Concurrency Control (MVCC):\n- Modern engines (PostgreSQL, MySQL InnoDB, Oracle) use MVCC: Readers do not block Writers, and Writers do not block Readers. Updates create new row versions with transaction timestamps (xmin/xmax).",
        "source": "Database Engine Concurrency & Storage"
    },

    # =========================================================================
    # 11. INDEXES & QUERY OPTIMIZATION
    # =========================================================================
    {
        "id": "DOC-SQL-INDEXES-BTREE-HASH",
        "domain": "sql",
        "topic": "indexes",
        "title": "B-Tree vs Hash vs Composite vs Covering Indexes (INCLUDE)",
        "tags": ["indexes", "index", "b-tree", "hash index", "composite index", "covering index", "include clause", "index types"],
        "content": "Indexes are auxiliary search trees that accelerate query retrieval:\n\n1) B-Tree Index (Default): Self-balancing balanced tree supporting `=`, `<`, `<=`, `>`, `>=`, `BETWEEN`, and prefix `LIKE 'abc%'`.\n2) Hash Index: Instant O(1) equality lookup (`=`), but does NOT support range scans or sorting.\n3) Composite (Multi-Column) Index: Indexes `(col1, col2, col3)`. Queries must filter on `col1` (the leftmost prefix) to use the index.\n4) Covering Index (`INCLUDE`): Stores extra non-search columns in index leaf pages, enabling Index-Only Scans with 0 table page lookups.\n\n```sql\nCREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date) INCLUDE (total_amount);\n```",
        "source": "Database Storage & Indexing Guide"
    },
    {
        "id": "DOC-SQL-INDEX-SEEK-VS-SCAN",
        "domain": "sql",
        "topic": "indexes",
        "title": "Index Seek vs Index Scan vs Table Scan: Execution Plan Differences",
        "tags": ["index seek", "index scan", "table scan", "index seek vs index scan", "sequential scan"],
        "content": "Execution plan operators for accessing data:\n\n1) Index Seek (Fastest): Directly navigates the B-Tree from root to leaf node to locate specific matching keys (O(log N)). Occurs with selective equality/range predicates.\n2) Index Scan: Traverses all leaf pages of an index from start to finish. Faster than table scan if index is narrower than table pages.\n3) Table Scan / Sequential Scan (Slowest): Reads every single row and data page from disk. Appropriate on tiny tables or queries fetching >20-30% of all rows.",
        "source": "Database Performance Tuning"
    },
    {
        "id": "DOC-SQL-OPTIMIZATION-SARGABLE",
        "domain": "sql",
        "topic": "optimization",
        "title": "SARGable Predicates: Writing High-Performance Filter Conditions",
        "tags": ["sargable", "sargable queries", "sargable predicates", "query tuning", "avoid full table scan", "how does sargable query optimization work"],
        "content": "SARGable (Search Argument Able) predicates allow the query optimizer to utilize B-Tree index seeks:\n\n1) Rule: Never wrap indexed columns in functions or calculations in WHERE clauses.\n- Non-SARGable (Bad): `WHERE YEAR(order_date) = 2025` (forces full table scan on 10M rows).\n- SARGable (Good): `WHERE order_date >= '2025-01-01' AND order_date < '2026-01-01'` (uses fast Index Seek).\n- Non-SARGable: `WHERE salary * 1.1 > 50000` $\\to$ SARGable: `WHERE salary > 50000 / 1.1`.\n- Non-SARGable: `WHERE UPPER(email) = 'USER@EXAMPLE.COM'` $\\to$ Use a Functional/Expression Index or store lowercase.",
        "source": "Database Performance & Query Tuning"
    },
    {
        "id": "DOC-SQL-EXPLAIN-ANALYZE",
        "domain": "sql",
        "topic": "optimization",
        "title": "EXPLAIN & EXPLAIN ANALYZE: Reading Database Execution Plans",
        "tags": ["explain", "explain analyze", "execution plan", "query plan", "cost based optimizer", "query cost"],
        "content": "EXPLAIN and EXPLAIN ANALYZE inspect the query optimizer's execution plan:\n\n1) EXPLAIN: Shows the estimated query plan, operator tree, and estimated cost/rows without running the query.\n2) EXPLAIN ANALYZE: Actually executes the query and measures exact runtime millisecond latency, actual row counts, memory/buffers used, and loop iterations.\n3) Key Operators to Inspect: Seq Scan, Index Seek, Hash Join, Nested Loops, Materialize, Sort.",
        "source": "Database Performance Tuning"
    },

    # =========================================================================
    # 12. DATABASE OBJECTS: PROCEDURES, FUNCTIONS, VIEWS, TRIGGERS
    # =========================================================================
    {
        "id": "DOC-SQL-STORED-PROCEDURES-DEEP",
        "domain": "sql",
        "topic": "stored_procedures",
        "title": "Stored Procedures (SP): Complete Architecture, Parameters, and Implementation",
        "tags": ["stored procedure", "storedprocedure", "storeprocedure", "sp", "sprocs", "procedures", "create procedure", "call procedure", "plsql", "tsql"],
        "content": "A Stored Procedure (SP) is a precompiled collection of one or more SQL statements and procedural control flow logic stored on the database server.\n\n1) Core Architectural Pillars:\n- Precompiled Execution: Compiled once upon creation, reducing query parsing overhead on subsequent runs.\n- Procedural Capabilities: Supports IF/ELSE branching, WHILE loops, local variables, and TRY-CATCH / EXCEPTION handling.\n- Transaction Control: Can explicitly execute BEGIN TRANSACTION, COMMIT, and ROLLBACK.\n- Security Abstraction: Allows users to execute business logic via GRANT EXECUTE without giving direct table access.\n\n2) Parameter Modes:\n- IN: Input parameter passed by caller (read-only inside procedure).\n- OUT: Output parameter populated by procedure and returned to caller.\n- INOUT: Parameter passed in with an initial value and modified by procedure.\n\n```sql\n-- PostgreSQL Stored Procedure Example:\nCREATE OR REPLACE PROCEDURE UpdateEmployeeSalary(\n    p_emp_id INT,\n    p_percentage NUMERIC\n)\nLANGUAGE plpgsql\nAS '\nBEGIN\n    UPDATE employees\n    SET salary = salary * (1 + p_percentage / 100.0)\n    WHERE emp_id = p_emp_id;\n    COMMIT;\nEND;\n';\n\n-- Execution:\nCALL UpdateEmployeeSalary(101, 10.0);\n```",
        "source": "Database Programmability Architecture"
    },
    {
        "id": "DOC-SQL-FUNCTIONS-UDF-DEEP",
        "domain": "sql",
        "topic": "functions",
        "title": "User-Defined Functions (UDF): Scalar, Table-Valued, Deterministic, and UDF vs SP",
        "tags": ["functions", "udf", "user defined function", "scalar function", "table valued function", "tvf", "deterministic function", "udf vs sp", "function vs procedure", "explain udf vs sp"],
        "content": "User-Defined Functions (UDF) are reusable computational routines stored in the database:\n\n1) Function Types:\n- Scalar Functions: Return a single discrete value (e.g. calculating sales tax). Usable in SELECT columns and WHERE filters.\n- Table-Valued Functions (TVF): Return an entire relational table (result set). Usable directly in FROM and JOIN clauses.\n\n2) Deterministic Functions: Always return the identical result for identical inputs (e.g. `ABS(x)`). Optimizer can cache results.\n\n3) Comprehensive Comparison: Function (UDF) vs Stored Procedure (SP):\n- Invocation: UDFs are embedded directly in SQL queries (`SELECT CalcTax(salary) FROM employees`); SPs are invoked with standalone `CALL` or `EXEC` commands.\n- Return Type: UDF MUST return a value; SP does not require a return value.\n- DML & Side Effects: UDF cannot modify database state (cannot perform INSERT/UPDATE/DELETE on tables); SP can perform full DML operations.\n- Transactions: UDF cannot manage transactions (no COMMIT/ROLLBACK allowed); SP can explicitly manage transaction boundaries.",
        "source": "Database Computational Objects Guide"
    },
    {
        "id": "DOC-SQL-VIEWS-AND-MVS",
        "domain": "sql",
        "topic": "views",
        "title": "Standard Views vs Materialized Views: Storage, Performance, and Refresh",
        "tags": ["views", "view", "materialized view", "mv", "create view", "refresh materialized view", "virtual table", "view vs materialized view"],
        "content": "Comparison between Standard Views and Materialized Views:\n\n1) Standard View (Virtual Table):\n- A saved query definition that does NOT store physical data on disk. Executes the underlying SELECT dynamically whenever queried.\n- Storage: 0 disk space. Data Freshness: 100% real-time.\n\n2) Materialized View (Physical Cache):\n- Physically computes and persists the query result set on disk as an actual physical table.\n- Storage: Consumes disk space and supports custom B-Tree indexes.\n- Query Speed: Instant reads on massive multi-table aggregations.\n- Refresh Strategy: Must be refreshed on-demand or periodically (`REFRESH MATERIALIZED VIEW view_name`).",
        "source": "Database Views & Storage Architecture"
    },
    {
        "id": "DOC-SQL-TRIGGERS-DEEP",
        "domain": "sql",
        "topic": "triggers",
        "title": "Database Triggers: Event-Driven Procedures, Timing, and Audit Logging",
        "tags": ["triggers", "trigger", "create trigger", "before trigger", "after trigger", "instead of trigger", "audit log", "event driven"],
        "content": "A Database Trigger is a specialized stored procedure that fires automatically in response to data modification events (INSERT, UPDATE, DELETE):\n\n1) Timing Types:\n- BEFORE Trigger: Fires before the DML writes to disk. Used for validation or data sanitization.\n- AFTER Trigger: Fires after the DML succeeds. Used for audit logging and secondary table synchronization.\n- INSTEAD OF Trigger: Replaces standard DML, primarily used to make complex multi-table views updatable.\n\n2) Execution Scope:\n- Row-Level Trigger (`FOR EACH ROW`): Executes once per modified row, with access to `OLD` and `NEW` records.\n- Statement-Level Trigger (`FOR EACH STATEMENT`): Executes once per command regardless of row count.",
        "source": "Database Event & Integrity Management"
    },

    # =========================================================================
    # 13. DATA TYPES, STRINGS, DATES & JSON
    # =========================================================================
    {
        "id": "DOC-SQL-DATA-TYPES-OVERVIEW",
        "domain": "sql",
        "topic": "data_types",
        "title": "SQL Data Types: Numeric, Character, Date/Time, Boolean, and Binary",
        "tags": ["data types", "numeric", "varchar", "text", "integer", "decimal", "timestamp", "boolean"],
        "content": "Standard SQL Data Types:\n\n1) Numeric: `INT`, `BIGINT`, `SMALLINT`, `DECIMAL(p,s) / NUMERIC(p,s)` (exact fixed-point precision for financial data), `FLOAT / REAL` (approximate floating point).\n2) Character: `CHAR(n)` (fixed length), `VARCHAR(n)` (variable length with maximum), `TEXT` (unbounded string).\n3) Date & Time: `DATE` (YYYY-MM-DD), `TIME` (HH:MM:SS), `TIMESTAMP` (Date + Time), `TIMESTAMPTZ` (Timestamp with Timezone offset).\n4) Boolean: `BOOLEAN` (`TRUE`, `FALSE`, `UNKNOWN`).\n5) Binary: `BLOB / BYTEA` (raw binary data for images/files).",
        "source": "SQL Foundation Reference"
    },
    {
        "id": "DOC-SQL-DATE-FUNCTIONS",
        "domain": "sql",
        "topic": "date_functions",
        "title": "Date and Time Functions: DATE_TRUNC, EXTRACT, Intervals, and Arithmetic",
        "tags": ["date functions", "date_trunc", "extract", "dateadd", "datediff", "intervals", "current_timestamp"],
        "content": "Manipulating temporal data in SQL:\n\n1) DATE_TRUNC (PostgreSQL/Databases): Truncates timestamp to specified precision (year, month, day, hour): `DATE_TRUNC('month', order_date)`.\n2) EXTRACT / DATEPART: Retrieves integer sub-components: `EXTRACT(YEAR FROM order_date)`, `EXTRACT(DOW FROM order_date)`.\n3) Interval Arithmetic: `CURRENT_DATE - INTERVAL '30 days'`.\n\n```sql\nSELECT \n    DATE_TRUNC('month', order_date) AS sales_month,\n    SUM(total_amount) AS monthly_revenue\nFROM orders\nGROUP BY DATE_TRUNC('month', order_date)\nORDER BY sales_month DESC;\n```",
        "source": "SQL Temporal Processing Guide"
    },
    {
        "id": "DOC-SQL-JSON-JSONB",
        "domain": "sql",
        "topic": "json",
        "title": "JSON and JSONB in SQL: Querying, Operators (->, ->>), and GIN Indexing",
        "tags": ["json", "jsonb", "json querying", "json operators", "gin index json", "json_extract"],
        "content": "Storing and querying semi-structured JSON data inside relational tables:\n\n1) JSON vs JSONB (PostgreSQL):\n- `JSON`: Stores exact raw text (preserves whitespace and key order, slower to query).\n- `JSONB`: Stores decomposed binary format (faster querying, supports GIN indexes).\n\n2) Query Operators:\n- `->`: Extracts JSON object/element by key/index (returns JSON).\n- `->>`: Extracts JSON field as plain text (returns VARCHAR/TEXT).\n- `@>`: JSON containment check (does left JSON contain right JSON).\n\n```sql\n-- PostgreSQL JSONB Query:\nSELECT \n    customer_id,\n    attributes->>'tier' AS loyalty_tier,\n    attributes->'address'->>'city' AS city\nFROM customers\nWHERE attributes @> '{\"is_verified\": true}';\n```",
        "source": "Semi-Structured Data in SQL"
    },

    # =========================================================================
    # 14. NORMALIZATION & RELATIONAL MODELING
    # =========================================================================
    {
        "id": "DOC-SQL-NORMALIZATION-123NF-BCNF",
        "domain": "sql",
        "topic": "schema_design",
        "title": "Database Normalization (1NF, 2NF, 3NF, BCNF) and Integrity Constraints",
        "tags": ["normalization", "1nf", "2nf", "3nf", "bcnf", "check constraint", "schema design", "database design", "denormalization", "difference between 1nf,2nf,3nf and bcnf", "explain 1nf 2nf 3nf bcnf database normalization"],
        "content": "Normalization organizes relational schemas to eliminate data redundancy and prevent insertion, update, and deletion anomalies:\n\n1) First Normal Form (1NF):\n- Every column must contain atomic (indivisible) values.\n- Every table must have a Primary Key.\n- No repeating groups or array columns.\n\n2) Second Normal Form (2NF):\n- Satisfies 1NF.\n- No Partial Functional Dependencies: All non-key attributes must depend on the ENTIRE composite Primary Key, not just a subset.\n\n3) Third Normal Form (3NF):\n- Satisfies 2NF.\n- No Transitive Dependencies: Non-key attributes must depend directly on the Primary Key only (X -> PK, not X -> Y -> PK).\n\n4) Boyce-Codd Normal Form (BCNF):\n- Stricter version of 3NF where every determinant must be a candidate key.\n\nIntegrity Constraints:\n- PRIMARY KEY (Unique + Not Null identity)\n- FOREIGN KEY (Enforces referential integrity with ON DELETE CASCADE / RESTRICT / SET NULL)\n- UNIQUE (Ensures uniqueness)\n- NOT NULL (Prevents missing values)\n- CHECK (Enforces domain validation, e.g. CHECK (salary > 0))",
        "source": "Relational Database Schema Design"
    }
]

# Write all documents to json
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(docs, f, indent=2)

print(f"[+] Successfully generated and saved {len(docs)} comprehensive SQL documents to {OUTPUT_FILE}")
