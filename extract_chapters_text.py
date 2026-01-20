import os
from pypdf import PdfReader

chapter_files = [
    "04_Bai_Al-Sarf.pdf",
    "05_Hibah.pdf",
    "06_Ijarah.pdf",
    "07_Istisna.pdf",
    "08_Kafalah.pdf",
    "09_Qard.pdf",
    "10_Rahn.pdf",
    "11_Tawarruq.pdf",
    "12_Wad.pdf",
    "13_Wakalah.pdf"
]

base_dir = r"C:\Users\Danial Syafiq\Desktop\NeuraDyn\AI Fiqh Hackathon\Split_Chapters"
output_file = r"C:\Users\Danial Syafiq\Desktop\NeuraDyn\AI Fiqh Hackathon\all_chapters_content.txt"

with open(output_file, "w", encoding="utf-8") as f_out:
    for filename in chapter_files:
        file_path = os.path.join(base_dir, filename)
        f_out.write(f"=== START {filename} ===\n")
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text = page.extract_text()
                f_out.write(text)
                f_out.write("\n")
        except Exception as e:
            f_out.write(f"Error reading {filename}: {e}\n")
        f_out.write(f"=== END {filename} ===\n\n")

print(f"Extraction complete. Saved to {output_file}")
