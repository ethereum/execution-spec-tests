"""
CLI entry points for the main pytest-based commands provided by
execution-spec-tests.

These can be directly accessed in a prompt if the user has directly installed
the package via:

```
python -m venv venv
source venv/bin/activate
pip install -e .
# or
pip install -e .[doc,lint,test]
```

Then, the entry points can be executed via:

```
fill --help
# for example, or
fill --collect-only
```

They can also be executed (and debugged) directly in an interactive python
shell:

```
from src.cli.pytest_commands import fill
from click.testing import CliRunner

runner = CliRunner()
result = runner.invoke(fill, ["--help"])
print(result.output)
```
"""

import sys

import click
import pytest


@click.command(context_settings=dict(ignore_unknown_options=True))
def tf():  # noqa: D103
    """
    The `tf` command, deprecated as of 2023-06.
    """
    print(
        "The `tf` command-line tool has been superseded by `fill`. Try:\n\n"
        "fill --help\n\n"
        "or see the online docs:\n"
        "https://ethereum.github.io/execution-spec-tests/getting_started/executing_tests_command_line/"  # noqa: E501
    )
    sys.exit(1)


def common_click_options(func):
    """
    Define common click options for fill and other pytest-based commands.

    Note that we don't verify any other options here, rather pass them
    directly to the pytest command for processing.
    """
    func = click.option(
        "-h",
        "--help",
        "help_flag",
        is_flag=True,
        default=False,
        expose_value=True,
        help="Show help message.",
    )(func)

    func = click.option(
        "--pytest-help",
        "pytest_help_flag",
        is_flag=True,
        default=False,
        expose_value=True,
        help="Show pytest's help message.",
    )(func)

    return click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)(func)


def handle_help_flags(pytest_args, help_flag, pytest_help_flag):
    """
    Modify the arguments passed to the click cli command before forwarding to
    to the pytest command.

    This is to make `--help` more useful because`pytest --help` is extremely
    verbose and lists all flags from pytest and pytest plugins.
    """
    if help_flag:
        return ["--test-help"]
    elif pytest_help_flag:
        return ["--help"]
    else:
        return list(pytest_args)


@click.command(context_settings=dict(ignore_unknown_options=True))
@common_click_options
def fill(pytest_args, help_flag, pytest_help_flag):
    """
    Entry point for the fill command.
    """
    args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)
    pytest.main(args)
