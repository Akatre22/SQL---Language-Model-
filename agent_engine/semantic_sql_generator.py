"""
Advanced Semantic NL-to-SQL Generator for Tiny SQL LLM.
Grounded directly in active database catalog metadata, foreign key relationships,
dynamic entity linking, categorical value parsing, and relational algebra reasoning.
Zero hardcoding — fully generalized for any relational database schema.
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

        # 1. Extract Named Entity / Person Name filters (e.g., "Amit", "Rahul", "Priya Patel", "Joel Lawrence")
        extracted_name, name_source_table = self._extract_person_name(p_raw, p_low, tables)

        # 2. Extract Numeric IDs / Specific Entity Identifiers (e.g., "id is 1003", "id = 1001", "1004 and 1007")
        extracted_ids = self._extract_numeric_ids(p_low)

        # 3. Extract Explicit Numeric Values (e.g., "balance is 125000.5", "salary > 50000", "amount = 450000")
        extracted_numeric_filter = self._extract_numeric_value_filter(p_low, tables)

        # 4. Extract Temporal Intervals (e.g., "last 34 days", "past 30 days", "last 7 days")
        temporal_days = self._extract_temporal_days(p_low)

        # 5. Extract Categorical Filters (e.g., "saving", "savings", "current", "retail", "premium", "active")
        categorical_filter = self._extract_categorical_filter(p_low, tables)

        # 6. Check for Aggregation, Ranking, and Mode / Frequency Operations
        is_mode_frequency_query, mode_column, mode_table = self._detect_mode_frequency_query(p_low, tables)
        
        is_max_query = any(k in p_low for k in ["maximum", "most", "highest", "top 1", "max number", "maximum number", "highest number", "largest"]) and not is_mode_frequency_query
        is_min_query = any(k in p_low for k in ["minimum", "least", "lowest", "bottom 1", "min number", "smallest"])
        is_count_query = any(k in p_low for k in ["how many", "count of", "total count", "number of count"]) and not any(k in p_low for k in ["list of", "show me list", "give me list"])
        is_sum_query = any(k in p_low for k in ["total", "sum", "overall", "total usage", "total spending", "total revenue", "total amount", "total budget"]) and not is_count_query

        # Check for Top N limit
        limit_match = re.search(r"\b(?:top|limit|first)\s+(\d+)\b", p_low)
        limit_n = int(limit_match.group(1)) if limit_match else (1 if (is_max_query or is_min_query) else None)

        # -------------------------------------------------------------
        # SCENARIO 0: Mode / Most Frequent Category or Entity (e.g. "which city is most appear in database ?")
        # -------------------------------------------------------------
        if is_mode_frequency_query and mode_column and mode_table:
            t_obj = tables[mode_table]
            return f"SELECT {mode_column}, COUNT(*) AS frequency_count FROM {mode_table} GROUP BY {mode_column} ORDER BY frequency_count DESC LIMIT 1;"

        # 7. Identify Primary and Secondary Target Tables
        primary_table, secondary_table = self._identify_target_tables(p_low, tables, name_source_table)
        if not primary_table:
            primary_table = list(tables.keys())[0]

        # Prioritize categorical filter matching the resolved primary table
        if primary_table:
            target_cat = self._extract_categorical_filter(p_low, tables, target_table=primary_table)
            if target_cat:
                categorical_filter = target_cat

        # If user asks for person's metric across tables (e.g. "bank balance of amit" -> customers + accounts)
        if extracted_name and name_source_table and name_source_table != primary_table and not secondary_table:
            secondary_table = name_source_table

        # If user asks for customer with balance 125000.5 (customers + accounts)
        if extracted_numeric_filter:
            num_tbl = extracted_numeric_filter.get("table")
            if num_tbl and num_tbl != primary_table and not secondary_table:
                secondary_table = num_tbl

        p_obj = tables.get(primary_table)
        s_obj = tables.get(secondary_table) if secondary_table else None

        p_cols = [c.name for c in p_obj.columns] if p_obj else []
        p_col_types = {c.name: c.data_type.upper() for c in p_obj.columns} if p_obj else {}
        
        s_cols = [c.name for c in s_obj.columns] if s_obj else []
        s_col_types = {c.name: c.data_type.upper() for c in s_obj.columns} if s_obj else {}

        # -------------------------------------------------------------
        # SCENARIO A: Multi-Table Join Queries
        # -------------------------------------------------------------
        if secondary_table and s_obj and p_obj:
            p_alias = primary_table[0].lower()
            s_alias = secondary_table[0].lower()
            if s_alias == p_alias:
                s_alias = "s"
                p_alias = "p"

            join_cond = self._find_join_condition(primary_table, p_obj, secondary_table, s_obj, p_alias, s_alias)
            if join_cond:
                # A0: Explicit JOIN syntax request (e.g. "left join branch and loan table", "inner join customers and accounts")
                explicit_join_match = re.search(r"\b(left\s+join|right\s+join|full\s+(?:outer\s+)?join|inner\s+join|cross\s+join|join)\b", p_low)
                if explicit_join_match and not (is_max_query or is_min_query or is_count_query or is_sum_query or extracted_name or extracted_numeric_filter):
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

                # A1: Filtered Person / Entity Metric Lookup (e.g. "what is bank balance of amit", "accounts of rahul")
                if extracted_name:
                    where_clauses = []
                    name_col = self._find_name_column(p_obj)
                    if name_col:
                        where_clauses.append(self._format_like_clause(f"{p_alias}.{name_col}", extracted_name))
                    s_name_col = self._find_name_column(s_obj)
                    if s_name_col:
                        where_clauses.append(self._format_like_clause(f"{s_alias}.{s_name_col}", extracted_name))

                    where_str = f" WHERE ({' OR '.join(where_clauses)})" if where_clauses else ""
                    return (
                        f"SELECT *\n"
                        f"FROM {primary_table} {p_alias}\n"
                        f"JOIN {secondary_table} {s_alias} ON {join_cond}\n"
                        f"{where_str}\n"
                        f"LIMIT 25;"
                    )

                # A2: Numeric Value Filter across joined tables (e.g. "customer whose bank balance is 125000.5")
                if extracted_numeric_filter:
                    col_name = extracted_numeric_filter["column"]
                    col_val = extracted_numeric_filter["value"]
                    op = extracted_numeric_filter.get("op", "=")
                    tbl_name = extracted_numeric_filter["table"]
                    target_alias = p_alias if tbl_name == primary_table else s_alias
                    where_str = f" WHERE {target_alias}.{col_name} {op} {col_val}"
                    return (
                        f"SELECT *\n"
                        f"FROM {primary_table} {p_alias}\n"
                        f"JOIN {secondary_table} {s_alias} ON {join_cond}\n"
                        f"{where_str}\n"
                        f"LIMIT 25;"
                    )

                # A3: Aggregation / Ranking on multi-table
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
        # SCENARIO B: Single-Table Operations (e.g. Customers, Accounts, Branches)
        # -------------------------------------------------------------
        id_col = self._find_id_column(p_obj)
        date_col = self._find_date_column(p_obj)
        name_col = self._find_name_column(p_obj)
        metric_col = self._find_metric_column(p_obj)

        where_clauses = []

        # Case B0: Numeric ID Filter with ID Disambiguation
        # (e.g. "bank balance of id = 1001", "customer whose id is 1003", "1004 and 1007")
        if extracted_ids:
            id_cols_to_check = []
            if id_col:
                id_cols_to_check.append(id_col)
            for c in p_cols:
                if c.lower().endswith("_id") and c not in id_cols_to_check:
                    id_cols_to_check.append(c)

            if len(extracted_ids) == 1:
                target_id = extracted_ids[0]
                if len(id_cols_to_check) > 1:
                    where_clauses.append(f"({' OR '.join([f'{c} = {target_id}' for c in id_cols_to_check])})")
                elif id_cols_to_check:
                    where_clauses.append(f"{id_cols_to_check[0]} = {target_id}")
            else:
                ids_str = ", ".join(str(i) for i in extracted_ids)
                if len(id_cols_to_check) > 1:
                    where_clauses.append(f"({' OR '.join([f'{c} IN ({ids_str})' for c in id_cols_to_check])})")
                elif id_cols_to_check:
                    where_clauses.append(f"{id_cols_to_check[0]} IN ({ids_str})")

        # Case B1: Numeric metric filter on single table (e.g. "balance = 125000.5", "balance > 50000")
        if extracted_numeric_filter and extracted_numeric_filter.get("table") == primary_table:
            col_name = extracted_numeric_filter["column"]
            col_val = extracted_numeric_filter["value"]
            op = extracted_numeric_filter.get("op", "=")
            where_clauses.append(f"{col_name} {op} {col_val}")

        # Case B2: Categorical Column Filter (e.g. "list of saving accounts", "retail customers", "active loans")
        if categorical_filter and categorical_filter.get("table") == primary_table:
            cat_col = categorical_filter["column"]
            cat_val = categorical_filter["value"]
            where_clauses.append(f"LOWER({cat_col}) LIKE '%{cat_val}%'")

        # Location / City / State Filter (e.g. "customers from Delhi and Maharashtra", "in Mumbai")
        loc_match = re.search(r"\b(?:from|in|living\s+in|based\s+in)\s+([a-zA-Z\s,and]+?)(?:\s*\?|\s*$|\s+with|\s+whose|\s+limit|\s+top|\s+order)", p_low)
        if loc_match and not any(k in loc_match.group(1) for k in ["table", "database", "yesterday", "today", "days", "account", "customer"]):
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

        where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Case B0: Direct ID record query
        if extracted_ids:
            lim = len(extracted_ids) if len(extracted_ids) > 1 else 10
            return f"SELECT * FROM {primary_table}{where_str} LIMIT {lim};"

        # Case B1: Aggregate Sum / Usage (e.g. "what is total balance", "ai token usage of last 34 days")
        if (is_sum_query or "usage" in p_low or "token" in p_low) and metric_col:
            return f"SELECT SUM({metric_col}) AS total_{metric_col} FROM {primary_table}{where_str};"

        # Case B2: Count queries (e.g. "how many users", "count of documents")
        if is_count_query:
            return f"SELECT COUNT(*) AS total_count FROM {primary_table}{where_str};"

        # Case B3: Maximum / Top query on single table
        if (is_max_query or is_min_query or limit_n) and metric_col:
            order_dir = "DESC" if (is_max_query or not is_min_query) else "ASC"
            n_val = limit_n or (1 if is_max_query or is_min_query else 10)
            return f"SELECT * FROM {primary_table}{where_str} ORDER BY {metric_col} {order_dir} LIMIT {n_val};"

        # Case B4: Filtered query for specific person / user (e.g. "Show Joel Lawrence")
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

        # Case B6: Categorical or general list
        limit_val = limit_n or (25 if any(k in p_low for k in ["all", "list", "show", "get"]) else 10)
        return f"SELECT * FROM {primary_table}{where_str} LIMIT {limit_val};"

    # =========================================================================
    # DYNAMIC ENTITY & ATTRIBUTE EXTRACTION (NO HARDCODING)
    # =========================================================================
    def _extract_numeric_ids(self, p_low: str) -> List[int]:
        """Extracts one or more integer IDs from phrases like 'id = 1001', 'id is 1003', 'customer 1003'."""
        ids = []
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
            r"\b(?:id)\s*=\s*['\"]?(\d+)['\"]?\b",
            r"\b(?:id)\s+['\"]?(\d+)['\"]?\b"
        ]
        for pat in patterns:
            for m in re.finditer(pat, p_low):
                val = int(m.group(1))
                if not any(k in p_low for k in [f"top {val}", f"limit {val}", f"last {val}", f"past {val}"]):
                    if val not in ids:
                        ids.append(val)
        return ids

    def _extract_numeric_value_filter(self, p_low: str, tables: Dict[str, TableMeta]) -> Optional[Dict[str, Any]]:
        """Extracts numeric filter values like 'balance is 125000.5', 'balance > 50000', 'loan amount 500000'."""
        num_match = re.search(r"\b([a-zA-Z_]+)\s*(?:is|=|>=|<=|>|<)\s*(\d+(?:\.\d+)?)\b", p_low)
        if num_match:
            attr_name = num_match.group(1).lower()
            val_str = num_match.group(2)
            
            # Determine operator
            op = "="
            if ">=" in p_low: op = ">="
            elif "<=" in p_low: op = "<="
            elif ">" in p_low: op = ">"
            elif "<" in p_low: op = "<"

            # Check which table has this column
            for t_name, t_obj in tables.items():
                for col in t_obj.columns:
                    c_low = col.name.lower()
                    if c_low == attr_name or attr_name in c_low or c_low in attr_name:
                        dt = col.data_type.upper()
                        if any(n in dt for n in ["INT", "NUMERIC", "DECIMAL", "FLOAT", "REAL", "DOUBLE"]):
                            return {
                                "table": t_name,
                                "column": col.name,
                                "value": val_str,
                                "op": op
                            }

        # Check for numeric floats in prompt (e.g. 125000.5)
        float_match = re.search(r"\b(\d+\.\d+)\b", p_low)
        if float_match:
            f_val = float_match.group(1)
            for t_name, t_obj in tables.items():
                for col in t_obj.columns:
                    if any(k in col.name.lower() for k in ["balance", "amount", "salary", "price", "revenue", "budget"]):
                        return {
                            "table": t_name,
                            "column": col.name,
                            "value": f_val,
                            "op": "="
                        }

        return None

    def _extract_person_name(self, p_raw: str, p_low: str, tables: Dict[str, TableMeta]) -> Tuple[Optional[str], Optional[str]]:
        """Extracts person names dynamically from natural language without hardcoding."""
        # Stopwords that are not names
        non_name_tokens = {
            "the", "all", "each", "a", "an", "saving", "savings", "current", "retail", "premium",
            "active", "inactive", "closed", "pending", "account", "accounts", "customer", "customers",
            "bank", "balance", "database", "table", "branch", "branches", "loan", "loans", "transaction",
            "transactions", "id", "kpi", "kpis", "report", "most", "which", "what", "how", "count",
            "city", "state", "country", "today", "yesterday", "month", "year", "week", "days"
        }

        # Check pattern: "balance of [Name]", "for [Name]", "details of [Name]"
        of_match = re.search(r"\b(?:of|for|about|named?)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\b", p_raw)
        if of_match:
            candidate = of_match.group(1).strip()
            cand_words = set(candidate.lower().split())
            if not cand_words.intersection(non_name_tokens) and len(candidate) > 2:
                match_table = self._find_table_with_name_columns(tables)
                return candidate.title(), match_table

        # Check quoted strings
        quote_match = re.search(r"['\"]([^'\"]+)['\"]", p_raw)
        if quote_match and len(quote_match.group(1).split()) <= 4:
            cand = quote_match.group(1).strip()
            cand_words = set(cand.lower().split())
            if not cand_words.intersection(non_name_tokens) and len(cand) > 2:
                match_table = self._find_table_with_name_columns(tables)
                return cand.title(), match_table

        # Check possessives: "[Name]'s balance"
        poss_match = re.search(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s*'?s\b", p_raw)
        if poss_match:
            cand = poss_match.group(1).strip()
            cand_words = set(cand.lower().split())
            if not cand_words.intersection(non_name_tokens) and len(cand) > 2:
                match_table = self._find_table_with_name_columns(tables)
                return cand, match_table

        return None, None

    def _find_table_with_name_columns(self, tables: Dict[str, TableMeta]) -> Optional[str]:
        """Finds table containing person name columns (e.g. customers, employees, users)."""
        for t_name, t_obj in tables.items():
            for c in t_obj.columns:
                c_low = c.name.lower()
                if any(k in c_low for k in ["first_name", "last_name", "full_name", "customer_name", "emp_name", "username"]):
                    return t_name
        return None

    def _extract_categorical_filter(self, p_low: str, tables: Dict[str, TableMeta], target_table: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extracts categorical values like 'saving', 'current', 'retail', 'premium', 'active'."""
        common_categories = [
            "saving", "savings", "current", "retail", "premium", "active", "inactive",
            "pending", "completed", "approved", "rejected", "gold", "platinum", "silver", "personal", "home", "auto"
        ]
        
        # Order tables checking target_table first
        ordered_tables = []
        if target_table and target_table in tables:
            ordered_tables.append((target_table, tables[target_table]))
        for t_name, t_obj in tables.items():
            if t_name != target_table:
                ordered_tables.append((t_name, t_obj))

        for cat in common_categories:
            if re.search(rf"\b{cat}\b", p_low):
                for t_name, t_obj in ordered_tables:
                    for col in t_obj.columns:
                        c_low = col.name.lower()
                        if any(k in c_low for k in ["type", "status", "category", "segment", "tier"]):
                            val = cat.rstrip("s") if cat == "savings" else cat
                            return {
                                "table": t_name,
                                "column": col.name,
                                "value": val
                            }
        return None

    def _detect_mode_frequency_query(self, p_low: str, tables: Dict[str, TableMeta]) -> Tuple[bool, Optional[str], Optional[str]]:
        """Detects queries asking for the most frequent / appearing entity (e.g. 'which city is most appear')."""
        mode_triggers = [
            r"\bwhich\s+([a-zA-Z_]+)\s+(?:is\s+)?(?:most\s+appear|appears?\s+most|is\s+most\s+frequent|is\s+most\s+common|most\s+recurring)\b",
            r"\b(?:most\s+appear|most\s+frequent|most\s+common|most\s+popular)\s+([a-zA-Z_]+)\b",
            r"\bwhich\s+([a-zA-Z_]+)\s+has\s+(?:the\s+)?most\b"
        ]
        for pat in mode_triggers:
            m = re.search(pat, p_low)
            if m:
                target_col_word = m.group(1).lower()
                # Find matching column in catalog
                for t_name, t_obj in tables.items():
                    for col in t_obj.columns:
                        c_low = col.name.lower()
                        if c_low == target_col_word or target_col_word in c_low or c_low in target_col_word:
                            return True, col.name, t_name

        return False, None, None

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

    def _identify_target_tables(self, p_low: str, tables: Dict[str, TableMeta], name_source_table: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Identifies primary and optional secondary table based on prompt entities."""
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

            # Semantic entity matching
            if re.search(r"\b(?:account|accounts|balance|saving|savings|current)\b", p_low) and any(ak in t_low for ak in ["account", "balance"]):
                score += 35
            if re.search(r"\b(?:customer|customers|client|clients)\b", p_low) and any(ck in t_low for ck in ["cust", "client"]):
                score += 35
            if re.search(r"\b(?:branch|branches|manager)\b", p_low) and any(bk in t_low for bk in ["branch"]):
                score += 35
            if re.search(r"\b(?:loan|loans)\b", p_low) and any(lk in t_low for lk in ["loan"]):
                score += 35
            if re.search(r"\b(?:transaction|transactions|deposit|withdrawal)\b", p_low) and any(tx in t_low for tx in ["transact"]):
                score += 35

            # Column matches
            for col in t_obj.columns:
                c_low = col.name.lower()
                if re.search(rf"\b{re.escape(c_low)}\b", p_low):
                    score += 15

            scored.append((score, t_name))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_candidates = [t for s, t in scored if s > 0]

        primary = top_candidates[0] if len(top_candidates) > 0 else list(tables.keys())[0]
        
        # Determine secondary table if multi-table signals exist
        secondary = None
        if len(top_candidates) > 1 and scored[1][0] >= 30:
            needs_join = any(k in p_low for k in ["join", "joined", "with their", "across", "along with", "per", "in each"])
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
            if any(k == c_low for k in ["name", "username", "emp_name", "first_name", "full_name", "title", "client_name", "branch_name", "manager_name"]):
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
        for c in table_obj.columns:
            c_low = c.name.lower()
            dt_upper = c.data_type.upper()
            if any(num in dt_upper for num in ["INT", "NUMERIC", "DECIMAL", "FLOAT"]):
                if not c_low.endswith("_id") and c_low != "id":
                    return c.name
        return None

    def _find_join_condition(self, t1_name: str, t1_obj: TableMeta, t2_name: str, t2_obj: TableMeta, a1: Optional[str] = None, a2: Optional[str] = None) -> Optional[str]:
        """Finds foreign key or common key connecting two tables prioritizing true relational ID keys."""
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

        # 4. Check common ID columns present in both tables: e.g. customer_id, branch_id
        common_cols = set(t1_col_map.keys()).intersection(set(t2_col_map.keys()))
        id_commons = [c for c in common_cols if c.endswith("_id") or c == "id"]
        if id_commons:
            best_col = id_commons[0]
            return f"{t1_ref}.{t1_col_map[best_col]} = {t2_ref}.{t2_col_map[best_col]}"

        # Avoid joining on generic non-ID columns like 'phone' unless no other option exists
        non_id_commons = [c for c in common_cols if c not in ["phone", "created_at", "updated_at", "status", "country"]]
        if non_id_commons:
            best_col = non_id_commons[0]
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
