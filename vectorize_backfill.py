import os
import time
from typing import List
from supabase import create_client, Client
from openai import OpenAI

# --- Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "text-embedding-3-large"

def get_existing_ids():
    """Fetch IDs that already have embeddings."""
    try:
        response = supabase.table("bnm_notices_embeddings").select("notice_id").execute()
        return {item['notice_id'] for item in response.data}
    except Exception as e:
        print(f"Error fetching existing embeddings: {e}")
        return set()

def get_notices(exclude_ids: set):
    """Fetch notices that don't have embeddings (limited to 100 at a time)."""
    # Note: Supabase Python client doesn't support 'not.in' easily on 'id' with a large list usually,
    # so we'll fetch ID and Content, then filter in Python if list is small, 
    # or just fetch all and skip. Given ~800 items, fetching all IDs is cheap.
    
    # 1. Fetch ALL notice IDs
    print("Fetching list of all notices...")
    response = supabase.table("bnm_notices").select("id, content").execute()
    all_notices = response.data
    
    # 2. Filter
    to_process = [n for n in all_notices if n['id'] not in exclude_ids]
    return to_process

def generate_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=MODEL).data[0].embedding

def main():
    existing_ids = get_existing_ids()
    print(f"Found {len(existing_ids)} existing embeddings.")
    
    notices = get_notices(existing_ids)
    print(f"Found {len(notices)} notices pending vectorization.")
    
    if not notices:
        print("All done!")
        return

    for i, notice in enumerate(notices):
        notice_id = notice['id']
        content = notice['content']
        
        if not content:
            print(f"Skipping ID {notice_id} (No content)")
            continue
            
        print(f"[{i+1}/{len(notices)}] Vectorizing Notice ID {notice_id}...")
        
        try:
            # Generate Embedding
            embedding = generate_embedding(content)
            
            # Insert into separate table
            data = {
                "notice_id": notice_id,
                "embedding": embedding
            }
            supabase.table("bnm_notices_embeddings").insert(data).execute()
            
            # Sleep briefly to avoid hitting standard tier rate limits too hard
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Error processing ID {notice_id}: {e}")
            # Identify if it's a rate limit error
            if "rate_limit" in str(e).lower():
                print("Rate limit hit. Sleeping for 10 seconds...")
                time.sleep(10)

if __name__ == "__main__":
    main()
