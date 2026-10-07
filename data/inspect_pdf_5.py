import pypdf

reader = pypdf.PdfReader(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\sql-the-complete-reference-third-edition-sep-2009.pdf")
num_pages = len(reader.pages)
print(f"Total pages in SQL Complete Reference: {num_pages}")

# Inspect Table of Contents (Pages 8 to 22)
toc_text = ""
for p in range(7, 22):
    t = reader.pages[p].extract_text() or ""
    toc_text += f"\n--- Page {p+1} ---\n" + t

with open(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\pdf_5_toc.txt", "w", encoding="utf-8") as f:
    f.write(toc_text)

print(f"TOC extracted: {len(toc_text)} chars saved to pdf_5_toc.txt")
