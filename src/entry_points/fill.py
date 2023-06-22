"""
Define an entry point wrapper for pytest.

Essentially an alias for pytest but modifies the behavior of --help:
- 'fill --help' only prints the options defined by ./src/pytest_plugins/.
- 'fill --help -v' prints the full help (equivalent to 'pytest --help')

The approach is brittle, but pragmatic. There isn't a direct way to trace
back a command-line option to the plugin that registered it because when
a plugin registers a command-line option, it doesn't tag that option with
its own name or ID.

There's an open feature request for this:
https://github.com/pytest-dev/pytest/issues/9452
"""

import subprocess
import sys

import pytest


def main():  # noqa: D103
    if "--help" in sys.argv and "-v" not in sys.argv:
        sys.argv.remove("--help")

        result = subprocess.run(["pytest", "--help"], capture_output=True, text=True)
        output = result.stdout

        start_string = "Arguments defining evm executable behavior:"
        end_string = "distributed and subprocess testing:"

        start = output.find(start_string)
        end = output.find(end_string)

        if start != -1 and end != -1:
            required_help_text = output[start : end - 2]
            print(
                "The 'fill' command is an alias for 'pytest'. Run 'fill --help -v' to\n"
                "see the complete pytest cli help.\n\n"
                "Here are the custom options provided by the plugins defined by the\n"
                "execution-spec-tests framework.\n"
            )
            print(required_help_text)
        else:
            print(
                "Unable to extract required help text. Run `fill --help` instead and "
                "go and shout at the maintainers."
            )
        return
    else:
        sys.argv.remove("-v")
        pytest.main(sys.argv[1:])


if __name__ == "__main__":
    main()
