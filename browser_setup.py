"""
Browser setup with anti-detection measures for PropertyGuru scraping.
Uses Firefox with non-headless mode, cookies, and stealth techniques.
"""

import os
from typing import Tuple
from playwright.async_api import async_playwright, Browser, BrowserContext
from playwright_stealth import stealth_async

# ABSOLUTE IMPORT
from src.modules.utils import load_cookies
from src.core.config import ROOT_DIR  # Assuming we might need this later, but good practice

__VERSION__ = "2025-01-05_PRODUCTION"


from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright

async def setup_browser(cookies_path: str = None, worker_index: int = 0) -> Tuple[Playwright, Browser, BrowserContext]:
    """
    Initialize Firefox browser with anti-detection measures.
    
    Args:
        cookies_path: Path to cookies.json file (optional)
        worker_index: Index for window positioning (default 0)
        
    Returns:
        Tuple of (browser, context)
    """
    playwright = await async_playwright().start()
    
    print(f"Launching Firefox browser (Worker {worker_index})...")
    
    # Calculate window position for SIDE-BY-SIDE layout
    # Assuming 1920x1080 screen
    screen_width = 1920
    half_width = screen_width // 2
    
    if worker_index == 0:
        win_x = 0
        win_y = 0
    else:
        win_x = half_width
        win_y = 0
        
    win_w = half_width
    win_h = 1000 # Leave room for taskbar
    
    # Launch Firefox in non-headless mode (more human-like)
    # Removing geometry args as they cause "URL not found" errors in some Firefox versions
    browser = await playwright.firefox.launch(
        headless=False,
        args=[
            '--no-remote', # Good practice for independent profiles
            # '--disable-blink-features=AutomationControlled' # Removed (Chrome only)
        ]
    )
    
    # Create context with realistic settings
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        viewport={'width': win_w, 'height': win_h}, # Match window size
        locale='en-MY',
        timezone_id='Asia/Kuala_Lumpur',
    )
    
    # Remove webdriver flag (anti-detection)
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    # Load cookies if provided
    if cookies_path and os.path.exists(cookies_path):
        print(f"Loading cookies from: {cookies_path}")
        raw_cookies = load_cookies(cookies_path)
        if raw_cookies:
            # Normalize cookies for Playwright
            normalized_cookies = []
            for cookie in raw_cookies:
                # Handle sameSite normalization
                same_site = cookie.get('sameSite')
                if same_site == 'no_restriction':
                    same_site = 'None'
                elif same_site == 'lax':
                    same_site = 'Lax'
                elif same_site == 'strict':
                    same_site = 'Strict'
                elif same_site is None or same_site == 'null' or same_site == '':
                    same_site = 'Lax'  # Default to Lax for null values
                
                normalized_cookie = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie.get('path', '/'),
                }
                
                # Add optional fields
                if cookie.get('expires') or cookie.get('expirationDate'):
                    expires = cookie.get('expirationDate', cookie.get('expires', -1))
                    if expires and expires != -1:
                        normalized_cookie['expires'] = int(expires)
                
                if cookie.get('httpOnly'):
                    normalized_cookie['httpOnly'] = cookie['httpOnly']
                if cookie.get('secure'):
                    normalized_cookie['secure'] = cookie['secure']
                if same_site:
                    normalized_cookie['sameSite'] = same_site
                
                normalized_cookies.append(normalized_cookie)
            
            await context.add_cookies(normalized_cookies)
            print(f"Loaded {len(normalized_cookies)} cookies")
        else:
            print("No cookies loaded (file empty or invalid)")
    else:
        print("No cookie file provided - phone numbers may not be accessible")
    
    # Note: Stealth patches will be applied to individual pages in scraper files
    # using: await stealth_async(page)
    
    print("Browser ready!\n")
    return playwright, browser, context


async def close_browser(browser: Browser) -> None:
    """
    Close the browser and cleanup.
    
    Args:
        browser: Browser instance to close
    """
    print("\nClosing browser...")
    await browser.close()
    print("Browser closed")
