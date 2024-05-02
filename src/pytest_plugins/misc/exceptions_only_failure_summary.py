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

        # if hasattr(call.excinfo.value, "args"):
        #    formatted_exception = "\nAdditional Info: " + str(call.excinfo.value.args)
        tb = call.excinfo.traceback

        # Extract the last traceback entry
        last_tb_entry = tb[-1]

        # Format the traceback entry to string, using only the last entry
        formatted_traceback = (
            f"{last_tb_entry.path}:{last_tb_entry.lineno}: in {last_tb_entry.name}\n"
        )
        excinfo = call.excinfo
        exception_name = excinfo.type.__name__
        exception_message = str(excinfo.value)
        formatted_exception = f"{exception_name}: {exception_message}"
        summary = f"{formatted_traceback}\n{formatted_exception}"
        new_lines_preserved = summary.replace("\\n", "\n").replace("\\t", "\t")
        report.longrepr = new_lines_preserved


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add a custom section to the terminal summary.
    """
    if not config.getoption("disable_exceptions_only"):
        terminalreporter.ensure_newline()
        terminalreporter.section("exceptions_only_failure_summary info")
        terminalreporter.line(
            "Pytest was ran with the `exceptions_only_failure_summary` plugin enabled."
        )
        terminalreporter.line(
            "Use `--tb=auto` or '--disable-exceptions-only' to disable it and get more detailed "
            "traceback information."
        )
