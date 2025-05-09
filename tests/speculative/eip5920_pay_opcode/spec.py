"""Defines EIP-5920 specification constants and functions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_5920 = ReferenceSpec("EIPS/eip-5920.md", "5840c325ea0daccf4cb9c00cda65f224f4df3b0a")


@dataclass(frozen=True)
class Spec:
    """Constants and gas‑cost helpers for the PAY opcode (EIP‑5920)."""

    WARM_STORAGE_READ_COST: int = 100
    COLD_ACCOUNT_ACCESS_COST: int = 2_600
    GAS_NEW_ACCOUNT: int = 25_000
    GAS_CALL_VALUE: int = 9_000

    @staticmethod
    def pay_gas(
        *,
        is_addr_warm: bool,
        addr_exists: bool,
        value: int,
    ) -> int:
        """Return total gas cost for a PAY execution."""
        cost = Spec.WARM_STORAGE_READ_COST if is_addr_warm else Spec.COLD_ACCOUNT_ACCESS_COST
        if not addr_exists and value != 0:
            cost += Spec.GAS_NEW_ACCOUNT
        if value != 0:
            cost += Spec.GAS_CALL_VALUE
        return cost
