"""
Block Access List expectation classes for test validation.

This module contains classes for defining and validating expected BAL values in tests.
"""

from typing import Any, Callable, Dict, List, Optional

from pydantic import Field, PrivateAttr

from ethereum_test_base_types import Address, CamelModel, StorageKey

from .account_absent_values import BalAccountAbsentValues
from .account_changes import (
    BalAccountChange,
    BalBalanceChange,
    BalCodeChange,
    BalNonceChange,
    BalStorageSlot,
    BlockAccessListChangeLists,
)
from .exceptions import BlockAccessListValidationError
from .t8n import BlockAccessList


class BalAccountExpectation(CamelModel):
    """
    Represents expected changes to a specific account in a block.

    Same as BalAccountChange but without the address field, used for expectations.
    """

    nonce_changes: List[BalNonceChange] = Field(
        default_factory=list, description="List of expected nonce changes"
    )
    balance_changes: List[BalBalanceChange] = Field(
        default_factory=list, description="List of expected balance changes"
    )
    code_changes: List[BalCodeChange] = Field(
        default_factory=list, description="List of expected code changes"
    )
    storage_changes: List[BalStorageSlot] = Field(
        default_factory=list, description="List of expected storage changes"
    )
    storage_reads: List[StorageKey] = Field(
        default_factory=list, description="List of expected read storage slots"
    )
    absent_values: Optional[BalAccountAbsentValues] = Field(
        default=None, description="Explicit absent value expectations using BalAccountAbsentValues"
    )


def compose(
    *modifiers: Callable[["BlockAccessList"], "BlockAccessList"],
) -> Callable[["BlockAccessList"], "BlockAccessList"]:
    """Compose multiple modifiers into a single modifier."""

    def composed(bal: BlockAccessList) -> BlockAccessList:
        result = bal
        for modifier in modifiers:
            result = modifier(result)
        return result

    return composed


class BlockAccessListExpectation(CamelModel):
    """
    Block Access List expectation model for test writing.

    This model is used to define expected BAL values in tests. It supports:
    - Partial validation (only checks explicitly set fields)
    - Convenient test syntax with named parameters
    - Verification against actual BAL from t8n
    - Explicit exclusion of addresses (using None values)

    Example:
        # In test definition
        expected_block_access_list = BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)]
                ),
                bob: None,  # Bob should NOT be in the BAL
            }
        )

    """

    model_config = CamelModel.model_config | {"extra": "forbid"}

    account_expectations: Dict[Address, BalAccountExpectation | None] = Field(
        default_factory=dict, description="Expected account changes or exclusions to verify"
    )

    _modifier: Callable[["BlockAccessList"], "BlockAccessList"] | None = PrivateAttr(default=None)

    def modify(
        self, *modifiers: Callable[["BlockAccessList"], "BlockAccessList"]
    ) -> "BlockAccessListExpectation":
        """
        Create a new expectation with a modifier for invalid test cases.

        Args:
            modifiers: One or more functions that take and return a BlockAccessList

        Returns:
            A new BlockAccessListExpectation instance with the modifiers applied

        Example:
            from ethereum_test_types.block_access_list.modifiers import remove_nonces

            expectation = BlockAccessListExpectation(
                account_expectations={...}
            ).modify(remove_nonces(alice))

        """
        new_instance = self.model_copy(deep=True)
        new_instance._modifier = compose(*modifiers)
        return new_instance

    def modify_if_invalid_test(self, t8n_bal: "BlockAccessList") -> "BlockAccessList":
        """
        Apply the modifier to the given BAL if this is an invalid test case.

        Args:
            t8n_bal: The BlockAccessList from t8n tool

        Returns:
            The potentially transformed BlockAccessList for the fixture

        """
        if self._modifier:
            return self._modifier(t8n_bal)
        return t8n_bal

    def verify_against(self, actual_bal: "BlockAccessList") -> None:
        """
        Verify that the actual BAL from the client matches this expected BAL.

        Validation steps:
        1. Validate actual BAL conforms to EIP-7928 ordering requirements
        2. Verify address expectations - presence or explicit absence
        3. Verify expected changes within accounts match actual changes

        Args:
            actual_bal: The BlockAccessList model from the client

        Raises:
            BlockAccessListValidationError: If verification fails

        """
        # validate the actual BAL structure follows EIP-7928 ordering
        self._validate_bal_ordering(actual_bal)

        actual_accounts_by_addr = {acc.address: acc for acc in actual_bal.root}
        for address, expectation in self.account_expectations.items():
            if expectation is None:
                # check explicit exclusion of address when set to `None`
                if address in actual_accounts_by_addr:
                    raise BlockAccessListValidationError(
                        f"Address {address} should not be in BAL but was found"
                    )
            else:
                # check address is present and validate changes
                if address not in actual_accounts_by_addr:
                    raise BlockAccessListValidationError(
                        f"Expected address {address} not found in actual BAL"
                    )

                actual_account = actual_accounts_by_addr[address]
                try:
                    self._compare_account_expectations(expectation, actual_account)
                except AssertionError as e:
                    raise BlockAccessListValidationError(f"Account {address}: {str(e)}") from e

    @staticmethod
    def _validate_bal_ordering(bal: "BlockAccessList") -> None:
        """
        Validate BAL ordering follows EIP-7928 requirements.

        Args:
            bal: The BlockAccessList to validate

        Raises:
            BlockAccessListValidationError: If ordering is invalid

        """
        # Check address ordering (ascending)
        for i in range(1, len(bal.root)):
            if bal.root[i - 1].address >= bal.root[i].address:
                raise BlockAccessListValidationError(
                    f"BAL addresses are not in lexicographic order: "
                    f"{bal.root[i - 1].address} >= {bal.root[i].address}"
                )

        # Check transaction index ordering within accounts
        for account in bal.root:
            change_lists: List[BlockAccessListChangeLists] = [
                account.nonce_changes,
                account.balance_changes,
                account.code_changes,
            ]
            for change_list in change_lists:
                for i in range(1, len(change_list)):
                    if change_list[i - 1].tx_index >= change_list[i].tx_index:
                        raise BlockAccessListValidationError(
                            f"Transaction indices not in ascending order in account "
                            f"{account.address}: {change_list[i - 1].tx_index} >= "
                            f"{change_list[i].tx_index}"
                        )

            # Check storage slot ordering
            for i in range(1, len(account.storage_changes)):
                if account.storage_changes[i - 1].slot >= account.storage_changes[i].slot:
                    raise BlockAccessListValidationError(
                        f"Storage slots not in ascending order in account "
                        f"{account.address}: {account.storage_changes[i - 1].slot} >= "
                        f"{account.storage_changes[i].slot}"
                    )

            # Check transaction index ordering within storage slots
            for storage_slot in account.storage_changes:
                for i in range(1, len(storage_slot.slot_changes)):
                    if (
                        storage_slot.slot_changes[i - 1].tx_index
                        >= storage_slot.slot_changes[i].tx_index
                    ):
                        raise BlockAccessListValidationError(
                            f"Transaction indices not in ascending order in storage slot "
                            f"{storage_slot.slot} of account {account.address}: "
                            f"{storage_slot.slot_changes[i - 1].tx_index} >= "
                            f"{storage_slot.slot_changes[i].tx_index}"
                        )

            # Check storage reads ordering
            for i in range(1, len(account.storage_reads)):
                if account.storage_reads[i - 1] >= account.storage_reads[i]:
                    raise BlockAccessListValidationError(
                        f"Storage reads not in ascending order in account "
                        f"{account.address}: {account.storage_reads[i - 1]} >= "
                        f"{account.storage_reads[i]}"
                    )

    @staticmethod
    def _compare_account_expectations(
        expected: BalAccountExpectation, actual: BalAccountChange
    ) -> None:
        """
        Compare expected and actual account changes using subsequence validation.

        Args:
            expected: The expected account changes
            actual: The actual account changes from the BAL

        Raises:
            AssertionError: If validation fails

        """
        # Check absence expectations first if defined
        if expected.absent_values is not None:
            expected.absent_values.validate_against(actual)

        # Validate expected changes using subsequence validation
        field_pairs: List[tuple[str, Any, Any]] = [
            ("nonce_changes", expected.nonce_changes, actual.nonce_changes),
            ("balance_changes", expected.balance_changes, actual.balance_changes),
            ("code_changes", expected.code_changes, actual.code_changes),
            ("storage_changes", expected.storage_changes, actual.storage_changes),
            ("storage_reads", expected.storage_reads, actual.storage_reads),
        ]

        for field_name, expected_list, actual_list in field_pairs:
            # Only validate fields that were explicitly set
            if field_name not in expected.model_fields_set:
                continue

            if field_name == "storage_reads":
                # storage_reads is a simple list of StorageKey
                actual_idx = 0
                for expected_read in expected_list:
                    found = False
                    while actual_idx < len(actual_list):
                        if actual_list[actual_idx] == expected_read:
                            found = True
                            actual_idx += 1
                            break
                        actual_idx += 1

                    if not found:
                        raise AssertionError(
                            f"Storage read {expected_read} not found or not in correct order. "
                            f"Actual reads: {actual_list}"
                        )

            elif field_name == "storage_changes":
                # storage_changes is a list of BalStorageSlot
                actual_idx = 0
                for expected_slot in expected_list:
                    found = False
                    while actual_idx < len(actual_list):
                        if actual_list[actual_idx].slot == expected_slot.slot:
                            # Found matching slot, now validate slot_changes
                            actual_slot_changes = actual_list[actual_idx].slot_changes
                            expected_slot_changes = expected_slot.slot_changes

                            if not expected_slot_changes:
                                # Empty expected means any slot_changes are acceptable
                                pass
                            else:
                                # Validate slot_changes as subsequence
                                slot_actual_idx = 0
                                for expected_change in expected_slot_changes:
                                    slot_found = False
                                    while slot_actual_idx < len(actual_slot_changes):
                                        actual_change = actual_slot_changes[slot_actual_idx]
                                        if (
                                            actual_change.tx_index == expected_change.tx_index
                                            and actual_change.post_value
                                            == expected_change.post_value
                                        ):
                                            slot_found = True
                                            slot_actual_idx += 1
                                            break
                                        slot_actual_idx += 1

                                    if not slot_found:
                                        raise AssertionError(
                                            f"Storage change {expected_change} not found "
                                            f"or not in correct order in slot "
                                            f"{expected_slot.slot}. "
                                            f"Actual slot changes: {actual_slot_changes}"
                                        )

                            found = True
                            actual_idx += 1
                            break
                        actual_idx += 1

                    if not found:
                        raise AssertionError(
                            f"Storage slot {expected_slot.slot} not found "
                            f"or not in correct order. Actual slots: "
                            f"{[s.slot for s in actual_list]}"
                        )

            else:
                # Handle nonce_changes, balance_changes, code_changes
                if not expected_list and actual_list:
                    # Empty expected but non-empty actual - error
                    item_type = field_name.replace("_changes", "")
                    raise AssertionError(
                        f"Expected {field_name} to be empty but found {actual_list}"
                    )

                else:
                    # Create tuples for comparison (ordering already validated)
                    if field_name == "nonce_changes":
                        expected_tuples = [(c.tx_index, c.post_nonce) for c in expected_list]
                        actual_tuples = [(c.tx_index, c.post_nonce) for c in actual_list]
                        item_type = "nonce"
                    elif field_name == "balance_changes":
                        expected_tuples = [
                            (c.tx_index, int(c.post_balance)) for c in expected_list
                        ]
                        actual_tuples = [(c.tx_index, int(c.post_balance)) for c in actual_list]
                        item_type = "balance"
                    elif field_name == "code_changes":
                        expected_tuples = [(c.tx_index, bytes(c.new_code)) for c in expected_list]
                        actual_tuples = [(c.tx_index, bytes(c.new_code)) for c in actual_list]
                        item_type = "code"
                    else:
                        # sanity check
                        raise ValueError(f"Unexpected field type: {field_name}")

                    # Check that expected forms a subsequence of actual
                    actual_idx = 0
                    for exp_tuple in expected_tuples:
                        found = False
                        while actual_idx < len(actual_tuples):
                            if actual_tuples[actual_idx] == exp_tuple:
                                found = True
                                actual_idx += 1
                                break
                            actual_idx += 1

                        if not found:
                            raise AssertionError(
                                f"{item_type.capitalize()} change {exp_tuple} not found "
                                f"or not in correct order. Actual changes: {actual_tuples}"
                            )


__all__ = [
    "BalAccountExpectation",
    "BlockAccessListExpectation",
    "compose",
]
