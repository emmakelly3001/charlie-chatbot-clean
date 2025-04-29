# Import necessary libraries
from flask import Flask, request, jsonify, render_template, send_from_directory
import logging
import torch
import random
import bleach
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import datasets
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util
from flask_cors import CORS
from bs4 import BeautifulSoup
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Suppress unnecessary warnings from transformers
logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)

# === Load Fine-tuned Charlie Model ===
model_path = "./fine_tuned_model"  # Path to your custom fine-tuned model
device = "cuda" if torch.cuda.is_available() else "cpu"  # Use GPU if available
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path).to(device)

# Set padding token if not already set
tokenizer.pad_token = tokenizer.eos_token if tokenizer.pad_token is None else tokenizer.pad_token

# Create a text generation pipeline using the model
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if device == "cuda" else -1
)

# === Load the Instruction-Tuned Dataset ===
dataset = datasets.load_dataset("json", data_files="final_finetune_dataset_mainlink.jsonl", split="train")
# Create a simple dictionary mapping questions to answers
qa_dict = {item["input"]: item["output"] for item in dataset}

# === Load Sentence Transformer for Semantic Matching ===
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
questions = list(qa_dict.keys())
question_embeddings = semantic_model.encode(questions, convert_to_tensor=True)

# === Find Best Match Logic (Fuzzy + Semantic Matching) ===
def find_best_match(user_question, qa_dict, question_embeddings, threshold_fuzzy=90, threshold_semantic=0.75):
    # Direct match
    if user_question in qa_dict:
        return user_question

    # Fuzzy match
    best_fuzzy_match = max(qa_dict.keys(), key=lambda q: fuzz.ratio(user_question.lower(), q.lower()), default=None)
    fuzzy_score = fuzz.ratio(user_question.lower(), best_fuzzy_match.lower())

    if fuzzy_score >= threshold_fuzzy:
        return best_fuzzy_match

    # Semantic match
    user_embedding = semantic_model.encode(user_question, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(user_embedding, question_embeddings)[0]
    best_semantic_score, best_idx = torch.max(similarities, dim=0)

    if best_semantic_score >= threshold_semantic:
        return questions[best_idx]

    # No good match found
    return None

# === Fallback Message for Unmatched Questions ===
def random_fallback():
    options = [
        "I'm not too sure about that one. Could you try rephrasing your question? I can help with queries related to NCI!",
        "Hmm, I don’t have an answer for that. Try asking me something else related to NCI.",
        "Sorry, I didn’t catch that. Maybe try asking in a different way?",
        "I couldn’t find a match for that question. I’m best at answering things about NCI!",
        "That one’s a bit outside my scope — if it's NCI-related, feel free to reword it!",
        "I’m not quite sure how to answer that. Want to try asking it a different way?",
    ]
    return random.choice(options)

# === Friendly Tone Wrapper (adds opening and closing phrases) ===
def wrap_with_friendly_tone(answer):
    openings = [
        "Sure! Here's what I found:",
        "No problem, this should help:",
        "Absolutely, happy to help!",
        "Here's what I can tell you:",
        "Of course! Here's the info:",
    ]
    closings = [
        "Let me know if you need anything else!",
        "Hope that clears things up!",
        "Do you have anymore questions for me?",
        "I'm here if you need anything else!",
    ]
    opening = random.choice(openings)
    closing = random.choice(closings)

    # Sanitize the answer to remove any dangerous HTML
    clean_answer = bleach.clean(answer, tags=['b', 'i', 'u', 'em', 'strong', 'p', 'ul', 'li', 'br'], strip=True)

    # Wrap answer nicely inside paragraph tags
    return f"<p>{opening}</p>{clean_answer.strip()}<p>{closing}</p>"
# === Setup Flask App ===
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS (allow frontend apps to communicate)

# === Setup Rate Limiter ===
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]  # 10 requests per minute per IP
)

# === Chat API Endpoint ===
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '').strip()

    # Check if user input is empty
    if not user_input:
        return jsonify({'reply': "No input received."}), 400

    # Quick replies for common small-talk
    small_talk_responses = {
        "hi": "Hey there!",
        "hello": "Hello! How can I help you today?",
        "how are you": "I'm doing great, thanks! How can I help you today?",
        "how are you doing": "I'm doing well, thank you! Let me know if there's anything I can help with.",
        "thank you": "You're very welcome!",
        "thanks": "No problem at all!",
    }

    clean_input = user_input.lower().strip("?!.")  # Normalize small talk
    if clean_input in small_talk_responses:
        return jsonify({'reply': small_talk_responses[clean_input]})

    # Try to find best match from dataset
    matched_question = find_best_match(user_input, qa_dict, question_embeddings)

    if matched_question:
        matched_answer = qa_dict[matched_question]

        # No rephrasing — directly use dataset answer
        output = matched_answer.strip()

        # Wrap answer nicely
        reply = wrap_with_friendly_tone(output)

        print(f"\n[Original]: {matched_answer}\n[Final Reply]: {reply}\n")
    else:
        # Use fallback if no match found
        reply = random_fallback()

    return jsonify({'reply': reply})

# === Homepage Route (Serves NCI.html) ===
@app.route('/')
def serve_homepage():
    return render_template('NCI.html')

# === Static Files Route (Serves files for the site like JS, CSS, images) ===
@app.route('/National College of Ireland_files/<path:filename>')
def static_from_saved_site(filename):
    return send_from_directory('National College of Ireland_files', filename)

# === Run the Flask App ===
if __name__ == '__main__':
    print("Charlie is running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
