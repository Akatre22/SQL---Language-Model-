"""
Comprehensive NLP Intent Router for Tiny SQL LLM.
Classifies any natural language input into functional intent categories:
- TEXT_TO_SQL: User specifically asks to query database tables, calculate values on data, or generate executable query statements for tables.
- CONCEPT_COMPARISON: User wants to compare two or more database concepts (e.g. WHERE vs HAVING, DELETE vs TRUNCATE, LIMIT vs TOP, PK vs FK, LEFT vs RIGHT JOIN, CTE vs SP).
- CONCEPT_EXPLANATION: User wants a tutorial, definition, roadmap, practice checklist, or explanation of a concept/topic/acronym.
- QUERY_OPTIMIZATION: User wants to optimize or analyze query performance.
- METADATA_INSPECTION: User asks to list tables, inspect schema, or check database objects.
"""

import re
from enum import Enum
from typing import Dict, Any, Tuple

class SQLIntent(Enum):
    TEXT_TO_SQL = "text_to_sql"
    CONCEPT_COMPARISON = "concept_comparison"
    CONCEPT_EXPLANATION = "concept_explanation"
    QUERY_OPTIMIZATION = "query_optimization"
    METADATA_INSPECTION = "metadata_inspection"
    GENERAL_CHAT = "general_chat"

class SQLIntentRouter:
    def __init__(self):
        # 1. Standalone Core SQL Keywords & Acronyms
        self.sql_concept_terms = {
            "sql", "rdbms", "dbms", "cte", "sp", "acid", "ddl", "dml", "dcl", "tcl",
            "1nf", "2nf", "3nf", "bcnf", "join", "joins", "left join", "right join",
            "inner join", "outer join", "cross join", "full outer join", "subquery",
            "trigger", "triggers", "view", "views", "cursor", "cursors", "stored procedure",
            "stored procedures", "transaction", "transactions", "index", "indexes",
            "clustered index", "non clustered index", "normalization", "denormalization",
            "group by", "order by", "having", "where", "where clause", "order by clause",
            "having clause", "group by clause", "exists", "union", "union all", "case when",
            "coalesce", "nullif", "row_number", "rank", "dense_rank", "ntile", "lead",
            "lag", "window function", "window functions", "aggregate function", "partition by",
            "primary key", "foreign key", "unique key", "check constraint", "default constraint",
            "execution order", "query plan", "explain analyze", "sargable", "isolation levels"
        }

        # 2. Educational, Learning & Roadmap Inquiries
        self.learning_pattern = re.compile(
            r"\b(?:help\s+me\s+(?:to\s+)?(?:learn|understand|practice)|teach\s+me|roadmap|road\s*map|learning\s*path|learn\s*sql|how\s+to\s+learn|topics?|syllabus|curriculum|where\s+to\s+start|how\s+to\s+start|beginner\s+guide|study\s+plan|practice\s+topics?|interview\s+questions?|checklist|sequence\s+to\s+learn)\b",
            re.IGNORECASE
        )

        # 3. Linguistic Comparison Patterns
        self.comp_pattern = re.compile(
            r"\b(?:difference|versus|vs|compare|distinguish|comparison|contrast|between\s+.+\s+and)\b",
            re.IGNORECASE
        )

        # 4. Performance & Optimization Patterns
        self.opt_pattern = re.compile(
            r"\b(?:optimize|tune|slow\s+query|performance|execution\s+plan|indexing\s+strategy|sargable)\b",
            re.IGNORECASE
        )

        # 5. Metadata / Schema Inspection Patterns
        self.metadata_pattern = re.compile(
            r"\b(?:list|show|get|display|view|name|names|count)\s+(?:of\s+)?(?:\w+\s+)?tables?\b|\btables?\s+(?:in|from|of)\s+(?:connected|this|the|my|database|db|postgres|postgresql)\b|\b(?:what|which)\s+tables?\b|\b(?:all\s+tables?|table\s+names?|how\s+many\s+tables?|describe\s+schema|show\s+schema|list\s+schema)\b",
            re.IGNORECASE
        )

        # 6. Conceptual Inquiry & Definition Patterns
        self.expl_pattern = re.compile(
            r"\b(?:what\s+is|what\s+are|what\s+us|explain|how\s+does|how\s+to\s+write|why|define|definition|meaning\s+of|overview\s+of|guide|tutorial|tell\s+me\s+about)\b",
            re.IGNORECASE
        )

        # 7. Conversational, Greetings & General English Chat Patterns
        self.general_greetings = {
            "hi", "hello", "hey", "hola", "namaste", "greetings", "good morning",
            "good afternoon", "good evening", "good day", "howdy", "sup", "yo", "hai"
        }
        self.general_chat_regex = re.compile(
            r"^(?:hi|hello|hey|hola|namaste|greetings|good\s+(?:morning|afternoon|evening|day)|howdy|sup|yo)[\s!.,?]*$|"
            r"\b(?:how\s+are\s+you|how\s+is\s+it\s+going|how\s+r\s+u|how\s+do\s+you\s+do|how\'s\s+it\s+going)\b|"
            r"\b(?:who\s+are\s+you|what\s+is\s+your\s+name|what\s+are\s+you|introduce\s+yourself|tell\s+me\s+about\s+yourself)\b|"
            r"\b(?:what\s+(?:can|do)\s+you\s+do|what\s+are\s+your\s+capabilities|how\s+can\s+you\s+help|what\s+can\s+i\s+ask)\b|"
            r"\b(?:thank\s+you|thanks|thank\s+u|thx|thanks\s+a\s+lot|thank\s+you\s+so\s+much)\b|"
            r"\b(?:bye|goodbye|see\s+you|cya|take\s+care|have\s+a\s+good\s+day)\b|"
            r"^(?:help|help\s+me|can\s+you\s+help\s+me)[\s!.,?]*$|"
            r"\b(?:tell\s+me\s+a\s+joke|sql\s+joke|joke)\b",
            re.IGNORECASE
        )

        # 8. Explicit Database Operational Actions (Text-to-SQL)
        self.table_action_pattern = re.compile(
            r"\b(?:write\s+(?:a\s+)?(?:sql\s+)?query\s+to|sql\s+query\s+to|query\s+to\s+(?:take|find|get|show|select|count|calculate)|find\s+all|show\s+all|select\s+all|top\s+\d+|highest\s+salaried|lowest\s+salaried|salary\s*>|salary\s*<|salary\s*=|total\s+spent|orders\s+by|customers\s+from|employees\s+in)\b",
            re.IGNORECASE
        )

    def route(self, query: str) -> Tuple[SQLIntent, Dict[str, Any]]:
        """
        Dynamically and accurately classifies user queries.
        """
        q_clean = query.strip()
        q_lower = q_clean.lower()
        q_normalized = re.sub(r"[^\w\s]", " ", q_lower).strip()
        q_words = q_normalized.split()

        # 0. Conversational & General English Small Talk (e.g. "Hello", "how are you ?", "who are you")
        if q_normalized in self.general_greetings or self.general_chat_regex.search(q_clean):
            # Ensure it's not actually an operational SQL prompt (e.g., "Hello, find all orders")
            if not any(k in q_lower for k in ["select ", "from customers", "from employees", "from orders", "group by", "order by", "where salary", "top 5"]):
                return SQLIntent.GENERAL_CHAT, {"query": q_clean}

        # 0.5 Business Intelligence & Report Advisory Queries (e.g. "what KPIs can be considered", "recommend metrics for dashboard", "how to build a report")
        advisory_pattern = re.compile(
            r"\b(?:what\s+(?:kpis?|metrics?)|which\s+(?:kpis?|metrics?)|kpis?\s+(?:can|should|to)|recommend\s+(?:kpis?|metrics?|reports?)|report\s+(?:ideas?|design|guidelines?)|dashboard\s+(?:ideas?|metrics?)|best\s+practices\s+for\s+(?:reporting|analytics|kpis?))\b",
            re.IGNORECASE
        )
        if advisory_pattern.search(q_lower):
            return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}

        # 1. Metadata Inspection (e.g., "list all tables", "show database tables")
        if self.metadata_pattern.search(q_lower):
            if not re.search(r"\b(?:where|group\s+by|order\s+by|sum\(|avg\(|having)\b", q_lower):
                return SQLIntent.METADATA_INSPECTION, {"query": q_clean}

        # 1. Comparison Intent Check (e.g. "difference between right and left join", "difference between CTE and SP", "WHERE vs HAVING")
        if self.comp_pattern.search(q_lower):
            # If the user is comparing SQL concepts/terms, route to CONCEPT_COMPARISON
            if any(term in q_lower for term in self.sql_concept_terms) or not any(k in q_lower for k in ["salary", "spent", "revenue", "price", "count", "where"]):
                return SQLIntent.CONCEPT_COMPARISON, {"query": q_clean}

        # Operational data query indicators (e.g. asking for records, token usage, users, documents, numbers, dates, banking entities)
        has_operational_data_signals = any(k in q_lower for k in [
            "token", "tokens", "usage", "ai token", "token usage", "document", "documents",
            "processed", "user", "users", "employee", "employees", "customer", "customers",
            "order", "orders", "product", "products", "department", "departments",
            "branch", "branches", "loan", "loans", "account", "accounts", "transaction", "transactions",
            "table", "tables", "database", "salary", "spent", "spending", "revenue", "budget", "amount", "price", "balance",
            "last ", "past ", "days", "yesterday", "today", "this month", "which user",
            "who processed", "who earned", "whose", "how many", "count", "maximum number",
            "total number", "average number", "most documents", "highest", "whose id", "id is", "id = ", "id=", "id "
        ]) or bool(re.search(r"\b(?:id\s*(?:is|=|:)?\s*\d+|from\s+\w+)\b", q_lower))

        # Check for explicit query generation commands (e.g., "give me sql query to left join branch and loan table", "write a query to find...")
        has_explicit_query_request = bool(re.search(
            r"\b(?:give\s+me\s+(?:a\s+)?(?:sql\s+)?query\s+to|write\s+(?:a\s+)?(?:sql\s+)?query\s+to|can\s+you\s+(?:give|write|provide|show|generate)\s+(?:me\s+)?(?:a\s+)?(?:sql\s+)?query\s+to|query\s+to\s+(?:join|left\s+join|right\s+join|select|find|get|show|list|filter|calculate))\b",
            q_lower
        ))
        if has_explicit_query_request:
            return SQLIntent.TEXT_TO_SQL, {"query": q_clean}

        # 3. Check for Standalone Single Concept or Short Acronym (e.g., "CTE", "SP", "ACID", "3NF")
        if (q_normalized in self.sql_concept_terms or (len(q_words) <= 3 and any(w in self.sql_concept_terms for w in q_words))) and not has_operational_data_signals:
            if not any(act in q_lower for act in ["select ", "insert ", "update ", "delete ", "where salary", "customers with", "top 5 ", "from "]):
                return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}

        # 4. Inverted conceptual inquiries (e.g., "SQL is ?", "CTE meaning ?", "Indexes are ?")
        if re.search(r"\b(?:is\s*\?|are\s*\?|meaning\s*\?|purpose\s*\?)\b", q_lower) and not has_operational_data_signals:
            if any(term in q_lower for term in self.sql_concept_terms):
                return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}

        # 5. Explicit Concept, Syntax & Generic Query Inquiries (e.g., "give me sql query for - Recursive CTE", "syntax of dense rank", "what is SQL ?")
        self.syntax_pattern = re.compile(
            r"\b(?:syntax|syntax\s+of|syntax\s+for|syntax\s+template|give\s+me\s+(?:a\s+)?(?:sql\s+)?query\s+for\s+(?:recursive|cte|window|dense_rank|rank|lead|lag|running\s+total|org\s+tree|hierarchy|pivot|upsert|merge)|show\s+syntax|template\s+for|code\s+template|example\s+syntax|how\s+to\s+write\s+syntax|pattern\s+for)\b",
            re.IGNORECASE
        )
        if self.syntax_pattern.search(q_lower) and not has_operational_data_signals:
            return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}

        # 6. Conceptual Explanation & Educational Questions (e.g., "what is normalization", "explain ACID", "explain left join")
        if (self.expl_pattern.search(q_lower) or self.learning_pattern.search(q_lower)) and not has_operational_data_signals:
            # Only if mentioning SQL theoretical concepts (e.g., ACID, CTE, B-Tree, Normalization, Isolation levels)
            if any(term in q_lower for term in self.sql_concept_terms) or self.learning_pattern.search(q_lower):
                return SQLIntent.CONCEPT_EXPLANATION, {"query": q_clean}

        # 7. Performance Optimization
        if self.opt_pattern.search(q_lower) and not has_operational_data_signals:
            return SQLIntent.QUERY_OPTIMIZATION, {"query": q_clean}

        # 8. Default to Text-to-SQL Operational Execution
        return SQLIntent.TEXT_TO_SQL, {"query": q_clean}

if __name__ == "__main__":
    router = SQLIntentRouter()
    test_cases = [
        "what is SQL ?",
        "difference between right and left join",
        "what is order by and where clause ?",
        "CTE",
        "difference between CTE and SP",
        "SQL is ?",
        "list all tables",
        "show top 5 customers by total spend",
        "find all employees in engineering with salary > 100000"
    ]
    print("\n" + "=" * 65)
    print("Testing Comprehensive NLP Intent Router:")
    print("=" * 65)
    for tc in test_cases:
        intent, _ = router.route(tc)
        print(f"  Query: '{tc}'\n  -> INTENT: [{intent.value.upper()}]\n")
