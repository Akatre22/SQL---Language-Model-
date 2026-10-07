# Product Blueprint: Universal Data & BI Intelligence Studio
**Platform Code Name:** DataForge AI / RelationalOS  
**Core Engine:** Domain-Specialized SQL & Metadata Transformer (5.4M Parameters)  
**Deployment Tier:** On-Premises / Air-Gapped Private Cloud / Lakehouse Native  

---

## 1. Executive Summary & Product Vision

Enterprises struggle with fragmented tooling across the modern data stack. Data engineers write glue code for Snowflake and Databricks, analytics engineers build fragile dbt transformations, DBAs tune queries manually, and BI analysts struggle with DAX, LOD expressions, and dashboard formatting. Sending enterprise schemas and sensitive data to general-purpose cloud LLMs (GPT-4 / Claude) creates severe compliance risks, latency bottlenecks (2–5s), and unpredictable token costs.

**Universal Data & BI Intelligence Studio** is an all-in-one on-premise intelligence layer that connects directly to enterprise data sources (Snowflake, Databricks, PostgreSQL, BigQuery, SQL Server). Powered by a specialized **5.4M parameter Transformer**, it automates the full lifecycle of data work: **automated schema understanding**, **lakehouse engineering & pipeline generation**, **self-healing analytical SQL**, and **conversational BI report design**.

```
+-----------------------------------------------------------------------------+
|               UNIVERSAL DATA & BI INTELLIGENCE STUDIO (DataOS)              |
+-----------------------------------------------------------------------------+
                                       |
    +-------------------+-------------------+-------------------+-------------------+
    |                   |                   |                   |                   |
[1. SCHEMA ENGINE]  [2. DATA ENGINEERING] [3. ANALYTICS & SQL][4. BI & DASHBOARDS]
Auto Metadata Graph Snowflake Snowpark / Tasks Complex CTE Queries Vega-Lite / WebGL
PII Tagging & Dict  Databricks Delta / PySpark AST Verification    Power BI DAX / Tab
Lineage Tracking    dbt Models & Airflow DAGs  Self-Healing Errors  KPI Driver Analysis
```

---

## 2. The 4 Core Architectural Pillars

### Pillar 1: Schema Understanding & Semantic Knowledge Graph
* **Automatic Metadata Ingestion:** Connects via read-only credentials to catalog tables, column data types, foreign keys, partition keys, and primary indices.
* **Smart Data Dictionary Generation:** Automatically infers and documents cryptic column names (e.g., `cust_ltv_adj_v2` $\rightarrow$ "Customer Lifetime Value adjusted for churn rate v2").
* **Automated PII & Compliance Tagging:** Identifies sensitive entities (SSN, credit card, email, patient IDs) and marks columns with governance classifications.
* **Lineage & Dependency Graph:** Traces upstream sources and downstream consumers. Immediately alerts engineers if modifying a column breaks a dbt model or executive dashboard.

### Pillar 2: Lakehouse & Data Engineering Automation
* **Snowflake Native Automation:**
  * Generates Snowpark Python and SQL stored procedures.
  * Writes declarative Dynamic Tables, Task orchestrations, and Streams.
  * Recommends optimal Clustering Keys and auto-detects idle Virtual Warehouses.
* **Databricks & Spark Automation:**
  * Generates PySpark transformations and optimized SQL queries.
  * Produces Delta Lake maintenance commands (`OPTIMIZE`, `Z-ORDER BY`).
  * Scaffold Medallion Architecture pipelines (Bronze raw ingestion $\rightarrow$ Silver cleaned $\rightarrow$ Gold business aggregates).
* **dbt & Airflow Pipeline Synthesis:**
  * Compiles complete dbt models with Jinja templating, `schema.yml` test suites, and documentation.
  * Produces production-ready Apache Airflow DAG definitions with sensor dependencies.

### Pillar 3: Deterministic Analytics & Self-Healing Query Engine
* **High-Precision Multi-Table SQL:** Synthesizes complex analytical queries with window functions, recursive CTEs, and mathematical pivots.
* **Deterministic AST Verification:** Routes every generated query through `sqlglot` semantic parsers to ensure 100% syntax compliance before database submission.
* **Self-Healing Error Recovery:** If a query fails during execution, the studio analyzes the database engine's error log, cross-references table schemas, rewrites the query, and re-executes automatically in `< 15ms`.

### Pillar 4: Conversational BI & Automated Report Synthesis
* **Zero-Code Interactive Charts:** Translates natural business questions into declarative Vega-Lite and Plotly JSON dashboard specifications rendered client-side via WebGL.
* **Native BI Tool Code Generation:**
  * Power BI: Generates complex DAX measures and Power Query M scripts.
  * Tableau: Generates Level of Detail (LOD) calculations and custom SQL data sources.
* **Automated KPI Variance & Root-Cause Analysis:** Decomposes revenue or churn fluctuations across dimensions (e.g., "Why did gross margins decrease 4.3% in EMEA during Q3?").

---

## 3. Technical Architecture & Data Flow

```
[ Data Sources ]
(Snowflake / Databricks / Postgres / BigQuery)
       |
       v  (Read-Only Metadata & Information Schema)
+-------------------------------------------------------------+
| IN-MEMORY SCHEMA KNOWLEDGE GRAPH & DIALECT TRANSPILER       |
+-------------------------------------------------------------+
       |
       +---> [ Domain BPE Tokenizer (4,096 Relational Vocab) ]
       |
       v
+-------------------------------------------------------------+
| 5.4M DOMAIN-SPECIALIZED DECODER TRANSFORMER                 |
| (RMSNorm, RoPE, 8-Head Causal Attention, SwiGLU FFN)        |
+-------------------------------------------------------------+
       |
       v
+-------------------------------------------------------------+
| DETERMINISTIC AST VALIDATION & COMPILER ENGINE (sqlglot)    |
+-------------------------------------------------------------+
       |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
[ Lakehouse Tasks ]  [ SQL Execution ]    [ BI Dashboard Spec ]
(Snowpark / Delta)   (Verified Queries)   (Vega-Lite / DAX)
```

---

## 4. Key Engineering Specifications

| Specification | Dimension / Value | Rationale |
| :--- | :--- | :--- |
| **Model Size** | 5.4M Parameters | Ultra-lightweight; runs on CPU workstations / standard containers. |
| **Memory Footprint** | < 35 MB RAM | Zero dedicated GPU requirement; deploys inside existing infra. |
| **Inference Latency** | < 12 ms | Instant keystroke autocompletion and rapid conversational feedback. |
| **Dialect Coverage** | Snowflake, Databricks, Postgres, BigQuery, T-SQL, Oracle | Multi-engine AST normalization using sqlglot. |
| **Security & Privacy** | 100% On-Premises (Air-Gapped) | Zero external cloud API calls; absolute data sovereignty. |
| **Cost Model** | Constant Baseline ($X / month flat) | Zero per-token or variable metering fees. |

---

## 5. Enterprise Business Impact & ROI

1. **80% Faster BI & Pipeline Development:** Data analysts and engineers generate validated queries, dbt models, and dashboards in seconds rather than hours.
2. **Zero Outages from Schema Drift:** Continuous AST analysis prevents broken downstream pipelines and corrupted dashboards.
3. **100% Data Sovereignty:** Highly regulated banks, healthcare institutions, and defense contractors can deploy state-of-the-art GenAI intelligence without violating privacy policies.
4. **Predictable Cloud Spend:** Eliminates unpredictable multi-thousand-dollar monthly bills from generalist cloud LLM APIs.
