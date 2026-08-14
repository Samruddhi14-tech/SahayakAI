import os
import json

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

PROGRESS_FILE = "progress.json"


# =========================================================
# PROGRESS
# =========================================================

def default_progress():

    return {
        "questions": 0,
        "attempts": 0,
        "correct": 0,
        "incorrect": 0,
        "mastery_streak": 0,
        "concepts": {}
    }


def load_progress():

    if not os.path.exists(PROGRESS_FILE):
        return default_progress()

    try:

        with open(PROGRESS_FILE, "r") as file:
            progress = json.load(file)

    except Exception as error:

        print("Progress load error:", repr(error))

        return default_progress()

    defaults = default_progress()

    for key, value in defaults.items():

        if key not in progress:
            progress[key] = value

    return progress


def save_progress(progress):

    try:

        with open(PROGRESS_FILE, "w") as file:

            json.dump(
                progress,
                file,
                indent=4
            )

    except Exception as error:

        print("Progress save error:", repr(error))


# =========================================================
# GEMINI SETUP
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")


if not api_key:

    raise RuntimeError(
        "GEMINI_API_KEY not found in .env"
    )


client = genai.Client(
    api_key=api_key
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# ASK SAHAYAK
# =========================================================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json() or {}

    question = data.get(
        "question",
        ""
    ).strip()

    language = data.get(
        "language",
        "English"
    )


    # -----------------------------------------------------
    # VALIDATE
    # -----------------------------------------------------

    if not question:

        return jsonify({
            "error": "Please enter a question."
        }), 400


    # -----------------------------------------------------
    # UPDATE PROGRESS
    # -----------------------------------------------------

    progress = load_progress()

    progress["questions"] += 1

    # New question starts a fresh mastery sequence

    progress["mastery_streak"] = 0

    save_progress(progress)


    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are Sahayak AI, an adaptive educational tutor.

Student question:
{question}

Selected language:
{language}

Respond completely in {language}.

Your response must be simple and beginner-friendly.

Use EXACTLY this structure:

CONCEPT:
Identify the main academic concept.

LEARNING GAP:
Identify what the student may be struggling with.

EXPLANATION:
Explain the concept simply and clearly.

HINT:
Give a useful hint without directly giving the final answer.

TRY THIS:
Give ONE small practice question.

IMPORTANT:

- Do not immediately reveal the answer to TRY THIS.
- Be encouraging.
- Give only ONE practice question.
- Keep the practice question related to the same concept.
- If the question is mathematics, calculate carefully.
- NEVER use LaTeX.
- NEVER use \\frac.
- NEVER use $, $$, or mathematical formatting.
- Write fractions only in plain text.
- Example: 1/2 + 1/4 = 3/4.
- Do NOT display fractions vertically.
"""


    # -----------------------------------------------------
    # GEMINI
    # -----------------------------------------------------

    try:

        interaction = client.interactions.create(

            model="gemini-3.6-flash",

            input=prompt

        )

        result = interaction.output_text


    except Exception as error:

        print()
        print("======================================")
        print("GEMINI ASK ERROR")
        print("======================================")
        print(repr(error))
        print("======================================")
        print()

        return jsonify({

            "error":
            "Sahayak could not process the question. "
            "Check the terminal for the Gemini error."

        }), 500


    # -----------------------------------------------------
    # EXTRACT PRACTICE QUESTION
    # -----------------------------------------------------

    practice_question = ""


    if "TRY THIS:" in result:

        practice_question = result.split(
            "TRY THIS:",
            1
        )[1].strip()


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "message": result,

        "practice_question":
        practice_question

    })


# =========================================================
# EVALUATE ANSWER
# =========================================================

@app.route("/evaluate", methods=["POST"])
def evaluate():

    data = request.get_json() or {}

    question = data.get(
        "question",
        ""
    ).strip()

    student_answer = data.get(
        "answer",
        ""
    ).strip()

    language = data.get(
        "language",
        "English"
    )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not question:

        return jsonify({
            "error": "Question is missing."
        }), 400


    if not student_answer:

        return jsonify({
            "error": "Please enter your answer."
        }), 400


    # -----------------------------------------------------
    # LOAD PROGRESS
    # -----------------------------------------------------

    progress = load_progress()

    progress["attempts"] += 1


    # -----------------------------------------------------
    # EVALUATION PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are Sahayak AI, an adaptive educational tutor.

Practice question:
{question}

Student answer:
{student_answer}

Selected language:
{language}

Evaluate the student's answer carefully.

IMPORTANT FOR MATHEMATICS:

Treat mathematically equivalent answers as CORRECT.

Examples:

1/2 = 2/4
3/4 = 6/8
0.5 = 1/2
75% = 3/4

Do not mark an answer incorrect merely because the student
used a different but mathematically equivalent format.

Respond completely in {language}.

Use EXACTLY this structure:

RESULT:
Write ONLY:
CORRECT
or
INCORRECT

FEEDBACK:
Give short and encouraging feedback.

LEARNING GAP:
Identify the specific concept or skill that needs improvement.

If the answer is correct, write:
No major gap detected.

HINT:
If incorrect, give one useful hint without directly revealing
the final answer.

NEXT STEP:
If correct, give ONE slightly harder practice question.

If incorrect, give ONE slightly easier practice question
focused on the learning gap.

ADAPTIVE LEVEL:
Write exactly one:
EASIER
SAME
HARDER

IMPORTANT:

- Be encouraging.
- Do not discourage the student.
- Give only ONE next practice question.
- Do not immediately reveal the answer to the next question.
- NEVER use LaTeX.
- NEVER use \\frac.
- NEVER use $, $$, or mathematical formatting.
- Write fractions only in plain text.
- Example: 3/4.
"""


    # -----------------------------------------------------
    # GEMINI
    # -----------------------------------------------------

    try:

        interaction = client.interactions.create(

            model="gemini-3.6-flash",

            input=prompt

        )

        result = interaction.output_text


    except Exception as error:

        print()
        print("======================================")
        print("GEMINI EVALUATION ERROR")
        print("======================================")
        print(repr(error))
        print("======================================")
        print()

        return jsonify({

            "error":
            "Unable to evaluate the answer. "
            "Check the terminal for the Gemini error."

        }), 500


    # =====================================================
    # EXTRACT RESULT
    # =====================================================

    result_upper = result.upper()

    result_section = ""


    if "RESULT:" in result_upper:

        result_section = result_upper.split(
            "RESULT:",
            1
        )[1].strip()

        result_section = result_section.split(
            "\n",
            1
        )[0].strip()


    # =====================================================
    # EXTRACT LEARNING GAP
    # =====================================================

    learning_gap = "Unknown"


    if "LEARNING GAP:" in result:

        learning_gap = result.split(
            "LEARNING GAP:",
            1
        )[1]


        if "HINT:" in learning_gap:

            learning_gap = learning_gap.split(
                "HINT:",
                1
            )[0]


        learning_gap = learning_gap.strip()


    if not learning_gap:

        learning_gap = "Unknown"


    # =====================================================
    # CREATE CONCEPT RECORD
    # =====================================================

    if "concepts" not in progress:

        progress["concepts"] = {}


    if learning_gap not in progress["concepts"]:

        progress["concepts"][learning_gap] = {

            "attempts": 0,

            "correct": 0,

            "incorrect": 0

        }


    concept = progress["concepts"][learning_gap]

    concept["attempts"] += 1


    # =====================================================
    # CORRECT
    # =====================================================

    mastered = False


    if result_section == "CORRECT":

        progress["correct"] += 1

        concept["correct"] += 1

        progress["mastery_streak"] += 1


        if progress["mastery_streak"] >= 3:

            mastered = True

            adaptive_level = "MASTERED"

        else:

            adaptive_level = "HARDER"


    # =====================================================
    # INCORRECT
    # =====================================================

    else:

        progress["incorrect"] += 1

        concept["incorrect"] += 1

        progress["mastery_streak"] = 0

        adaptive_level = "EASIER"


    # =====================================================
    # SAVE
    # =====================================================

    save_progress(progress)


    # =====================================================
    # RETURN
    # =====================================================

    return jsonify({

        "message": result,

        "mastered": mastered,

        "adaptive_level": adaptive_level,

        "mastery_streak":
            progress["mastery_streak"]

    })


# =========================================================
# PROGRESS
# =========================================================

@app.route("/progress", methods=["GET"])
def get_progress():

    progress = load_progress()

    return jsonify(progress)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({

        "status": "Sahayak AI is running",

        "gemini": "configured",

        "model": "gemini-3.6-flash"

    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )