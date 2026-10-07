import pypdf

reader = pypdf.PdfReader(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\SQL-Manual.pdf")
print("SQL-Manual.pdf total pages:", len(reader.pages))
for i in [5, 10, 15, 20, 25]:
    text = reader.pages[i].extract_text()
    print(f"--- Page {i} len={len(text)} ---")
    print(text[:300])
