#This was an attempt to finetune my model I did on April 25th

from trl import SFTTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
import datasets

# Load dataset
dataset = datasets.load_dataset("json", data_files="html_finetune_dataset.jsonl", split="train")

# Load model and tokenizer
model_path = "./fine_tuned_model"
model = AutoModelForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token

# Training arguments
training_args = TrainingArguments(
    output_dir="./html_model",
    per_device_train_batch_size=2,  # adjust depending on your GPU
    num_train_epochs=2,
    learning_rate=2e-5,
    logging_steps=10,
    save_strategy="epoch",
    save_total_limit=1,
    evaluation_strategy="no",
)

# Define how to format each sample
def formatting_func(example):
    return f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"

# Create trainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    formatting_func=formatting_func,
    args=training_args,
)


# Train
trainer.train()
trainer.save_model("./html_model")
