"""Prague fork definition including transition fork from Cancun."""

from typing import Optional

from semver import Version

from ...compose_fork import compose_fork
from ...transition_base_fork import transition_fork
from ..cancun.fork import Cancun
from .eips import (
    EIP2537,
    EIP2935,
    EIP6110,
    EIP7002,
    EIP7251,
    EIP7623,
    EIP7685,
    EIP7691,
    EIP7702,
    EIP7840,
)


@compose_fork(
    EIP2537, EIP2935, EIP6110, EIP7002, EIP7251, EIP7623, EIP7685, EIP7691, EIP7702, EIP7840
)
class Prague(Cancun):
    """Prague fork."""

    @classmethod
    def is_deployed(cls) -> bool:
        """Flag that the fork has not been deployed to mainnet."""
        return False

    @classmethod
    def solc_min_version(cls) -> Version:
        """Return minimum version of solc that supports this fork."""
        return Version.parse("1.0.0")  # set a high version; currently unknown

    @classmethod
    def header_requests_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """
        Prague requires that the execution layer header contains the beacon chain
        requests hash.
        """
        return True

    @classmethod
    def engine_new_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """From Prague, new payload calls must use version 4."""
        return 4

    @classmethod
    def engine_forkchoice_updated_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """At Prague, version number of NewPayload and ForkchoiceUpdated diverge."""
        return 3

    @classmethod
    def max_request_type(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """At Prague, three request types are introduced, hence the max request type is 2."""
        request_types = [
            int(EIP6110.DEPOSIT_REQUEST_TYPE),
            int(EIP7002.WITHDRAWAL_REQUEST_TYPE),
            int(EIP7251.CONSOLIDATION_REQUEST_TYPE),
        ]
        return max(request_types)


@transition_fork(to_fork=Prague, at_timestamp=15_000)
class CancunToPragueAtTime15k(Cancun):
    """Cancun to Prague transition fork."""

    pass
