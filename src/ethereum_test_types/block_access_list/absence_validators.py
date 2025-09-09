"""
Absence validator functions for BAL testing.

This module provides validator functions that check for the absence of specific
changes in Block Access Lists. These validators are used with the `must_not_exist`
field in BalAccountExpectation to ensure certain changes do NOT occur.

Note: It's important to use ``@validate_call`` on these functions to ensure proper
argument validation for comparison.
"""

from pydantic import validate_call

from ethereum_test_base_types import Number, StorageKey

from . import AbsenceValidator, BalAccountChange


@validate_call
def nonce_changes_at_tx(*tx_indices: Number) -> AbsenceValidator:
    """Forbid nonce changes at specified transaction indices."""
    tx_set = set(tx_indices)

    def check(account: BalAccountChange) -> None:
        for nonce_change in account.nonce_changes:
            if nonce_change.tx_index in tx_set:
                raise AssertionError(
                    f"Unexpected nonce change found at tx {nonce_change.tx_index}"
                )

    return check


@validate_call
def balance_changes_at_tx(*tx_indices: Number) -> AbsenceValidator:
    """Forbid balance changes at specified transaction indices."""
    tx_set = set(tx_indices)

    def check(account: BalAccountChange) -> None:
        for balance_change in account.balance_changes:
            if balance_change.tx_index in tx_set:
                raise AssertionError(
                    f"Unexpected balance change found at tx {balance_change.tx_index}"
                )

    return check


@validate_call
def storage_changes_at_slots(*slots: StorageKey) -> AbsenceValidator:
    """Forbid storage changes at specified slots."""
    slots_set = set(slots)

    def check(account: BalAccountChange) -> None:
        for storage_slot in account.storage_changes:
            if storage_slot.slot in slots_set:
                raise AssertionError(
                    f"Unexpected storage change found at slot {storage_slot.slot}"
                )

    return check


@validate_call
def storage_reads_at_slots(*slots: StorageKey) -> AbsenceValidator:
    """Forbid storage reads at specified slots."""
    slots_set = set(slots)

    def check(account: BalAccountChange) -> None:
        for read_slot in account.storage_reads:
            if read_slot in slots_set:
                raise AssertionError(f"Unexpected storage read found at slot {read_slot}")

    return check


@validate_call
def code_changes_at_tx(*tx_indices: Number) -> AbsenceValidator:
    """Forbid code changes at specified transaction indices."""
    tx_set = set(tx_indices)

    def check(account: BalAccountChange) -> None:
        for code_change in account.code_changes:
            if code_change.tx_index in tx_set:
                raise AssertionError(f"Unexpected code change found at tx {code_change.tx_index}")

    return check


__all__ = [
    "AbsenceValidator",
    "nonce_changes_at_tx",
    "balance_changes_at_tx",
    "storage_changes_at_slots",
    "storage_reads_at_slots",
    "code_changes_at_tx",
]
