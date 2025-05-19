"""Command to display EEST and system information."""

import platform
import subprocess
import sys

import click

from config.app import AppConfig


def run_command(command: list[str]) -> str:
    """Run a CLI command and return its output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def get_git_commit() -> str:
    """Get the current git commit message and hash."""
    git_hash = run_command(["git", "rev-parse", "--short=6", "HEAD"])
    message = run_command(["git", "log", "-1", "--pretty=%s"])
    return f"{message} ({git_hash})" if git_hash != "unknown" else "unknown"


def get_uv_version() -> str:
    """Get the installed uv package manager version."""
    return run_command(["uv", "--version"])


@click.command(name="info")
def info():
    """Display EEST and system information."""
    # Format headers
    title = click.style("EEST", fg="green", bold=True)
    version = click.style(f"{AppConfig().version}", fg="blue", bold=True)

    info_text = f"""
    {title} {version}
{"─" * 50}

    Git commit: {click.style(get_git_commit(), fg="yellow")}
    Python: {click.style(platform.python_version(), fg="blue")}
    uv: {click.style(get_uv_version(), fg="magenta")}
    OS: {click.style(f"{platform.system()} {platform.release()}", fg="cyan")}
    Platform: {click.style(platform.machine(), fg="cyan")}
    Python Path: {click.style(sys.executable, dim=True)}
    """

    click.echo(info_text)
