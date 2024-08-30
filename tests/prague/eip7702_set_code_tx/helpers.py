"""
Helper types, functions and classes for testing EIP-7702 Set Code Transaction.
"""

from enum import Enum, auto


class ChainIDType(Enum):
    """
    Different types of chain IDs used in the authorization list.
    """

    GENERIC = auto()
    CHAIN_SPECIFIC = auto()
