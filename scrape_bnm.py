import asyncio
import csv
import os
import re
from datetime import datetime
from typing import List, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup

# --- Browser Setup ---
async def setup_browser(worker_index: int = 0):
    playwright = await async_playwright().start()
    print(f"Launching Firefox browser (Worker {worker_index})...")
    
    win_w = 1920 // 2
    win_h = 1000

    browser = await playwright.firefox.launch(
        headless=False,
        args=['--no-remote']
    )
    
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        viewport={'width': win_w, 'height': win_h},
        locale='en-MY',
        timezone_id='Asia/Kuala_Lumpur',
    )
    
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    return playwright, browser, context

async def close_browser(playwright, browser):
    await browser.close()
    await playwright.stop()

# --- HTML to Markdown Conversion ---
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def html_to_markdown(html_content):
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process Tables
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        if not rows:
            continue

        # 1. Determine dimensions
        # A simple pass might be inaccurate if there are complex spans, 
        # so we'll just build a sparse matrix (dict) and calculate max cols later or infer it.
        # Actually, let's assume a grid.
        
        grid = {} # (row_idx, col_idx) -> text
        max_col = 0
        
        for r_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            c_idx = 0
            for cell in cells:
                # Skip if this position is already filled (by a rowspan from above)
                while (r_idx, c_idx) in grid:
                    c_idx += 1
                
                text = clean_text(cell.get_text())
                rowspan = int(cell.get('rowspan', 1))
                colspan = int(cell.get('colspan', 1))
                
                # Fill the grid
                for r in range(rowspan):
                    for c in range(colspan):
                        grid[(r_idx + r, c_idx + c)] = text
                        
                c_idx += colspan
                max_col = max(max_col, c_idx)

        # 2. Extract headers (first row) and data
        markdown_lines = []
        if rows:
            # Headers - assume row 0
            headers = []
            for c in range(max_col):
                headers.append(grid.get((0, c), ""))
            
            markdown_lines.append(f"| {' | '.join(headers)} |")
            markdown_lines.append(f"| {' | '.join(['---'] * len(headers))} |")
            
            # Data - rows 1 to end
            for r in range(1, len(rows)):
                row_cells = []
                for c in range(max_col):
                    row_cells.append(grid.get((r, c), "")) # Propagated text
                markdown_lines.append(f"| {' | '.join(row_cells)} |")

        # Replace table with markdown
        new_tag = soup.new_tag("p")
        new_tag.string = "\n" + "\n".join(markdown_lines) + "\n"
        table.replace_with(new_tag)

    # Process basic tags
    for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(h.name[1])
        h.replace_with(f"\n{'#' * level} {clean_text(h.get_text())}\n")
        
    for a in soup.find_all('a'):
        if a.has_attr('href'):
            text = clean_text(a.get_text())
            href = a['href']
            if text:
               a.replace_with(f"[{text}]({href})")

    for li in soup.find_all('li'):
        li.replace_with(f"- {clean_text(li.get_text())}\n")

    return soup.get_text(separator='\n\n').strip()

# --- Scraper Logic ---

BASE_URL = "https://www.bnm.gov.my/notices-announcements"

async def scrape_all_listings(page: Page) -> List[Dict]:
    print(f"Navigating to {BASE_URL}...")
    await page.goto(BASE_URL, timeout=60000)
    
    all_items = []
    page_num = 1
    
    while True:
        print(f"Processing Listing Page {page_num}...")
        
        # Scrape current page links
        try:
            await page.wait_for_selector('table#result', timeout=15000)
            rows = await page.locator('table#result tr').all()
            
            items_on_page = 0
            for row in rows:
                link_loc = row.locator('td a')
                if await link_loc.count() > 0:
                    href = await link_loc.first.get_attribute('href')
                    text = await link_loc.first.inner_text()
                    if href and text.strip():
                        item = {"url": href, "title": text.strip()}
                        if item not in all_items: # Simple dedup
                            all_items.append(item)
                            items_on_page += 1
            
            print(f"Found {items_on_page} items on page {page_num}. Total: {len(all_items)}")
            
        except Exception as e:
            print(f"Error reading list on page {page_num}: {e}")
            break

        # Pagination
        # Selector for 'Next': .lfr-pagination-buttons.pager li:not(.disabled) a with text "Next" or similar
        # BNM uses Liferay. Button usually looks like 'Next' in a list.
        # Let's try to find the 'Next' link.
        
        # Check if there is a 'Next' link that is not disabled
        # Method 1: finding text 'Next'
        next_btn = page.locator('.lfr-pagination-buttons.pager li:not(.disabled) a', has_text=re.compile(r'Next', re.IGNORECASE))
        
        if await next_btn.count() > 0 and await next_btn.is_visible():
            print("Clicking Next page...")
            await next_btn.first.click()
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2) # Stability
            page_num += 1
        else:
            print("No next page found or 'Next' is disabled. Reached end of listings.")
            break
            
    return all_items

async def scrape_details(page: Page, url: str, listing_title: str) -> Dict:
    # print(f"Scraping: {listing_title[:30]}...")
    try:
        await page.goto(url, timeout=45000)
        await page.wait_for_load_state('domcontentloaded')
        await stealth_async(page)
        
        # Extract metadata
        date = "N/A"
        date_loc = page.locator('.text-small.text-muted')
        if await date_loc.count() > 0:
            date = await date_loc.first.inner_text()
            
        
        # Content
        # KEY FIX: Wait for the element specifically, as some pages load it async
        try:
            await page.wait_for_selector('.journal-content-article', timeout=5000)
        except:
            pass # count will be 0 below if not found
            
        content_loc = page.locator('.journal-content-article')
        content_md = ""
        
        count = await content_loc.count()
        if count > 0:
            found_valid_content = False
            for i in range(count):
                element = content_loc.nth(i)
                text_content = await element.inner_text()
                
                # Filter out short garbage (e.g. "Print" button)
                if len(text_content) < 100:
                    continue

                # Filter out the Sidebar
                # The sidebar typically contains "Filter by year" and "Search keywords"
                if "Filter by year" in text_content and "Search keywords" in text_content:
                    continue
                
                # This is likely the real content
                html = await element.inner_html()
                content_md = html_to_markdown(html)
                found_valid_content = True
                break
            
            if not found_valid_content:
                # Fallback: if we filtered everything out, maybe the article is just weird?
                # Just take the first one (or last?) as a Hail Mary, or leave empty.
                content_md = "Error: Only sidebar found."
        else:
            # Fallback
            content_md = "No content found or stealth block."

        return {
            "url": url,
            "title": listing_title,
            "date": date.strip(),
            "content": content_md
        }
        
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return {
            "url": url,
            "title": listing_title,
            "date": "Error",
            "content": f"Error: {str(e)}"
        }

# --- Supabase Setup ---
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv

# Load env (for OpenAI)
load_dotenv()

SUPABASE_URL = "https://wndnznopltyrbiujyhgh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InduZG56bm9wbHR5cmJpdWp5aGdoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODg3NzE1OCwiZXhwIjoyMDg0NDUzMTU4fQ.i8GtCqey7PW8q21E3Mw1fQKxYPmGIfQBOZr1HGGbu48"
TABLE_NAME = "bnm_notices"
VECTOR_TABLE = "bnm_notices_vectors"
MODEL = "text-embedding-3-large"

def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def init_openai():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chunks(text, chunk_size=2000, overlap=200):
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

def get_embedding(client, text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=MODEL).data[0].embedding

async def check_existing_urls(supabase: Client, urls: List[str]) -> List[str]:
    """
    Check which URLs already exist in Supabase to skip them.
    """
    if not urls:
        return []
        
    existing = []
    # Query in chunks to avoid URL length limits if checking many
    chunk_size = 20
    for i in range(0, len(urls), chunk_size):
        batch = urls[i:i+chunk_size]
        try:
            # We select only the URL column where URL is in our list
            response = supabase.table(TABLE_NAME).select("url").in_("url", batch).execute()
            if response.data:
                existing.extend([item['url'] for item in response.data])
        except Exception as e:
            print(f"Error checking existing URLs: {e}")
            
    return existing

async def run_scraper():
    supabase = init_supabase()
    openai_client = init_openai()
    
    playwright, browser, context = await setup_browser()
    page = await context.new_page()
    
    try:
        # 1. Get ALL listings
        print("Starting listing scrape...")
        all_items = await scrape_all_listings(page)
        print(f"Finished scraping listings. Found {len(all_items)} total articles.")
        
        # 2. Deduplication: Filter out items that are already in Supabase
        all_urls = [item['url'] for item in all_items]
        existing_urls = await check_existing_urls(supabase, all_urls)
        
        new_items = [item for item in all_items if item['url'] not in existing_urls]
        
        print(f"Deduplication Analysis:")
        print(f"Total Found: {len(all_items)}")
        print(f"Already in DB: {len(existing_urls)}")
        print(f"New to Scrape: {len(new_items)}")
        
        if not new_items:
            print("No new articles to scrape. Exiting.")
            return

        # 3. Scrape details for NEW items only
        for i, item in enumerate(new_items):
            print(f"[{i+1}/{len(new_items)}] Scraping NEW article: {item['title'][:40]}...")
            
            data = await scrape_details(page, item['url'], item['title'])
            
            # Add updated_at
            data['updated_at'] = datetime.utcnow().isoformat()
            
            # 4. Upload DIRECTLY to Supabase (Successive Upsert)
            try:
                # A. Main Content
                response = supabase.table(TABLE_NAME).upsert(data, on_conflict="url").execute()
                print(f"   -> Uploaded to Supabase.")
                
                # B. Vectorization
                print(f"   -> Vectorizing...")
                chunks = get_chunks(data['content'])
                vectors_to_upload = []
                for idx, chunk_text in enumerate(chunks):
                    try:
                        embedding = get_embedding(openai_client, chunk_text)
                        vector_record = {
                            "url": data['url'],
                            "chunk_index": idx,
                            "content": chunk_text,
                            "metadata": {
                                "title": data['title'],
                                "date": data['date'],
                                "source": "bnm_scraper"
                            },
                            "embedding": embedding
                        }
                        vectors_to_upload.append(vector_record)
                    except Exception as ve:
                        print(f"      -> Vector generation failed for chunk {idx}: {ve}")
                
                if vectors_to_upload:
                    # Cleanup old vectors first just in case
                    supabase.table(VECTOR_TABLE).delete().eq("url", data['url']).execute()
                    # Insert new
                    supabase.table(VECTOR_TABLE).insert(vectors_to_upload).execute()
                    print(f"   -> Uploaded {len(vectors_to_upload)} vectors.")

            except Exception as e:
                print(f"   -> FAILED to upload: {e}")
                if 'column "updated_at" of relation "bnm_notices" does not exist' in str(e):
                    print("!!! ALERT: You need to create the 'updated_at' column in Supabase first.")

            # Small delay to be polite
            await asyncio.sleep(0.5)
            try:
                response = supabase.table(TABLE_NAME).upsert(data, on_conflict="url").execute()
                print(f"   -> Uploaded to Supabase.")
            except Exception as e:
                print(f"   -> FAILED to upload: {e}")
                if 'column "updated_at" of relation "bnm_notices" does not exist' in str(e):
                    print("!!! ALERT: You need to create the 'updated_at' column in Supabase first.")

            # Small delay to be polite
            await asyncio.sleep(0.5)
            
    finally:
        await close_browser(playwright, browser)

if __name__ == "__main__":
    asyncio.run(run_scraper())
