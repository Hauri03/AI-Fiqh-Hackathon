import pypdf
import re

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

print(f"{'Chapter':<20} | {'Found on Content Page (approx)'}")
print("-" * 50)

# We know Bahagian IV starts around PDF page 71 (Content 51).
# We'll search primarily in the range of PDF 70 to 150.
start_pdf_page = 70
end_pdf_page = 150

for page_num in range(start_pdf_page, end_pdf_page):
    try:
        page = reader.pages[page_num]
        text = page.extract_text()
        
        # Look for the chapter number pattern like "27." "28." or just the title
        # The titles in TOC usually have a number before them or are large.
        # Let's just print if we find the exact term in the first few lines of the page.
        
        lines = text.split('\n')[:10] # Check first 10 lines
        for line in lines:
            for term in search_terms:
                if term.lower() in line.lower() and len(line) < 100:
                    # Content page is PDF page - 20
                    content_page = page_num + 1 - 20 
                    print(f"Found '{term}' on PDF Page {page_num + 1} (Content {content_page}) -> Line: {line.strip()}")
    except Exception as e:
        pass
