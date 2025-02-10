"""Listings of all current post-merge, upcoming, and custom forks."""

from .arrow_glacier.fork import ArrowGlacier
from .berlin.fork import Berlin
from .byzantium.fork import Byzantium
from .cancun.fork import Cancun
from .constantinople.fork import Constantinople
from .constantinople_fix.fork import ConstantinopleFix
from .custom import CancunEIP7692
from .frontier.fork import Frontier
from .gray_glacier.fork import GrayGlacier
from .homestead.fork import Homestead
from .istanbul.fork import Istanbul
from .london.fork import London
from .muir_glacier.fork import MuirGlacier
from .osaka.fork import Osaka
from .paris.fork import Paris
from .prague.eips import (
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
from .prague.fork import Prague
from .shanghai.fork import Shanghai

__all__ = [
    "EIP2537",
    "EIP2935",
    "EIP6110",
    "EIP7002",
    "EIP7251",
    "EIP7623",
    "EIP7685",
    "EIP7691",
    "EIP7702",
    "EIP7840",
    "Cancun",
    "Prague",
    "Osaka",
    "Shanghai",
    "Paris",
    "ArrowGlacier",
    "Berlin",
    "Byzantium",
    "Constantinople",
    "ConstantinopleFix",
    "Frontier",
    "GrayGlacier",
    "Homestead",
    "Istanbul",
    "London",
    "MuirGlacier",
    "CancunEIP7692",
]
