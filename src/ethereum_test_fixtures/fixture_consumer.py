"""Ethereum test fixture consumer abstract class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from .base import FixtureFormat


class FixtureConsumer(ABC):
    """Abstract class for verifying Ethereum test fixtures."""

    fixture_formats: List[FixtureFormat]

    def can_consume(
        self,
        fixture_format: FixtureFormat,
    ) -> bool:
        """Return whether the fixture format is consumable by this consumer."""
        return fixture_format in self.fixture_formats

    @abstractmethod
    def consume_fixture(
        self,
        fixture_format: FixtureFormat,
        fixture_path: Path,
        fixture_name: str | None = None,
        debug_output_path: Path | None = None,
    ):
        """Test the client with the specified fixture using its direct consumer interface."""
        raise NotImplementedError(
            "The `consume_fixture()` function is not supported by this tool."
        )
