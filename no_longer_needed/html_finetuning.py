#This was another attempt to finetune my model

import json

# Load your formatted HTML dataset
with open("formatted_instruction_tuned_data.jsonl", "r", encoding="utf-8") as f:
    original_data = [json.loads(line) for line in f]

# Create a new fine-tuning dataset
new_finetune_data = []

for entry in original_data:
    question = entry["question"]
    answer_html = entry["answer_html"]

    # We simulate output as slightly reworded (for now keep identical)
    simulated_output = answer_html  # Later you could human-edit a few if you want

    new_entry = {
        "instruction": "Rephrase the following HTML text to sound more student-friendly, without changing the HTML structure.",
        "input": answer_html,
        "output": simulated_output
    }
    new_finetune_data.append(new_entry)

# Save to new JSONL file
with open("html_finetune_dataset.jsonl", "w", encoding="utf-8") as f:
    for item in new_finetune_data:
        json.dump(item, f)
        f.write("\n")

print("Finished creating new fine-tune dataset!")
