# 🤖 Sahayak AI

### Adaptive AI Learning Assistant for Students

Sahayak AI is an adaptive educational assistant designed to help students understand concepts, identify learning gaps, practice questions, and improve through personalized feedback.

Instead of simply giving students an answer, Sahayak follows a learning cycle:

**Ask → Understand → Identify Gap → Practice → Evaluate → Adapt → Master**

---

## 🎯 Problem

Many students struggle because traditional learning systems provide the same explanation and difficulty level to everyone.

Students may:

* Understand one part of a concept but struggle with another.
* Need simpler explanations.
* Need additional practice after making mistakes.
* Need progressively harder questions after mastering a concept.
* Not know which specific learning gap they need to improve.

Sahayak AI addresses this by adapting the learning experience based on the student's responses.

---

## 💡 Solution

Sahayak AI acts as an adaptive learning tutor.

When a student asks a question, Sahayak:

1. Identifies the main concept.
2. Detects a possible learning gap.
3. Explains the concept in simple language.
4. Provides a hint instead of immediately revealing the answer.
5. Generates a practice question.
6. Evaluates the student's response.
7. Adjusts the next question difficulty.
8. Tracks learning progress.
9. Detects mastery after consistent correct answers.

---

## ✨ Key Features

### 🌐 Multilingual Learning

Students can select:

* English
* Hindi
* Marathi

Sahayak responds in the selected language using beginner-friendly explanations.

### 🧠 Learning Gap Detection

Sahayak identifies the concept or skill where the student needs improvement.

### ✏️ Adaptive Practice

Practice difficulty changes according to performance:

* **EASIER** — after an incorrect response
* **SAME** — when more practice is needed
* **HARDER** — after a correct response
* **MASTERED** — after demonstrating consistent understanding

### 🏆 Mastery Detection

The practice cycle does not continue forever.

After three consecutive correct responses, Sahayak marks the concept as:

**CONCEPT MASTERED**

and ends the current practice session.

### 📊 Progress Tracking

The dashboard tracks:

* Questions asked
* Practice attempts
* Correct answers
* Accuracy
* Learning gaps
* Concept-level performance
* Mastery streak

---

## 🔄 Adaptive Learning Flow

```text
Student Question
       ↓
Concept Identification
       ↓
Learning Gap Detection
       ↓
Simple Explanation + Hint
       ↓
Practice Question
       ↓
Student Answer
       ↓
AI Evaluation
       ↓
   ┌───────────────┐
   │               │
Correct          Incorrect
   │               │
   ↓               ↓
Harder          Easier
Question        Question
   │               │
   └───────┬───────┘
           ↓
    Mastery Tracking
           ↓
  3 Correct Responses
           ↓
     🏆 Mastered
```

---

## 🛠️ Technology Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask

### AI

* Google Gemini API

### Data

* JSON-based progress tracking

### Environment

* Python virtual environment
* `.env` for API key management

---

## 📁 Project Structure

```text
SahayakAI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── index.html
│
├── sahayak.py
└── shayak.py
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd SahayakAI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

### Windows

```powershell
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create `.env`

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not upload the `.env` file to GitHub.

---

## ▶️ Run Sahayak AI

Start the Flask application:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 🔐 Security

The Gemini API key is stored in an environment variable:

```text
GEMINI_API_KEY
```

The `.env` file is excluded from Git using `.gitignore`.

The Python virtual environment and local progress data are also excluded from the repository.

---

## 🌍 Intended Impact

Sahayak AI is designed to make personalized learning more accessible to students who may not have access to individual tutoring.

By combining multilingual support, learning-gap detection, adaptive practice, and mastery tracking, Sahayak aims to provide a more personalized learning experience.

---

## 🚀 Future Improvements

Potential future improvements include:

* Voice-based interaction
* Speech-to-text learning
* Text-to-speech explanations
* More Indian regional languages
* Personalized learning paths
* Teacher dashboard
* Student performance analytics
* Subject-wise mastery tracking
* Offline/low-bandwidth support
* Image-based question solving

---

## 🏆 Hackathon Demo

The demo demonstrates the complete adaptive learning cycle:

**Ask → Learn → Practice → Evaluate → Adapt → Master**

Sahayak is designed to demonstrate that an AI educational agent can do more than answer questions — it can adapt to the learner.

---

## 👩‍💻 Project

**Sahayak AI**

Built as an AI-powered adaptive education solution for the AceSAT AI-Agent Hackathon.
