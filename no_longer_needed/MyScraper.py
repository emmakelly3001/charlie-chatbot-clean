#This was the code I used to scrape NCI support hub

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import os

# Initialize the Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
driver = webdriver.Chrome(options=options)

# List of URLs to scrape
urls_to_scrape = [
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/4403640877842-Exams',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/360002531399-IT',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/6261334725276-Getting-Started',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/4403839059090-Student-Services',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/5100315593884-International',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/4416152689810-Policies-Procedures',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/6566916013724-Library',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/4619661151004-Central-Timetable-Office',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/6648647876380-Quality-and-Institutional-Effectiveness',
    'https://ncisupporthub.ncirl.ie/hc/en-ie/categories/4403640947218-Student-Experience-Sport'
]

# Open the first URL
driver.get(urls_to_scrape[0])
time.sleep(5)

# Track visited links
visited_links = []
scraped_data = []

# Function to scrape a page
def scrape_page(url):
    print(f"Scraping {url}")
    driver.get(url)
    time.sleep(3)

    # Collect <h2> elements
    h2_elements = driver.find_elements(By.CSS_SELECTOR, 'h2.h3 a')
    h2_links = [h2.get_attribute('href') for h2 in h2_elements if h2.get_attribute('href')]

    for href in h2_links:
        if href not in visited_links:
            visited_links.append(href)
            print(f"Found h2 link: {href}")

            driver.get(href)
            time.sleep(3)

            ul_elements = driver.find_elements(By.CSS_SELECTOR, 'ul[class^="row"]')

            for ul in ul_elements:
                list_items = ul.find_elements(By.TAG_NAME, 'li')

                for li in list_items:
                    a_tag = li.find_element(By.TAG_NAME, 'a')
                    inner_href = a_tag.get_attribute('href')
                    print(f"Found inner href: {inner_href}")

                    driver.get(inner_href)
                    time.sleep(3)

                    try:
                        title = driver.title
                        print(f"Question: {title}")

                        article_section = driver.find_element(By.CSS_SELECTOR, 'section.content.article-content.mb-6[itemprop="articleBody"]')

                        # Remove images
                        images = article_section.find_elements(By.TAG_NAME, 'img')
                        for img in images:
                            driver.execute_script("arguments[0].style.display = 'none';", img)

                        content = article_section.text.strip()
                        print(f"Answer: {content}")

                        current_article_url = driver.current_url
                        print(f"Article URL: {current_article_url}")

                        hyperlinks = []
                        link_elements = article_section.find_elements(By.TAG_NAME, 'a')
                        for link in link_elements:
                            href = link.get_attribute('href')
                            if href:
                                hyperlinks.append(href)
                        print(f"Found {len(hyperlinks)} hyperlinks.")

                        scraped_data.append({
                            "question": title,
                            "answer": content,
                            "url": current_article_url,
                            "internal_links": hyperlinks
                        })

                    except Exception as e:
                        print("Error finding article content:", e)

                    # Go back
                    driver.back()
                    time.sleep(2)

    driver.get(url)
    time.sleep(2)

# Start scraping
for url in urls_to_scrape:
    scrape_page(url)

# Save raw scraped data
raw_data_path = "scraped_articles_raw.jsonl"
with open(raw_data_path, "w", encoding="utf-8") as f:
    for item in scraped_data:
        json.dump(item, f, ensure_ascii=False)
        f.write('\n')

print(f"Scraped raw data saved to '{raw_data_path}'")

# Process scraped data: add dynamic footer and prepare fine-tuning format
processed_data_path = "scraped_articles_for_finetune.jsonl"
final_data = []

for item in scraped_data:
    question = item["question"]
    answer = item["answer"]
    article_url = item["url"]
    internal_links = item.get("internal_links", [])

    if internal_links:
        first_link = internal_links[0]
    else:
        first_link = article_url

    # Build footer
    footer = (
        f'<p>For more information, please visit our website where we answer the question '
        f'<a href="{first_link}" target="_blank">here</a>, or '
        f'<a href="https://ncisupporthub.ncirl.ie/hc/en-ie/requests/new" target="_blank">open a ticket with student support</a>.</p>'
    )

    full_answer = answer + "\n\n" + footer

    final_data.append({
        "instruction": "Answer the following question using clear HTML formatting, including any important links if relevant.",
        "input": question,
        "output": full_answer
    })

# Save final processed data
with open(processed_data_path, "w", encoding="utf-8") as f:
    for item in final_data:
        json.dump(item, f, ensure_ascii=False)
        f.write('\n')

print(f"Processed fine-tuning data saved to '{processed_data_path}'")

# Close the browser
driver.quit()
