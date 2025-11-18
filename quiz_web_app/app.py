import json
import random
import time
import os
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify
)

app = Flask(__name__)
app.secret_key = "change_this_secret"  # used for sessions (stored in cookie)

QUESTIONS_FILE = "questions.json"
SCORES_FILE = "scores.json"

QUIZ_TIME_LIMIT_SECONDS = 60  # total time for quiz (simple mode)
HINT_PENALTY = 0.5            # points deducted if hint used on a correct answer
MAX_HINTS_PER_QUIZ = 1        # only allow one hint per quiz


# ---------- Helper functions ----------

def load_questions():
    """Load all questions from JSON file."""
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_questions(difficulty=None, category=None):
    """Filter questions by difficulty and category. If none match, return all."""
    questions = load_questions()
    filtered = []
    for q in questions:
        if difficulty and q.get("difficulty") != difficulty:
            continue
        if category and q.get("category") != category:
            continue
        filtered.append(q)
    return filtered if filtered else questions


def load_scores():
    """Load all scores from scores.json."""
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_scores(scores):
    """Save all scores back to scores.json."""
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)


def setup_quiz(username, difficulty, category):
    """Initialize quiz data in the session."""
    questions = filter_questions(difficulty, category)

    # Randomize question order and answer options
    random.shuffle(questions)
    for q in questions:
        random.shuffle(q["options"])

    session["username"] = username
    session["difficulty"] = difficulty
    session["category"] = category
    session["questions"] = questions
    session["current_index"] = 0
    session["score"] = 0.0
    session["start_time"] = time.time()
    session["hints_used"] = 0
    session["answers_log"] = []  # store for review screen


def get_time_left():
    """Return remaining time for the quiz (can be negative if time is up)."""
    start_time = session.get("start_time")
    if start_time is None:
        return 0
    elapsed = time.time() - start_time
    return QUIZ_TIME_LIMIT_SECONDS - elapsed


# ---------- Routes ----------

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Home page.
    - If returning user (session has username), greet them and show history.
    - Let user enter name, difficulty, and category to start quiz.
    """
    scores = load_scores()
    username = session.get("username")

    user_history = []
    if username:
        for s in scores:
            if s.get("name") == username:
                user_history.append(s)

    # Simple list of difficulty and category options (could be dynamic)
    difficulties = ["Any", "Easy", "Medium", "Hard"]
    categories = ["Any", "Movies", "Geography", "Art", "Literature", "Architecture"]

    if request.method == "POST":
        name = request.form.get("username", "").strip()
        difficulty = request.form.get("difficulty")
        category = request.form.get("category")

        if not name:
            name = "Guest"

        # Store in session (Flask sessions are stored in a secure cookie)
        session["username"] = name

        # Convert "Any" to None so filter_questions() does not filter on it
        if difficulty == "Any":
            difficulty = None
        if category == "Any":
            category = None

        setup_quiz(name, difficulty, category)
        return redirect(url_for("quiz"))

    return render_template(
        "index.html",
        username=username,
        user_history=user_history,
        difficulties=difficulties,
        categories=categories
    )


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    """
    Main quiz page.
    - Shows one question at a time.
    - Tracks score and progress.
    - Supports a simple hint system.
    - Enforces a total quiz time limit (front-end and back-end).
    """
    questions = session.get("questions", [])
    current_index = session.get("current_index", 0)
    score = session.get("score", 0.0)
    hints_used = session.get("hints_used", 0)
    answers_log = session.get("answers_log", [])

    if not questions:
        return redirect(url_for("index"))

    time_left = get_time_left()
    if time_left <= 0:
        # Time is up for the whole quiz
        return redirect(url_for("result", timed_out=1))

    feedback = None
    is_correct = None

    if request.method == "POST":
        # Check again after form submit
        time_left = get_time_left()
        if time_left <= 0:
            return redirect(url_for("result", timed_out=1))

        selected = request.form.get("answer")
        hint_used_for_this = request.form.get("hint_used") == "1"
        current_question = questions[current_index]
        correct_answer = current_question["correct"]

        if hint_used_for_this and hints_used < MAX_HINTS_PER_QUIZ:
            hints_used += 1
            session["hints_used"] = hints_used

        if selected:
            if selected == correct_answer:
                # Base point is 1, but if hint was used, apply penalty
                gained = 1.0
                if hint_used_for_this:
                    gained -= HINT_PENALTY
                    if gained < 0:
                        gained = 0
                score += gained
                feedback = "Correct!"
                is_correct = True
            else:
                feedback = f"Wrong. Correct answer: {correct_answer}"
                is_correct = False

            # Save answer for review screen
            answers_log.append({
                "question": current_question["question"],
                "selected": selected,
                "correct": correct_answer,
                "hint": current_question.get("hint"),
                "explanation": current_question.get("explanation"),
                "used_hint": hint_used_for_this and hints_used <= MAX_HINTS_PER_QUIZ,
                "is_correct": is_correct
            })

            # Update session
            session["score"] = score
            session["answers_log"] = answers_log

            # Move to next question
            current_index += 1
            session["current_index"] = current_index

            # If quiz is done, go to result
            if current_index >= len(questions):
                return redirect(url_for("result", timed_out=0))

    # After processing POST (or on GET), show current question
    current_index = session.get("current_index", 0)
    if current_index >= len(questions):
        return redirect(url_for("result", timed_out=0))

    current_question = questions[current_index]
    total_questions = len(questions)
    progress = int((current_index / total_questions) * 100)

    # Pass feedback from last answer down to template
    return render_template(
        "quiz.html",
        question=current_question,
        index=current_index + 1,
        total=total_questions,
        score=score,
        progress=progress,
        time_left=int(time_left),
        hints_left=max(0, MAX_HINTS_PER_QUIZ - hints_used),
        feedback=feedback,
        is_correct=is_correct
    )


@app.route("/result")
def result():
    """
    Result page.
    - Shows final score and summary.
    - Shows missed questions with explanations.
    - Shows simple leaderboard (top 10).
    - Shows user score history.
    """
    questions = session.get("questions", [])
    total_questions = len(questions)
    score = session.get("score", 0.0)
    username = session.get("username", "Guest")
    difficulty = session.get("difficulty")
    category = session.get("category")
    hints_used = session.get("hints_used", 0)
    answers_log = session.get("answers_log", [])

    timed_out = request.args.get("timed_out", "0") == "1"

    # Save attempt to scores.json
    scores = load_scores()
    attempt = {
        "name": username,
        "score": score,
        "total": total_questions,
        "difficulty": difficulty or "Any",
        "category": category or "Any",
        "hints_used": hints_used,
        "timed_out": timed_out,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }
    scores.append(attempt)
    save_scores(scores)

    # Build leaderboard (sort by score, then timestamp)
    leaderboard = sorted(
        scores,
        key=lambda s: (s.get("score", 0), s.get("timestamp", "")),
        reverse=True
    )[:10]

    # User's own history
    user_history = [s for s in scores if s.get("name") == username]

    # Count correct/incorrect
    num_correct = sum(1 for a in answers_log if a.get("is_correct"))
    num_incorrect = len(answers_log) - num_correct

    return render_template(
        "result.html",
        username=username,
        score=score,
        total=total_questions,
        timed_out=timed_out,
        difficulty=difficulty or "Any",
        category=category or "Any",
        hints_used=hints_used,
        answers_log=answers_log,
        num_correct=num_correct,
        num_incorrect=num_incorrect,
        leaderboard=leaderboard,
        user_history=user_history
    )


# ---------- Simple JSON API endpoints (REST-ish) ----------

@app.route("/api/questions")
def api_questions():
    """Return the current quiz questions as JSON."""
    questions = session.get("questions") or []
    return jsonify(questions)


@app.route("/api/leaderboard")
def api_leaderboard():
    """Return top 10 scores as JSON."""
    scores = load_scores()
    leaderboard = sorted(
        scores,
        key=lambda s: (s.get("score", 0), s.get("timestamp", "")),
        reverse=True
    )[:10]
    return jsonify(leaderboard)


if __name__ == "__main__":
    app.run(debug=True)