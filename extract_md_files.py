import csv
import os
import re

def clean_filename(title):
    # Keep only alphanumeric and spaces, limit length
    cleaned = re.sub(r'[^\w\s-]', '', title).strip()
    return cleaned[:50].replace(' ', '_')

def extract_md_files(csv_path, output_dir="sample_md_files", limit=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Reading from {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if count >= limit:
                break
                
            title = row.get('title', 'No Title')
            date = row.get('date', 'No Date')
            url = row.get('url', 'No URL')
            content = row.get('content', '')
            
            # Create MD content
            md_output = f"# {title}\n\n"
            md_output += f"**Date:** {date}\n"
            md_output += f"**Source:** {url}\n\n"
            md_output += "---\n\n"
            md_output += content
            
            # Save file
            filename = f"{count+1}_{clean_filename(title)}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as md_file:
                md_file.write(md_output)
                
            print(f"Created: {filepath}")
            count += 1

if __name__ == "__main__":
    extract_md_files("bnm_notices_partial.csv", limit=5)
