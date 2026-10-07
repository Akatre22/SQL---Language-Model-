"""
Comprehensive PDF 1 Processor & Dataset Generator
Source: data/202003291621085101sanjeev_rdbms_unit-I_sql_bba_ms_4_sem.pdf

Extracts structured SQL Q&A, syntax patterns, conceptual knowledge, and exercises
covering:
1. SQL Fundamentals & RDBMS Principles
2. SQL Processing Architecture & Components
3. 5 SQL Command Classifications (DDL, DML, DCL, TCL, DQL)
4. Full DDL suite: CREATE TABLE, ALTER (ADD/MODIFY), DROP TABLE, TRUNCATE TABLE
5. Full DML suite: INSERT INTO, UPDATE WHERE, DELETE WHERE
6. Full DCL suite: GRANT, REVOKE
7. Full TCL suite: COMMIT, ROLLBACK, SAVEPOINT
8. Full DQL suite: SELECT, WHERE, Projection, Predicates
9. SQL Operators: Arithmetic (+, -, *, /, %), Comparison (=, !=, <>, >, <, >=, <=, !<, !>), Logical (AND, OR, NOT, IN, BETWEEN, LIKE, ALL, ANY, EXISTS)
10. SQL Views: Virtual tables, CREATE VIEW single table, CREATE VIEW multiple tables, DROP VIEW
11. SQL Indexes: CREATE INDEX, CREATE UNIQUE INDEX, DROP INDEX, performance mechanics
12. SQL Subqueries: SELECT subqueries, INSERT subqueries, UPDATE subqueries, DELETE subqueries
13. SQL Clauses: GROUP BY, HAVING, ORDER BY (ASC/DESC)
14. SQL Aggregate Functions: COUNT(*), COUNT(DISTINCT), SUM(), AVG(), MAX(), MIN()
15. SQL Joins: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN
16. SQL Set Operations: UNION, INTERSECT, MINUS
"""

import json
import random
from pathlib import Path
from typing import List, Dict

SEED = 42
random.seed(SEED)

PDF_NAME = "202003291621085101sanjeev_rdbms_unit-I_sql_bba_ms_4_sem.pdf"

def generate_pdf_1_samples() -> List[Dict[str, str]]:
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
    # 1. SQL DEFINITIONS & FOUNDATIONS
    # ==========================================
    add_sample(
        "What is SQL and what is its primary purpose in relational database systems?",
        "SQL stands for Structured Query Language. It is the standard language for Relational Database Management Systems (RDBMS) such as MySQL, Oracle, PostgreSQL, SQL Server, and MS Access.\n\nSQL enables users to:\n1. Create and modify relational database structures and tables.\n2. Query, read, and extract data using English-like statements.\n3. Insert, update, and delete table records.\n4. Control user access permissions and manage transactional integrity.\n\nSQL operates based on relational algebra and tuple relational calculus.",
        "sql_concept"
    )

    add_sample(
        "What core rules govern the syntax and execution of SQL statements?",
        "Core SQL syntax rules include:\n1. **Case Insensitivity**: SQL keywords are not case-sensitive, though writing keywords (e.g., `SELECT`, `FROM`, `WHERE`) in uppercase is standard practice for readability.\n2. **Line Independence**: SQL statements can span single or multiple lines freely.\n3. **Clause Ordering**: Clauses must follow a predefined logical hierarchy (e.g., `SELECT` -> `FROM` -> `WHERE` -> `GROUP BY` -> `HAVING` -> `ORDER BY`).\n4. **Theoretical Basis**: SQL queries are mapped mathematically to relational algebra and tuple relational calculus operations.",
        "sql_concept"
    )

    add_sample(
        "Explain the internal SQL query processing workflow and engine components.",
        "When an SQL command executes within an RDBMS, the system determines the optimal execution plan through several key components:\n1. **Query Engine & Parser**: Interprets, validates, and parses the SQL syntax.\n2. **Optimization Engine (Query Optimizer)**: Evaluates multiple execution paths and selects the lowest-cost strategy based on table statistics and indexes.\n3. **Query Dispatcher**: Directs execution requests to the underlying storage and execution subsystems.\n4. **Classic Engine**: Manages non-SQL / legacy logical file operations while the SQL engine handles relational queries.",
        "sql_concept"
    )

    add_sample(
        "What are the major advantages of using SQL?",
        "The primary advantages of SQL include:\n1. **High Speed**: Optimized relational query engines retrieve large datasets rapidly.\n2. **Declarative (No Low-Level Coding)**: Users specify *what* data to retrieve rather than *how* to iterate through files.\n3. **Standardized & Portable**: ANSI/ISO standards allow queries to be ported across multiple RDBMS engines (Oracle, MySQL, SQL Server, PostgreSQL).\n4. **Interactive & Programmatic**: Usable via interactive shells as well as embedded within application code.\n5. **Multiple Data Views**: Allows creating distinct security and data views tailored to different user roles.",
        "sql_concept"
    )

    add_sample(
        "What is the role of data types in SQL?",
        "An SQL data type defines the category of values a table column can hold. Every column in a relational table requires a designated column name and data type.\n\nCommon SQL data types include:\n- `INT` / `INTEGER`: Whole numeric values.\n- `VARCHAR(n)` / `VARCHAR2(n)`: Variable-length character strings up to length `n`.\n- `CHAR(n)`: Fixed-length character strings.\n- `DATE`: Calendar date values (year, month, day).\n- `FLOAT` / `DECIMAL(p, s)`: Exact or floating-point numerical values.",
        "sql_concept"
    )

    # ==========================================
    # 2. 5 TYPES OF SQL COMMANDS
    # ==========================================
    add_sample(
        "What are the five main classifications of SQL commands? Provide examples for each.",
        "The five main classifications of SQL commands are:\n\n1. **DDL (Data Definition Language)**: Defines and alters database schema and objects.\n   - Commands: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`\n   - Characteristic: Auto-committed (changes are permanent immediately).\n\n2. **DML (Data Manipulation Language)**: Modifies dataset rows/records.\n   - Commands: `INSERT`, `UPDATE`, `DELETE`\n   - Characteristic: Non-autocommitted by default; can be rolled back.\n\n3. **DQL (Data Query Language)**: Fetches and retrieves data.\n   - Command: `SELECT`\n\n4. **DCL (Data Control Language)**: Manages permissions and security privileges.\n   - Commands: `GRANT`, `REVOKE`\n\n5. **TCL (Transaction Control Language)**: Manages transactional states of DML operations.\n   - Commands: `COMMIT`, `ROLLBACK`, `SAVEPOINT`",
        "sql_concept"
    )

    # ==========================================
    # 3. DDL COMMANDS (CREATE, ALTER, DROP, TRUNCATE)
    # ==========================================
    add_sample(
        "Write a SQL query to create a table named EMPLOYEE with columns Name (VARCHAR2 20), Email (VARCHAR2 100), and DOB (DATE).",
        "```sql\nCREATE TABLE EMPLOYEE (\n    Name VARCHAR2(20),\n    Email VARCHAR2(100),\n    DOB DATE\n);\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL statement to create an EMPLOYEE table with EMP_ID (INT, NOT NULL, PRIMARY KEY), EMP_NAME (VARCHAR(25), NOT NULL), PHONE_NO (INT, NOT NULL), and ADDRESS (CHAR(30)).",
        "```sql\nCREATE TABLE EMPLOYEE (\n    EMP_ID INT NOT NULL,\n    EMP_NAME VARCHAR(25) NOT NULL,\n    PHONE_NO INT NOT NULL,\n    ADDRESS CHAR(30),\n    PRIMARY KEY (EMP_ID)\n);\n```",
        "text_to_sql"
    )

    add_sample(
        "Write SQL queries to alter table STU_DETAILS by adding an ADDRESS column (VARCHAR2(20)) and modifying the NAME column to VARCHAR2(20).",
        "```sql\n-- Add new column\nALTER TABLE STU_DETAILS ADD (ADDRESS VARCHAR2(20));\n\n-- Modify existing column\nALTER TABLE STU_DETAILS MODIFY (NAME VARCHAR2(20));\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL statement to permanently drop the EMPLOYEE table.",
        "```sql\nDROP TABLE EMPLOYEE;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL statement to truncate all data from the EMPLOYEE table while keeping the table structure intact.",
        "```sql\nTRUNCATE TABLE EMPLOYEE;\n```",
        "text_to_sql"
    )

    add_sample(
        "What is the difference between DROP and TRUNCATE in SQL?",
        "Key differences between `DROP` and `TRUNCATE`:\n- **`DROP TABLE`**: Removes both the table's records AND the table structure itself from the database catalog. Once dropped, the table no longer exists.\n- **`TRUNCATE TABLE`**: Deletes all records from the table and deallocates storage space, but preserves the table structure, columns, constraints, and indexes for future insertions.\n- Both `DROP` and `TRUNCATE` are DDL commands and are auto-committed in standard SQL.",
        "sql_concept"
    )

    # ==========================================
    # 4. DML COMMANDS (INSERT, UPDATE, DELETE)
    # ==========================================
    add_sample(
        "Write a SQL query to insert a record into table XYZ with Author 'Sonoo' and Subject 'DBMS'.",
        "```sql\nINSERT INTO XYZ (Author, Subject) \nVALUES ('Sonoo', 'DBMS');\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query to update the User_Name of student with Student_Id = '3' to 'Sonoo' in the students table.",
        "```sql\nUPDATE students\nSET User_Name = 'Sonoo'\nWHERE Student_Id = '3';\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query to delete all records from CUSTOMERS where AGE is 25.",
        "```sql\nDELETE FROM CUSTOMERS\nWHERE AGE = 25;\n```",
        "text_to_sql"
    )

    add_sample(
        "Explain the difference between DELETE and TRUNCATE in SQL.",
        "Key differences between `DELETE` and `TRUNCATE`:\n1. **Command Type**: `DELETE` is a DML (Data Manipulation Language) command, whereas `TRUNCATE` is a DDL (Data Definition Language) command.\n2. **Filtering**: `DELETE` supports a `WHERE` clause to filter specific rows; `TRUNCATE` removes all rows indiscriminately.\n3. **Transaction Logging & Rollback**: `DELETE` logs individual row deletions and can be rolled back in a transaction; `TRUNCATE` is minimally logged / auto-committed and cannot be rolled back in many databases.\n4. **Performance**: `TRUNCATE` is significantly faster than `DELETE` for wiping large tables because it deallocates data pages directly.",
        "sql_concept"
    )

    # ==========================================
    # 5. DCL COMMANDS (GRANT, REVOKE)
    # ==========================================
    add_sample(
        "Write a SQL statement to grant SELECT and UPDATE permissions on MY_TABLE to users USER1 and USER2.",
        "```sql\nGRANT SELECT, UPDATE ON MY_TABLE TO USER1, USER2;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL statement to revoke SELECT and UPDATE permissions on MY_TABLE from USER1 and USER2.",
        "```sql\nREVOKE SELECT, UPDATE ON MY_TABLE FROM USER1, USER2;\n```",
        "text_to_sql"
    )

    add_sample(
        "Explain what DCL is and how GRANT and REVOKE work.",
        "DCL (Data Control Language) manages security privileges and access rights across database objects.\n- **`GRANT`**: Allocates specific permissions (such as `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `EXECUTE`) on a table, view, or schema to specified database users or roles.\n- **`REVOKE`**: Withdraws previously granted permissions from database users or roles, restricting unauthorized operations.",
        "sql_concept"
    )

    # ==========================================
    # 6. TCL COMMANDS (COMMIT, ROLLBACK, SAVEPOINT)
    # ==========================================
    add_sample(
        "Explain how COMMIT, ROLLBACK, and SAVEPOINT function in SQL transactions.",
        "TCL (Transaction Control Language) manages transactional units of work for DML statements (`INSERT`, `UPDATE`, `DELETE`):\n1. **`COMMIT`**: Permanently applies and saves all modifications made during the current transaction to the database.\n2. **`ROLLBACK`**: Reverts all changes made during the current uncommitted transaction, restoring the database to its prior consistent state.\n3. **`SAVEPOINT`**: Sets intermediate checkpoints within a transaction. This allows rolling back partially to a designated savepoint (`ROLLBACK TO savepoint_name;`) without aborting the entire transaction.",
        "sql_concept"
    )

    add_sample(
        "Provide an example demonstrating the use of SAVEPOINT and ROLLBACK in an SQL transaction.",
        "```sql\n-- Begin transactional operations\nINSERT INTO CUSTOMERS (ID, NAME, AGE) VALUES (101, 'Alice', 30);\nSAVEPOINT sp1;\n\nUPDATE CUSTOMERS SET AGE = 31 WHERE ID = 101;\nSAVEPOINT sp2;\n\nDELETE FROM CUSTOMERS WHERE AGE = 25;\n\n-- Roll back only to checkpoint sp2 (retaining Alice's insertion & update)\nROLLBACK TO sp2;\n\n-- Commit the remaining valid transaction state\nCOMMIT;\n```",
        "sql_explanation"
    )

    # ==========================================
    # 7. DQL & OPERATORS
    # ==========================================
    add_sample(
        "Write a SQL query to select employee names from the employee table where age is greater than 20.",
        "```sql\nSELECT emp_name \nFROM employee \nWHERE age > 20;\n```",
        "text_to_sql"
    )

    add_sample(
        "Explain the categories of SQL operators with examples.",
        "SQL operators are categorized into:\n\n1. **Arithmetic Operators**: Perform mathematical calculations (`+`, `-`, `*`, `/`, `%` modulo).\n   - Example: `SELECT SALARY + BONUS FROM EMPLOYEE;`\n\n2. **Comparison Operators**: Compare expressions and return boolean truth values (`=`, `!=`, `<>`, `>`, `<`, `>=`, `<=`, `!<`, `!>`).\n   - Example: `WHERE AGE >= 21`\n\n3. **Logical Operators**: Combine multiple boolean conditions:\n   - `AND`: True if all conditions are true.\n   - `OR`: True if any condition is true.\n   - `NOT`: Inverts the truth value.\n   - `BETWEEN`: Searches within an inclusive range (`WHERE SALARY BETWEEN 3000 AND 5000`).\n   - `IN`: Matches any value in a discrete set (`WHERE DEPT IN ('HR', 'IT')`).\n   - `LIKE`: Matches pattern with wildcards (`%` for multi-character, `_` for single character).\n   - `EXISTS`: Evaluates whether a subquery returns any rows.\n   - `ALL` / `ANY`: Compares scalar value to all or any values returned by a subquery.",
        "sql_concept"
    )

    # ==========================================
    # 8. SQL VIEWS
    # ==========================================
    add_sample(
        "What is a View in SQL and what are its key benefits?",
        "A View in SQL is a virtual table defined by a stored SQL query. It does not store physical data itself; instead, it dynamically queries the underlying base tables whenever accessed.\n\nKey benefits of Views:\n1. **Security & Access Control**: Restricts user access to specific columns or rows without exposing raw tables.\n2. **Simplicity**: Encapsulates complex multi-table joins and aggregation logic into a simple virtual table.\n3. **Consistency**: Provides a consistent schema abstraction even if underlying base table structures change.",
        "sql_concept"
    )

    add_sample(
        "Write a SQL statement to create a view named DetailsView containing NAME and ADDRESS from Student_Details for students with STU_ID < 4.",
        "```sql\nCREATE VIEW DetailsView AS\nSELECT NAME, ADDRESS\nFROM Student_Details\nWHERE STU_ID < 4;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL statement to create a view named MarksView joining Student_Detail and Student_Marks on student NAME, returning NAME, ADDRESS, and MARKS.",
        "```sql\nCREATE VIEW MarksView AS\nSELECT \n    Student_Detail.NAME,\n    Student_Detail.ADDRESS,\n    Student_Marks.MARKS\nFROM Student_Detail\nINNER JOIN Student_Marks\n    ON Student_Detail.NAME = Student_Marks.NAME;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL statement to drop a view named DetailsView.",
        "```sql\nDROP VIEW DetailsView;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 9. SQL INDEXES
    # ==========================================
    add_sample(
        "What is an Index in SQL? Explain its advantages and trade-offs.",
        "An Index is a database data structure (such as B-Tree or Hash) created on table columns to accelerate data retrieval speed during `SELECT` queries and `WHERE` filtering.\n\n**Advantages**:\n- Substantially reduces disk I/O and query execution time for searches and lookups.\n- Speeds up sorting (`ORDER BY`) and grouping (`GROUP BY`).\n\n**Trade-offs**:\n- Consumes additional physical storage space.\n- Slows down write operations (`INSERT`, `UPDATE`, `DELETE`) because indexes must be recalculated and updated on each write.",
        "sql_concept"
    )

    add_sample(
        "Write SQL queries to create a standard index, create a unique index on websites(site_name), and drop the index.",
        "```sql\n-- Create standard index\nCREATE INDEX idx_emp_dept ON EMPLOYEE (DEPT_ID);\n\n-- Create unique index\nCREATE UNIQUE INDEX websites_idx ON websites (site_name);\n\n-- Drop index\nDROP INDEX websites_idx;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 10. SUBQUERIES (SELECT, INSERT, UPDATE, DELETE)
    # ==========================================
    add_sample(
        "Explain the rules and structure of SQL subqueries.",
        "A Subquery (or inner query) is an SQL query nested inside another outer SQL statement (such as `SELECT`, `INSERT`, `UPDATE`, or `DELETE`).\n\nRules for Subqueries:\n1. **Enclosure**: Must be enclosed within parentheses `(...)`.\n2. **Placement**: Can be placed in `WHERE`, `FROM` (derived table), `SELECT`, or `HAVING` clauses.\n3. **Comparison Operators**: Used with single-row operators (`=`, `<`, `>`, `<=`, `>=`) or multi-row operators (`IN`, `ANY`, `ALL`, `EXISTS`).\n4. **Ordering**: An `ORDER BY` clause cannot be used inside a subquery unless accompanied by pagination (`TOP` / `LIMIT`), though `GROUP BY` is permitted.",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query using a subquery to select all columns from EMPLOYEE for employees whose ID is among those with SALARY > 4500.",
        "```sql\nSELECT *\nFROM EMPLOYEE\nWHERE ID IN (\n    SELECT ID\n    FROM EMPLOYEE\n    WHERE SALARY > 4500\n);\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query to insert records into EMPLOYEE_BKP from EMPLOYEE using a subquery.",
        "```sql\nINSERT INTO EMPLOYEE_BKP\nSELECT *\nFROM EMPLOYEE\nWHERE ID IN (\n    SELECT ID\n    FROM EMPLOYEE\n);\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query using a subquery to reduce SALARY by 75% (multiply by 0.25) in EMPLOYEE for employees whose AGE is in CUSTOMERS_BKP with AGE >= 29.",
        "```sql\nUPDATE EMPLOYEE\nSET SALARY = SALARY * 0.25\nWHERE AGE IN (\n    SELECT AGE\n    FROM CUSTOMERS_BKP\n    WHERE AGE >= 29\n);\n```",
        "text_to_sql"
    )

    add_sample(
        "Write a SQL query using a subquery to delete employees from EMPLOYEE whose AGE is in EMPLOYEE_BKP with AGE >= 29.",
        "```sql\nDELETE FROM EMPLOYEE\nWHERE AGE IN (\n    SELECT AGE\n    FROM EMPLOYEE_BKP\n    WHERE AGE >= 29\n);\n```",
        "text_to_sql"
    )

    # ==========================================
    # 11. CLAUSES & AGGREGATE FUNCTIONS
    # ==========================================
    add_sample(
        "Explain the purpose and execution sequence of GROUP BY, HAVING, and ORDER BY clauses.",
        "1. **`GROUP BY`**: Collapses rows with identical values in specified columns into summary rows for aggregation.\n2. **`HAVING`**: Filters groups *after* aggregation (evaluated after `GROUP BY`). Unlike `WHERE`, `HAVING` can filter on aggregate function results (e.g. `HAVING COUNT(*) > 2`).\n3. **`ORDER BY`**: Sorts the final result set in ascending (`ASC`, default) or descending (`DESC`) order.\n\n**Logical Execution Order**: `FROM` -> `WHERE` -> `GROUP BY` -> `HAVING` -> `SELECT` -> `ORDER BY`.",
        "sql_concept"
    )

    add_sample(
        "Write a SQL query to count the number of products per COMPANY from PRODUCT_MAST, filtering for companies with more than 2 products.",
        "```sql\nSELECT COMPANY, COUNT(*)\nFROM PRODUCT_MAST\nGROUP BY COMPANY\nHAVING COUNT(*) > 2;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write SQL queries demonstrating COUNT(*), COUNT(DISTINCT column), and COUNT with WHERE conditions on table PRODUCT_MAST.",
        "```sql\n-- Total rows\nSELECT COUNT(*) FROM PRODUCT_MAST;\n\n-- Total rows matching condition\nSELECT COUNT(*) FROM PRODUCT_MAST WHERE RATE >= 20;\n\n-- Distinct companies count\nSELECT COUNT(DISTINCT COMPANY) FROM PRODUCT_MAST;\n```",
        "text_to_sql"
    )

    add_sample(
        "Write SQL queries demonstrating SUM, AVG, MAX, and MIN aggregate functions on table PRODUCT_MAST.",
        "```sql\n-- Total cost\nSELECT SUM(COST) FROM PRODUCT_MAST;\n\n-- Sum with GROUP BY and HAVING\nSELECT COMPANY, SUM(COST) \nFROM PRODUCT_MAST \nGROUP BY COMPANY \nHAVING SUM(COST) >= 170;\n\n-- Average cost\nSELECT AVG(COST) FROM PRODUCT_MAST;\n\n-- Maximum rate\nSELECT MAX(RATE) FROM PRODUCT_MAST;\n\n-- Minimum rate\nSELECT MIN(RATE) FROM PRODUCT_MAST;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 12. SQL JOINS
    # ==========================================
    add_sample(
        "Explain the four types of SQL JOINs with clear distinctions.",
        "SQL JOINs combine columns from two or more tables based on a related column:\n\n1. **INNER JOIN**: Returns only rows where there is a matching value in both tables.\n2. **LEFT (OUTER) JOIN**: Returns all rows from the left table, plus matched rows from the right table. Non-matching right columns are populated with `NULL`.\n3. **RIGHT (OUTER) JOIN**: Returns all rows from the right table, plus matched rows from the left table. Non-matching left columns are populated with `NULL`.\n4. **FULL (OUTER) JOIN**: Returns all records when there is a match in either left or right table, filling unmatched columns on either side with `NULL`.",
        "sql_concept"
    )

    add_sample(
        "Write SQL queries for INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL JOIN between EMPLOYEE and PROJECT on EMP_ID.",
        "```sql\n-- INNER JOIN\nSELECT EMPLOYEE.EMP_NAME, PROJECT.DEPARTMENT\nFROM EMPLOYEE\nINNER JOIN PROJECT\n    ON PROJECT.EMP_ID = EMPLOYEE.EMP_ID;\n\n-- LEFT JOIN\nSELECT EMPLOYEE.EMP_NAME, PROJECT.DEPARTMENT\nFROM EMPLOYEE\nLEFT JOIN PROJECT\n    ON PROJECT.EMP_ID = EMPLOYEE.EMP_ID;\n\n-- RIGHT JOIN\nSELECT EMPLOYEE.EMP_NAME, PROJECT.DEPARTMENT\nFROM EMPLOYEE\nRIGHT JOIN PROJECT\n    ON PROJECT.EMP_ID = EMPLOYEE.EMP_ID;\n\n-- FULL JOIN\nSELECT EMPLOYEE.EMP_NAME, PROJECT.DEPARTMENT\nFROM EMPLOYEE\nFULL JOIN PROJECT\n    ON PROJECT.EMP_ID = EMPLOYEE.EMP_ID;\n```",
        "text_to_sql"
    )

    # ==========================================
    # 13. SQL SET OPERATIONS
    # ==========================================
    add_sample(
        "Explain SQL Set Operations: UNION, UNION ALL, INTERSECT, and MINUS.",
        "SQL Set operations combine the result sets of two or more `SELECT` queries into a single result set.\n\n**Requirements**: Both queries must have the same number of columns in the select list with compatible data types in corresponding positions.\n\n1. **`UNION`**: Combines results from both queries and removes duplicate rows.\n2. **`UNION ALL`**: Combines results from both queries and preserves all duplicates (faster execution).\n3. **`INTERSECT`**: Returns only the common distinct rows present in both queries.\n4. **`MINUS` (or `EXCEPT`)**: Returns distinct rows from the first query that do not exist in the second query.",
        "sql_concept"
    )

    add_sample(
        "Write SQL queries demonstrating UNION, INTERSECT, and MINUS between tables First and Second.",
        "```sql\n-- UNION (all distinct rows from First and Second)\nSELECT column_name FROM First\nUNION\nSELECT column_name FROM Second;\n\n-- INTERSECT (rows common to both First and Second)\nSELECT column_name FROM First\nINTERSECT\nSELECT column_name FROM Second;\n\n-- MINUS (rows in First that do not exist in Second)\nSELECT column_name FROM First\nMINUS\nSELECT column_name FROM Second;\n```",
        "text_to_sql"
    )

    return samples

if __name__ == "__main__":
    pdf_samples = generate_pdf_1_samples()
    print(f"Generated {len(pdf_samples)} high-fidelity instruction-tuning samples from PDF 1.")
    
    # Save standalone PDF 1 dataset
    pdf1_jsonl = Path("data/pdf_1_dataset.jsonl")
    with open(pdf1_jsonl, "w", encoding="utf-8") as f:
        for s in pdf_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"Saved PDF 1 samples to {pdf1_jsonl}")
