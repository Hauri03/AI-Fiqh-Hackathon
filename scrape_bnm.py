import asyncio
import csv
import os
import re
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
        markdown_table = []
        rows = table.find_all('tr')
        if not rows:
            continue
            
        # Headers
        headers = []
        first_row = rows[0]
        cells = first_row.find_all(['th', 'td'])
        headers = [clean_text(cell.get_text()) for cell in cells]
        
        if not headers:
            continue
            
        markdown_table.append(f"| {' | '.join(headers)} |")
        markdown_table.append(f"| {' | '.join(['---'] * len(headers))} |")
        
        # Data
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            row_data = [clean_text(cell.get_text()) for cell in cells]
            # Pad row if needed
            while len(row_data) < len(headers):
                row_data.append("")
            markdown_table.append(f"| {' | '.join(row_data)} |")
        
        # Replace table with markdown
        new_tag = soup.new_tag("p")
        new_tag.string = "\n" + "\n".join(markdown_table) + "\n"
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
        content_loc = page.locator('.journal-content-article')
        content_md = ""
        
        if await content_loc.count() > 0:
            # multiple elements might exist, take the first visible one or the main one
            # The error showed: 1) Print Notices... 2) .asset-content > .journal-content-article
            # Usually the second one is better if nested, but .first is safer than erroring.
            # Let's try to get the one with the most text or just the first.
            # For now, .first reduces the error rate immediately.
            html = await content_loc.first.inner_html()
            content_md = html_to_markdown(html)
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

SUPABASE_URL = "https://wndnznopltyrbiujyhgh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InduZG56bm9wbHR5cmJpdWp5aGdoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODg3NzE1OCwiZXhwIjoyMDg0NDUzMTU4fQ.i8GtCqey7PW8q21E3Mw1fQKxYPmGIfQBOZr1HGGbu48"
TABLE_NAME = "bnm_notices"

def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

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
        final_data = []
        for i, item in enumerate(new_items):
            print(f"[{i+1}/{len(new_items)}] Scraping NEW article: {item['title'][:40]}...")
            
            data = await scrape_details(page, item['url'], item['title'])
            
            # 4. Upload DIRECTLY to Supabase (Successive Upsert)
            try:
                response = supabase.table(TABLE_NAME).upsert(data, on_conflict="url").execute()
                print(f"   -> Uploaded to Supabase.")
            except Exception as e:
                print(f"   -> FAILED to upload: {e}")

            # Small delay to be polite
            await asyncio.sleep(0.5)
            
    finally:
        await close_browser(playwright, browser)

if __name__ == "__main__":
    asyncio.run(run_scraper())
