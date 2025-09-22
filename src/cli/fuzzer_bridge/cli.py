"""Command-line interface for the fuzzer bridge."""

import json
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import click
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn

from ethereum_clis import GethTransitionTool, TransitionTool

from .blocktest_builder import BlocktestBuilder


def count_json_files(start_path: Path) -> int:
    """Count JSON files in directory."""
    return sum(1 for _ in start_path.rglob("*.json"))


def get_input_files(input_path: Path) -> Generator[Path, None, None]:
    """Generate input file paths."""
    if input_path.is_file():
        yield input_path
    else:
        yield from input_path.rglob("*.json")


def generate_test_name(file_path: Path, index: int = 0) -> str:
    """Generate unique test name from file path."""
    stem = file_path.stem
    if index > 0:
        return f"fuzzer_{stem}_{index}"
    return f"fuzzer_{stem}"


def process_single_file(
    input_file: Path,
    output_path: Path,
    builder: BlocktestBuilder,
    fork: Optional[str],
    pretty: bool,
    quiet: bool,
) -> Dict[str, Any]:
    """Process a single fuzzer output file."""
    with open(input_file) as f:
        fuzzer_data = json.load(f)

    # Override fork if specified
    if fork:
        fuzzer_data["fork"] = fork

    # Build blocktest
    blocktest = builder.build_blocktest(fuzzer_data)
    test_name = generate_test_name(input_file)
    fixtures = {test_name: blocktest}

    # Write output
    output_file = output_path / f"{input_file.stem}.json"
    json_kwargs = {"indent": 2} if pretty else {}
    with open(output_file, "w") as f:
        json.dump(fixtures, f, **json_kwargs)

    if not quiet:
        click.echo(f"Generated: {output_file}", err=True)

    return fixtures


def process_directory(
    input_dir: Path,
    output_dir: Path,
    builder: BlocktestBuilder,
    fork: Optional[str],
    pretty: bool,
    merge: bool,
    quiet: bool,
):
    """Process directory of fuzzer output files."""
    all_fixtures = {}
    file_count = count_json_files(input_dir) if not quiet else 0
    success_count = 0
    error_count = 0

    with Progress(
        TextColumn("[bold cyan]{task.fields[filename]}", justify="left"),
        BarColumn(bar_width=None, complete_style="green3", finished_style="bold green3"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        expand=True,
        disable=quiet,
    ) as progress:
        task_id = progress.add_task("Processing", total=file_count, filename="...")

        for json_file_path in get_input_files(input_dir):
            # Preserve directory structure
            rel_path = json_file_path.relative_to(input_dir)
            display_name = str(rel_path)
            if len(display_name) > 40:
                display_name = "..." + display_name[-37:]

            progress.update(task_id, advance=1, filename=display_name)

            try:
                with open(json_file_path) as f:
                    fuzzer_data = json.load(f)

                # Override fork if specified
                if fork:
                    fuzzer_data["fork"] = fork

                # Build blocktest
                blocktest = builder.build_blocktest(fuzzer_data)
                test_name = generate_test_name(json_file_path)

                if merge:
                    # Add to merged fixtures
                    all_fixtures[test_name] = blocktest
                else:
                    # Write individual file preserving structure
                    output_file = output_dir / rel_path.with_suffix(".json")
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    fixtures = {test_name: blocktest}
                    json_kwargs = {"indent": 2} if pretty else {}
                    with open(output_file, "w") as f:
                        json.dump(fixtures, f, **json_kwargs)

                success_count += 1

            except Exception as e:
                error_count += 1
                if not quiet:
                    progress.console.print(f"[red]Error processing {json_file_path}: {e}[/red]")

        # Write merged file if requested
        if merge and all_fixtures:
            merged_file = output_dir / "merged_fixtures.json"
            json_kwargs = {"indent": 2} if pretty else {}
            with open(merged_file, "w") as f:
                json.dump(all_fixtures, f, **json_kwargs)
            if not quiet:
                progress.console.print(f"[green]Merged fixtures written to: {merged_file}[/green]")

        # Final status
        if not quiet:
            emoji = "✅" if error_count == 0 else "⚠️"
            progress.update(
                task_id,
                completed=file_count,
                filename=f"Done! {success_count} succeeded, {error_count} failed {emoji}",
            )


@click.command()
@click.argument(
    "input_path",
    type=click.Path(exists=True, dir_okay=True, file_okay=True, path_type=Path),
)
@click.argument(
    "output_path",
    type=click.Path(dir_okay=True, file_okay=False, path_type=Path),
)
@click.option(
    "--fork",
    default=None,
    help="Override fork specified in fuzzer output",
)
@click.option(
    "--evm-bin",
    type=click.Path(exists=True, path_type=Path),
    help="Path to evm binary for transition tool",
)
@click.option(
    "--pretty",
    is_flag=True,
    help="Pretty-print JSON output",
)
@click.option(
    "--merge",
    is_flag=True,
    help="Merge all tests into a single output file",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress progress output",
)
def main(
    input_path: Path,
    output_path: Path,
    fork: Optional[str],
    evm_bin: Optional[Path],
    pretty: bool,
    merge: bool,
    quiet: bool,
):
    """
    Convert fuzzer output to valid blocktest fixtures.

    INPUT_PATH: Input JSON file or directory containing fuzzer output files
    OUTPUT_PATH: Output directory for generated blocktest fixtures
    """
    # Create transition tool
    t8n: TransitionTool
    if evm_bin:
        t8n = GethTransitionTool(binary=evm_bin)
    else:
        t8n = GethTransitionTool()

    # Create builder
    builder = BlocktestBuilder(t8n)

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Process input
    if input_path.is_file():
        # Single file processing
        process_single_file(input_path, output_path, builder, fork, pretty, quiet)
    else:
        # Directory processing
        process_directory(input_path, output_path, builder, fork, pretty, merge, quiet)


if __name__ == "__main__":
    main()
