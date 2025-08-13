"""List of all transition fork definitions."""

from ..transition_base_fork import transition_fork
from .forks import Berlin, Cancun, London, Osaka, Paris, Prague, Shanghai
from .forks import OsakaBPO1, OsakaBPO2, OsakaBPO3, OsakaBPO4, OsakaBPO5


# Transition Forks
@transition_fork(to_fork=London, at_block=5)
class BerlinToLondonAt5(Berlin):
    """Berlin to London transition at Block 5."""

    pass


@transition_fork(to_fork=Shanghai, at_timestamp=15_000)
class ParisToShanghaiAtTime15k(Paris):
    """Paris to Shanghai transition at Timestamp 15k."""

    pass


@transition_fork(to_fork=Cancun, at_timestamp=15_000)
class ShanghaiToCancunAtTime15k(Shanghai):
    """Shanghai to Cancun transition at Timestamp 15k."""

    pass


@transition_fork(to_fork=Prague, at_timestamp=15_000)
class CancunToPragueAtTime15k(Cancun):
    """Cancun to Prague transition at Timestamp 15k."""

    pass


@transition_fork(to_fork=Osaka, at_timestamp=15_000)
class PragueToOsakaAtTime15k(Prague):
    """Prague to Osaka transition at Timestamp 15k."""

    pass


# Temporary Osaka BPO Transition Fork
@transition_fork(to_fork=BPO1, at_timestamp=15_000)
class OsakaToBPO1AtTime15k(Osaka):
    """Osaka to BPO1 transition at Timestamp 15k."""
    pass
