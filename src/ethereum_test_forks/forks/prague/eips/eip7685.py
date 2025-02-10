"""EIP-7685 definition."""

from typing import List

from ....base_eip import BaseEIP


class EIP7685(BaseEIP, fork="Prague"):
    """
    EIP-7685: General purpose execution layer requests.

    A general purpose bus for sharing EL triggered requests with the CL.
    """

    @classmethod
    def header_fields_required(cls) -> List[str]:
        """Return header fields required by this EIP."""
        return ["requests_hash"]
