"""CLI entry point for the EIP version checker pytest-based command."""

import sys

import click
import pytest


@click.command(
    context_settings={
        "help_option_names": ["-h", "--help"],
    }
)
@click.option(
    "--github-token",
    help="GitHub API token required to avoid rate limiting when checking EIP versions",
    envvar="GITHUB_TOKEN",
    required=True,
)
def check_eip_versions(github_token: str) -> None:
    """Run pytest with the `spec_version_checker` plugin."""
    args = ["-c", "pytest-check-eip-versions.ini", "--github-token", github_token]

    result = pytest.main(args)
    sys.exit(result)
