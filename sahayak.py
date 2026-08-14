import os
import json

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

PROGRESS_FILE = "progress.json"


# ---------------------------------------------
# PROGRESS FUNCTIONS
# ---------------------------------------------

def load_progress():

    if not os.path.exists(PROGRESS_FILE):
        return {
            "questions": 0,
            "attempts": 0,
            "correct": 0,
            "incorrect": 0,
            "concepts": {}
        }

    with open(PROGRESS_FILE, "r") as file:
        return json.load(file)


def save_progress(progress):

    with open(PROGRESS_FILE, "w") as file:
        json.dump(progress, file, indent=4)


# ---------------------------------------------
# GEMINI SETUP
# ---------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


# ---------------------------------------------
# HOME PAGE
# ---------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------
# STEP 1: ASK SAHAYAK
# ---------------------------------------------

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    progress = load_progress()

    progress["questions"] += 1

    save_progress(progress)

    prompt = f"""
You are Sahayak AI, an adaptive educational tutor.

A student has asked:

{question}

Analyze the student's question and respond in this format:

CONCEPT:
Identify the main academic concept involved.

LEARNING GAP:
Identify the likely concept or skill the student may be struggling with.

EXPLANATION:
Explain the concept simply, as if teaching a beginner.

HINT:
Give a hint that helps the student think instead of immediately giving the final answer.

TRY THIS:
Give the student one small question to attempt.

IMPORTANT:

- Do not immediately reveal the final answer.
- Use simple and encouraging language.
- NEVER use LaTeX or mathematical formatting.
- NEVER use \frac, $, $$, or LaTeX commands.
- Write fractions only in simple format such as 1/2, 2/5, 3/4.
- Write mathematical expressions in plain text.
- Example: write "2/5 + 1/5 = 3/5", NOT "\frac{2}{5} + \frac{1}{5} = \frac{3}{5}".
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    result = interaction.output_text

    # Extract practice question
    practice_question = ""

    if "TRY THIS:" in result:
        practice_question = result.split(
            "TRY THIS:", 1
        )[1].strip()

    return jsonify({
        "message": result,
        "practice_question": practice_question
    })


# ---------------------------------------------
# STEP 2: EVALUATE STUDENT ANSWER
# ---------------------------------------------

@app.route("/evaluate", methods=["POST"])
def evaluate():

    data = request.get_json()

    question = data.get("question", "").strip()
    student_answer = data.get("answer", "").strip()

    if not question:
        return jsonify({
            "error": "Question is missing."
        }), 400

    if not student_answer:
        return jsonify({
            "error": "Please enter your answer."
        }), 400

    progress = load_progress()
    progress["attempts"] += 1

    prompt = f"""
You are Sahayak AI, an adaptive educational tutor.

The original learning question was:

{question}

The student submitted this answer:

{student_answer}

Evaluate the student's answer and adapt the next learning activity.

Respond using exactly this structure:

RESULT:
Write either CORRECT or INCORRECT.

FEEDBACK:
Give short, encouraging feedback.

LEARNING GAP:
Identify the specific concept or skill the student needs to improve.
If correct, write "No major gap detected."

HINT:
If incorrect, give one helpful hint without directly giving the answer.
If correct, give a short encouraging message.

NEXT STEP:
If CORRECT:
Give a slightly harder practice question based on the same concept.

If INCORRECT:
Give a similar but slightly easier practice question focused on
the student's learning gap.

ADAPTIVE LEVEL:
Write one of:
EASIER
SAME
HARDER

IMPORTANT:

- Do not discourage the student.
- Do not immediately reveal the answer.
- Keep everything beginner-friendly.
- NEVER use LaTeX or mathematical formatting.
- NEVER use \frac, $, $$, or LaTeX commands.
- Write fractions only in simple format such as 1/2, 2/5, 3/4.
- Write mathematical expressions in plain text.
- Example: write "1/4 + 2/4 = 3/4", NOT "\frac{1}{4} + \frac{2}{4} = \frac{3}{4}".
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    result = interaction.output_text

    # -----------------------------------------
    # EXTRACT LEARNING GAP
    # -----------------------------------------

    learning_gap = "Unknown"

    if "LEARNING GAP:" in result:
        learning_gap = result.split(
            "LEARNING GAP:", 1
        )[1].split(
            "HINT:", 1
        )[0].strip()

    # -----------------------------------------
    # CREATE CONCEPT RECORD
    # -----------------------------------------

    if "concepts" not in progress:
        progress["concepts"] = {}

    if learning_gap not in progress["concepts"]:
        progress["concepts"][learning_gap] = {
            "attempts": 0,
            "correct": 0,
            "incorrect": 0
        }

    progress["concepts"][learning_gap]["attempts"] += 1

    # -----------------------------------------
    # RECORD RESULT
    # -----------------------------------------

    result_upper = result.upper()

    result_section = ""

    if "RESULT:" in result_upper:
        result_section = result_upper.split(
            "RESULT:", 1
        )[1].strip()

        result_section = result_section.split(
            "\n", 1
        )[0].strip()

    if result_section == "CORRECT":
        progress["correct"] += 1
        progress["concepts"][learning_gap]["correct"] += 1
    else:
        progress["incorrect"] += 1
        progress["concepts"][learning_gap]["incorrect"] += 1

    # -----------------------------------------
    # SAVE PROGRESS
    # -----------------------------------------

    save_progress(progress)

    return jsonify({
        "message": result
    })

# ---------------------------------------------
# STEP 3: GET PROGRESS
# ---------------------------------------------

@app.route("/progress", methods=["GET"])
def get_progress():

    progress = load_progress()

    return jsonify(progress)


# ---------------------------------------------
# START APPLICATION
# ---------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)