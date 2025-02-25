"""Ethereum blockchain config test spec definition and filler."""

from typing import Callable, ClassVar, Dict, Generator, List, Optional, Sequence, Type

import pytest

from ethereum_clis import TransitionTool
from ethereum_test_base_types import Address
from ethereum_test_execution import (
    BaseExecute,
    ExecuteFormat,
    LabeledExecuteFormat,
    TransactionPost,
)
from ethereum_test_fixtures import (
    BaseFixture,
    ConfigFixture,
    FixtureFormat,
    LabeledFixtureFormat,
)
from ethereum_test_forks import Fork

from .base import BaseTest


class ConfigTest(BaseTest):
    """Filler type that tests multiple blocks (valid or invalid) in a chain."""

    chain_id: int = 1
    homestead_block: int | None = None
    dao_fork_block: int | None = None
    dao_fork_support: bool | None = None

    # EIP150 implements the Gas price changes (https://github.com/ethereum/EIPs/issues/150)
    eip_150_block: int | None = None
    eip_155_block: int | None = None
    eip_158_block: int | None = None

    byzantium_block: int | None = None
    constantinople_block: int | None = None
    petersburg_block: int | None = None
    istanbul_block: int | None = None
    muir_glacier_block: int | None = None
    berlin_block: int | None = None
    london_block: int | None = None
    arrow_glacier_block: int | None = None
    gray_glacier_block: int | None = None
    merge_netsplit_block: int | None = None

    # Fork scheduling was switched from blocks to timestamps here

    shanghai_time: int | None = None
    cancun_time: int | None = None
    prague_time: int | None = None
    osaka_time: int | None = None

    terminal_total_difficulty: int | None = None

    deposit_contract_address: Address | None = None

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | LabeledFixtureFormat]] = [
        ConfigFixture,
    ]
    supported_execute_formats: ClassVar[Sequence[ExecuteFormat | LabeledExecuteFormat]] = []

    def make_config_fixture(self, fork: Fork) -> ConfigFixture:
        """Generate the config fixture."""
        fixture: ConfigFixture = ConfigFixture(
            **self.model_dump(exclude_none=True),
            blob_schedule=fork.blob_schedule,
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
