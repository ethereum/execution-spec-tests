"""
Utility functions for the EEST framework.
"""

from importlib.metadata import version

from git import InvalidGitRepositoryError, Repo


def get_framework_version() -> str:
    """
    Returns the current version of the EEST framework.
    """
    try:
        local_commit_hash = Repo(search_parent_directories=True).head.commit.hexsha[:7]
    except InvalidGitRepositoryError:  # required for some framework tests
        local_commit_hash = "unknown"
    return f"execution-spec-tests v{version('execution-spec-tests')}-{local_commit_hash}"
