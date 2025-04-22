#this page is being used to format my txt file as needed to fine-tune it
import re

# Read the original text file
with open("scraped_data.txt", "r", encoding="utf-8") as file:
    content = file.read()

# Replace the "Question:" and "Answer:" labels with the new format
formatted_content = re.sub(r'Question:', '###Question\n', content)
formatted_content = re.sub(r'Answer:', '###Answer\n', formatted_content)

# Write the modified content back to the file
with open("scraped_data.txt", "w", encoding="utf-8") as file:
    file.write(formatted_content)

print("File formatting complete.")