from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model and tokenizer
model_path = r"C:\Users\emmak\OneDrive - National College of Ireland\4. Fourth Year\Computing Project\MyScraper\fine_tuned_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path).to("cuda" if torch.cuda.is_available() else "cpu")

# Interactive chat loop
print("Welcome to your fine-tuned LLaMA! Type 'exit' to quit.")
while True:
    prompt = input("You: ")
    if prompt.lower() == "exit":
        print("Goodbye!")
        break

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    outputs = model.generate(**inputs, max_length=512, num_return_sequences=1, do_sample=True, temperature=0.5, top_k=50)
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"LLaMA: {response}")
