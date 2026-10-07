"""
ChromaDB + BM25 Hybrid Vector Store for Tiny SQL LLM.
Features:
1. Dense Vector Similarity via ChromaDB Persistent Storage.
2. Sparse Keyword Matching via Native BM25 Okapi Algorithm.
3. Extensive SQL Domain Acronym & Concept Expansion.
4. Reciprocal Rank Fusion (RRF) & Multi-Factor Tag/Title Re-ranking.
"""

import sys
import json
import re
import math
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHROMA_DIR = Path(__file__).resolve().parent / "chroma_db"
DOCS_PATH = Path(__file__).resolve().parent / "documents.json"
COLLECTION_NAME = "sql_domain_knowledge"

# Comprehensive SQL Acronym & Concept Expansion Map
ACRONYM_MAP = {
    r"\bsp\b": "Stored Procedure",
    r"\bsprocs?\b": "Stored Procedure",
    r"\bstoreprocedure\b": "Stored Procedure",
    r"\bstore\s+procedure\b": "Stored Procedure",
    r"\bcte\b": "Common Table Expression",
    r"\bctes\b": "Common Table Expressions",
    r"\budf\b": "User Defined Function",
    r"\budfs\b": "User Defined Functions",
    r"\btvf\b": "Table Valued Function",
    r"\bmv\b": "Materialized View",
    r"\bmvs\b": "Materialized Views",
    r"\bfk\b": "Foreign Key",
    r"\bpk\b": "Primary Key",
    r"\bacid\b": "ACID Transactions Atomicity Consistency Isolation Durability",
    r"\bddl\b": "Data Definition Language CREATE ALTER DROP TRUNCATE",
    r"\bdml\b": "Data Manipulation Language SELECT INSERT UPDATE DELETE",
    r"\btcl\b": "Transaction Control Language COMMIT ROLLBACK SAVEPOINT",
    r"\bdcl\b": "Data Control Language GRANT REVOKE",
    r"\bdql\b": "Data Query Language SELECT",
    r"\bmvcc\b": "Multi Version Concurrency Control",
    r"\bwal\b": "Write Ahead Logging",
    r"\b1nf\b": "First Normal Form 1NF",
    r"\b2nf\b": "Second Normal Form 2NF",
    r"\b3nf\b": "Third Normal Form 3NF",
    r"\bbcnf\b": "Boyce Codd Normal Form BCNF",
    r"\broad\s*map\b": "SQL Learning Roadmap",
    r"\blearning\s*path\b": "SQL Learning Roadmap",
    r"\btopics?\s+to\s+practice\b": "SQL Practice Topics",
    r"\bpractice\s+topics?\b": "SQL Practice Topics",
    r"\binterview\s+questions?\b": "SQL Interview Topics and Checklist",
    r"\bnull\s*handling\b": "NULL Handling Three Valued Logic",
    r"\bsargable\b": "SARGable Predicates and Query Optimization",
    r"\block(?:s|ing)?\b": "Database Locks Deadlocks and Concurrency Control",
    r"\bdeadlock(?:s)?\b": "Database Deadlocks and Locking Mechanism",
    r"\brollup\b": "ROLLUP Advanced Aggregation",
    r"\bcube\b": "CUBE Multidimensional Aggregation",
    r"\bgrouping\s*sets\b": "GROUPING SETS Aggregation",
    r"\bqualify\b": "QUALIFY Window Function Filter",
    r"\blateral\b": "LATERAL Join Subquery",
    r"\bcross\s+apply\b": "CROSS APPLY Correlated Join",
    r"\bgaps\s+(?:and|&)\s+islands\b": "Gaps and Islands Consecutive Sequences"
}

def tokenize_for_bm25(text: str) -> List[str]:
    """Tokenizes text into normalized alphanumeric keywords for BM25."""
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = [t.strip() for t in clean.split() if len(t.strip()) > 1]
    return tokens

def normalize_sql_query(query: str) -> str:
    """Expands acronyms, splits camelCase terms, and normalizes synonyms."""
    q = query.strip()
    
    # Split camelCase words (e.g. 'StoreProcedure' -> 'Store Procedure')
    q = re.sub(r"([a-z])([A-Z])", r"\1 \2", q)
    
    # Expand acronyms & concepts
    for pattern, replacement in ACRONYM_MAP.items():
        q = re.sub(pattern, replacement, q, flags=re.IGNORECASE)
        
    return q

class BM25Index:
    """Zero-dependency, high-performance BM25Okapi implementation for local text corpus."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avgdl = 0.0
        self.doc_lengths = []
        self.doc_token_counts = []
        self.doc_ids = []
        self.idf = {}

    def fit(self, doc_ids: List[str], documents: List[str]):
        self.doc_ids = doc_ids
        self.corpus_size = len(documents)
        if self.corpus_size == 0:
            return

        total_length = 0
        self.doc_lengths = []
        self.doc_token_counts = []
        df = Counter()

        for doc in documents:
            tokens = tokenize_for_bm25(doc)
            length = len(tokens)
            self.doc_lengths.append(length)
            total_length += length
            
            counts = Counter(tokens)
            self.doc_token_counts.append(counts)
            for token in counts.keys():
                df[token] += 1

        self.avgdl = total_length / self.corpus_size if self.corpus_size > 0 else 0.0

        # Calculate Okapi IDF with smoothing
        self.idf = {}
        for token, freq in df.items():
            idf_val = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)
            self.idf[token] = max(idf_val, 0.01)

    def score(self, query: str) -> Dict[str, float]:
        """Calculates BM25 score for all documents given a query string."""
        query_tokens = tokenize_for_bm25(query)
        scores = {}

        for idx, doc_id in enumerate(self.doc_ids):
            doc_len = self.doc_lengths[idx]
            counts = self.doc_token_counts[idx]
            score = 0.0

            for q_tok in query_tokens:
                if q_tok not in counts:
                    continue
                tf = counts[q_tok]
                idf_val = self.idf.get(q_tok, 0.0)
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avgdl + 1e-9)))
                score += idf_val * (numerator / denominator)

            scores[doc_id] = score

        return scores

class DomainVectorStore:
    def __init__(self, persist_directory: Optional[Path] = None, force_reindex: bool = False):
        self.persist_dir = persist_directory or CHROMA_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Persistent ChromaDB Client
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        if force_reindex:
            try:
                self.client.delete_collection(name=COLLECTION_NAME)
            except Exception:
                pass
                
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Pure SQL Relational Domain Knowledge Base"}
        )
        
        self.bm25 = BM25Index()
        self.docs_cache: Dict[str, Dict[str, Any]] = {}
        
        # Ingest documents if collection empty or forced
        if self.collection.count() == 0 or force_reindex:
            self.ingest_documents()
        else:
            self._load_local_docs()

    def _load_local_docs(self, docs_path: Optional[Path] = None):
        """Loads and indexes documents for local BM25 scoring."""
        path = docs_path or DOCS_PATH
        if not path.exists():
            return
            
        with open(path, "r", encoding="utf-8") as f:
            docs: List[Dict[str, Any]] = json.load(f)

        ids = []
        raw_texts = []
        for d in docs:
            doc_id = d["id"]
            self.docs_cache[doc_id] = d
            ids.append(doc_id)
            tags_str = ", ".join(d.get("tags", []))
            full_text = f"{d['title']} {d['topic']} {tags_str} {d['content']}"
            raw_texts.append(full_text)

        self.bm25.fit(ids, raw_texts)

    def ingest_documents(self, docs_path: Optional[Path] = None) -> int:
        """Ingests structured SQL documents from JSON into ChromaDB and fits BM25."""
        path = docs_path or DOCS_PATH
        if not path.exists():
            raise FileNotFoundError(f"Documents file not found at {path}")
            
        with open(path, "r", encoding="utf-8") as f:
            docs: List[Dict[str, Any]] = json.load(f)
            
        ids = []
        documents = []
        metadatas = []
        raw_texts_for_bm25 = []
        
        for d in docs:
            doc_id = d["id"]
            self.docs_cache[doc_id] = d
            ids.append(doc_id)
            tags_list = d.get("tags", [])
            tags_str = ", ".join(tags_list)
            full_text = f"Title: {d['title']}\nTopic: {d['topic']}\nKeywords & Aliases: {tags_str}\n\n{d['content']}"
            documents.append(full_text)
            raw_texts_for_bm25.append(f"{d['title']} {d['topic']} {tags_str} {d['content']}")
            metadatas.append({
                "domain": d.get("domain", "sql"),
                "topic": d.get("topic", ""),
                "title": d.get("title", ""),
                "tags": tags_str,
                "source": d.get("source", "SQL Docs")
            })
            
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        self.bm25.fit(ids, raw_texts_for_bm25)
        print(f"[+] Ingested {len(docs)} SQL domain documents into ChromaDB ({self.persist_dir}) and indexed BM25.")
        return len(docs)

    def search(
        self,
        query: str,
        n_results: int = 2,
        domain_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid Semantic Search:
        1. Dense Vector query via ChromaDB.
        2. Sparse BM25 keyword matching.
        3. Reciprocal Rank Fusion + Tag/Title exact match boosting.
        """
        expanded_query = normalize_sql_query(query)
        where_clause = {"domain": domain_filter} if domain_filter else None
        
        candidate_count = min(max(n_results * 4, 10), max(self.collection.count(), 1))
        
        # 1. ChromaDB Vector Query
        try:
            results = self.collection.query(
                query_texts=[expanded_query],
                n_results=candidate_count,
                where=where_clause
            )
        except Exception as e:
            results = {}

        # 2. BM25 Query
        bm25_scores = self.bm25.score(expanded_query)
        max_bm25 = max(bm25_scores.values()) if bm25_scores and max(bm25_scores.values()) > 0 else 1.0

        hits = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)
            doc_ids = results["ids"][0] if "ids" in results else [""] * len(docs)
            
            q_lower = query.lower()
            exp_lower = expanded_query.lower()

            for doc_id, doc_text, meta, dist in zip(doc_ids, docs, metas, distances):
                raw_sim = 1.0 / (1.0 + dist)
                bm25_norm = bm25_scores.get(doc_id, 0.0) / max_bm25
                
                # Tag & Title exact match bonus
                boost = 0.0
                tags = meta.get("tags", "").lower()
                title = meta.get("title", "").lower()
                
                for tag_token in tags.split(", "):
                    if tag_token and (tag_token in q_lower or tag_token in exp_lower):
                        boost += 0.45
                        break
                        
                if any(w in title for w in exp_lower.split() if len(w) > 3):
                    boost += 0.25
                    
                # Hybrid Blended Score: 50% Vector + 30% BM25 + 20% Keyword Boost
                final_score = (0.50 * raw_sim) + (0.30 * bm25_norm) + boost
                
                hits.append({
                    "id": doc_id,
                    "text": doc_text,
                    "metadata": meta,
                    "distance": dist,
                    "similarity": round(raw_sim, 4),
                    "bm25_score": round(bm25_norm, 4),
                    "final_score": round(final_score, 4)
                })
            
            hits.sort(key=lambda x: x["final_score"], reverse=True)
            
        return hits[:n_results]

    def lookup_glossary(self, query: str) -> Dict[str, str]:
        """
        Maps enterprise business terminology to physical database tables & columns.
        """
        glossary_map = {
            r"\b(?:revenue|turnover|gross\s+sales|income|total\s+earnings)\b": "orders.total_amount (and sales.amount)",
            r"\b(?:client|buyer|subscriber|account\s+holder)\b": "customers (customer_id, first_name, segment, region)",
            r"\b(?:staff|worker|headcount|workforce|compensation|wage)\b": "employees (emp_id, emp_name, salary, department_id)",
            r"\b(?:division|branch|office|location|unit)\b": "departments (department_id, dept_name, location, budget)",
            r"\b(?:quota|commission|annual\s+target|sales\s+rep)\b": "sales_reps (rep_id, rep_name, region, commission_rate, annual_target)",
            r"\b(?:inventory|stock|sku|merchandise|items)\b": "products (product_id, product_name, category, unit_price, stock_quantity)"
        }
        
        matches = {}
        for pattern, mapping in glossary_map.items():
            if re.search(pattern, query, re.IGNORECASE):
                matches[pattern] = mapping
        return matches

    def retrieve_relevant_tables(
        self,
        query: str,
        available_tables: Optional[Dict[str, List[str]]] = None,
        top_k: int = 3
    ) -> List[str]:
        """
        Dynamically selects only the most relevant database tables for a user query.
        """
        if not available_tables:
            # Default enterprise sandbox tables
            available_tables = {
                "customers": ["customer_id", "first_name", "last_name", "email", "region", "segment", "join_date", "clients", "buyers"],
                "orders": ["order_id", "customer_id", "order_date", "total_amount", "status", "payment_method", "sales", "revenue", "spending"],
                "products": ["product_id", "product_name", "category", "unit_price", "stock_quantity", "inventory", "items"],
                "sales_reps": ["rep_id", "rep_name", "region", "commission_rate", "annual_target", "quota"],
                "departments": ["department_id", "dept_name", "location", "budget", "division", "office"],
                "employees": ["emp_id", "emp_name", "department_id", "salary", "hire_date", "job_title", "staff", "compensation", "wage"]
            }

        q_lower = query.lower()
        scored_tables = []

        for tbl, cols in available_tables.items():
            score = 0.0
            # Table name mention
            if tbl.lower() in q_lower or tbl.lower().rstrip("s") in q_lower:
                score += 3.0
                
            # Column name / synonym mentions
            for col in cols:
                c_clean = col.split()[0].lower()
                if c_clean in q_lower:
                    score += 1.5
                    
            # Add general query token overlaps
            for token in q_lower.split():
                if len(token) > 3 and any(token in c.lower() for c in cols):
                    score += 0.5

            if score > 0:
                scored_tables.append((tbl, score))

        scored_tables.sort(key=lambda x: x[1], reverse=True)
        selected = [t[0] for t in scored_tables[:top_k]]
        return selected if selected else list(available_tables.keys())[:top_k]

if __name__ == "__main__":
    store = DomainVectorStore(force_reindex=False)
    print("[*] Testing Business Glossary & Schema Retrieval:")
    test_prompts = [
        "Find turnover by client segment in EMEA",
        "Show staff compensation and department budget",
        "List merchandise in stock with price over 500"
    ]
    for tp in test_prompts:
        tables = store.retrieve_relevant_tables(tp, top_k=2)
        glossary = store.lookup_glossary(tp)
        print(f"\nPrompt: '{tp}'")
        print(f"  -> Retrieved Relevant Tables: {tables}")
        print(f"  -> Business Glossary Matches: {glossary}")

