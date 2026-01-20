import csv
import json
import os

keywords = [
    "kewangan", "bank", "pelaburan", "saham", "riba", "hutang", 
    "zakat", "emas", "takaful", "insurans", "niaga", "jual", 
    "beli", "trade", "forex", "cagaran", "pinjaman", "faedah"
]

csv_files = [
    "Scrape-page-details-from-muftiselangor.gov.my-2026-01-20.csv",
    "Scrape-page-details-from-muftiwp.gov.my-2026-01-20.csv"
]

results = {}

for csv_file in csv_files:
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        continue
        
    print(f"Scanning {csv_file}...")
    filtered_rows = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Adjust column names based on actual CSV structure if needed. 
                # Assuming standard scraping output often has 'question' and 'answer' or similar.
                # If keys are unknown, we'll check values.
                content = " ".join(str(v) for v in row.values()).lower()
                
                if any(k in content for k in keywords):
                    filtered_rows.append(row)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        
    results[csv_file] = filtered_rows[:20] # Keep top 20 candidates per file
    print(f"Found {len(filtered_rows)} potentially relevant rows in {csv_file}")

with open("filtered_finance_questions.json", "w", encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("Saved candidates to filtered_finance_questions.json")
