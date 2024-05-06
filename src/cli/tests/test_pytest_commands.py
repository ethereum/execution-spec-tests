"""
Tests for pytest commands (e.g., fill) click CLI.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from click.testing import CliRunner

from ..pytest_commands import fill


@pytest.fixture
def runner():
    """Provides a Click CliRunner for invoking command-line interfaces."""
    return CliRunner()


def test_fill_help(runner):
    """
    Test the `--help` option of the `fill` command.
    """
    result = runner.invoke(fill, ["--help"])
    assert result.exit_code == pytest.ExitCode.OK
    assert "[--evm-bin EVM_BIN] [--traces]" in result.output
    assert "--help" in result.output
    assert "Arguments defining evm executable behavior:" in result.output


def test_fill_pytest_help(runner):
    """
    Test the `--pytest-help` option of the `fill` command.
    """
    result = runner.invoke(fill, ["--pytest-help"])
    assert result.exit_code == pytest.ExitCode.OK
    assert "[options] [file_or_dir] [file_or_dir] [...]" in result.output
    assert "-k EXPRESSION" in result.output


def test_fill_with_invalid_option(runner):
    """
    Test invoking `fill` with an invalid option.
    """
    result = runner.invoke(fill, ["--invalid-option"])
    assert result.exit_code != 0
    assert "unrecognized arguments" in result.output


def test_tf_deprecation(runner):
    """
    Test the deprecation message of the `tf` command.
    """
    from ..pytest_commands import tf

    result = runner.invoke(tf, [])
    assert result.exit_code == 1
    assert "The `tf` command-line tool has been superseded by `fill`" in result.output


@pytest.fixture
def default_html_report_fill_args():
    """
    Provides default arguments for the `fill` command when testing html report generation.

    Specifies a single existing example test case for faster fill execution, and to allow for tests
    to check for the fixture generation location.
    """
    return ["-k", "test_dup and state_test-DUP16", "--fork", "Frontier"]


def test_fill_html_report_default(
    runner,
    default_html_report_fill_args,
):
    """
    Tests the default pytest html report generation.
    """
    default_html = Path("fixtures/report.html")
    with TemporaryDirectory():
        result = runner.invoke(fill, default_html_report_fill_args)
        assert result.exit_code == pytest.ExitCode.OK
        assert default_html.exists()


def test_fill_html_report_no_html_option(
    runner,
    default_html_report_fill_args,
):
    """
    Tests pytest html report generation with the `--no-html` flag.
    """
    default_html = Path("fixtures/report.html")
    with TemporaryDirectory() as temp_dir:
        default_html = Path(temp_dir, default_html)
        fill_args = default_html_report_fill_args + ["--no-html"]
        result = runner.invoke(fill, fill_args)
        assert result.exit_code == pytest.ExitCode.OK
        assert not default_html.exists()


def test_fill_html_report_specified_path_option(
    runner,
    default_html_report_fill_args,
):
    """
    Tests pytest html report generation with the `--html` flag.
    """
    with TemporaryDirectory() as temp_dir:
        temp_html = Path(temp_dir + "test/report.html")
        fill_args = default_html_report_fill_args + ["--html", str(temp_html)]
        result = runner.invoke(fill, fill_args)
        assert result.exit_code == pytest.ExitCode.OK
        assert temp_html.exists()


def test_fill_html_report_output_option(
    runner,
    default_html_report_fill_args,
):
    """
    Tests pytest html report generation with the `--output` flag.
    """
    with TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir, "output")
        temp_html = output_dir / "report.html"
        fill_args = default_html_report_fill_args + ["--output", output_dir]
        result = runner.invoke(fill, fill_args)
        assert result.exit_code == pytest.ExitCode.OK
        assert temp_html.exists()

        # Check the output directory contains fixture/s
        assert (output_dir / "state_tests").exists()
