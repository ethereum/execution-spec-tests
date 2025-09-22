"""Command-line interface for the fuzzer bridge."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from ethereum_clis import GethTransitionTool, TransitionTool

from .blocktest_builder import BlocktestBuilder


@click.command()
@click.argument(
    "input_file",
    type=click.Path(exists=True, path_type=Path),
    required=False,
)
@click.argument(
    "output_file",
    type=click.Path(path_type=Path),
    required=False,
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
def main(
    input_file: Optional[Path],
    output_file: Optional[Path],
    fork: Optional[str],
    evm_bin: Optional[Path],
    pretty: bool,
):
    """
    Convert fuzzer output to valid blocktest fixture.

    INPUT_FILE: Input JSON file from fuzzer (default: stdin)
    OUTPUT_FILE: Output blocktest JSON file (default: stdout)
    """
    # Read fuzzer data
    if input_file:
        with open(input_file) as f:
            fuzzer_data = json.load(f)
    else:
        fuzzer_data = json.load(sys.stdin)

    # Override fork if specified
    if fork:
        fuzzer_data["fork"] = fork

    # Create transition tool
    t8n: TransitionTool
    if evm_bin:
        t8n = GethTransitionTool(binary=evm_bin)
    else:
        t8n = GethTransitionTool()

    # Build blocktest
    builder = BlocktestBuilder(t8n)
    blocktest = builder.build_blocktest(fuzzer_data)
    fixtures = {"fuzzer_generated_test": blocktest}

    # Output result
    json_kwargs = {"indent": 2} if pretty else {}
    if output_file:
        with open(output_file, "w") as f:
            json.dump(fixtures, f, **json_kwargs)
        click.echo(f"Blocktest written to: {output_file}", err=True)
    else:
        json.dump(fixtures, sys.stdout, **json_kwargs)
        if sys.stdout.isatty():
            sys.stdout.write("\n")


if __name__ == "__main__":
    main()
