# ⚡ Tiny SQL LLM (SQL-SLM)

> **A specialized, ultra-lightweight 6.16M-parameter Small Language Model (SLM), Autonomous Agent & Vector RAG ecosystem for text-to-SQL generation and database intelligence on standard CPU hardware.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI%20Dashboard-FF4B4B.svg)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20RAG-purple.svg)](https://chromadb.com)

---

## 📖 Table of Contents
- [Executive Overview](#-executive-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [The 5 Core Pillars](#-the-5-core-pillars)
- [Project Directory Structure](#-project-directory-structure)
- [Quickstart & Installation](#-quickstart--installation)
- [Interactive UI & APIs](#-interactive-ui--apis)
- [Model Evaluation & Benchmarks](#-model-evaluation--benchmarks)
- [License](#-license)

---

## 🌟 Executive Overview

Unlike generic multi-billion parameter cloud models that introduce latency, parameter dilution, and security concerns with sensitive enterprise schemas, **Tiny SQL LLM** is engineered specifically for relational database tasks:

* **Compact Footprint**: 6.16M parameter Decoder-only Transformer trained from scratch.
* **100% Local & Private**: Runs entirely offline on standard consumer CPU hardware without sending schemas or data to third-party APIs.
* **Guaranteed Syntax & Safety**: Uses `sqlglot` Abstract Syntax Tree (AST) validation and self-repair loops before executing queries against isolated database sandboxes.
* **Hybrid Intelligence**: Combines neural SQL generation with persistent **ChromaDB Vector RAG** to explain complex SQL concepts, comparisons, and schema questions.

---

## ✨ Key Features

- ⚡ **Domain-Specific BPE Tokenizer**: 4,096 custom subword vocabulary optimized for SQL grammar and identifiers.
- 🧠 **Multi-Intent NLP Router**: Automatically distinguishes between SQL generation, concept tutorials, entity comparisons, and ambiguous user prompts.
- 🛡️ **Self-Healing SQL Agent**: Validates queries against schema ASTs; automatically detects syntax errors and executes dynamic self-repair loops.
- 📦 **Zero-Leakage Training Pipeline**: Supervised Fine-Tuning (SFT) dataset generation partitioned strictly by database schema.
- 🚀 **Production-Ready FastAPI Backend**: Token-authenticated REST endpoints with rate limiting and execution sandboxing.
- 📊 **Interactive Streamlit Web Dashboard**: Real-time natural language query interface, visual dataframe viewer, and schema explorer.

---

## 🏛️ System Architecture

```
                                  ┌────────────────────────┐
                                  │   User Natural Query   │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                             ┌──────────────────────────────────┐
                             │    Linguistic Intent Router      │
                             │   (agent_engine/intent_router)   │
                             └────────────────┬─────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
     [TEXT_TO_SQL / ACTION]      [CONCEPT_COMPARISON]       [CONCEPT_EXPLANATION / TUTORIAL]
                    │                         │                         │
                    ▼                         ▼                         ▼
     ┌────────────────────────────┐ ┌───────────────────┐ ┌───────────────────────────┐
     │   Autonomous SQL Agent     │ │ Dynamic Entity    │ │ Pedagogical Synthesizer   │
     │   (agent_engine/agent.py)  │ │ Comparison Engine │ │ (Definition -> Code ->    │
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
                     │ Streamlit Dashboard / FastAPI API │
                     │  - Structured Explanations        │
                     │  - Executable SQL Code Snippets   │
                     │  - Interactive Pandas DataFrames  │
                     └───────────────────────────────────┘
```

---

## 🏛️ The 5 Core Pillars

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   TINY SQL LLM SYSTEM BLUEPRINT                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
  │
  ├── 1. ⚙️ THE FOUNDATION & ENGINE ROOM (Neural Architecture & Tokenizer)
  │     ├── 1.1 Decoder-Only Transformer Core (`transformer.py`)
  │     ├── 1.2 Multi-Head Causal Self-Attention (`attention.py`)
  │     ├── 1.3 Hyperparameter & Architecture Configuration (`config.py`)
  │     ├── 1.4 BPE Vocabulary Training Engine (`train_tokenizer.py`)
  │     └── 1.5 Subword Encoding & Inference Wrapper (`tokenizer_wrapper.py`)
  │
  ├── 2. 🧪 THE REFINERY & DATA WORKSHOP (Data Engineering & Synthesis)
  │     ├── 2.1 PDF Textbook & Manual Extraction (`process_pdf_1.py` - `5.py`)
  │     ├── 2.2 Schema-Conditioned NL-to-SQL Synthesis (`data_generator.py`)
  │     ├── 2.3 Hard Negative & Antipattern Generation (`hard_negative_generator.py`)
  │     ├── 2.4 Query Ambiguity & Clarification Generator (`ambiguity_generator.py`)
  │     └── 2.5 Zero-Data-Leakage Dataset Partitioning (`leakage_safe_splitter.py`)
  │
  ├── 3. 🔨 THE FORGE & INFERENCE ENGINE (Training, Optimization & Generation)
  │     ├── 3.1 Supervised Fine-Tuning (SFT) Trainer (`train.py`)
  │     ├── 3.2 Target-Masked Autoregressive Dataset Loader (`dataset.py`)
  │     ├── 3.3 Learning Rate Scheduler & Checkpoint Manager (`inspect_ckpt.py`)
  │     ├── 3.4 Autoregressive Text-to-SQL Generator (`generate.py`)
  │     └── 3.5 Token Sampling & Repetition Penalty Controller (`generate.py`)
  │
  ├── 4. 🧠 THE BRAIN VAULT & CONTROL TOWER (RAG Knowledge & Autonomous Agent)
  │     ├── 4.1 Dense Vector Storage & Embeddings (`vector_store.py`)
  │     ├── 4.2 Semantic RAG Retrieval Pipeline (`rag_pipeline.py`)
  │     ├── 4.3 Linguistic Intent Routing Engine (`intent_router.py`)
  │     ├── 4.4 Autonomous SQL Agent & Self-Repair Loop (`agent.py`)
  │     └── 4.5 Sandboxed Database Execution & Schema Introspection (`db_sandbox.py`)
  │
  └── 5. 🖥️ THE SHOWROOM & BENCHMARK SUITE (UI, APIs & Evaluation)
        ├── 5.1 Interactive Streamlit Web Dashboard (`streamlit_app.py`)
        ├── 5.2 Authenticated REST API & Key Vault (`api_server.py`)
        ├── 5.3 Execution & AST Accuracy Evaluation Engine (`evaluate_model.py`)
        ├── 5.4 Domain-Specific Complex Banking Benchmarks (`banking_challenge_suite.py`)
        └── 5.5 Stakeholder Interactive Presentation Deck (`index.html`)
```

---

## 📂 Project Directory Structure

```text
Tiny LLM/
├── ⚙️ model/               # Custom Transformer architecture (Attention, Config, Blocks)
├── 🔤 tokenizer/           # Custom Byte-Pair Encoding (BPE) tokenizer & vocabulary
├── 🧪 data/                # Data pipelines, PDF extractors & synthesized training splits
├── 🔨 training/            # PyTorch SFT training loops, loss masking & checkpoints
├── ⚡ inference/           # Autoregressive generation engine with Top-K/Top-P sampling
├── 🧠 knowledge/           # ChromaDB vector store, document embeddings & RAG pipeline
├── 🤖 agent_engine/        # Autonomous SQL Agent, AST parser, and SQLite sandbox
├── 📊 evaluation/          # Evaluation benchmarks (Exact Match, Execution Accuracy)
├── 🖥️ app/                 # Streamlit web dashboard & FastAPI server
└── 📄 docs/
    ├── pitch_deck/         # Interactive web presentation deck
    └── ...                 # Architectural and technical documentation
```

---

## 🚀 Quickstart & Installation

### 1. Clone & Setup Environment
```bash
# Clone the repository
git clone https://github.com/Akatre22/SQL---Language-Model-.git
cd SQL---Language-Model-

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required dependencies
pip install torch torchvision torchaudio
pip install tokenizers fastapi uvicorn streamlit chromadb sentence-transformers sqlglot pandas pydantic
```

### 2. Run the Interactive Streamlit Web App
```bash
streamlit run app/streamlit_app.py
```
Open your browser at `http://localhost:8501` to start querying your database in natural English.

### 3. Launch the Authenticated REST API Server
```bash
python app/api_server.py
```
API docs will be available at `http://localhost:8000/docs`.

---

## 💻 Python Agent Usage Example

```python
from agent_engine.agent import SQLAgent

# Initialize the autonomous agent
agent = SQLAgent()

# Ask any analytical query in plain English
response = agent.run("Find top 5 customers who spent more than 5000 in total orders")

print("Generated SQL:\n", response["sql"])
print("Execution Status:\n", response["status"])
print("Result Rows:\n", response["results"])
```

---

## 📊 Model Evaluation & Benchmarks

| Metric | Tiny SQL LLM (6.16M) | Target / Baseline |
|---|---|---|
| **Parameters** | **6.16M** | Compact CPU Footprint |
| **AST Validity Rate** | **96.4%** | Enforces clean SQL syntax |
| **Execution Accuracy (EX)** | **88.2%** | Validated against SQLite Sandbox |
| **Inference Latency (CPU)** | **~85ms** | Real-time interactive response |
| **Privacy & Cloud Cost** | **100% Offline / $0 API Cost** | Zero data egress |

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
