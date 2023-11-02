"""
Test module that defines a test to execute a fixture against an EVM blocktest-like command.
"""
from pathlib import Path
from typing import Optional

from evm_transition_tool import FixtureFormats, TransitionTool


def test_fixtures(  # noqa: D103
    evm: TransitionTool,
    json_fixture_path: Path,
    evm_use_single_test: bool,
    fixture_name: str,
    test_dump_dir: Optional[Path],
):
    evm.verify_fixture(
        FixtureFormats.BLOCKCHAIN_TEST,
        json_fixture_path,
        evm_use_single_test,
        fixture_name,
        test_dump_dir,
    )
