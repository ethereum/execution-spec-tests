"""
BalAccountAbsentValues class for BAL testing.

This module provides a unified class for specifying explicit absent values in Block Access Lists.
This class uses the same change classes as BalAccountChanges to specify specific values that
should NOT exist in the BAL. For checking complete absence, use BalAccountExpectation
with empty lists instead.
"""

from typing import List

from pydantic import Field, model_validator

from ethereum_test_base_types import CamelModel, StorageKey

from .account_changes import (
    BalAccountChange,
    BalBalanceChange,
    BalCodeChange,
    BalNonceChange,
    BalStorageSlot,
)
from .exceptions import BlockAccessListValidationError

EMPTY_LIST_ERROR_MSG = (
    "Empty lists are not allowed. This would mean 'check for any change' and "
    "is bad practice. Instead, use the `BalAccountExpectation` to define "
    "explicit, expected changes."
)


class BalAccountAbsentValues(CamelModel):
    """
    Represents explicit absent value expectations for a specific account in a block.

    This class specifies specific changes that should NOT exist in the BAL for a
    given account.

    IMPORTANT: This class is for checking that specific values are absent, NOT for
    checking that entire categories are empty. For complete absence checks
    (e.g., "no nonce changes at all"), use BalAccountExpectation with empty lists
    instead.

    The validation works by checking that none of the specified explicit changes
    exist in the actual BAL.

    Example:
        # Forbid specific nonce change at tx 1 with post_nonce=5, and specific
        # storage change
        absent_values = BalAccountAbsentValues(
            nonce_changes=[
                # Forbid exact nonce change at this tx
                BalNonceChange(tx_index=1, post_nonce=5),
            ],
            storage_changes=[
                BalStorageSlot(
                    slot=0x42,
                    slot_changes=[
                        # Forbid exact storage change at this slot and tx
                        BalStorageChange(tx_index=2, post_value=0x99)
                    ],
                )
            ],
        )

    For checking complete absence:
        # Use BalAccountExpectation with empty lists instead
        expectation = BalAccountExpectation(
            nonce_changes=[],  # Expect NO nonce changes at all
            storage_changes=[],  # Expect NO storage changes at all
        )

    """

    nonce_changes: List[BalNonceChange] = Field(
        default_factory=list,
        description="List of nonce changes that should NOT exist in the BAL. "
        "Validates that none of these changes are present.",
    )
    balance_changes: List[BalBalanceChange] = Field(
        default_factory=list,
        description="List of balance changes that should NOT exist in the BAL. "
        "Validates that none of these changes are present.",
    )
    code_changes: List[BalCodeChange] = Field(
        default_factory=list,
        description="List of code changes that should NOT exist in the BAL. "
        "Validates that none of these changes are present.",
    )
    storage_changes: List[BalStorageSlot] = Field(
        default_factory=list,
        description="List of storage slots/changes that should NOT exist in the BAL. "
        "Validates that none of these changes are present.",
    )
    storage_reads: List[StorageKey] = Field(
        default_factory=list,
        description="List of storage slots that should NOT be read.",
    )

    @model_validator(mode="after")
    def validate_specific_absences_only(self) -> "BalAccountAbsentValues":
        """Ensure absence fields contain specific values, not empty checks."""
        # at least one field must have content
        if not any(
            [
                self.nonce_changes,
                self.balance_changes,
                self.code_changes,
                self.storage_changes,
                self.storage_reads,
            ]
        ):
            raise ValueError(
                "At least one absence field must be specified. "
                "`BalAccountAbsentValues` is for checking specific forbidden values. "
                f"{EMPTY_LIST_ERROR_MSG}"
            )

        # check that no fields are explicitly set to empty lists
        field_checks = [
            ("nonce_changes", self.nonce_changes),
            ("balance_changes", self.balance_changes),
            ("code_changes", self.code_changes),
            ("storage_changes", self.storage_changes),
            ("storage_reads", self.storage_reads),
        ]

        for field_name, field_value in field_checks:
            if field_name in self.model_fields_set and field_value == []:
                raise ValueError(
                    f"`BalAccountAbsentValues.{field_name}` cannot be an empty list. "
                    f"{EMPTY_LIST_ERROR_MSG}"
                )

        # validate that storage_changes don't have empty slot_changes
        for storage_slot in self.storage_changes:
            if not storage_slot.slot_changes:
                raise ValueError(
                    f"`BalAccountAbsentValues.storage_changes[{storage_slot.slot}].slot_changes` "
                    f"cannot be an empty list. {EMPTY_LIST_ERROR_MSG}"
                )

        return self

    def validate_against(self, account: BalAccountChange) -> None:
        """
        Validate that the account does not contain the forbidden changes specified in
        this object.

        Args:
            account: The BalAccountChange to validate against

        Raises:
            BlockAccessListValidationError: If any forbidden changes are found

        """
        for forbidden_nonce in self.nonce_changes:
            for actual_nonce in account.nonce_changes:
                if (
                    actual_nonce.tx_index == forbidden_nonce.tx_index
                    and actual_nonce.post_nonce == forbidden_nonce.post_nonce
                ):
                    raise BlockAccessListValidationError(
                        f"Unexpected nonce change found at tx {actual_nonce.tx_index}"
                    )

        for forbidden_balance in self.balance_changes:
            for actual_balance in account.balance_changes:
                if (
                    actual_balance.tx_index == forbidden_balance.tx_index
                    and actual_balance.post_balance == forbidden_balance.post_balance
                ):
                    raise BlockAccessListValidationError(
                        f"Unexpected balance change found at tx {actual_balance.tx_index}"
                    )

        for forbidden_code in self.code_changes:
            for actual_code in account.code_changes:
                if (
                    actual_code.tx_index == forbidden_code.tx_index
                    and actual_code.new_code == forbidden_code.new_code
                ):
                    raise BlockAccessListValidationError(
                        f"Unexpected code change found at tx {actual_code.tx_index}"
                    )

        for forbidden_storage_slot in self.storage_changes:
            for actual_storage_slot in account.storage_changes:
                if actual_storage_slot.slot == forbidden_storage_slot.slot:
                    # Check specific slot changes only (empty slot_changes not allowed)
                    for forbidden_slot_change in forbidden_storage_slot.slot_changes:
                        for actual_slot_change in actual_storage_slot.slot_changes:
                            if (
                                actual_slot_change.tx_index == forbidden_slot_change.tx_index
                                and actual_slot_change.post_value
                                == forbidden_slot_change.post_value
                            ):
                                raise BlockAccessListValidationError(
                                    f"Unexpected storage change found at slot "
                                    f"{actual_storage_slot.slot} in tx "
                                    f"{actual_slot_change.tx_index}"
                                )

        for forbidden_read in self.storage_reads:
            for actual_read in account.storage_reads:
                if actual_read == forbidden_read:
                    raise BlockAccessListValidationError(
                        f"Unexpected storage read found at slot {actual_read}"
                    )


__all__ = [
    "BalAccountAbsentValues",
]
