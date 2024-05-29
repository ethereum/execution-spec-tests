"""
Utility module with helper functions for versioning.
"""

import re

from git import Repo  # type: ignore


def get_current_commit_hash_or_tag(repo_path="."):
    """
    Get the latest commit hash or tag from the clone where doc is being built.
    """
    repo = Repo(repo_path)
    try:
        # Get the tag that points to the current commit
        current_tag = next((tag for tag in repo.tags if tag.commit == repo.head.commit))
        return current_tag.name
    except StopIteration:
        # If there are no tags that point to the current commit, return the commit hash
        return repo.head.commit.hexsha


def generate_github_url(file_path, branch_or_commit_or_tag="main", line_number=""):
    """
    Generate a permalink to a source file in Github.
    """
    base_url = "https://github.com"
    username = "ethereum"
    repository = "execution-spec-tests"
    if line_number:
        line_number = f"#L{line_number}"
    if re.match(
        r"^v[0-9]{1,2}\.[0-9]{1,3}\.[0-9]{1,3}(a[0-9]+|b[0-9]+|rc[0-9]+)?$",
        branch_or_commit_or_tag,
    ):
        return (
            f"{base_url}/{username}/{repository}/tree/"
            f"{branch_or_commit_or_tag}/{file_path}{line_number}"
        )
    else:
        return (
            f"{base_url}/{username}/{repository}/blob/"
            f"{branch_or_commit_or_tag}/{file_path}{line_number}"
        )
