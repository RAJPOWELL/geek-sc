import requests
from bs4 import BeautifulSoup
import json
from markdownify import markdownify as md


def find_problem_data(obj):
    """Recursively search dict/list for problem_name key."""
    if isinstance(obj, dict):
        if "problem_name" in obj and "problem_question" in obj:
            return obj
        for v in obj.values():
            result = find_problem_data(v)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_problem_data(item)
            if result:
                return result
    return None


def scrape_gfg(url: str, fetch_editorial: bool = True):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract JSON inside __NEXT_DATA__
    next_data = soup.find("script", {"id": "__NEXT_DATA__"})
    if not next_data:
        raise Exception("Could not find problem data on page")

    data = json.loads(next_data.string)

    # Recursively search for problem details
    problem_details = find_problem_data(data)
    if not problem_details:
        raise Exception("Problem details not found in JSON")

    # --- Title ---
    title = problem_details.get("problem_name", "No Title Found")

    # --- Problem statement ---
    problem_html = problem_details.get("problem_question", "")
    problem_md = md(problem_html, heading_style="ATX") if problem_html else "No Problem Found"

    # --- Editorial / Solution ---
    solution_md = "No Solution Found"
    articles = problem_details.get("article_list", [])

    if articles:
        editorial_url = articles[0]
        if fetch_editorial:
            try:
                solution_md = fetch_editorial_content(editorial_url)
            except Exception:
                solution_md = f"Editorial available at: {editorial_url}"
        else:
            solution_md = f"Editorial available at: {editorial_url}"

    return title, problem_md.strip(), solution_md.strip()


def fetch_editorial_content(editorial_url: str) -> str:
    """Fetch editorial article from GeeksforGeeks and return Markdown content."""
    resp = requests.get(editorial_url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    article = soup.find("article") or soup.find("div", {"class": "content"})
    if not article:
        return f"Editorial available at: {editorial_url}"

    editorial_md = md(str(article), heading_style="ATX")
    return editorial_md.strip()
