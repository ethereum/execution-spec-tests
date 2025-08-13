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


# Temporary Osaka BPO Transition Forks
@transition_fork(to_fork=OsakaBPO1, at_timestamp=10_000)
class OsakaToOsakaBPO1AtTime10k(Osaka):
    """Osaka to OsakaBPO1 transition at Timestamp 10k."""
    pass

@transition_fork(to_fork=OsakaBPO2, at_timestamp=20_000)
class OsakaBPO1ToOsakaBPO2AtTime20k(OsakaBPO1):
    """OsakaBPO1 to OsakaBPO2 transition at Timestamp 20k."""
    pass

@transition_fork(to_fork=OsakaBPO3, at_timestamp=30_000)
class OsakaBPO2ToOsakaBPO3AtTime30k(OsakaBPO2):
    """OsakaBPO2 to OsakaBPO3 transition at Timestamp 30k."""
    pass

@transition_fork(to_fork=OsakaBPO4, at_timestamp=40_000)
class OsakaBPO3ToOsakaBPO4AtTime40k(OsakaBPO3):
    """OsakaBPO3 to OsakaBPO4 transition at Timestamp 40k."""
    pass

@transition_fork(to_fork=OsakaBPO5, at_timestamp=50_000)
class OsakaBPO4ToOsakaBPO5AtTime50k(OsakaBPO4):
    """OsakaBPO4 to OsakaBPO5 transition at Timestamp 50k."""
    pass