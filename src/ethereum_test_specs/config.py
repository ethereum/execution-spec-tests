"""Ethereum blockchain config test spec definition and filler."""

from typing import Callable, ClassVar, Generator, List, Optional, Sequence, Type

import pytest

from ethereum_clis import TransitionTool
from ethereum_test_execution import (
    ExecuteFormat,
    LabeledExecuteFormat,
)
from ethereum_test_fixtures import (
    BaseFixture,
    ConfigFixture,
    FixtureFormat,
    LabeledFixtureFormat,
)
from ethereum_test_forks import Fork, ForkConfig

from .base import BaseTest


class ConfigTest(BaseTest, ForkConfig):
    """Filler type that tests multiple blocks (valid or invalid) in a chain."""

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | LabeledFixtureFormat]] = [
        ConfigFixture,
    ]
    supported_execute_formats: ClassVar[Sequence[ExecuteFormat | LabeledExecuteFormat]] = []

    def make_config_fixture(self, fork: Fork) -> ConfigFixture:
        """Generate the config fixture."""
        fixture: ConfigFixture = ConfigFixture(
            **self.model_dump(exclude_none=True),
            fork=fork.blockchain_test_network_name(),
        )
        return fixture

    def generate(
        self,
        request: pytest.FixtureRequest,
        t8n: TransitionTool,  # Unused
        fork: Fork,
        fixture_format: FixtureFormat,
        eips: Optional[List[int]] = None,
    ) -> BaseFixture:
        """Generate the ConfigTest fixture."""
        t8n.reset_traces()
        if fixture_format == ConfigFixture:
            return self.make_config_fixture(fork)

        raise Exception(f"Unknown fixture format: {fixture_format}")


ConfigTestSpec = Callable[[str], Generator[ConfigTest, None, None]]
ConfigTestFiller = Type[ConfigTest]
