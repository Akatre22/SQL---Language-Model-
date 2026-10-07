import pypdf

reader = pypdf.PdfReader(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\rbafy.pdf")
num_pages = len(reader.pages)
print(f"Total pages in rbafy.pdf: {num_pages}")

# Inspect Table of Contents (Pages 5 to 20)
toc_text = ""
for p in range(4, 15):
    toc_text += f"\n--- Page {p+1} ---\n" + reader.pages[p].extract_text()

with open(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\pdf_4_toc.txt", "w", encoding="utf-8") as f:
    f.write(toc_text)

print(f"TOC extracted: {len(toc_text)} chars saved to pdf_4_toc.txt")
