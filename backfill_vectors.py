import os
import json
from datetime import datetime
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv

# Load env variables (API Keys)
load_dotenv()

# --- Configuration ---
SUPABASE_URL = "https://wndnznopltyrbiujyhgh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InduZG56bm9wbHR5cmJpdWp5aGdoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODg3NzE1OCwiZXhwIjoyMDg0NDUzMTU4fQ.i8GtCqey7PW8q21E3Mw1fQKxYPmGIfQBOZr1HGGbu48"
SOURCE_TABLE = "bnm_notices"
VECTOR_TABLE = "bnm_notices_vectors"
MODEL = "text-embedding-3-large"

# Initialize Clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chunks(text, chunk_size=2000, overlap=200):
    """
    Simple character-based chunking with overlap.
    In production, use a markdown-aware splitter (e.g. LangChain).
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
        
    return chunks

def get_embedding(text):
    """Generates embedding for a single string."""
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input=[text], model=MODEL).data[0].embedding

def backfill():
    print("Fetching existing notices...")
    # Fetch all notices (you might want to paginate this if > 1000)
    response = supabase.table(SOURCE_TABLE).select("*").execute()
    notices = response.data
    print(f"Found {len(notices)} notices to process.")

    for i, notice in enumerate(notices):
        url = notice['url']
        title = notice.get('title', 'No Title')
        content = notice.get('content', '')
        
        print(f"[{i+1}/{len(notices)}] Processing: {title[:50]}...")
        
        # 1. Check if already vectorized? 
        # (Optional: skip if exists, but for now we overwrite/add to ensure freshness)
        
        # 2. Chunk content
        chunks = get_chunks(content)
        print(f"   -> Split into {len(chunks)} chunks.")
        
        vectors_to_upload = []
        for idx, chunk_text in enumerate(chunks):
            try:
                # 3. Generate Embedding
                embedding = get_embedding(chunk_text)
                
                # 4. Prepare Record
                vector_record = {
                    "url": url,
                    "chunk_index": idx,
                    "content": chunk_text,
                    "metadata": {
                        "title": title,
                        "date": notice.get('date'),
                        "source": "bnm_scraper"
                    },
                    "embedding": embedding
                }
                vectors_to_upload.append(vector_record)
            except Exception as e:
                print(f"   -> Error embedding chunk {idx}: {e}")
        
        # 5. Upload Chunks
        if vectors_to_upload:
            try:
                # Upsert might be tricky if we don't have a unique constraint on (url, chunk_index)
                # But ID is random UUID.
                # Use insert for now. To prevent duplicates on re-run, we should probably delete old ones for this URL first.
                
                # Cleanup old vectors for this URL
                supabase.table(VECTOR_TABLE).delete().eq("url", url).execute()
                
                # Insert new
                supabase.table(VECTOR_TABLE).insert(vectors_to_upload).execute()
                print(f"   -> Uploaded {len(vectors_to_upload)} vectors.")
            except Exception as e:
                print(f"   -> Upload Error: {e}")

if __name__ == "__main__":
    backfill()
