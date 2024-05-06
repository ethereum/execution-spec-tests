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
    """
    return ["--co", "--fork", "Frontier"]


@pytest.fixture
def default_html_report_path():
    """
    Provides a default html report path for the `fill` command when testing html report generation.
    """
    return Path("fixtures/report.html")


def test_fill_pytest_html_report(runner, default_html_report_fill_args, default_html_report_path):
    """
    Tests pytest html report generation with the `--html,` `--no-html`, and `--output` options for
    the `fill` command.
    """
    with TemporaryDirectory() as temp_dir:
        # Don't generate the html report
        default_html = Path(temp_dir, default_html_report_path)
        fill_args = default_html_report_fill_args + ["--no-html"]
        result = runner.invoke(fill, fill_args)
        assert result.exit_code == pytest.ExitCode.OK
        assert not default_html.exists()

        # Do not specify the directory of the html report
        result = runner.invoke(fill, default_html_report_fill_args)
        assert result.exit_code == pytest.ExitCode.OK
        assert default_html_report_path.exists()

        # Specify the directory of the html report
        temp_html = Path(temp_dir + "test/report.html")
        fill_args = default_html_report_fill_args + ["--html", str(temp_html)]
        result = runner.invoke(fill, fill_args)
        assert result.exit_code == pytest.ExitCode.OK
        assert temp_html.exists()

        # Specify the fixture output directory
        output_dir = Path(temp_dir, "output")
        temp_html = output_dir / "report.html"
        fill_args = default_html_report_fill_args + ["--output", output_dir]
        result = runner.invoke(fill, fill_args)
        assert result.exit_code == pytest.ExitCode.OK
        assert temp_html.exists()
