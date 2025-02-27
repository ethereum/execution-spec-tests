"""London fork definition including transition from Berlin."""

from typing import List

from ethereum_test_vm import Opcodes

from ...transition_base_fork import transition_fork
from ..berlin.fork import Berlin


class London(Berlin):
    """London fork."""

    @classmethod
    def header_base_fee_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Header must contain the Base Fee starting from London."""
        return True

    @classmethod
    def tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """At London, dynamic fee transactions are introduced."""
        return [2] + super(London, cls).tx_types(block_number, timestamp)

    @classmethod
    def contract_creating_tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """At London, dynamic fee transactions are introduced."""
        return [2] + super(London, cls).contract_creating_tx_types(block_number, timestamp)

    @classmethod
    def valid_opcodes(
        cls,
    ) -> List[Opcodes]:
        """Return list of Opcodes that are valid to work on this fork."""
        return [Opcodes.BASEFEE] + super(London, cls).valid_opcodes()


@transition_fork(to_fork=London, at_block=5)
class BerlinToLondonAt5(Berlin):
    """Berlin to London transition fork."""

    pass
