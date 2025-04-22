#This is the code used to scrape the NCI website

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

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

# Wait for the page to load
time.sleep(5)

# Track visited links
visited_links = []
scraped_data = []

# Function to scrape the content of a page
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

            # Visit the link
            driver.get(href)
            time.sleep(3)

            # Collect <ul> elements that start with 'row'
            ul_elements = driver.find_elements(By.CSS_SELECTOR, 'ul[class^="row"]')

            for ul in ul_elements:
                list_items = ul.find_elements(By.TAG_NAME, 'li')

                for li in list_items:
                    a_tag = li.find_element(By.TAG_NAME, 'a')
                    inner_href = a_tag.get_attribute('href')
                    print(f"Found inner href: {inner_href}")

                    # Visit the inner href
                    driver.get(inner_href)
                    time.sleep(3)

                    try:
                        # Get the title and save it as 'question'
                        title = driver.title
                        print(f"Question: {title}")

                        # Find the section containing the article body
                        article_section = driver.find_element(By.CSS_SELECTOR, 'section.content.article-content.mb-6[itemprop="articleBody"]')

                        # Remove all images from the content
                        images = article_section.find_elements(By.TAG_NAME, 'img')
                        for img in images:
                            driver.execute_script("arguments[0].style.display = 'none';", img)

                        # Get the content text (excluding images) and save it as 'answer'
                        content = article_section.text
                        print(f"Answer: {content}")

                        # Save the title and content to scraped_data
                        scraped_data.append({"question": title, "answer": content})

                    except Exception as e:
                        print("Error finding article content:", e)


                    # Return to the previous page
                    driver.back()
                    time.sleep(2)

    # Return to the main page after scraping
    driver.get(url)
    time.sleep(2)

# Loop through each URL in the list and scrape
for url in urls_to_scrape:
    scrape_page(url)

# Save the scraped data to a file
with open("scraped_data.txt", "w", encoding="utf-8") as file:
    for data in scraped_data:
        # Write the question and answer (accessing the dictionary keys properly)
        file.write(f"Question: {data['question']}\n")
        file.write(f"Answer: {data['answer']}\n")
        file.write("\n\n")

print("Scraping completed and saved to 'scraped_data.txt'")

# Close the driver after finishing
driver.quit()