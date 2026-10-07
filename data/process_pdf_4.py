"""
Process PDF 4: rbafy.pdf (Enterprise SQL Programming, DB2/ANSI SQL Architecture)
Generates high-quality enterprise SQL samples covering Views, Indexes, Materialized Query Tables,
Sequences vs Identity Columns, Constraints & Cascades, Triggers, Stored Procedures,
User-Defined Functions (UDFs), Transactions/Isolation Levels, CTEs & Recursive Queries.
"""

import json
import os
import re

OUTPUT_JSONL = r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\pdf_4_dataset.jsonl"

qa_dataset = []

def add_qa(question, answer, category="Enterprise SQL"):
    text = f"### Question:\n{question.strip()}\n\n### Answer:\n{answer.strip()}"
    qa_dataset.append({
        "question": question.strip(),
        "answer": answer.strip(),
        "text": text,
        "source": "IBM_Enterprise_SQL_rbafy",
        "category": category
    })

pdf4_qa_specs = [
    # 1. Views & View Options
    {
        "q": "What is an SQL View and what is the purpose of the WITH CHECK OPTION clause?",
        "a": "An **SQL View** is a virtual table defined by an underlying `SELECT` query that does not store data itself but displays dynamic data from base tables.\n\n**`WITH CHECK OPTION` Purpose:**\nWhen creating updatable views, `WITH CHECK OPTION` enforces that any `INSERT` or `UPDATE` executed through the view must satisfy the view's `WHERE` clause condition. If an update would cause a row to disappear from the view, the database rejects the operation.\n\n**Example SQL:**\n```sql\nCREATE VIEW ActiveEmployeesView AS\nSELECT EmployeeID, Name, Department, Status\nFROM Employees\nWHERE Status = 'Active'\nWITH CHECK OPTION;\n```",
        "cat": "Views"
    },
    {
        "q": "What is the difference between WITH LOCAL CHECK OPTION and WITH CASCADED CHECK OPTION on nested views?",
        "a": "- **`WITH CASCADED CHECK OPTION` (Default):** Evaluates and enforces the `WHERE` clauses of the current view *and all underlying views* in the hierarchy.\n- **`WITH LOCAL CHECK OPTION`:** Enforces only the `WHERE` clause conditions defined directly in the current view, without validating search conditions of underlying non-checked views.\n\n**Example SQL:**\n```sql\nCREATE VIEW HighSalarySales AS\nSELECT * FROM ActiveEmployeesView\nWHERE Salary > 80000\nWITH CASCADED CHECK OPTION;\n```",
        "cat": "Views"
    },

    # 2. Materialized Query Tables (MQT) & Temp Tables
    {
        "q": "What is a Materialized Query Table (MQT) and how does it differ from a standard View?",
        "a": "A **Materialized Query Table (MQT)** (also called an Indexed View or Materialized View) stores the precomputed physical result set of a complex query on disk, unlike a standard View which re-executes the query dynamically.\n\n**Key Differences:**\n1. **Performance:** MQTs provide extremely fast reads on large aggregate queries without recalculating joins or aggregations.\n2. **Maintenance:** Can be refreshed automatically (`REFRESH IMMEDIATE`) or on demand (`REFRESH DEFERRED`).\n3. **Query Rewrite:** The SQL query optimizer can automatically route incoming queries to the MQT even if the user queries the base tables.\n\n**Example SQL:**\n```sql\nCREATE TABLE MonthlySalesSummary AS (\n    SELECT DepartmentID, Region, SUM(SalesAmount) AS TotalSales, COUNT(*) AS OrderCount\n    FROM Sales\n    GROUP BY DepartmentID, Region\n) DATA INITIALLY DEFERRED REFRESH DEFERRED;\n```",
        "cat": "Database Objects"
    },
    {
        "q": "How do you create and use a Declared Global Temporary Table in SQL?",
        "a": "A **Declared Global Temporary Table (DGTT)** is a temporary table created within an application session that is automatically dropped when the session ends or transaction disconnects.\n\n**Example SQL:**\n```sql\nDECLARE GLOBAL TEMPORARY TABLE SESSION.TempOrders (\n    OrderID INT,\n    CustomerID INT,\n    TotalAmount DECIMAL(10, 2)\n) ON COMMIT PRESERVE ROWS;\n\n-- Inserting session data:\nINSERT INTO SESSION.TempOrders (OrderID, CustomerID, TotalAmount)\nSELECT OrderID, CustomerID, TotalAmount \nFROM Orders \nWHERE OrderDate >= CURRENT_DATE - 7;\n```",
        "cat": "Temporary Tables"
    },

    # 3. Sequences vs Identity Columns
    {
        "q": "What is the difference between an Identity Column and an SQL Sequence?",
        "a": "| Feature | Identity Column | SQL Sequence (`CREATE SEQUENCE`) |\n| :--- | :--- | :--- |\n| **Scope** | Bound to a single table column. | Independent database object usable across multiple tables. |\n| **Generation** | `GENERATED ALWAYS AS IDENTITY` | `NEXT VALUE FOR SequenceName` |\n| **Flexibility** | Automatically increments on insert. | Can be assigned, cached, recycled, or fetched before inserting. |\n| **Sharing** | Cannot be shared among tables. | Can generate unique surrogate keys across multiple related tables. |\n\n**Sequence Example:**\n```sql\nCREATE SEQUENCE OrderNumberSeq START WITH 1000 INCREMENT BY 1 NO MAXVALUE;\n\nINSERT INTO Orders (OrderID, OrderDate) \nVALUES (NEXT VALUE FOR OrderNumberSeq, CURRENT_DATE);\n```",
        "cat": "Sequences & Keys"
    },

    # 4. Indexes & Performance Optimization
    {
        "q": "What is the difference between a Clustered Index and a Non-Clustered Index?",
        "a": "- **Clustered Index:** Physically sorts and stores the actual table data rows on disk in the order of the index key. A table can only have **one** clustered index (often the Primary Key).\n- **Non-Clustered Index:** A separate data structure (B-tree) containing sorted key columns and row pointers (RID / ROWID) that point back to the actual data pages. A table can have multiple non-clustered indexes.\n\n**Example SQL:**\n```sql\nCREATE INDEX idx_customer_email ON Customers (Email);\nCREATE UNIQUE INDEX idx_emp_national_id ON Employees (NationalID);\n```",
        "cat": "Indexes & Performance"
    },
    {
        "q": "What is a Composite Index and what is the Leftmost Prefix Rule?",
        "a": "A **Composite Index** is an index created on two or more columns in a table.\n\n**Leftmost Prefix Rule:**\nThe database query engine can use the composite index only if the query's filtering predicates (`WHERE` clauses) include the leading (leftmost) column of the index definition.\n\n**Example:**\n```sql\nCREATE INDEX idx_emp_dept_salary ON Employees (DepartmentID, Salary);\n```\n- `WHERE DepartmentID = 5 AND Salary > 50000` $\\rightarrow$ **Uses Index**\n- `WHERE DepartmentID = 5` $\\rightarrow$ **Uses Index**\n- `WHERE Salary > 50000` $\\rightarrow$ **Cannot use index effectively (skips leftmost column)**",
        "cat": "Indexes & Performance"
    },

    # 5. Cascading Referential Integrity
    {
        "q": "Explain ON DELETE CASCADE and ON DELETE SET NULL in SQL foreign key constraints.",
        "a": "Cascading referential actions dictate how child rows react when a referenced parent record is deleted:\n\n1. **`ON DELETE CASCADE`:** Automatically deletes all related child records when the referenced parent record is deleted.\n2. **`ON DELETE SET NULL`:** Sets the child foreign key column value to `NULL` when the parent record is deleted (requires foreign key to be nullable).\n3. **`ON DELETE RESTRICT` / `NO ACTION` (Default):** Rejects the deletion of the parent row if any referencing child rows exist.\n\n**Example SQL:**\n```sql\nCREATE TABLE OrderItems (\n    ItemID INT PRIMARY KEY,\n    OrderID INT,\n    ProductID INT,\n    Quantity INT,\n    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE\n);\n```",
        "cat": "Constraints"
    },

    # 6. Triggers
    {
        "q": "What is an SQL Trigger and when would you use a BEFORE vs AFTER Trigger?",
        "a": "An **SQL Trigger** is a named database object that automatically executes (fires) in response to `INSERT`, `UPDATE`, or `DELETE` events on a table.\n\n- **`BEFORE` Trigger:** Executes before the change is written to disk. Used for data validation, data sanitization, setting default values, or blocking invalid transactions with errors.\n- **`AFTER` Trigger:** Executes after the row modification is committed to the buffer. Used for audit logging, updating summary tables, or sending notifications.\n\n**Example Audit Trigger:**\n```sql\nCREATE TRIGGER trg_audit_salary_update\nAFTER UPDATE OF Salary ON Employees\nREFERENCING OLD ROW AS old_emp NEW ROW AS new_emp\nFOR EACH ROW\nBEGIN\n    INSERT INTO SalaryAuditLog (EmployeeID, OldSalary, NewSalary, ChangedAt)\n    VALUES (new_emp.EmployeeID, old_emp.Salary, new_emp.Salary, CURRENT_TIMESTAMP);\nEND;\n```",
        "cat": "Triggers"
    },

    # 7. Stored Procedures & User Defined Functions
    {
        "q": "What is the difference between a Stored Procedure and a User-Defined Function (UDF)?",
        "a": "| Feature | Stored Procedure | User-Defined Function (UDF) |\n| :--- | :--- | :--- |\n| **Invocation** | Executed using `CALL ProcedureName(...)`. | Called directly within SQL statements (`SELECT`, `WHERE`). |\n| **Return Value** | Can return zero, one, or multiple values via `OUT` parameters or result sets. | Must return a single scalar value or a table result. |\n| **Transaction Control** | Can execute `COMMIT` and `ROLLBACK` commands. | Cannot perform transaction control (`COMMIT`/`ROLLBACK`). |\n| **Data Modification** | Can execute DDL and DML operations. | Scalar UDFs cannot alter database state (read-only in queries). |\n\n**UDF Example:**\n```sql\nCREATE FUNCTION CalculateTax(salary DECIMAL(10,2))\nRETURNS DECIMAL(10,2)\nLANGUAGE SQL\nBEGIN\n    RETURN salary * 0.18;\nEND;\n```",
        "cat": "Programmability"
    },
    {
        "q": "How do you write a Stored Procedure with IN and OUT parameters in SQL?",
        "a": "```sql\nCREATE PROCEDURE GetCustomerOrderTotal(\n    IN in_customer_id INT,\n    OUT out_total_amount DECIMAL(12, 2),\n    OUT out_order_count INT\n)\nLANGUAGE SQL\nBEGIN\n    SELECT COALESCE(SUM(TotalAmount), 0), COUNT(*)\n    INTO out_total_amount, out_order_count\n    FROM Orders\n    WHERE CustomerID = in_customer_id;\nEND;\n```\n\n**Execution:**\n```sql\nCALL GetCustomerOrderTotal(101, @total, @count);\nSELECT @total AS TotalSpent, @count AS TotalOrders;\n```",
        "cat": "Programmability"
    },

    # 8. Transactions & Isolation Levels
    {
        "q": "What are ACID properties in relational database management systems?",
        "a": "ACID properties ensure transaction reliability:\n\n1. **Atomicity:** All operations in a transaction succeed completely or none take effect (\"all-or-nothing\").\n2. **Consistency:** A transaction transforms the database from one valid state to another, upholding all constraints and rules.\n3. **Isolation:** Concurrent transactions execute without interfering with one another.\n4. **Durability:** Once a transaction commits, its changes are permanently recorded and survive system failures.",
        "cat": "Transactions"
    },
    {
        "q": "Explain SQL Transaction Isolation Levels and the concurrency phenomena they prevent.",
        "a": "SQL standard defines 4 transaction isolation levels:\n\n| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read |\n| :--- | :---: | :---: | :---: |\n| **Read Uncommitted** | Possible | Possible | Possible |\n| **Read Committed** | Prevented | Possible | Possible |\n| **Repeatable Read** | Prevented | Prevented | Possible |\n| **Serializable** | Prevented | Prevented | Prevented |\n\n- **Dirty Read:** Reading uncommitted changes made by another active transaction.\n- **Non-Repeatable Read:** Re-reading the same row returns modified column values.\n- **Phantom Read:** Re-executing a range query returns newly inserted or deleted rows.",
        "cat": "Transactions"
    },

    # 9. Advanced Querying: CTEs and Window Functions
    {
        "q": "How do Common Table Expressions (CTEs) improve query readability and modularity?",
        "a": "A **Common Table Expression (CTE)** defines a temporary named result set within the execution scope of a single `SELECT`, `INSERT`, `UPDATE`, or `DELETE` statement using the `WITH` keyword.\n\n**Advantages:**\n- Breaks complex nested subqueries into readable logical blocks.\n- Allows reusing the intermediate result multiple times in the main query.\n\n**Example SQL:**\n```sql\nWITH RegionalSales AS (\n    SELECT Region, SUM(SalesAmount) AS TotalSales\n    FROM Orders\n    GROUP BY Region\n),\nAverageSales AS (\n    SELECT AVG(TotalSales) AS AvgRegionalSales\n    FROM RegionalSales\n)\nSELECT r.Region, r.TotalSales\nFROM RegionalSales r, AverageSales a\nWHERE r.TotalSales > a.AvgRegionalSales;\n```",
        "cat": "Advanced SQL"
    },
    {
        "q": "How do you write a Recursive CTE to traverse organizational hierarchies or parent-child trees?",
        "a": "A **Recursive CTE** references itself to iteratively process hierarchical tree structures until a termination condition is reached.\n\n**Example SQL (Employee Hierarchy):**\n```sql\nWITH RECURSIVE OrgHierarchy AS (\n    -- Anchor Member: Top-level manager (no manager)\n    SELECT EmployeeID, Name, ManagerID, 1 AS Level\n    FROM Employees\n    WHERE ManagerID IS NULL\n    \n    UNION ALL\n    \n    -- Recursive Member: Subordinates\n    SELECT e.EmployeeID, e.Name, e.ManagerID, o.Level + 1\n    FROM Employees e\n    JOIN OrgHierarchy o ON e.ManagerID = o.EmployeeID\n)\nSELECT EmployeeID, Name, ManagerID, Level\nFROM OrgHierarchy\nORDER BY Level, ManagerID;\n```",
        "cat": "Advanced SQL"
    },
    {
        "q": "What is the difference between ROW_NUMBER(), RANK(), and DENSE_RANK() in SQL?",
        "a": "All three are ranking window functions evaluated over `OVER (ORDER BY ...)`:\n\n- **`ROW_NUMBER()`:** Assigns a strict sequential integer (1, 2, 3, 4) with no duplicates or gaps, even for tied values.\n- **`RANK()`:** Assigns the same rank to ties but skips subsequent rank numbers (e.g., 1, 2, 2, 4).\n- **`DENSE_RANK()`:** Assigns the same rank to ties without skipping subsequent rank numbers (e.g., 1, 2, 2, 3).\n\n**Example SQL:**\n```sql\nSELECT \n    EmployeeID, DepartmentID, Salary,\n    ROW_NUMBER() OVER(PARTITION BY DepartmentID ORDER BY Salary DESC) AS RowNum,\n    RANK()       OVER(PARTITION BY DepartmentID ORDER BY Salary DESC) AS Rnk,\n    DENSE_RANK() OVER(PARTITION BY DepartmentID ORDER BY Salary DESC) AS DenseRnk\nFROM Employees;\n```",
        "cat": "Window Functions"
    },
    {
        "q": "How do LEAD() and LAG() window functions work in SQL?",
        "a": "`LEAD()` and `LAG()` access column data from subsequent or previous rows relative to the current row without requiring self-joins.\n\n- **`LAG(col, offset, default)`:** Retrieves value from `offset` rows before the current row.\n- **`LEAD(col, offset, default)`:** Retrieves value from `offset` rows after the current row.\n\n**Example (Month-over-Month Revenue Growth):**\n```sql\nSELECT \n    SalesMonth,\n    Revenue,\n    LAG(Revenue, 1, 0) OVER(ORDER BY SalesMonth) AS PrevMonthRevenue,\n    Revenue - LAG(Revenue, 1, 0) OVER(ORDER BY SalesMonth) AS MoMGrowth\nFROM MonthlySales;\n```",
        "cat": "Window Functions"
    }
]

# Add specs
for spec in pdf4_qa_specs:
    add_qa(spec["q"], spec["a"], spec["cat"])

# Add variations
variations = []
for item in qa_dataset:
    p_q = item["question"]
    if "What is" in p_q:
        p_q2 = p_q.replace("What is", "Explain the concept of")
    elif "How do you" in p_q:
        p_q2 = p_q.replace("How do you", "Explain how to")
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

def generate_pdf_4_samples():
    """Returns standardized training sample dicts for process_sql_data pipeline."""
    samples = []
    for item in qa_dataset:
        samples.append({
            "instruction": item["question"],
            "response": item["answer"],
            "output": item["answer"],
            "domain": "sql",
            "task": "pdf_qa",
            "source": "IBM_Enterprise_SQL_rbafy"
        })
    return samples

if __name__ == "__main__":
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for row in qa_dataset:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[+] Successfully generated {len(qa_dataset)} Q&A pairs in {OUTPUT_JSONL}")
