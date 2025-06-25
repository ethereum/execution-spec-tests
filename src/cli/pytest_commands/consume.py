"""CLI entry point for the `consume` pytest-based command."""

import functools
from pathlib import Path
from typing import Any, Callable, List

import click

from .base import ArgumentProcessor, PytestCommand, PytestExecution, common_pytest_options
from .processors import ConsumeCommandProcessor, HelpFlagsProcessor, HiveEnvironmentProcessor


class ConsumeCommand(PytestCommand):
    """Pytest command for consume operations."""

    def __init__(self, command_paths: List[Path], is_hive: bool = False, command_name: str = ""):
        """Initialize consume command with paths and processors."""
        processors: List[ArgumentProcessor] = [HelpFlagsProcessor("consume")]

        if is_hive:
            processors.extend(
                [
                    HiveEnvironmentProcessor(command_name=command_name),
                    ConsumeCommandProcessor(is_hive=True),
                ]
            )
        else:
            processors.append(ConsumeCommandProcessor(is_hive=False))

        super().__init__(
            config_file="pytest-consume.ini",
            argument_processors=processors,
        )
        self.command_paths = command_paths

    def create_executions(self, pytest_args: List[str]) -> List[PytestExecution]:
        """Create execution with test paths prepended."""
        processed_args = self.process_arguments(pytest_args)

        # Prepend test paths to arguments
        test_path_args = [str(p) for p in self.command_paths]
        final_args = test_path_args + processed_args

        return [
            PytestExecution(
                config_file=self.config_file,
                args=final_args,
            )
        ]


def get_command_paths(command_name: str, is_hive: bool) -> List[Path]:
    """Determine the command paths based on the command name and hive flag."""
    base_path = Path("src/pytest_plugins/consume")
    if command_name == "hive":
        commands = ["rlp", "engine"]
        command_paths = [
            base_path / "simulators" / "hive_tests" / f"test_via_{cmd}.py" for cmd in commands
        ]
    elif command_name in ["engine", "enginex"]:
        command_paths = [base_path / "simulators" / "hive_tests" / "test_via_engine.py"]
    elif command_name == "rlp":
        command_paths = [base_path / "simulators" / "hive_tests" / "test_via_rlp.py"]
    elif command_name == "direct":
        command_paths = [base_path / "direct" / "test_via_direct.py"]
    else:
        raise ValueError(f"Unexpected command: {command_name}.")
    return command_paths


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def consume() -> None:
    """Consume command to aid client consumption of test fixtures."""
    pass


def consume_command(is_hive: bool = False) -> Callable[[Callable[..., Any]], click.Command]:
    """Generate a consume sub-command."""

    def decorator(func: Callable[..., Any]) -> click.Command:
        command_name = func.__name__
        command_help = func.__doc__
        command_paths = get_command_paths(command_name, is_hive)

        @consume.command(
            name=command_name,
            help=command_help,
            context_settings={"ignore_unknown_options": True},
        )
        @common_pytest_options
        @functools.wraps(func)
        def command(pytest_args: List[str], **kwargs) -> None:
            consume_cmd = ConsumeCommand(command_paths, is_hive, command_name)
            consume_cmd.execute(list(pytest_args))

        return command

    return decorator


@consume_command(is_hive=False)
def direct() -> None:
    """Clients consume directly via the `blocktest` interface."""
    pass


@consume_command(is_hive=True)
def rlp() -> None:
    """Client consumes RLP-encoded blocks on startup."""
    pass


@consume_command(is_hive=True)
def engine() -> None:
    """Client consumes Engine Fixtures via the Engine API."""
    pass


@consume.command(
    name="enginex",
    help="Client consumes Engine X Fixtures via the Engine API.",
    context_settings={"ignore_unknown_options": True},
)
@click.option(
    "--enginex-fcu-frequency",
    type=int,
    default=1,
    help=(
        "Control forkchoice update frequency for enginex simulator. "
        "0=disable FCUs, 1=FCU every test (default), N=FCU every Nth test per "
        "pre-allocation group."
    ),
)
@common_pytest_options
def enginex(enginex_fcu_frequency: int, pytest_args: List[str], **_kwargs) -> None:
    """Client consumes Engine X Fixtures via the Engine API."""
    command_name = "enginex"
    command_paths = get_command_paths(command_name, is_hive=True)

    # Validate the frequency parameter
    if enginex_fcu_frequency < 0:
        raise click.BadParameter("FCU frequency must be non-negative")

    # Add the FCU frequency to pytest args as a custom config option
    pytest_args_with_fcu = [f"--enginex-fcu-frequency={enginex_fcu_frequency}"] + list(pytest_args)

    consume_cmd = ConsumeCommand(command_paths, is_hive=True, command_name=command_name)
    consume_cmd.execute(pytest_args_with_fcu)


@consume_command(is_hive=True)
def hive() -> None:
    """Client consumes via rlp & engine hive methods."""
    pass


@consume.command(
    context_settings={"ignore_unknown_options": True},
)
@common_pytest_options
def cache(pytest_args: List[str], **kwargs) -> None:
    """Consume command to cache test fixtures."""
    cache_cmd = ConsumeCommand([], is_hive=False)
    cache_cmd.execute(list(pytest_args))
