"""
CLI entry points for the main commands provided by execution-spec-tests.

These can be directly accessed in a prompt if the user has directly installed
the package via:

```
python -m venv venv
source venv/bin/activate
pip install -e .[doc,lint,test]
# or, more minimally:
pip install -e .
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
from src.entry_points.cli import fill
from click.testing import CliRunner

runner = CliRunner()
result = runner.invoke(fill, ["--help"])
print(result.output)
```
"""
import os
import sys
import tempfile
import warnings
from pathlib import Path

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


def common_options(func):
    """
    Common options for both the fill and consume commands.
    """
    func = click.option(
        "-h",
        "--help",
        "help_flag",
        is_flag=True,
        default=False,
        expose_value=True,
        help="Show pytest's help message.",
    )(func)

    func = click.option(
        "--pytest-help",
        "pytest_help_flag",
        is_flag=True,
        default=False,
        expose_value=True,
        help="Show pytest's help message.",
    )(func)

    func = click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)(func)

    return func


def handle_help_flags(pytest_args, help_flag, pytest_help_flag):
    """
    Modify pytest arguments based on the provided help flags.
    """
    if help_flag:
        return ["--test-help"]
    elif pytest_help_flag:
        return ["--help"]
    else:
        return list(pytest_args)


def handle_stdout_flags(args):
    """
    If the user has requested to write to stdout, add pytest arguments in order
    to suppress pytest's test session header and summary output.
    """
    writing_to_stdout = False
    if any(arg == "--output=stdout" for arg in args):
        writing_to_stdout = True
    elif "--output" in args:
        output_index = args.index("--output")
        if args[output_index + 1] == "stdout":
            writing_to_stdout = True
    if writing_to_stdout:
        if any(arg == "-n" or arg.startswith("-n=") for arg in args):
            sys.exit("error: xdist-plugin not supported with --output=stdout (remove -n args).")
        args.extend(["-qq", "-s"])
    return args


def get_hive_flags_from_env():
    """
    Read simulator flags from environment variables and convert them, as best as
    possible, into pytest flags.
    """
    pytest_args = []
    xdist_workers = os.getenv("HIVE_PARALLELISM")
    if xdist_workers is not None:
        pytest_args.extend("-n", xdist_workers)
    test_pattern = os.getenv("HIVE_TEST_PATTERN")
    if test_pattern is not None:
        # TODO: Check that the regex is a valid pytest -k "test expression"
        pytest_args.extend("-k", test_pattern)
    random_seed = os.getenv("HIVE_RANDOM_SEED")
    if random_seed is not None:
        # TODO: implement random seed
        warnings.warning("HIVE_RANDOM_SEED is not yet supported.")
    log_level = os.getenv("HIVE_LOGLEVEL")
    if log_level is not None:
        # TODO add logging within simulators and implement log level via cli
        warnings.warning("HIVE_LOG_LEVEL is not yet supported.")
    return pytest_args


@click.command(context_settings=dict(ignore_unknown_options=True))
@common_options
def fill(pytest_args, help_flag, pytest_help_flag):
    """
    Entry point for the fill command.
    """
    args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)
    args = handle_stdout_flags(args)
    pytest.main(args)


@click.group()
def consume():
    """
    Help clients consume JSON test fixtures.
    """
    pass


@click.command(context_settings=dict(ignore_unknown_options=True))
@common_options
def consume_direct(pytest_args, help_flag, pytest_help_flag):
    """
    Clients consume directly via the `blocktest` interface.
    """
    args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)
    args += ["-c", "pytest-consume-direct.ini"]
    if not sys.stdin.isatty():  # the command is receiving input on stdin
        args.extend(["-s", "--input=stdin"])
    pytest.main(args)


@click.command(context_settings=dict(ignore_unknown_options=True))
@common_options
def consume_via_rlp(pytest_args, help_flag, pytest_help_flag):
    """
    Clients consume RLP-encoded blocks on startup.
    """
    args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)
    args += ["-c", "pytest-consume-via-rlp.ini"]
    args += get_hive_flags_from_env()
    if not sys.stdin.isatty():  # the command is receiving input on stdin
        args.extend(["-s", "--input=stdin"])
    pytest.main(args)


@click.command(context_settings=dict(ignore_unknown_options=True))
@common_options
def consume_via_engine_api(pytest_args, help_flag, pytest_help_flag):
    """
    Clients consume via the Engine API.
    """
    args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)
    args += ["-c", "pytest-consume-via-engine-api.ini"]
    args += get_hive_flags_from_env()
    if not sys.stdin.isatty():  # the command is receiving input on stdin
        args.extend(["-s", "--input=stdin"])
    pytest.main(args)


@click.command(context_settings=dict(ignore_unknown_options=True))
@common_options
def consume_all(pytest_args, help_flag, pytest_help_flag):
    """
    Clients consume via all available methods (direct, rlp, engine).
    """
    args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)
    args += ["-c", "pytest-consume-all.ini"]
    args += get_hive_flags_from_env()
    if not sys.stdin.isatty():  # the command is receiving input on stdin
        args.extend(["-s", "--input=stdin"])
    pytest.main(args)


@click.command(context_settings=dict(ignore_unknown_options=True))
@common_options
def fill_and_consume_all(pytest_args, help_flag, pytest_help_flag):
    """
    Fill and consume test fixtures using all available consume commands.
    """
    args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)

    temp_dir = Path(tempfile.TemporaryDirectory().name) / "fixtures"
    args += ["--output", temp_dir]
    pytest.main(args)
    consume_args = get_hive_flags_from_env()
    pytest.main(["-c", "pytest-consume-all.ini", "--input", temp_dir, "-v"] + consume_args)


consume.add_command(consume_all, name="all")
consume.add_command(consume_direct, name="direct")
consume.add_command(consume_via_rlp, name="rlp")
consume.add_command(consume_via_engine_api, name="engine")
