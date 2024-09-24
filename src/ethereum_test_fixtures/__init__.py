"""
Ethereum test fixture format definitions.
"""

from typing import Dict

from .base import BaseFixture, FixtureFormat
from .blockchain import EngineFixture as BlockchainEngineFixture
from .blockchain import Fixture as BlockchainFixture
from .blockchain import FixtureCommon as BlockchainFixtureCommon
from .collector import FixtureCollector, TestInfo
from .eof import Fixture as EOFFixture
from .state import Fixture as StateFixture
from .verify import FixtureVerifier

FIXTURE_FORMATS: Dict[str, FixtureFormat] = {
    BlockchainFixture.fixture_test_type: BlockchainFixture,
    BlockchainEngineFixture.fixture_test_type: BlockchainEngineFixture,
    EOFFixture.fixture_test_type: EOFFixture,
    StateFixture.fixture_test_type: StateFixture,
}
__all__ = [
    "FIXTURE_FORMATS",
    "BaseFixture",
    "BlockchainFixture",
    "BlockchainFixtureCommon",
    "BlockchainEngineFixture",
    "EOFFixture",
    "FixtureCollector",
    "FixtureFormat",
    "FixtureVerifier",
    "StateFixture",
    "TestInfo",
]
