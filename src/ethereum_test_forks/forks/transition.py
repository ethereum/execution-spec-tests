"""
List of all transition fork definitions.
"""

from typing import Dict

from ..transition_base_fork import transition_fork
from .constants import VERKLE_PRE_ALLOCATION
from .forks import Berlin, Cancun, London, Paris, Prague, Shanghai


# Transition Forks
@transition_fork(to_fork=London, at_block=5)
class BerlinToLondonAt5(Berlin):
    """
    Berlin to London transition at Block 5
    """

    pass


@transition_fork(to_fork=Shanghai, at_timestamp=15_000)
class ParisToShanghaiAtTime15k(Paris, blockchain_test_network_name="ParisToShanghaiAtTime15k"):
    """
    Paris to Shanghai transition at Timestamp 15k
    """

    pass


@transition_fork(to_fork=Cancun, at_timestamp=15_000)
class ShanghaiToCancunAtTime15k(Shanghai):
    """
    Shanghai to Cancun transition at Timestamp 15k
    """

    pass


@transition_fork(to_fork=Prague, at_timestamp=32)
class ShanghaiToPragueAtTime32(Shanghai):
    """
    Shanghai to Prague transition at Timestamp 32
    """

    pass


@transition_fork(to_fork=Prague, at_timestamp=1, always_execute=True)
class ShanghaiToPragueVerkleTransition(Shanghai):
    """
    Shanghai to Prague transition at Timestamp 1

    This is a special case where the transition happens on the first block after genesis, used
    to test the MPT to Verkle tree conversion.

    We run all tests with this transition fork.
    """

    @classmethod
    def pre_allocation(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Dict[int, Dict[str, str | int | Dict[int, int]]]:
        """
        Pre-allocates a big state full of accounts and storage to test the MPT to Verkle tree
        conversion.
        """

        return VERKLE_PRE_ALLOCATION | super(Shanghai, cls).pre_allocation(block_number, timestamp)
