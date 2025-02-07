"""Byzantium fork definition."""

from typing import List, Tuple

from ethereum_test_base_types import Address
from ethereum_test_forks.forks.homestead.fork import Homestead
from ethereum_test_vm import EVMCodeType, Opcodes


class Byzantium(Homestead):
    """Byzantium fork."""

    @classmethod
    def get_reward(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """
        At Byzantium, the block reward is reduced to
        3_000_000_000_000_000_000 wei.
        """
        return 3_000_000_000_000_000_000

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """
        At Byzantium, pre-compiles for bigint modular exponentiation, addition and scalar
        multiplication on elliptic curve alt_bn128, and optimal ate pairing check on
        elliptic curve alt_bn128 are introduced.
        """
        return [Address(i) for i in range(5, 9)] + super(Byzantium, cls).precompiles(
            block_number, timestamp
        )

    @classmethod
    def call_opcodes(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> List[Tuple[Opcodes, EVMCodeType]]:
        """At Byzantium, STATICCALL opcode was introduced."""
        return [(Opcodes.STATICCALL, EVMCodeType.LEGACY)] + super(Byzantium, cls).call_opcodes(
            block_number, timestamp
        )

    @classmethod
    def valid_opcodes(
        cls,
    ) -> List[Opcodes]:
        """Return list of Opcodes that are valid to work on this fork."""
        return [Opcodes.RETURNDATASIZE, Opcodes.STATICCALL] + super(Byzantium, cls).valid_opcodes()
