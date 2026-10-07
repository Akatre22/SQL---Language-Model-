import fitz  # PyMuPDF
from pathlib import Path

pdf_path = Path("data/365 Data Science_SQL BASICS_sm.pdf")
if not pdf_path.exists():
    print(f"[!] Error: {pdf_path} not found!")
    exit(1)

doc = fitz.open(pdf_path)
print(f"Total Pages in PDF 2: {len(doc)}")

full_text = []
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    full_text.append(f"--- PAGE {page_num + 1} ---\n{text}")

full_content = "\n".join(full_text)
output_path = Path("data/extracted_pdf_2_raw.txt")
output_path.write_text(full_content, encoding="utf-8")
print(f"Extracted {len(full_content)} characters across {len(doc)} pages into {output_path}")
print("\nFirst 1200 characters preview:")
print(full_content[:1200])
