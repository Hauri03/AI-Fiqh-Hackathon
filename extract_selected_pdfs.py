import pypdf
import os

pdf_dir = "Split_Chapters"
selected_pdfs = [
    "04_Bai_Al-Sarf.pdf",
    "05_Hibah.pdf",
    "06_Ijarah.pdf",
    "10_Rahn.pdf",
    "13_Wakalah.pdf"
]

output_file = "selected_pdfs_content.txt"

with open(output_file, "w", encoding="utf-8") as out:
    for pdf_name in selected_pdfs:
        pdf_path = os.path.join(pdf_dir, pdf_name)
        try:
            reader = pypdf.PdfReader(pdf_path)
            out.write(f"=== START {pdf_name} ===\n")
            for page in reader.pages:
                out.write(page.extract_text())
                out.write("\n")
            out.write(f"=== END {pdf_name} ===\n\n")
            print(f"Extracted {pdf_name}")
        except Exception as e:
            print(f"Error reading {pdf_name}: {e}")

print(f"Extraction complete. Saved to {output_file}")
