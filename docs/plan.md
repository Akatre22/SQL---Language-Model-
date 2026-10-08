Project: NICE Tiny Data & AI LLM
The goal

Build a small domain-specific language model from scratch, initially around 250K–500K parameters, eventually targeting ~1M parameters, specialized in:

Enterprise Data Engineering + SQL + BI + GenAI

It should run locally first, have a Streamlit interface, and eventually be deployable as an API on a VM.

1. What exactly are we building?

Don't start with:

"NICE's own ChatGPT."

That's far too ambitious for 1M parameters.

Instead:

A tiny language model that understands the terminology, syntax, patterns and basic reasoning associated with NICE's Data & AI engineering work.

Initial capabilities:

SQL
Explain SQL
Generate simple SQL
Complete SQL
Identify SQL concepts
Explain joins
Explain aggregations
Explain window functions
Data Engineering
ETL / ELT
Data pipelines
Data warehouses
Data lakes
Data modeling
Data quality
Data validation
Orchestration
Snowflake
Warehouses
Schemas
Tables
Stages
Streams
Tasks
Snowpipe
SQL
Performance concepts

NICE publicly positions Snowflake as a major capability, including implementation, migration, data engineering and Cortex/GenAI use cases.

Databricks
Spark
Delta Lake
Lakehouse
Unity Catalog
MLflow
ETL
Batch
Streaming
SQL

These align with NICE's current Databricks positioning.

BI
Power BI
DAX
Measures
Dimensions
Facts
KPIs
Dashboards
Semantic models
Reports
GenAI
LLM
Prompt engineering
Embeddings
Vector databases
RAG
Agents
Chunking
Retrieval
Evaluation
Structured output
2. The complete project architecture

Eventually:

                         NICE Tiny AI
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
          Tiny LLM        Knowledge DB      Application
         ~1M params          │              Streamlit
              │              │
              │        ┌─────┴─────┐
              │        │           │
              │       SQL         Docs
              │        │           │
              └────────┴───────────┘
                       │
                       ▼
                    Answer

But we will NOT build all of this initially.

We'll build it in stages.

3. Phase 0 — Define the scope

Before writing Python, freeze the initial scope.

V0.1 domains

I'd use:

Domain	Priority
SQL	Very High
Data Engineering	Very High
Snowflake	High
Databricks	High
BI / Power BI	High
GenAI / RAG	Medium
DAX	Medium
Python for Data Engineering	Medium
AWS/Azure/GCP	Later
Industry-specific knowledge	Later

Don't put 50 technologies into V0.1.

4. Phase 1 — Build the dataset

This is probably the most important part of the project.

Don't immediately start scraping the internet.

We want high-quality domain data.

I would create four sources.

Source A — Public NICE material

Use publicly available NICE material such as:

NICE website
Technology pages
Data engineering pages
Snowflake pages
Databricks pages
AI pages
Blog articles
Public case studies
Public brochures
Public technical material

For example, NICE publicly describes data engineering capabilities around automated pipelines, transformation logic, schema design, performance optimization and governance.

That gives us NICE-specific terminology and positioning.

Important

Don't blindly copy website content into training.

Instead:

Public NICE material
        ↓
Extract concepts
        ↓
Create structured knowledge
        ↓
Generate training examples
5. Source B — General technical knowledge

We need significantly more technical material than NICE's website alone can provide.

For example:

SQL

Create material around:

SELECT
WHERE
GROUP BY
ORDER BY
JOIN
UNION
CTE
Subquery
Window functions
CASE
Aggregation
Indexes
Views
Stored procedures
Data Engineering
ETL
ELT
CDC
Batch processing
Streaming
Data lake
Data warehouse
Lakehouse
Data modeling
Star schema
Snowflake schema
SCD
Data quality
Orchestration
Snowflake
Database
Schema
Warehouse
Stage
Table
View
Streams
Tasks
Snowpipe
Time Travel
Zero-copy cloning
Databricks
Spark
DataFrame
Delta Lake
Lakehouse
Unity Catalog
MLflow
Jobs
Notebooks
Structured Streaming
GenAI
Transformer
Tokenization
Embedding
Vector DB
RAG
Chunking
Retriever
Reranker
Agent
Tool calling
Evaluation
6. Source C — Synthetic training data

This will be extremely important for a tiny model.

We can generate training examples programmatically.

For example, one concept:

SQL JOIN

can produce:

Question:
What is an INNER JOIN?

Answer:
An INNER JOIN returns rows where matching values exist in both tables.

Then:

Question:
Explain INNER JOIN in simple terms.

Answer:
It returns records that have matching values in both tables.

Then:

Question:
When would you use INNER JOIN?

Answer:
Use it when you only want records that exist in both datasets.

And:

SQL:
SELECT *
FROM customers c
JOIN orders o
ON c.id = o.customer_id;

Generate hundreds of variations around the same concept.

7. Source D — NICE internal knowledge

This could become the most valuable dataset, but only if NICE authorizes its use.

Potential sources:

Internal documentation
Project architecture documents
Technical SOPs
Reusable SQL patterns
Data engineering standards
Deployment standards
Anonymized project examples
Troubleshooting guides
Internal FAQs
Architecture templates

But:

Do NOT put client confidential information into the training dataset.

Especially:

Client names
Credentials
Passwords
API keys
Production SQL containing sensitive information
PII
Customer data
Confidential architecture
Contracts
Internal secrets

Instead:

Real project
    ↓
Anonymize
    ↓
Generalize
    ↓
Training example

For example:

BAD:

SELECT * FROM EmiratesBankCustomerTransactions...


GOOD:

SELECT customer_id, SUM(amount)
FROM transactions
GROUP BY customer_id;
8. Create a proper data repository

Don't throw everything into training.txt.

Use:

dataset/
│
├── raw/
│   ├── nice_public/
│   ├── technical/
│   └── synthetic/
│
├── processed/
│
├── instruction/
│
├── validation/
│
└── test/

Eventually:

dataset/
│
├── sql/
├── data_engineering/
├── snowflake/
├── databricks/
├── powerbi/
├── dax/
├── genai/
└── python/
9. Create your training format

For the first model, I recommend plain text / instruction-response examples.

Example:

{
  "instruction": "Explain what ETL means.",
  "response": "ETL stands for Extract, Transform and Load..."
}

Another:

{
  "instruction": "What is a Snowflake warehouse?",
  "response": "A Snowflake virtual warehouse provides compute resources..."
}

Another:

{
  "instruction": "Write SQL to calculate total sales by region.",
  "response": "SELECT region, SUM(sales) FROM sales GROUP BY region;"
}
10. Build the dataset generator

This becomes one of your Python projects.

data_generator.py

It should create:

concept
    ↓
definition
    ↓
questions
    ↓
answers
    ↓
examples
    ↓
variations

For example:

Concept = "CTE"

Generate:

What is a CTE?
Explain CTE.
Why use CTE?
Show a CTE example.
When should I use CTE?
CTE vs subquery.
...

This can produce thousands of training samples.

11. But don't generate everything with an LLM blindly

This is important.

If you use GPT/Claude/etc. to generate your dataset, you'll introduce errors.

So use:

Generation
    ↓
Validation
    ↓
Deduplication
    ↓
Quality check
    ↓
Final dataset

For SQL:

Generated SQL
     ↓
SQL parser
     ↓
Syntax validation
     ↓
Valid?
 ┌───┴───┐
Yes      No
 ↓        ↓
Keep    Reject
12. Dataset size

For the first experiment, don't chase millions of examples.

Start with:

5,000 examples

Then:

10,000

Then:

25,000

Then:

50,000+

The important thing is quality and diversity, not just the number.

13. Phase 2 — Tokenizer

Now we actually start building the LLM.

We'll create our own tokenizer.

For example:

"Snowflake warehouse"

becomes something like:

["Snow", "flake", "warehouse"]

or token IDs:

[421, 928, 1732]

For our domain, tokenizer vocabulary should handle:

SQL
Python
Snowflake
Databricks
DAX
JSON
RAG
API
ETL
ELT

This is especially important because technical terminology has lots of unusual tokens.

14. Phase 3 — Build the tiny Transformer

Now we write the actual LLM.

Don't use an existing 7B model.

Build a small Transformer ourselves using PyTorch.

Initial target:

~250K parameters

Something like:

Embedding dimension: 128
Layers:              4
Attention heads:     4
FFN dimension:       512
Context length:      256
Vocabulary:          ~4K–8K

We'll calculate the exact architecture to hit the target parameter count.

15. What the model learns

Initially:

SQL
SQL
SQL
JOIN
JOIN
Snowflake
Snowflake

Then:

What is SQL?

The model learns patterns such as:

What is X?
        ↓
X is...

Eventually:

What is a Snowflake warehouse?

could produce something resembling:

A Snowflake warehouse provides compute resources...

Don't expect ChatGPT-level quality.

The objective of V0.1 is:

Prove that our own Transformer learns the NICE domain.

16. Phase 4 — Training

Pipeline:

Dataset
   ↓
Tokenizer
   ↓
Token IDs
   ↓
Training sequences
   ↓
Tiny Transformer
   ↓
Forward pass
   ↓
Loss
   ↓
Backpropagation
   ↓
Optimizer
   ↓
Updated weights
   ↓
Repeat

Use:

Python
PyTorch
NumPy

Initially, CPU is fine if the model and dataset are tiny.

A GPU will become useful as we scale.

17. Track experiments properly

Create:

experiments/
│
├── exp_001/
├── exp_002/
├── exp_003/
└── exp_004/

Track:

model size
dataset size
learning rate
batch size
epochs
training loss
validation loss
generation samples
training time

Example:

Experiment	Params	Data	Val Loss
E001	250K	5K	...
E002	250K	10K	...
E003	500K	10K	...
E004	1M	25K	...

This turns the project into an actual ML experiment rather than just a demo.

18. Phase 5 — Evaluation

This is where your project becomes much more impressive.

Create a NICE benchmark.

For example:

SQL

100 questions.

"Explain GROUP BY"
"Write a JOIN"
"Explain CTE"
"Create aggregation"
Snowflake

100 questions.

Databricks
Data Engineering
BI
GenAI

Total:

600-question benchmark

Then test every model version against exactly the same benchmark.

19. Evaluate more than loss

Track:

Language quality
Perplexity
Validation loss
SQL
Syntax correctness
Execution correctness
Classification
Accuracy
Precision
Recall
Retrieval later

For the RAG version:

Hit Rate
MRR
NDCG

This is particularly useful because you already care about retrieval evaluation.

20. Phase 6 — Streamlit application

Once the model works locally:

Streamlit
     ↓
Python inference
     ↓
Tiny NICE LLM

UI:

┌──────────────────────────────────────────┐
│ NICE Tiny Data AI                       │
├──────────────────────────────────────────┤
│                                          │
│ Ask a Data / AI question                 │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Explain Snowflake streams            │ │
│ └──────────────────────────────────────┘ │
│                                          │
│              [Generate]                  │
│                                          │
│ Response                                 │
│ ──────────────────────────────────────── │
│ Snowflake streams capture...             │
│                                          │
└──────────────────────────────────────────┘

No API initially.

Everything runs locally.

21. Phase 7 — Add database

Only after the basic LLM works.

Create:

PostgreSQL

or initially:

SQLite

Schema:

knowledge
────────────────────────
id
domain
topic
title
content
source
version
created_at

Example:

domain = snowflake
topic = streams
content = ...
source = approved_document
22. Now combine LLM + DB

This is where the architecture we discussed earlier becomes useful.

User
 ↓
Tiny LLM
 ↓
Understand question
 ↓
Search Knowledge DB
 ↓
Retrieve relevant information
 ↓
Tiny LLM
 ↓
Generate response

This is essentially a tiny domain-specific RAG system.

23. But don't let the tiny LLM hallucinate database answers

For factual questions:

"What is Snowflake Time Travel?"

Prefer:

Question
 ↓
Retrieve source
 ↓
Provide context
 ↓
Generate answer

rather than:

Question
 ↓
LLM memory
 ↓
Answer

This is particularly important because a 1M model will have limited capacity.

24. Phase 8 — Add NICE-specific knowledge

Now we can introduce:

NICE terminology
NICE service categories
NICE technology stack
NICE architecture patterns
NICE reusable practices

Subject to internal approval.

For example:

Question:

Which technologies are commonly used in NICE
data engineering solutions?


The system can retrieve approved NICE knowledge and answer from it.

NICE's public technology pages currently describe its Data Intelligence, Decision Intelligence and AI capabilities and list technologies/platforms including Snowflake and Databricks.

25. Phase 9 — Add SQL execution

This would make the project much more useful.

Architecture:

User
 ↓
Tiny LLM
 ↓
Generate SQL
 ↓
SQL Validator
 ↓
Database
 ↓
Execute
 ↓
Result
 ↓
Tiny LLM
 ↓
Explain result

Example:

"Give me sales by region."

Tiny LLM
    ↓
SELECT region, SUM(sales)
FROM sales
GROUP BY region;
    ↓
Validator
    ↓
Database
    ↓
Result

Now you've moved from:

LLM demo

to:

Data Engineering AI system.

26. Phase 10 — Add Snowflake

Eventually:

Tiny LLM
     ↓
SQL generation
     ↓
SQL validation
     ↓
Snowflake
     ↓
Result
     ↓
Natural language explanation

This fits particularly well with NICE's current Snowflake work, including data engineering, migration/modernization and AI-powered SQL/data processing.

27. Phase 11 — Add Databricks

Then:

Tiny LLM
     ↓
Understand request
     ↓
Generate SQL / Spark
     ↓
Databricks
     ↓
Result

Potential capabilities:

Generate Spark SQL
Explain Spark code
Explain Delta tables
Explain Lakehouse architecture
Explain Unity Catalog
Generate basic PySpark
28. Phase 12 — API

Once Streamlit works:

Streamlit
     ↓
FastAPI
     ↓
Tiny LLM

API:

POST /generate
POST /sql
POST /search
POST /explain
29. Phase 13 — VM deployment

Now take exactly what works locally:

Your Laptop
    ↓
Docker
    ↓
VM
    ↓
FastAPI
    ↓
API

Then:

yourwebsite.com
       ↓
api.yourwebsite.com
       ↓
VM
       ↓
Tiny NICE LLM
30. Final architecture

Eventually:

                         USER
                           │
                           ▼
                     NICE AI UI
                           │
                           ▼
                        FastAPI
                           │
               ┌───────────┴───────────┐
               │                       │
               ▼                       ▼
          Tiny LLM                 Knowledge DB
          ~1M params                    │
               │                  ┌─────┴─────┐
               │                  │           │
               │               NICE Docs   Technical
               │                           Knowledge
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
      SQL            RAG/Search
       │                │
       ▼                ▼
 Snowflake /       Retrieved
 Databricks         Context
       │                │
       └────────┬───────┘
                ▼
             Response
31. Recommended GitHub structure

I'd make the repository like this:

nice-tiny-llm/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── train/
│   ├── validation/
│   └── test/
│
├── tokenizer/
│   ├── train_tokenizer.py
│   └── tokenizer.json
│
├── model/
│   ├── config.py
│   ├── attention.py
│   ├── transformer.py
│   └── model.py
│
├── training/
│   ├── dataset.py
│   ├── train.py
│   ├── evaluate.py
│   └── checkpoints/
│
├── inference/
│   └── generate.py
│
├── evaluation/
│   ├── benchmark.json
│   ├── evaluate_sql.py
│   └── results/
│
├── knowledge/
│   ├── database.py
│   ├── retrieval.py
│   └── ingestion.py
│
├── app/
│   └── streamlit_app.py
│
├── api/
│   └── main.py
│
├── requirements.txt
├── README.md
└── .gitignore
32. Your first 30 days

I would not try to implement the entire architecture immediately.

Week 1 — Data
Day 1
Define domains

Day 2
Collect SQL material

Day 3
Collect Data Engineering material

Day 4
Collect Snowflake material

Day 5
Collect Databricks material

Day 6
Create synthetic examples

Day 7
Clean + deduplicate

Target:

5,000–10,000 high-quality training samples.

Week 2 — Tokenizer + Model
Day 8
Tokenizer

Day 9
Dataset loader

Day 10
Transformer architecture

Day 11
Forward pass

Day 12
Loss + optimizer

Day 13
Training loop

Day 14
First training run

Target:

~250K model successfully training.

Week 3 — Improve
Day 15
Validation split

Day 16
Generation

Day 17
Fix tokenizer

Day 18
Improve dataset

Day 19
Increase to 500K

Day 20
Compare experiments

Day 21
Evaluation benchmark
Week 4 — Productize
Day 22
Inference pipeline

Day 23
Streamlit UI

Day 24
Knowledge DB

Day 25
Basic retrieval

Day 26
LLM + retrieval

Day 27
SQL generation

Day 28
SQL validation

Day 29
Documentation

Day 30
Demo

At the end of 30 days, the target should be:

                NICE Tiny Data AI v0.1

                   Streamlit
                       │
                       ▼
                Tiny Transformer
                  ~250-500K
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
       Data/SQL QA            Basic RAG
            │                     │
            └──────────┬──────────┘
                       ▼
                    Answer

Not production-ready.

But genuinely your own trained model.

33. What I would NOT do initially

Avoid these until V0.1 works:

❌ 7B model
❌ Fine-tuning Llama
❌ Hugging Face model as the core model
❌ GPU cluster
❌ Kubernetes
❌ Microservices
❌ Agents
❌ Multi-agent system
❌ Voice
❌ Vision
❌ Mobile app
❌ Complex frontend
❌ 100+ technologies

The point of this project is:

Can we actually build and train a small language model ourselves?

Once the answer is yes, everything else becomes an extension.

34. The most important thing: data strategy

For a 1M model, I'd prioritize the data roughly like this:

                Training Data
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   Technical      Synthetic     NICE-specific
   knowledge      examples       knowledge
      40%            40%             20%

And within technical knowledge:

SQL                 25%
Data Engineering    20%
Snowflake           15%
Databricks          15%
BI/Power BI         10%
GenAI/RAG           10%
Python               5%

These percentages are initial design targets, not fixed rules. We should adjust them after evaluating what the model actually learns.

35. One very important corporate consideration

If this becomes an actual NICE internal project, get approval before using internal/client material for model training.

The safest progression is:

PUBLIC DATA
   ↓
SYNTHETIC DATA
   ↓
APPROVED INTERNAL DATA
   ↓
ANONYMIZED PROJECT PATTERNS

Never:

Client production data
       ↓
Training dataset

without explicit authorization.

36. What your final demo could look like

This is the demo I'd ultimately aim for:

NICE Tiny Data AI

User:

Explain what a Snowflake Stream is and
give me a simple example.

System:

Intent detected:
Snowflake → Streams → Explanation

Knowledge retrieved:
3 relevant approved documents

Tiny LLM response:
...

Then:

Generate SQL to calculate monthly revenue by region.

System:

Generated SQL
     ↓
SQL validation
     ↓
Valid
     ↓
Execute against sample DB
     ↓
Result

Then:

Explain this SQL query.

The same tiny model handles it.

That gives you a much stronger story than simply saying "I trained a 1M parameter LLM."

You can demonstrate the entire lifecycle:

Data Engineering → Dataset Creation → Tokenization → Transformer Architecture → Training → Evaluation → RAG → SQL → Streamlit → API → VM Deployment.