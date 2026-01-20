from supabase import create_client

SUPABASE_URL = "https://wndnznopltyrbiujyhgh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InduZG56bm9wbHR5cmJpdWp5aGdoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODg3NzE1OCwiZXhwIjoyMDg0NDUzMTU4fQ.i8GtCqey7PW8q21E3Mw1fQKxYPmGIfQBOZr1HGGbu48"

def verify():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Fetch all 5 items we just uploaded
    response = supabase.table("bnm_notices").select("title, content").order("updated_at", desc=True).limit(5).execute()
    
    for i, item in enumerate(response.data):
        print(f"\n--- Item {i+1}: {item['title']} ---")
        # Print a chunk of content to see if tables look right
        # We look for markdown table syntax
        if "|" in item['content']:
            print("Found table structure:")
            lines = item['content'].split('\n')
            for line in lines:
                if "|" in line:
                    print(line)
        else:
            print("No table found in this item.")

if __name__ == "__main__":
    verify()
