"""
Filter test fixtures by fork range.

This tool filters test fixtures from an input directory to an output directory
based on fork inclusion criteria, similar to the fill command's --until functionality.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Type

import click
from rich.progress import track

from ethereum_test_fixtures.file import Fixtures
from ethereum_test_fixtures.pre_alloc_groups import PreAllocGroup
from ethereum_test_forks import get_deployed_forks, get_fork_by_name
from ethereum_test_forks.base_fork import BaseFork


def get_valid_fork_range(
    single_fork: str | None = None,
    forks_from: str | None = None,
    forks_until: str | None = None,
) -> tuple[Type[BaseFork] | None, Type[BaseFork] | None, Type[BaseFork] | None]:
    """
    Get the fork range for filtering. Returns (single_fork, from_fork, until_fork).

    This function validates the fork names but doesn't try to enumerate all valid forks,
    since transition forks are dynamically created and not in the fork registry.
    """
    if single_fork:
        fork = get_fork_by_name(single_fork)
        if fork is None:
            raise ValueError(f"Fork '{single_fork}' not found")
        return fork, None, None

    # Validate from fork if specified
    from_fork = None
    if forks_from:
        from_fork = get_fork_by_name(forks_from)
        if from_fork is None:
            raise ValueError(f"Fork '{forks_from}' not found")

    # Validate until fork if specified
    until_fork = None
    if forks_until:
        until_fork = get_fork_by_name(forks_until)
        if until_fork is None:
            raise ValueError(f"Fork '{forks_until}' not found")

    return None, from_fork, until_fork


def should_include_fixture_fork(
    fixture_fork: Type[BaseFork],
    single_fork: Type[BaseFork] | None,
    from_fork: Type[BaseFork] | None,
    until_fork: Type[BaseFork] | None,
) -> bool:
    """
    Determine if a fixture's fork should be included based on the filtering criteria.

    This uses fork comparison operators to handle both regular and transition forks.
    """
    if single_fork:
        return fixture_fork == single_fork

    # Default range is all deployed forks if no range specified
    if not from_fork and not until_fork:
        deployed_forks = get_deployed_forks()
        return deployed_forks[0] <= fixture_fork <= deployed_forks[-1]

    # Handle range filtering
    from_ok = True
    until_ok = True

    if from_fork:
        from_ok = fixture_fork >= from_fork

    if until_fork:
        until_ok = fixture_fork <= until_fork

    return from_ok and until_ok


def filter_regular_fixture_file(
    input_path: Path,
    output_path: Path,
    single_fork: Type[BaseFork] | None,
    from_fork: Type[BaseFork] | None,
    until_fork: Type[BaseFork] | None,
) -> bool:
    """
    Filter a regular fixture file (state test or blockchain test).

    Returns True if the output file has any content, False otherwise.

    Raises:
        Exception: If fixture file cannot be loaded or validated

    """
    try:
        fixtures = Fixtures.model_validate_json(input_path.read_text())
    except Exception as e:
        # Print detailed error first (Pydantic validation errors can be very long)
        click.echo(f"❌ FATAL: Failed to load fixture file {input_path}", err=True)
        error_str = str(e)

        # Truncate extremely long error messages
        if len(error_str) > 2000:
            lines = error_str.split("\n")
            if len(lines) > 20:
                truncated_lines = (
                    lines[:10] + ["   ... (truncated, showing first 10 errors) ..."] + lines[-5:]
                )
                error_str = "\n".join(truncated_lines)

        click.echo(f"   Error: {error_str}", err=True)

        # Add summary at the end to avoid scrolling
        click.echo("\n" + "=" * 60, err=True)
        click.echo("❌ FILTER OPERATION FAILED", err=True)
        click.echo("=" * 60, err=True)
        click.echo(f"📁 File: {input_path}", err=True)
        click.echo("🔍 Possible causes:", err=True)
        click.echo("   • Corrupted or invalid fixture data", err=True)
        click.echo("   • Pydantic models incompatible with fixtures format", err=True)
        click.echo("   • Missing required fields in fixture", err=True)
        click.echo("   • Fixture format version mismatch", err=True)
        click.echo(
            "\n💡 Suggestion: Check if this fixture was generated with a different version",
            err=True,
        )
        click.echo("   of the execution-spec-tests framework.", err=True)
        click.echo("=" * 60, err=True)
        raise

    filtered_fixtures = Fixtures(root={})

    for test_case_id, fixture in fixtures.items():
        fixture_fork = fixture.get_fork()
        if fixture_fork and should_include_fixture_fork(
            fixture_fork, single_fork, from_fork, until_fork
        ):
            filtered_fixtures[test_case_id] = fixture

    # Only write file if it has content
    if len(filtered_fixtures) > 0:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        filtered_fixtures.collect_into_file(output_path)
        return True

    return False


def filter_pre_alloc_file(
    input_path: Path,
    output_path: Path,
    single_fork: Type[BaseFork] | None,
    from_fork: Type[BaseFork] | None,
    until_fork: Type[BaseFork] | None,
) -> bool:
    """
    Filter a pre-alloc file based on its network field using Pydantic models.

    Returns True if the file should be included, False otherwise.

    Raises:
        Exception: If pre-alloc file cannot be loaded or validated

    """
    try:
        pre_alloc_group = PreAllocGroup.model_validate_json(input_path.read_text())
    except Exception as e:
        # Print detailed error first (Pydantic validation errors can be very long)
        click.echo(f"❌ FATAL: Failed to load pre-alloc file {input_path}", err=True)
        error_str = str(e)

        # Truncate extremely long error messages
        if len(error_str) > 2000:
            lines = error_str.split("\n")
            if len(lines) > 20:
                truncated_lines = (
                    lines[:10] + ["   ... (truncated, showing first 10 errors) ..."] + lines[-5:]
                )
                error_str = "\n".join(truncated_lines)

        click.echo(f"   Error: {error_str}", err=True)

        # Add summary at the end to avoid scrolling
        click.echo("\n" + "=" * 60, err=True)
        click.echo("❌ FILTER OPERATION FAILED", err=True)
        click.echo("=" * 60, err=True)
        click.echo(f"📁 File: {input_path}", err=True)
        click.echo("🔍 Possible causes:", err=True)
        click.echo("   • Corrupted or invalid pre-alloc data", err=True)
        click.echo("   • Pydantic models incompatible with pre-alloc format", err=True)
        click.echo("   • Missing required fields in pre-alloc file", err=True)
        click.echo("   • Pre-alloc format version mismatch", err=True)
        click.echo(
            "\n💡 Suggestion: Check if this pre-alloc file was generated with a different",
            err=True,
        )
        click.echo("   version of the execution-spec-tests framework.", err=True)
        click.echo("=" * 60, err=True)
        raise

    fixture_fork = pre_alloc_group.fork
    if should_include_fixture_fork(fixture_fork, single_fork, from_fork, until_fork):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pre_alloc_group.to_file(output_path)
        return True

    return False


def copy_non_fixture_files(input_dir: Path, output_dir: Path) -> None:
    """Copy non-fixture files like the entire .meta directory to the output directory."""
    meta_dir = input_dir / ".meta"
    if meta_dir.exists():
        output_meta_dir = output_dir / ".meta"
        # Remove existing .meta directory if it exists, then copy the entire directory
        if output_meta_dir.exists():
            shutil.rmtree(output_meta_dir)
        shutil.copytree(meta_dir, output_meta_dir)


def regenerate_index(output_dir: Path) -> None:
    """Regenerate the index.json file using the genindex command."""
    try:
        subprocess.run(
            ["uv", "run", "genindex", "--input", str(output_dir), "--quiet", "--force"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Warning: Failed to regenerate index: {e}", err=True)


def clean_output_directory(output_dir: Path, quiet_mode: bool = False) -> None:
    """Remove all contents from the output directory to ensure clean state."""
    if output_dir.exists():
        if not quiet_mode:
            click.echo(f"Cleaning output directory: {output_dir}")
        # Remove all contents but keep the directory itself
        for item in output_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


def cleanup_empty_directories(output_dir: Path) -> None:
    """Remove empty directories from the output directory tree."""
    import os

    for root, dirs, files in reversed(list(os.walk(output_dir))):
        root_path = Path(root)
        if not dirs and not files and root_path != output_dir:
            try:
                root_path.rmdir()
            except OSError:
                pass  # Directory not empty or other error


def process_directory(
    input_dir: Path,
    output_dir: Path,
    single_fork: Type[BaseFork] | None,
    from_fork: Type[BaseFork] | None,
    until_fork: Type[BaseFork] | None,
    quiet_mode: bool = False,
) -> None:
    """Process all fixture files in a directory recursively."""
    # Get all JSON files to process
    json_files = list(input_dir.rglob("*.json"))

    # Filter out index.json and other meta files
    fixture_files = [f for f in json_files if f.name != "index.json" and ".meta" not in f.parts]

    if not quiet_mode:
        click.echo(f"Processing {len(fixture_files)} fixture files...")

    files_written = 0

    # Use track only if not in quiet mode, otherwise use plain iteration
    file_iterator = (
        fixture_files if quiet_mode else track(fixture_files, description="Filtering fixtures...")
    )
    for input_file in file_iterator:
        relative_path = input_file.relative_to(input_dir)
        output_file = output_dir / relative_path

        if "pre_alloc" in input_file.parts:
            if filter_pre_alloc_file(input_file, output_file, single_fork, from_fork, until_fork):
                files_written += 1
        else:
            if filter_regular_fixture_file(
                input_file, output_file, single_fork, from_fork, until_fork
            ):
                files_written += 1

    if not quiet_mode:
        click.echo(f"Wrote {files_written} fixture files to {output_dir}")


@click.command()
@click.option(
    "--input",
    "-i",
    "input_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path),
    required=True,
    help="The input fixtures directory",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    required=True,
    help="The output fixtures directory",
)
@click.option("--fork", "single_fork", help="Only include fixtures for the specified fork.")
@click.option(
    "--from", "forks_from", help="Include fixtures from and including the specified fork."
)
@click.option(
    "--until", "forks_until", help="Include fixtures until and including the specified fork."
)
@click.option(
    "--quiet",
    "-q",
    "quiet_mode",
    is_flag=True,
    default=False,
    expose_value=True,
    help="Don't show progress output while processing fixture files.",
)
@click.option(
    "--clean",
    "clean_output",
    is_flag=True,
    default=False,
    expose_value=True,
    help="Clean the output directory before filtering (removes all existing content).",
)
def filter_fixtures(
    input_dir: Path,
    output_dir: Path,
    single_fork: str | None,
    forks_from: str | None,
    forks_until: str | None,
    quiet_mode: bool,
    clean_output: bool,
):
    """
    Filter test fixtures by fork range.

    This command filters fixture files from the input directory to the output directory
    based on fork inclusion criteria. It handles both regular fixture files and
    pre-allocation files, and properly excludes transition forks when their target
    fork is not included.

    Examples:
        # Filter up to Prague (excludes Osaka development fork)
        filter_fixtures -i fixtures_develop/ -o fixtures_stable/ --until Prague

        # Filter specific fork range, cleaning output directory first
        filter_fixtures -i fixtures/ -o filtered/ --from Cancun --until Prague --clean

        # Filter single fork only
        filter_fixtures -i fixtures/ -o single/ --fork Prague

    """
    try:
        single_fork_obj, from_fork, until_fork = get_valid_fork_range(
            single_fork, forks_from, forks_until
        )

        if not quiet_mode:
            if single_fork_obj:
                click.echo(f"Including fork: {single_fork_obj.__name__}")
            else:
                range_desc = []
                if from_fork:
                    range_desc.append(f"from {from_fork.__name__}")
                if until_fork:
                    range_desc.append(f"until {until_fork.__name__}")
                if range_desc:
                    click.echo(f"Including forks {' '.join(range_desc)}")
                else:
                    click.echo("Including all deployed forks")

        output_dir.mkdir(parents=True, exist_ok=True)
        if clean_output:
            clean_output_directory(output_dir, quiet_mode)
        else:
            if any(output_dir.iterdir()):
                raise click.ClickException(
                    f"Output directory {output_dir} is not empty. "
                    "Use --clean flag to overwrite or choose an empty directory."
                )

        process_directory(
            input_dir, output_dir, single_fork_obj, from_fork, until_fork, quiet_mode
        )

        copy_non_fixture_files(input_dir, output_dir)

        cleanup_empty_directories(output_dir)

        if not quiet_mode:
            click.echo("Regenerating index...")
        regenerate_index(output_dir)

        if not quiet_mode:
            click.echo(f"✅ Filtering complete. Output written to {output_dir}")

    except Exception as e:
        error_str = str(e)
        if "validation error" in error_str.lower():
            sys.exit(1)
        else:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)


if __name__ == "__main__":
    filter_fixtures()
