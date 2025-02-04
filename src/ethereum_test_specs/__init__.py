"""Test spec definitions and utilities."""

from typing import List, Type

from .base import BaseTest, TestSpec
from .blockchain import (
    BlockchainTest,
    BlockchainTestEngine,
    BlockchainTestEngineFiller,
    BlockchainTestEngineSpec,
    BlockchainTestFiller,
    BlockchainTestSpec,
)
from .eof import (
    EOFStateTest,
    EOFStateTestFiller,
    EOFStateTestSpec,
    EOFTest,
    EOFTestFiller,
    EOFTestSpec,
)
from .payload_building import (
    Payload,
    PayloadBuildingTest,
    PayloadBuildingTestFiller,
    PayloadBuildingTestSpec,
    TransactionWithPost,
)
from .state import StateTest, StateTestFiller, StateTestOnly, StateTestSpec
from .transaction import TransactionTest, TransactionTestFiller, TransactionTestSpec

SPEC_TYPES: List[Type[BaseTest]] = [
    BlockchainTest,
    BlockchainTestEngine,
    EOFStateTest,
    EOFTest,
    PayloadBuildingTest,
    StateTest,
    StateTestOnly,
    TransactionTest,
]


__all__ = (
    "SPEC_TYPES",
    "BaseTest",
    "BlockchainTest",
    "BlockchainTestEngine",
    "BlockchainTestEngineFiller",
    "BlockchainTestEngineSpec",
    "BlockchainTestFiller",
    "BlockchainTestSpec",
    "EOFStateTest",
    "EOFStateTestFiller",
    "EOFStateTestSpec",
    "EOFTest",
    "EOFTestFiller",
    "EOFTestSpec",
    "Payload",
    "PayloadBuildingTest",
    "PayloadBuildingTestFiller",
    "PayloadBuildingTestSpec",
    "StateTest",
    "StateTestFiller",
    "StateTestOnly",
    "StateTestSpec",
    "TestSpec",
    "TransactionTest",
    "TransactionTestFiller",
    "TransactionTestSpec",
    "TransactionWithPost",
)
