import re
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from utils.scraper import scrape_gfg
from config import GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH

app = Flask(__name__)
app.secret_key = "supersecretkey"  # replace with env var if desired

GITHUB_API = "https://api.github.com"

def _safe_filename(title):
    # keep basic alphanumerics, underscores, dashes; limit length
    name = re.sub(r"[^A-Za-z0-9_\-]+", "_", title).strip("_")
    if not name:
        name = "no_title"
    return f"gfg_{name[:80]}.md"

def save_to_github(filename, content):
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    # Check if file exists to include sha (update) vs create
    get_r = requests.get(url, headers=headers)
    if get_r.status_code == 200:
        sha = get_r.json().get("sha")
        data = {
            "message": f"Update {filename}",
            "content": encoded_content,
            "branch": GITHUB_BRANCH,
            "sha": sha
        }
    else:
        data = {
            "message": f"Add {filename}",
            "content": encoded_content,
            "branch": GITHUB_BRANCH
        }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in (200, 201):
        # raise useful info for debugging
        raise Exception(f"GitHub API error: {response.status_code} {response.text}")
    return response.json()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        gfg_url = request.form.get("gfg_url")
        try:
            # set debug=True temporarily if you want to print HTML to console
            title, problem_md, solution_md = scrape_gfg(gfg_url)

            filename = _safe_filename(title)
            content = f"# {title}\n\n## Problem\n\n{problem_md}\n\n## Solution\n\n{solution_md}\n"

            save_to_github(filename, content)
            flash("File saved to GitHub successfully!", "success")
        except Exception as e:
            # show the full error message so you can debug
            flash(f"Error: {str(e)}", "error")
        return redirect(url_for("index"))
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
