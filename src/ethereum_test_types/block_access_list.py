"""
Block Access List (BAL) models for EIP-7928.

Following the established pattern in the codebase (AccessList, AuthorizationTuple),
these are simple data classes that can be composed together.
"""

from typing import Any, ClassVar, Dict, List, Optional

from pydantic import Field

from ethereum_test_base_types import (
    Address,
    Bytes,
    CamelModel,
    HexNumber,
    RLPSerializable,
    StorageKey,
)


class BalNonceChange(CamelModel, RLPSerializable):
    """Represents a nonce change in the block access list."""

    tx_index: int = Field(..., description="Transaction index where the change occurred")
    post_nonce: int = Field(..., description="Nonce value after the transaction")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "post_nonce"]


class BalBalanceChange(CamelModel, RLPSerializable):
    """Represents a balance change in the block access list."""

    tx_index: int = Field(..., description="Transaction index where the change occurred")
    post_balance: HexNumber = Field(..., description="Balance after the transaction")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "post_balance"]


class BalCodeChange(CamelModel, RLPSerializable):
    """Represents a code change in the block access list."""

    tx_index: int = Field(..., description="Transaction index where the change occurred")
    new_code: Bytes = Field(..., description="New code bytes")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "new_code"]


class BalStorageChange(CamelModel, RLPSerializable):
    """Represents a change to a specific storage slot."""

    tx_index: int = Field(..., description="Transaction index where the change occurred")
    post_value: StorageKey = Field(..., description="Value after the transaction")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "post_value"]


class BalStorageSlot(CamelModel, RLPSerializable):
    """Represents all changes to a specific storage slot."""

    slot: StorageKey = Field(..., description="Storage slot key")
    slot_changes: List[BalStorageChange] = Field(
        default_factory=list, description="List of changes to this slot"
    )

    rlp_fields: ClassVar[List[str]] = ["slot", "slot_changes"]


class BalAccountChange(CamelModel, RLPSerializable):
    """Represents all changes to a specific account in a block."""

    address: Address = Field(..., description="Account address")
    nonce_changes: Optional[List[BalNonceChange]] = Field(
        None, description="List of nonce changes"
    )
    balance_changes: Optional[List[BalBalanceChange]] = Field(
        None, description="List of balance changes"
    )
    code_changes: Optional[List[BalCodeChange]] = Field(None, description="List of code changes")
    storage_changes: Optional[List[BalStorageSlot]] = Field(
        None, description="List of storage changes"
    )
    storage_reads: Optional[List[StorageKey]] = Field(
        None, description="List of storage slots that were read"
    )

    rlp_fields: ClassVar[List[str]] = [
        "address",
        "storage_changes",
        "storage_reads",
        "balance_changes",
        "nonce_changes",
        "code_changes",
    ]

    def to_list(self, signing: bool = False) -> List[Any]:
        """
        Override to handle None list fields properly.
        None list fields should serialize as empty lists, not empty bytes.
        """
        from ethereum_test_base_types.serialization import to_serializable_element

        result: list[Any] = []
        for field_name in self.rlp_fields:
            value = getattr(self, field_name)

            # Special handling for None list fields - they should be empty lists
            if value is None and field_name in [
                "storage_changes",
                "storage_reads",
                "balance_changes",
                "nonce_changes",
                "code_changes",
            ]:
                result.append([])
            else:
                result.append(to_serializable_element(value))

        return result


class BlockAccessList(CamelModel, RLPSerializable):
    """
    Expected Block Access List for verification.

    This follows the same pattern as AccessList and AuthorizationTuple -
    a simple data class that can be used directly in tests.

    Example:
        expected_block_access_list = BlockAccessList(
            account_changes=[
                BalAccountChange(
                    address=alice,
                    nonce_changes=[
                        BalNonceChange(tx_index=0, post_nonce=1)
                    ],
                    balance_changes=[
                        BalBalanceChange(tx_index=0, post_balance=9000)
                    ]
                ),
                BalAccountChange(
                    address=bob,
                    balance_changes=[
                        BalBalanceChange(tx_index=0, post_balance=100)
                    ]
                ),
            ]
        )

    """

    account_changes: List[BalAccountChange] = Field(
        default_factory=list, description="List of account changes in the block"
    )

    rlp_fields: ClassVar[List[str]] = ["account_changes"]

    def to_list(self, signing: bool = False) -> List[Any]:
        """
        Override to_list to return the account changes list directly.

        The BlockAccessList IS the list of account changes, not a container
        that contains a list, per EIP-7928.
        """
        # Return the list of accounts directly, not wrapped in another list
        from ethereum_test_base_types.serialization import to_serializable_element

        return to_serializable_element(self.account_changes)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(exclude_none=True)

    def verify_against(self, actual_bal: "BlockAccessList") -> None:
        """
        Verify that the actual BAL from the client matches this expected BAL.

        Args:
            actual_bal: The BlockAccessList model from the client

        Raises:
            Exception: If verification fails

        """
        actual_accounts_by_addr = {acc.address: acc for acc in actual_bal.account_changes}
        expected_accounts_by_addr = {acc.address: acc for acc in self.account_changes}

        # Check for missing accounts
        missing_accounts = set(expected_accounts_by_addr.keys()) - set(
            actual_accounts_by_addr.keys()
        )
        if missing_accounts:
            raise Exception(
                "Expected accounts not found in actual BAL: "
                f"{', '.join(str(a) for a in missing_accounts)}"
            )

        # Verify each expected account
        for address, expected_account in expected_accounts_by_addr.items():
            actual_account = actual_accounts_by_addr[address]

            try:
                self._compare_account_changes(expected_account, actual_account)
            except AssertionError as e:
                raise Exception(f"Account {address}: {str(e)}") from e

    def _compare_account_changes(
        self, expected: BalAccountChange, actual: BalAccountChange
    ) -> None:
        """
        Compare two BalAccountChange models with detailed error reporting.

        Only validates fields that were explicitly set in the expected model,
        using model_fields_set to determine what was intentionally specified.
        """
        # Only check fields that were explicitly set in the expected model
        for field_name in expected.model_fields_set:
            if field_name == "address":
                continue  # Already matched by account lookup

            expected_value = getattr(expected, field_name)
            actual_value = getattr(actual, field_name)

            # If we explicitly set a field to None, verify it's None/empty
            if expected_value is None:
                if actual_value is not None and actual_value != []:
                    raise AssertionError(
                        f"Expected {field_name} to be empty/None but found: {actual_value}"
                    )
                continue

            # If actual is ``None`` but we expected something, raise
            if actual_value is None:
                raise AssertionError(f"Expected {field_name} but found none")

            if field_name == "storage_reads":
                # Convert to comparable format (both are lists of 32-byte values)
                expected_set = {bytes(v) if hasattr(v, "__bytes__") else v for v in expected_value}
                actual_set = {bytes(v) if hasattr(v, "__bytes__") else v for v in actual_value}
                if expected_set != actual_set:
                    missing = expected_set - actual_set
                    extra = actual_set - expected_set
                    msg = "Storage reads mismatch."
                    if missing:
                        msg += f" Missing: {
                            [v.hex() if isinstance(v, bytes) else str(v) for v in missing]
                        }."
                    if extra:
                        msg += f" Extra: {
                            [v.hex() if isinstance(v, bytes) else str(v) for v in extra]
                        }."
                    raise AssertionError(msg)

            elif isinstance(expected_value, list):
                # For lists of changes, use the model_dump approach for comparison
                expected_data = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in expected_value
                ]
                actual_data = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in actual_value
                ]

                if not self._compare_change_lists(field_name, expected_data, actual_data):
                    # The comparison method will raise with details
                    pass

    def _compare_change_lists(self, field_name: str, expected: List, actual: List) -> bool:
        """Compare lists of change objects using set operations for better error messages."""
        if field_name == "storage_changes":
            # Storage changes are nested (slot -> changes)
            expected_by_slot = {slot["slot"]: slot["slot_changes"] for slot in expected}
            actual_by_slot = {slot["slot"]: slot["slot_changes"] for slot in actual}

            missing_slots = set(expected_by_slot.keys()) - set(actual_by_slot.keys())
            if missing_slots:
                raise AssertionError(f"Missing storage slots: {missing_slots}")

            for slot, exp_changes in expected_by_slot.items():
                act_changes = actual_by_slot.get(slot, [])
                # Handle Hash/bytes for post_value comparison
                exp_set = {
                    (
                        c["tx_index"],
                        bytes(c["post_value"])
                        if hasattr(c["post_value"], "__bytes__")
                        else c["post_value"],
                    )
                    for c in exp_changes
                }
                act_set = {
                    (
                        c["tx_index"],
                        bytes(c["post_value"])
                        if hasattr(c["post_value"], "__bytes__")
                        else c["post_value"],
                    )
                    for c in act_changes
                }

                if exp_set != act_set:
                    missing = exp_set - act_set
                    extra = act_set - exp_set
                    msg = f"Slot {slot} changes mismatch."
                    if missing:
                        msg += f" Missing: {missing}."
                    if extra:
                        msg += f" Extra: {extra}."
                    raise AssertionError(msg)
        else:
            # Create comparable tuples for each change type
            if field_name == "nonce_changes":
                expected_set = {(c["tx_index"], c["post_nonce"]) for c in expected}
                actual_set = {(c["tx_index"], c["post_nonce"]) for c in actual}
                item_type = "nonce"
            elif field_name == "balance_changes":
                expected_set = {(c["tx_index"], int(c["post_balance"])) for c in expected}
                actual_set = {(c["tx_index"], int(c["post_balance"])) for c in actual}
                item_type = "balance"
            elif field_name == "code_changes":
                expected_set = {(c["tx_index"], bytes(c["new_code"])) for c in expected}
                actual_set = {(c["tx_index"], bytes(c["new_code"])) for c in actual}
                item_type = "code"
            else:
                raise ValueError("Unexpected type")

            if expected_set != actual_set:
                missing = expected_set - actual_set
                extra = actual_set - expected_set
                msg = f"{item_type.capitalize()} changes mismatch."
                if missing:
                    msg += f" Missing: {missing}."
                if extra:
                    msg += f" Extra: {extra}."
                raise AssertionError(msg)

        return True
