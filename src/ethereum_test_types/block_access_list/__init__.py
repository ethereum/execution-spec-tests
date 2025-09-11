"""
Block Access List (BAL) models for EIP-7928.

Following the established pattern in the codebase (AccessList, AuthorizationTuple),
these are simple data classes that can be composed together.
"""

from functools import cached_property
from typing import Any, Callable, ClassVar, Dict, List, Union

import ethereum_rlp as eth_rlp
from pydantic import Field, PrivateAttr

from ethereum_test_base_types import (
    Address,
    Bytes,
    CamelModel,
    EthereumTestRootModel,
    HexNumber,
    RLPSerializable,
    StorageKey,
)
from ethereum_test_base_types.serialization import to_serializable_element


class BlockAccessListValidationError(Exception):
    """Custom exception for Block Access List validation errors."""

    pass


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

    tx_index: HexNumber = Field(
        HexNumber(1),
        description="Transaction index where the change occurred",
    )
    post_nonce: HexNumber = Field(..., description="Nonce value after the transaction")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "post_nonce"]


class BalBalanceChange(CamelModel, RLPSerializable):
    """Represents a balance change in the block access list."""

    tx_index: HexNumber = Field(
        HexNumber(1),
        description="Transaction index where the change occurred",
    )
    post_balance: HexNumber = Field(..., description="Balance after the transaction")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "post_balance"]


class BalCodeChange(CamelModel, RLPSerializable):
    """Represents a code change in the block access list."""

    tx_index: HexNumber = Field(
        HexNumber(1),
        description="Transaction index where the change occurred",
    )
    new_code: Bytes = Field(..., description="New code bytes")

    rlp_fields: ClassVar[List[str]] = ["tx_index", "new_code"]


class BalStorageChange(CamelModel, RLPSerializable):
    """Represents a change to a specific storage slot."""

    tx_index: HexNumber = Field(
        HexNumber(1),
        description="Transaction index where the change occurred",
    )
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


BlockAccessListChangeLists = Union[
    List[BalNonceChange],
    List[BalBalanceChange],
    List[BalCodeChange],
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

        Validation steps:
        1. Validate actual BAL conforms to EIP-7928 ordering requirements
        2. Verify address expectations - presence or explicit absence
        3. Verify expected changes within accounts match actual changes

        Args:
            actual_bal: The BlockAccessList model from the client

        Raises:
            Exception: If verification fails

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
        Validate that the actual BAL follows EIP-7928 ordering requirements.

        Per EIP-7928:
        - Addresses must be in lexicographic (bytewise) order
        - Storage keys must be in lexicographic order within each account
        - Block access indices must be in ascending order within each change list

        Args:
            bal: The BlockAccessList to validate

        Raises:
            Exception: If BAL doesn't follow EIP-7928 ordering

        """
        addresses = [acc.address for acc in bal.root]

        # Check addresses are in lexicographic order
        sorted_addresses = sorted(addresses, key=lambda x: bytes(x))
        if addresses != sorted_addresses:
            raise BlockAccessListValidationError(
                f"BAL addresses not in lexicographic order per EIP-7928. "
                f"Got: {[str(a) for a in addresses]}, "
                f"Expected: {[str(a) for a in sorted_addresses]}"
            )

        # Check ordering within each account
        for account in bal.root:
            # Check storage slots are in lexicographic order
            if account.storage_changes:
                slots = [s.slot for s in account.storage_changes]
                sorted_slots = sorted(slots, key=lambda x: bytes(x))
                if slots != sorted_slots:
                    raise BlockAccessListValidationError(
                        f"Account {account.address}: Storage slots not in lexicographic order. "
                        f"Got: {slots}, Expected: {sorted_slots}"
                    )

                # Check tx indices within each storage slot are in ascending order
                for slot_change in account.storage_changes:
                    if slot_change.slot_changes:
                        tx_indices = [c.tx_index for c in slot_change.slot_changes]
                        if tx_indices != sorted(tx_indices):
                            raise BlockAccessListValidationError(
                                f"Account {account.address}, Slot {slot_change.slot}: "
                                f"tx_indices not in ascending order. Got: {tx_indices}"
                            )

            # Check storage reads are in lexicographic order
            if account.storage_reads:
                sorted_reads = sorted(account.storage_reads, key=lambda x: bytes(x))
                if account.storage_reads != sorted_reads:
                    raise BlockAccessListValidationError(
                        f"Account {account.address}: Storage reads not in "
                        f"lexicographic order. Got: {account.storage_reads}, "
                        f"Expected: {sorted_reads}"
                    )

            # Check tx indices in other change lists
            changes_to_check: List[tuple[str, Union[BlockAccessListChangeLists]]] = [
                ("nonce_changes", account.nonce_changes),
                ("balance_changes", account.balance_changes),
                ("code_changes", account.code_changes),
            ]
            for field_name, changes in changes_to_check:
                if changes:
                    tx_indices = [c.tx_index for c in changes]
                    if tx_indices != sorted(tx_indices):
                        raise BlockAccessListValidationError(
                            f"Account {account.address}: {field_name} tx_indices "
                            f"not in ascending order. Got: {tx_indices}"
                        )

    def _compare_account_expectations(
        self, expected: BalAccountExpectation, actual: BalAccountChange
    ) -> None:
        """
        Compare expected account changes with actual BAL account entry.

        Only validates fields that were explicitly set in the expected model,
        using model_fields_set to determine what was intentionally specified.
        """
        change_fields = {
            "nonce_changes",
            "balance_changes",
            "code_changes",
            "storage_changes",
        }
        bal_fields = change_fields | {"storage_reads"}

        # Only check fields that were explicitly set in the expected model
        for field_name in expected.model_fields_set.intersection(bal_fields):
            expected_value = getattr(expected, field_name)
            actual_value = getattr(actual, field_name)

            # empty list explicitly set (no changes expected)
            if not expected_value:
                if actual_value:
                    raise BlockAccessListValidationError(
                        f"Expected {field_name} to be empty but found: {actual_value}"
                    )
                continue

            if field_name == "storage_reads":
                # EIP-7928: Storage reads must be in lexicographic order
                # check as subsequence
                expected_reads = [
                    bytes(v) if hasattr(v, "__bytes__") else v for v in expected_value
                ]
                actual_reads = [bytes(v) if hasattr(v, "__bytes__") else v for v in actual_value]

                # Check that expected reads form a subsequence of actual reads
                actual_idx = 0
                for exp_read in expected_reads:
                    found = False
                    while actual_idx < len(actual_reads):
                        if actual_reads[actual_idx] == exp_read:
                            found = True
                            actual_idx += 1
                            break
                        actual_idx += 1

                    if not found:
                        exp_str = exp_read.hex() if isinstance(exp_read, bytes) else str(exp_read)
                        actual_str = [
                            r.hex() if isinstance(r, bytes) else str(r) for r in actual_reads
                        ]
                        raise BlockAccessListValidationError(
                            f"Storage read {exp_str} not found or not in correct order. "
                            f"Actual reads: {actual_str}"
                        )

            elif field_name in change_fields:
                # For lists of changes, convert Pydantic models to dicts for
                # comparison
                expected_data = [item.model_dump() for item in expected_value]
                actual_data = [item.model_dump() for item in actual_value]
                self._validate_change_lists(field_name, expected_data, actual_data)

    @staticmethod
    def _validate_change_lists(field_name: str, expected: List, actual: List) -> None:
        """
        Validate that expected change lists form a subsequence of actual changes.

        Note: Ordering validation per EIP-7928 is already done in _validate_bal_ordering.
        This method only checks that expected items appear in the actual list as a subsequence.

        Raises:
            AssertionError: If expected changes are not found or not in correct order

        """
        if field_name == "storage_changes":
            # Storage changes are nested (slot -> changes)
            expected_slots = [slot["slot"] for slot in expected]
            actual_slots = [slot["slot"] for slot in actual]

            # Check expected slots form a subsequence (ordering already validated)
            actual_idx = 0
            for exp_slot in expected_slots:
                found = False
                while actual_idx < len(actual_slots):
                    if actual_slots[actual_idx] == exp_slot:
                        found = True
                        break
                    actual_idx += 1

                if not found:
                    raise BlockAccessListValidationError(
                        f"Expected storage slot {exp_slot} not found or not in "
                        f"correct order. Actual slots: {actual_slots}"
                    )

            # check changes within each slot
            expected_by_slot = {slot["slot"]: slot["slot_changes"] for slot in expected}
            actual_by_slot = {slot["slot"]: slot["slot_changes"] for slot in actual}

            for slot, exp_changes in expected_by_slot.items():
                if slot not in actual_by_slot:
                    raise BlockAccessListValidationError(
                        f"Expected storage slot {slot} not found in actual"
                    )

                act_changes = actual_by_slot[slot]

                # Check that expected changes form a subsequence
                exp_tuples = [
                    (
                        c["tx_index"],
                        bytes(c["post_value"])
                        if hasattr(c["post_value"], "__bytes__")
                        else c["post_value"],
                    )
                    for c in exp_changes
                ]
                act_tuples = [
                    (
                        c["tx_index"],
                        bytes(c["post_value"])
                        if hasattr(c["post_value"], "__bytes__")
                        else c["post_value"],
                    )
                    for c in act_changes
                ]

                act_idx = 0
                for exp_tuple in exp_tuples:
                    found = False
                    while act_idx < len(act_tuples):
                        if act_tuples[act_idx] == exp_tuple:
                            found = True
                            act_idx += 1
                            break
                        act_idx += 1

                    if not found:
                        raise BlockAccessListValidationError(
                            f"Slot {slot}: Expected change {exp_tuple} not found "
                            f"or not in correct order. Actual changes: {act_tuples}"
                        )

        else:
            # Create tuples for comparison (ordering already validated)
            if field_name == "nonce_changes":
                expected_tuples = [(c["tx_index"], c["post_nonce"]) for c in expected]
                actual_tuples = [(c["tx_index"], c["post_nonce"]) for c in actual]
                item_type = "nonce"
            elif field_name == "balance_changes":
                expected_tuples = [(c["tx_index"], int(c["post_balance"])) for c in expected]
                actual_tuples = [(c["tx_index"], int(c["post_balance"])) for c in actual]
                item_type = "balance"
            elif field_name == "code_changes":
                expected_tuples = [(c["tx_index"], bytes(c["new_code"])) for c in expected]
                actual_tuples = [(c["tx_index"], bytes(c["new_code"])) for c in actual]
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
                    raise BlockAccessListValidationError(
                        f"{item_type.capitalize()} change {exp_tuple} not found "
                        f"or not in correct order. Actual changes: {actual_tuples}"
                    )


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
