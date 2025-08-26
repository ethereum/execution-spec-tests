"""
BAL modifier functions for invalid test cases.

This module provides modifier functions that can be used to modify Block Access Lists
in various ways for testing invalid block scenarios. They are composable and can be
combined to create complex modifications.
"""

from typing import Callable, List

from ethereum_test_base_types import Address, Number

from .. import BalCodeChange
from . import (
    BalAccountChange,
    BalBalanceChange,
    BalNonceChange,
    BalStorageChange,
    BlockAccessList,
)


def remove_accounts(*addresses: Address) -> Callable[[BlockAccessList], BlockAccessList]:
    """Remove entire account entries from the BAL."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address not in addresses:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def remove_nonces(*addresses: Address) -> Callable[[BlockAccessList], BlockAccessList]:
    """Remove nonce changes from specified accounts."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address in addresses:
                # Create a copy without nonce changes
                new_account = account_change.model_copy(deep=True)
                new_account.nonce_changes = []
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def remove_balances(*addresses: Address) -> Callable[[BlockAccessList], BlockAccessList]:
    """Remove balance changes from specified accounts."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address in addresses:
                # Create a copy without balance changes
                new_account = account_change.model_copy(deep=True)
                new_account.balance_changes = []
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def remove_storage(*addresses: Address) -> Callable[[BlockAccessList], BlockAccessList]:
    """Remove storage changes from specified accounts."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address in addresses:
                # Create a copy without storage changes
                new_account = account_change.model_copy(deep=True)
                new_account.storage_changes = []
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def remove_storage_reads(*addresses: Address) -> Callable[[BlockAccessList], BlockAccessList]:
    """Remove storage reads from specified accounts."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address in addresses:
                # Create a copy without storage reads
                new_account = account_change.model_copy(deep=True)
                new_account.storage_reads = []
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def remove_code(*addresses: Address) -> Callable[[BlockAccessList], BlockAccessList]:
    """Remove code changes from specified accounts."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address in addresses:
                # Create a copy without code changes
                new_account = account_change.model_copy(deep=True)
                new_account.code_changes = []
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def modify_nonce(
    address: Address, tx_index: int, nonce: int
) -> Callable[[BlockAccessList], BlockAccessList]:
    """Set an incorrect nonce value for a specific account and transaction."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address == address:
                new_account = account_change.model_copy(deep=True)
                # Find and modify the specific nonce change
                for i, nonce_change in enumerate(new_account.nonce_changes or []):
                    if nonce_change.tx_index == tx_index:
                        new_account.nonce_changes[i] = BalNonceChange(
                            tx_index=tx_index, post_nonce=nonce
                        )
                        break
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def modify_balance(
    address: Address, tx_index: int, balance: int
) -> Callable[[BlockAccessList], BlockAccessList]:
    """Set an incorrect balance value for a specific account and transaction."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address == address:
                new_account = account_change.model_copy(deep=True)
                # Find and modify the specific balance change
                if new_account.balance_changes:
                    for i, balance_change in enumerate(new_account.balance_changes):
                        if balance_change.tx_index == tx_index:
                            # Create new balance change with wrong value
                            new_account.balance_changes[i] = BalBalanceChange(
                                tx_index=tx_index, post_balance=balance
                            )
                            break
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def modify_storage(
    address: Address, tx_index: int, slot: int, value: int
) -> Callable[[BlockAccessList], BlockAccessList]:
    """Set an incorrect storage value for a specific account, transaction, and slot."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address == address:
                new_account = account_change.model_copy(deep=True)
                # Find and modify the specific storage change (nested structure)
                if new_account.storage_changes:
                    for storage_slot in new_account.storage_changes:
                        if storage_slot.slot == slot:
                            for j, change in enumerate(storage_slot.slot_changes):
                                if change.tx_index == tx_index:
                                    # Create new storage change with wrong value
                                    storage_slot.slot_changes[j] = BalStorageChange(
                                        tx_index=tx_index, post_value=value
                                    )
                                    break
                            break
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def modify_code(
    address: Address, tx_index: int, code: bytes
) -> Callable[[BlockAccessList], BlockAccessList]:
    """Set an incorrect code value for a specific account and transaction."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address == address:
                new_account = account_change.model_copy(deep=True)
                # Find and modify the specific code change
                if new_account.code_changes:
                    for i, code_change in enumerate(new_account.code_changes):
                        if code_change.tx_index == tx_index:
                            # Create new code change with wrong value
                            new_account.code_changes[i] = BalCodeChange(
                                tx_index=tx_index, post_code=code
                            )
                            break
                new_root.append(new_account)
            else:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def swap_tx_indices(tx1: int, tx2: int) -> Callable[[BlockAccessList], BlockAccessList]:
    """Swap transaction indices throughout the BAL, modifying tx ordering."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            new_account = account_change.model_copy(deep=True)

            # Swap in nonce changes
            if new_account.nonce_changes:
                for nonce_change in new_account.nonce_changes:
                    if nonce_change.tx_index == tx1:
                        nonce_change.tx_index = Number(tx2)
                    elif nonce_change.tx_index == tx2:
                        nonce_change.tx_index = Number(tx1)

            # Swap in balance changes
            if new_account.balance_changes:
                for balance_change in new_account.balance_changes:
                    if balance_change.tx_index == tx1:
                        balance_change.tx_index = Number(tx2)
                    elif balance_change.tx_index == tx2:
                        balance_change.tx_index = Number(tx1)

            # Swap in storage changes (nested structure)
            if new_account.storage_changes:
                for storage_slot in new_account.storage_changes:
                    for storage_change in storage_slot.slot_changes:
                        if storage_change.tx_index == tx1:
                            storage_change.tx_index = Number(tx2)
                        elif storage_change.tx_index == tx2:
                            storage_change.tx_index = Number(tx1)

            # Note: storage_reads is just a list of StorageKey, no tx_index to swap

            # Swap in code changes
            if new_account.code_changes:
                for code_change in new_account.code_changes:
                    if code_change.tx_index == tx1:
                        code_change.tx_index = Number(tx2)
                    elif code_change.tx_index == tx2:
                        code_change.tx_index = Number(tx1)

            new_root.append(new_account)

        return BlockAccessList(root=new_root)

    return transform


def append_account(
    account_change: BalAccountChange,
) -> Callable[[BlockAccessList], BlockAccessList]:
    """Append an account to account changes."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = list(bal.root)
        new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


def duplicate_account(address: Address) -> Callable[[BlockAccessList], BlockAccessList]:
    """Duplicate an account entry in the BAL."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            new_root.append(account_change)
            if account_change.address == address:
                # Add duplicate immediately after
                new_root.append(account_change.model_copy(deep=True))
        return BlockAccessList(root=new_root)

    return transform


def reverse_accounts() -> Callable[[BlockAccessList], BlockAccessList]:
    """Reverse the order of accounts in the BAL."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        return BlockAccessList(root=list(reversed(bal.root)))

    return transform


def sort_accounts_by_address() -> Callable[[BlockAccessList], BlockAccessList]:
    """Sort accounts by address (may modify expected ordering)."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        sorted_root = sorted(bal.root, key=lambda x: x.address)
        return BlockAccessList(root=sorted_root)

    return transform


def reorder_accounts(indices: List[int]) -> Callable[[BlockAccessList], BlockAccessList]:
    """Reorder accounts according to the provided index list."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        if len(indices) != len(bal.root):
            raise ValueError("Index list length must match number of accounts")
        new_root = [bal.root[i] for i in indices]
        return BlockAccessList(root=new_root)

    return transform


def clear_all() -> Callable[[BlockAccessList], BlockAccessList]:
    """Return an empty BAL."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        return BlockAccessList(root=[])

    return transform


def keep_only(*addresses: Address) -> Callable[[BlockAccessList], BlockAccessList]:
    """Keep only the specified accounts, removing all others."""

    def transform(bal: BlockAccessList) -> BlockAccessList:
        new_root = []
        for account_change in bal.root:
            if account_change.address in addresses:
                new_root.append(account_change)
        return BlockAccessList(root=new_root)

    return transform


__all__ = [
    # Core functions
    # Account-level modifiers
    "remove_accounts",
    "append_account",
    "duplicate_account",
    "reverse_accounts",
    "keep_only",
    # Field-level modifiers
    "remove_nonces",
    "remove_balances",
    "remove_storage",
    "remove_storage_reads",
    "remove_code",
    # Value modifiers
    "modify_nonce",
    "modify_balance",
    "modify_storage",
    "modify_code",
    # Transaction index modifiers
    "swap_tx_indices",
]
