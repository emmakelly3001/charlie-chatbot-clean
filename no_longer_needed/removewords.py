import json

# Paths
input_path = "C:/Users/emmak/OneDrive - National College of Ireland/4. Fourth Year/Computing Project/MyScraper/final_finetune_dataset.jsonl"
output_path = "C:/Users/emmak/OneDrive - National College of Ireland/4. Fourth Year/Computing Project/MyScraper/final_finetune_dataset_cleaned.jsonl"

# Process and clean
cleaned_data = []

with open(input_path, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)

        # Clean the question by removing " – National College of Ireland"
        cleaned_question = item["question"].replace(" – National College of Ireland", "").strip()

        # Save the cleaned item
        cleaned_data.append({
            "question": cleaned_question,
            "answer": item["answer"]
        })

# Save cleaned dataset
with open(output_path, "w", encoding="utf-8") as f:
    for item in cleaned_data:
        json.dump(item, f, ensure_ascii=False)
        f.write("\n")

print(f"Cleaned dataset saved to {output_path}")
