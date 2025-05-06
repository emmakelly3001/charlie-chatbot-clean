import os
from bs4 import BeautifulSoup

TEMPLATE_DIR = "templates"

for filename in os.listdir(TEMPLATE_DIR):
    if filename.endswith(".html"):
        filepath = os.path.join(TEMPLATE_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        changed = False

        for a_tag in soup.find_all("a", href=True):
            img = a_tag.find("img")
            if img:
                alt_text = img.get("alt", "")
                class_list = " ".join(img.get("class", []))
                if "logo" in (alt_text + class_list).lower():
                    if a_tag["href"] != "/":
                        a_tag["href"] = "/"
                        changed = True

        if changed:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(soup))
            print(f" Updated logo link in: {filename}")
        else:
            print(f" No logo link updated in: {filename}")
