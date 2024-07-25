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

import os
import sys
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, List

import click
import pytest

# Define a custom type for decorators, which are functions that return functions.
Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]


@click.command(context_settings=dict(ignore_unknown_options=True))
def tf() -> None:
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


def common_click_options(func: Callable[..., Any]) -> Decorator:
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


def handle_help_flags(
    pytest_args: List[str], help_flag: bool, pytest_help_flag: bool
) -> List[str]:
    """
    Modifies the help arguments passed to the click CLI command before forwarding to
    the pytest command.

    This is to make `--help` more useful because `pytest --help` is extremely
    verbose and lists all flags from pytest and pytest plugins.
    """
    if help_flag:
        return ["--test-help"]
    elif pytest_help_flag:
        return ["--help"]
    else:
        return list(pytest_args)


def handle_stdout_flags(args: List[str]) -> List[str]:
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
        args.extend(["-qq", "-s", "--no-html"])
    return args


def handle_timing_data_flag(args: List[str]) -> List[str]:
    """
    Consume only. If the user requests timing data ensure stdout is captured.
    """
    if "--timing-data" in args and "-s" not in args:
        args.append("-s")
    return args


@click.command(context_settings=dict(ignore_unknown_options=True))
@common_click_options
def fill(
    pytest_args: List[str],
    help_flag: bool,
    pytest_help_flag: bool,
) -> None:
    """
    Entry point for the fill command.
    """
    args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)
    args = handle_stdout_flags(args)
    result = pytest.main(args)
    sys.exit(result)


def get_hive_flags_from_env():
    """
    Read simulator flags from environment variables and convert them, as best as
    possible, into pytest flags.
    """
    pytest_args = []
    xdist_workers = os.getenv("HIVE_PARALLELISM")
    if xdist_workers is not None:
        pytest_args.extend(["-n", xdist_workers])
    test_pattern = os.getenv("HIVE_TEST_PATTERN")
    if test_pattern is not None:
        # TODO: Check that the regex is a valid pytest -k "test expression"
        pytest_args.extend(["-k", test_pattern])
    random_seed = os.getenv("HIVE_RANDOM_SEED")
    if random_seed is not None:
        # TODO: implement random seed
        warnings.warn("HIVE_RANDOM_SEED is not yet supported.")
    log_level = os.getenv("HIVE_LOGLEVEL")
    if log_level is not None:
        # TODO add logging within simulators and implement log level via cli
        warnings.warn("HIVE_LOG_LEVEL is not yet supported.")
    return pytest_args


def input_provided(args) -> bool:
    """
    Returns true if `--input` is provided via the command line.
    """
    return any(arg.startswith("--input") for arg in args)


@click.group()
def consume():
    """
    Help clients consume JSON test fixtures.
    """
    pass


def consume_test_path(command: str, hive: bool) -> Path:
    """
    Get the test path for the specified consume command.
    """
    consume_path = Path("src/pytest_plugins/consume")
    if not hive:
        return consume_path / command / f"test_{command}.py"
    else:  # rlp or engine
        return consume_path / "hive_simulators" / command / f"test_via_{command}.py"


consume_paths: List[Path] = []
consume_hive_paths: List[Path] = []


def consume_command(hive: bool = False) -> Decorator:
    """
    Decorator to generate a consume sub-command.
    """

    def decorator(func: Callable[..., Any]) -> Decorator:
        command_name = func.__name__
        if command_name == "all":
            command_paths = consume_paths
        elif command_name == "hive":
            command_paths = consume_hive_paths
        else:
            test_path = consume_test_path(command_name, hive)
            consume_paths.append(test_path)
            command_paths = [test_path]
            if hive:
                consume_hive_paths.append(test_path)

        def command(pytest_args, help_flag, pytest_help_flag):
            args = handle_help_flags(pytest_args, help_flag, pytest_help_flag)
            args = handle_timing_data_flag(args)
            args += [
                "-c",
                "pytest-consume.ini",
            ]
            if hive:
                args += ["-p", "pytest_plugins.pytest_hive.pytest_hive"]
                args += get_hive_flags_from_env()

            args += [str(p) for p in command_paths]

            if not input_provided(args) and not sys.stdin.isatty():
                # command is receiving input on stdin
                args.extend(["-s", "--input=stdin"])

            if hive and (not any(arg.startswith("--hive-session-temp-folder") for arg in args)):
                # create temp directory for hive session
                with TemporaryDirectory() as temp_dir:
                    args.extend(["--hive-session-temp-folder", temp_dir])
                    pytest.main(args)
            else:
                pytest.main(args)

        command.__name__ = command_name
        command.__doc__ = func.__doc__

        return consume.command(context_settings=dict(ignore_unknown_options=True))(
            common_click_options(command)
        )

    return decorator


@consume_command()
def direct():
    """
    Clients consume directly via the `blocktest` interface.
    """
    pass


@consume_command(hive=True)
def rlp():
    """
    Clients consume RLP-encoded blocks on startup.
    """
    pass


@consume_command(hive=True)
def engine():
    """
    Clients consume via the Engine API.
    """
    pass


@consume_command(hive=True)
def hive():
    """
    Clients consume via all available hive methods (rlp, engine).
    """
    pass


@consume_command(hive=True)
def all():
    """
    Clients consume via all available methods (direct, rlp, engine).
    """
    pass
