"""
Process PDF 3: keip108.pdf (Introduction to Structured Query Language - SQL & RDBMS)
Generates high-quality Q&A samples covering MySQL data types, constraints, DDL, DML, DQL, aggregate functions, filtering, pattern matching, and table modifications.
"""

import json
import os
import re

OUTPUT_JSONL = r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\pdf_3_dataset.jsonl"
RAW_FILE = r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\extracted_pdf_3_raw.txt"

qa_dataset = []

def add_qa(question, answer, category="SQL"):
    # Format with clean markdown standard
    text = f"### Question:\n{question.strip()}\n\n### Answer:\n{answer.strip()}"
    qa_dataset.append({
        "question": question.strip(),
        "answer": answer.strip(),
        "text": text,
        "source": "NCERT_SQL_ClassXI_keip108",
        "category": category
    })

# Define curated, detailed, structured Q&A pairs directly from the contents of keip108.pdf
pdf3_qa_specs = [
    # 1. RDBMS and SQL Fundamentals
    {
        "q": "What is Structured Query Language (SQL) and what are its primary capabilities in an RDBMS?",
        "a": "Structured Query Language (SQL) is the standard query language used by relational database management systems (such as MySQL, PostgreSQL, Oracle, and SQL Server) to store, retrieve, and manipulate data.\n\n**Primary Capabilities of SQL:**\n- **Data Definition (DDL):** Define and modify database schemas, tables, and constraints (`CREATE`, `ALTER`, `DROP`).\n- **Data Manipulation (DML):** Insert, update, and delete rows in tables (`INSERT`, `UPDATE`, `DELETE`).\n- **Data Querying (DQL):** Retrieve and filter subsets of data with conditions (`SELECT`).\n- **Declarative Nature:** Users specify *what* data to retrieve rather than *how* to physically access it.",
        "cat": "SQL Basics"
    },
    {
        "q": "What are the syntax rules for writing SQL statements in MySQL?",
        "a": "Key syntax rules in MySQL include:\n1. **Case-Insensitive:** SQL keywords and commands are case-insensitive (`SELECT` is identical to `select`). By convention, keywords are written in uppercase.\n2. **Statement Terminator:** Every SQL statement terminates with a semicolon (`;`).\n3. **Multiline Statements:** Pressing Enter without a semicolon continues the statement on the next line, indicated by the continuation prompt (`->`).\n4. **Comments:** Single-line comments start with `-- ` or `#`, and multi-line comments are enclosed in `/* ... */`.",
        "cat": "SQL Syntax"
    },
    {
        "q": "What is the difference between CHAR and VARCHAR data types in MySQL?",
        "a": "The difference between `CHAR` and `VARCHAR` lies in memory allocation and length handling:\n\n- **`CHAR(M)` (Fixed Length):**\n  - Allocates a fixed number of `M` characters regardless of actual input length.\n  - Remaining space is padded with trailing spaces.\n  - Storage is constant (`M` bytes).\n  - Best for fixed-size values like state codes (`CHAR(2)`) or gender (`CHAR(1)`).\n\n- **`VARCHAR(M)` (Variable Length):**\n  - Stores only the actual characters provided plus 1 or 2 bytes of length prefix.\n  - Saves storage when string lengths vary significantly (e.g., `VARCHAR(100)` for customer names).\n  - Best for names, addresses, and descriptions.",
        "cat": "Data Types"
    },
    {
        "q": "Explain numeric data types in MySQL: INT, DECIMAL, and FLOAT.",
        "a": "Numeric data types in MySQL include:\n- **`INT` / `INTEGER`:** Stores standard 4-byte integers ranging from -2,147,483,648 to 2,147,483,647.\n- **`FLOAT` / `DOUBLE`:** Stores approximate floating-point numbers with scientific precision.\n- **`DECIMAL(P, D)` / `NUMERIC(P, D)`:** Stores exact fixed-point numbers with precision `P` (total digits) and scale `D` (digits after the decimal point). Example: `DECIMAL(10, 2)` for currency amounts up to `99,999,999.99`.",
        "cat": "Data Types"
    },
    {
        "q": "How does MySQL store DATE and TIME data types?",
        "a": "MySQL stores date and time values in standardized ISO formats:\n- **`DATE`:** Stores date in `'YYYY-MM-DD'` format (e.g., `'2026-09-24'`).\n- **`TIME`:** Stores time in `'HH:MM:SS'` format (e.g., `'14:30:00'`).\n- **`DATETIME`:** Combines date and time in `'YYYY-MM-DD HH:MM:SS'` format.\n- **`YEAR`:** Stores 4-digit year values (e.g., `2026`).",
        "cat": "Data Types"
    },

    # 2. Constraints
    {
        "q": "What are SQL constraints and why are they used?",
        "a": "SQL constraints are rules enforced on table columns to ensure data integrity, accuracy, and reliability.\n\n**Common MySQL Constraints:**\n1. **`PRIMARY KEY`:** Uniquely identifies each record; rejects duplicate and `NULL` values.\n2. **`NOT NULL`:** Ensures that a column cannot store `NULL` values.\n3. **`UNIQUE`:** Ensures all values in a column are distinct across rows (allows one `NULL`).\n4. **`DEFAULT <val>`:** Provides a fallback default value when no value is specified.\n5. **`FOREIGN KEY`:** Establishes a referential link to a primary key in another table.\n6. **`CHECK`:** Validates that values meet a boolean condition (e.g., `CHECK (age >= 18)`).",
        "cat": "Constraints"
    },
    {
        "q": "How do you define a PRIMARY KEY constraint during table creation in SQL?",
        "a": "You can define a primary key at the column level or table level.\n\n**Column-Level Definition:**\n```sql\nCREATE TABLE Student (\n    RollNo INT PRIMARY KEY,\n    Name VARCHAR(50) NOT NULL,\n    Class INT\n);\n```\n\n**Table-Level Definition (Useful for Composite Keys):**\n```sql\nCREATE TABLE StudentCourse (\n    RollNo INT,\n    CourseID VARCHAR(10),\n    EnrollDate DATE,\n    PRIMARY KEY (RollNo, CourseID)\n);\n```",
        "cat": "DDL"
    },
    {
        "q": "What is a FOREIGN KEY constraint and what is Referential Integrity?",
        "a": "A **`FOREIGN KEY`** is a column (or combination of columns) in one table that references the `PRIMARY KEY` of another table.\n\n**Referential Integrity:**\nIt ensures that relationships between tables remain consistent. MySQL prevents inserting a foreign key value if it does not exist in the referenced parent table, and restricts deleting parent records that have child dependencies.\n\n**Example SQL:**\n```sql\nCREATE TABLE Orders (\n    OrderID INT PRIMARY KEY,\n    OrderDate DATE,\n    CustomerID INT,\n    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)\n);\n```",
        "cat": "Constraints"
    },

    # 3. DDL Commands
    {
        "q": "How do you create, select, and view databases in MySQL?",
        "a": "Essential MySQL database commands:\n\n1. **Create Database:**\n```sql\nCREATE DATABASE SchoolDB;\n```\n\n2. **View Available Databases:**\n```sql\nSHOW DATABASES;\n```\n\n3. **Select Active Database:**\n```sql\nUSE SchoolDB;\n```\n\n4. **Delete Database:**\n```sql\nDROP DATABASE SchoolDB;\n```",
        "cat": "DDL"
    },
    {
        "q": "How do you view table structure and table lists in MySQL?",
        "a": "To view tables in the active database:\n\n1. **List all tables:**\n```sql\nSHOW TABLES;\n```\n\n2. **Describe table schema (columns, types, constraints):**\n```sql\nDESCRIBE Student;\n-- Or shorthand:\nDESC Student;\n```",
        "cat": "DDL"
    },
    {
        "q": "How do you use the ALTER TABLE statement in SQL to add, modify, or drop columns?",
        "a": "The `ALTER TABLE` statement modifies existing table structures:\n\n1. **Add a new column:**\n```sql\nALTER TABLE Student ADD Email VARCHAR(100);\n```\n\n2. **Modify existing column datatype/constraint:**\n```sql\nALTER TABLE Student MODIFY Name VARCHAR(80) NOT NULL;\n```\n\n3. **Drop a column:**\n```sql\nALTER TABLE Student DROP COLUMN Email;\n```\n\n4. **Add Primary Key Constraint:**\n```sql\nALTER TABLE Student ADD PRIMARY KEY (RollNo);\n```",
        "cat": "DDL"
    },
    {
        "q": "What is the difference between DROP TABLE and TRUNCATE TABLE in SQL?",
        "a": "- **`DROP TABLE`:** Completely removes the table structure along with all data, indexes, and triggers from the database.\n```sql\nDROP TABLE Student;\n```\n- **`TRUNCATE TABLE`:** Deletes all rows inside the table quickly, resetting auto-increment counters, while preserving the table schema and column definitions.\n```sql\nTRUNCATE TABLE Student;\n```",
        "cat": "DDL"
    },

    # 4. DML Commands
    {
        "q": "How do you insert single and multiple rows into a MySQL table using INSERT INTO?",
        "a": "1. **Insert all column values in order:**\n```sql\nINSERT INTO Student \nVALUES (101, 'Aman', 11, '2008-05-12', 'A');\n```\n\n2. **Insert specific columns only:**\n```sql\nINSERT INTO Student (RollNo, Name, Class) \nVALUES (102, 'Priya', 11);\n```\n\n3. **Insert multiple rows in a single query:**\n```sql\nINSERT INTO Student (RollNo, Name, Class) VALUES\n(103, 'Rahul', 11),\n(104, 'Sneha', 12),\n(105, 'Karan', 12);\n```",
        "cat": "DML"
    },
    {
        "q": "How do you update existing records in SQL with the UPDATE statement?",
        "a": "The `UPDATE` statement modifies values in existing rows. Always use a `WHERE` clause to avoid updating all rows in the table.\n\n**Example SQL:**\n```sql\nUPDATE Student\nSET Class = 12, Grade = 'A+'\nWHERE RollNo = 101;\n```\n\n> **Caution:** Omitting the `WHERE` clause updates every record in the entire table.",
        "cat": "DML"
    },
    {
        "q": "How do you delete records using the DELETE FROM statement in SQL?",
        "a": "The `DELETE FROM` statement removes specific rows matching a condition.\n\n**Example SQL:**\n```sql\nDELETE FROM Student\nWHERE RollNo = 105;\n```\n\n**Delete all rows (preserving table structure):**\n```sql\nDELETE FROM Student;\n```",
        "cat": "DML"
    },

    # 5. DQL, Filtering, Operators
    {
        "q": "How does the SELECT DISTINCT clause work in SQL?",
        "a": "The `SELECT DISTINCT` clause eliminates duplicate rows from the query result, returning only unique values.\n\n**Example SQL:**\n```sql\nSELECT DISTINCT City \nFROM Student;\n```",
        "cat": "DQL"
    },
    {
        "q": "Explain SQL comparison and logical operators with examples.",
        "a": "SQL uses comparison and logical operators in `WHERE` clauses:\n\n**Comparison Operators:**\n- `=`, `!=` or `<>` (Not equal), `<`, `>`, `<=`, `>=`\n\n**Logical Operators:**\n- **`AND`:** Both conditions must evaluate to true.\n```sql\nSELECT * FROM Student WHERE Class = 11 AND Marks > 80;\n```\n- **`OR`:** At least one condition must evaluate to true.\n```sql\nSELECT * FROM Student WHERE City = 'Delhi' OR City = 'Mumbai';\n```\n- **`NOT`:** Negates a condition.\n```sql\nSELECT * FROM Student WHERE NOT (Class = 10);\n```",
        "cat": "DQL"
    },
    {
        "q": "How do BETWEEN and IN operators simplify SQL queries?",
        "a": "- **`BETWEEN ... AND ...`:** Filters values within an inclusive range (inclusive of boundary values).\n```sql\nSELECT * FROM Student \nWHERE Marks BETWEEN 70 AND 90;\n```\n\n- **`IN (...)`:** Checks if a value matches any item in a specified list.\n```sql\nSELECT * FROM Student \nWHERE City IN ('Delhi', 'Pune', 'Bangalore');\n```\n\n- **`NOT IN (...)`:** Rejects records matching any item in the list.",
        "cat": "DQL"
    },
    {
        "q": "How does pattern matching work with LIKE and wildcard characters in SQL?",
        "a": "The `LIKE` operator performs pattern matching on text strings using two wildcards:\n1. **`%` (Percent):** Matches zero, one, or multiple characters.\n2. **`_` (Underscore):** Matches exactly one single character.\n\n**Examples:**\n```sql\n-- Names starting with 'A':\nSELECT * FROM Student WHERE Name LIKE 'A%';\n\n-- Names ending with 'a':\nSELECT * FROM Student WHERE Name LIKE '%a';\n\n-- Names having exactly 4 characters:\nSELECT * FROM Student WHERE Name LIKE '____';\n\n-- Names where 2nd letter is 'a':\nSELECT * FROM Student WHERE Name LIKE '_a%';\n```",
        "cat": "DQL"
    },
    {
        "q": "How do you handle NULL values in SQL using IS NULL and IS NOT NULL?",
        "a": "In SQL, `NULL` represents missing or unknown data. You cannot compare `NULL` using standard `=` or `!=` operators (e.g. `WHERE col = NULL` always yields false/unknown). Instead, use `IS NULL` or `IS NOT NULL`.\n\n**Example SQL:**\n```sql\n-- Retrieve students who do not have an email assigned:\nSELECT Name, RollNo \nFROM Student \nWHERE Email IS NULL;\n\n-- Retrieve students with valid email addresses:\nSELECT Name, Email \nFROM Student \nWHERE Email IS NOT NULL;\n```",
        "cat": "DQL"
    },
    {
        "q": "How do you sort query results using ORDER BY in SQL?",
        "a": "The `ORDER BY` clause sorts the result set in ascending (`ASC`, default) or descending (`DESC`) order by one or more columns.\n\n**Example SQL:**\n```sql\n-- Sort by Marks descending, then by Name ascending:\nSELECT Name, Marks \nFROM Student \nORDER BY Marks DESC, Name ASC;\n```",
        "cat": "DQL"
    },

    # 6. Aggregate Functions and Grouping
    {
        "q": "What are the standard SQL aggregate functions and how do they handle NULL values?",
        "a": "SQL aggregate functions calculate a single summary value from a set of column values:\n\n1. **`COUNT(*)`:** Counts all returned rows including `NULL` values.\n2. **`COUNT(column)`:** Counts non-NULL entries in the specified column.\n3. **`SUM(column)`:** Calculates the total sum of numeric values (ignores `NULL`s).\n4. **`AVG(column)`:** Computes the arithmetic mean of numeric values (ignores `NULL`s).\n5. **`MIN(column)`:** Finds the minimum value.\n6. **`MAX(column)`:** Finds the maximum value.\n\n**Example SQL:**\n```sql\nSELECT COUNT(*) AS TotalStudents, AVG(Marks) AS AverageMarks, MAX(Marks) AS TopScore \nFROM Student;\n```",
        "cat": "Aggregate Functions"
    },
    {
        "q": "How do GROUP BY and HAVING clauses work together in SQL?",
        "a": "- **`GROUP BY`:** Groups rows sharing identical values in specified columns so aggregate functions can compute metrics per group.\n- **`HAVING`:** Filters aggregated groups *after* grouping is applied. (`WHERE` filters rows *before* aggregation).\n\n**Example SQL:**\n```sql\n-- Find classes with more than 30 students and an average marks above 75:\nSELECT Class, COUNT(*) AS TotalStudents, AVG(Marks) AS AvgMarks\nFROM Student\nWHERE AttendancePercentage >= 75\nGROUP BY Class\nHAVING COUNT(*) > 30;\n```",
        "cat": "Aggregation & Grouping"
    },
    {
        "q": "What is the difference between WHERE and HAVING in SQL?",
        "a": "| Feature | `WHERE` Clause | `HAVING` Clause |\n| :--- | :--- | :--- |\n| **Application** | Filters individual records/rows. | Filters summary groups. |\n| **Timing** | Executed *before* `GROUP BY` aggregation. | Executed *after* `GROUP BY` aggregation. |\n| **Aggregates** | Cannot use aggregate functions (`WHERE AVG(score) > 50` is invalid). | Can use aggregate functions (`HAVING AVG(score) > 50`). |\n| **Usage** | Can be used without `GROUP BY`. | Typically used alongside `GROUP BY`. |",
        "cat": "Aggregation & Grouping"
    },

    # 7. Joins and Multi-Table Queries
    {
        "q": "What is a Cartesian Product (Cross Join) in SQL?",
        "a": "A Cartesian Product (or `CROSS JOIN`) combines every row from the first table with every row from the second table. If Table A has $M$ rows and Table B has $N$ rows, the Cartesian product produces $M \\times N$ rows.\n\n**Example SQL:**\n```sql\nSELECT * FROM Student, Attendance;\n-- Or explicitly:\nSELECT * FROM Student CROSS JOIN Attendance;\n```",
        "cat": "Joins"
    },
    {
        "q": "What is an Equi-Join in SQL and how is it written?",
        "a": "An **Equi-Join** joins tables based on an equality condition between matching columns (usually primary and foreign keys).\n\n**Example SQL:**\n```sql\nSELECT s.RollNo, s.Name, a.AttendanceDate, a.Status\nFROM Student s\nJOIN Attendance a ON s.RollNo = a.RollNo\nWHERE a.Status = 'Present';\n```",
        "cat": "Joins"
    }
]

# Generate variations and additions from the raw textbook text
for spec in pdf3_qa_specs:
    add_qa(spec["q"], spec["a"], spec["cat"])

# Let's add additional focused problem-solving SQL Q&A pairs from keip108 exercises
additional_exercises = [
    {
        "q": "Write a SQL query to display the names of students whose names start with 'S' and end with 'a'.",
        "a": "```sql\nSELECT Name \nFROM Student \nWHERE Name LIKE 'S%a';\n```",
        "cat": "SQL Query"
    },
    {
        "q": "Write a SQL query to calculate the total salary and average salary for each department from the Employee table.",
        "a": "```sql\nSELECT Department, SUM(Salary) AS TotalSalary, AVG(Salary) AS AvgSalary\nFROM Employee\nGROUP BY Department;\n```",
        "cat": "SQL Query"
    },
    {
        "q": "Write a SQL query to display employee details who joined between '2023-01-01' and '2023-12-31' ordered by joining date.",
        "a": "```sql\nSELECT EmployeeID, Name, JoinDate, Salary \nFROM Employee \nWHERE JoinDate BETWEEN '2023-01-01' AND '2023-12-31'\nORDER BY JoinDate ASC;\n```",
        "cat": "SQL Query"
    },
    {
        "q": "Write a SQL query to count the number of students in each grade where the student count is greater than 5.",
        "a": "```sql\nSELECT Grade, COUNT(*) AS StudentCount\nFROM Student\nGROUP BY Grade\nHAVING COUNT(*) > 5;\n```",
        "cat": "SQL Query"
    },
    {
        "q": "How do you add a UNIQUE constraint to an existing column 'AadhaarNo' in the Student table?",
        "a": "```sql\nALTER TABLE Student \nADD CONSTRAINT uq_student_aadhaar UNIQUE (AadhaarNo);\n```",
        "cat": "DDL"
    },
    {
        "q": "Write a SQL statement to increase the salary of all employees in the 'Engineering' department by 10%.",
        "a": "```sql\nUPDATE Employee\nSET Salary = Salary * 1.10\nWHERE Department = 'Engineering';\n```",
        "cat": "DML"
    },
    {
        "q": "Write a SQL query to find all students who have not been assigned a stream (Stream is NULL).",
        "a": "```sql\nSELECT RollNo, Name \nFROM Student \nWHERE Stream IS NULL;\n```",
        "cat": "SQL Query"
    },
    {
        "q": "Write a SQL query to display the 5 highest-earning employees from the Employee table.",
        "a": "```sql\nSELECT Name, Department, Salary\nFROM Employee\nORDER BY Salary DESC\nLIMIT 5;\n```",
        "cat": "SQL Query"
    }
]

for ex in additional_exercises:
    add_qa(ex["q"], ex["a"], ex["cat"])

# Let's create variations to enrich training diversity
variations = []
for item in qa_dataset:
    # Paraphrased version
    p_q = item["question"]
    if "What is" in p_q:
        p_q2 = p_q.replace("What is", "Explain the concept of")
    elif "How do you" in p_q:
        p_q2 = p_q.replace("How do you", "Explain how to")
    elif "Write a SQL query to" in p_q:
        p_q2 = p_q.replace("Write a SQL query to", "Provide a SQL statement to")
    else:
        p_q2 = f"Can you explain {p_q.lower()}?"

    if p_q2 != item["question"]:
        variations.append({
            "question": p_q2,
            "answer": item["answer"],
            "text": f"### Question:\n{p_q2}\n\n### Answer:\n{item['answer']}",
            "source": item["source"],
            "category": item["category"]
        })

qa_dataset.extend(variations)

def generate_pdf_3_samples():
    """Returns standardized training sample dicts for process_sql_data pipeline."""
    samples = []
    for item in qa_dataset:
        samples.append({
            "instruction": item["question"],
            "response": item["answer"],
            "output": item["answer"],
            "domain": "sql",
            "task": "pdf_qa",
            "source": "NCERT_SQL_ClassXI_keip108"
        })
    return samples

if __name__ == "__main__":
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for row in qa_dataset:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[+] Successfully generated {len(qa_dataset)} Q&A pairs in {OUTPUT_JSONL}")

