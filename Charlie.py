# This is the main file that loads Charlie.

# Import necessary libraries
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
import logging
import torch
import os
import random
import bleach
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import datasets
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import render_template_string

# Suppress unnecessary warnings from transformers
logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO)

# === Load Fine-tuned Charlie Model ===
model_path = "./fine_tuned_model"
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path).to(device)

tokenizer.pad_token = tokenizer.eos_token if tokenizer.pad_token is None else tokenizer.pad_token

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if device == "cuda" else -1
)

# === Load the Instruction-Tuned Dataset ===
dataset = datasets.load_dataset("json", data_files="final_dataset.jsonl", split="train")
qa_dict = {item["input"]: item["output"] for item in dataset}

# === Load Sentence Transformer for Semantic Matching ===
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
questions = list(qa_dict.keys())
question_embeddings = semantic_model.encode(questions, convert_to_tensor=True)

# === Helper Functions ===

def find_best_match(user_question, qa_dict, question_embeddings, threshold_fuzzy=90, threshold_semantic=0.75):
    if user_question in qa_dict:
        return user_question

    best_fuzzy_match = max(qa_dict.keys(), key=lambda q: fuzz.ratio(user_question.lower(), q.lower()), default=None)
    fuzzy_score = fuzz.ratio(user_question.lower(), best_fuzzy_match.lower())

    if fuzzy_score >= threshold_fuzzy:
        return best_fuzzy_match

    user_embedding = semantic_model.encode(user_question, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(user_embedding, question_embeddings)[0]
    best_semantic_score, best_idx = torch.max(similarities, dim=0)

    if best_semantic_score >= threshold_semantic:
        return questions[best_idx]

    return None

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
        "Do you have any more questions for me?",
        "I'm here if you need anything else!",
    ]
    opening = random.choice(openings)
    closing = random.choice(closings)

    clean_answer = bleach.clean(
        answer,
        tags=['b', 'i', 'u', 'em', 'strong', 'p', 'ul', 'li', 'br', 'a'],
        attributes={'a': ['href', 'target', 'title']},
        strip=True
    )

    return f"<p>{opening}</p>{clean_answer.strip()}<p>{closing}</p>"

# === Setup Flask App ===
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"],
)

@limiter.exempt
@app.route('/NCIRL_files/<path:filename>')
def serve_ncirlfiles(filename):
    return send_from_directory('NCIRL_files', filename)

# === API Endpoints ===

@app.route('/chat', methods=['POST'])
def chat():
    print("in here")
    data = request.json
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify({'reply': "No input received."}), 400

    matched_question = find_best_match(user_input, qa_dict, question_embeddings)

    SMALL_TALK_INPUTS = {
        "hi", "hey", "hiya", "hello", "helo", "helloo",
        "how are you", "how r u", "how are you doing", "how's it going", "how you doing",
        "thank you", "thanks", "thx", "ty", "thank u", "cheers", "cool", "ok thanks", "awesome thanks",
        "bye", "goodbye", "see you", "see ya", "talk later", "talk to you later",
        "see you later", "later", "cya", "catch you later", "peace",
        "i'm good thanks", "i'm fine thanks"
    }

    if matched_question:
        matched_answer = qa_dict[matched_question]
        output = matched_answer.strip()
        if matched_question.lower() in SMALL_TALK_INPUTS:
            reply = output
        else:
            reply = wrap_with_friendly_tone(output)
    else:
        matched_answer = "No match found."
        reply = random_fallback()

    return jsonify({'reply': reply})

@app.route('/articles/<slug>')
def serve_nci_article(slug):
    filename = f"{slug}.html"
    path = os.path.join(app.template_folder, filename)
    print(f"Trying to load file: {path}")
    if not os.path.exists(path):
        return "Page not found", 404
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content, mimetype="text/html")
    except Exception as e:
        print(f"[ERROR] Could not serve {filename}: {e}")
        return "Page not found", 404

@app.route('/articles')
def list_nci_pages():
    files = os.listdir("templates")
    pages = [f[:-5] for f in files if f.endswith(".html") and f != "NCIRL_cleaned.html"]
    links = [f'<li><a href="/articles/{page}">{page}</a></li>' for page in sorted(pages)]
    return f"<h2>Saved NCI Site Pages</h2><ul>{''.join(links)}</ul>"

@app.route('/debug-templates')
def debug_templates():
    files = os.listdir("templates")
    return "<br>".join(files)

@app.route('/')
def serve_homepage():
    return render_template('nci-home-fixed.html')

@app.route('/NCIRL_files/<path:filename>')
def static_from_saved_site(filename):
    return send_from_directory('NCIRL_files', filename)

# === Run Flask App ===
if __name__ == '__main__':
    print("Charlie is running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
