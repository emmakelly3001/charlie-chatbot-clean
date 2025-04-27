from transformers import AutoModelForCausalLM, AutoTokenizer

# Path to the cloned model repository
model_path = r"C:\Users\emmak\Llama-3.2-1B"

try:
    model = AutoModelForCausalLM.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    print("LLaMA model and tokenizer loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")