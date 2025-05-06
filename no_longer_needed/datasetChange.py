import json
import re

input_file = "hrefs_final_cleaned.jsonl"
output_file = "final_dataset.jsonl"

# Match href="..."
href_pattern = re.compile(r'href="([^"]+)"', re.IGNORECASE)

# Match leading number before dash in the slug (after /articles/)
numeric_prefix = re.compile(r"/articles/\d+-")

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        item = json.loads(line)

        if "output" in item:
            original_output = item["output"]

            def clean_href(match):
                url = match.group(1).strip()

                # Remove numeric ID in /articles/<id>-
                url = numeric_prefix.sub("/articles/", url)

                # Separate query string or fragment
                if "?" in url:
                    base, rest = url.split("?", 1)
                    sep = "?"
                elif "#" in url:
                    base, rest = url.split("#", 1)
                    sep = "#"
                else:
                    base, rest = url, ""
                    sep = ""

                # Clean trailing / or \
                base = base.rstrip("/\\")

                return f'href="{base}{sep}{rest}"'

            item["output"] = href_pattern.sub(clean_href, original_output)

        json.dump(item, outfile, ensure_ascii=False)
        outfile.write("\n")

print(f"Final cleanup complete. Saved to: {output_file}")
