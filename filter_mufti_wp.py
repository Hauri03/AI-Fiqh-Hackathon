import csv
import json
import os

# Stricter keywords for finance
keywords = [
    "kewangan", "bank", "pelaburan", "saham", "riba", "hutang", 
    "zakat", "emas", "takaful", "insurans", "forex", "cagaran", 
    "pinjaman", "faedah", "bitcoin", "sukuk", "asb", "asn", "epf", "kwsp"
]

csv_file = "Scrape-page-details-from-muftiwp.gov.my-2026-01-20.csv"
results = []

print(f"Scanning {csv_file}...")

try:
    with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            content = " ".join(str(v) for v in row.values()).lower()
            
            # Count keyword occurrences to rank them? 
            # Or just check presence.
            if any(k in content for k in keywords):
                # Basic check to avoid false positives from 'jual/beli' which were removed
                results.append(row)
except Exception as e:
    print(f"Error reading {csv_file}: {e}")

# Save all matches, I will view them
print(f"Found {len(results)} matches.")
with open("mufti_wp_finance_candidates.json", "w", encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
