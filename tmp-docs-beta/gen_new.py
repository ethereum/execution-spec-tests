"""
Documentation generation script for mkdocs_gen_files.

This script is specified in mkdocs.yaml and can't take command-line arguments.
"""
import importlib
import logging
import sys
import warnings

import pytest
from click.testing import CliRunner

import pytest_plugins.filler.gen_test_doc as gen_test_doc
from cli.pytest_commands.fill import fill

importlib.reload(gen_test_doc)  # get changes in plugin for use with `mkdocs serve`
# warnings.filterwarnings("ignore", category=pytest.PytestAssertRewriteWarning)

logger = logging.getLogger("mkdocs")

dev_fork = "PragueEIP7692"

args = [
    "--override-ini",
    "filterwarnings=ignore::pytest.PytestAssertRewriteWarning",  # suppress warnings due to reload
    "--gen-docs",
    "-m",
    "(not blockchain_test_engine) and (not eip_version_check)",
    f"--fork={dev_fork}",
    "tests/",
]

runner = CliRunner()
logger.info(f"Generating documentation for {dev_fork} as fill {' '.join(args)}")
result = runner.invoke(fill, args)
for line in result.output.split("\n"):
    if "===" in line:
        logger.info(line.replace("===", "=="))
        continue
    logger.info(line)
if result.exit_code in [pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED]:
    logger.info(f"Documentation generation successful.")
    sys.exit(0)
logger.error(
    f"Documentation generation failed (exit: {pytest.ExitCode(result.exit_code)}, "
    f"{pytest.ExitCode(result.exit_code).name})."
)
sys.exit(result.exit_code)
