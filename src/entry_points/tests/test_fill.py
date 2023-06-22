"""
Tests for the 'fill' entry point.
"""

import subprocess


def run_fill_command(args):
    """
    Runs fill command with provided arguments and returns output.
    """
    command = ["fill"] + args
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout


def test_fill_help():
    """
    Tests the 'fill --help' command.
    """
    output = run_fill_command(["--help"])

    # check our custom help message is present
    assert "The 'fill' command is an alias for 'pytest'. Run 'fill --help -v' to" in output
    assert "Here are the custom options provided by the plugins defined by the" in output

    # check our custom options are present
    assert "--until" in output
    assert "--evm-bin" in output
    assert "--solc-bin" in output

    # check that pytest help output is not present
    assert "general:" not in output
    assert "PYTEST_PLUGINS" not in output

    # check error message is not present
    assert "Unable to extract required help text." not in output


def test_fill_help_v():
    """Tests 'fill --help -v' command."""
    output = run_fill_command(["--help", "-v"])

    # check our custom help message is present
    assert "The 'fill' command is an alias for 'pytest'. Run 'fill --help -v' to" not in output
    assert "Here are the custom options provided by the plugins defined by the" not in output

    # check our custom options are present
    assert "--until" in output
    assert "--evm-bin" in output
    assert "--solc-bin" in output

    # check if full help is present
    assert "general:" in output
    assert "PYTEST_PLUGINS" in output

    # check error message is not present
    assert "Unable to extract required help text." not in output
