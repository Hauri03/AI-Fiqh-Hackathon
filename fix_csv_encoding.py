import csv
import os

def convert_to_utf8_sig(file_path):
    print(f"Processing {file_path}...")
    try:
        # Read the content - trying utf-8 first
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Fallback
        try:
            with open(file_path, 'r', encoding='cp1252') as f:
                content = f.read()
        except:
             print(f"Failed to read {file_path}")
             return
    except PermissionError:
        print(f"Permission denied reading {file_path}. It might be open in another program.")
        return

    # Create new file name
    base, ext = os.path.splitext(file_path)
    new_path = f"{base}_fixed{ext}"

    # Write back with utf-8-sig (BOM)
    with open(new_path, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    print(f"Successfully created {new_path} with UTF-8 BOM.")

files_to_fix = [
    r"C:\Users\Danial Syafiq\Desktop\NeuraDyn\AI Fiqh Hackathon\Scrape-page-details-from-muftiselangor.gov.my-2026-01-20.csv",
    r"C:\Users\Danial Syafiq\Desktop\NeuraDyn\AI Fiqh Hackathon\Scrape-page-details-from-muftiwp.gov.my-2026-01-20.csv"
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        convert_to_utf8_sig(file_path)
    else:
        print(f"File not found: {file_path}")
