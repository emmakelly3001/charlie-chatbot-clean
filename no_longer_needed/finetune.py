#This code was used to finetune the original llama model 

from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
import datasets

model_path = r"C:\Users\emmak\Llama-3.2-1B"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# Ensure the tokenizer has a pad token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Load your formatted data
dataset = datasets.load_dataset("json", data_files="formatted_data.jsonl", split="train")

# Preprocess dataset to create a text prompt
def preprocess(example):
    # Concatenate the 'question' and 'answer' fields as a prompt
    return {
        "input_text": f"question: {example['question']} answer: {example['answer']}"
    }

# Apply preprocessing to the dataset
dataset = dataset.map(preprocess, remove_columns=["question", "answer"])

# Tokenize the dataset
def tokenize_function(examples):
    # Tokenize the input text and set labels equal to input_ids
    encodings = tokenizer(examples["input_text"], truncation=True, padding="max_length", max_length=512)
    encodings["labels"] = encodings["input_ids"]
    return encodings

# Tokenize both the train and evaluation datasets
dataset = dataset.map(tokenize_function, batched=True)

# Evaluate the dataset while training the model
eval_dataset = datasets.load_dataset("json", data_files="formatted_data.jsonl", split="train")
eval_dataset = eval_dataset.map(preprocess, remove_columns=["question", "answer"])
eval_dataset = eval_dataset.map(tokenize_function, batched=True)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    save_total_limit=2,
    remove_unused_columns=False,
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    eval_dataset=eval_dataset,
)

# Fine-tuning
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")