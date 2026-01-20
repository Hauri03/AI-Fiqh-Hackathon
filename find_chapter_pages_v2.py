import pypdf

pdf_path = "Kompilasi-Keputusan-Syariah-Dalam-Kewangan-Islam-Edisi-Ketiga-2011-2017.pdf"
reader = pypdf.PdfReader(pdf_path)

search_terms = [
    "Bai` Al-Sarf",
    "Hibah",
    "Ijarah",
    "Istisna'",
    "Kafalah",
    "Qard",
    "Rahn",
    "Tawarruq",
    "Wa'd",
    "Wakalah"
]

with open("chapter_scan.txt", "w", encoding="utf-8") as f:
    f.write(f"{'Chapter':<20} | {'Found on Content Page (approx)'}\n")
    f.write("-" * 50 + "\n")

    start_pdf_page = 70
    end_pdf_page = 150

    for page_num in range(start_pdf_page, end_pdf_page):
        try:
            page = reader.pages[page_num]
            text = page.extract_text()
            lines = text.split('\n')[:15] # Check first 15 lines
            for line in lines:
                for term in search_terms:
                    # Look for exact chapter titles often preceded by a number or on their own line
                    # We accept partial match if it's the main feature of the line
                    if term.lower() in line.lower() and len(line) < 100:
                         # Content page is PDF page - 20
                        content_page = page_num + 1 - 20 
                        f.write(f"Found '{term}' on PDF Page {page_num + 1} (Content {content_page}) -> Line: {line.strip()}\n")
        except Exception as e:
            f.write(f"Error on page {page_num}: {e}\n")

print("Scan complete. Check chapter_scan.txt")
