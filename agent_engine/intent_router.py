"""
Enhanced Generalized NLP Intent Router for Tiny SQL LLM.
Classifies any natural language input into functional intent categories:
- TEXT_TO_SQL: User specifically asks to query database tables, calculate values on data, or generate executable query statements for tables.
- CONCEPT_COMPARISON: User wants to compare two or more database concepts (e.g. WHERE vs HAVING, DELETE vs TRUNCATE, LIMIT vs TOP, PK vs FK).
- CONCEPT_EXPLANATION: User wants a tutorial, definition, roadmap, practice checklist, or explanation of a concept/topic.
- QUERY_OPTIMIZATION: User wants to optimize or analyze query performance.
"""

import re
from enum import Enum
from typing import Dict, Any, Tuple

class SQLIntent(Enum):
    TEXT_TO_SQL = "text_to_sql"
    CONCEPT_COMPARISON = "concept_comparison"
    CONCEPT_EXPLANATION = "concept_explanation"
    QUERY_OPTIMIZATION = "query_optimization"
    GENERAL_CHAT = "general_chat"

class SQLIntentRouter:
    def __init__(self):
        # 1. Educational, Learning & Tutorial Inquiries (Highest Priority for pedagogical prompts)
        self.learning_pattern = re.compile(
            r"\b(?:help\s+me\s+(?:to\s+)?(?:learn|understand|practice)|teach\s+me|roadmap|road\s*map|learning\s*path|learn\s*sql|how\s+to\s+learn|topics?|syllabus|curriculum|where\s+to\s+start|how\s+to\s+start|beginner\s+guide|study\s+plan|practice\s+topics?|interview\s+questions?|checklist|sequence\s+to\s+learn)\b",
            re.IGNORECASE
        )

        # 2. Linguistic Comparison Patterns
        self.comp_pattern = re.compile(
            r"\b(?:difference|versus|vs|compare|distinguish|comparison|contrast|between\s+.+\s+and)\b",
            re.IGNORECASE
        )

        # 3. Performance & Optimization Patterns
        self.opt_pattern = re.compile(
            r"\b(?:optimize|tune|slow\s+query|performance|execution\s+plan|indexing\s+strategy|sargable)\b",
            re.IGNORECASE
        )

        # 4. Explicit Database Table & Query Execution (Text-to-SQL) & Metadata
        self.table_action_pattern = re.compile(
            r"\b(?:write\s+(?:a\s+)?(?:sql\s+)?query\s+to|sql\s+query\s+to|query\s+to\s+(?:take|find|get|show|select|count|calculate)|find\s+all|show\s+all|select\s+all|top\s+\d+|highest\s+salaried|lowest\s+salaried|salary|total\s+spent|orders?|customers?|employees?|departments?|products?|sales_reps?|list\s+of\s+(?:\d+\s+)?tables?|list\s+tables?|show\s+tables?|database\s+tables?|tables?\s+in\s+connected|from\s+auditflow|in\s+auditflow)\b",
            re.IGNORECASE
        )

        # 5. Conceptual Inquiry & Definition Patterns
        self.expl_pattern = re.compile(
            r"\b(?:what\s+is|what\s+are|what\s+us|explain|how\s+does|how\s+to\s+write|why|define|meaning\s+of|overview\s+of|guide|tutorial|tell\s+me\s+about)\b",
            re.IGNORECASE
        )

    def route(self, query: str) -> Tuple[SQLIntent, Dict[str, Any]]:
        """
        Dynamically classifies any arbitrary user query into its functional intent.
        """
        q_clean = query.strip()
        q_lower = q_clean.lower()

        # 1. Check for Table Actions / Metadata first
        if self.table_action_pattern.search(q_lower):
            # If it's a pure concept definition inquiry like "what is primary key", keep it in explanation
            if re.search(r"\b(?:what\s+is\s+(?:primary\s+key|foreign\s+key|join|index|acid|cte|normalization))\b", q_lower):
                return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}
            return SQLIntent.TEXT_TO_SQL, {"query": q_clean}

        # 2. Educational / Learning Inquiries (e.g. "help me to learn StoreProcedure", "what is write sequence to learn SQL")
        if self.learning_pattern.search(q_lower):
            return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}

        # 3. Comparison Intent (e.g. "difference between WHERE and HAVING", "LIMIT vs TOP", "PK vs FK")
        if self.comp_pattern.search(q_lower):
            return SQLIntent.CONCEPT_COMPARISON, {"query": q_clean}

        # 4. Performance / Optimization Intent
        if self.opt_pattern.search(q_lower):
            return SQLIntent.QUERY_OPTIMIZATION, {"query": q_clean}

        # 5. Conceptual Inquiry / Definition
        if self.expl_pattern.search(q_lower):
            return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}

        # 6. Fallback based on question mark vs statement
        if q_clean.endswith("?") and any(q_lower.startswith(w) for w in ["how", "what is", "why", "when", "explain"]):
            return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}

        return SQLIntent.TEXT_TO_SQL, {"query": q_clean}

if __name__ == "__main__":
    router = SQLIntentRouter()
    test_queries = [
        "help me to learn StoreProcedure",
        "what is StoreProcedure ?",
        "what is execution order in SQL",
        "can you write a sql query to take 3 top highest salaried and 3 lowest salried employee from table",
        "what is windows function ?",
        "NTILE ?",
        "explain me NTILE in detail with code block as example",
        "what is write sequence to learn SQL ?",
        "difference between 1NF,2NF,3NF and BCNF ?",
        "what us difference between primary and foreign Key ?",
        "what is difference between Limit and TOP ?"
    ]
    print("\n[*] Testing Upgraded Robust Intent Router:")
    for q in test_queries:
        intent, _ = router.route(q)
        print(f"  Query: '{q}'\n  => Intent: [{intent.value.upper()}]\n")
