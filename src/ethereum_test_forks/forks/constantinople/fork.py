"""Constantinople fork definition."""

from typing import List, Tuple

from ethereum_test_vm import EVMCodeType, Opcodes

from ..byzantium.fork import Byzantium


class Constantinople(Byzantium):
    """Constantinople fork."""

    @classmethod
    def get_reward(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """
        At Constantinople, the block reward is reduced to
        2_000_000_000_000_000_000 wei.
        """
        return 2_000_000_000_000_000_000

    @classmethod
    def create_opcodes(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> List[Tuple[Opcodes, EVMCodeType]]:
        """At Constantinople, `CREATE2` opcode is added."""
        return [(Opcodes.CREATE2, EVMCodeType.LEGACY)] + super(Constantinople, cls).create_opcodes(
            block_number, timestamp
        )

    @classmethod
    def valid_opcodes(
        cls,
    ) -> List[Opcodes]:
        """Return list of Opcodes that are valid to work on this fork."""
        return [
            Opcodes.SHL,
            Opcodes.SHR,
            Opcodes.SAR,
            Opcodes.EXTCODEHASH,
            Opcodes.CREATE2,
        ] + super(Constantinople, cls).valid_opcodes()
