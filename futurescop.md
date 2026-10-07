SQL Small Language Model (SQL-SLM)
Enhancement & Implementation Roadmap

Enhancing the existing Tiny SQL LLM project into a stronger, schema-aware, production-oriented SQL language model

1. Executive Summary

The existing project already contains the core ingredients of a language model: a custom SQL tokenizer, a decoder-only Transformer, causal self-attention, autoregressive generation, and cross-entropy training. The current model is approximately 6.16M parameters and is specialized around SQL.

The objective of this roadmap is not to turn the system into a general-purpose LLM. The objective is to evolve it into a stronger Domain-Specific Small Language Model (SQL-SLM): a compact language model intentionally trained for SQL language understanding, natural-language-to-SQL generation, schema conditioning, SQL reasoning, and SQL correctness.

The surrounding RAG, intent router, SQL validator, database execution layer, evaluation framework, and UI remain important system components, but the Transformer itself should be clearly treated as the SQL language model.

2. Current Baseline — What Already Exists

Area

Current implementation

Status

Data

GitHub SQL harvesting + synthetic enterprise SQL across 12 domains

Strong foundation

Data processing

Cleaning, sqlglot AST validation, deduplication, 80/10/10 split

Keep + improve

Tokenizer

Custom Byte-Level BPE, 4,096 vocabulary, SQL special tokens

Keep + improve

Model

Decoder-only Transformer; 6 layers, 8 heads, d_model 256

Core SLM

Attention

Causal self-attention + RoPE

Keep

Feed-forward

SwiGLU + RMSNorm

Keep

Training

AdamW, cosine schedule, gradient clipping, validation/perplexity

Keep + improve

Knowledge

194 SQL documents + ChromaDB hybrid search

Useful auxiliary component

SQL agent

Intent routing, schema injection, sqlglot validation, SQLite execution

Keep + strengthen

Inference

Autoregressive generation from checkpoint

Keep + improve

UI

Streamlit SQL/RAG/agent interface

Keep

Evaluation

22 benchmark cases + AST/keyword/table/execution metrics

Major expansion needed

The existing architecture is therefore not starting from zero. The main work is to improve the quality and coverage of the language-model training task, especially schema-aware generation and execution correctness.

3. Target Definition — What We Want to Build

Target name: Domain-Specific SQL Small Language Model (SQL-SLM)

Target capability:

Understand natural-language requests about relational data.

Condition generation on an explicit database schema.

Generate syntactically valid SQL.

Generate semantically correct SQL for unseen schemas.

Handle joins, aggregations, subqueries, CTEs, windows, filters, date logic, NULL semantics, and nested queries.

Support selected SQL dialects explicitly rather than pretending one SQL syntax fits all databases.

Reject or flag unsupported, unsafe, ambiguous, or schema-invalid requests.

Provide deterministic or controlled generation for enterprise use.

Operate fully inside a controlled environment without requiring an external foundation-model API.

4. Most Important Conceptual Change

The biggest enhancement should be moving from primarily learning 'SQL text' toward learning the mapping 'natural language + schema + constraints → SQL'.

Recommended training example:

<schema>
customers(customer_id, name, segment)
transactions(transaction_id, customer_id, amount, transaction_date, status)
</schema>

<question>
Show customers whose completed transactions exceeded 10 lakh last quarter.
</question>

<sql>
SELECT ...
</sql>

5. Enhancement Roadmap by Existing Stage

Stage 1 — Data Harvesting & Synthetic Generation

Current: real SQL repositories + procedural synthetic SQL.

Enhance with:

Build a dedicated NL-to-SQL dataset rather than relying mainly on raw SQL text.

Generate multiple natural-language questions for the same SQL query.

Generate multiple SQL formulations for the same intent where semantically equivalent.

Attach explicit schemas to every supervised example.

Add hard negative examples: plausible but incorrect table/column joins, wrong aggregation, wrong date range, wrong filter, wrong GROUP BY.

Generate ambiguity cases and train the model to ask for clarification or return a structured 'ambiguous' result.

Add business terminology and synonyms: revenue/turnover, customer/client, transaction/payment, etc.

Add SQL dialect tags and dialect-specific examples.

Generate realistic banking schemas only as a controlled domain extension, not as the sole training domain.

Split by schema/template, not only by rows, to prevent leakage between train and validation.

Recommended dataset families:

Dataset family

Purpose

SQL language corpus

Teach SQL syntax and structure

NL→SQL supervised pairs

Teach natural-language-to-SQL mapping

Schema-conditioned pairs

Teach schema grounding

Execution-valid pairs

Teach queries that actually run

Hard negatives

Teach error discrimination

Ambiguity/clarification

Teach safe behavior

Dialect pairs

Teach database-specific SQL

Banking-domain pairs

Teach domain vocabulary and realistic schemas

Stage 2 — Tokenization

Current: 4,096-token Byte-Level BPE.

Keep the BPE tokenizer as the baseline.

Measure tokenization efficiency on SQL keywords, identifiers, operators, numbers, dates, quoted identifiers, and schema names.

Add/verify special tokens for schema, question, SQL, dialect, database, table, column, and error/clarification boundaries.

Compare 4,096 vs 8,192 vocabulary on validation token efficiency before changing the production vocabulary.

Do not enlarge vocabulary merely to make the model appear bigger; measure impact on sequence length and training quality.

Stage 3 — Neural Model Architecture

Current: ~6.16M decoder-only Transformer with RoPE, RMSNorm and SwiGLU.

Enhancement path:

Priority

Enhancement

Reason

P0

Keep decoder-only causal LM

Already a valid language-model architecture

P0

Improve context length from 256 if data requires it

Schemas + questions + SQL can exceed 256 tokens

P1

Experiment with 8–12 layers / wider hidden size

Increase capacity only if benchmark gains justify it

P1

Use grouped/multi-query attention only if scaling requires it

Potential inference efficiency

P1

Consider RMSNorm/RoPE implementation refinements

Stability and consistency

P2

Explore parameter tying and embedding sharing

Keep model compact

Do not make model size the primary objective. First establish whether failures come from insufficient model capacity, poor training data, schema grounding, or evaluation leakage.

Stage 4 — Training

Current: supervised autoregressive training with prompt loss masking.

Retain next-token cross-entropy as the core language-model objective.

Train on schema + question → SQL sequences.

Track training loss, validation loss, perplexity, exact-match accuracy, execution accuracy, and invalid-SQL rate separately.

Use curriculum training: SQL fundamentals → joins/aggregations → advanced SQL → schema grounding → difficult cases.

Introduce supervised fine-tuning stages after base SQL language training.

Use checkpoint selection based on execution-oriented validation metrics, not validation loss alone.

Add early stopping and reproducible seeds/configuration tracking.

Run ablation experiments to prove which dataset/model changes actually improve performance.

Stage 5 — SQL Knowledge Base & RAG

Keep the 194-document SQL knowledge base and ChromaDB RAG as an auxiliary knowledge component. Do not confuse RAG with the language model itself.

Use RAG for SQL explanations, dialect documentation, business definitions, and examples.

Use the SLM for language modeling and SQL generation.

Add schema metadata retrieval as a separate first-class retrieval path.

Retrieve only relevant tables/columns instead of dumping entire schemas into context.

Add business glossary retrieval for enterprise terms.

Measure retrieval separately using Hit Rate, MRR, and NDCG before optimizing generation.

Stage 6 — SQL Agent & Database Layer

Current: intent router → schema injection → generation → sqlglot validation → execution.

Add SQL AST safety policies before execution.

Default to read-only SQL for analytical use cases.

Block or separately authorize INSERT/UPDATE/DELETE/DDL.

Add table/column authorization based on user role.

Add row-level security enforcement where supported.

Add query timeout, row limits, cost limits, and result-size limits.

Log user request, schema version, generated SQL, validation outcome, execution time, and result metadata.

Add a repair loop for invalid SQL using deterministic error feedback, with a strict retry limit.

Add execution-guided candidate selection: generate a small number of candidates, validate/execute safely, then choose the valid candidate using deterministic rules.

Never allow the generated SQL itself to bypass authorization controls.

Stage 7 — Inference & Application

Expose the SLM as a versioned local inference service.

Separate model inference from Streamlit so the model can later serve multiple applications.

Support temperature=0 / deterministic mode for enterprise SQL generation.

Return structured output such as SQL, validation status, warnings, and confidence signals rather than only raw text.

Show the user the generated SQL before execution for sensitive workflows.

Add an optional approval step.

Keep UI, inference, RAG, and database connectors as separate services/modules.

Stage 8 — Evaluation & Quality Assurance

This is the largest gap in the current project. The existing 22-case benchmark should become a much larger evaluation suite.

Expand from 22 cases to hundreds/thousands of cases.

Create train/validation/test separation by schema and query template.

Measure exact SQL match, but do not use it as the only metric.

Measure execution accuracy / result equivalence.

Measure AST validity.

Measure table-selection accuracy.

Measure column-selection accuracy.

Measure join correctness.

Measure aggregation correctness.

Measure filter correctness.

Measure dialect correctness.

Measure unsafe-query rejection.

Measure clarification accuracy for ambiguous requests.

Create a challenge set containing unseen schemas.

Create a banking challenge set separately from the general SQL benchmark.

6. New Components That Should Be Added

New component

Why it matters

Schema Encoder/Formatter

Makes schema conditioning explicit and consistent

NL→SQL Dataset Builder

Creates the actual supervised language-to-SQL task

Hard-Negative Generator

Teaches semantic error discrimination

Execution Validator

Tests whether generated SQL actually works

Semantic Result Evaluator

Checks result equivalence rather than string equality

Dialect Manager

Controls SQL Server/PostgreSQL/Oracle/etc. syntax

SQL Safety Guard

Prevents dangerous or unauthorized SQL

Business Glossary Retriever

Maps enterprise language to database concepts

Schema Retrieval

Retrieves only relevant database metadata

Clarification Handler

Handles ambiguous user questions

Model Registry

Versions tokenizer, model, dataset and configuration

Expanded Benchmark

Provides meaningful evidence of model quality

7. Training Pipeline — Recommended Final Form

The improved training pipeline should look like this:

Raw SQL + curated SQL + synthetic SQL
        ↓
Clean + normalize + sqlglot validation
        ↓
Schema extraction
        ↓
Natural-language question generation
        ↓
Hard negatives + ambiguity + dialect variants
        ↓
Leakage-safe train / validation / test split
        ↓
SQL-specific BPE tokenizer
        ↓
Base SQL language-model training
        ↓
Schema-conditioned NL→SQL training
        ↓
Supervised fine-tuning
        ↓
Execution-based evaluation
        ↓
Best checkpoint selection
        ↓
Private SQL-SLM inference service

8. What Should NOT Be Added

Do not add general internet knowledge just to make the model look like a general LLM.

Do not depend on OpenAI/Claude/Gemini for the core SQL generation path if the objective is a fully in-house SLM.

Do not assume RAG makes the Transformer itself a better language model; evaluate the SLM and RAG separately.

Do not judge success using only training loss or perplexity.

Do not use random train/test row splits when the same schema/query templates can appear in both sets.

Do not execute generated SQL directly against production databases without authorization and safety controls.

Do not increase parameters before proving that the current model is capacity-limited.

9. Definition of 'Actually an SQL Language Model'

The project should meet all of the following before making a strong SQL-SLM claim:

Requirement

Target evidence

Language model architecture

Decoder-only Transformer predicts next tokens

Language-model training

Autoregressive next-token objective

SQL specialization

Majority of training/evaluation language is SQL-related

Natural language understanding

NL questions mapped to SQL

Schema grounding

Correct SQL against schemas not seen during training

Generalization

Works on unseen schemas/templates

SQL correctness

High execution/result accuracy

Safety

Rejects or blocks unauthorized/dangerous SQL

Reproducibility

Versioned data, tokenizer, config and checkpoints

Independent evaluation

Held-out challenge set not used during development

10. Recommended Development Phases

Phase

Work

Outcome

Phase 1

Improve dataset + schema-conditioned examples

Strong SQL training corpus

Phase 2

Improve tokenizer/context and retrain baseline

Better SQL language model

Phase 3

Build schema-aware NL→SQL dataset

Core SQL-SLM capability

Phase 4

Expand benchmark + execution evaluation

Reliable quality measurement

Phase 5

Fine-tune on difficult SQL + hard negatives

Higher semantic accuracy

Phase 6

Add dialect and banking-domain tracks

Enterprise specialization

Phase 7

Add safety/RBAC/approval/audit layer

Production-ready private system

Phase 8

Package local inference service

Deployable in-house SQL-SLM

11. Recommended Architecture After Enhancement

User
  ↓
Private SQL-SLM Application
  ↓
Intent + Request Normalization
  ↓
Schema / Business Glossary Retrieval
  ↓
SQL SLM
  ↓
SQL AST Validation
  ↓
Security / RBAC / Policy Engine
  ↓
Execution Sandbox / Approved Database Connection
  ↓
Result Validation
  ↓
Response + SQL + Audit Record

12. Final Position

The current project already contains a genuine language-model core. The main missing capability is not 'becoming a language model'; it is becoming a stronger and more demonstrably capable SQL language model.

The highest-value upgrades are: schema-conditioned training, a much larger NL→SQL dataset, unseen-schema evaluation, execution/result-based metrics, hard-negative and ambiguity training, dialect handling, and enterprise SQL safety controls.

If these are implemented and validated, the project can be presented technically as a Domain-Specific SQL Small Language Model rather than merely a neural SQL generator or a rule-based SQL agent.

13. Existing Project Elements Referenced

This roadmap is based on the uploaded project architecture guide. That guide describes the current seven-stage pipeline, custom 4,096-token BPE tokenizer, 6.16M-parameter decoder-only Transformer, SQL training pipeline, 194-document SQL knowledge base, SQL agent, Streamlit application, and 22-case evaluation framework.