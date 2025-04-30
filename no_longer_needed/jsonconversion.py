#This code was used to convert my data from .txt into .jsonl format


import json

# Convert your text file into JSON format
data = []
with open("scraped_data.txt", "r", encoding="utf-8") as file:
    content = file.read().strip().split("###Question\n")[1:]  # Split by "###Question"

    for block in content:
        parts = block.strip().split("###Answer\n")
        if len(parts) == 2:
            question = parts[0].strip()
            answer = parts[1].strip()
            data.append({"question": question, "answer": answer})

# Save the converted data as JSONL
with open("formatted_data.jsonl", "w", encoding="utf-8") as out_file:
    for entry in data:
        json.dump(entry, out_file)
        out_file.write("\n")

print("Data successfully converted to JSONL format.")