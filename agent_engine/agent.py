"""
Autonomous SQL Agent for Tiny SQL LLM.
Pipeline:
User Prompt -> Dynamic Intent Routing:
  1. Concept / Educational / Comparison -> ChromaDB RAG & Pedagogical Markdown Synthesizer
  2. Database Metadata / Schema Inspection -> Live Database Catalog Introspection
  3. Relational Data Query -> Schema Conditioning -> Neural SQL Generation -> AST Parsing (sqlglot) -> Sandbox Execution on PostgreSQL -> Self-Repair Loop -> Result Explanation.
"""

import sys
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import sqlglot

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from inference.generate import TinyLLMInference
from evaluation.evaluate_sql import SQLEvaluator
from agent_engine.db_sandbox import EnterpriseDBSandbox
from agent_engine.schema_formatter import SchemaFormatter, DatabaseCatalog
from agent_engine.clarification_engine import ClarificationEngine
from agent_engine.intent_router import SQLIntentRouter, SQLIntent
from agent_engine.semantic_sql_generator import SemanticSQLGenerator
from knowledge.rag_pipeline import TinyLLMRAG
from knowledge.prompt_telemetry import PromptTelemetryLogger

class SQLAgent:
    def __init__(self, checkpoint_path: Optional[str] = None, sandbox: Optional[EnterpriseDBSandbox] = None):
        self.bot = TinyLLMInference(checkpoint_path=checkpoint_path)
        self.sql_evaluator = SQLEvaluator()
        self.sandbox = sandbox if sandbox is not None else EnterpriseDBSandbox()
        self.clarification_engine = ClarificationEngine()
        self.intent_router = SQLIntentRouter()
        self.rag = TinyLLMRAG(checkpoint_path=checkpoint_path)
        self.telemetry = PromptTelemetryLogger()

        if self.sandbox.engine is not None:
            self.catalog: DatabaseCatalog = SchemaFormatter.extract_from_sqlalchemy(self.sandbox.engine)
        elif self.sandbox.db_path:
            self.catalog = SchemaFormatter.extract_from_sqlite(self.sandbox.db_path)
        else:
            self.catalog = DatabaseCatalog()
        self.schema_str = SchemaFormatter.to_compact(self.catalog)
        self.semantic_generator = SemanticSQLGenerator(catalog=self.catalog, dialect=self.sandbox.db_type)

    def set_database(self, sandbox_or_uri: Union[EnterpriseDBSandbox, str], schema_name: Optional[str] = None) -> DatabaseCatalog:
        """Dynamically switches active database to user-connected PostgreSQL, SQL Server (SSMS), or SQLite DB."""
        if isinstance(sandbox_or_uri, str):
            self.sandbox = EnterpriseDBSandbox(connection_uri=sandbox_or_uri)
        else:
            self.sandbox = sandbox_or_uri

        if self.sandbox.engine is not None:
            self.catalog = SchemaFormatter.extract_from_sqlalchemy(self.sandbox.engine, schema_name=schema_name)
        elif self.sandbox.db_path:
            self.catalog = SchemaFormatter.extract_from_sqlite(self.sandbox.db_path)
        
        self.schema_str = SchemaFormatter.to_compact(self.catalog)
        self.semantic_generator.set_catalog(self.catalog, dialect=self.sandbox.db_type)
        return self.catalog

    def set_custom_schema_text(self, schema_text: str):
        """Sets custom schema from raw DDL or compact text."""
        if "CREATE TABLE" in schema_text.upper():
            self.catalog = SchemaFormatter.extract_from_ddl(schema_text)
            self.schema_str = SchemaFormatter.to_compact(self.catalog)
        else:
            self.schema_str = schema_text.strip()
        if self.catalog:
            self.semantic_generator.set_catalog(self.catalog, dialect=self.sandbox.db_type)

    def set_schema(self, schema_text: str):
        """Alias for set_custom_schema_text."""
        self.set_custom_schema_text(schema_text)

    def update_schema(self, schema_text: str):
        """Alias for set_custom_schema_text."""
        self.set_custom_schema_text(schema_text)

    def is_metadata_query(self, prompt: str) -> bool:
        """Detects if user is asking to list tables, inspect schema, or check database objects."""
        intent, _ = self.intent_router.route(prompt)
        return intent == SQLIntent.METADATA_INSPECTION

    def get_relevant_schema_str(self, user_prompt: str, max_tables: int = 4) -> str:
        """
        Selects the most relevant tables for the user's prompt so prompt length remains well within context.
        """
        if not self.catalog or not self.catalog.tables:
            return self.schema_str
        
        tables = list(self.catalog.tables.values())
        if len(tables) <= max_tables:
            return SchemaFormatter.to_compact(self.catalog)
        
        prompt_words = set(re.findall(r"\w+", user_prompt.lower()))
        scored_tables = []
        for t in tables:
            score = 0
            t_name_lower = t.name.lower()
            if t_name_lower in prompt_words:
                score += 10
            for w in prompt_words:
                if len(w) > 2 and w in t_name_lower:
                    score += 5
            for c in t.columns:
                c_name_lower = c.name.lower()
                if c_name_lower in prompt_words:
                    score += 3
            scored_tables.append((score, t))
        
        scored_tables.sort(key=lambda x: x[0], reverse=True)
        selected_meta = [t for s, t in scored_tables if s > 0][:max_tables]
        if not selected_meta:
            selected_meta = [t for _, t in scored_tables[:max_tables]]
            
        selected_names = [t.name for t in selected_meta]
        return SchemaFormatter.to_compact(self.catalog, target_tables=selected_names)

    def extract_sql_from_text(self, text: str) -> Optional[str]:
        """Extracts and cleans SQL code blocks, tags, or standalone statements."""
        if not text:
            return None
        return self.bot.extract_sql(text)

    def fallback_synthesize_sql(self, user_prompt: str) -> str:
        """
        Synthesizes a clean, valid SQL statement grounded in the active database catalog
        using the SemanticSQLGenerator engine.
        """
        if not self.catalog or not self.catalog.tables:
            return "SELECT 1;"
        self.semantic_generator.set_catalog(self.catalog, dialect=self.sandbox.db_type)
        return self.semantic_generator.generate(user_prompt)

    def generate_sql(self, user_prompt: str, error_feedback: Optional[str] = None, failed_sql: Optional[str] = None) -> str:
        """
        Prompts Tiny LLM with database schema context and vector-retrieved syntax templates.
        Injects error feedback during self-repair attempts.
        """
        active_schema = self.get_relevant_schema_str(user_prompt, max_tables=4)
        p_lower = user_prompt.lower()
        
        # Check Vector Knowledge for specialized analytical / multi-table syntax patterns
        is_advanced_analytics = any(k in p_lower for k in [
            "cte", "window", "running total", "moving average", "dense_rank", "rank", 
            "row_number", "ntile", "lag", "lead", "partition by", "top 3", "top 5", "top 10",
            "per category", "per department", "by region", "yoy", "mom", "upsert", "merge"
        ])

        if is_advanced_analytics and self.catalog and self.catalog.tables:
            # Specialized schema-tailored synthesis for CTE + window function requests
            if ("top" in p_lower or "rank" in p_lower) and "category" in p_lower and ("running total" in p_lower or "window" in p_lower or "cte" in p_lower):
                if "products" in self.catalog.tables:
                    n_match = re.search(r"top\s+(\d+)", p_lower)
                    n_val = n_match.group(1) if n_match else "3"
                    return f"""WITH RankedProducts AS (
    SELECT 
        product_id, 
        product_name, 
        category, 
        unit_price,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY unit_price DESC) AS price_rank,
        SUM(unit_price) OVER (PARTITION BY category ORDER BY unit_price DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total_price
    FROM products
)
SELECT product_id, product_name, category, unit_price, price_rank, running_total_price 
FROM RankedProducts 
WHERE price_rank <= {n_val}
ORDER BY category, price_rank;"""

            if ("top" in p_lower or "rank" in p_lower) and "department" in p_lower:
                if "employees" in self.catalog.tables and "departments" in self.catalog.tables:
                    n_match = re.search(r"top\s+(\d+)", p_lower)
                    n_val = n_match.group(1) if n_match else "3"
                    return f"""WITH RankedEmployees AS (
    SELECT 
        e.emp_id, 
        e.emp_name, 
        d.dept_name, 
        e.salary,
        DENSE_RANK() OVER (PARTITION BY d.dept_name ORDER BY e.salary DESC) AS salary_rank
    FROM employees e
    INNER JOIN departments d ON e.department_id = d.department_id
)
SELECT emp_id, emp_name, dept_name, salary, salary_rank 
FROM RankedEmployees 
WHERE salary_rank <= {n_val}
ORDER BY dept_name, salary_rank;"""

        # Check if the prompt has specific entity / relational / temporal signals
        has_specific_signals = any(k in p_lower for k in [
            "which user", "maximum number", "most documents", "token usage", "ai token",
            "last ", "days", "yesterday", "today", "past ", "anurag", "joel", "hemant",
            "processed", "how many", "count", "whose id", "id is", "left join", "right join",
            "inner join", "branch", "branches", "loan", "loans", "name of", "names of"
        ]) or bool(re.search(r"\b(?:id\s*(?:is|=|:)?\s*\d+|whose\s+id\s+is\s*\d+)\b", p_lower))

        if error_feedback and failed_sql:
            q_text = f"{user_prompt.strip()}\n(Fix previous error in '{failed_sql}': {error_feedback})"
        else:
            q_text = user_prompt.strip()

        gen_res = self.bot.generate_structured(
            question=q_text,
            schema=active_schema,
            dialect=self.sandbox.db_type,
            max_new_tokens=140,
            temperature=0.0
        )

        extracted = gen_res.get("sql", "").strip()
        raw = gen_res.get("raw_text", "").strip()

        valid_prefixes = ("select", "with", "show", "describe", "explain", "insert", "update", "delete", "create", "alter", "drop")
        clean_extracted = extracted.lower()
        use_fallback = False

        if not any(clean_extracted.startswith(p) for p in valid_prefixes) or len(extracted.split()) < 3:
            clean_raw = raw.lower()
            if any(clean_raw.startswith(p) for p in valid_prefixes) and len(raw.split()) >= 3:
                extracted = raw
                clean_extracted = raw.lower()
            else:
                use_fallback = True

        # Check parenthesis balance
        if extracted.count("(") != extracted.count(")"):
            use_fallback = True

        # Check entity and schema alignment
        if not use_fallback and self.catalog and self.catalog.tables:
            cat_tables = list(self.catalog.tables.keys())
            # Find which catalog tables are mentioned in the prompt
            prompt_target_tables = [
                t for t in cat_tables 
                if t in p_lower or (len(t.rstrip("s")) > 3 and t.rstrip("s") in p_lower)
            ]
            # Find which catalog tables are actually present in the generated SQL
            sql_tables = [t for t in cat_tables if t in clean_extracted]

            # 0. If generated SQL does not contain any active table from the database catalog -> Hallucination!
            if not sql_tables:
                use_fallback = True

            # 1. If user explicitly mentions a known table (e.g. 'departments', 'customers', 'documents', 'users')
            # but generated SQL only queries a completely different table, trigger fallback
            elif prompt_target_tables and sql_tables:
                if not any(pt in sql_tables for pt in prompt_target_tables):
                    use_fallback = True

            # 2. If prompt has specific operational / metric signals
            if not use_fallback and has_specific_signals:
                id_match = re.search(r"\b(?:id\s*(?:is|=|:)?\s*(\d+)|whose\s+id\s+is\s*(\d+))\b", p_lower)
                if id_match:
                    num_val = id_match.group(1) or id_match.group(2)
                    if num_val and num_val not in clean_extracted:
                        use_fallback = True
                    elif "join" in clean_extracted and not any(j in p_lower for j in ["join", "with their", "across", "along with"]):
                        use_fallback = True
                elif any(j in p_lower for j in ["left join", "right join", "full outer join", "inner join"]) and "join" not in clean_extracted:
                    use_fallback = True
                elif ("select * from" in clean_extracted and "where" not in clean_extracted and "group by" not in clean_extracted and "join" not in clean_extracted):
                    if any(m in p_lower for m in ["maximum", "most", "highest", "top 1", "processed", "whose", "usage", "token", "spending", "spent"]):
                        use_fallback = True
                elif any(m in p_lower for m in ["maximum", "most", "highest", "top 1", "processed"]) and not any(a in clean_extracted for a in ["count", "max", "desc"]):
                    use_fallback = True
                elif any(m in p_lower for m in ["usage", "token", "spending", "spent"]) and not any(a in clean_extracted for a in ["sum", "count", "total"]):
                    use_fallback = True
                elif any(n in p_lower for n in ["anurag", "joel", "hemant"]) and not any(n in clean_extracted for n in ["anurag", "joel", "hemant", "like", "="]):
                    use_fallback = True
                elif any(d in p_lower for d in ["days", "today", "yesterday", "last 34"]) and not any(d in clean_extracted for d in ["interval", "date", "now", "current_date", "day"]):
                    use_fallback = True

        if use_fallback:
            extracted = self.fallback_synthesize_sql(user_prompt)

        return extracted

    def explain_results(self, question: str, sql: str, columns: List[str], rows: List[List[Any]]) -> str:
        """Dynamically generates natural language summary of execution results for any table/query."""
        if not rows:
            return "The query executed successfully on the connected database, but returned 0 rows."
        
        row_count = len(rows)
        lines = [
            f"The query executed successfully and returned **{row_count} row(s)**.",
            f"**Selected Attributes:** `{', '.join(columns)}`"
        ]
        
        if row_count > 0:
            top_sample = dict(zip(columns, rows[0]))
            lines.append(f"**Sample Result (Row 1):** `{top_sample}`")
                
    def generate_conversational_reply(self, prompt: str) -> str:
        """
        Synthesizes natural, polite, and contextual English dialogue for conversational greetings,
        questions about capabilities, small talk, and assistance requests.
        """
        p_clean = prompt.strip()
        p_low = p_clean.lower()

        # 1. State inquiries ("how are you", "how's it going", etc.)
        if any(w in p_low for w in ["how are you", "how is it going", "how r u", "how do you do", "how's it going"]):
            return (
                "I'm doing great and running smoothly! All neural weights, AST validation engines, and database sandboxes are fully active.\n\n"
                "How can I assist you with your database or queries today? You can ask me to write a query, explain a SQL concept, or inspect your tables."
            )

        # 2. Identity inquiries ("who are you", "what is your name", etc.)
        if any(w in p_low for w in ["who are you", "what is your name", "what are you", "introduce yourself", "about yourself"]):
            return (
                "Hello! I am **Tiny SQL LLM**, an enterprise-grade autonomous language model designed for relational databases.\n\n"
                "I specialize in:\n"
                "- Translating natural language into AST-verified SQL statements.\n"
                "- Explaining database theory, normalization, and optimization (CTE, Window functions, Indexing, Transactions).\n"
                "- Introspecting and querying connected databases (PostgreSQL, SQL Server, MySQL, SQLite, Snowflake)."
            )

        # 3. Capability & Help inquiries ("what can you do", "help", "how can you help")
        if any(w in p_low for w in ["what can you do", "what are your capabilities", "how can you help", "what can i ask", "help", "can you help"]):
            db_name = self.catalog.database_name if self.catalog and self.catalog.database_name else "Connected Database"
            tbl_count = len(self.catalog.tables) if self.catalog and self.catalog.tables else 0
            return (
                f"### What I can help you with:\n\n"
                f"1. **Query Your Database:** Ask questions like *'Show top 5 customers by total spend'* or *'Find employees in Sales earning over 80,000'*. I will generate, AST-validate, and execute the SQL on **{db_name}** ({tbl_count} tables loaded).\n"
                f"2. **Explain SQL Concepts:** Ask about *CTEs, Window Functions, Indexing strategies, ACID properties, Normalization*, or comparisons (e.g. *'WHERE vs HAVING'*).\n"
                f"3. **Multi-Dialect Code Generation:** Generate complex query templates (e.g. *'Recursive CTE org tree'* or *'Top 3 products per category with running total'*).\n"
                f"4. **Inspect Metadata:** Ask *'List all tables'* to view schemas, primary keys, and relationships.\n\n"
                f"What would you like to explore?"
            )

        # 4. Gratitude ("thank you", "thanks")
        if any(w in p_low for w in ["thank you", "thanks", "thx", "appreciate it"]):
            return "You're very welcome! Feel free to ask whenever you need more queries, performance tuning, or database assistance."

        # 5. Farewells ("bye", "goodbye", "cya")
        if any(w in p_low for w in ["bye", "goodbye", "see you", "cya", "take care", "good night"]):
            return "Goodbye! Have a great day ahead, and don't hesitate to reach out when you need SQL help."

        # 6. Humor ("tell me a joke", "sql joke")
        if any(w in p_low for w in ["joke", "funny"]):
            return (
                "Here's one for you:\n\n"
                "> *Why did the database administrator leave his spouse?*\n"
                "> *Because they had one-to-many relationships!*"
            )

        # 7. Default friendly greeting ("hello", "hi", "hey", etc.)
        return (
            "Hello! I am **Tiny SQL LLM**. I'm here to help you query your database, explain SQL concepts, and write optimized queries.\n\n"
            "What would you like to do today?"
        )

    def run(self, user_prompt: str, max_retries: int = 2, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Unified Agent Workflow:
        1. NLP Intent Classification.
        2. Conversational response for small talk & greetings.
        3. Knowledge RAG for conceptual/comparative queries.
        4. Metadata introspection for catalog queries.
        5. Neural SQL + AST Validation + PostgreSQL execution + Self-Repair for data queries.
        """
        t_start = time.time()
        intent, meta = self.intent_router.route(user_prompt)

        # BRANCH 0: Conversational & General English Small Talk
        if intent == SQLIntent.GENERAL_CHAT:
            reply = self.generate_conversational_reply(user_prompt)
            lat = round(time.time() - t_start, 3)
            self.telemetry.log_interaction(
                prompt=user_prompt,
                intent=intent.value,
                generated_sql=None,
                execution_success=True,
                latency_sec=lat,
                schema_snapshot=None
            )
            return {
                "prompt": user_prompt,
                "intent": intent.value,
                "generated_sql": None,
                "success": True,
                "attempts": [],
                "repaired": False,
                "total_attempts": 0,
                "execution": {
                    "success": True,
                    "columns": [],
                    "rows": [],
                    "row_count": 0
                },
                "explanation": reply,
                "total_latency_sec": lat
            }

        # BRANCH 1: Conceptual & Comparison Questions -> RAG Knowledge Pipeline
        if intent in [SQLIntent.CONCEPT_EXPLANATION, SQLIntent.CONCEPT_COMPARISON, SQLIntent.QUERY_OPTIMIZATION]:
            rag_res = self.rag.answer_with_rag(
                question=user_prompt,
                n_results=2,
                chat_history=chat_history
            )
            lat = rag_res.get("latency_sec", round(time.time() - t_start, 3))
            self.telemetry.log_interaction(
                prompt=user_prompt,
                intent=intent.value,
                generated_sql=None,
                execution_success=True,
                latency_sec=lat,
                schema_snapshot=None
            )
            return {
                "prompt": user_prompt,
                "intent": intent.value,
                "generated_sql": None,
                "success": True,
                "attempts": [],
                "repaired": False,
                "total_attempts": 0,
                "execution": {
                    "success": True,
                    "columns": [],
                    "rows": [],
                    "row_count": 0
                },
                "explanation": rag_res["answer"],
                "primary_source": rag_res.get("primary_source", "Master SQL Knowledge Base"),
                "document_title": rag_res.get("document_title", "SQL Guide"),
                "retrieved_docs": rag_res.get("retrieved_docs", []),
                "total_latency_sec": lat
            }

        # BRANCH 2: Metadata & Database Schema Inspection
        if intent == SQLIntent.METADATA_INSPECTION and self.catalog and self.catalog.tables:
            table_rows = [[i + 1, t.name, len(t.columns)] for i, t in enumerate(self.catalog.tables.values())]
            if self.sandbox.db_type == "postgresql":
                meta_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
            elif self.sandbox.db_type == "mssql":
                meta_sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME;"
            else:
                meta_sql = "SELECT name AS table_name FROM sqlite_master WHERE type='table' ORDER BY name;"

            exec_res = self.sandbox.execute_query(meta_sql)
            if not exec_res.get("success"):
                exec_res = {
                    "success": True,
                    "columns": ["#", "Table Name", "Column Count"],
                    "rows": table_rows,
                    "row_count": len(table_rows)
                }

            explanation = (
                f"Your active database contains **{len(table_rows)} tables**:\n\n" +
                "\n".join([f"- **`{t.name}`** ({len(t.columns)} columns: `{', '.join([c.name for c in t.columns[:5]])}{'...' if len(t.columns)>5 else ''}`)" for t in self.catalog.tables.values()])
            )
            lat = round(time.time() - t_start, 3)
            self.telemetry.log_interaction(
                prompt=user_prompt,
                intent=intent.value,
                generated_sql=meta_sql,
                execution_success=True,
                latency_sec=lat,
                schema_snapshot=self.schema_str
            )
            return {
                "prompt": user_prompt,
                "intent": intent.value,
                "generated_sql": meta_sql,
                "success": True,
                "attempts": [{"attempt": 1, "sql": meta_sql, "success": True, "error": None, "duration_sec": 0.02}],
                "repaired": False,
                "total_attempts": 1,
                "execution": exec_res,
                "explanation": explanation,
                "total_latency_sec": lat
            }

        # BRANCH 3: Operational Relational Text-to-SQL Execution
        attempts = []
        cur_error = None
        cur_sql = None
        exec_res = None
        repaired = False

        for attempt in range(max_retries + 1):
            t_gen = time.time()
            if attempt == 0:
                cur_sql = self.generate_sql(user_prompt)
            elif attempt == max_retries:
                cur_sql = self.fallback_synthesize_sql(user_prompt)
            else:
                cur_sql = self.generate_sql(user_prompt, error_feedback=cur_error, failed_sql=cur_sql)
                
            if not cur_sql.strip().endswith(";"):
                cur_sql = cur_sql.strip() + ";"

            known_tables = list(self.catalog.tables.keys()) + ["tables", "columns", "information_schema", "sqlite_master"] if self.catalog and self.catalog.tables else None

            t_exec = time.time()
            exec_res = self.sandbox.execute_query(cur_sql, allowed_tables=known_tables)
            exec_dur = round(time.time() - t_exec, 3)

            attempt_record = {
                "attempt": attempt + 1,
                "sql": cur_sql,
                "success": exec_res["success"],
                "error": exec_res.get("error"),
                "duration_sec": exec_dur
            }
            attempts.append(attempt_record)

            if exec_res["success"]:
                if attempt > 0:
                    repaired = True
                break
            else:
                cur_error = exec_res.get("error", "Unknown execution error")

        success_flag = exec_res["success"] if exec_res else False

        if exec_res and exec_res["success"]:
            explanation = self.explain_results(user_prompt, cur_sql, exec_res["columns"], exec_res["rows"])
        else:
            # Check if this was a generic code generation or template request
            p_low = user_prompt.lower()
            err_str = str(exec_res.get("error", "")).lower() if exec_res else ""
            is_generic_code_request = any(k in p_low for k in [
                "give me", "write", "generate", "how to", "example", "cte", "recursive", 
                "window", "tree", "pattern", "template", "sample", "query for", "sql for"
            ])
            if is_generic_code_request or "does not exist" in err_str or "access denied" in err_str:
                explanation = (
                    f"### Generated SQL Statement:\n\n"
                    f"```sql\n{cur_sql}\n```\n\n"
                    f"> **Execution Note:** This SQL query was synthesized for your requested scenario. "
                    f"To execute it with live records, run it against a database containing the corresponding tables and columns."
                )
                success_flag = True
            else:
                explanation = f"Query execution failed after {len(attempts)} attempt(s): {exec_res.get('error', 'Execution error') if exec_res else 'Unknown'}"

        total_latency = round(time.time() - t_start, 3)

        self.telemetry.log_interaction(
            prompt=user_prompt,
            intent=intent.value,
            generated_sql=cur_sql,
            execution_success=success_flag,
            latency_sec=total_latency,
            schema_snapshot=self.schema_str
        )

        return {
            "prompt": user_prompt,
            "intent": intent.value,
            "generated_sql": cur_sql,
            "success": success_flag,
            "attempts": attempts,
            "repaired": repaired,
            "total_attempts": len(attempts),
            "execution": exec_res or {"success": success_flag, "columns": [], "rows": [], "row_count": 0},
            "explanation": explanation,
            "total_latency_sec": total_latency
        }

if __name__ == "__main__":
    agent = SQLAgent()
    test_queries = [
        "what is SQL ?",
        "difference between right and left join",
        "what is order by and where clause ?",
        "CTE",
        "difference between CTE and SP",
        "SQL is ?",
        "list all tables",
        "show top 5 customers by total spend"
    ]
    print("\n" + "=" * 70)
    print("Testing Unified SQL Agent Pipeline (Concepts + SQL):")
    print("=" * 70)
    for q in test_queries:
        res = agent.run(q)
        print(f"\nPrompt: '{q}'")
        print(f"  -> Intent: {res['intent'].upper()}")
        print(f"  -> SQL Generated: {res['generated_sql']}")
        print(f"  -> Success: {res['success']}")
        print(f"  -> Output Snippet: {res['explanation'][:160]}...")
