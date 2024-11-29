"""
Clean CLI command removes generated files and directories.
"""

import os
import shutil

import click


@click.command()
@click.option("--all", is_flag=True, help="Remove the virtual environment as well.")
def clean(all: bool):
    """
    Remove all generated files and directories from the repository.
    ```
    rm -rf .tox .cache .pytest_cache .mypy_cache fixtures build venv
    ```
    Note: The virtual environment is not removed by default.
    """
    # List of items to remove
    items_to_remove = [".tox", ".pytest_cache", ".mypy_cache", "fixtures", "build", "site"]
    if all:
        items_to_remove.append("venv")
    for item in items_to_remove:
        if os.path.exists(item):
            shutil.rmtree(item, ignore_errors=True)
    click.echo("🧹 Cleanup complete!")
