"""
Autonomous SQL Agent for Tiny LLM
Pipeline:
User Prompt -> Schema In-Context Injection -> Neural Model SQL Generation -> AST Parsing (sqlglot) -> Sandbox Execution -> Self-Repair Loop (on error) -> Dynamic Explanation.
"""

import sys
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import sqlglot
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.append(str(Path(__file__).resolve().parent.parent))

from inference.generate import TinyLLMInference
from evaluation.evaluate_sql import SQLEvaluator
from agent_engine.db_sandbox import EnterpriseDBSandbox
from agent_engine.schema_formatter import SchemaFormatter, DatabaseCatalog
from agent_engine.clarification_engine import ClarificationEngine

class SQLAgent:
    def __init__(self, checkpoint_path: Optional[str] = None, sandbox: Optional[EnterpriseDBSandbox] = None):
        self.bot = TinyLLMInference(checkpoint_path=checkpoint_path)
        self.sql_evaluator = SQLEvaluator()
        self.sandbox = sandbox if sandbox is not None else EnterpriseDBSandbox()
        self.clarification_engine = ClarificationEngine()
        if self.sandbox.engine is not None:
            self.catalog: DatabaseCatalog = SchemaFormatter.extract_from_sqlalchemy(self.sandbox.engine)
        elif self.sandbox.db_path:
            self.catalog = SchemaFormatter.extract_from_sqlite(self.sandbox.db_path)
        else:
            self.catalog = DatabaseCatalog()
        self.schema_str = SchemaFormatter.to_compact(self.catalog)

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
        return self.catalog

    def set_custom_schema_text(self, schema_text: str):
        """Sets custom schema from raw DDL or compact text."""
        if "CREATE TABLE" in schema_text.upper():
            self.catalog = SchemaFormatter.extract_from_ddl(schema_text)
            self.schema_str = SchemaFormatter.to_compact(self.catalog)
        else:
            self.schema_str = schema_text.strip()

    def is_metadata_query(self, prompt: str) -> bool:
        """Detects if user is asking to list tables, inspect schema, or check database objects."""
        p_lower = prompt.lower().strip()
        
        # Table/schema keywords
        table_keywords = ["table", "tables", "schema", "database structure", "entities", "relations"]
        has_table_kw = any(kw in p_lower for kw in table_keywords)
        
        meta_action_keywords = [
            "list", "show", "get", "what are", "which", "display", "tell me", "names of", 
            "name of", "all", "how many", "describe", "count of", "inventory", "can you list"
        ]
        has_meta_action = any(act in p_lower for act in meta_action_keywords)
        
        # If user is asking for table names / list of tables
        if has_table_kw and has_meta_action:
            # Exclude explicit data filtering queries like "show all users where salary > 1000"
            if not re.search(r"\b(?:where|group\s+by|order\s+by|sum\(|avg\(|having)\b", p_lower):
                return True

        patterns = [
            r"\b(?:list|show|get|display|view|name|names|count)\s+(?:of\s+)?(?:\w+\s+)?tables?\b",
            r"\btables?\s+(?:in|from|of)\s+(?:connected|this|the|my|database|db|postgres|postgresql|auditflow|ssms)\b",
            r"\b(?:what|which)\s+tables?\b",
            r"\b(?:all\s+tables?|table\s+names?|how\s+many\s+tables?)\b",
            r"\b(?:describe\s+schema|show\s+schema|list\s+schema)\b"
        ]
        return any(re.search(pat, p_lower) for pat in patterns)

    def get_relevant_schema_str(self, user_prompt: str, max_tables: int = 4) -> str:
        """
        If catalog has many tables (e.g. 11+ tables in auditflow), selects the most relevant tables
        for the user's prompt so prompt length remains well within the LLM's sequence context window.
        """
        if not self.catalog or not self.catalog.tables:
            return self.schema_str
        
        tables = list(self.catalog.tables.values())
        if len(tables) <= max_tables:
            return SchemaFormatter.to_compact(self.catalog)
        
        # Keyword matching on table name and column names
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
        
        # Sort by score descending
        scored_tables.sort(key=lambda x: x[0], reverse=True)
        selected_meta = [t for s, t in scored_tables if s > 0][:max_tables]
        if not selected_meta:
            # If no keyword matched, take the first max_tables
            selected_meta = [t for _, t in scored_tables[:max_tables]]
            
        selected_names = [t.name for t in selected_meta]
        return SchemaFormatter.to_compact(self.catalog, target_tables=selected_names)

    def extract_sql_from_text(self, text: str) -> Optional[str]:
        """Extracts and cleans SQL code blocks, tags, or standalone statements."""
        if not text:
            return None
        return self.bot.extract_sql(text)

    def generate_sql(self, user_prompt: str, error_feedback: Optional[str] = None, failed_sql: Optional[str] = None) -> str:
        """
        Prompts Tiny LLM with database schema context.
        Injects error feedback during self-repair attempts.
        """
        active_schema = self.get_relevant_schema_str(user_prompt, max_tables=4)
        
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

        extracted = gen_res.get("sql")
        return extracted or gen_res.get("raw_text", "").strip()

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
                
        return "\n\n".join(lines)

    def run(self, user_prompt: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Autonomous Agent Workflow with Execution-Guided Self-Repair:
        1. Checks for metadata / table inventory inspection.
        2. Generates initial SQL using schema conditioning.
        3. Validates AST safety and executes in Sandbox.
        4. If error occurs, engages Self-Repair loop with error feedback.
        5. Dynamically explains verified results.
        """
        t_start = time.time()

        # Handle Metadata Queries (e.g. "can you list name of 11 tables ?", "show all tables")
        if self.is_metadata_query(user_prompt) and self.catalog and self.catalog.tables:
            table_rows = [[i + 1, t.name, len(t.columns)] for i, t in enumerate(self.catalog.tables.values())]
            if self.sandbox.db_type == "postgresql":
                meta_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
            elif self.sandbox.db_type == "mssql":
                meta_sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME;"
            else:
                meta_sql = "SELECT name AS table_name FROM sqlite_master WHERE type='table' ORDER BY name;"

            # Try execution if DB is live
            exec_res = self.sandbox.execute_query(meta_sql)
            if not exec_res.get("success"):
                exec_res = {
                    "success": True,
                    "columns": ["#", "Table Name", "Column Count"],
                    "rows": table_rows,
                    "row_count": len(table_rows)
                }

            explanation = (
                f"Your connected database contains **{len(table_rows)} tables**:\n\n" +
                "\n".join([f"- **`{t.name}`** ({len(t.columns)} columns: `{', '.join([c.name for c in t.columns[:5]])}{'...' if len(t.columns)>5 else ''}`)" for t in self.catalog.tables.values()])
            )

            return {
                "prompt": user_prompt,
                "generated_sql": meta_sql,
                "success": True,
                "attempts": [{"attempt": 1, "sql": meta_sql, "success": True, "error": None, "duration_sec": 0.02}],
                "repaired": False,
                "total_attempts": 1,
                "execution": exec_res,
                "explanation": explanation,
                "total_latency_sec": round(time.time() - t_start, 3)
            }

        attempts = []
        cur_error = None
        cur_sql = None
        exec_res = None
        repaired = False

        for attempt in range(max_retries + 1):
            t_gen = time.time()
            if attempt == 0:
                cur_sql = self.generate_sql(user_prompt)
            else:
                cur_sql = self.generate_sql(user_prompt, error_feedback=cur_error, failed_sql=cur_sql)
                
            if not cur_sql.strip().endswith(";"):
                cur_sql = cur_sql.strip() + ";"

            # Available tables for safety check (allow information_schema for metadata)
            known_tables = list(self.catalog.tables.keys()) + ["tables", "columns", "information_schema", "sqlite_master"] if self.catalog and self.catalog.tables else None

            # Execute in connected database with table validation
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

        # Step 4: Explain Results
        if exec_res and exec_res["success"]:
            explanation = self.explain_results(user_prompt, cur_sql, exec_res["columns"], exec_res["rows"])
        else:
            explanation = f"⚠️ Query execution failed after {len(attempts)} attempt(s): {exec_res.get('error', 'Execution error') if exec_res else 'Unknown'}"

        total_latency = round(time.time() - t_start, 3)

        return {
            "prompt": user_prompt,
            "generated_sql": cur_sql,
            "success": exec_res["success"] if exec_res else False,
            "attempts": attempts,
            "repaired": repaired,
            "total_attempts": len(attempts),
            "execution": exec_res,
            "explanation": explanation,
            "total_latency_sec": total_latency
        }

    def run_with_consensus(self, user_prompt: str, k: int = 4) -> Dict[str, Any]:
        """
        Execution-Guided Multi-Candidate Generation with Consensus (Item 19):
        1. Checks for semantic ambiguity / missing parameters.
        2. Samples K candidate queries and evaluates AST / sandbox execution.
        3. Returns the highest-consensus candidate with detailed telemetry.
        """
        # 1. Ambiguity Check
        clarification = self.clarification_engine.analyze_query(user_prompt)
        if clarification.is_ambiguous:
            return {
                "prompt": user_prompt,
                "needs_clarification": True,
                "clarification": {
                    "type": clarification.ambiguity_type,
                    "message": clarification.clarification_message,
                    "options": clarification.suggested_options
                },
                "generated_sql": None,
                "success": False
            }

        # 2. Multi-Candidate Generation & Execution
        cand_res = self.bot.generate_candidates(
            question=user_prompt,
            schema=self.schema_str,
            dialect="sqlite",
            k=k,
            temperature=0.7,
            db_sandbox=self.sandbox
        )

        best_cand = cand_res["best_candidate"]
        exec_res = self.sandbox.execute_query(best_cand["sql"]) if best_cand["sql"] else None

        if exec_res and exec_res["success"]:
            explanation = self.explain_results(user_prompt, best_cand["sql"], exec_res["columns"], exec_res["rows"])
        else:
            explanation = f"⚠️ Execution error on best candidate: {exec_res.get('error') if exec_res else 'No valid SQL candidate'}"

        return {
            "prompt": user_prompt,
            "needs_clarification": False,
            "generated_sql": best_cand["sql"],
            "success": exec_res["success"] if exec_res else False,
            "consensus_confidence": cand_res["consensus_confidence"],
            "total_candidates": k,
            "ranked_candidates": cand_res["ranked_candidates"],
            "execution": exec_res,
            "explanation": explanation,
            "latency_sec": cand_res["total_time_sec"]
        }

if __name__ == "__main__":
    agent = SQLAgent()
    print("[*] Testing SQL Agent with Execution Verification & Consensus:")
    test_queries = [
        "List all customers from EMEA region",
        "Show top customers",
        "Show total budget by department name"
    ]
    for q in test_queries:
        print(f"\nPrompt: '{q}'")
        res = agent.run_with_consensus(q, k=3)
        if res.get("needs_clarification"):
            print(f"  [CLARIFICATION REQUIRED] {res['clarification']['message']}")
            for opt in res['clarification']['options']:
                print(f"    - {opt}")
        else:
            print(f"  -> Best SQL: {res['generated_sql']}")
            print(f"  -> Consensus Confidence: {res['consensus_confidence'] * 100:.0f}%")
            print(f"  -> Success: {res['success']}")

