import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    prompt = f"""
You are Sahayak AI, an educational learning agent for students.

The student asked:
{question}

Do NOT simply give the final answer.

Your job is to:
1. Identify the main concept.
2. Identify a possible learning gap.
3. Explain the concept simply.
4. Give a helpful hint that makes the student think.
5. Give one small practice question.

Be encouraging and use simple student-friendly language.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return jsonify({
        "message": interaction.output_text,
        "concept": "Identified by Sahayak AI",
        "hint": "Try the practice question in the response."
    })


if __name__ == "__main__":
    app.run(debug=True)