import os
from bs4 import BeautifulSoup

TEMPLATE_DIR = "templates"

def remove_cookie_popup_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Define all known IDs or classes related to the cookie banner
    targets = [
        "onetrust-banner-sdk", "onetrust-consent-sdk", "onetrust-policy-text",
        "onetrust-button-group-parent", "onetrust-close-btn-container",
        "onetrust-pc-btn-handler", "onetrust-accept-btn-handler",
        "onetrust-reject-all-handler", "onetrust-button-group"
    ]

    # Remove any matching tags by id or class
    for target in targets:
        tag_by_id = soup.find(id=target)
        if tag_by_id:
            tag_by_id.decompose()
        for tag_by_class in soup.find_all(class_=target):
            tag_by_class.decompose()

    # Save cleaned file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"Cleaned: {filepath}")

# Process all HTML files in the templates folder
for filename in os.listdir(TEMPLATE_DIR):
    if filename.endswith(".html"):
        remove_cookie_popup_from_file(os.path.join(TEMPLATE_DIR, filename))

print("Cookie popup removal complete.")
