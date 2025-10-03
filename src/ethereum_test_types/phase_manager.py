"""Test phase management for Ethereum tests."""

from contextlib import contextmanager
from enum import Enum
from typing import Any, Iterator, List, Optional

from pydantic import GetCoreSchemaHandler
from pydantic_core.core_schema import (
    PlainValidatorFunctionSchema,
    no_info_plain_validator_function,
)


class TestPhase(Enum):
    """Test phase for state and blockchain tests."""

    SETUP = "setup"
    EXECUTION = "execution"


class TestPhaseManager:
    """
    Manages test phases and collects transactions and blocks by phase.
    This class provides a mechanism for "setup" and "execution" phases,
    Only supports "setup" and "execution" phases now.
    """

    def __init__(self, *args, **kwargs):
        """Initialize TestPhaseManager with empty transactions and blocks."""
        self.setup_transactions: List = []
        self.setup_blocks: List = []
        self.execution_transactions: List = []
        self.execution_blocks: List = []
        self._current_phase: Optional[TestPhase] = TestPhase.EXECUTION

    @contextmanager
    def setup(self) -> Iterator["TestPhaseManager"]:
        """Context manager for the setup phase of a benchmark test."""
        old_phase = self._current_phase
        self._current_phase = TestPhase.SETUP
        try:
            yield self
        finally:
            self._current_phase = old_phase

    @contextmanager
    def execution(self) -> Iterator["TestPhaseManager"]:
        """Context manager for the execution phase of a test."""
        old_phase = self._current_phase
        self._current_phase = TestPhase.EXECUTION
        try:
            yield self
        finally:
            self._current_phase = old_phase

    def add_transaction(self, tx) -> None:
        """Add a transaction to the current phase."""
        current_phase = self._current_phase
        tx.test_phase = current_phase

        if current_phase == TestPhase.EXECUTION:
            self.execution_transactions.append(tx)
        else:
            self.setup_transactions.append(tx)

    def add_block(self, block) -> None:
        """Add a block to the current phase."""
        current_phase = self._current_phase
        for tx in block.txs:
            tx.test_phase = current_phase

        if current_phase == TestPhase.EXECUTION:
            self.execution_blocks.append(block)
        else:
            self.setup_blocks.append(block)

    def get_current_phase(self) -> Optional[TestPhase]:
        """Get the current test phase."""
        return self._current_phase

    @staticmethod
    def __get_pydantic_core_schema__(
        source_type: Any, handler: GetCoreSchemaHandler
    ) -> PlainValidatorFunctionSchema:
        """Pydantic schema for TestPhaseManager."""

        def validate_test_phase_manager(value):
            """Return the TestPhaseManager instance as-is."""
            if isinstance(value, source_type):
                return value
            return source_type()

        return no_info_plain_validator_function(
            validate_test_phase_manager,
        )
