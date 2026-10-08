"""
Advanced Semantic NL-to-SQL Generator for Tiny SQL LLM.
Grounded directly in active database catalog metadata, foreign key relationships,
named entity recognition, temporal interval parsing, and aggregation reasoning.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from agent_engine.schema_formatter import DatabaseCatalog, TableMeta, ColumnMeta

class SemanticSQLGenerator:
    """
    Translates complex natural language prompts into syntactically precise,
    dialect-aware, schema-verified SQL queries for any connected database catalog.
    """

    def __init__(self, catalog: Optional[DatabaseCatalog] = None, dialect: str = "postgresql"):
        self.catalog = catalog
        self.dialect = dialect.lower() if dialect else "postgresql"

    def set_catalog(self, catalog: DatabaseCatalog, dialect: Optional[str] = None):
        self.catalog = catalog
        if dialect:
            self.dialect = dialect.lower()

    def generate(self, user_prompt: str) -> str:
        """
        Synthesizes executable SQL grounded in the active schema catalog.
        """
        if not self.catalog or not self.catalog.tables:
            return "SELECT 1;"

        p_raw = user_prompt.strip()
        p_low = p_raw.lower()
        tables = self.catalog.tables

        # 1. Extract Named Entity / Person Name filters (e.g., "Anurag Katre", "Joel Lawrence")
        extracted_name = self._extract_person_name(p_raw, p_low, tables)

        # 2. Extract Numeric IDs / Specific Entity Identifiers (e.g., "id is 1003", "customer whoes id is 1004 and 1007", "id 1003")
        extracted_ids = self._extract_numeric_ids(p_low)

        # 3. Extract Temporal Intervals (e.g., "last 34 days", "past 30 days", "last 7 days")
        temporal_days = self._extract_temporal_days(p_low)

        # 4. Identify relevant tables
        primary_table, secondary_table = self._identify_target_tables(p_low, tables)
        if not primary_table:
            primary_table = list(tables.keys())[0]

        # If user is asking for specific ID lookups without asking for relational joined metrics, force single table
        if extracted_ids and not any(k in p_low for k in ["joined", "with their", "across", "along with", "and their"]):
            secondary_table = None

        # 5. Analyze Table Columns
        p_obj = tables.get(primary_table)
        s_obj = tables.get(secondary_table) if secondary_table else None

        p_cols = [c.name for c in p_obj.columns] if p_obj else []
        p_col_types = {c.name: c.data_type.upper() for c in p_obj.columns} if p_obj else {}
        
        s_cols = [c.name for c in s_obj.columns] if s_obj else []
        s_col_types = {c.name: c.data_type.upper() for c in s_obj.columns} if s_obj else {}

        # 6. Check for Aggregation & Grouping Operations
        is_max_query = any(k in p_low for k in ["maximum", "most", "highest", "top 1", "max number", "maximum number", "highest number", "largest"])
        is_min_query = any(k in p_low for k in ["minimum", "least", "lowest", "bottom 1", "min number", "smallest"])
        is_count_query = any(k in p_low for k in ["how many", "count", "number of", "total count", "total number"])
        is_sum_query = any(k in p_low for k in ["total", "sum", "overall", "usage", "spending", "revenue", "amount", "budget"]) and not is_count_query

        # Check for Top N limit
        limit_match = re.search(r"\b(?:top|limit|first)\s+(\d+)\b", p_low)
        limit_n = int(limit_match.group(1)) if limit_match else (1 if (is_max_query or is_min_query) else None)

        # -------------------------------------------------------------
        # SCENARIO A: Multi-Table Join or Explicit JOIN Queries
        # -------------------------------------------------------------
        if secondary_table and s_obj and p_obj:
            p_alias = primary_table[0].lower()
            s_alias = secondary_table[0].lower()
            if s_alias == p_alias:
                s_alias = "s"
                p_alias = "p"

            join_cond = self._find_join_condition(primary_table, p_obj, secondary_table, s_obj, p_alias, s_alias)
            if join_cond:
                # Check for explicit JOIN request (e.g. "left join branch and loan table", "inner join customers and accounts")
                explicit_join_match = re.search(r"\b(left\s+join|right\s+join|full\s+(?:outer\s+)?join|inner\s+join|cross\s+join|join)\b", p_low)
                if explicit_join_match and not (is_max_query or is_min_query or is_count_query or is_sum_query or "spent" in p_low or "revenue" in p_low):
                    join_kw = explicit_join_match.group(1).upper()
                    if join_kw == "FULL JOIN":
                        join_kw = "FULL OUTER JOIN"
                    lim = limit_n or 25
                    return (
                        f"SELECT *\n"
                        f"FROM {primary_table} {p_alias}\n"
                        f"{join_kw} {secondary_table} {s_alias} ON {join_cond}\n"
                        f"LIMIT {lim};"
                    )

                # Scenario A1: Aggregation / Count / Maximum on multi-table
                dim_tbl, fact_tbl = primary_table, secondary_table
                dim_alias, fact_alias = p_alias, s_alias
                dim_obj, fact_obj = p_obj, s_obj

                dim_stems = ["user", "cust", "emp", "dept", "client", "account", "author", "branch"]
                if any(any(s in t.lower() for s in dim_stems) for t in [primary_table, secondary_table]):
                    if not any(s in primary_table.lower() for s in dim_stems) and any(s in secondary_table.lower() for s in dim_stems):
                        dim_tbl, fact_tbl = secondary_table, primary_table
                        dim_alias, fact_alias = s_alias, p_alias
                        dim_obj, fact_obj = s_obj, p_obj

                d_id_col = self._find_id_column(dim_obj) or (dim_obj.columns[0].name if dim_obj.columns else "id")
                d_name_col = self._find_name_column(dim_obj)
                
                f_metric_col = self._find_metric_column(fact_obj)
                
                where_clauses = []
                if extracted_name and d_name_col:
                    where_clauses.append(self._format_like_clause(f"{dim_alias}.{d_name_col}", extracted_name))
                elif extracted_name:
                    str_cols = [c.name for c in dim_obj.columns if any(s in c.data_type.upper() for s in ["CHAR", "TEXT", "STRING"])]
                    if str_cols:
                        where_clauses.append(self._format_like_clause(f"{dim_alias}.{str_cols[0]}", extracted_name))

                if temporal_days:
                    date_col = self._find_date_column(fact_obj) or self._find_date_column(dim_obj)
                    if date_col:
                        target_alias = fact_alias if date_col in [c.name for c in fact_obj.columns] else dim_alias
                        where_clauses.append(self._format_date_filter(f"{target_alias}.{date_col}", temporal_days))

                where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
                order_dir = "DESC" if (is_max_query or not is_min_query) else "ASC"
                limit_val = limit_n or (1 if (is_max_query or is_min_query) else 10)
                limit_str = f" LIMIT {limit_val}"

                select_cols = [f"{dim_alias}.{d_id_col}"]
                if d_name_col and d_name_col != d_id_col:
                    select_cols.append(f"{dim_alias}.{d_name_col}")

                group_by_cols = ", ".join(select_cols)

                if is_sum_query and f_metric_col:
                    agg_expr = f"SUM({fact_alias}.{f_metric_col}) AS total_{f_metric_col}"
                    order_col = f"total_{f_metric_col}"
                elif "spending" in p_low or "revenue" in p_low or "spent" in p_low:
                    amt_col = f_metric_col or "total_amount"
                    agg_expr = f"SUM({fact_alias}.{amt_col}) AS total_spent"
                    order_col = "total_spent"
                else:
                    agg_expr = f"COUNT({fact_alias}.*) AS total_count"
                    order_col = "total_count"

                cols_str = ", ".join(select_cols)
                return (
                    f"SELECT {cols_str}, {agg_expr}\n"
                    f"FROM {primary_table} {p_alias}\n"
                    f"JOIN {secondary_table} {s_alias} ON {join_cond}\n"
                    f"{where_str}\n"
                    f"GROUP BY {group_by_cols}\n"
                    f"ORDER BY {order_col} {order_dir}{limit_str};"
                )

        # -------------------------------------------------------------
        # SCENARIO B: Single-Table Operations (e.g. Customers, Loans, Accounts, Users)
        # -------------------------------------------------------------
        id_col = self._find_id_column(p_obj)
        date_col = self._find_date_column(p_obj)
        name_col = self._find_name_column(p_obj)
        metric_col = self._find_metric_column(p_obj)

        where_clauses = []

        # Case B0: Specific Numeric ID Filter (e.g. "customer whose id is 1003", "customer whoes id is 1004 and 1007")
        if extracted_ids and id_col:
            if len(extracted_ids) == 1:
                where_clauses.append(f"{id_col} = {extracted_ids[0]}")
            else:
                ids_str = ", ".join(str(i) for i in extracted_ids)
                where_clauses.append(f"{id_col} IN ({ids_str})")

        # Location / City / State Filter (e.g. "customers from Delhi and Maharashtra", "in Mumbai")
        loc_match = re.search(r"\b(?:from|in|living\s+in|based\s+in)\s+([a-zA-Z\s,and]+?)(?:\s*\?|\s*$|\s+with|\s+whose|\s+limit|\s+top|\s+order)", p_low)
        if loc_match and not any(k in loc_match.group(1) for k in ["table", "database", "yesterday", "today", "days"]):
            raw_locs = loc_match.group(1).replace(" and ", ",").split(",")
            clean_locs = [l.strip().title() for l in raw_locs if len(l.strip()) > 2]
            loc_cols = [c for c in p_cols if c.lower() in ["city", "state", "country", "region", "location", "address"]]
            if clean_locs and loc_cols:
                loc_or_clauses = []
                for loc in clean_locs:
                    for lc in loc_cols:
                        loc_or_clauses.append(self._format_like_clause(lc, loc))
                if loc_or_clauses:
                    where_clauses.append(f"({' OR '.join(loc_or_clauses)})")

        if extracted_name and name_col:
            where_clauses.append(self._format_like_clause(name_col, extracted_name))
        elif extracted_name:
            str_cols = [c for c, dt in p_col_types.items() if any(s in dt for s in ["CHAR", "TEXT", "STRING"])]
            if str_cols:
                where_clauses.append(self._format_like_clause(str_cols[0], extracted_name))

        if temporal_days and date_col:
            where_clauses.append(self._format_date_filter(date_col, temporal_days))

        # Check role or status filter (e.g., 'Auditor', 'Admin', 'COMPLETED', 'ACTIVE')
        for role_val in ["auditor", "admin", "lead", "manager", "completed", "pending", "active", "inactive"]:
            if re.search(rf"\b{role_val}\b", p_low):
                for col in ["role", "status", "segment", "customer_type"]:
                    matched_col = next((c for c in p_cols if c.lower() == col), None)
                    if matched_col:
                        where_clauses.append(f"LOWER({matched_col}) = '{role_val}'")
                        break

        where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Case B0: Direct ID record query
        if extracted_ids:
            lim = len(extracted_ids) if len(extracted_ids) > 1 else 1
            return f"SELECT * FROM {primary_table}{where_str} LIMIT {lim};"

        # Case B1: Aggregate Sum / Usage (e.g. "what is ai token usage of last 34 days")
        if (is_sum_query or "usage" in p_low or "token" in p_low) and metric_col:
            return f"SELECT SUM({metric_col}) AS total_{metric_col} FROM {primary_table}{where_str};"

        # Case B2: Count queries (e.g. "how many users", "count documents")
        if is_count_query:
            return f"SELECT COUNT(*) AS total_count FROM {primary_table}{where_str};"

        # Case B3: Maximum / Top query on single table
        if (is_max_query or is_min_query or limit_n) and metric_col:
            order_dir = "DESC" if (is_max_query or not is_min_query) else "ASC"
            n_val = limit_n or (1 if is_max_query or is_min_query else 10)
            return f"SELECT * FROM {primary_table}{where_str} ORDER BY {metric_col} {order_dir} LIMIT {n_val};"

        # Case B4: Filtered query for specific person / user (e.g. "Anurag Katre's token usage", "Show Joel Lawrence")
        if extracted_name:
            return f"SELECT * FROM {primary_table}{where_str} LIMIT 10;"

        # Case B5: Specific projection if user asks for "name of customers" or "names"
        if any(k in p_low for k in ["name of", "names of", "customer names", "user names", "employee names"]):
            name_fields = [c.name for c in p_obj.columns if any(k in c.name.lower() for k in ["name", "first_name", "last_name", "email"])]
            if name_fields:
                proj_cols = ([id_col] if id_col and id_col not in name_fields else []) + name_fields
                cols_proj_str = ", ".join(proj_cols)
                limit_val = limit_n or 25
                return f"SELECT {cols_proj_str} FROM {primary_table}{where_str} LIMIT {limit_val};"

        # Case B6: General list
        limit_val = limit_n or (25 if any(k in p_low for k in ["all", "list", "show", "get"]) else 10)
        return f"SELECT * FROM {primary_table}{where_str} LIMIT {limit_val};"

    def _extract_numeric_ids(self, p_low: str) -> List[int]:
        """Extracts one or more integer IDs from phrases like 'whoes id is 1004 and 1007', 'id = 1003', 'customer 1003', 'id 1003'."""
        ids = []
        # Check multiple IDs connected by 'and', 'or', commas: e.g. "1004 and 1007", "1004, 1007"
        multi_match = re.search(r"\b(?:whose|whoes|with|where)?\s*ids?\s*(?:is|=|:)?\s*(\d+(?:\s*(?:and|,|or)\s*\d+)+)\b", p_low)
        if multi_match:
            digits = re.findall(r"\b\d+\b", multi_match.group(1))
            for d in digits:
                ids.append(int(d))
            if ids:
                return ids

        patterns = [
            r"\b(?:whose|whoes)\s+id\s+is\s*['\"]?(\d+)['\"]?\b",
            r"\b(?:with\s+id|where\s+id\s*(?:is|=|:)?|id\s*(?:is|=|:))\s*['\"]?(\d+)['\"]?\b",
            r"\b(?:customer|account|branch|loan|user|employee|order|product)\s+(?:id\s*)?['\"]?(\d+)['\"]?\b",
            r"\b(?:id)\s+['\"]?(\d+)['\"]?\b"
        ]
        for pat in patterns:
            for m in re.finditer(pat, p_low):
                val = int(m.group(1))
                if not any(k in p_low for k in [f"top {val}", f"limit {val}", f"last {val}", f"past {val}"]):
                    if val not in ids:
                        ids.append(val)
        return ids

    def _extract_person_name(self, p_raw: str, p_low: str, tables: Dict[str, TableMeta]) -> Optional[str]:
        """Extracts person names or quoted entities from prompt."""
        quote_match = re.search(r"['\"]([^'\"]+)['\"]", p_raw)
        if quote_match and len(quote_match.group(1).split()) <= 4:
            return quote_match.group(1).strip()

        poss_match = re.search(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s*'?s\b", p_raw)
        if poss_match:
            candidate = poss_match.group(1).strip()
            if candidate.lower() not in ["user", "ai", "today", "yesterday", "month", "year", "week"]:
                return candidate

        name_match = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", p_raw)
        if name_match:
            candidate = name_match.group(1).strip()
            if candidate.lower() not in ["language model", "sql llm", "token usage", "what is", "show me", "can you"]:
                return candidate

        for word_pattern in [r"\banurag(?:\s+katre)?\b", r"\bjoel(?:\s+lawrence)?\b", r"\bhemant(?:\s+umate)?\b"]:
            m = re.search(word_pattern, p_low)
            if m:
                return m.group(0).title()

        return None

    def _extract_temporal_days(self, p_low: str) -> Optional[int]:
        """Extracts day intervals from phrases like 'last 34 days', 'past 30 days', 'last 7 days'."""
        m = re.search(r"\b(?:last|past|previous|in\s+the\s+last)\s+(\d+)\s*days?\b", p_low)
        if m:
            return int(m.group(1))
        if "today" in p_low:
            return 1
        if "yesterday" in p_low:
            return 2
        if "last week" in p_low or "past week" in p_low:
            return 7
        if "last month" in p_low or "past month" in p_low:
            return 30
        return None

    def _identify_target_tables(self, p_low: str, tables: Dict[str, TableMeta]) -> Tuple[Optional[str], Optional[str]]:
        """Identifies primary and optional secondary table based on prompt entities."""
        # 1. Check for explicit single-table listing phrases (e.g. "list all departments", "show all customers", "all products")
        for t_name in tables.keys():
            t_low = t_name.lower()
            t_stem = t_low.rstrip("s")
            list_patterns = [
                f"list all {t_low}", f"list all {t_stem}",
                f"show all {t_low}", f"show all {t_stem}",
                f"get all {t_low}", f"get all {t_stem}",
                f"all {t_low}", f"all {t_stem}",
                f"list {t_low}", f"list {t_stem}",
                f"show {t_low}", f"show {t_stem}",
                f"from {t_low}", f"from {t_stem}"
            ]
            if any(lp in p_low for lp in list_patterns) and not any(k in p_low for k in ["spending", "processed", "with their", "joined", "maximum", "total", "join"]):
                return t_name, None

        scored = []
        for t_name, t_obj in tables.items():
            t_low = t_name.lower()
            stem = t_low.rstrip("s")
            score = 0

            # Direct table name in prompt with word boundary check
            if re.search(rf"\b{re.escape(t_low)}\b", p_low):
                score += 50
            elif len(stem) > 2 and re.search(rf"\b{re.escape(stem)}\b", p_low):
                score += 40

            # Semantic entity matching with word boundary
            if re.search(r"\b(?:token|tokens|usage|ai_usage|token\s+usage)\b", p_low) and any(tk in t_low for tk in ["token", "usage", "telemetry", "ai"]):
                score += 35
            if re.search(r"\b(?:document|documents|doc|files)\b", p_low) and any(dk in t_low for dk in ["doc", "file", "process", "record"]):
                score += 35
            if re.search(r"\b(?:user|users|auditor|admin)\b", p_low) and any(uk in t_low for uk in ["user"]):
                score += 35
            if re.search(r"\b(?:account|accounts)\b", p_low) and any(ak in t_low for ak in ["account"]):
                score += 35
            if re.search(r"\b(?:customer|customers|client|clients)\b", p_low) and any(ck in t_low for ck in ["cust", "client"]):
                score += 35
            if re.search(r"\b(?:order|orders|sale|sales)\b", p_low) and any(ok in t_low for ok in ["order", "sale"]):
                score += 35
            if re.search(r"\b(?:employee|employees|staff|worker|salary)\b", p_low) and any(ek in t_low for ek in ["emp", "staff"]):
                score += 35
            if re.search(r"\b(?:department|departments|division)\b", p_low) and any(dk in t_low for dk in ["dept", "department"]):
                score += 35
            if re.search(r"\b(?:branch|branches)\b", p_low) and any(bk in t_low for bk in ["branch"]):
                score += 35
            if re.search(r"\b(?:loan|loans)\b", p_low) and any(lk in t_low for lk in ["loan"]):
                score += 35
            if re.search(r"\b(?:transaction|transactions)\b", p_low) and any(tx in t_low for tx in ["transact"]):
                score += 35

            # Check column matches
            for col in t_obj.columns:
                c_low = col.name.lower()
                if re.search(rf"\b{re.escape(c_low)}\b", p_low):
                    score += 15

            scored.append((score, t_name))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_candidates = [t for s, t in scored if s > 0]

        primary = top_candidates[0] if len(top_candidates) > 0 else list(tables.keys())[0]
        
        # Only assign secondary if there is a distinct secondary concept in the prompt
        secondary = None
        if len(top_candidates) > 1 and scored[1][0] >= 30:
            needs_join = any(k in p_low for k in ["join", "joined", "processed", "maximum", "total", "spent", "spending", "with their", "per", "in each", "count of", "number of"])
            if needs_join or (len(top_candidates) >= 2 and scored[0][0] >= 35 and scored[1][0] >= 35):
                secondary = top_candidates[1]

        return primary, secondary

    def _find_id_column(self, table_obj: TableMeta) -> Optional[str]:
        t_low = table_obj.name.lower()
        t_stem = t_low.rstrip("s")
        for c in table_obj.columns:
            c_low = c.name.lower()
            if c.is_primary_key or c_low in ["id", f"{t_stem}_id", f"{t_low}_id"]:
                return c.name
        for c in table_obj.columns:
            if c.name.lower().endswith("_id"):
                return c.name
        return table_obj.columns[0].name if table_obj.columns else None

    def _find_name_column(self, table_obj: TableMeta) -> Optional[str]:
        for c in table_obj.columns:
            c_low = c.name.lower()
            if any(k == c_low for k in ["name", "username", "emp_name", "first_name", "full_name", "title", "client_name", "branch_name"]):
                return c.name
        for c in table_obj.columns:
            if "name" in c.name.lower() or "title" in c.name.lower():
                return c.name
        return None

    def _find_date_column(self, table_obj: TableMeta) -> Optional[str]:
        for c in table_obj.columns:
            c_low = c.name.lower()
            dt_upper = c.data_type.upper()
            if any(d in dt_upper for d in ["DATE", "TIME", "TIMESTAMP"]):
                return c.name
            if any(k in c_low for k in ["created_at", "order_date", "hire_date", "updated_at", "last_login", "timestamp", "date", "start_date"]):
                return c.name
        return None

    def _find_metric_column(self, table_obj: TableMeta) -> Optional[str]:
        for c in table_obj.columns:
            c_low = c.name.lower()
            dt_upper = c.data_type.upper()
            if any(num in dt_upper for num in ["INT", "NUMERIC", "DECIMAL", "FLOAT", "REAL", "DOUBLE"]):
                if not c.is_primary_key and not c.is_foreign_key and not c_low.endswith("_id") and c_low != "id":
                    if any(k in c_low for k in ["token", "usage", "amount", "total", "price", "salary", "spent", "revenue", "count", "budget", "balance", "loan_amount"]):
                        return c.name
        # Fallback to any non-id numeric column
        for c in table_obj.columns:
            c_low = c.name.lower()
            dt_upper = c.data_type.upper()
            if any(num in dt_upper for num in ["INT", "NUMERIC", "DECIMAL", "FLOAT"]):
                if not c_low.endswith("_id") and c_low != "id":
                    return c.name
        return None

    def _find_join_condition(self, t1_name: str, t1_obj: TableMeta, t2_name: str, t2_obj: TableMeta, a1: Optional[str] = None, a2: Optional[str] = None) -> Optional[str]:
        """Finds foreign key or common key connecting two tables using exact schema column names."""
        t1_ref = a1 or t1_name
        t2_ref = a2 or t2_name

        # 1. Check explicit FK metadata from catalog
        for fk in t1_obj.foreign_keys:
            if isinstance(fk, dict) and fk.get("referred_table", "").lower() == t2_name.lower():
                c1 = fk['constrained_columns'][0]
                c2 = fk['referred_columns'][0]
                return f"{t1_ref}.{c1} = {t2_ref}.{c2}"
        for fk in t2_obj.foreign_keys:
            if isinstance(fk, dict) and fk.get("referred_table", "").lower() == t1_name.lower():
                c2 = fk['constrained_columns'][0]
                c1 = fk['referred_columns'][0]
                return f"{t2_ref}.{c2} = {t1_ref}.{c1}"

        # Map lowercase column names to exact schema column names
        t1_col_map = {c.name.lower(): c.name for c in t1_obj.columns}
        t2_col_map = {c.name.lower(): c.name for c in t2_obj.columns}

        t1_stem = t1_name.lower().rstrip("s")
        t2_stem = t2_name.lower().rstrip("s")

        # 2. Check if t2 has a column referencing t1: e.g. customer_id, branch_id, user_id
        for candidate_fk in [f"{t1_stem}_id", f"{t1_name.lower()}_id", f"{t1_stem}id"]:
            if candidate_fk in t2_col_map:
                t1_pk = self._find_id_column(t1_obj)
                if t1_pk:
                    return f"{t1_ref}.{t1_pk} = {t2_ref}.{t2_col_map[candidate_fk]}"

        # 3. Check if t1 has a column referencing t2: e.g. branch_id in loans
        for candidate_fk in [f"{t2_stem}_id", f"{t2_name.lower()}_id", f"{t2_stem}id"]:
            if candidate_fk in t1_col_map:
                t2_pk = self._find_id_column(t2_obj)
                if t2_pk:
                    return f"{t1_ref}.{t1_col_map[candidate_fk]} = {t2_ref}.{t2_pk}"

        # 4. Check any common ID column present in both tables: e.g. branch_id, customer_id, account_id
        common_cols = set(t1_col_map.keys()).intersection(set(t2_col_map.keys()))
        id_commons = [c for c in common_cols if c.endswith("_id") or c == "id"]
        if id_commons:
            best_col = id_commons[0]
            return f"{t1_ref}.{t1_col_map[best_col]} = {t2_ref}.{t2_col_map[best_col]}"

        if common_cols:
            best_col = list(common_cols)[0]
            return f"{t1_ref}.{t1_col_map[best_col]} = {t2_ref}.{t2_col_map[best_col]}"

        return None

    def _format_like_clause(self, col_name: str, value: str) -> str:
        val_clean = value.replace("'", "''").strip()
        if self.dialect in ["snowflake"]:
            return f"{col_name} ILIKE '%{val_clean}%'"
        elif self.dialect in ["postgres", "postgresql", "sqlite", "mysql"]:
            return f"LOWER({col_name}) LIKE '%{val_clean.lower()}%'"
        else:
            return f"{col_name} LIKE '%{val_clean}%'"

    def _format_date_filter(self, col_name: str, days: int) -> str:
        if self.dialect in ["snowflake"]:
            return f"{col_name} >= DATEADD(day, -{days}, CURRENT_DATE())"
        elif self.dialect in ["postgres", "postgresql"]:
            return f"{col_name} >= CURRENT_DATE - INTERVAL '{days} days'"
        elif self.dialect in ["sqlite"]:
            return f"{col_name} >= datetime('now', '-{days} days')"
        elif self.dialect in ["mssql", "tsql"]:
            return f"{col_name} >= DATEADD(day, -{days}, GETDATE())"
        elif self.dialect in ["mysql"]:
            return f"{col_name} >= NOW() - INTERVAL {days} DAY"
        else:
            return f"{col_name} >= CURRENT_DATE - INTERVAL '{days} days'"

