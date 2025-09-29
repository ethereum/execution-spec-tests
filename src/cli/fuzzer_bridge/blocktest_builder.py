"""Build valid blocktests from fuzzer-generated transactions and pre-state."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import ethereum_test_forks
from ethereum_clis import GethTransitionTool, TransitionTool
from ethereum_test_fixtures import BlockchainFixture
from ethereum_test_specs import BlockchainTest

from .models import FuzzerOutput


class BlocktestBuilder:
    """Build valid blocktests from fuzzer-generated transactions."""

    def __init__(self, transition_tool: Optional[TransitionTool] = None):
        """Initialize the builder with optional transition tool."""
        self.t8n = transition_tool or GethTransitionTool()

    def build_blocktest(self, fuzzer_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build a valid blocktest from fuzzer output."""
        # Parse and validate using Pydantic model
        fuzzer_data = FuzzerOutput(**fuzzer_output)

        # Get fork
        fork_name = fuzzer_data.fork
        fork = getattr(ethereum_test_forks, fork_name)

        # Create BlockchainTest using from_fuzzer method
        test = BlockchainTest.from_fuzzer(fuzzer_output, fork)

        # Generate fixture
        fixture = test.generate(
            t8n=self.t8n,
            fork=fork,
            fixture_format=BlockchainFixture,
        )

        return fixture.model_dump(exclude_none=True, by_alias=True, mode="json")

    def build_and_save(self, fuzzer_output: Dict[str, Any], output_path: Path) -> Path:
        """Build blocktest and save to file."""
        blocktest = self.build_blocktest(fuzzer_output)
        fixtures = {"fuzzer_generated_test": blocktest}

        with open(output_path, "w") as f:
            json.dump(fixtures, f, indent=2)

        return output_path


def build_blocktest_from_fuzzer(
    fuzzer_data: Dict[str, Any], t8n: Optional[TransitionTool] = None
) -> Dict[str, Any]:
    """Build blocktest from fuzzer output."""
    builder = BlocktestBuilder(t8n)
    return builder.build_blocktest(fuzzer_data)
