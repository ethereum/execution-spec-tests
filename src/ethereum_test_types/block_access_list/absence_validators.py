"""
Absence validator functions for BAL testing.

This module provides validator functions that check for the absence of specific
changes in Block Access Lists. These validators are used with the
``should_not_exist`` field in BalAccountExpectation to ensure certain changes
do *not* occur.

All validator functions must be decorated with
``@validate_call(validate_return=True)`` to ensure proper type validation.
This is enforced via tests.
"""

from typing import Set

from pydantic import validate_call

from ethereum_test_base_types import Number, StorageKey

from . import AbsenceValidator, BalAccountChange


@validate_call(validate_return=True)
def no_nonce_changes(tx_indices: Set[Number] | None = None) -> AbsenceValidator:
    """
    Forbid nonce changes at specified transaction indices or all indices if None.

    Args:
        tx_indices: Set of transaction indices to check. If None,
        checks all transactions.

    """

    def check(account: BalAccountChange) -> None:
        for nonce_change in account.nonce_changes:
            if tx_indices is None or nonce_change.tx_index in tx_indices:
                raise AssertionError(
                    f"Unexpected nonce change found at tx {nonce_change.tx_index}"
                )

    return check


@validate_call(validate_return=True)
def no_balance_changes(tx_indices: Set[Number] | None = None) -> AbsenceValidator:
    """
    Forbid balance changes at specified transaction indices or all indices
    if None.

    Args:
        tx_indices: Set of transaction indices to check. If None,
        checks all transactions.

    """

    def check(account: BalAccountChange) -> None:
        for balance_change in account.balance_changes:
            if tx_indices is None or balance_change.tx_index in tx_indices:
                raise AssertionError(
                    f"Unexpected balance change found at tx {balance_change.tx_index}"
                )

    return check


@validate_call(validate_return=True)
def no_storage_changes(
    slots: Set[StorageKey] | None = None,
    tx_indices: Set[Number] | None = None,
) -> AbsenceValidator:
    """
    Forbid storage changes at specified slots and/or transaction indices.

    Args:
        slots: Set of storage slots to check. If None, checks all slots.
        tx_indices: Set of transaction indices to check. If None,
        checks all transactions.

    """

    def check(account: BalAccountChange) -> None:
        for storage_slot in account.storage_changes:
            if slots is None or storage_slot.slot in slots:
                for slot_change in storage_slot.slot_changes:
                    if tx_indices is None or slot_change.tx_index in tx_indices:
                        raise AssertionError(
                            "Unexpected storage change found at slot "
                            f"{storage_slot.slot} in tx "
                            f"{slot_change.tx_index}"
                        )

    return check


@validate_call(validate_return=True)
def no_storage_reads(slots: Set[StorageKey] | None = None) -> AbsenceValidator:
    """
    Forbid storage reads at specified slots or all slots if None.

    Args:
        slots: Set of storage slots to check. If None, checks all slots.

    """

    def check(account: BalAccountChange) -> None:
        for read_slot in account.storage_reads:
            if slots is None or read_slot in slots:
                raise AssertionError(f"Unexpected storage read found at slot {read_slot}")

    return check


@validate_call(validate_return=True)
def no_code_changes(tx_indices: Set[Number] | None = None) -> AbsenceValidator:
    """
    Forbid code changes at specified transaction indices or all indices
    if None.

    Args:
        tx_indices: Set of transaction indices to check. If None,
        checks all transactions.

    """

    def check(account: BalAccountChange) -> None:
        for code_change in account.code_changes:
            if tx_indices is None or code_change.tx_index in tx_indices:
                raise AssertionError(f"Unexpected code change found at tx {code_change.tx_index}")

    return check


__all__ = [
    "AbsenceValidator",
    "no_nonce_changes",
    "no_balance_changes",
    "no_storage_changes",
    "no_storage_reads",
    "no_code_changes",
]
