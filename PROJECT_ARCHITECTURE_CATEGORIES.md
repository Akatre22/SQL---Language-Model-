# 🏛️ Tiny SQL LLM — 5-Pillar Architectural Breakdown

Like a house organized into dedicated rooms—where each room has a distinct purpose, specific tools, and specialized functions—the **Tiny SQL LLM** project is divided into **5 major categories**, with **5 specialized sub-categories** in each.

---

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   TINY SQL LLM SYSTEM BLUEPRINT                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
  │
  ├── 1. ⚙️ THE FOUNDATION & ENGINE ROOM (Neural Architecture & Tokenizer)
  │     ├── 1.1 Decoder-Only Transformer Core
  │     ├── 1.2 Multi-Head Causal Self-Attention
  │     ├── 1.3 Hyperparameter & Architecture Configuration
  │     ├── 1.4 BPE Vocabulary Training Engine
  │     └── 1.5 Subword Encoding & Inference Wrapper
  │
  ├── 2. 🧪 THE REFINERY & DATA WORKSHOP (Data Engineering & Synthesis)
  │     ├── 2.1 PDF Textbook & Manual Extraction
  │     ├── 2.2 Schema-Conditioned NL-to-SQL Synthesis
  │     ├── 2.3 Hard Negative & Antipattern Generation
  │     ├── 2.4 Query Ambiguity & Clarification Generator
  │     └── 2.5 Zero-Data-Leakage Dataset Partitioning
  │
  ├── 3. 🔨 THE FORGE & INFERENCE ENGINE (Training, Optimization & Generation)
  │     ├── 3.1 Supervised Fine-Tuning (SFT) Trainer
  │     ├── 3.2 Target-Masked Autoregressive Dataset Loader
  │     ├── 3.3 Learning Rate Scheduler & Checkpoint Manager
  │     ├── 3.4 Autoregressive Text-to-SQL Generator
  │     └── 3.5 Token Sampling & Repetition Penalty Controller
  │
  ├── 4. 🧠 THE BRAIN VAULT & CONTROL TOWER (RAG Knowledge & Autonomous Agent)
  │     ├── 4.1 Dense Vector Storage & Embeddings
  │     ├── 4.2 Semantic RAG Retrieval Pipeline
  │     ├── 4.3 Linguistic Intent Routing Engine
  │     ├── 4.4 Autonomous SQL Agent & Self-Repair Loop
  │     └── 4.5 Sandboxed Database Execution & Schema Introspection
  │
  └── 5. 🖥️ THE SHOWROOM & BENCHMARK SUITE (UI, APIs & Evaluation)
        ├── 5.1 Interactive Streamlit Web Dashboard
        ├── 5.2 Authenticated REST API & Key Vault
        ├── 5.3 Execution & AST Accuracy Evaluation Engine
        ├── 5.4 Domain-Specific Complex Banking Benchmarks
        └── 5.5 Stakeholder Interactive Presentation Deck
```

---

## 1. ⚙️ Category 1: The Foundation & Engine Room (Neural Architecture & Tokenizer)
> **Analogy:** *The Engine & Structural Frame* — Establishes the mathematical foundation, neural layers, and vocabulary system for processing natural language and SQL tokens.

### 1.1 Decoder-Only Transformer Core
- **Primary File:** `transformer.py`
- **Tech Stack:** `PyTorch (torch.nn)`, `Python Math`
- **Role:** Implements the 6.16M parameter Decoder-only Transformer stack, Layer Normalization, Residual Connections, Feed-Forward Networks (FFN), and the Language Modeling prediction head.

### 1.2 Multi-Head Causal Self-Attention
- **Primary File:** `attention.py`
- **Tech Stack:** `PyTorch`, `Tensor Operations`
- **Role:** Computes scaled dot-product attention across multiple attention heads with causal triangular masking to ensure strict autoregressive token prediction.

### 1.3 Hyperparameter & Architecture Configuration
- **Primary File:** `config.py`
- **Tech Stack:** `Python Data Structures`
- **Role:** Defines core structural parameters (`d_model=384`, `n_layers=6`, `n_heads=6`, `vocab_size=4096`, `max_seq_len=512`, `dropout=0.1`).

### 1.4 BPE Vocabulary Training Engine
- **Primary File:** `train_tokenizer.py`, `tokenizer.json`
- **Tech Stack:** `Hugging Face Tokenizers (BPE Rust Engine)`
- **Role:** Trains a custom Byte-Pair Encoding tokenizer from raw SQL corpus text, creating a compact 4,096-token vocabulary tailored to SQL keywords and schema identifiers.

### 1.5 Subword Encoding & Inference Wrapper
- **Primary File:** `tokenizer_wrapper.py`
- **Tech Stack:** `Hugging Face Tokenizers`, `Python`
- **Role:** Provides encoding, decoding, special token management (`<pad>`, `<bos>`, `<eos>`, `<unk>`), and tensor batching utilities during training and inference.

---

## 2. 🧪 Category 2: The Refinery & Data Workshop (Data Engineering & Synthesis)
> **Analogy:** *The Kitchen & Refinery* — Gathers raw educational SQL resources and manufactures clean, diverse, schema-aware training datasets.

### 2.1 PDF Textbook & Manual Extraction
- **Primary Files:** `process_pdf_1.py`, `process_pdf_2.py`, `process_pdf_3.py`, `process_pdf_4.py`, `process_pdf_5.py`
- **Tech Stack:** `PyMuPDF (fitz)`, `Python RegEx`
- **Role:** Extracts structured text, definitions, code blocks, and syntax rules from SQL manuals and textbooks.

### 2.2 Schema-Conditioned NL-to-SQL Synthesis
- **Primary Files:** `data_generator.py`, `nl_to_sql_builder.py`
- **Tech Stack:** `Python JSON / JSONL`, `AST Schema Builders`
- **Role:** Synthesizes paired prompt-SQL training examples injected with database schema context (tables, columns, foreign keys).

### 2.3 Hard Negative & Antipattern Generation
- **Primary File:** `hard_negative_generator.py`, `hard_negatives.jsonl`
- **Tech Stack:** `Python RegEx`, `Query Mutation Algorithms`
- **Role:** Introduces intentional syntax errors, missing `JOIN` conditions, and schema mismatches to train the model on query robustness and error handling.

### 2.4 Query Ambiguity & Clarification Generator
- **Primary File:** `ambiguity_generator.py`, `ambiguity_dataset.jsonl`
- **Tech Stack:** `Python Random`, `Rule-based Linguistic Synthesizers`
- **Role:** Creates ambiguous user questions that require schema clarification before generating SQL queries.

### 2.5 Zero-Data-Leakage Dataset Partitioning
- **Primary Files:** `leakage_safe_splitter.py`, `train.jsonl`, `val.jsonl`, `test_unseen.jsonl`
- **Tech Stack:** `Python JSONL`, `Schema Hash Partitioning`
- **Role:** Splits datasets by database schema rather than random sampling, ensuring that evaluation measures true generalization to unseen databases.

---

## 3. 🔨 Category 3: The Forge & Inference Engine (Training, Optimization & Generation)
> **Analogy:** *The Workshop & Powerhouse* — Performs neural parameter optimization and generates SQL queries token-by-token at runtime.

### 3.1 Supervised Fine-Tuning (SFT) Trainer
- **Primary File:** `train.py`
- **Tech Stack:** `PyTorch`, `torch.cuda.amp (Mixed Precision)`, `AdamW Optimizer`
- **Role:** Runs the complete training loop, executes backward passes with gradient clipping, and optimizes model weights against cross-entropy loss.

### 3.2 Target-Masked Autoregressive Dataset Loader
- **Primary File:** `dataset.py`
- **Tech Stack:** `PyTorch Dataset & DataLoader`, `Tensor Masking`
- **Role:** Batches tokenized sequences and applies cross-entropy loss masks to prompt tokens so the loss is computed solely on generated SQL target tokens.

### 3.3 Learning Rate Scheduler & Checkpoint Manager
- **Primary Files:** `train.py`, `inspect_ckpt.py`, `checkpoints/`
- **Tech Stack:** `PyTorch CosineAnnealingLR`, `Torch Serialization`
- **Role:** Dynamically adjusts learning rates with warmup/decay cycles and manages saving and inspecting the best validation checkpoints (`.pt`).

### 3.4 Autoregressive Text-to-SQL Generator
- **Primary File:** `generate.py`
- **Tech Stack:** `PyTorch (CPU/CUDA Inference)`
- **Role:** Performs greedy and probabilistic token-by-token autoregressive decoding from prompt inputs to output valid SQL text.

### 3.5 Token Sampling & Repetition Penalty Controller
- **Primary File:** `generate.py`
- **Tech Stack:** `Temperature Scaling`, `Top-K Filtering`, `Nucleus (Top-P) Sampling`
- **Role:** Controls generation randomness, prevents repetitive SQL token loops, and terminates generation at `<eos>` or maximum sequence length.

---

## 4. 🧠 Category 4: The Brain Vault & Control Tower (RAG Knowledge & Autonomous Agent)
> **Analogy:** *The Library & Control Center* — Maintains persistent domain knowledge, classifies intent, validates syntax, and securely executes queries.

### 4.1 Dense Vector Storage & Embeddings
- **Primary File:** `vector_store.py`
- **Tech Stack:** `ChromaDB`, `Sentence-Transformers (all-MiniLM-L6-v2)`
- **Role:** Generates 384-dimensional dense semantic vector embeddings for SQL documentation and maintains the persistent local vector database.

### 4.2 Semantic RAG Retrieval Pipeline
- **Primary Files:** `rag_pipeline.py`, `documents.json`
- **Tech Stack:** `ChromaDB Vector Search`, `Cosine Similarity Filtering`
- **Role:** Performs semantic similarity search to fetch SQL concept definitions, tutorials, and function syntaxes to augment user prompts.

### 4.3 Linguistic Intent Routing Engine
- **Primary File:** `intent_router.py`
- **Tech Stack:** `Python Pattern Matching`, `Linguistic Classification Rules`
- **Role:** Analyzes incoming user queries and routes them to appropriate handlers (`TEXT_TO_SQL`, `CONCEPT_EXPLANATION`, `CONCEPT_COMPARISON`, `CLARIFICATION`).

### 4.4 Autonomous SQL Agent & Self-Repair Loop
- **Primary File:** `agent.py`
- **Tech Stack:** `sqlglot (AST Parser & Transpiler)`, `Python Exception Handling`
- **Role:** Orchestrates the full query pipeline: schema formatting, neural SQL generation, AST validation, error detection, and automatic query repair.

### 4.5 Sandboxed Database Execution & Schema Introspection
- **Primary Files:** `db_sandbox.py`, `enterprise_sandbox.db`, `schema_formatter.py`, `clarification_engine.py`
- **Tech Stack:** `SQLite3`, `Database Schema Introspection`
- **Role:** Provides an isolated SQLite environment with preloaded enterprise tables, executes read-only queries, and returns formatted result tables or error diagnostics.

---

## 5. 🖥️ Category 5: The Showroom & Benchmark Suite (UI, APIs & Evaluation)
> **Analogy:** *The Living Room & Testing Grounds* — Exposes user interfaces, provides backend API services, and benchmarks system accuracy.

### 5.1 Interactive Streamlit Web Dashboard
- **Primary File:** `streamlit_app.py`
- **Tech Stack:** `Streamlit`, `Pandas`, `Session State Management`
- **Role:** Provides a reactive web UI for natural language querying, schema exploration, real-time SQL generation, and tabular data visualization.

### 5.2 Authenticated REST API & Key Vault
- **Primary Files:** `api_server.py`, `key_manager.py`, `api_keys.json`
- **Tech Stack:** `FastAPI`, `Uvicorn`, `SHA-256 Token Auth`, `Rate Limiting`
- **Role:** Exposes production-ready REST API endpoints (`/generate-sql`, `/execute`, `/explain`, `/health`) with role-based API key authentication.

### 5.3 Execution & AST Accuracy Evaluation Engine
- **Primary Files:** `evaluate_model.py`, `evaluate_sql.py`
- **Tech Stack:** `sqlglot`, `Execution Accuracy (EX)`, `Exact Match (EM)`
- **Role:** Evaluates generated queries against ground truth benchmarks, measuring semantic equivalence, execution success, and syntax validity.

### 5.4 Domain-Specific Complex Banking Benchmarks
- **Primary Files:** `banking_challenge_suite.py`, `benchmark.json`, `build_expanded_benchmark.py`
- **Tech Stack:** `SQLite3`, `JSON Benchmark Suites`
- **Role:** Tests the system on complex multi-table joins, aggregations, window functions, and nested subqueries on banking schema datasets.

### 5.5 Stakeholder Interactive Presentation Deck
- **Primary Files:** `index.html`, `styles.css`, `app.js` (under `docs/pitch_deck/`)
- **Tech Stack:** `HTML5`, `CSS3 Glassmorphism`, `Vanilla JavaScript (ES6+)`
- **Role:** Delivers an interactive web pitch deck demonstrating architecture, technical benchmarks, privacy benefits, and business ROI.

---

## 📋 Comprehensive 5x5 Summary Matrix

| # | Main Category | Sub-Category | Primary File(s) | Specific Tech Stack | Core Role |
|---|---|---|---|---|---|
| **1.1** | **Foundation & Engine** | Transformer Core | `transformer.py` | PyTorch (`torch.nn`) | 6.16M param Decoder-only Transformer & LM Head |
| **1.2** | **Foundation & Engine** | Causal Self-Attention | `attention.py` | PyTorch | Multi-head attention with causal triangular masks |
| **1.3** | **Foundation & Engine** | Architecture Config | `config.py` | Python Dataclasses | Dimensions (`d_model=384`, `layers=6`, `heads=6`) |
| **1.4** | **Foundation & Engine** | BPE Tokenizer Training | `train_tokenizer.py` | HF Tokenizers (BPE) | Vocabulary training on SQL corpus (4,096 tokens) |
| **1.5** | **Foundation & Engine** | Inference Tokenizer | `tokenizer_wrapper.py` | HF Tokenizers / Python | Encoding/decoding & special token handling |
| **2.1** | **Refinery & Data** | PDF Text Extraction | `process_pdf_1-5.py` | PyMuPDF (`fitz`), RegEx | Parses SQL manuals and academic textbooks |
| **2.2** | **Refinery & Data** | NL-to-SQL Synthesis | `data_generator.py` | Python AST / JSONL | Generates schema-conditioned training pairs |
| **2.3** | **Refinery & Data** | Hard Negative Creation | `hard_negative_generator.py` | Python RegEx | Injects intentional syntax & schema errors |
| **2.4** | **Refinery & Data** | Ambiguity Generation | `ambiguity_generator.py` | Python Random | Creates queries requiring clarification |
| **2.5** | **Refinery & Data** | Zero-Leakage Split | `leakage_safe_splitter.py` | JSONL / Schema Hashing | Schema-isolated train/val/test partitioning |
| **3.1** | **Forge & Inference** | SFT Model Trainer | `train.py` | PyTorch, AMP, AdamW | Mixed precision training & loss optimization |
| **3.2** | **Forge & Inference** | Masked Data Loader | `dataset.py` | PyTorch Dataset/DataLoader | Target-only cross-entropy loss masking |
| **3.3** | **Forge & Inference** | LR & Checkpoints | `train.py`, `inspect_ckpt.py` | CosineAnnealingLR, Torch | Dynamic LR scheduling & model weight storage |
| **3.4** | **Forge & Inference** | Autoregressive Engine | `generate.py` | PyTorch CPU/CUDA | Token-by-token text-to-SQL inference |
| **3.5** | **Forge & Inference** | Sampling Controller | `generate.py` | Top-K, Top-P, Temperature | Prevents repetitions & controls randomness |
| **4.1** | **Brain & Control** | Vector Embedding Store | `vector_store.py` | ChromaDB, Sentence-Transformers | Dense vector store (`all-MiniLM-L6-v2`) |
| **4.2** | **Brain & Control** | RAG Search Pipeline | `rag_pipeline.py` | ChromaDB, Cosine Search | Semantic retrieval of SQL concepts & docs |
| **4.3** | **Brain & Control** | Intent Routing Engine | `intent_router.py` | Linguistic Pattern Matcher | Classifies queries (SQL vs Concept vs Compare) |
| **4.4** | **Brain & Control** | Autonomous SQL Agent | `agent.py` | `sqlglot`, Python Agent | AST validation, self-repair & query orchestration |
| **4.5** | **Brain & Control** | Database Sandbox | `db_sandbox.py` | SQLite3 | Safe execution & result table extraction |
| **5.1** | **Showroom & UI** | Streamlit Web App | `streamlit_app.py` | Streamlit, Pandas | Real-time query UI & data visualizer |
| **5.2** | **Showroom & UI** | REST API & Security | `api_server.py`, `key_manager.py` | FastAPI, Uvicorn, SHA-256 | Authenticated API endpoints & token vault |
| **5.3** | **Showroom & UI** | Accuracy Benchmarks | `evaluate_model.py` | `sqlglot`, Python Metrics | Computes Exact Match (EM) & Execution (EX) |
| **5.4** | **Showroom & UI** | Banking Test Suite | `banking_challenge_suite.py` | SQLite3, JSON Suites | Complex multi-table join challenge evaluation |
| **5.5** | **Showroom & UI** | Pitch Deck App | `index.html`, `app.js` | HTML5, CSS3, JavaScript | Interactive product pitch and ROI deck |
