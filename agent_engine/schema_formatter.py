"""
Schema Formatter & Serializer for Tiny SQL LLM.
Parses, normalizes, serializes, and formats database schemas into standardized prompt formats:
1. XML/Tag representation (<schema> ... </schema>)
2. Compact column-list representation (table(col1 PK, col2 FK))
3. Standard ANSI DDL representation (CREATE TABLE ...)
Supports extraction from live SQLite connections, schema dictionaries, and raw DDL strings.
"""

import sqlite3
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union, Any
from pathlib import Path
import sqlglot
from sqlglot import exp

@dataclass
class ColumnMeta:
    name: str
    data_type: str = "TEXT"
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: Optional[str] = None  # e.g. "customers.customer_id"

@dataclass
class TableMeta:
    name: str
    columns: List[ColumnMeta] = field(default_factory=list)
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)

    @property
    def column_names(self) -> List[str]:
        return [c.name for c in self.columns]

@dataclass
class DatabaseCatalog:
    database_name: str = "default_db"
    tables: Dict[str, TableMeta] = field(default_factory=dict)

    def get_table(self, table_name: str) -> Optional[TableMeta]:
        return self.tables.get(table_name.lower())

class SchemaFormatter:
    """
    Standardized formatter and serializer for SQL-SLM schema conditioning.
    """

    @staticmethod
    def extract_from_sqlite(conn_or_path: Union[sqlite3.Connection, str, Path]) -> DatabaseCatalog:
        """Extracts schema catalog from a live SQLite connection or file path."""
        if isinstance(conn_or_path, (str, Path)):
            conn = sqlite3.connect(str(conn_or_path))
            should_close = True
        else:
            conn = conn_or_path
            should_close = False

        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        table_names = [row[0] for row in cursor.fetchall()]

        catalog = DatabaseCatalog()

        for t in table_names:
            # Table info: cid, name, type, notnull, dflt_value, pk
            cursor.execute(f"PRAGMA table_info('{t}');")
            col_rows = cursor.fetchall()

            # Foreign key info: id, seq, table, from, to, on_update, on_delete, match
            cursor.execute(f"PRAGMA foreign_key_list('{t}');")
            fk_rows = cursor.fetchall()
            fk_map = {row[3]: f"{row[2]}.{row[4]}" for row in fk_rows}

            cols = []
            for row in col_rows:
                col_name = row[1]
                col_type = row[2] or "TEXT"
                is_pk = bool(row[5] > 0)
                is_fk = col_name in fk_map
                ref = fk_map.get(col_name)

                cols.append(ColumnMeta(
                    name=col_name,
                    data_type=col_type.upper(),
                    is_primary_key=is_pk,
                    is_foreign_key=is_fk,
                    references=ref
                ))

            catalog.tables[t.lower()] = TableMeta(
                name=t,
                columns=cols,
                foreign_keys=[{"from": k, "to": v} for k, v in fk_map.items()]
            )

        if should_close:
            conn.close()

        return catalog

    @staticmethod
    def extract_from_sqlalchemy(engine_or_conn_str: Any, schema_name: Optional[str] = None) -> DatabaseCatalog:
        """
        Extracts schema catalog from PostgreSQL, SQL Server / SSMS, SQLite, or any SQLAlchemy-supported DB.
        """
        from sqlalchemy import create_engine, inspect
        if isinstance(engine_or_conn_str, str):
            engine = create_engine(engine_or_conn_str)
        else:
            engine = engine_or_conn_str

        inspector = inspect(engine)
        db_name = getattr(engine.url, "database", None) or "connected_db"
        catalog = DatabaseCatalog(database_name=str(db_name))

        table_names = []
        try:
            table_names = inspector.get_table_names(schema=schema_name)
        except Exception:
            table_names = []

        for t in table_names:
            cols_meta = []
            try:
                col_dicts = inspector.get_columns(t, schema=schema_name)
                pk_constraint = inspector.get_pk_constraint(t, schema=schema_name) or {}
                pk_cols = set(pk_constraint.get("constrained_columns", []))
                
                fks = inspector.get_foreign_keys(t, schema=schema_name) or []
                fk_map = {}
                fk_list = []
                for fk in fks:
                    referred_table = fk.get("referred_table", "")
                    referred_cols = fk.get("referred_columns", [])
                    constrained_cols = fk.get("constrained_columns", [])
                    for c_col, r_col in zip(constrained_cols, referred_cols):
                        fk_map[c_col] = f"{referred_table}.{r_col}"
                        fk_list.append({"from": c_col, "to": f"{referred_table}.{r_col}"})

                for c in col_dicts:
                    c_name = c["name"]
                    c_type = str(c.get("type", "TEXT")).upper()
                    is_pk = c_name in pk_cols
                    is_fk = c_name in fk_map
                    ref = fk_map.get(c_name)

                    cols_meta.append(ColumnMeta(
                        name=c_name,
                        data_type=c_type,
                        is_primary_key=is_pk,
                        is_foreign_key=is_fk,
                        references=ref
                    ))

                catalog.tables[t.lower()] = TableMeta(
                    name=t,
                    columns=cols_meta,
                    foreign_keys=fk_list
                )
            except Exception:
                continue

        return catalog

    @staticmethod
    def extract_from_dict(schema_dict: Dict[str, List[str]]) -> DatabaseCatalog:
        """Extracts catalog from a simple {table_name: [col1 (TYPE), col2]} dictionary."""
        catalog = DatabaseCatalog()
        for tbl_name, cols in schema_dict.items():
            col_metas = []
            for c in cols:
                # Parse "col_name (TYPE)" or "col_name"
                if "(" in c and c.endswith(")"):
                    c_name, c_type = c[:-1].split("(", 1)
                    c_name = c_name.strip()
                    c_type = c_type.strip()
                else:
                    c_name = c.strip()
                    c_type = "TEXT"

                is_pk = "id" in c_name.lower() and (c_name.lower().startswith(tbl_name.lower()[:4]) or c_name.lower() == "id")
                col_metas.append(ColumnMeta(name=c_name, data_type=c_type.upper(), is_primary_key=is_pk))

            catalog.tables[tbl_name.lower()] = TableMeta(name=tbl_name, columns=col_metas)
        return catalog

    @staticmethod
    def extract_from_ddl(ddl_script: str) -> DatabaseCatalog:
        """Extracts schema catalog from a raw CREATE TABLE DDL string using sqlglot."""
        catalog = DatabaseCatalog()
        try:
            statements = sqlglot.parse(ddl_script, read="sqlite")
            for stmt in statements:
                if isinstance(stmt, exp.Create) and isinstance(stmt.this, exp.Schema):
                    table_name = stmt.this.this.name
                    cols = []
                    for col_def in stmt.this.expressions:
                        if isinstance(col_def, exp.ColumnDef):
                            c_name = col_def.name
                            c_type = str(col_def.kind).upper() if col_def.kind else "TEXT"
                            is_pk = bool(col_def.find(exp.PrimaryKey))
                            cols.append(ColumnMeta(name=c_name, data_type=c_type, is_primary_key=is_pk))
                    catalog.tables[table_name.lower()] = TableMeta(name=table_name, columns=cols)
        except Exception:
            pass
        return catalog

    @classmethod
    def to_compact(cls, catalog: DatabaseCatalog, target_tables: Optional[List[str]] = None) -> str:
        """
        Formats schema into compact single-line per table representation:
        customers(customer_id PK, first_name, region), orders(order_id PK, customer_id FK, amount)
        """
        lines = []
        tables_to_format = [t for t in catalog.tables.values() if not target_tables or t.name.lower() in [x.lower() for x in target_tables]]

        for t in tables_to_format:
            col_strs = []
            for c in t.columns:
                flags = []
                if c.is_primary_key:
                    flags.append("PK")
                if c.is_foreign_key:
                    flags.append("FK")
                flag_str = f" {'/'.join(flags)}" if flags else ""
                col_strs.append(f"{c.name}{flag_str}")
            lines.append(f"{t.name}({', '.join(col_strs)})")

        return "\n".join(lines)

    @classmethod
    def to_xml_tags(cls, catalog: DatabaseCatalog, target_tables: Optional[List[str]] = None) -> str:
        """
        Formats schema wrapped in <schema> tags for SLM training and inference.
        """
        compact_str = cls.to_compact(catalog, target_tables=target_tables)
        return f"<schema>\n{compact_str}\n</schema>"

    @classmethod
    def to_ddl(cls, catalog: DatabaseCatalog, target_tables: Optional[List[str]] = None) -> str:
        """
        Formats schema as clean standard CREATE TABLE DDL statements.
        """
        ddl_blocks = []
        tables_to_format = [t for t in catalog.tables.values() if not target_tables or t.name.lower() in [x.lower() for x in target_tables]]

        for t in tables_to_format:
            col_lines = []
            for c in t.columns:
                pk_clause = " PRIMARY KEY" if c.is_primary_key else ""
                fk_clause = f" REFERENCES {c.references}" if c.references else ""
                col_lines.append(f"  {c.name} {c.data_type}{pk_clause}{fk_clause}")
            block = f"CREATE TABLE {t.name} (\n" + ",\n".join(col_lines) + "\n);"
            ddl_blocks.append(block)

        return "\n\n".join(ddl_blocks)

    @classmethod
    def build_prompt(
        cls,
        catalog: DatabaseCatalog,
        question: str,
        dialect: Optional[str] = None,
        target_tables: Optional[List[str]] = None
    ) -> str:
        """
        Builds a complete, standardized SLM input sequence.
        """
        dialect_tag = f"<dialect>{dialect}</dialect>\n" if dialect else ""
        schema_tag = cls.to_xml_tags(catalog, target_tables=target_tables)
        prompt = f"{dialect_tag}{schema_tag}\n\n<question>\n{question.strip()}\n</question>\n\n<sql>\n"
        return prompt

if __name__ == "__main__":
    from pathlib import Path
    db_path = Path(__file__).resolve().parent / "enterprise_sandbox.db"
    
    if db_path.exists():
        print(f"[*] Extracting catalog from {db_path}...")
        cat = SchemaFormatter.extract_from_sqlite(db_path)
        print("\n--- Compact Format ---")
        print(SchemaFormatter.to_compact(cat))
        print("\n--- XML Tags Format ---")
        print(SchemaFormatter.to_xml_tags(cat))
        print("\n--- Complete SLM Prompt ---")
        prompt = SchemaFormatter.build_prompt(cat, "Show total revenue by customer segment", dialect="sqlite")
        print(prompt)
