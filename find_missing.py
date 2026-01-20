import pypdf

pdf_path = "Kompilasi-Keputusan-Syariah-Dalam-Kewangan-Islam-Edisi-Ketiga-2011-2017.pdf"
reader = pypdf.PdfReader(pdf_path)

search_terms = [
    "Istisna",
    "Wa'd",
    "Qard",
    "Wa`d" # Alternate spelling tick
]

print(f"{'Chapter':<20} | {'Found on PDF Page'}")
print("-" * 50)

# Search ranges based on gaps
# Istisna: between Ijarah (87) and Kafalah (105) -> Range 90-105
# Qard: between Kafalah (105) and Rahn (115) -> Range 105-115
# Wa'd: between Tawarruq (127) and Wakalah (137) -> Range 127-140

ranges = [
    (80, 110),
    (100, 120),
    (125, 145)
]

found_pages = []

for start, end in ranges:
    for page_num in range(start, end):
        try:
            page = reader.pages[page_num]
            text = page.extract_text()
            lines = text.split('\n')[:10]
            for line in lines:
                for term in search_terms:
                    if term.lower() in line.lower() and len(line) < 50: # Title usually short
                        print(f"[{term}] Found on PDF Page {page_num + 1} -> {line.strip()}")
        except:
            pass
