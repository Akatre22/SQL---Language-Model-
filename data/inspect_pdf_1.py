import fitz  # PyMuPDF
from pathlib import Path

pdf_path = Path("data/202003291621085101sanjeev_rdbms_unit-I_sql_bba_ms_4_sem.pdf")
doc = fitz.open(pdf_path)

print(f"Total Pages: {len(doc)}")
full_text = []
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    full_text.append(f"--- PAGE {page_num + 1} ---\n{text}")

full_content = "\n".join(full_text)
output_path = Path("data/extracted_pdf_1_raw.txt")
output_path.write_text(full_content, encoding="utf-8")
print(f"Extracted {len(full_content)} characters across {len(doc)} pages into {output_path}")
print("First 1000 characters preview:")
print(full_content[:1000])
