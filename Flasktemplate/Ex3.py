from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "change-me"  # needed for session

# --- Minimal question bank ---
# Rule: first option is the correct answer; we'll shuffle before showing.
QUESTIONS = [
    {
        "prompt": "What is the airspeed of an unladen swallow (mph)?",
        "options": ["12", "8", "11", "15"],
    },
    {
        "prompt": "What is the capital of Texas?",
        "options": ["Austin", "San Antonio", "Dallas", "Waco"],
    },
    {
        "prompt": "The Last Supper was painted by which artist?",
        "options": ["Da Vinci", "Rembrandt", "Picasso", "Michelangelo"],
    },
    {
        "prompt": "Which classic novel opens with 'Call me Ishmael'?",
        "options": ["Moby Dick", "Wuthering Heights", "The Old Man and the Sea", "The Scarlet Letter"],
    },
    {
        "prompt": "Frank Lloyd Wright’s waterfall house is called…",
        "options": ["Fallingwater", "Mossyledge", "Taliesin", "Watering Heights"],
    },
]

def new_game():
    """Initialize a fresh game into the session."""
    # shuffle question order
    order = list(range(len(QUESTIONS)))
    random.shuffle(order)
    session["order"] = order
    session["q_idx"] = 0
    session["score"] = 0
    session["total"] = len(order)

@app.route("/")
def index():
    # Show landing page; if a game is mid-run offer resume
    in_progress = "order" in session and session.get("q_idx", 0) < session.get("total", 0)
    return render_template("index.html", in_progress=in_progress)

@app.route("/start")
def start():
    new_game()
    return redirect(url_for("question"))

@app.route("/question", methods=["GET"])
def question():
    # Guard: if game not started, go home
    if "order" not in session:
        return redirect(url_for("index"))

    q_idx = session.get("q_idx", 0)
    total = session.get("total", 0)

    # If finished, go to results
    if q_idx >= total:
        return redirect(url_for("results"))

    # Get current question according to shuffled order
    q_number = session["order"][q_idx]
    q = QUESTIONS[q_number]

    # Shuffle a copy of the options for display, but remember mapping so we can grade
    opts = q["options"][:]
    random.shuffle(opts)

    # Store the correct answer text for grading later
    session["correct_text"] = q["options"][0]
    session["shown_options"] = opts  # for re-render if they submit invalid choice

    return render_template(
        "question.html",
        prompt=q["prompt"],
        options=opts,
        q_idx=q_idx + 1,
        total=total
    )

@app.route("/answer", methods=["POST"])
def answer():
    # Basic defensive checks
    if "order" not in session or "correct_text" not in session:
        return redirect(url_for("index"))

    choice = request.form.get("choice", "").strip()
    shown = session.get("shown_options", [])
    if choice not in shown:
        # invalid submission or tampered; just re-show question
        return redirect(url_for("question"))

    correct = session.get("correct_text")
    if choice == correct:
        session["score"] = session.get("score", 0) + 1

    # advance to next question
    session["q_idx"] = session.get("q_idx", 0) + 1
    return redirect(url_for("question"))

@app.route("/results")
def results():
    if "order" not in session:
        return redirect(url_for("index"))
    score = session.get("score", 0)
    total = session.get("total", 0)
    return render_template("results.html", score=score, total=total)

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Run with:  python Ex3.py
    app.run(debug=True)