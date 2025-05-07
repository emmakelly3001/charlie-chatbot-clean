# This is the main file that loads Charlie (a Flask-based chatbot using a fine-tuned language model).

# === Import necessary libraries ===
from flask import Flask, request, jsonify, render_template, send_from_directory, Response, render_template_string
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

# === Configure logging ===
# Suppress unnecessary warnings from the transformers library
logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)

# === Load fine-tuned Charlie model ===
model_path = "./fine_tuned_model"  # Path to your fine-tuned model
device = "cuda" if torch.cuda.is_available() else "cpu"  # Use GPU if available
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path).to(device)

# Set padding token if not already set
tokenizer.pad_token = tokenizer.eos_token if tokenizer.pad_token is None else tokenizer.pad_token

# Create a text generation pipeline using the fine-tuned model
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if device == "cuda" else -1
)

# === Load dataset used for question-answer matching ===
dataset = datasets.load_dataset("json", data_files="final_dataset.jsonl", split="train")
qa_dict = {item["input"]: item["output"] for item in dataset}  # Map questions to answers

# === Load sentence transformer for semantic similarity checking ===
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
questions = list(qa_dict.keys())  # Extract all known questions
question_embeddings = semantic_model.encode(questions, convert_to_tensor=True)  # Precompute embeddings

# === Helper Functions ===

def find_best_match(user_question, qa_dict, question_embeddings, threshold_fuzzy=90, threshold_semantic=0.75):
    """
    Tries to match a user's input with known questions using:
    1. Exact match
    2. Fuzzy string similarity
    3. Semantic similarity
    """
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

    return None  # No match found

def random_fallback():
    """Return a random fallback response when no good match is found."""
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
    """
    Wraps a given answer in a friendly, conversational tone.
    Sanitizes HTML for safety.
    """
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

    # Clean the answer to prevent XSS
    clean_answer = bleach.clean(
        answer,
        tags=['b', 'i', 'u', 'em', 'strong', 'p', 'ul', 'li', 'br', 'a'],
        attributes={'a': ['href', 'target', 'title']},
        strip=True
    )

    return f"<p>{opening}</p>{clean_answer.strip()}<p>{closing}</p>"

# === Setup Flask App ===
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable Cross-Origin Resource Sharing

# Rate limiting (10 requests per minute per IP)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"],
)

# Route to serve static files from the NCIRL_files directory
@limiter.exempt
@app.route('/NCIRL_files/<path:filename>')
def serve_ncirlfiles(filename):
    return send_from_directory('NCIRL_files', filename)

# === API Endpoints ===

@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint. Accepts user input and returns chatbot reply.
    Includes small talk detection, fuzzy/semantic match, and fallback.
    """
    print("in here")
    data = request.json
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify({'reply': "No input received."}), 400

    matched_question = find_best_match(user_input, qa_dict, question_embeddings)

    # Define common small talk inputs
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
            reply = output  # No need to wrap small talk
        else:
            reply = wrap_with_friendly_tone(output)
    else:
        matched_answer = "No match found."
        reply = random_fallback()

    return jsonify({'reply': reply})

@app.route('/articles/<slug>')
def serve_nci_article(slug):
    """
    Dynamically serves NCI article pages by slug.
    """
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
    """
    Lists all saved HTML pages for browsing.
    """
    files = os.listdir("templates")
    pages = [f[:-5] for f in files if f.endswith(".html") and f != "NCIRL_cleaned.html"]
    links = [f'<li><a href="/articles/{page}">{page}</a></li>' for page in sorted(pages)]
    return f"<h2>Saved NCI Site Pages</h2><ul>{''.join(links)}</ul>"

@app.route('/debug-templates')
def debug_templates():
    """
    Debug route: lists all files in the templates folder.
    """
    files = os.listdir("templates")
    return "<br>".join(files)

@app.route('/')
def serve_homepage():
    """
    Serves the home page.
    """
    return render_template('nci-home-fixed.html')

@app.route('/NCIRL_files/<path:filename>')
def static_from_saved_site(filename):
    """
    Serves static site assets like CSS, JS, and images.
    """
    return send_from_directory('NCIRL_files', filename)

# === Run the Flask app locally ===
if __name__ == '__main__':
    print("Charlie is running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
