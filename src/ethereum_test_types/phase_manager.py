"""Test phase management for Ethereum tests."""

from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum
from typing import Iterator, Optional

from pydantic import BaseModel


class TestPhase(Enum):
    """Test phase for state and blockchain tests."""

    SETUP = "setup"
    EXECUTION = "execution"


_current_phase: ContextVar[Optional[TestPhase]] = ContextVar("test_phase", default=TestPhase.SETUP)


class TestPhaseManager(BaseModel):
    """
    Manages test phases and collects transactions and blocks by phase.
    This class provides a mechanism for tracking "setup" and "execution" phases,
    Only supports "setup" and "execution" phases now.
    """

    model_config = {"arbitrary_types_allowed": True}

    setup_transactions: list = []
    setup_blocks: list = []
    execution_transactions: list = []
    execution_blocks: list = []

    def __init__(self, **data):
        """Initialize the TestPhaseManager with empty transaction and block lists."""
        super().__init__(**data)
        self.setup_transactions = []
        self.setup_blocks = []
        self.execution_transactions = []
        self.execution_blocks = []

    @contextmanager
    def setup(self) -> Iterator["TestPhaseManager"]:
        """Context manager for the setup phase of a benchmark test."""
        token = _current_phase.set(TestPhase.SETUP)
        try:
            yield self
        finally:
            _current_phase.reset(token)

    @contextmanager
    def execution(self) -> Iterator["TestPhaseManager"]:
        """Context manager for the execution phase of a test."""
        token = _current_phase.set(TestPhase.EXECUTION)
        try:
            yield self
        finally:
            _current_phase.reset(token)

    def add_transaction(self, tx) -> None:
        """Add a transaction to the current phase."""
        current_phase = _current_phase.get()
        tx.test_phase = current_phase

        if current_phase == TestPhase.EXECUTION:
            self.execution_transactions.append(tx)
        else:
            self.setup_transactions.append(tx)

    def add_block(self, block) -> None:
        """Add a block to the current phase."""
        current_phase = _current_phase.get()
        for tx in block.txs:
            tx.test_phase = current_phase

        if current_phase == TestPhase.EXECUTION:
            self.execution_blocks.append(block)
        else:
            self.setup_blocks.append(block)

    def get_current_phase(self) -> Optional[TestPhase]:
        """Get the current test phase."""
        return _current_phase.get()
