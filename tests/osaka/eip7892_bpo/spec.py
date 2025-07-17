"""Defines EIP-7892 specification constants and functions."""

from dataclasses import dataclass

# Base the spec on EIP-4844 which EIP-7892 extends
from ...cancun.eip4844_blobs.spec import Spec as EIP4844Spec


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_7892 = ReferenceSpec("EIPS/eip-7892.md", "e42c14f83052bfaa8c38832dcbc46e357dd1a1d9")


@dataclass(frozen=True)
class Spec(EIP4844Spec):
    """Parameters from the EIP-7892 specifications."""

    pass
