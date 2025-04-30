#This was another attempt to fine-tune the dataset, so I could use the LLM

import json
import re

# Paths
input_path = "final_finetune_dataset_styled.jsonl"
output_path = "final_finetune_dataset_styled.jsonl"

final_data = []

with open(input_path, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        question = item["question"]
        answer = item["answer"]

        # Process paragraphs and lists
        paragraphs = answer.split("\n")
        styled_paragraphs = []
        inside_list = False

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Add <hr> before related links
            if para.lower().startswith("see more") or para.lower().startswith("related"):
                if inside_list:
                    styled_paragraphs.append("</ul>")
                    inside_list = False
                styled_paragraphs.append("<hr>")
                styled_paragraphs.append(f"<p>{para}</p>")
                continue

            # Detect bullet points
            if re.match(r"^[-*]\s+", para) or re.match(r"^\d+\.", para):
                if not inside_list:
                    styled_paragraphs.append("<ul>")
                    inside_list = True
                clean_text = re.sub(r"^[-*]\s+|\d+\.\s+", "", para).strip()
                styled_paragraphs.append(f"<li>{clean_text}</li>")
                continue
            else:
                if inside_list:
                    styled_paragraphs.append("</ul>")
                    inside_list = False

            # Style strong keywords
            important_words = ["Steps", "Tip:", "Note:", "Important:"]
            for word in important_words:
                para = para.replace(word, f"<strong>{word}</strong>")

            # If paragraph looks like a title, wrap in <h3>
            if para.endswith(":") and len(para.split()) <= 8:
                styled_paragraphs.append(f"<h3>{para}</h3>")
            else:
                styled_paragraphs.append(f"<p>{para}</p>")

        if inside_list:
            styled_paragraphs.append("</ul>")

        # Join the final styled answer
        styled_answer = "\n".join(styled_paragraphs)

        final_data.append({
            "instruction": "Answer the following question using clear HTML formatting, including important links where relevant.",
            "input": question,
            "output": styled_answer
        })

# Save final instruction-tuned HTML styled file
with open(output_path, "w", encoding="utf-8") as f:
    for item in final_data:
        json.dump(item, f, ensure_ascii=False)
        f.write("\n")

print(f"Dataset saved to {output_path}")
