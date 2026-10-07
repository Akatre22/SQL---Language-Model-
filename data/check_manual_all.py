import pypdf

reader = pypdf.PdfReader(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\SQL-Manual.pdf")
print("Total pages in SQL-Manual.pdf:", len(reader.pages))

non_empty = 0
for idx, p in enumerate(reader.pages):
    t = p.extract_text() or ""
    if len(t.strip()) > 0:
        non_empty += 1
        if non_empty <= 5:
            print(f"Page {idx+1} has {len(t)} chars: {t[:100]}...")

print(f"Total non-empty pages found: {non_empty} / {len(reader.pages)}")
