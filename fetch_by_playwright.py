from playwright.sync_api import sync_playwright
import os
import time
import random

BASE_URL = "https://ir.aboutamazon.com"
START_URL = BASE_URL + "/annual-reports-proxies-and-shareholder-letters/default.aspx"

def download_pdf(title, url, context, download_dir="downloads"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    response = context.request.get(url)
    if response.ok:
        content = response.body()
        safe_title = "".join(c if c.isalnum() else "_" for c in title)
        file_path = os.path.join(download_dir, safe_title + ".pdf")
        with open(file_path, "wb") as f:
            f.write(content)
        print(f"Downloaded '{title}' to {file_path}")
    else:
        print(f"Failed to download '{title}', status: {response.status}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(\
            #proxy={"server": "http://your_proxy:port"},  # Uncomment and set your proxy if needed
            extra_http_headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                'Referer': 'https://ir.aboutamazon.com/',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                # add any additional headers here
                "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            })
        page = context.new_page()
        print(f"Navigating to {START_URL}")
        page.goto(START_URL, timeout=60000)
        page.wait_for_load_state("networkidle")
        page.screenshot()
        
        # Use Playwright to query all <a> tags
        links = page.query_selector_all("a")
        letters = []
        for link in links:
            text = link.inner_text().strip()
            if "Letter to Shareholders" in text:
                href = link.get_attribute("href")
                if not href.startswith("http"):
                    href = BASE_URL + href
                letters.append((text, href))
            #else:
                #print(f"Skipping link: {text}")
        
        print(f"Found {len(letters)} letters")
        for title, url in letters:
            print(f"Title: {title}")
            print(f"URL: {url}\n")
        
        # Download each PDF letter file
        for title, url in letters:
            download_pdf(title, url, context)
            time.sleep(random.randint(5,10))  # Optional: sleep to avoid overwhelming the server
        browser.close()

if __name__ == "__main__":
    main()