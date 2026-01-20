import pypdf
import os

pdf_dir = "Split_Chapters"
if not os.path.exists(pdf_dir):
    print(f"Directory {pdf_dir} does not exist.")
    exit()

files = sorted([f for f in os.listdir(pdf_dir) if f.endswith(".pdf")])

with open("page_counts.txt", "w", encoding="utf-8") as f:
    f.write(f"{'Filename':<50} | {'Pages':<5}\n")
    f.write("-" * 60 + "\n")
    
    for filename in files:
        try:
            path = os.path.join(pdf_dir, filename)
            reader = pypdf.PdfReader(path)
            f.write(f"{filename:<50} | {len(reader.pages):<5}\n")
        except Exception as e:
            f.write(f"{filename:<50} | Error: {e}\n")

print("Done writing to page_counts.txt")
