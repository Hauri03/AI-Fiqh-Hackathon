import pypdf

pdf_path = "Kompilasi-Keputusan-Syariah-Dalam-Kewangan-Islam-Edisi-Ketiga-2011-2017.pdf"

try:
    reader = pypdf.PdfReader(pdf_path)
    with open("toc_output.txt", "w", encoding="utf-8") as f:
        # Check first 30 pages
        for i in range(min(30, len(reader.pages))):
            page = reader.pages[i]
            text = page.extract_text()
            f.write(f"--- Page {i+1} ---\n")
            f.write(text)
            f.write("\n\n")
            
    print("Done extracting text to toc_output.txt")
except Exception as e:
    print(f"Error: {e}")
