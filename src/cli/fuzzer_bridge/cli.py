#!/usr/bin/env python
"""Command-line interface for the fuzzer bridge."""

import json
import sys
from pathlib import Path

import click

from .blocktest_builder import BlocktestBuilder


@click.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    help="Input JSON file from fuzzer (default: stdin)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output blocktest JSON file (default: stdout)",
)
@click.option("--fork", default=None, help="Override fork specified in fuzzer output")
@click.option(
    "--evm-bin",
    type=click.Path(exists=True, path_type=Path),
    help="Path to evm binary for transition tool",
)
@click.option("--pretty", is_flag=True, help="Pretty-print JSON output")
def main(input, output, fork, evm_bin, pretty):
    """Convert fuzzer output to valid blocktest fixture."""
    # Read fuzzer data
    if input:
        with open(input) as f:
            fuzzer_data = json.load(f)
    else:
        fuzzer_data = json.load(sys.stdin)

    # Override fork if specified
    if fork:
        fuzzer_data["fork"] = fork

    # Create transition tool
    from ethereum_clis.clis.geth import GethTransitionTool

    if evm_bin:
        t8n = GethTransitionTool(binary=evm_bin)
    else:
        t8n = GethTransitionTool()

    # Build blocktest
    builder = BlocktestBuilder(t8n)
    blocktest = builder.build_blocktest(fuzzer_data)

    # Wrap in fixtures format
    fixtures = {"fuzzer_generated_test": blocktest}

    # Output result
    json_kwargs = {"indent": 2} if pretty else {}
    if output:
        with open(output, "w") as f:
            json.dump(fixtures, f, **json_kwargs)
        click.echo(f"Blocktest written to: {output}", err=True)
    else:
        json.dump(fixtures, sys.stdout, **json_kwargs)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
