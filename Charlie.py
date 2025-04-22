from flask import Flask, request, jsonify, render_template, send_from_directory
import logging
import torch
import re
import random
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import datasets
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util
from flask_cors import CORS

# Suppress model logging
logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)

# Load Charlie model
model_path = r"C:\Users\emmak\OneDrive - National College of Ireland\4. Fourth Year\Computing Project\MyScraper\fine_tuned_model"
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

# Load dataset into a dictionary
dataset = datasets.load_dataset("json", data_files="formatted_data.jsonl", split="train")
qa_dict = {item["question"]: item["answer"] for item in dataset}

# Load semantic model
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
questions = list(qa_dict.keys())
question_embeddings = semantic_model.encode(questions, convert_to_tensor=True)

# Matching logic
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

# Fallback random answer
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

# Validate rephrased output
def validate_rephrased_output(original, rephrased, threshold=0.85):
    original = original.strip()
    rephrased = rephrased.strip()
    original_embedding = semantic_model.encode(original, convert_to_tensor=True)
    rephrased_embedding = semantic_model.encode(rephrased, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(original_embedding, rephrased_embedding).item()
    print(f"Rephrase similarity score: {similarity:.3f}")
    if similarity < threshold or len(rephrased) < 20:
        return original
    return rephrased

# Friendly wrapping
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

    return f"{opening}<br><br>{answer.strip()}<br><br>{closing}"

def truncate_to_last_full_sentence(text):
    # Match everything up to the last punctuation that ends a sentence
    sentences = re.findall(r'.*?[.!?]', text.strip(), re.DOTALL)
    if sentences:
        return ' '.join(sentences).strip()
    else:
        return text.strip()  # fallback if no punctuation

# Create Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify({'reply': "No input received."}), 400

    # ✅ Small talk responses
    small_talk_responses = {
        "hi": "Hey there! 😊",
        "hello": "Hello! How can I help you today?",
        "how are you": "I'm doing great, thanks! How can I help you today?",
        "how are you doing": "I'm doing well, thank you! Let me know if there's anything I can help with.",
        "thank you": "You're very welcome!",
        "thanks": "No problem at all!",
    }

    clean_input = user_input.lower().strip("?!.")

    if clean_input in small_talk_responses:
        return jsonify({'reply': small_talk_responses[clean_input]})

    # Proceed with normal matching
    matched_question = find_best_match(user_input, qa_dict, question_embeddings)

    if matched_question:
        raw_answer = qa_dict[matched_question]

        # Prompt LLaMA to rephrase
        prompt = (
            "Turn the following answer into a friendly, helpful explanation suitable for a student:\n\n"
            f"{raw_answer}\n\n"
            "Friendly version:"
        )
        response = generator(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)[0]['generated_text']

        # Extract just the generated part
        raw_output = response.split("Friendly version:")[-1].strip()
        rephrased = truncate_to_last_full_sentence(raw_output)

        # Validate rephrased output
        final_answer = validate_rephrased_output(raw_answer, rephrased)

        # Wrap in a friendly tone
        reply = wrap_with_friendly_tone(final_answer)

        # Debug logging
        print(f"\n[Original Answer]: {raw_answer}\n[Rephrased]: {rephrased}\n[Final Reply Sent]: {reply}\n")

    else:
        reply = random_fallback()

    return jsonify({'reply': reply})


@app.route('/')
def serve_homepage():
    return render_template('NCI.html')

@app.route('/National College of Ireland_files/<path:filename>')
def static_from_saved_site(filename):
    return send_from_directory('National College of Ireland_files', filename)

if __name__ == '__main__':
    print("Charlie is running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
