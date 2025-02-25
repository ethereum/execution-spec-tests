"""Test spec definitions and utilities."""

from typing import List, Type

from .base import BaseTest, TestSpec
from .blockchain import (
    BlockchainTest,
    BlockchainTestFiller,
    BlockchainTestSpec,
)
from .config import ConfigTest, ConfigTestFiller, ConfigTestSpec
from .eof import (
    EOFStateTest,
    EOFStateTestFiller,
    EOFStateTestSpec,
    EOFTest,
    EOFTestFiller,
    EOFTestSpec,
)
from .state import StateTest, StateTestFiller, StateTestSpec
from .transaction import TransactionTest, TransactionTestFiller, TransactionTestSpec

SPEC_TYPES: List[Type[BaseTest]] = [
    BlockchainTest,
    ConfigTest,
    EOFStateTest,
    EOFTest,
    StateTest,
    TransactionTest,
]


__all__ = (
    "SPEC_TYPES",
    "BaseTest",
    "BlockchainTest",
    "BlockchainTestEngineFiller",
    "BlockchainTestEngineSpec",
    "BlockchainTestFiller",
    "BlockchainTestSpec",
    "ConfigTest",
    "ConfigTestFiller",
    "ConfigTestSpec",
    "EOFStateTest",
    "EOFStateTestFiller",
    "EOFStateTestSpec",
    "EOFTest",
    "EOFTestFiller",
    "EOFTestSpec",
    "StateTest",
    "StateTestFiller",
    "StateTestSpec",
    "TestSpec",
    "TransactionTest",
    "TransactionTestFiller",
    "TransactionTestSpec",
)
