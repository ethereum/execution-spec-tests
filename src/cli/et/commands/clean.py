"""
Clean CLI command removes generated files and directories.
"""

import glob
import os
import shutil

import click


@click.command()
@click.option(
    "--all", is_flag=True, help="Remove the virtual environment and .tox directory as well."
)
@click.option("--dry-run", is_flag=True, help="Simulate the cleanup without removing files.")
def clean(all: bool, dry_run: bool):
    """
    Remove all generated files and directories from the repository.
    If --all is specified, the virtual environment and .tox directory will also be removed.

    Note: The virtual environment and .tox directory are not removed by default.
    """
    # List of items to remove can contain files and directories.
    items_to_remove = [
        ".pytest_cache",
        ".mypy_cache",
        "fixtures",
        "build",
        "site",
        "cached_downloads",
        ".pyspelling_en.dict",
    ]

    # glob patterns to remove.
    patterns_to_remove = ["**/__pycache__"]

    for pattern in patterns_to_remove:
        matching_files = glob.glob(pattern, recursive=True)
        items_to_remove.extend(matching_files)

    if all:
        items_to_remove.extend([".tox", ".venv"])

    # Perform dry run or actual deletion
    for item in items_to_remove:
        if os.path.exists(item):
            if dry_run:
                click.echo(f"[🧐 Dry run] File would be deleted: {item}")
            else:
                try:
                    if os.path.isdir(item):
                        shutil.rmtree(item, ignore_errors=False)
                    else:
                        os.remove(item)
                except PermissionError:
                    click.echo(f"❌ Permission denied to remove {item}.")
                except Exception as e:
                    click.echo(f"❌ Failed to remove {item}: {e}")

                click.echo("🧹 Cleanup complete!")
