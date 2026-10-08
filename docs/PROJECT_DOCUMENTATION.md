# ⚡ Tiny SQL LLM — End-to-End Technical Documentation (A to Z)

---

## 📖 1. Executive Summary & Vision

**Tiny SQL LLM** is an in-house, domain-specialized AI ecosystem designed from scratch to understand, write, explain, optimize, and execute relational SQL queries. 

Unlike generic multi-billion parameter cloud models that suffer from parameter dilution and heavy compute requirements, Tiny SQL LLM combines a **custom-trained 6.16M-parameter Transformer neural network**, **custom Byte-Pair Encoding (BPE) tokenizer**, **persistent ChromaDB vector RAG**, **linguistic NLP intent routing**, and an **autonomous SQLite execution sandbox** to deliver instant, verifiable, and private SQL intelligence on standard local CPU hardware.

---

## 🏛️ 2. System Architecture & Information Flow

```
                                  ┌────────────────────────┐
                                  │   User Prompt / Chat   │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                             ┌──────────────────────────────────┐
                             │    Linguistic NLP Intent Router  │
                             │     (sql_agent/intent_router)    │
                             └────────────────┬─────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
     [TEXT_TO_SQL / ACTION]      [CONCEPT_COMPARISON]       [CONCEPT_EXPLANATION / TUTORIAL]
                    │                         │                         │
                    ▼                         ▼                         ▼
     ┌────────────────────────────┐ ┌───────────────────┐ ┌───────────────────────────┐
     │   Autonomous SQL Agent     │ │ Dynamic Entity    │ │ Pedagogical Synthesizer   │
     │    (sql_agent/agent.py)    │ │ Comparison Engine │ │ (Definition -> Code ->    │
     │  - Schema Prompt Injection │ │ (ChromaDB RAG)    │ │  Execution Rules)         │
     │  - Neural SQL Generation   │ └─────────┬─────────┘ └─────────────┬─────────────┘
     │  - AST Check (sqlglot)     │           │                         │
     │  - Sandbox Execution (DB)  │           └────────────┬────────────┘
     │  - Table Result Formatter  │                        │
     └──────────────┬─────────────┘                        │
                    │                                      │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │ Streamlit Interactive Web App UI  │
                     │  - Formatted Markdown Explanations│
                     │  - Executable SQL Code Snippets   │
                     │  - Interactive Pandas DataFrames  │
                     └───────────────────────────────────┘
```

---

## 🪜 3. Chronological Step-by-Step Development Roadmap (Steps 1 to 10)

Here is the exact sequential engineering process undertaken from start to finish to achieve the specialized **Tiny SQL LLM**:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DEVELOPMENT LIFECYCLE (STEPS 1 TO 10)                            │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Step 1: Raw Data Collection & Mining (Cloned 7 Curated SQL Repositories via Git Ingestor)        │
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 2: Parsing, AST Normalization & Synthetic Data Generation (6,180 Pairs, 4.31 MB Corpus)     │
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 3: Domain Tokenizer Engineering (Custom 4,096-Vocab Byte-Level BPE in Rust/Tokenizers)      │
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 4: Neural Architecture Implementation (Decoder Transformer with RoPE, SwiGLU & RMSNorm)     │
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 5: Pretraining & Optimization (AdamW, Cosine Annealing, Cross-Entropy with Masking)         │
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 6: Knowledge Base Indexing (ChromaDB Vector Store + 384-d Dense MiniLM Embeddings)          │
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 7: Linguistic Intent Routing & Dynamic RAG (Zero-Hardcoding Entity Comparison & Synthesis)  │
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 8: Autonomous SQL Agent & Sandbox Execution (SQLite 7-Table Sandbox + sqlglot AST Validator)│
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 9: Frontend Web Interface (Streamlit Interactive Chat, Schema Explorer, DataFrame Visuals)  │
│    │                                                                                             │
│    ▼                                                                                             │
│ Step 10: Benchmarking & Quantitative Evaluation (22 Multi-Domain Tests, Perplexity & Accuracy)   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 🔹 Step 1: Raw Data Ingestion & GitHub Repository Mining
* **Objective:** Source high-quality, pure SQL code, relational database tutorials, real-world analytical queries, and schema definitions without generic text pollution.
* **Tech Stack:** Python 3.10+, `GitPython`, `subprocess`, GitHub REST API.
* **What We Did:**
  1. Built an automated repository ingestor script: [`data/fetch_github_sql.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/fetch_github_sql.py).
  2. Configured long path support (`git config --system core.longpaths true`) to handle deep nested folders on Windows.
  3. Cloned 7 open-source SQL repositories into `data/raw_repos/`:
     - `mouredev/hello-sql` (Foundations, DDL/DML)
     - `civilian7/sql-tutorial` (30-table realistic e-commerce database, 690K rows, 21 lessons)
     - `DataWithBaraa/sql-ultimate-course` (Analytical queries, aggregations, window functions)
     - `datawithdanny/sql-masterclass` (Complex CTEs, multi-stage pipelines)
     - `btholt/complete-intro-to-sql` (PostgreSQL schemas, constraints, indexing)
     - `Baeldung/sql-tutorials` (Advanced SQL recipes, subqueries, grouping)
     - `academind/sql-complete-guide-code` (Table relationships, foreign keys, views)
* **Output Artifacts:** `data/raw_repos/` with 1,000+ `.sql`, `.md`, and database schema files.

---

### 🔹 Step 2: Data Extraction, Normalization & Synthetic Augmentation
* **Objective:** Convert unstructured Markdown and raw `.sql` files into standardized JSONL instruction-response pairs, plus augment with edge cases (window functions, recursive CTEs, anti-joins).
* **Tech Stack:** Python, `sqlglot` (SQL Abstract Syntax Tree parser), Regular Expressions.
* **What We Did:**
  1. Built [`data/process_sql_data.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/process_sql_data.py):
     - **Markdown Parser:** Scanned headers (`#`, `##`, `###`) as user prompts and paired them with the subsequent ` ```sql ... ``` ` blocks as targets.
     - **SQL Script Parser:** Split `.sql` files by statement terminator `;`, using SQL header comments (`-- ...`) as instructions.
  2. Built [`data/data_generator.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/data_generator.py):
     - Programmatically generated 4,000+ realistic multi-table relational queries across SQLite, PostgreSQL, and MySQL dialects.
     - Formatted each entry into `<|bos|>User: {prompt}\nAssistant: {response}<|eos|>`.
  3. Deduplicated all entries and compiled a continuous text corpus for unsupervised token pretraining.
* **Output Artifacts:**
  - [`data/train.jsonl`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/train.jsonl) (5,562 training samples, 90%)
  - [`data/val.jsonl`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/val.jsonl) (618 validation samples, 10%)
  - [`data/corpus.txt`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/corpus.txt) (4.31 MB raw domain text)

---

### 🔹 Step 3: Custom Domain Byte-Level BPE Tokenizer Training
* **Objective:** Eliminate token fragmentation on SQL reserved words and syntax symbols by training a vocabulary specifically tailored to relational databases.
* **Tech Stack:** Hugging Face `tokenizers` library (Rust backend), Byte-Pair Encoding algorithm.
* **What We Did:**
  1. Built [`tokenizer/train_tokenizer.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/tokenizer/train_tokenizer.py).
  2. Defined 5 essential special tokens: `<|pad|>`, `<|unk|>`, `<|bos|>`, `<|eos|>`, `<|endoftext|>`.
  3. Trained a **4,096-vocabulary Byte-Level BPE** model directly on `data/corpus.txt`.
  4. Wrapped the tokenizer in [`tokenizer/tokenizer.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/tokenizer/tokenizer.py) with helper methods: `encode()`, `decode()`, `pad_sequence()`, and tensor converters.
* **Key Achievement:** Common SQL operators and keywords (`SELECT`, `WHERE`, `PARTITION BY`, `DENSE_RANK`, `GROUP BY`, `FOREIGN KEY`) tokenize as single atomic tokens instead of 3–5 sub-tokens, drastically reducing sequence length and compute costs.
* **Output Artifacts:** [`tokenizer/tokenizer.json`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/tokenizer/tokenizer.json).

---

### 🔹 Step 4: Neural Transformer Architecture Implementation (from Scratch)
* **Objective:** Implement a modern, high-performance Decoder-Only Transformer in PyTorch utilizing 2024–2026 architectural best practices (RoPE, SwiGLU, RMSNorm).
* **Tech Stack:** PyTorch 2.x, Tensor math.
* **What We Did in [`model/transformer.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/model/transformer.py):**
  1. **Rotary Position Embeddings (RoPE):** Replaced learned absolute positional embeddings with rotational query/key transformations ($\mathbf{q}_m = \mathbf{R}_{\Theta, m} \mathbf{W}_q \mathbf{x}_m$) to capture relative token distances in nested SQL queries.
  2. **RMSNorm:** Replaced standard LayerNorm with Root Mean Square Normalization ($\bar{a}_i = \frac{a_i}{\sqrt{\frac{1}{d}\sum a_j^2 + \epsilon}} \cdot \gamma_i$), speeding up backward passes.
  3. **SwiGLU Gated Feed-Forward Network:** Replaced standard GELU MLP with SwiGLU ($\text{SwiGLU}(\mathbf{x}) = (\text{SiLU}(\mathbf{x}\mathbf{W}_1) \odot \mathbf{x}\mathbf{W}_3)\mathbf{W}_2$) with hidden dimension $d_{\text{ffn}} = 768$.
  4. **Multi-Head Causal Attention:** 8 heads, head dimension 32, with upper-triangular causal attention masking.
  5. **Weight Tying:** Tied `token_embedding.weight` directly to `lm_head.weight` to reduce parameter redundancy.
* **Model Parameters:** $d_{\text{model}}=256, n_{\text{layers}}=6, n_{\text{heads}}=8, d_{\text{ffn}}=768 \implies$ **6,163,712 (6.16 Million) trainable parameters**.

---

### 🔹 Step 5: Pretraining, Optimization & Checkpoint Serialization
* **Objective:** Train the 6.16M Transformer on pure SQL pairs, optimize convergence, and serialize the best validation model weights.
* **Tech Stack:** PyTorch `DataLoader`, AdamW Optimizer, Cosine Annealing Learning Rate Scheduler.
* **What We Did in [`training/train.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/training/train.py):**
  1. Formatted input-target sequences with prompt masking so the model only incurs loss on predicting the assistant response tokens.
  2. Set training hyperparams: Batch size 32, Peak LR $1\times 10^{-3}$, Min LR $5\times 10^{-5}$, Weight Decay $0.01$, Gradient Clipping norm $1.0$.
  3. Executed 5 training epochs over 5,562 training samples and 618 validation samples.
  4. Tracked Validation Loss and calculated Validation Perplexity ($\text{PPL} = \exp(\text{Validation Loss})$) after every epoch.
* **Results Achieved:**
  - Initial Epoch 1 Val Loss: `3.4772` (PPL: 32.37)
  - Converged Epoch 5 Val Loss: **`2.4371`** (PPL: **`11.44`**)
* **Output Artifacts:** [`training/checkpoints/best_model.pt`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/training/checkpoints/best_model.pt).

---

### 🔹 Step 6: Vector Knowledge Base & Embedding Indexing (ChromaDB)
* **Objective:** Build a domain knowledge store for theoretical SQL concepts, query performance principles, and execution orders that can be queried semantically.
* **Tech Stack:** ChromaDB, `sentence-transformers` (`all-MiniLM-L6-v2` dense 384-dimensional embeddings).
* **What We Did:**
  1. Authored [`knowledge/documents.json`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/knowledge/documents.json) containing 14 comprehensive, authoritative SQL architectural documents (Joins, CTEs, Window Functions, ACID, Indexes, SARGability, Logical Processing Order, Normalization, Views).
  2. Implemented [`knowledge/vector_store.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/knowledge/vector_store.py) to ingest, chunk, embed, and index all documents into a persistent ChromaDB collection (`sql_domain_knowledge`).
* **Output Artifacts:** Local persistent vector database in `knowledge/chroma_db/`.

---

### 🔹 Step 7: Linguistic NLP Intent Router & Dynamic Conversational RAG
* **Objective:** Dynamically classify incoming user queries into appropriate functional tracks without hardcoding query phrases, and synthesize pedagogical markdown explanations.
* **Tech Stack:** Regular Expressions, NLTK-style linguistic action verb/question parsing, Semantic Similarity Matching.
* **What We Did:**
  1. Built [`sql_agent/intent_router.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/sql_agent/intent_router.py):
     - Classifies input into 4 semantic tracks: `TEXT_TO_SQL`, `CONCEPT_COMPARISON`, `CONCEPT_EXPLANATION`, `QUERY_OPTIMIZATION`.
  2. Built [`knowledge/rag_pipeline.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/knowledge/rag_pipeline.py):
     - **Dynamic Entity Comparison:** Uses regex to extract $X$ and $Y$ from queries like `"difference between X and Y"` or `"X vs Y"`, fetches relevant embeddings from ChromaDB for both, and builds a side-by-side comparison table.
     - **Pedagogical Synthesizer:** Formats answers with Concept Overview, Detailed Bullet Points, Syntax Examples, and Best Practice Pro-Tips.

---

### 🔹 Step 8: Autonomous SQL Agent & SQLite Database Sandbox
* **Objective:** Enable the system to safely execute generated SQL queries against a live relational schema and return real tabular data.
* **Tech Stack:** SQLite3, `sqlglot`, Python Pandas.
* **What We Did:**
  1. Implemented [`sql_agent/db_sandbox.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/sql_agent/db_sandbox.py) with 7 normalized relational tables (`customers`, `products`, `orders`, `order_items`, `departments`, `employees`, `sales_reps`) pre-populated with realistic enterprise data.
  2. Implemented [`sql_agent/agent.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/sql_agent/agent.py):
     - Injects live table schema into the model prompt.
     - Generates neural SQL.
     - Validates syntax using `sqlglot` Abstract Syntax Trees.
     - Executes query in the sandbox database.
     - Formats results into readable Pandas DataFrames with natural language summaries.

---

### 🔹 Step 9: Interactive Frontend Web Application (Streamlit)
* **Objective:** Provide a responsive, high-aesthetic web interface for interacting with Tiny SQL LLM.
* **Tech Stack:** Streamlit, CSS styling, Pandas.
* **What We Did in [`app/streamlit_app.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/app/streamlit_app.py):**
  1. Developed a dark-themed conversational chat interface with real-time response rendering.
  2. Added a sidebar **Database Schema Explorer** allowing users to inspect tables, column types, and sample rows.
  3. Integrated interactive DataFrame rendering for query results.
  4. Added execution timing indicators (`⏱️ 0.02s`) and provenance badges (`📌 SQL Knowledge Base`).

---

### 🔹 Step 10: Automated Benchmarking & Continuous Validation
* **Objective:** Continuously verify the model's SQL generation accuracy, AST validity, and conceptual correctness.
* **Tech Stack:** Python `unittest` / benchmark runner, `sqlglot`.
* **What We Did in [`evaluation/evaluate_model.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/evaluation/evaluate_model.py):**
  1. Created [`evaluation/benchmark.json`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/evaluation/benchmark.json) with 22 structured test cases across all SQL difficulty tiers.
  2. Tested AST parsing rate, SQL keyword presence, execution validity on SQLite, and semantic response relevancy.

---

## 📊 4. Data Engineering & Ingestion Pipeline

### 4.1 Cloned & Ingested GitHub Repositories
We built an automated repository ingestor ([`data/fetch_github_sql.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/fetch_github_sql.py)) that cloned 7 open-source SQL repositories:

| Repository | Source URL | Ingested Contents |
| :--- | :--- | :--- |
| **`hello-sql`** | `mouredev/hello-sql` | Relational fundamentals, basic/advanced clauses, DDL/DML |
| **`sql-tutorial`** | `civilian7/sql-tutorial` | 30-table e-commerce schema, 21 lessons, 270 real-world exercises |
| **`sql-ultimate-course`** | `DataWithBaraa/sql-ultimate-course` | Practical analytical queries, window functions & joins |
| **`sql-masterclass`** | `datawithdanny/sql-masterclass` | Advanced CTEs, multi-stage analytical queries |
| **`complete-intro-to-sql`** | `btholt/complete-intro-to-sql` | PostgreSQL fundamentals, indexes, relational constraints |
| **`sql-tutorials`** | `Baeldung/sql-tutorials` | Deep-dive recipes, optimizations, subqueries, grouping |
| **`sql-complete-guide-code`**| `academind/sql-complete-guide-code` | CRUD, relationships, constraints, schemas & views |

### 4.2 Data Extraction & Consolidation Pipeline
[`data/process_sql_data.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/process_sql_data.py) traversed all cloned files:
1. **Markdown Parser**: Extracted `### Heading` context + embedded ` ```sql ... ``` ` code blocks into (Instruction $\leftrightarrow$ Response) pairs.
2. **SQL File Parser**: Segmented standalone `.sql` files by statement terminator (`;`), extracting header comments as instructions.
3. **Synthetic Generator Integration** ([`data/data_generator.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/data_generator.py)): Augmented with 4,000+ programmatically generated and `sqlglot`-validated queries across Joins, CTEs, Window Functions, and Constraints.
4. **Deduplication & Splitting**: Deduplicated across normalized instruction strings and created a 90/10 split.

### 4.3 Final Dataset Metrics
- **Total Unique Pure SQL Samples:** **6,180**
- **Training Set ([`data/train.jsonl`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/train.jsonl)):** `5,562` samples
- **Validation Set ([`data/val.jsonl`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/val.jsonl)):** `618` samples
- **Pretraining Domain Corpus ([`data/corpus.txt`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/data/corpus.txt)):** `4.31 MB` raw SQL text

---

## 🔤 5. Custom NLP & Tokenization Engine

Implemented in [`tokenizer/train_tokenizer.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/tokenizer/train_tokenizer.py) using Hugging Face's `tokenizers` library.

### 5.1 Tokenizer Specifications
- **Algorithm:** Byte-Level Byte-Pair Encoding (BPE)
- **Vocabulary Size:** `4,096` tokens
- **Special Tokens:**
  - `<|pad|>`: Padding token (ID: 0)
  - `<|unk|>`: Unknown token (ID: 1)
  - `<|bos|>`: Beginning of sequence (ID: 2)
  - `<|eos|>`: End of sequence (ID: 3)
  - `<|endoftext|>`: End of text separator (ID: 4)

### 5.2 SQL Tokenization Efficiency
Trained directly on `data/corpus.txt`, ensuring common SQL keywords (`SELECT`, `WHERE`, `GROUP BY`, `ORDER BY`, `HAVING`, `PARTITION BY`, `ROW_NUMBER`, `DENSE_RANK`, `CREATE TABLE`, `FOREIGN KEY`) are encoded as single, dense tokens rather than split into multiple sub-word characters.

---

## 🧠 6. Neural Network Architecture (Deep Dive)

The neural network in [`model/transformer.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/model/transformer.py) is a modernized **Decoder-Only Transformer** incorporating state-of-the-art architectures from LLaMA 3, Mistral, and Qwen.

```
Input Token IDs (B, T)
        │
        ▼
[Token Embedding] (Vocab: 4096 -> d_model: 256)
        │
        ├──────────────────────────────────────────────┐
        ▼                                              │ (Residual)
[RMSNorm] (Root Mean Square Layer Normalization)       │
        │                                              │
        ▼                                              │
[RoPE Attention] (Multi-Head Self-Attention with RoPE) │
        │                                              │
        ▼                                              │
      [ + ] <──────────────────────────────────────────┘
        │
        ├──────────────────────────────────────────────┐
        ▼                                              │ (Residual)
[RMSNorm]                                              │
        │                                              │
        ▼                                              │
[SwiGLU FFN] (Gated Linear Feed-Forward Network)       │
        │                                              │
        ▼                                              │
      [ + ] <──────────────────────────────────────────┘
        │ (Repeated across N=6 Transformer Layers)
        ▼
[Final RMSNorm]
        │
        ▼
[Linear LM Head] (Tied with Token Embedding: 256 -> 4096)
        │
        ▼
Logits / Next Token Probabilities
```

### 6.1 Architectural Components

#### 1. Rotary Position Embeddings (RoPE)
Instead of adding static absolute positional embeddings to input vectors, RoPE applies a rotational transformation directly to the Query ($Q$) and Key ($K$) representations in the complex plane:
$$\mathbf{q}_m = \mathbf{R}_{\Theta, m}^d \mathbf{W}_q \mathbf{x}_m, \quad \mathbf{k}_n = \mathbf{R}_{\Theta, n}^d \mathbf{W}_k \mathbf{x}_n$$
- Enables the self-attention score $\mathbf{q}_m^\top \mathbf{k}_n$ to naturally depend on relative token distance $(m - n)$.
- Prevents degradation on long SQL queries and nested clauses.

#### 2. SwiGLU Gated Feed-Forward Network
Replaced standard GELU MLP with SwiGLU (Swish Gated Linear Unit):
$$\text{SwiGLU}(\mathbf{x}) = \left( \text{SiLU}(\mathbf{x} \mathbf{W}_1) \odot (\mathbf{x} \mathbf{W}_3) \right) \mathbf{W}_2$$
- $W_1$ acts as a gate, $W_3$ provides linear projection, and $W_2$ projects back to $d_{\text{model}}$.
- Delivers sharper token representation transitions for formal languages like SQL.

#### 3. RMSNorm (Root Mean Square Layer Normalization)
Replaced standard LayerNorm with RMSNorm:
$$\bar{a}_i = \frac{a_i}{\sqrt{\frac{1}{d} \sum_{j=1}^d a_j^2 + \epsilon}} \cdot \gamma_i$$
- Reduces computational overhead by eliminating mean calculation while preserving numerical stability.

#### 4. Weight Tying
Ties the input token embedding matrix directly with the output language modeling head (`lm_head.weight = token_embedding.weight`), saving ~1M redundant parameters.

### 6.2 Model Configuration & Parameters
- **Vocabulary Size:** `4,096`
- **Embedding Dimension ($d_{\text{model}}$):** `256`
- **Number of Layers ($n_{\text{layers}}$):** `6`
- **Attention Heads ($n_{\text{heads}}$):** `8` (Head dimension = 32)
- **FFN Hidden Dimension ($d_{\text{ffn}}$):** `768`
- **Max Sequence Length:** `256` tokens
- **Total Trainable Parameters:** **6,163,712 (6.16 Million)**

---

## 🏋️ 7. Training Pipeline & Convergence

Implemented in [`training/train.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/training/train.py).

### 7.1 Hyperparameters
- **Optimizer:** AdamW ($\beta_1 = 0.9, \beta_2 = 0.98, \epsilon = 10^{-8}$)
- **Weight Decay:** `0.01`
- **Peak Learning Rate:** `1e-3` (with minimum learning rate $\eta_{\min} = 5\times 10^{-5}$)
- **LR Scheduler:** Cosine Annealing over total training steps
- **Batch Size:** `32`
- **Gradient Clipping:** Max norm `1.0`
- **Loss Masking:** Padding tokens masked with target `-100` so `CrossEntropyLoss` ignores padding in backpropagation.

### 7.2 Training Convergence Metrics
Trained on CPU across 5 epochs:

| Epoch | Train Loss | Validation Loss | Validation Perplexity | Checkpoint Action |
| :---: | :---: | :---: | :---: | :---: |
| **1** | `4.6276` | `3.4772` | `32.37` | Saved `best_model.pt` |
| **2** | `3.0921` | `2.8873` | `17.95` | Saved `best_model.pt` |
| **3** | `2.7025` | `2.6119` | `13.63` | Saved `best_model.pt` |
| **4** | `2.4963` | `2.4807` | `11.95` | Saved `best_model.pt` |
| **5** | **`2.4061`** | **`2.4371`** | **`11.44`** | **Saved Final Checkpoint** |

---

## 🗄️ 8. Knowledge Base & Hybrid Vector Store (ChromaDB)

Implemented in [`knowledge/vector_store.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/knowledge/vector_store.py) and [`knowledge/documents.json`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/knowledge/documents.json).

### 8.1 Exhaustive Knowledge Taxonomy (194 Topic-Specific Documents)
The knowledge base has been scaled to **194 exhaustive, micro-to-macro SQL domain documents** across 16 major architectural and relational pillars:

1. **Roadmaps, Practice & Interview Guides (5 docs)**: Learning roadmaps, practice checklists, interview prep, debugging workflows, and cheat sheets.
2. **Core Query Clauses & Operators (15 docs)**: `SELECT`, `DISTINCT`, `WHERE`, `AND`/`OR`/`NOT`, `IN`/`NOT IN`, `BETWEEN`, `LIKE`/`ILIKE`, `IS NULL`, `ORDER BY`, `LIMIT`/`OFFSET`, `CASE WHEN`, `COALESCE`, `NULLIF`, `CAST`/`CONVERT`, Logical Query Execution Order.
3. **Relational Joins & Set Operations (15 docs)**: `INNER`, `LEFT`, `RIGHT`, `FULL OUTER`, `CROSS`, `NATURAL`, `SELF`, `ANTI`, `SEMI`, `LATERAL JOIN`, `CROSS APPLY`/`OUTER APPLY`, Non-Equi Joins, Join Algorithms (Hash/Nested Loop/Merge), `UNION`/`UNION ALL`, `INTERSECT`/`EXCEPT`.
4. **Aggregations & Group Operations (15 docs)**: `COUNT` variations, `GROUP BY`, `HAVING`, `WHERE` vs `HAVING`, `COUNT(DISTINCT)`, `ROLLUP`, `CUBE`, `GROUPING SETS`, `STRING_AGG`, `ARRAY_AGG`, Conditional Aggregation, `PIVOT`/`UNPIVOT`, Statistical aggregates, `FILTER` clause.
5. **Window Functions & Analytical SQL (15 docs)**: `OVER()`, `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `RANK` vs `DENSE_RANK`, `NTILE()`, `LAG()`, `LEAD()`, `FIRST_VALUE()`, `LAST_VALUE()`, `NTH_VALUE()`, `CUME_DIST()` / `PERCENT_RANK()`, `ROWS` vs `RANGE` frames, Cumulative Running Totals, Moving Averages.
6. **Common Table Expressions (CTEs) (10 docs)**: Standard CTEs, Recursive CTEs (`WITH RECURSIVE`), Chained Multi-CTEs, CTE vs Subquery vs Temp Table vs View, Deduplication CTEs, Data-Modifying CTEs, Materialized CTEs, Hierarchical Trees & Graphs, Keyset Pagination CTEs, Optimization Pitfalls.
7. **Subqueries & Relational Logic (12 docs)**: Scalar Subqueries, Multi-Row Subqueries, Correlated Subqueries, `EXISTS` vs `IN`, `NOT EXISTS` vs `NOT IN`, Derived Tables, `ANY`/`ALL`/`SOME`, Subqueries in `SELECT`/`HAVING`, Subqueries in `INSERT`/`UPDATE`/`DELETE`, Subquery Unnesting, Inline Views.
8. **DDL, Schemas & Constraints (15 docs)**: Primary Keys, Foreign Keys, Primary Key vs Foreign Key, `CHECK` Constraints, `UNIQUE` Constraints, `NOT NULL` Constraints, `DEFAULT` Constraints, `AUTO_INCREMENT`/`SERIAL`/`IDENTITY`, `ALTER TABLE`, `DROP` vs `TRUNCATE`, `DELETE` vs `TRUNCATE` vs `DROP`, Database Schemas & Namespaces, Temporary Tables, Table Partitioning, Cascading Referential Actions (`CASCADE`, `SET NULL`, `RESTRICT`).
9. **DML Mutation Operations (10 docs)**: `INSERT INTO`, `INSERT INTO SELECT`, `UPDATE`, `UPDATE` with `JOIN`, `DELETE`, `DELETE` with `JOIN`, `UPSERT` / `MERGE`, `RETURNING` / `OUTPUT` clauses, Bulk Loading Best Practices, `SELECT INTO`.
10. **Transactions, Locking & Concurrency (12 docs)**: ACID Properties, Transaction Isolation Levels, Concurrency Anomalies (Dirty, Non-Repeatable, Phantom Reads), Shared (`S`) & Exclusive (`X`) Locks, Deadlock Detection & Resolution, Multi-Version Concurrency Control (MVCC), TCL Commands (`COMMIT`, `ROLLBACK`, `SAVEPOINT`), Write-Ahead Logging (WAL), Optimistic vs Pessimistic Locking, Two-Phase Commit (2PC).
11. **Indexing & Performance Optimization (12 docs)**: B-Tree Index Architecture, Clustered vs Non-Clustered Indexes, Composite / Multi-Column Indexes (Leftmost Prefix Rule), Covering Indexes with `INCLUDE`, Filtered / Partial Indexes, Expression-Based / Functional Indexes, Index Seek vs Index Scan, SARGable Query Design, `EXPLAIN` & `EXPLAIN ANALYZE` Query Plans, Column Pruning & Projection, Index Maintenance & Fragmentation, Cost-Based Optimizer (CBO) Statistics.
12. **Database Objects & Programmability (15 docs)**: Stored Procedures, User-Defined Functions (UDF), Standard Views, Materialized Views, Database Triggers, Updatable Views, Database Cursors, Dynamic SQL, Database Packages & Modules, `LIMIT` vs `TOP`, Indexed Views, Error Handling (`TRY...CATCH`, `EXCEPTION`), Trigger-Based Audit Logging, Deterministic vs Non-Deterministic Functions, Table-Valued Functions (TVF).
13. **Data Types, Dates, Strings & JSON (15 docs)**: Numeric Data Types (`INT`, `BIGINT`, `DECIMAL`, `FLOAT`), Character & String Types (`VARCHAR`, `TEXT`, `CHAR`), Date & Timestamp Types, Date Arithmetic & Truncation (`DATEADD`, `DATEDIFF`, `DATE_TRUNC`), String Functions (`SUBSTRING`, `CONCAT`, `REPLACE`, `TRIM`), Regular Expressions (`REGEXP`), `JSON` & `JSONB` Semi-Structured Data, JSON Construction & Aggregation, UUID / GUID Identifiers, `ENUM` Types, Boolean Logic & Three-Valued Logic, Binary Data (`BLOB`, `BYTEA`), Character Collations & UTF-8, Interval Data Types, Implicit vs Explicit Type Precedence.
14. **Normalization & Data Modeling (10 docs)**: First Normal Form (1NF), Second Normal Form (2NF), Third Normal Form (3NF), Boyce-Codd Normal Form (BCNF), Fourth & Fifth Normal Forms (4NF / 5NF), Denormalization Tradeoffs, Relational Cardinalities (1:1, 1:N, M:N), Surrogate Keys vs Natural Keys, Dimensional Modeling (Star vs Snowflake Schemas), Slowly Changing Dimensions (SCD Types 1, 2, 3).
15. **Security, DCL & Administration (8 docs)**: `GRANT` & `REVOKE` Permissions, Role-Based Access Control (RBAC), Row-Level Security (RLS), SQL Injection Defense, Dynamic Data Masking, Database Auditing & Compliance, Transparent Data Encryption (TDE), Database Backup Strategies & Point-in-Time Recovery (PITR).
16. **Dialects & Engine Internals (10 docs)**: Cross-Dialect Comparative Matrix, PostgreSQL Features, MySQL & InnoDB Architecture, SQLite Engine Internals, SQL Server & T-SQL Ecosystem, Oracle Database & PL/SQL, OLTP vs OLAP Workloads, Row-Oriented vs Columnar Storage, ANSI SQL Standards Evolution, Database Page & Buffer Pool Architecture.

### 8.2 Acronym Normalizer & Hybrid Tag Boosting
- **Query Preprocessing:** Automatically expands 40+ acronyms and splits camelCase terms (`SP` $\to$ `Stored Procedure`, `StoreProcedure` $\to$ `Stored Procedure`, `CTE` $\to$ `Common Table Expression`, `UDF` $\to$ `User Defined Function`, `TVF` $\to$ `Table Valued Function`, `MV` $\to$ `Materialized View`, `MVCC` $\to$ `Multi Version Concurrency Control`, `WAL` $\to$ `Write Ahead Logging`, `1NF`/`2NF`/`3NF`/`BCNF` $\to$ `Database Normalization`, `roadmap` $\to$ `SQL Learning Roadmap`, `practice topics` $\to$ `SQL Practice Topics`, `SARGable` $\to$ `SARGable Predicates`).
- **Hybrid Scoring:** Combines dense cosine similarity with tag matching boosts ($\text{Final Score} = \text{Cosine Similarity} + \text{Tag Boost}$), ensuring 100% precision on conceptual queries.

---

## 🔄 9. Conversational RAG & Dynamic Knowledge Synthesizer

Implemented in [`knowledge/rag_pipeline.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/knowledge/rag_pipeline.py).

### 9.1 Zero-Hardcoding Architecture
- **Dynamic Entity Comparison**: Uses regex linguistic extraction to identify when any two concepts are being contrasted (`difference between X and Y`, `X vs Y`, `compare X with Y`), independently searches ChromaDB for $X$ and $Y$, and constructs a comparative guide dynamically.
- **Pedagogical Markdown Synthesizer**: Converts raw vector chunks into structured markdown:
  - 🎯 **Core Overview & Concept**
  - 📋 **Numbered Details transformed to clean bullet points**
  - 💻 **Syntax & Code Blocks**
  - 💡 **Key Takeaways & Best Practices**

---

## 🤖 10. Autonomous SQL Agent & Sandbox Execution Engine

Implemented in [`sql_agent/agent.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/sql_agent/agent.py) and [`sql_agent/db_sandbox.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/sql_agent/db_sandbox.py).

### 10.1 The 4-Step Agent Execution Loop
```
User Prompt (e.g. "Find top 5 highest salaried employees")
  │
  ├─> Step 1: In-Context Schema Injection + Neural SQL Generation
  │           Injects current database schema (tables, columns, types) dynamically.
  │
  ├─> Step 2: AST Validation & Dialect Transpilation (sqlglot)
  │           Validates SQL syntax and ensures safe read-only operations.
  │
  ├─> Step 3: SQLite Sandbox Execution
  │           Executes query in safe local SQLite sandbox with timing diagnostics.
  │
  └─> Step 4: Natural Language Result Synthesis
              Summarizes row counts, key columns, and top insights.
```

### 10.2 Sandbox Database Schema
The database sandbox contains 7 realistic relational tables:
- **`customers`**: `customer_id`, `first_name`, `last_name`, `email`, `region`, `segment`, `join_date`
- **`products`**: `product_id`, `product_name`, `category`, `unit_price`, `stock_quantity`
- **`orders`**: `order_id`, `customer_id`, `order_date`, `total_amount`, `status`, `payment_method`
- **`order_items`**: `item_id`, `order_id`, `product_id`, `quantity`, `item_price`
- **`departments`**: `department_id`, `dept_name`, `location`, `budget`
- **`employees`**: `emp_id`, `emp_name`, `department_id`, `salary`, `hire_date`, `job_title`
- **`sales_reps`**: `rep_id`, `rep_name`, `region`, `commission_rate`, `annual_target`

---

## 🧭 11. Linguistic NLP Intent Router

Implemented in [`sql_agent/intent_router.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/sql_agent/intent_router.py).

Classifies user input using linguistic structure (parts of speech, action verbs, and inquiry prepositions) rather than hardcoded query keywords:

| Intent Category | Linguistic Pattern Examples | Destination Engine |
| :--- | :--- | :--- |
| **`CONCEPT_EXPLANATION`**| Inquiry markers & Educational: `"what is"`, `"what are"`, `"explain"`, `"roadmap"`, `"topics to practice"`, `"tutorial"`, `"guide"` | Pedagogical RAG Synthesizer |
| **`CONCEPT_COMPARISON`** | Contrastive prepositions: `"difference between ... and"`, `"vs"`, `"versus"`, `"compare"`, `"contrast"` | Dynamic RAG Comparative Engine |
| **`QUERY_OPTIMIZATION`** | Performance verbs: `"optimize"`, `"tune"`, `"slow query"`, `"execution plan"`, `"sargable"` | Optimization Advisor |
| **`TEXT_TO_SQL`** | Table & Data Actions: `"write query to"`, `"find all customers"`, `"calculate total sales"`, `"top 5 highest salary"` | SQL Agent & Sandbox Execution |

---

## 🧪 12. Testing & Automated Benchmark Evaluation

Implemented in [`evaluation/evaluate_model.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/evaluation/evaluate_model.py) and [`evaluation/benchmark.json`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/evaluation/benchmark.json).

### 12.1 Benchmark Test Suite
22 comprehensive evaluation questions covering:
- Basic & Conditional queries (`WHERE`, `CASE WHEN`, `BETWEEN`, `IN`)
- Relational Joins (`INNER`, `LEFT`, `ANTI-JOIN`, `CROSS`)
- Aggregations (`GROUP BY`, `HAVING`, `ROLLUP`)
- Window Functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`)
- Common Table Expressions (`WITH`, `RECURSIVE`)
- Subqueries (`EXISTS` vs `IN`, Correlated subqueries)
- DDL & Constraints (`CREATE TABLE`, `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`)
- Transactions & Performance (`ACID`, `DELETE vs TRUNCATE vs DROP`, `B-Tree vs Hash`)

---

## 🖥️ 13. Frontend Web Interface (Streamlit)

Implemented in [`app/streamlit_app.py`](file:///c:/Users/akatre/OneDrive%20-%20Nice%20Software%20Solutions/Desktop/Tiny%20LLM/app/streamlit_app.py).

### Features:
- **Unified Conversational Interface**: Auto-routes between SQL query execution and conceptual RAG.
- **Syntax-Highlighted SQL Code**: Displays formatted SQL in copyable code blocks.
- **Live DataFrame Table Rendering**: Visualizes returned database rows interactively with column headers.
- **Diagnostics**: Displays latency in seconds (`⏱️ 0.02s`) and citation sources (`📌 SQL Knowledge Base`).
- **Sidebar Database Schema Explorer**: Lets users browse available tables and column types live.

---

## 🚀 14. Step-by-Step Guide: How to Run, Test & Retrain

### 14.1 Run the Streamlit Web Application
```bash
streamlit run app/streamlit_app.py
```

### 14.2 Fetch Latest SQL Repositories
```bash
python data/fetch_github_sql.py
```

### 14.3 Process Raw Data into Training Datasets
```bash
python data/process_sql_data.py
```

### 14.4 Retrain Custom BPE Tokenizer
```bash
python tokenizer/train_tokenizer.py
```

### 14.5 Train the Neural Network Model
```bash
python training/train.py
```

### 14.6 Run Benchmark Evaluation
```bash
python evaluation/evaluate_model.py
```

### 14.7 Test Standalone Modules
```bash
# Test Intent Router
python sql_agent/intent_router.py

# Test SQL Agent & Sandbox Execution
python sql_agent/agent.py

# Test Conversational RAG
python knowledge/rag_pipeline.py
```

---

## 🏁 15. Technology Stack Summary

| Layer | Technology Used | Role |
| :--- | :--- | :--- |
| **Core Language** | Python 3.10+ | Primary runtime environment |
| **Deep Learning** | PyTorch 2.x | Neural network training, RoPE, SwiGLU, RMSNorm |
| **Tokenization** | Hugging Face `tokenizers` | Custom 4,096 Byte-Level BPE Tokenizer |
| **Vector Database** | ChromaDB | Local persistent vector storage for RAG |
| **SQL Engine** | SQLite3 | Local in-memory / file sandbox execution |
| **SQL Parser & Linter** | `sqlglot` | AST parsing, dialect transpilation, syntax checks |
| **Data Manipulation** | Pandas | Tabular data representation and formatting |
| **User Interface** | Streamlit | Real-time interactive web application |
| **Version Control & Ingestion** | Git & Git Submodules | Automated cloning of curated SQL datasets |
