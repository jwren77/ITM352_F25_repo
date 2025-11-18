import json
import random
import time
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "change_this_to_something_secret"  # needed for sessions

QUIZ_TIME_LIMIT_SECONDS = 60  # total time for the whole quiz


def load_questions():
    """Load questions from JSON file."""
    with open("questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    return questions


def setup_quiz():
    """Initialize quiz state in the session."""
    questions = load_questions()
    # shuffle questions
    random.shuffle(questions)
    # shuffle options inside each question
    for q in questions:
        random.shuffle(q["options"])

    session["questions"] = questions
    session["current_index"] = 0
    session["score"] = 0
    session["start_time"] = time.time()  # used for timer


def get_time_left():
    """Return remaining time in seconds (can be negative if time is up)."""
    start_time = session.get("start_time")
    if start_time is None:
        return 0
    elapsed = time.time() - start_time
    return QUIZ_TIME_LIMIT_SECONDS - elapsed


@app.route("/")
def index():
    return render_template("index.html", time_limit=QUIZ_TIME_LIMIT_SECONDS)


@app.route("/start")
def start():
    setup_quiz()
    return redirect(url_for("quiz"))


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    # Check timer first
    time_left = get_time_left()
    if time_left <= 0:
        # time's up – send to result
        return redirect(url_for("result", timed_out=1))

    questions = session.get("questions", [])
    current_index = session.get("current_index", 0)
    score = session.get("score", 0)
    total_questions = len(questions)

    if total_questions == 0:
        # no questions loaded
        return "No questions available."

    # Handle previous answer
    feedback = None
    if request.method == "POST":
        selected = request.form.get("answer")
        if selected is not None:
            current_question = questions[current_index]
            correct_answer = current_question["correct"]
            if selected == correct_answer:
                score += 1
                feedback = "Correct!"
            else:
                feedback = f"Wrong. Correct answer is: {correct_answer}"
            session["score"] = score

            # Move to next question
            current_index += 1
            session["current_index"] = current_index

            # If that was the last question, go to result page
            if current_index >= total_questions:
                return redirect(url_for("result", timed_out=0))

    # If we moved to the last question after POST, reload from session
    current_index = session.get("current_index", 0)
    if current_index >= total_questions:
        return redirect(url_for("result", timed_out=0))

    current_question = questions[current_index]
    progress = int((current_index / total_questions) * 100)

    return render_template(
        "quiz.html",
        question=current_question,
        index=current_index + 1,
        total=total_questions,
        score=score,
        progress=progress,
        time_left=int(time_left),
        time_limit=QUIZ_TIME_LIMIT_SECONDS,
        feedback=feedback,
    )


@app.route("/result")
def result():
    questions = session.get("questions", [])
    total_questions = len(questions)
    score = session.get("score", 0)
    timed_out = request.args.get("timed_out", "0") == "1"

    return render_template(
        "result.html",
        score=score,
        total=total_questions,
        timed_out=timed_out
    )


if __name__ == "__main__":
    app.run(debug=True)