import json

with open("formatted_data.jsonl", "r", encoding="utf-8") as infile, open("instruction_tuned_data.jsonl", "w", encoding="utf-8") as outfile:
    for line in infile:
        item = json.loads(line)
        new_item = {
            "instruction": "Answer the following question in a clear and helpful way for a student at NCI.",
            "input": item["question"],
            "output": item["answer"]
        }
        outfile.write(json.dumps(new_item) + "\n")
