#This was used to finish off the dataset, and only keep what I needed. This was the final change made.

import json

# Paths to your files
input_file = 'final_finetune_dataset_mainlink.jsonl'
output_file = 'dataset.jsonl'

# Read the input file and remove "instruction"
cleaned_data = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        record = json.loads(line)
        record.pop('instruction', None)  # Safely remove 'instruction' if it exists
        cleaned_data.append(record)

# Write the cleaned records into a new JSONL file
with open(output_file, 'w', encoding='utf-8') as f:
    for record in cleaned_data:
        f.write(json.dumps(record) + '\n')

print("Done! Saved cleaned file to:", output_file)
