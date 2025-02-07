"""Shanghai fork definition."""

from typing import List, Optional

from ethereum_test_forks import Paris
from ethereum_test_vm import Opcodes


class Shanghai(Paris):
    """Shanghai fork."""

    @classmethod
    def header_withdrawals_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Withdrawals are required starting from Shanghai."""
        return True

    @classmethod
    def engine_new_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """From Shanghai, new payload calls must use version 2."""
        return 2

    @classmethod
    def valid_opcodes(cls) -> List[Opcodes]:
        """
        Return list of Opcodes that are valid to work on this fork.
        Shanghai adds PUSH0 opcode.
        """
        return [Opcodes.PUSH0] + super().valid_opcodes()
