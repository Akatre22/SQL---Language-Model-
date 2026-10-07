# 📊 NICE Tiny LLM — Benchmark Evaluation Report

**Date:** `2026-09-24 14:11:32`  
**Total Questions:** `22`  

## 🚀 Summary Metrics

- **Avg Domain Term Coverage:** `18.41%`
- **SQL Syntax Validity Rate:** `0.0%` (10 SQL test cases)
- **SQL Sandbox Execution Rate:** `0.0%`
- **Avg Inference Latency:** `0.497s` per response on CPU

## 📈 Performance Breakdown by Domain

| Domain | Total Questions | Term Coverage (%) | SQL Syntax Pass (%) | SQL Execution Pass (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Sql** | 22 | 18.4% | 0.0% | 0.0% |

## 🔍 Sample Benchmark Outputs

### `SQL-001`: What is an INNER JOIN in SQL and when would you use it?
**Domain:** `sql` | **Keyword Coverage:** `20.0%`

> A LEFT JOIN on a single query execution p.

---
### `SQL-002`: Write a SQL query to join the 'customers' and 'orders' tables on customer_id to get customer name and total amount.
**Domain:** `sql` | **Keyword Coverage:** `50.0%`

> ```sql
> SELECT * FROM customers WHERE grade = 'VIP';
> ```

**SQL Evaluation:** Syntax Valid: `False`, Executable: `False`

---
### `SQL-003`: Write a SQL query using a LEFT JOIN anti-pattern to find all customers who have never placed an order.
**Domain:** `sql` | **Keyword Coverage:** `50.0%`

> ```sql
> SELECT c.customer_id, o.order_number, o.total_amount FROM orders o INNER JOIN orders o ON o.customer_id = o.customer_id WHERE o.status NOT IN ('cancelled', 'returned') AND o.ordered_at < '2024-01-01' AND o.status NOT IN ('cancelled')
> GROUP BY c.name;
> ```

**SQL Evaluation:** Syntax Valid: `False`, Executable: `False`

---
### `SQL-004`: Write a SQL query to calculate the total order amount and average order amount per customer.
**Domain:** `sql` | **Keyword Coverage:** `60.0%`

> ```sql
> SELECT c.customer_id, o.order_number, o.total_amount FROM orders AS o ON o.customer_id = o.customer_id WHERE o.status NOT IN ('cancelled')
> GROUP BY o.ordered_at DESC;
> ```
> 
> **Explanation:**
> - Joins `orders` on `customers` table.

**SQL Evaluation:** Syntax Valid: `False`, Executable: `False`

---
### `SQL-005`: Write a SQL query to find product categories with an average price greater than 50 using the HAVING clause.
**Domain:** `sql` | **Keyword Coverage:** `50.0%`

> ```sql
> SELECT name, email, grade
> FROM products;
> ```

**SQL Evaluation:** Syntax Valid: `False`, Executable: `False`

---
