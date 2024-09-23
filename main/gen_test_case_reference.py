"""
Script called during mkdocs build|serve to create the "Test Case Reference".

Called via the mkdocs-gen-files plugin; it's specified in mkdocs.yaml and
can't take command-line arguments. The main logic is implemented in
src/pytest_plugins/filler/gen_test_doc.py.
"""
import importlib
import logging
import sys

import pytest
from click.testing import CliRunner

import pytest_plugins.filler.gen_test_doc.gen_test_doc as gen_test_doc
from cli.pytest_commands.fill import fill

importlib.reload(gen_test_doc)  # get changes in plugin for use with `mkdocs serve`

logger = logging.getLogger("mkdocs")
dev_fork = "PragueEIP7692"
args = [
    "--override-ini",
    "filterwarnings=ignore::pytest.PytestAssertRewriteWarning",  # suppress warnings due to reload
    "-p",
    "pytest_plugins.filler.gen_test_doc.gen_test_doc",
    "--gen-docs",
    "-m",
    "(not blockchain_test_engine) and (not eip_version_check)",
    f"--fork={dev_fork}",
    "-s",
    "tests",
    # "tests/shanghai",
    # "tests/prague/eip7692_eof_v1",  # noqa: SC100
    # "tests/prague/eip2537_bls_12_381_precompiles",  # noqa: SC100
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
    logger.info("Documentation generation successful.")
    sys.exit(0)
logger.error(
    f"Documentation generation failed (exit: {pytest.ExitCode(result.exit_code)}, "
    f"{pytest.ExitCode(result.exit_code).name})."
)
sys.exit(result.exit_code)
