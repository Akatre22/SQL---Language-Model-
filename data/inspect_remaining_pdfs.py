import os
import pypdf

data_dir = r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data"
pdfs = [
    "SQL-Manual.pdf",
    "keip108.pdf",
    "rbafy.pdf",
    "sql-the-complete-reference-third-edition-sep-2009.pdf"
]

for pdf_name in pdfs:
    pdf_path = os.path.join(data_dir, pdf_name)
    if os.path.exists(pdf_path):
        reader = pypdf.PdfReader(pdf_path)
        num_pages = len(reader.pages)
        sample_text = ""
        for i in range(min(5, num_pages)):
            sample_text += f"\n--- Page {i+1} ---\n" + reader.pages[i].extract_text()[:400]
        print(f"=== {pdf_name} ({num_pages} pages) ===")
        print(sample_text[:1200])
        print("\n" + "="*50 + "\n")
