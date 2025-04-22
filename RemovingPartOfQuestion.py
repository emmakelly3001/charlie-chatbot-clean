# The jsonl file had "\u2013 National College of Ireland" at the end of every quesion. I wanted to remove it

import json

# Input and output file paths
input_file = 'formatted_data.jsonl'
output_file = 'modified_data.jsonl'

# Open the input file for reading and output file for writing
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    # Iterate through each line in the JSONL file
    for line in infile:
        # Load the JSON object from the line
        data = json.loads(line)
        
        # Remove the unwanted part from the question after the en dash (–)
        question = data['question']
        if '\u2013 National College of Ireland' in question:
            data['question'] = question.split('\u2013 National College of Ireland')[0].strip()

        # Write the modified data to the output file
        json.dump(data, outfile, ensure_ascii=False)
        outfile.write('\n')

print("Processing complete. Modified data saved to", output_file)
