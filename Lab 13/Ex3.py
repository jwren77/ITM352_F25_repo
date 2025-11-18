# Ex3.py
from flask import Flask, render_template
import requests
import time

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True  # auto-reload template changes

API_URL = "https://meme-api.com/gimme/wholesomememes"

def get_meme():
    """Fetch one wholesome meme and normalize the fields for the template."""
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        # The API returns keys like: url, subreddit, title, postLink
        return {
            "title": data.get("title", "Untitled"),
            "image_url": data.get("url"),
            "subreddit": data.get("subreddit", "unknown"),
            "post_link": data.get("postLink"),
        }
    except Exception as e:
        # Return a safe fallback; template will show the error.
        return {
            "title": "Could not load meme 😕",
            "image_url": None,
            "subreddit": None,
            "post_link": None,
            "error": str(e),
        }

@app.route("/")
def home():
    meme = get_meme()
    # ts added to help bust any image caching on refresh
    return render_template("index.html", meme=meme, ts=int(time.time()))

if __name__ == "__main__":
    # debug=True gives auto-reload when you change code in VS Code
    app.run(debug=True)