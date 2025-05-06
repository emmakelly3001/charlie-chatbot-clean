import os
from bs4 import BeautifulSoup

TEMPLATE_DIR = "templates"
TARGET_HREF = "https://www.ncirl.ie/Courses/search"

# Only modify your course search pages
target_files = [
    "postgraduate-courses.html",
    "undergraduate-courses.html",
    "full-time-courses.html",
    "part-time-courses.html",
    "cao-courses.html",
    "international-students-courses.html",
    "list-of-all-courses.html"
]

for filename in target_files:
    filepath = os.path.join(TEMPLATE_DIR, filename)

    if not os.path.exists(filepath):
        print(f"[SKIPPED] File not found: {filename}")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for a in soup.find_all("a", href=True):
        a["href"] = TARGET_HREF

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print(f"[UPDATED] All links in {filename} now point to {TARGET_HREF}")
