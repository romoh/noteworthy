# noteworthy/repo.py

import os
import re
import subprocess
import git

def validate_repo(repo_url):
    if not repo_url.startswith("https://github.com/"):
        raise ValueError("Invalid GitHub repository URL")

    result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", repo_url],
            capture_output=True,
            text=True,
            check=True
        )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to check GitHub repository: {result.stderr.strip()}")

    status_code = int(result.stdout.strip())
    if status_code != 200:
        raise ValueError(f"GitHub repo check failed. Status code: {status_code}")

    return True

import os
import shutil
import subprocess

def clone_after_tag(repo_url, tag_name, clone_path="repo"):
    tmp_path = "repo-tmp"
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)

    # Shallow clone to retrieve the tag date
    subprocess.run([
        "git", "clone", "--depth", "1", "--branch", tag_name, repo_url, tmp_path
    ], check=True)

    result = subprocess.run(
        ["git", "-C", tmp_path, "log", "-1", "--format=%cI"],
        capture_output=True, text=True, check=True
    )
    tag_date = result.stdout.strip()

    shutil.rmtree(tmp_path)

    # Now clone from the tag onwards only
    if os.path.exists(clone_path):
        print(f"Directory {clone_path} already exists. Skipping clone.")
        return clone_path

    print(f"Cloning {repo_url} since tag '{tag_name}' (date: {tag_date}) into {clone_path}")

    subprocess.run([
        "git", "clone", f"--shallow-since={tag_date}", "--single-branch", repo_url, clone_path
    ], check=True)

    if not os.path.exists(os.path.join(clone_path, ".git")):
        raise RuntimeError(f"Failed to clone repository from {repo_url} to {clone_path}")

    return clone_path

def get_latest_tag(repo_url):
    result = subprocess.run(
        ["git", "ls-remote", "--tags", repo_url],
        capture_output=True, text=True, check=True
    )
    tag_lines = [
        line for line in result.stdout.splitlines()
        if not line.endswith('^{}')  # avoid tag deref lines
    ]

    # Extract tag names
    tags = []
    for line in tag_lines:
        match = re.search(r"refs/tags/(.*)", line)
        if match:
            tags.append(match.group(1))

    # Sort tags semantically (basic)
    tags = sorted(tags, key=lambda s: [int(part) if part.isdigit() else part for part in re.split(r'[.-]', s)])

    return tags[-1] if tags else None

def get_commits(repo_path, since="HEAD~10"):
    repo = git.Repo(repo_path)
    commits = list(repo.iter_commits(since))
    return commits

def get_top_contributors(repo_path, n=3):
    repo = git.Repo(repo_path)
    authors = [commit.author.name for commit in repo.iter_commits()]
    from collections import Counter
    return Counter(authors).most_common(n)
