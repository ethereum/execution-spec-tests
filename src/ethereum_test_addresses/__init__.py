"""
Addresses of pre-compiles and system contracts on Ethereum mainnet and testnets.
"""

from .precompiles import Precompile
from .system_contracts import SystemContract

SYSTEM_ADDRESS = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE

__all__ = [
    "Precompile",
    "SystemContract",
    "SYSTEM_ADDRESS",
]
