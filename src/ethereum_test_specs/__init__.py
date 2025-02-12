"""Test spec definitions and utilities."""

from typing import List, Type

from .base import BaseTest, TestSpec
from .blockchain import (
    BlockchainTest,
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
from .state import StateTest, StateTestFiller, StateTestSpec
from .transaction import TransactionTest, TransactionTestFiller, TransactionTestSpec

SPEC_TYPES: List[Type[BaseTest]] = [
    BlockchainTest,
    EOFStateTest,
    EOFTest,
    PayloadBuildingTest,
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
    "StateTestSpec",
    "TestSpec",
    "TransactionTest",
    "TransactionTestFiller",
    "TransactionTestSpec",
    "TransactionWithPost",
)
