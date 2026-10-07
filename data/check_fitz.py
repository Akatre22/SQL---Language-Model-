try:
    import fitz
    doc = fitz.open(r"c:\Users\akatre\OneDrive - Nice Software Solutions\Desktop\Tiny LLM\data\SQL-Manual.pdf")
    print("fitz page count:", len(doc))
    for i in range(min(5, len(doc))):
        print(f"Page {i+1} text length:", len(doc[i].get_text()))
        print(f"Page {i+1} image list:", len(doc[i].get_images()))
except Exception as e:
    print("Error / fitz not available:", e)
