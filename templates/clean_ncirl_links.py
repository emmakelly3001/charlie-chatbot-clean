from bs4 import BeautifulSoup

# Load HTML
with open("templates/NCIRL.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Process all <a> tags
for a in soup.find_all("a", href=True):
    href = a["href"]

    # Disable links to ncirl.ie or /Default.aspx pages
    if "ncirl.ie" in href or "Default.aspx" in href:
        a["href"] = "#"
        a["onclick"] = "event.preventDefault()"
        a["style"] = a.get("style", "") + ";pointer-events: none; cursor: default;"

# Save the cleaned file
with open("templates/NCIRL_cleaned.html", "w", encoding="utf-8") as file:
    file.write(str(soup))

print("Cleaned links in NCIRL.html and saved as NCIRL_cleaned.html.")
