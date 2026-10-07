import pypdf

reader = pypdf.PdfReader(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\keip108.pdf")
print("keip108.pdf total pages:", len(reader.pages))
total_text = ""
for idx, page in enumerate(reader.pages):
    t = page.extract_text() or ""
    total_text += f"\n\n=== PAGE {idx+1} ===\n\n" + t
    print(f"Page {idx+1}: {len(t)} chars")

with open(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\extracted_pdf_3_raw.txt", "w", encoding="utf-8") as f:
    f.write(total_text)

print(f"\nSaved {len(total_text)} characters from keip108.pdf to extracted_pdf_3_raw.txt")
