"""EIP-7685 definition."""

from typing import List

from ethereum_test_forks.base_eip import EIP, BaseEIP
from ethereum_test_forks.eips import EIP6110, EIP7002, EIP7251


class EIP7685(BaseEIP, fork="Prague"):
    """
    EIP-7685: General purpose execution layer requests.

    A general purpose bus for sharing EL triggered requests with the CL.
    """

    @classmethod
    def header_fields_required(cls) -> List[str]:
        """Return header fields required by this EIP."""
        return ["requests_hash"]

    @classmethod
    def required_eips(cls) -> List[EIP]:
        """Return list of EIPs that must be enabled for this EIP to work."""
        return [
            EIP6110,  # Beacon chain deposit request contract
            EIP7002,  # Beacon chain withdrawal request contract
            EIP7251,  # Beacon chain consolidation request contract
        ]
