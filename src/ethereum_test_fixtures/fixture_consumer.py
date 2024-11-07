"""
Ethereum test fixture consumer abstract class.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .base import FixtureFormat
from .blockchain import Fixture as BlockchainFixture
from .eof import Fixture as EOFFixture
from .state import Fixture as StateFixture


class FixtureConsumer(ABC):
    """
    Abstract class for verifying Ethereum test fixtures.
    """

    def __init__(
        self,
        statetest_binary: Optional[Path] = None,
        blocktest_binary: Optional[Path] = None,
        eoftest_binary: Optional[Path] = None,
    ):
        self.statetest_binary = statetest_binary
        self.blocktest_binary = blocktest_binary
        self.eoftest_binary = eoftest_binary

    def is_consumable(
        self,
        fixture_format: FixtureFormat,
    ) -> bool:
        """
        Returns whether the fixture format is verifiable by this verifier.
        """
        if fixture_format == StateFixture:
            return self.statetest_binary is not None
        elif fixture_format == BlockchainFixture:
            return self.blocktest_binary is not None
        elif fixture_format == EOFFixture:
            return self.eoftest_binary is not None
        return False

    @abstractmethod
    def consume_fixture(
        self,
        fixture_format: FixtureFormat,
        fixture_path: Path,
        fixture_name: str | None = None,
        debug_output_path: Path | None = None,
    ):
        """
        Test the client with the specified fixture using its direct consumer interface.
        """
        raise NotImplementedError(
            "The `consume_fixture()` function is not supported by this tool."
        )
