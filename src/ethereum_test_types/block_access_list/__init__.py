"""
Block Access List (BAL) models for EIP-7928.

Following the established pattern in the codebase (AccessList, AuthorizationTuple),
these are simple data classes that can be composed together.
"""

from functools import cached_property
from typing import Any, Callable, ClassVar, Dict, List

import ethereum_rlp as eth_rlp
from pydantic import Field, PrivateAttr

from ethereum_test_base_types import (
    Address,
    Bytes,
    CamelModel,
    EthereumTestRootModel,
    HexNumber,
    Number,
    RLPSerializable,
    StorageKey,
)
from ethereum_test_base_types.serialization import to_serializable_element


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


class BalNonceChange(CamelModel, RLPSerializable):
    """Represents a nonce change in the block access list."""

    tx_index: Number = Field(..., description="Transaction index where the change occurred")
    post_nonce: Number = Field(..., description="Nonce value after the transaction")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "post_nonce"]


class BalBalanceChange(CamelModel, RLPSerializable):
    """Represents a balance change in the block access list."""

    tx_index: Number = Field(..., description="Transaction index where the change occurred")
    post_balance: HexNumber = Field(..., description="Balance after the transaction")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "post_balance"]


class BalCodeChange(CamelModel, RLPSerializable):
    """Represents a code change in the block access list."""

    tx_index: Number = Field(..., description="Transaction index where the change occurred")
    new_code: Bytes = Field(..., description="New code bytes")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "new_code"]


class BalStorageChange(CamelModel, RLPSerializable):
    """Represents a change to a specific storage slot."""

    tx_index: Number = Field(..., description="Transaction index where the change occurred")
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
    nonce_changes: List[BalNonceChange] = Field(
        default_factory=list, description="List of nonce changes"
    )
    balance_changes: List[BalBalanceChange] = Field(
        default_factory=list, description="List of balance changes"
    )
    code_changes: List[BalCodeChange] = Field(
        default_factory=list, description="List of code changes"
    )
    storage_changes: List[BalStorageSlot] = Field(
        default_factory=list, description="List of storage changes"
    )
    storage_reads: List[StorageKey] = Field(
        default_factory=list, description="List of storage slots that were read"
    )

    rlp_fields: ClassVar[List[str]] = [
        "address",
        "storage_changes",
        "storage_reads",
        "balance_changes",
        "nonce_changes",
        "code_changes",
    ]


class BlockAccessList(EthereumTestRootModel[List[BalAccountChange]]):
    """
    Block Access List for t8n tool communication and fixtures.

    This model represents the BAL exactly as defined in EIP-7928 - it is itself a list
    of account changes (root model), not a container. Used for:
    - Communication with t8n tools
    - Fixture generation
    - RLP encoding for hash verification

    Example:
        bal = BlockAccessList([
            BalAccountChange(address=alice, nonce_changes=[...]),
            BalAccountChange(address=bob, balance_changes=[...])
        ])

    """

    root: List[BalAccountChange] = Field(default_factory=list)

    def to_list(self) -> List[Any]:
        """Return the list for RLP encoding per EIP-7928."""
        return to_serializable_element(self.root)

    @cached_property
    def rlp(self) -> Bytes:
        """Return the RLP encoded block access list for hash verification."""
        return Bytes(eth_rlp.encode(self.to_list()))

    @cached_property
    def rlp_hash(self) -> Bytes:
        """Return the hash of the RLP encoded block access list."""
        return self.rlp.keccak256()


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

    def to_fixture_bal(self, t8n_bal: "BlockAccessList") -> "BlockAccessList":
        """
        Convert t8n BAL to fixture BAL, optionally applying transformations.

        1. First validates expectations are met (if any)
        2. Then applies modifier if specified (for invalid tests)

        Args:
            t8n_bal: The BlockAccessList from t8n tool

        Returns:
            The potentially transformed BlockAccessList for the fixture

        """
        if self.account_expectations:
            self.verify_against(t8n_bal)

        # Apply modifier if present (for invalid tests)
        if self._modifier:
            return self._modifier(t8n_bal)

        return t8n_bal

    def verify_against(self, actual_bal: "BlockAccessList") -> None:
        """
        Verify that the actual BAL from the client matches this expected BAL.

        Args:
            actual_bal: The BlockAccessList model from the client

        Raises:
            Exception: If verification fails

        """
        actual_accounts_by_addr = {acc.address: acc for acc in actual_bal.root}

        for address, expectation in self.account_expectations.items():
            if expectation is None:
                # check explicit exclusion of address when set to `None`
                if address in actual_accounts_by_addr:
                    raise Exception(f"Address {address} should not be in BAL but was found")
            else:
                # Address should be in BAL with expected values
                if address not in actual_accounts_by_addr:
                    raise Exception(f"Expected address {address} not found in actual BAL")

                actual_account = actual_accounts_by_addr[address]
                try:
                    self._compare_account_expectations(expectation, actual_account)
                except AssertionError as e:
                    raise Exception(f"Account {address}: {str(e)}") from e

    def _compare_account_expectations(
        self, expected: BalAccountExpectation, actual: BalAccountChange
    ) -> None:
        """
        Compare expected account changes with actual BAL account entry.

        Only validates fields that were explicitly set in the expected model,
        using model_fields_set to determine what was intentionally specified.
        """
        # Only check fields that were explicitly set in the expected model
        for field_name in expected.model_fields_set:
            expected_value = getattr(expected, field_name)
            actual_value = getattr(actual, field_name)

            # empty list explicitly set (no changes expected)
            if not expected_value:
                if actual_value:
                    raise AssertionError(
                        f"Expected {field_name} to be empty but found: {actual_value}"
                    )
                continue

            if field_name == "storage_reads":
                # Convert to comparable format (both are lists of 32-byte values)
                expected_set = {bytes(v) if hasattr(v, "__bytes__") else v for v in expected_value}
                actual_set = {bytes(v) if hasattr(v, "__bytes__") else v for v in actual_value}
                if expected_set != actual_set:
                    missing = expected_set - actual_set
                    extra = actual_set - expected_set
                    msg = "Storage reads mismatch."
                    if missing:
                        missing_str = [
                            v.hex() if isinstance(v, bytes) else str(v) for v in missing
                        ]
                        msg += f" Missing: {missing_str}."
                    if extra:
                        extra_str = [v.hex() if isinstance(v, bytes) else str(v) for v in extra]
                        msg += f" Extra: {extra_str}."
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

    @staticmethod
    def _compare_change_lists(field_name: str, expected: List, actual: List) -> bool:
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


__all__ = [
    # Core models
    "BlockAccessList",
    "BlockAccessListExpectation",
    "BalAccountExpectation",
    # Change types
    "BalAccountChange",
    "BalNonceChange",
    "BalBalanceChange",
    "BalCodeChange",
    "BalStorageChange",
    "BalStorageSlot",
]
