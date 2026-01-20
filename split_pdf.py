import pypdf
import os

pdf_path = "Kompilasi-Keputusan-Syariah-Dalam-Kewangan-Islam-Edisi-Ketiga-2011-2017.pdf"
output_dir = "Split_Chapters"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Mapping of filename to (start_page, end_page) 1-indexed PDF page numbers
# Based on corrected implementation plan
chapter_map = [
    ("00_Preliminaries.pdf", 1, 20),
    ("01_Bahagian_I_Produk_Perbankan_Islam.pdf", 21, 38),
    ("02_Bahagian_II_Takaful.pdf", 39, 62),
    ("03_Bahagian_III_Instrumen_Pasaran_Wang.pdf", 63, 70),
    ("04_Bai_Al-Sarf.pdf", 71, 75), # Adjusted start to cover potential title page if any, end at 75
    ("05_Hibah.pdf", 76, 86),
    ("06_Ijarah.pdf", 87, 97),
    ("07_Istisna.pdf", 98, 104),
    ("08_Kafalah.pdf", 105, 110),
    ("09_Qard.pdf", 111, 114),
    ("10_Rahn.pdf", 115, 126),
    ("11_Tawarruq.pdf", 127, 129),
    ("12_Wad.pdf", 130, 136),
    ("13_Wakalah.pdf", 137, 140),
    ("14_Bahagian_V_Penggulungan.pdf", 141, 148),
    ("15_Bahagian_VI_Lain_Lain.pdf", 149, 172),
    ("16_Glosari_End.pdf", 173, -1) # -1 means to the end
]

try:
    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    for filename, start, end in chapter_map:
        writer = pypdf.PdfWriter()
        
        # Handle "End" case
        if end == -1:
            end_idx = total_pages
        else:
            end_idx = end
            
        start_idx = start - 1 # 0-indexed
        
        # Add pages
        for i in range(start_idx, end_idx):
            if i < total_pages:
                writer.add_page(reader.pages[i])
        
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "wb") as f_out:
            writer.write(f_out)
        print(f"Created {filename} (Pages {start}-{end_idx})")

    print("\nSplit complete!")

except Exception as e:
    print(f"Error: {e}")
