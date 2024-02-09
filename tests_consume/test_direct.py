"""
Executes a JSON test fixture directly against a client using a dedicated
client interface similar to geth's EVM 'blocktest' command.
"""

import json
import re
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from evm_transition_tool import FixtureFormats, TransitionTool
from pytest_plugins.consume.consume import TestCase


@pytest.fixture
def write_stdin_fixture_to_file(test_case: TestCase):
    """
    If json fixtures have been provided on stdin, write the current test case's
    fixture to a file for the blocktest command.
    """
    if test_case.json_file == "stdin":
        temp_dir = tempfile.TemporaryDirectory()
        test_case.json_file = (
            Path(temp_dir.name) / f"{test_case.fixture_name.replace('/','_')}.json"
        )
        with open(test_case.json_file, "w") as f:
            json.dump(test_case.fixture_json, f, indent=4)
    yield
    if test_case.json_file == "stdin":
        temp_dir.cleanup()


@pytest.mark.usefixtures("write_stdin_fixture_to_file")
def test_blocktest(  # noqa: D103
    test_case: TestCase,
    evm: TransitionTool,
    evm_use_single_test: bool,
    test_dump_dir: Optional[Path],
):
    evm.verify_fixture(
        FixtureFormats.BLOCKCHAIN_TEST,
        test_case.json_file,
        evm_use_single_test,
        re.escape(test_case.fixture_name),
        test_dump_dir,
    )
