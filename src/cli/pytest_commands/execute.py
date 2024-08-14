"""
CLI entry point for the `execute` pytest-based command.
"""

import sys
from tempfile import TemporaryDirectory
from typing import Tuple

import click
import pytest

from .common import common_click_options, handle_help_flags


@click.option(
    "--hive-mode",
    "hive_mode_flag",
    is_flag=True,
    default=False,
    expose_value=True,
    help="Whether to run in hive mode, which spawns a devnet with the required genesis.",
)
@click.command(context_settings=dict(ignore_unknown_options=True))
@common_click_options
def execute(
    pytest_args: Tuple[str, ...],
    help_flag: bool,
    hive_mode_flag: bool,
    pytest_help_flag: bool,
) -> None:
    """
    Entry point for the execute command.
    """
    with TemporaryDirectory() as temp_dir:
        ini_file = "pytest-execute-hive.ini" if hive_mode_flag else "pytest-execute.ini"
        default_args = ("-c", ini_file, f"--hive-session-temp-folder={temp_dir}")
        args = handle_help_flags(list(pytest_args + default_args), help_flag, pytest_help_flag)
        result = pytest.main(args)
    sys.exit(result)
