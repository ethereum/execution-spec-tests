"""Unit tests for BlockAccessListExpectation validation."""

import pytest

from ethereum_test_base_types import Address
from ethereum_test_types.block_access_list import (
    BalAccountChange,
    BalAccountExpectation,
    BalBalanceChange,
    BalNonceChange,
    BalStorageChange,
    BalStorageSlot,
    BlockAccessList,
    BlockAccessListExpectation,
)


def test_address_exclusion_validation_passes():
    """Test that address exclusion works when address is not in BAL."""
    alice = Address("0x000000000000000000000000000000000000000a")
    bob = Address("0x000000000000000000000000000000000000000b")

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            alice: BalAccountExpectation(nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)]),
            bob: None,  # expect Bob is not in BAL (correctly)
        }
    )

    expectation.verify_against(actual_bal)


def test_address_exclusion_validation_raises_when_address_is_present():
    """Test that validation fails when excluded address is in BAL."""
    alice = Address("0x000000000000000000000000000000000000000a")
    bob = Address("0x000000000000000000000000000000000000000b")

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
            ),
            BalAccountChange(
                address=bob,
                balance_changes=[BalBalanceChange(tx_index=1, post_balance=100)],
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        # explicitly expect Bob to NOT be in BAL (wrongly)
        account_expectations={bob: None},
    )

    with pytest.raises(Exception, match="should not be in BAL but was found"):
        expectation.verify_against(actual_bal)


def test_empty_list_validation():
    """Test that empty list validates correctly."""
    alice = Address("0x000000000000000000000000000000000000000a")

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                balance_changes=[],  # no balance changes
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            alice: BalAccountExpectation(
                nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                balance_changes=[],  # explicitly expect no balance changes
            ),
        }
    )

    expectation.verify_against(actual_bal)


def test_empty_list_validation_fails():
    """Test that validation fails when expecting empty but field has values."""
    alice = Address("0x000000000000000000000000000000000000000a")

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                balance_changes=[BalBalanceChange(tx_index=1, post_balance=100)],
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            # expect no balance changes (wrongly)
            alice: BalAccountExpectation(balance_changes=[]),
        }
    )

    with pytest.raises(Exception, match="Expected balance_changes to be empty"):
        expectation.verify_against(actual_bal)


def test_partial_validation():
    """Test that unset fields are not validated."""
    alice = Address("0x000000000000000000000000000000000000000a")

    # Actual BAL has multiple types of changes
    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                balance_changes=[BalBalanceChange(tx_index=1, post_balance=100)],
                storage_reads=[0x01, 0x02],
            ),
        ]
    )

    # Only validate nonce changes, ignore balance and storage
    expectation = BlockAccessListExpectation(
        account_expectations={
            alice: BalAccountExpectation(
                nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                # balance_changes and storage_reads not set and won't be validated
            ),
        }
    )

    expectation.verify_against(actual_bal)


def test_storage_changes_validation():
    """Test storage changes validation."""
    contract = Address("0x000000000000000000000000000000000000000c")

    # Actual BAL with storage changes
    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=contract,
                storage_changes=[
                    BalStorageSlot(
                        slot=0x01,
                        slot_changes=[BalStorageChange(tx_index=1, post_value=0x42)],
                    )
                ],
            ),
        ]
    )

    # Expect the same storage changes
    expectation = BlockAccessListExpectation(
        account_expectations={
            contract: BalAccountExpectation(
                storage_changes=[
                    BalStorageSlot(
                        slot=0x01,
                        slot_changes=[BalStorageChange(tx_index=1, post_value=0x42)],
                    )
                ],
            ),
        }
    )

    expectation.verify_against(actual_bal)


def test_missing_expected_address():
    """Test that validation fails when expected address is missing."""
    alice = Address("0x000000000000000000000000000000000000000a")
    bob = Address("0x000000000000000000000000000000000000000b")

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            # wrongly expect Bob to be present
            bob: BalAccountExpectation(
                nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
            ),
        }
    )

    with pytest.raises(Exception, match="Expected address .* not found in actual BAL"):
        expectation.verify_against(actual_bal)
