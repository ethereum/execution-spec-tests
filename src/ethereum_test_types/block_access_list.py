"""
Block Access List (BAL) models for EIP-7928.

Following the established pattern in the codebase (AccessList, AuthorizationTuple),
these are simple data classes that can be composed together.
"""

from typing import Any, Dict, List, Optional

import rlp
from pydantic import Field

from ethereum_test_base_types import Address, Bytes, CamelModel, HexNumber
from ethereum_test_base_types.conversions import BytesConvertible, to_bytes


class BalNonceChange(CamelModel):
    """Represents a nonce change in the block access list."""

    tx_index: int = Field(..., description="Transaction index where the change occurred")
    post_nonce: int = Field(..., description="Nonce value after the transaction")


class BalBalanceChange(CamelModel):
    """Represents a balance change in the block access list."""

    tx_index: int = Field(..., description="Transaction index where the change occurred")
    post_balance: HexNumber = Field(..., description="Balance after the transaction")


class BalCodeChange(CamelModel):
    """Represents a code change in the block access list."""

    tx_index: int = Field(..., description="Transaction index where the change occurred")
    new_code: Bytes = Field(..., description="New code bytes")


class BalStorageChange(CamelModel):
    """Represents a change to a specific storage slot."""

    tx_index: int = Field(..., description="Transaction index where the change occurred")
    post_value: HexNumber = Field(..., description="Value after the transaction")


class BalStorageSlot(CamelModel):
    """Represents all changes to a specific storage slot."""

    slot: HexNumber = Field(..., description="Storage slot key")
    slot_changes: List[BalStorageChange] = Field(
        default_factory=list, description="List of changes to this slot"
    )


class BalAccountChange(CamelModel):
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
    storage_reads: Optional[List[HexNumber]] = Field(
        None, description="List of storage slots that were read"
    )


class BlockAccessList(CamelModel):
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(exclude_none=True)

    def verify_against(self, actual_rlp: BytesConvertible) -> None:
        """
        Verify that the actual BAL from the client matches this expected BAL.

        Args:
            actual_rlp: RLP-encoded BAL from the client

        Raises:
            Exception: If verification fails

        """
        # Decode the actual BAL
        actual_bal = self._decode_rlp(actual_rlp)

        # Verify all expected accounts are present
        for expected_account in self.account_changes:
            actual_account = self._find_account(actual_bal, expected_account.address)
            if actual_account is None:
                raise Exception(
                    f"Expected account {expected_account.address} not found in actual BAL"
                )

            # Verify nonce changes
            if expected_account.nonce_changes:
                self._verify_nonce_changes(
                    expected_account.address,
                    expected_account.nonce_changes,
                    actual_account.get("nonce_changes", []),
                )

            # Verify balance changes
            if expected_account.balance_changes:
                self._verify_balance_changes(
                    expected_account.address,
                    expected_account.balance_changes,
                    actual_account.get("balance_changes", []),
                )

            # Similar for other change types...

    def _decode_rlp(self, rlp_data: BytesConvertible) -> Dict[str, Any]:
        """Decode RLP data to dictionary."""
        decoded = rlp.decode(to_bytes(rlp_data))

        account_changes = []
        for account_entry in decoded:
            if len(account_entry) < 2:
                continue

            address = Address(account_entry[0])
            account_data = {
                "address": address,
                "storage_changes": account_entry[1] if len(account_entry) > 1 else [],
                "storage_reads": account_entry[2] if len(account_entry) > 2 else [],
                "balance_changes": account_entry[3] if len(account_entry) > 3 else [],
                "nonce_changes": account_entry[4] if len(account_entry) > 4 else [],
                "code_changes": account_entry[5] if len(account_entry) > 5 else [],
            }
            account_changes.append(account_data)

        return {"account_changes": account_changes}

    def _find_account(self, bal: Dict[str, Any], address: Address) -> Optional[Dict[str, Any]]:
        """Find an account in the decoded BAL."""
        # Convert address to bytes for comparison
        address_bytes = bytes(address) if hasattr(address, "__bytes__") else address

        for account in bal.get("account_changes", []):
            account_addr = account.get("address")
            # Convert to bytes if needed for comparison
            if isinstance(account_addr, Address):
                account_addr = bytes(account_addr)
            if account_addr == address_bytes:
                return account
        return None

    def _verify_nonce_changes(
        self, address: Address, expected: List[BalNonceChange], actual: List[Any]
    ) -> None:
        """Verify nonce changes match."""
        # Decode actual changes for better error reporting
        actual_decoded = []
        for act_change in actual:
            if len(act_change) >= 2:
                tx_index = (
                    int.from_bytes(act_change[0], "big")
                    if isinstance(act_change[0], bytes) and act_change[0]
                    else (0 if isinstance(act_change[0], bytes) else act_change[0])
                )
                post_nonce = (
                    int.from_bytes(act_change[1], "big")
                    if isinstance(act_change[1], bytes) and act_change[1]
                    else (0 if isinstance(act_change[1], bytes) else act_change[1])
                )
                actual_decoded.append(f"tx_index={tx_index} post_nonce={post_nonce}")

        for exp_change in expected:
            found = False
            for act_change in actual:
                # Each nonce change is [tx_index, post_nonce]
                if len(act_change) >= 2:
                    # Convert bytes to int if needed
                    tx_index = (
                        int.from_bytes(act_change[0], "big")
                        if isinstance(act_change[0], bytes) and act_change[0]
                        else (0 if isinstance(act_change[0], bytes) else act_change[0])
                    )
                    post_nonce = (
                        int.from_bytes(act_change[1], "big")
                        if isinstance(act_change[1], bytes) and act_change[1]
                        else (0 if isinstance(act_change[1], bytes) else act_change[1])
                    )
                    if tx_index == exp_change.tx_index and post_nonce == exp_change.post_nonce:
                        found = True
                        break
            if not found:
                raise Exception(
                    f"Account {address}: Nonce change mismatch\n"
                    f"  Expected: tx_index={exp_change.tx_index} "
                    f"post_nonce={exp_change.post_nonce}\n"
                    f"  Actual nonce changes: {actual_decoded}"
                )

    def _verify_balance_changes(
        self, address: Address, expected: List[BalBalanceChange], actual: List[Any]
    ) -> None:
        """Verify balance changes match."""
        # Decode actual changes for better error reporting
        actual_decoded = []
        for act_change in actual:
            if len(act_change) >= 2:
                tx_index = (
                    int.from_bytes(act_change[0], "big")
                    if isinstance(act_change[0], bytes) and act_change[0]
                    else (0 if isinstance(act_change[0], bytes) else act_change[0])
                )
                post_balance = (
                    int.from_bytes(act_change[1], "big")
                    if isinstance(act_change[1], bytes) and act_change[1]
                    else (0 if isinstance(act_change[1], bytes) else int(act_change[1]))
                )
                actual_decoded.append(f"tx_index={tx_index} post_balance={post_balance}")

        for exp_change in expected:
            found = False
            for act_change in actual:
                # Each balance change is [tx_index, post_balance]
                if len(act_change) >= 2:
                    # Convert bytes to int if needed, handling empty bytes
                    tx_index = (
                        int.from_bytes(act_change[0], "big")
                        if isinstance(act_change[0], bytes) and act_change[0]
                        else (0 if isinstance(act_change[0], bytes) else act_change[0])
                    )
                    # Balance is stored as bytes/int, need to compare properly
                    post_balance = (
                        int.from_bytes(act_change[1], "big")
                        if isinstance(act_change[1], bytes) and act_change[1]
                        else (0 if isinstance(act_change[1], bytes) else int(act_change[1]))
                    )
                    if tx_index == exp_change.tx_index and post_balance == int(
                        exp_change.post_balance
                    ):
                        found = True
                        break
            if not found:
                raise Exception(
                    f"Account {address}: Balance change mismatch\n"
                    f"  Expected: tx_index={exp_change.tx_index} "
                    f"post_balance={exp_change.post_balance}\n"
                    f"  Actual balance changes: {actual_decoded}"
                )
