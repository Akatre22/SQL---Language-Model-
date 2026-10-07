"""
Comprehensive PDF 2 Processor & Dataset Generator
Source: data/365 Data Science_SQL BASICS_sm.pdf

Extracts structured SQL Q&A, syntax patterns, conceptual knowledge, and practical exercises
covering:
1. SQL Theory: DDL, DML, DCL, TCL, Keywords, Syntax Standards
2. SELECT Fundamentals: Column Projection, Table Selection
3. WHERE Clause Filtering: Single/Multiple conditions
4. Logical Operators & Operator Precedence: AND, OR, Parentheses Evaluation Order
5. Pattern Matching: Wildcard Characters (% and _) with LIKE and NOT LIKE
6. Range & Null Operators: BETWEEN ... AND ..., IS NULL, IS NOT NULL
7. Comparison Operators: =, !=, <>, >, <, >=, <=
8. Deduplication: SELECT DISTINCT (Single & Multi-Column)
9. Aggregate Functions: COUNT(*), COUNT(col), COUNT(DISTINCT col), SUM, AVG, MIN, MAX
10. Grouping & Aggregate Filtering: GROUP BY, HAVING, WHERE vs HAVING Deep Dive
11. Sorting & Pagination: ORDER BY (ASC/DESC, multi-column), LIMIT
12. Data Insertion: Single Row, Multi-Row Batch, INSERT INTO ... SELECT
13. Data Modification: UPDATE Statement, Multi-Column Updates, Safe Updating Practices
14. Data Removal & Architectural Comparisons: DELETE Statement, DROP vs TRUNCATE vs DELETE
15. Transaction Control: COMMIT, ROLLBACK in Practice
"""

import json
import random
from pathlib import Path
from typing import List, Dict

SEED = 42
random.seed(SEED)

PDF_NAME = "365 Data Science_SQL BASICS_sm.pdf"

def generate_pdf_2_samples() -> List[Dict[str, str]]:
    samples = []

    def add_sample(instruction: str, response: str, task: str):
        samples.append({
            "instruction": instruction.strip(),
            "response": response.strip(),
            "output": response.strip(),
            "domain": "sql",
            "task": task,
            "source": PDF_NAME
        })

    # ==========================================
    # 1. SQL THEORY & CLASSIFICATIONS
    # ==========================================
    add_sample(
        "Explain the four major subsets of SQL statements (DDL, DML, DCL, TCL) and their specific purposes.",
        "SQL statements are categorized into four major functional subsets:\n\n1. **Data Definition Language (DDL)**:\n   - **Purpose**: Defines, modifies, and deletes database objects (tables, views, indexes, schemas).\n   - **Key Statements**: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`.\n   - **Nature**: Auto-committed; changes are applied immediately to the database catalog.\n\n2. **Data Manipulation Language (DML)**:\n   - **Purpose**: Manages and queries data records within tables.\n   - **Key Statements**: `SELECT` (often categorized as DQL), `INSERT`, `UPDATE`, `DELETE`.\n   - **Nature**: Can be transactional and rolled back unless auto-commit is enabled.\n\n3. **Data Control Language (DCL)**:\n   - **Purpose**: Manages access permissions, user roles, and security privileges.\n   - **Key Statements**: `GRANT` (bestow privileges), `REVOKE` (remove privileges).\n\n4. **Transaction Control Language (TCL)**:\n   - **Purpose**: Manages the state and boundary of transactions executed by DML commands.\n   - **Key Statements**: `COMMIT` (make permanent), `ROLLBACK` (revert changes), `SAVEPOINT` (intermediate checkpoint).",
        "sql_concept"
    )

    add_sample(
        "What are SQL keywords, identifiers, and syntax conventions?",
        "In SQL:\n- **Keywords / Reserved Words**: Predefined terms that have special semantic meaning to the SQL parser (e.g., `SELECT`, `FROM`, `WHERE`, `JOIN`, `GROUP BY`, `ORDER BY`). Keywords cannot be used as table or column names without quotation/escaping.\n- **Identifiers**: Names assigned by users to database objects such as tables (`employees`, `orders`), columns (`first_name`, `salary`), and aliases.\n- **Syntax Conventions**: SQL is case-insensitive regarding keywords, but standard best practice is to write SQL keywords in UPPERCASE and table/column names in lowercase snake_case for readability.",
        "sql_concept"
    )

    # ==========================================
    # 2. SELECT & WHERE FILTERING
    # ==========================================
    add_sample(
        "Write a SQL query to retrieve first_name, last_name, and hire_date from the employees table.",
        "```sql\nSELECT first_name, last_name, hire_date\nFROM employees;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query to select all female employees with the first name 'Denis' from the employees table.",
        "```sql\nSELECT *\nFROM employees\nWHERE first_name = 'Denis' \n  AND gender = 'F';\n```",
        "text_to_sql"
    )

    # ==========================================
    # 3. OPERATOR PRECEDENCE: AND vs OR
    # ==========================================
    add_sample(
        "Explain operator precedence between AND and OR in SQL and why parentheses are critical.",
        "In SQL logical operations:\n- **Precedence**: `AND` has higher operator precedence than `OR`. The SQL engine evaluates all `AND` conditions first before evaluating `OR` conditions.\n- **The Pitfall**: Writing `WHERE gender = 'F' AND first_name = 'Denis' OR first_name = 'Elvis'` is evaluated by SQL as `(gender = 'F' AND first_name = 'Denis') OR (first_name = 'Elvis')`. This returns all female Denis employees PLUS ALL Elvis employees (both male and female).\n- **Solution**: Use parentheses `()` to explicitly enforce desired grouping: `WHERE gender = 'F' AND (first_name = 'Denis' OR first_name = 'Elvis')`.",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query to select all female employees whose first name is either 'Kellie' or 'Aruna'.",
        "```sql\nSELECT *\nFROM employees\nWHERE gender = 'F' \n  AND (first_name = 'Kellie' OR first_name = 'Aruna');\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query using the IN operator to find all employees whose first name is 'Denis', 'Elvis', or 'Kellie'.",
        "```sql\nSELECT *\nFROM employees\nWHERE first_name IN ('Denis', 'Elvis', 'Kellie');\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query using NOT IN to find all employees whose first name is NOT 'John', 'Mark', or 'Jacob'.",
        "```sql\nSELECT *\nFROM employees\nWHERE first_name NOT IN ('John', 'Mark', 'Jacob');\n```",
        "text_to_sql"
    )

    # ==========================================
    # 4. WILDCARDS & PATTERN MATCHING (LIKE)
    # ==========================================
    add_sample(
        "Explain SQL wildcard characters used with the LIKE operator.",
        "The SQL `LIKE` operator enables pattern matching on text strings using two standard wildcard characters:\n\n1. **Percent Sign (`%`)**: Represents zero, one, or multiple characters.\n   - `'Mar%'`: Matches any string starting with 'Mar' (e.g., 'Mark', 'Mary', 'Martin').\n   - `'%son'`: Matches any string ending with 'son' (e.g., 'Johnson', 'Wilson').\n   - `'%jack%'`: Matches any string containing 'jack' anywhere.\n\n2. **Underscore (`_`)**: Represents exactly one single character.\n   - `'Mar_'`: Matches 4-letter strings starting with 'Mar' (e.g., 'Mark', 'Mary', but not 'Martin').\n   - `'__hn'`: Matches 4-letter strings ending in 'hn' (e.g., 'John').",
        "sql_concept"
    )

    add_sample(
        "Write SQL queries to find employees whose first name starts with 'Mar', ends with 'an', and exactly 4 characters long starting with 'Mar'.",
        "```sql\n-- Starts with 'Mar'\nSELECT * FROM employees WHERE first_name LIKE ('Mar%');\n\n-- Ends with 'an'\nSELECT * FROM employees WHERE first_name LIKE ('%an');\n\n-- Exactly 4 characters long starting with 'Mar'\nSELECT * FROM employees WHERE first_name LIKE ('Mar_');\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query to find all employees who were hired in the year 2000 using the LIKE operator.",
        "```sql\nSELECT *\nFROM employees\nWHERE hire_date LIKE ('2000%');\n```",
        "text_to_sql"
    )

    # ==========================================
    # 5. BETWEEN ... AND ...
    # ==========================================
    add_sample(
        "Explain the BETWEEN ... AND ... operator in SQL and how it handles range boundaries.",
        "The `BETWEEN ... AND ...` operator selects values within a specified range:\n- **Inclusivity**: `BETWEEN` is **inclusive** on both ends. `WHERE salary BETWEEN 50000 AND 70000` includes rows where salary is exactly 50000 and 70000.\n- **Data Types**: Works with numeric values, dates (`WHERE hire_date BETWEEN '1990-01-01' AND '2000-01-01'`), and alphabetical strings.\n- **Negation**: `NOT BETWEEN ... AND ...` selects values strictly outside the specified range.",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query to select all employees hired between January 1, 1990, and January 1, 2000, inclusive.",
        "```sql\nSELECT *\nFROM employees\nWHERE hire_date BETWEEN '1990-01-01' AND '2000-01-01';\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query to select all contracts from salaries where salary is NOT between $66,000 and $70,000.",
        "```sql\nSELECT *\nFROM salaries\nWHERE salary NOT BETWEEN 66000 AND 70000;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 6. NULL HANDLING (IS NULL / IS NOT NULL)
    # ==========================================
    add_sample(
        "Explain NULL in SQL and why comparison operators like = NULL fail.",
        "In SQL, `NULL` represents a missing, unknown, or non-applicable value. It is not equal to zero `0` or an empty string `''`.\n\n- **Three-Valued Logic**: Any direct comparison with `NULL` using standard comparison operators (e.g., `WHERE column = NULL` or `WHERE column != NULL`) evaluates to `UNKNOWN` (treated as `FALSE`), returning zero rows.\n- **Correct Syntax**: Always use the specialized operators `IS NULL` and `IS NOT NULL`:\n  - `WHERE first_name IS NULL;` (identifies rows with missing values)\n  - `WHERE first_name IS NOT NULL;` (identifies rows with populated values)",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query to select all departments from departments where dept_no is NOT NULL.",
        "```sql\nSELECT *\nFROM departments\nWHERE dept_no IS NOT NULL;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 7. COMPARISON OPERATORS & SELECT DISTINCT
    # ==========================================
    add_sample(
        "Write SQL queries demonstrating comparison operators: equal (=), not equal (!= or <>), greater than (>), and less than or equal (<=).",
        "```sql\n-- Equal\nSELECT * FROM employees WHERE gender = 'F';\n\n-- Not Equal\nSELECT * FROM employees WHERE first_name != 'Mark';\nSELECT * FROM employees WHERE first_name <> 'Mark';\n\n-- Greater Than\nSELECT * FROM salaries WHERE salary > 100000;\n\n-- Less than or equal\nSELECT * FROM employees WHERE hire_date <= '1985-02-01';\n```",
        "text_to_sql"
    )

    add_sample(
        "What is SELECT DISTINCT in SQL and how does it handle multiple columns?",
        "`SELECT DISTINCT` removes duplicate rows from the output result set.\n- **Single Column**: `SELECT DISTINCT gender FROM employees;` returns each unique gender value once (`M`, `F`).\n- **Multiple Columns**: `SELECT DISTINCT first_name, last_name FROM employees;` evaluates uniqueness across the **combination of all selected columns**. A row is only eliminated if both `first_name` AND `last_name` are identical to another row.",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query to retrieve all distinct hire dates from the employees table.",
        "```sql\nSELECT DISTINCT hire_date\nFROM employees;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 8. AGGREGATE FUNCTIONS & COUNT MECHANICS
    # ==========================================
    add_sample(
        "Explain the differences among COUNT(*), COUNT(column_name), and COUNT(DISTINCT column_name).",
        "1. **`COUNT(*)`**: Counts the total number of rows in the table matching the filter, including rows containing `NULL` values and duplicate entries.\n2. **`COUNT(column_name)`**: Counts the number of non-`NULL` values in that specific column (ignores `NULL`s).\n3. **`COUNT(DISTINCT column_name)`**: Counts the number of unique, non-`NULL` values in that specific column.",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query to count the total number of employees, the number of distinct first names, and the number of distinct annual salaries exceeding $100,000.",
        "```sql\n-- Total employees\nSELECT COUNT(*) FROM employees;\n\n-- Distinct first names\nSELECT COUNT(DISTINCT first_name) FROM employees;\n\n-- Distinct salaries > 100,000\nSELECT COUNT(DISTINCT salary) \nFROM salaries \nWHERE salary > 100000;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write SQL queries calculating the sum, average, minimum, and maximum salary from the salaries table.",
        "```sql\nSELECT \n    SUM(salary) AS total_payroll,\n    AVG(salary) AS average_salary,\n    MIN(salary) AS minimum_salary,\n    MAX(salary) AS maximum_salary\nFROM salaries;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 9. GROUP BY & HAVING (WHERE vs HAVING)
    # ==========================================
    add_sample(
        "Provide a deep architectural comparison between WHERE and HAVING clauses in SQL.",
        "| Feature | `WHERE` Clause | `HAVING` Clause |\n| :--- | :--- | :--- |\n| **Evaluation Timing** | Filter rows **before** aggregation / grouping | Filters groups **after** aggregation (`GROUP BY`) |\n| **Aggregate Functions** | **Cannot** use aggregate functions (`SUM`, `AVG`, `COUNT`) | **Can** filter on aggregate expressions (`HAVING COUNT(*) > 5`) |\n| **Scope** | Applied to individual table rows | Applied to grouped summary rows |\n| **Association** | Used with `SELECT`, `UPDATE`, `DELETE` | Used primarily with `SELECT ... GROUP BY` |\n\n**Best Practice Rule**: Use `WHERE` to filter individual records before grouping to reduce computational overhead, and use `HAVING` only to filter aggregated results.",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query to list all first names in the employees table that appear more than 250 times, along with their occurrence count, ordered by occurrence descending.",
        "```sql\nSELECT first_name, COUNT(first_name) AS names_count\nFROM employees\nGROUP BY first_name\nHAVING COUNT(first_name) > 250\nORDER BY names_count DESC;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query to select all employee numbers who have signed more than 1 contract after January 1, 2000, from the salaries table.",
        "```sql\nSELECT emp_no, COUNT(from_date) AS contract_count\nFROM salaries\nWHERE from_date > '2000-01-01'\nGROUP BY emp_no\nHAVING COUNT(from_date) > 1\nORDER BY emp_no ASC;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 10. ORDER BY & LIMIT
    # ==========================================
    add_sample(
        "Explain ORDER BY clause mechanics, sorting options, and LIMIT usage in SQL.",
        "1. **`ORDER BY`** sorts query output by one or multiple columns:\n   - `ASC` (default): Ascending order (lowest to highest, A-Z).\n   - `DESC`: Descending order (highest to lowest, Z-A).\n   - **Multi-column**: `ORDER BY first_name ASC, last_name DESC` sorts primarily by `first_name`, and ties are broken by `last_name`.\n2. **`LIMIT`** restricts the number of rows returned in the output:\n   - `LIMIT n`: Returns the first `n` rows.\n   - `LIMIT offset, count`: Returns `count` rows starting after `offset` rows (used for pagination).",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query to select the top 10 highest paid employee contracts from the salaries table.",
        "```sql\nSELECT emp_no, salary, from_date, to_date\nFROM salaries\nORDER BY salary DESC\nLIMIT 10;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 11. SQL INSERT STATEMENT
    # ==========================================
    add_sample(
        "Explain single-row and multi-row INSERT syntax in SQL with examples.",
        "1. **Single-Row INSERT**:\n```sql\nINSERT INTO employees (\n    emp_no, birth_date, first_name, last_name, gender, hire_date\n) VALUES (\n    999901, '1986-04-21', 'John', 'Smith', 'M', '2011-01-01'\n);\n```\n\n2. **Multi-Row Batch INSERT** (Significantly faster than multiple single-row inserts):\n```sql\nINSERT INTO departments (dept_no, dept_name)\nVALUES \n    ('d010', 'Business Analysis'),\n    ('d011', 'Data Architecture'),\n    ('d012', 'AI & Machine Learning');\n```",
        "sql_concept"
    )

    add_sample(
        "Write a SQL statement to insert data into a new table departments_dup from the departments table using INSERT INTO ... SELECT.",
        "```sql\nINSERT INTO departments_dup (dept_no, dept_name)\nSELECT dept_no, dept_name\nFROM departments;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 12. SQL UPDATE STATEMENT & TCL SAFETY
    # ==========================================
    add_sample(
        "Write a SQL UPDATE query to modify the department name of department 'd010' to 'Data Engineering' in the departments table.",
        "```sql\nUPDATE departments\nSET dept_name = 'Data Engineering'\nWHERE dept_no = 'd010';\n```",
        "text_to_sql"
    )

    add_sample(
        "Explain safe UPDATE practices in SQL and how TCL COMMIT and ROLLBACK prevent catastrophic data loss.",
        "**The Danger**: If you execute `UPDATE employees SET first_name = 'John';` without a `WHERE` clause, SQL will overwrite EVERY employee's name in the entire database.\n\n**Safe Execution Pattern**:\n1. Disable auto-commit or start a transaction: `SET autocommit = 0;` (or `START TRANSACTION;`).\n2. Execute the UPDATE statement with a strict `WHERE` filter.\n3. Run a `SELECT` verification query to inspect the modified rows.\n4. If results are correct, execute `COMMIT;` to permanently persist changes.\n5. If an error occurred or too many rows were modified, execute `ROLLBACK;` to instantly restore prior table state.",
        "sql_concept"
    )

    add_sample(
        "Provide an example demonstrating safe transaction rollback after an accidental update.",
        "```sql\n-- 1. Begin transaction\nSTART TRANSACTION;\n\n-- 2. Execute update\nUPDATE departments_dup\nSET dept_name = 'Quality Assurance'\nWHERE dept_no = 'd001';\n\n-- 3. Verify\nSELECT * FROM departments_dup WHERE dept_no = 'd001';\n\n-- 4. Revert changes if mistaken\nROLLBACK;\n\n-- 5. Confirm original state restored\nSELECT * FROM departments_dup WHERE dept_no = 'd001';\n```",
        "sql_explanation"
    )

    # ==========================================
    # 13. SQL DELETE STATEMENT & DROP vs TRUNCATE vs DELETE
    # ==========================================
    add_sample(
        "Write a SQL query to delete employee with emp_no = 999901 from the employees table.",
        "```sql\nDELETE FROM employees\nWHERE emp_no = 999901;\n```",
        "text_to_sql"
    )

    add_sample(
        "Explain the deep architectural differences between DROP TABLE, TRUNCATE TABLE, and DELETE FROM table.",
        "| Aspect | `DROP TABLE` | `TRUNCATE TABLE` | `DELETE FROM` |\n| :--- | :--- | :--- | :--- |\n| **SQL Category** | DDL | DDL | DML |\n| **What is Removed** | Table records **AND** table schema definition | All table records (retains schema) | Filtered or all table records (retains schema) |\n| **WHERE Clause** | No | No | **Yes** (supports conditional filtering) |\n| **Auto-Increment Counter** | Destroyed | **Reset** to initial seed (1) | **Not reset** (continues from max) |\n| **Transaction Logging** | DDL catalog update | Deallocates data pages (minimal logging) | Logs individual row deletions (heavy logging) |\n| **Rollback Capability** | Non-rollbackable in standard SQL | Cannot be rolled back in most RDBMS | **Fully rollbackable** with TCL `ROLLBACK` |\n| **Speed & Performance** | Instant | Extremely fast on large tables | Slow on large tables due to row-by-row logging |",
        "sql_concept"
    )

    return samples

if __name__ == "__main__":
    pdf_samples = generate_pdf_2_samples()
    print(f"Generated {len(pdf_samples)} high-fidelity instruction-tuning samples from PDF 2.")
    
    # Save standalone PDF 2 dataset
    pdf2_jsonl = Path("data/pdf_2_dataset.jsonl")
    with open(pdf2_jsonl, "w", encoding="utf-8") as f:
        for s in pdf_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"Saved PDF 2 samples to {pdf2_jsonl}")
