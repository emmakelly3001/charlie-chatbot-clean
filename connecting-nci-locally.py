import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver

# === Mapping of NCI URLs to expected local filenames ===
pages_to_scrape = {
    "https://www.ncirl.ie/About/EDI/Autism-Acceptance-Festival": "a-look-back-at-this-year’s-autism-acceptance-festival.html",
   }

# === Setup Paths ===
BASE_DOMAIN = "https://www.ncirl.ie"
TEMPLATE_DIR = "templates"
STATIC_DIR = "static"

os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# === Headless Selenium Setup ===
options = webdriver.ChromeOptions()
options.add_argument("headless=new")
driver = webdriver.Chrome(options=options)

# === Download Static Assets ===
def download_asset(url, subfolder):
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        url = urljoin(BASE_DOMAIN, url)
    
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        return url  # skip
    
    local_folder = os.path.join(STATIC_DIR, subfolder)
    os.makedirs(local_folder, exist_ok=True)
    local_path = os.path.join(local_folder, filename)
    local_href = f"/static/{subfolder}/{filename}"

    if os.path.exists(local_path):
        return local_href

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(r.content)
            return local_href
    except:
        pass

    return url  # fallback to original

# === Clean and Save a Page ===
def clean_and_save(url, filename):
    driver.get(url)
    time.sleep(3)

    if "404" in driver.title or "Page Not Found" in driver.page_source:
        print(f"[SKIPPED] 404 page: {url}")
        return

    soup = BeautifulSoup(driver.page_source, "html.parser")


    # Fix asset links
    for tag in soup.find_all("link", href=True):
        if "stylesheet" in tag.get("rel", []):
            tag["href"] = download_asset(tag["href"], "css")

    for tag in soup.find_all("script", src=True):
        tag["src"] = download_asset(tag["src"], "js")

    for tag in soup.find_all("img", src=True):
        tag["src"] = download_asset(tag["src"], "img")

    # Save HTML
    filepath = os.path.join(TEMPLATE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print(f"[SAVED] {url} → {filepath}")

# === Run the scraper ===
for url, filename in pages_to_scrape.items():
    clean_and_save(url, filename)

driver.quit()
print(" Scraping complete.")
