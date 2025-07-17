# noteworthy/repo.py

import os
import re
import shutil
import subprocess
import git
from typing import Optional

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

def clone_after_tag(repo_url: str, from_tag: Optional[str] = None) -> str:
    tmp_path = "repo-tmp"
    clone_path = "repo"

    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)

    # Shallow clone to retrieve the tag date
    subprocess.run([
        "git", "clone", "--depth", "1", "--branch", from_tag, repo_url, tmp_path
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
        # Still fetch tags even if directory exists
        repo = git.Repo(clone_path)
        repo.git.fetch('--tags')
        return clone_path

    print(f"Cloning {repo_url} since tag '{from_tag}' (date: {tag_date}) into {clone_path}")

    # Clone with more depth to ensure we get all commits in the range
    # TODO: consider dynamically setting the depth based on the number of commits in the range or using sth like "git", "clone", f"--shallow-since={tag_date}", "--single-branch", repo_url, clone_path
    subprocess.run([
        "git", "clone", "--depth", "1000", "--single-branch", repo_url, clone_path
    ], check=True)

    if not os.path.exists(os.path.join(clone_path, ".git")):
        raise RuntimeError(f"Failed to clone repository from {repo_url} to {clone_path}")

    # After cloning, fetch tags so they're available for git operations
    repo = git.Repo(clone_path)
    repo.git.fetch('--tags')

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

def get_commits_with_file_counts(repo_path, since="HEAD~10"):
    repo = git.Repo(repo_path)

    # Handle revision ranges like "tag1..tag2"
    if ".." in since:
        from_tag, to_tag = since.split("..")
        # Use git log command directly for revision ranges
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "--pretty=format:%H", f"{from_tag}..{to_tag}"],
            capture_output=True, text=True, check=True
        )
        commit_hashes = result.stdout.strip().splitlines()
        commits = [repo.commit(hash.strip()) for hash in commit_hashes if hash.strip()]
    else:
        commits = list(repo.iter_commits(since))

    commit_data = []

    for c in commits:
        files_changed = list(c.stats.files.keys())
        commit_data.append({
            "message": c.message.strip().split("\n")[0],
            "author": c.author.name,
            "files_changed": len(files_changed),
            "file_names": files_changed,
            "hash": c.hexsha
        })

    return commit_data

def get_top_contributors(repo_path, rev_range=None, n=3):
    """
    Return the top n contributors in the given revision range (e.g., 'tag1..tag2').
    If rev_range is None, use all commits.
    """
    import git
    repo = git.Repo(repo_path)
    if rev_range:
        # Use git log to get commit hashes in the range
        if ".." in rev_range:
            parts = rev_range.split("..")
            if len(parts) == 2:
                from_tag, to_tag = parts
                hashes = repo.git.log(f"{from_tag}..{to_tag}", pretty='%H').splitlines()
            else:
                hashes = []
        else:
            hashes = repo.git.log(rev_range, pretty='%H').splitlines()
        commits = [repo.commit(h) for h in hashes if h.strip()]
    else:
        commits = list(repo.iter_commits())
    authors = [commit.author.name for commit in commits]
    from collections import Counter
    return Counter(authors).most_common(n)
