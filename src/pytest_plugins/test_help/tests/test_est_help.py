"""
Test the est_help plugin.
"""

import pytest

EST_ARGS = (
    "--evm-bin",
    "--traces",
    "--solc-bin",
    "--filler-path",
    "--output",
    "--forks",
    "--fork",
    "--from",
    "--until",
    "--eth-help",
)


@pytest.mark.parametrize("help_flag", ["--eth-help", "--est-help"])
def test_local_arguments_present_in_est_help(pytester, help_flag):
    """
    Test that locally defined command-line flags appear in the help if
    our custom help flag is used.
    """
    pytester.copy_example(name="pytest.ini")
    result = pytester.runpytest(help_flag)
    for est_arg in EST_ARGS:
        assert est_arg in "\n".join(result.stdout.lines)
