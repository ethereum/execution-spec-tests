"""Istanbul fork definition."""

from dataclasses import replace
from typing import List

from ethereum_test_base_types import Address
from ethereum_test_forks.forks.constantinople_fix.fork import ConstantinopleFix
from ethereum_test_forks.gas_costs import GasCosts
from ethereum_test_vm import Opcodes


class Istanbul(ConstantinopleFix):
    """Istanbul fork."""

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """At Istanbul, pre-compile for blake2 compression is introduced."""
        return [Address(9)] + super(Istanbul, cls).precompiles(block_number, timestamp)

    @classmethod
    def valid_opcodes(
        cls,
    ) -> List[Opcodes]:
        """Return list of Opcodes that are valid to work on this fork."""
        return [Opcodes.CHAINID, Opcodes.SELFBALANCE] + super(Istanbul, cls).valid_opcodes()

    @classmethod
    def gas_costs(cls, block_number: int = 0, timestamp: int = 0) -> GasCosts:
        """
        On Istanbul, the non-zero transaction data byte cost is reduced to 16 due to
        EIP-2028.
        """
        return replace(
            super(Istanbul, cls).gas_costs(block_number, timestamp),
            G_TX_DATA_NON_ZERO=16,  # https://eips.ethereum.org/EIPS/eip-2028
        )
