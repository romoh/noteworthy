# noteworthy/notes_generator.py

from typing import Optional, List

from noteworthy.repo import (
    clone_after_tag,
    validate_repo,
    get_commits, get_top_contributors, get_latest_tag, get_commits_with_file_counts
)
from noteworthy.notes_processor import process_release_notes

def generate_release_notes(
    repo_url: str,
    output_format: str = "markdown",
    output_file: Optional[str] = None,
    exclude_patterns: Optional[List[str]] = None,
    shoutout: bool = False,
    from_tag: Optional[str] = None,
    to_tag: Optional[str] = None,
) -> str:
    print(f"🔗 Validating and cloning: {repo_url}")
    validate_repo(repo_url)

    # First get tags so we can efficiently determine the date range to get commits and clone the repo
    if not from_tag:
        from_tag = get_latest_tag(repo_url)
        print(f"📌 Using latest tag: {from_tag}")
    if not to_tag:
        to_tag = "HEAD"

    # Now clone only after the from_tag
    print(f"🔍 Getting commits from {from_tag or '<beginning>'} to {to_tag}")
    repo_path = clone_after_tag(repo_url, from_tag)

    rev_range = f"{from_tag}..{to_tag}" if from_tag else to_tag
    commits = get_commits_with_file_counts(repo_path, rev_range)

    print(f"📝 Found {len(commits)} commits")

    commit_lines = []
    for c in commits:
        msg = c["message"].strip().split("\n")[0]
        if exclude_patterns and any(p in msg for p in exclude_patterns):
            continue
        commit_lines.append(f"- {msg} ({c['author']})")


    # Use AI to generate release notes from commit lines
    ai_notes = process_release_notes(commit_lines)

    # Contributor shoutouts
    shoutout_section = ""
    if shoutout:
        contributors = get_top_contributors(repo_path)
        names = [f"@{name}" for name, _ in contributors]
        shoutout_section = "\n\n🙌 **Thanks to our top contributors:** " + ", ".join(names)

    output = f"{ai_notes}{shoutout_section}\n"
    print(output)

    return output
