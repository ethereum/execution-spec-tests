"""
A Pytest plugin to configure logging for pytest sessions.

Note: While pytest's builtin logging is generally amazing, it does not write timestamps
when log output is written to pytest's caplog (the captured output for a test). And having
timestamps in this output is the main use case for adding logging to our plugins.
This output gets shown in the `FAILURES` summary section, which is shown as the
"simulator log" in hive simulations. For this use case, timestamps are essential to verify
timing issues against the clients log.
"""

import functools
import logging
import os
import sys
from datetime import datetime, timezone
from logging import LogRecord
from pathlib import Path
from typing import Optional

import pytest
from _pytest.terminal import TerminalReporter

logger = logging.getLogger(__name__)

# global that gets set in pytest_configure()
file_handler: Optional[logging.FileHandler] = None

FAIL_LEVEL = 35  # Between WARNING (30) and ERROR (40)


def fail(self, message, *args, **kwargs):
    """Define a new log level for failing tests."""
    if self.isEnabledFor(FAIL_LEVEL):
        self._log(FAIL_LEVEL, message, args, **kwargs)


if not hasattr(logging.Logger, "fail"):
    logging.addLevelName(FAIL_LEVEL, "FAIL")
    logging.Logger.fail = fail  # type: ignore[attr-defined]


class UTCFormatter(logging.Formatter):
    """Log formatter that formats UTC timestamps with milliseconds and +00:00 suffix."""

    def formatTime(self, record, datefmt=None):  # noqa: D102,N802  # camelcase required
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "+00:00"


class ColorFormatter(UTCFormatter):
    """Formatter that adds ANSI color codes to log level names for terminal output."""

    COLORS = {
        logging.DEBUG: "\033[37m",  # Gray
        logging.INFO: "\033[36m",  # Cyan
        logging.WARNING: "\033[33m",  # Yellow
        FAIL_LEVEL: "\033[35m",  # Magenta
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record: LogRecord) -> str:
        """Apply colorful formatting."""
        if self.running_in_docker():
            return super().format(record)
        color = self.COLORS.get(record.levelno, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

    @staticmethod
    def running_in_docker() -> bool:
        """Return True if `/.dockerenv` exists."""
        return Path("/.dockerenv").exists()


class LogLevel:
    """Help parse a log-level provided on the command-line."""

    @classmethod
    def from_cli(cls, value: str) -> int:
        """
        Parse a logging level from CLI.

        Accepts standard level names (e.g. 'INFO', 'debug') or numeric values.
        """
        try:
            return int(value)
        except ValueError:
            pass

        level_name = value.upper()
        if level_name in logging._nameToLevel:
            return logging._nameToLevel[level_name]

        valid = ", ".join(logging._nameToLevel.keys())
        raise ValueError(f"Invalid log level '{value}'. Expected one of: {valid} or a number.")


def pytest_addoption(parser):  # noqa: D103
    logging_group = parser.getgroup(
        "logging", "Arguments related to logging from test fixtures and tests."
    )
    logging_group.addoption(
        "--eest-log-level",  # --log-level is defined by pytest's built-in logging
        "--eestloglevel",
        action="store",
        default="INFO",
        type=LogLevel.from_cli,
        dest="eest_log_level",
        help=(
            "The logging level to use in the test session: DEBUG INFO WARNING ERROR or "
            "CRITICAL, default - INFO. An integer in [0, 50] may be also provided."
        ),
    )


@functools.cache
def get_log_stem(argv0: str, argv1: Optional[str]) -> str:
    """Generate the stem (prefix-subcommand-timestamp) for log files."""
    stem = Path(argv0).stem
    prefix = "pytest" if stem in ("", "-c", "__main__") else stem
    subcommand = argv1 if argv1 and not argv1.startswith("-") else None
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    name_parts = [prefix]
    if subcommand:
        name_parts.append(subcommand)
    name_parts.append(timestamp)

    return "-".join(name_parts)


def pytest_configure_node(node):
    """Initialize a variable for use in the worker (xdist hook)."""
    potential_subcommand = None
    if len(sys.argv) > 1:
        potential_subcommand = sys.argv[1]
    node.workerinput["log_stem"] = get_log_stem(sys.argv[0], potential_subcommand)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """
    Initialize logging.

    This goes to a lot of effort to ensure that a log file is created per worker
    if xdist is used and that the timestamp used in the filename is the same across
    main and all workers.
    """
    global file_handler

    potential_subcommand = None
    if len(sys.argv) > 1:
        potential_subcommand = sys.argv[1]
    log_stem = getattr(config, "workerinput", {}).get("log_stem") or get_log_stem(
        sys.argv[0], potential_subcommand
    )

    worker_id = os.getenv("PYTEST_XDIST_WORKER", "main")
    log_filename = f"{log_stem}-{worker_id}.log"
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    config.option.eest_log_file_path = log_path / log_filename

    formatter = UTCFormatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(config.getoption("eest_log_level"))

    file_handler = logging.FileHandler(config.option.eest_log_file_path, mode="w")
    file_handler.setFormatter(formatter)
    config._eest_file_handler = file_handler  # type: ignore[attr-defined]
    root_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        ColorFormatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    root_logger.addHandler(stream_handler)


def pytest_report_header(config: pytest.Config) -> list[str]:
    """Show the log file path in the test session header."""
    if eest_log_file_path := config.option.eest_log_file_path:
        return [f"Log file: {eest_log_file_path}"]
    return []


def pytest_terminal_summary(terminalreporter: TerminalReporter, exitstatus: int) -> None:
    """Display the log file path in the terminal summary like the HTML report does."""
    if terminalreporter.config.option.collectonly:
        return
    if eest_log_file_path := terminalreporter.config.option.eest_log_file_path:
        terminalreporter.write_sep("-", f"Log file: {eest_log_file_path.resolve()}", yellow=True)


def log_only_to_file(level: int, msg: str, *args, **kwargs) -> None:
    """Log a message only to the file handler, bypassing stdout."""
    if not file_handler:
        return
    handler: logging.Handler = file_handler  # type: ignore[attr-defined]
    logger = logging.getLogger(__name__)
    if not logger.isEnabledFor(level):
        return
    record: LogRecord = logger.makeRecord(
        logger.name,
        level,
        fn=__file__,
        lno=0,
        msg=msg,
        args=args,
        exc_info=None,
        func=None,
        extra=None,
    )
    handler.handle(record)


def pytest_runtest_logstart(nodeid: str, location: tuple[str, int, str]) -> None:
    """Log test start to file."""
    log_only_to_file(logging.INFO, f"ℹ️  - START TEST: {nodeid}")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Log test status and duration to file after it runs."""
    if report.when != "call":
        return

    nodeid = report.nodeid
    duration = report.duration

    log_level = logging.INFO
    if hasattr(report, "wasxfail"):
        if report.skipped:
            status = "XFAIL"
            emoji = "💤"
        elif report.passed:
            status = "XPASS"
            emoji = "🚨"
        else:
            status = "XFAIL ERROR"
            emoji = "💣"
            log_level = logging.ERROR
    elif report.skipped:
        status = "SKIPPED"
        emoji = "⏭️"
    elif report.failed:
        status = "FAILED"
        emoji = "❌"
        log_level = FAIL_LEVEL
    else:
        status = "PASSED"
        emoji = "✅"

    log_only_to_file(log_level, f"{emoji} - {status} in {duration:.2f}s: {nodeid}")


def pytest_runtest_logfinish(nodeid: str, location: tuple[str, int, str]) -> None:
    """Log end of test to file."""
    log_only_to_file(logging.INFO, f"ℹ️  - END TEST: {nodeid}")
