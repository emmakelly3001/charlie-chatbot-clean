# I used this to generate a preview of my dataset, to see how all of my answers would look when they were formatted

import json

# Load your cleaned dataset
input_path = "final_finetune_dataset_mainlink.jsonl"
output_path = "final_finetune_dataset_full_preview.html"

# Read dataset
with open(input_path, 'r', encoding='utf-8') as f:
    dataset = [json.loads(line) for line in f.readlines()]

# Build full HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Full Dataset Preview</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .entry { margin-bottom: 60px; }
        .input { font-weight: bold; font-size: 20px; margin-bottom: 10px; color: #2c3e50; }
        .output { background: #f4f4f4; padding: 20px; border-radius: 8px; }
        hr { margin: 40px 0; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>Complete Styled Dataset Preview</h1>
"""

# Add all entries (no limits)
for entry in dataset:
    html_content += f"""
    <div class="entry">
        <div class="input">Question: {entry['input']}</div>
        <div class="output">{entry['output']}</div>
    </div>
    <hr>
    """

html_content += """
</body>
</html>
"""

# Save the HTML
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Preview saved as:", output_path)
