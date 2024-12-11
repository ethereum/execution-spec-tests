"""
Helpers for testing EIP-7623.
"""

from enum import Enum, auto


class DataTestType(Enum):
    """
    Enum for the different types of data tests.
    """

    FLOOR_GAS_COST_LESS_THAN_OR_EQUAL_TO_INTRINSIC_GAS = auto()
    FLOOR_GAS_COST_GREATER_THAN_INTRINSIC_GAS = auto()


class GasTestType(Enum):
    """
    Enum for the different types of gas tests.
    """

    CONSUME_ZERO_GAS = auto()
    CONSUME_ALL_GAS = auto()
    CONSUME_ALL_GAS_WITH_REFUND = auto()
