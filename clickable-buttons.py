import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from slugify import slugify

BASE_URL = "https://www.ncirl.ie"
TEMPLATE_DIR = "templates"
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Only scrape these missing pages
MISSING_PATHS = [
    "/register-here",
    "/postgraduate-courses",
    "/undergraduate-courses",
    "/full-time-courses",
    "/part-time-courses",
    "/cao-courses",
    "/international-students'-courses",
    "/list-of-all-courses",
    "/pay-your-fees",
    "/student-mail",
    "/cao-student-story:-ian-ray",
    "/cipd-story:-linda-conway",
    "/springboard+:-cian's-story",
    "/careers",
    "/international",
    "/fees-&-grants"
]

options = webdriver.ChromeOptions()
options.add_argument("headless=new")
driver = webdriver.Chrome(options=options)

def save_full_page(driver, url, slug):
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Fix internal links to /articles/<slug>
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.startswith("/"):
            tag["href"] = f"/articles/{slugify(href.strip('/'))}"

    filepath = os.path.join(TEMPLATE_DIR, f"{slug}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print(f"Saved: templates/{slug}.html")

# Scrape and save each missing page
for path in MISSING_PATHS:
    full_url = urljoin(BASE_URL, path)
    slug = slugify(path.strip("/"))
    print(f"Scraping: {full_url} as {slug}.html")
    try:
        driver.get(full_url)
        time.sleep(2)
        save_full_page(driver, full_url, slug)
    except Exception as e:
        print(f"Failed to scrape {full_url}: {e}")

driver.quit()
print("Done scraping missing pages.")
