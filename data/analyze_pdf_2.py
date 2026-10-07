import re
from pathlib import Path

content = Path("data/extracted_pdf_2_raw.txt").read_text(encoding="utf-8")
pages = content.split("--- PAGE ")

print(f"Total parsed page blocks: {len(pages) - 1}")

topics = {}
current_topic = "Intro"

for p in pages[1:]:
    lines = [l.strip() for l in p.split("\n") if l.strip()]
    if not lines:
        continue
    p_num = lines[0].split(" ---")[0]
    p_text = "\n".join(lines[1:])
    
    # Check for keywords
    for kw in ["DDL", "DML", "DCL", "TCL", "SELECT", "WHERE", "AND", "OR", "OPERATOR PRECEDENCE", 
               "WILDCARD", "LIKE", "BETWEEN", "IS NULL", "IS NOT NULL", "DISTINCT", "AGGREGATE",
               "COUNT", "SUM", "AVG", "MIN", "MAX", "GROUP BY", "HAVING", "ORDER BY", "LIMIT",
               "INSERT", "UPDATE", "DELETE", "DROP vs TRUNCATE", "COMMIT", "ROLLBACK"]:
        if re.search(r'\b' + re.escape(kw) + r'\b', p_text, re.IGNORECASE):
            topics[kw] = topics.get(kw, 0) + 1

print("\nTopic occurrences across pages:")
for k, v in sorted(topics.items(), key=lambda x: x[1], reverse=True):
    print(f"  - {k}: {v} pages")
