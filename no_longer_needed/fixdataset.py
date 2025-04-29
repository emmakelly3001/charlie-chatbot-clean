import json
import re

input_path = "final_finetune_dataset_styled_cleaned.jsonl"
output_path = "final_finetune_dataset_mainlink.jsonl"

# Read the cleaned dataset
with open(input_path, 'r', encoding='utf-8') as f:
    dataset = [json.loads(line) for line in f.readlines()]

# Function to clean and trim outputs
def keep_main_link_only(output_html):
    # Step 1: Keep everything before "See more related articles here" if it exists
    split_text = output_html.split("See more related articles here:")
    main_text = split_text[0]

    # Step 2: Optionally clean trailing line breaks or empty <p> after trimming
    main_text = re.sub(r'<p>\s*</p>', '', main_text)
    main_text = main_text.strip()

    return main_text

# Clean all entries
cleaned_dataset = []
for entry in dataset:
    cleaned_entry = entry.copy()
    cleaned_entry['output'] = keep_main_link_only(cleaned_entry['output'])
    cleaned_dataset.append(cleaned_entry)

# Save the cleaned dataset
with open(output_path, 'w', encoding='utf-8') as f:
    for item in cleaned_dataset:
        json.dump(item, f, ensure_ascii=False)
        f.write('\n')

print("✅ Finished! Only main links kept.")
print("✅ New file saved as:", output_path)
