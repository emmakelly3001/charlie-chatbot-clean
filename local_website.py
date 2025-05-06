import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from slugify import slugify

BASE_URL = "https://www.ncirl.ie"
STATIC_DIR = "static"
TEMPLATE_DIR = "templates"
PAGES_TO_SCRAPE = ["/study", "/students", "/research", "/about"]

# Create folders
os.makedirs(f"{STATIC_DIR}/css", exist_ok=True)
os.makedirs(f"{STATIC_DIR}/js", exist_ok=True)
os.makedirs(f"{STATIC_DIR}/img", exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Headless browser
options = webdriver.ChromeOptions()
options.add_argument("headless=new")
driver = webdriver.Chrome(options=options)

def slugify_path(path):
    return path.strip("/").replace("/", "-") or "index"

def download_asset(url, folder):
    try:
        if not url or "<%" in url:
            return url
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = urljoin(BASE_URL, url)

        filename = os.path.basename(urlparse(url).path)
        if not filename:
            return url

        local_path = os.path.join(STATIC_DIR, folder, filename)
        flask_path = f"/static/{folder}/{filename}"

        if os.path.exists(local_path):
            return flask_path

        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 403:
            return url

        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
        return flask_path
    except:
        return url

def save_full_page(url):
    print(f"Scraping: {url}")
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Fix assets
    for tag in soup.find_all("link", href=True):
        if "stylesheet" in tag.get("rel", []):
            tag["href"] = download_asset(tag["href"], "css")

    for tag in soup.find_all("script", src=True):
        tag["src"] = download_asset(tag["src"], "js")

    for tag in soup.find_all("img", src=True):
        tag["src"] = download_asset(tag["src"], "img")

    # Get list of slugs from templates
    saved_slugs = {
        os.path.splitext(f)[0] for f in os.listdir(TEMPLATE_DIR) if f.endswith(".html")
    }

    # Fix only internal links that match saved slugs
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if not href or href.startswith("javascript:") or href.startswith("#"):
            continue

        if href.startswith(BASE_URL):
            path = href.replace(BASE_URL, "").strip("/")
        elif href.startswith("/"):
            path = href.strip("/")
        else:
            continue

        slug = slugify(path)  # Convert to same format used for filenames

        if slug in saved_slugs:
            tag["href"] = f"/articles/{slug}"
        else:
            tag["href"] = "#"

    # Save HTML
    slug = slugify(url.replace(BASE_URL, "").strip("/")) or "index"
    filepath = os.path.join(TEMPLATE_DIR, f"{slug}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print(f"Saved: templates/{slug}.html")

# Run scraper for 4 pages only
for path in PAGES_TO_SCRAPE:
    full_url = urljoin(BASE_URL, path)
    save_full_page(full_url)

driver.quit()
print("Done. 4 pages saved.")
