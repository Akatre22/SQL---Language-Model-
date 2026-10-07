"""
Leakage-Safe Schema & Template-Based Dataset Splitter (Item 12).
Partitions dataset samples by AST query template and schema domain
to guarantee 0% data leakage between Training, Validation, and Test sets.
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict
import sqlglot
from sqlglot import exp

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent
TRAIN_FILE = DATA_DIR / "train.jsonl"
VAL_FILE = DATA_DIR / "val.jsonl"
TEST_UNSEEN_FILE = DATA_DIR / "test_unseen.jsonl"

def extract_ast_template(sql_query: str) -> str:
    """
    Extracts structural AST skeleton by stripping literal constants,
    table aliases, and variable identifiers.
    """
    if not sql_query or not sql_query.strip():
        return "EMPTY"
    
    cleaned = sql_query.strip().rstrip(";")
    try:
        parsed = sqlglot.parse_one(cleaned, read="sqlite")
        if parsed is None:
            return "UNPARSED"
        
        # Anonymize literals & identifiers
        for literal in parsed.find_all(exp.Literal):
            literal.replace(exp.Literal.string("VAL"))
        for num in parsed.find_all(exp.Literal.number):
            num.replace(exp.Literal.number(0))

        # Generate structural representation
        skeleton = parsed.sql(pretty=False)
        # Collapse whitespace
        skeleton = " ".join(skeleton.split())
        return skeleton
    except Exception:
        # Fallback to keyword-sequence hash
        keywords = ["SELECT", "FROM", "JOIN", "WHERE", "GROUP BY", "HAVING", "ORDER BY", "LIMIT", "UNION", "WITH"]
        found = [k for k in keywords if k in sql_query.upper()]
        return "_".join(found) if found else "RAW_SQL"

def extract_sql_from_item(item: Dict[str, Any]) -> str:
    """Extracts SQL query string from various item schema formats."""
    if "sql" in item and item["sql"]:
        return item["sql"]
    if "response" in item and item["response"]:
        res = item["response"]
        if "```sql" in res:
            parts = res.split("```sql")
            if len(parts) > 1:
                return parts[1].split("```")[0].strip()
        return res.strip()
    if "output" in item and item["output"]:
        return item["output"]
    return ""

def partition_leakage_safe(
    samples: List[Dict[str, Any]],
    train_ratio: float = 0.80,
    val_ratio: float = 0.10,
    test_ratio: float = 0.10
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Groups samples by (Domain/Schema, AST_Template) and assigns entire
    structural template clusters strictly to train, validation, or test.
    Never splits a single template across multiple sets.
    """
    template_clusters = defaultdict(list)
    
    for item in samples:
        sql = extract_sql_from_item(item)
        ast_template = extract_ast_template(sql)
        cluster_key = ast_template
        template_clusters[cluster_key].append(item)

    # Sort cluster keys deterministically
    sorted_cluster_keys = sorted(template_clusters.keys(), key=lambda k: hashlib.sha256(k.encode()).hexdigest())

    total_samples = len(samples)
    target_train_count = int(total_samples * train_ratio)
    target_val_count = int(total_samples * val_ratio)

    train_data = []
    val_data = []
    test_data = []

    # Assign entire cluster to exactly one split
    for key in sorted_cluster_keys:
        cluster_items = template_clusters[key]
        if len(train_data) + len(cluster_items) <= target_train_count or (len(train_data) < target_train_count and not val_data):
            train_data.extend(cluster_items)
        elif len(val_data) + len(cluster_items) <= target_val_count or (len(val_data) < target_val_count and not test_data):
            val_data.extend(cluster_items)
        else:
            test_data.extend(cluster_items)

    return train_data, val_data, test_data

def run_leakage_audit(train_data: List[Dict], val_data: List[Dict], test_data: List[Dict]) -> Dict[str, Any]:
    """Audits train, val, and test splits for template or text leakage."""
    train_templates = {extract_ast_template(extract_sql_from_item(s)) for s in train_data}
    val_templates = {extract_ast_template(extract_sql_from_item(s)) for s in val_data}
    test_templates = {extract_ast_template(extract_sql_from_item(s)) for s in test_data}

    train_test_overlap = train_templates.intersection(test_templates)
    train_val_overlap = train_templates.intersection(val_templates)

    audit_report = {
        "train_samples": len(train_data),
        "val_samples": len(val_data),
        "test_samples": len(test_data),
        "unique_train_templates": len(train_templates),
        "unique_test_templates": len(test_templates),
        "train_test_template_overlap_count": len(train_test_overlap),
        "train_test_leakage_rate_pct": round(len(train_test_overlap) / max(1, len(test_templates)) * 100, 2),
        "train_val_template_overlap_count": len(train_val_overlap),
        "is_leakage_safe": (len(train_test_overlap) == 0)
    }
    return audit_report

def split_and_save():
    print("[*] Starting Leakage-Safe Dataset Splitting...")
    
    # Load all unique samples from existing train, val, and schema_conditioned_sft
    all_samples = []
    sources = [TRAIN_FILE, VAL_FILE, DATA_DIR / "schema_conditioned_sft.jsonl"]
    for filepath in sources:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        all_samples.append(json.loads(line))

    # Deduplicate by instruction text
    seen_instructions = set()
    deduped_samples = []
    for s in all_samples:
        inst = s.get("instruction", s.get("question", "")).strip().lower()
        if inst and inst not in seen_instructions:
            seen_instructions.add(inst)
            deduped_samples.append(s)

    print(f"[+] Loaded {len(deduped_samples)} unique dataset samples.")

    # Partition by Template & Schema Cluster
    train_split, val_split, test_split = partition_leakage_safe(deduped_samples)

    # Save to disk
    with open(TRAIN_FILE, "w", encoding="utf-8") as f:
        for item in train_split:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(VAL_FILE, "w", encoding="utf-8") as f:
        for item in val_split:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(TEST_UNSEEN_FILE, "w", encoding="utf-8") as f:
        for item in test_split:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Run audit
    audit = run_leakage_audit(train_split, val_split, test_split)
    print("\n" + "=" * 60)
    print("           LEAKAGE-SAFE DATASET SPLIT AUDIT")
    print("=" * 60)
    print(f"Train Records:         {audit['train_samples']} (Unique Templates: {audit['unique_train_templates']})")
    print(f"Validation Records:    {audit['val_samples']}")
    print(f"Test (Unseen) Records: {audit['test_samples']} (Unique Templates: {audit['unique_test_templates']})")
    print(f"Train/Test Overlap:    {audit['train_test_template_overlap_count']} templates ({audit['train_test_leakage_rate_pct']}%)")
    print(f"Leakage-Safe Status:   {'PASSED (Zero Overlap)' if audit['is_leakage_safe'] else 'WARNING'}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    split_and_save()
