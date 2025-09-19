import os
from dotenv import load_dotenv

load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # personal access token
GITHUB_REPO = os.getenv("GITHUB_REPO")    # e.g. "username/reponame"
GITHUB_BRANCH = "main"
