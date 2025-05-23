"""Ethereum test fork definitions."""

from typing import Literal

from .base_fork import Fork, ForkAttribute
from .forks.forks import (
    ArrowGlacier,
    Berlin,
    Byzantium,
    Cancun,
    Constantinople,
    ConstantinopleFix,
    EOFv1,
    Frontier,
    GrayGlacier,
    Homestead,
    Istanbul,
    London,
    MuirGlacier,
    Osaka,
    Paris,
    Prague,
    Shanghai,
)
from .forks.transition import (
    BerlinToLondonAt5,
    CancunToPragueAtTime15k,
    ParisToShanghaiAtTime15k,
    ShanghaiToCancunAtTime15k,
)
from .gas_costs import GasCosts
from .helpers import (
    ForkRangeDescriptor,
    InvalidForkError,
    forks_from,
    forks_from_until,
    get_closest_fork_with_solc_support,
    get_deployed_forks,
    get_development_forks,
    get_fork_by_name,
    get_forks,
    get_forks_with_no_descendants,
    get_forks_with_no_parents,
    get_forks_with_solc_support,
    get_forks_without_solc_support,
    get_from_until_fork_set,
    get_last_descendants,
    get_relative_fork_markers,
    get_transition_fork_predecessor,
    get_transition_fork_successor,
    get_transition_forks,
    transition_fork_from_to,
    transition_fork_to,
)

__all__ = [
    "Fork",
    "ForkAttribute",
    "ArrowGlacier",
    "Berlin",
    "BerlinToLondonAt5",
    "Byzantium",
    "Constantinople",
    "ConstantinopleFix",
    "EOFv1",
    "ForkRangeDescriptor",
    "Frontier",
    "GrayGlacier",
    "Homestead",
    "InvalidForkError",
    "Istanbul",
    "London",
    "Paris",
    "ParisToShanghaiAtTime15k",
    "MuirGlacier",
    "Shanghai",
    "ShanghaiToCancunAtTime15k",
    "Cancun",
    "CancunToPragueAtTime15k",
    "Prague",
    "Osaka",
    "get_transition_forks",
    "forks_from",
    "forks_from_until",
    "get_closest_fork_with_solc_support",
    "get_deployed_forks",
    "get_development_forks",
    "get_transition_fork_predecessor",
    "get_transition_fork_successor",
    "get_fork_by_name",
    "get_forks_with_no_descendants",
    "get_forks_with_no_parents",
    "get_forks_with_solc_support",
    "get_forks_without_solc_support",
    "get_relative_fork_markers",
    "get_forks",
    "get_from_until_fork_set",
    "get_last_descendants",
    "transition_fork_from_to",
    "transition_fork_to",
    "GasCosts",
]

# blob-related constants
FIELD_ELEMENTS_PER_BLOB = 4096
BYTES_PER_FIELD_ELEMENT = 32
BYTES_PER_BLOB = FIELD_ELEMENTS_PER_BLOB * BYTES_PER_FIELD_ELEMENT  # 131072
CELL_LENGTH = 2048
BLS_MODULUS = 0x73EDA753299D7D483339D80809A1D80553BDA402FFFE5BFEFFFFFFFF00000001  # EIP-2537: Main subgroup order = q  # noqa: E501
#       due to BLS_MODULUS every blob byte (uint256) must be smaller than 116

#       deneb constants that have not changed (https://github.com/ethereum/consensus-specs/blob/cc6996c22692d70e41b7a453d925172ee4b719ad/specs/deneb/polynomial-commitments.md?plain=1#L78)
BYTES_PER_PROOF = 48
BYTES_PER_COMMITMENT = 48
KZG_ENDIANNESS: Literal["big"] = "big"

#       eip-7691
MAX_BLOBS_PER_BLOCK_ELECTRA = 9
TARGET_BLOBS_PER_BLOCK_ELECTRA = 6
MAX_BLOB_GAS_PER_BLOCK = 1179648
TARGET_BLOB_GAS_PER_BLOCK = 786432
BLOB_BASE_FEE_UPDATE_FRACTION_PRAGUE = 5007716
