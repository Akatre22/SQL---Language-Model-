"""
Process PDF 5: sql-the-complete-reference-third-edition-sep-2009.pdf
(McGraw-Hill SQL: The Complete Reference, 3rd Edition)
Generates high-level Q&A covering Relational Foundations (Codd's Rules), Advanced Joins & Set Operations,
Subqueries (Correlated, EXISTS, ALL/ANY), Data Integrity & Normalization, Transaction Concurrency & Locks,
Security (GRANT/REVOKE/Roles), Information Schema, and Data Warehousing (OLAP vs OLTP, Star/Snowflake schemas).
"""

import json
import os
import re

OUTPUT_JSONL = r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\pdf_5_dataset.jsonl"

qa_dataset = []

def add_qa(question, answer, category="SQL Complete Reference"):
    text = f"### Question:\n{question.strip()}\n\n### Answer:\n{answer.strip()}"
    qa_dataset.append({
        "question": question.strip(),
        "answer": answer.strip(),
        "text": text,
        "source": "McGrawHill_SQL_Complete_Reference_3rdEd",
        "category": category
    })

pdf5_qa_specs = [
    # 1. Relational Model & Codd's Rules
    {
        "q": "What is E.F. Codd's Relational Model and what are its core tenets?",
        "a": "Proposed by Edgar F. Codd in 1970, the **Relational Model** represents data in terms of mathematical relations (tables) composed of tuples (rows) and attributes (columns).\n\n**Core Tenets:**\n1. **Data Representation:** All information is represented explicitly at the logical level as values in table cells.\n2. **Physical Data Independence:** Logical database schemas and application programs are independent of physical storage structures, access paths, or disk layout.\n3. **Set-Oriented Operations:** Data retrieval and manipulation operate on entire sets of records rather than row-by-row navigation.\n4. **Systematic Null Treatment:** Systematic handling of missing or inapplicable information distinct from zero or empty strings.",
        "cat": "Relational Theory"
    },
    {
        "q": "What are the four levels of Database Integrity in SQL?",
        "a": "SQL enforces data integrity across four structural tiers:\n\n1. **Entity Integrity:** Guarantees that each row in a table is uniquely identifiable and the primary key is never `NULL`.\n2. **Domain Integrity:** Restricts column values to valid ranges, formats, and data types via `CHECK`, `NOT NULL`, and data type definitions.\n3. **Referential Integrity:** Guarantees valid relationships across tables by requiring foreign keys to match existing parent primary keys or be `NULL`.\n4. **User-Defined Integrity:** Business rules implemented via triggers, stored procedures, or complex assertions that cannot be expressed purely with standard declarative constraints.",
        "cat": "Data Integrity"
    },

    # 2. Database Normalization
    {
        "q": "Explain the stages of Database Normalization from 1NF to 3NF and BCNF.",
        "a": "Database Normalization eliminates data redundancy and prevents update/delete anomalies:\n\n- **1NF (First Normal Form):** Each column contains atomic (indivisible) values, and there are no repeating groups.\n- **2NF (Second Normal Form):** Meets 1NF, and all non-key attributes are fully functionally dependent on the entire primary key (eliminates partial key dependency).\n- **3NF (Third Normal Form):** Meets 2NF, and no non-key attribute depends on another non-key attribute (eliminates transitive dependencies: $X \\rightarrow Y \\rightarrow Z$).\n- **BCNF (Boyce-Codd Normal Form):** Stricter version of 3NF where for every functional dependency $X \\rightarrow Y$, $X$ must be a super key.",
        "cat": "Data Modeling"
    },

    # 3. Set Operations & Advanced Subqueries
    {
        "q": "What are the differences between UNION, UNION ALL, INTERSECT, and EXCEPT in SQL?",
        "a": "SQL Set Operations combine result sets from two or more queries:\n\n- **`UNION`:** Combines result sets and removes duplicate records (requires sorting/deduplication step).\n- **`UNION ALL`:** Combines result sets and preserves all duplicate rows (faster than `UNION`).\n- **`INTERSECT`:** Returns only the distinct rows that appear in **both** query result sets.\n- **`EXCEPT` / `MINUS`:** Returns distinct rows from the first query that do **not** appear in the second query.\n\n**Syntax Requirement:** All combined `SELECT` queries must have identical column counts and compatible data types.",
        "cat": "Set Operations"
    },
    {
        "q": "How does a Correlated Subquery work and how does it compare to an Uncorrelated Subquery?",
        "a": "- **Uncorrelated Subquery:** Evaluates once independently before the outer query runs. Its static result is passed to the outer query.\n- **Correlated Subquery:** References columns from the outer query table, requiring the subquery to be evaluated once for **every individual row** processed by the outer query.\n\n**Correlated Subquery Example:**\n```sql\n-- Find employees earning more than the average salary of their respective department:\nSELECT e.EmployeeID, e.Name, e.DepartmentID, e.Salary\nFROM Employees e\nWHERE e.Salary > (\n    SELECT AVG(d.Salary)\n    FROM Employees d\n    WHERE d.DepartmentID = e.DepartmentID\n);\n```",
        "cat": "Subqueries"
    },
    {
        "q": "How do EXISTS and NOT EXISTS operators work in SQL subqueries?",
        "a": "The `EXISTS` operator tests whether a subquery returns at least one row, returning `TRUE` or `FALSE` without retrieving the full dataset.\n\n**Key Characteristics:**\n- Evaluation terminates as soon as the first matching row is found (short-circuiting), making it highly optimized.\n- Handles `NULL` values safely compared to `IN` / `NOT IN`.\n\n**Example SQL:**\n```sql\n-- Find customers who have placed at least one high-value order:\nSELECT c.CustomerID, c.CompanyName\nFROM Customers c\nWHERE EXISTS (\n    SELECT 1 \n    FROM Orders o \n    WHERE o.CustomerID = c.CustomerID AND o.TotalAmount > 5000\n);\n```",
        "cat": "Subqueries"
    },

    # 4. Locking & Concurrency Control
    {
        "q": "What is the difference between Shared Locks (S-Locks) and Exclusive Locks (X-Locks)?",
        "a": "- **Shared Lock (S-Lock / Read Lock):** Acquired during `SELECT` operations. Multiple concurrent transactions can hold shared locks on the same data resource simultaneously, but no transaction can modify the resource until all shared locks are released.\n- **Exclusive Lock (X-Lock / Write Lock):** Acquired during `INSERT`, `UPDATE`, or `DELETE` operations. Only one transaction can hold an exclusive lock on a resource at a time. It prevents other transactions from reading or writing to that resource until committed.\n\n**Lock Compatibility Table:**\n| | Shared (S) | Exclusive (X) |\n| :--- | :---: | :---: |\n| **Shared (S)** | Compatible | Conflict |\n| **Exclusive (X)** | Conflict | Conflict |",
        "cat": "Concurrency & Locking"
    },
    {
        "q": "What is a Deadlock in SQL and how do database management systems resolve it?",
        "a": "A **Deadlock** occurs when two or more transactions hold locks on resources that the other transactions need, creating a circular wait state where none can proceed.\n\n**Example:**\n- Transaction 1 locks Table A and requests a lock on Table B.\n- Transaction 2 locks Table B and requests a lock on Table A.\n\n**Resolution:**\nThe DBMS Deadlock Detector identifies the cycle in the lock-wait graph, selects the least costly transaction (\"the victim\"), automatically rolls it back (`ROLLBACK`), and allows the remaining transaction to complete.",
        "cat": "Concurrency & Locking"
    },

    # 5. Security & Access Control
    {
        "q": "How do GRANT and REVOKE statements manage database security and permissions in SQL?",
        "a": "The Data Control Language (DCL) commands manage user access and privileges:\n\n1. **`GRANT`:** Bestows specific permissions on database objects to users or roles.\n```sql\nGRANT SELECT, INSERT ON Orders TO SalesRole;\nGRANT ALL PRIVILEGES ON Customers TO AdminUser WITH GRANT OPTION;\n```\n\n2. **`REVOKE`:** Removes previously granted permissions.\n```sql\nREVOKE INSERT ON Orders FROM SalesRole;\n```\n\n3. **Roles:** Collections of privileges assigned to groups of users for streamlined security management.\n```sql\nCREATE ROLE AnalystRole;\nGRANT SELECT ON Schema.Analytics TO AnalystRole;\nGRANT AnalystRole TO User1, User2;\n```",
        "cat": "Security"
    },

    # 6. Information Schema & Catalogs
    {
        "q": "What is the INFORMATION_SCHEMA in SQL and how is it queried?",
        "a": "The `INFORMATION_SCHEMA` is an ANSI-standard set of read-only views containing metadata about all database objects (tables, columns, views, constraints, routines).\n\n**Common Queries:**\n```sql\n-- List all tables in a schema:\nSELECT TABLE_NAME, TABLE_TYPE \nFROM INFORMATION_SCHEMA.TABLES \nWHERE TABLE_SCHEMA = 'production';\n\n-- Inspect columns and data types:\nSELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE \nFROM INFORMATION_SCHEMA.COLUMNS \nWHERE TABLE_NAME = 'Orders';\n```",
        "cat": "System Catalog"
    },

    # 7. Data Warehousing: OLTP vs OLAP, Star vs Snowflake Schemas
    {
        "q": "What are the core differences between OLTP and OLAP database systems?",
        "a": "| Dimension | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |\n| :--- | :--- | :--- |\n| **Purpose** | Day-to-day transactional operations (e.g. e-commerce, banking). | Business intelligence, historical reporting, and analytics. |\n| **Data Structure** | Normalized (3NF/BCNF) to minimize redundancy. | Denormalized (Star/Snowflake schemas) optimized for reads. |\n| **Query Types** | Fast, simple read/write of individual records. | Complex aggregate queries scanning millions of rows. |\n| **Storage** | Row-oriented storage engines. | Columnar storage engines (e.g., Snowflake, BigQuery, ClickHouse). |",
        "cat": "Data Warehousing"
    },
    {
        "q": "What is the difference between a Star Schema and a Snowflake Schema in data warehousing?",
        "a": "- **Star Schema:** Consists of a central **Fact Table** surrounded by completely **denormalized Dimension Tables**. Produces simpler queries with fewer joins and optimal query performance.\n- **Snowflake Schema:** An extension of the Star Schema where dimension tables are **further normalized** into sub-dimensions (e.g., `DimProduct` references `DimCategory` and `DimBrand`). Reduces data redundancy but requires more join operations in queries.\n\n**Fact vs Dimension:**\n- **Fact Table:** Stores quantitative numeric metrics/measures (e.g., `SalesAmount`, `Quantity`) and foreign keys.\n- **Dimension Table:** Stores descriptive context attributes (e.g., `CustomerName`, `StoreCity`, `DateKey`).",
        "cat": "Data Warehousing"
    }
]

# Add specs
for spec in pdf5_qa_specs:
    add_qa(spec["q"], spec["a"], spec["cat"])

# Add variations
variations = []
for item in qa_dataset:
    p_q = item["question"]
    if "What is" in p_q:
        p_q2 = p_q.replace("What is", "Explain the concept of")
    elif "What are" in p_q:
        p_q2 = p_q.replace("What are", "Provide a detailed breakdown of")
    elif "How do" in p_q:
        p_q2 = p_q.replace("How do", "Explain how")
    elif "Explain" in p_q:
        p_q2 = p_q.replace("Explain", "Discuss in detail")
    else:
        p_q2 = f"Can you describe {p_q.lower()}?"

    if p_q2 != item["question"]:
        variations.append({
            "question": p_q2,
            "answer": item["answer"],
            "text": f"### Question:\n{p_q2}\n\n### Answer:\n{item['answer']}",
            "source": item["source"],
            "category": item["category"]
        })

qa_dataset.extend(variations)

def generate_pdf_5_samples():
    """Returns standardized training sample dicts for process_sql_data pipeline."""
    samples = []
    for item in qa_dataset:
        samples.append({
            "instruction": item["question"],
            "response": item["answer"],
            "output": item["answer"],
            "domain": "sql",
            "task": "pdf_qa",
            "source": "McGrawHill_SQL_Complete_Reference_3rdEd"
        })
    return samples

if __name__ == "__main__":
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for row in qa_dataset:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[+] Successfully generated {len(qa_dataset)} Q&A pairs in {OUTPUT_JSONL}")
