"""
A pytest plugin that modifies the "Failures" terminal summary to only show the
exception name and message; it removes all traceback information for a clearer
summary.

The stdout and stderr sections of a failing test will still be displayed.

The user can disable this plugin and achieve default traceback behavior by
either:

1. Specifying the `--disable-exceptions-only` flag, or,
2. Specifying the `--tb` flag.
"""
import sys


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    terminal_output = parser.getgroup(
        "custom_terminal_output", "Arguments modifying terminal output"
    )
    terminal_output.addoption(
        "--disable-exceptions-only",
        dest="disable_exceptions_only",
        action="store_true",
        default=False,
        help="Disable custom terminal output for test failures (use pytest's default format).",
    )


def pytest_configure(config):
    """
    Apply configuration after command-line options have been parsed.

    Disable the custom failures summary output if the user has
    specified the `--tb` flag. This allows the user to easily override
    this custom behavior using standard pytest flags.
    """
    if any(arg.startswith("--tb") for arg in sys.argv):
        config.option.disable_exceptions_only = True


def pytest_exception_interact(node, call, report):
    """
    Modify the terminal output to display only the exception message.

    In particular, we remove all traceback information.
    """
    if not node.config.getoption("disable_exceptions_only") and report.failed:
        excinfo = call.excinfo
        exception_name = excinfo.type.__name__
        exception_message = str(excinfo.value)
        formatted_exception = f"{exception_name}: {exception_message}"
        new_lines_preserved = formatted_exception.replace("\\n", "\n").replace("\\t", "\t")
        report.longrepr = new_lines_preserved
