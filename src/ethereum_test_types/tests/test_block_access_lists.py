"""Unit tests for BlockAccessListExpectation validation."""

import pytest

from ethereum_test_base_types import Address, StorageKey
from ethereum_test_types.block_access_list import (
    BalAccountChange,
    BalAccountExpectation,
    BalBalanceChange,
    BalCodeChange,
    BalNonceChange,
    BalStorageChange,
    BalStorageSlot,
    BlockAccessList,
    BlockAccessListExpectation,
)
from ethereum_test_types.block_access_list.absence_validators import (
    balance_changes_at_tx,
    code_changes_at_tx,
    nonce_changes_at_tx,
    storage_changes_at_slots,
    storage_reads_at_slots,
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


@pytest.mark.parametrize("has_change_should_raise", [True, False])
def test_absence_validator_nonce_changes(has_change_should_raise):
    """Test nonce_changes_at_tx validator with present/absent changes."""
    alice = Address("0x000000000000000000000000000000000000000a")

    nonce_changes = [BalNonceChange(tx_index=1, post_nonce=1)]
    if has_change_should_raise:
        # add nonce change at tx 2 which should trigger failure
        nonce_changes.append(BalNonceChange(tx_index=2, post_nonce=2))

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                nonce_changes=nonce_changes,
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            # no nonce changes at tx 2
            alice: BalAccountExpectation(should_not_exist=[nonce_changes_at_tx(2)])
        }
    )

    if has_change_should_raise:
        with pytest.raises(Exception, match="Unexpected nonce change found at tx 2"):
            expectation.verify_against(actual_bal)
    else:
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize("has_change_should_raise", [True, False])
def test_absence_validator_balance_changes(has_change_should_raise):
    """Test balance_changes_at_tx validator with present/absent changes."""
    alice = Address("0x000000000000000000000000000000000000000a")

    balance_changes = [BalBalanceChange(tx_index=1, post_balance=100)]
    if has_change_should_raise:
        # add balance change at tx 2 which should trigger failure
        balance_changes.append(BalBalanceChange(tx_index=2, post_balance=200))

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                balance_changes=balance_changes,
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            alice: BalAccountExpectation(
                should_not_exist=[balance_changes_at_tx(2)],
            ),
        }
    )

    if has_change_should_raise:
        with pytest.raises(Exception, match="Unexpected balance change found at tx 2"):
            expectation.verify_against(actual_bal)
    else:
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize("has_change_should_raise", [True, False])
def test_absence_validator_storage_changes(has_change_should_raise):
    """Test storage_changes_at_slots validator with present/absent changes."""
    contract = Address("0x000000000000000000000000000000000000000c")

    storage_changes = [
        BalStorageSlot(
            slot=0x01,
            slot_changes=[BalStorageChange(tx_index=1, post_value=0x99)],
        )
    ]
    if has_change_should_raise:
        storage_changes.append(
            BalStorageSlot(
                slot=0x42,
                slot_changes=[BalStorageChange(tx_index=1, post_value=0xBEEF)],
            )
        )

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=contract,
                storage_changes=storage_changes,
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            # no storage changes at slot 0x42
            contract: BalAccountExpectation(should_not_exist=[storage_changes_at_slots(0x42)]),
        }
    )

    if has_change_should_raise:
        with pytest.raises(Exception, match="Unexpected storage change found at slot"):
            expectation.verify_against(actual_bal)
    else:
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize("has_read_should_raise", [True, False])
def test_absence_validator_storage_reads(has_read_should_raise):
    """Test storage_reads_at_slots validator with present/absent reads."""
    contract = Address("0x000000000000000000000000000000000000000c")

    # Create actual BAL with or without storage read at slot 0x42
    storage_reads = [StorageKey(0x01)]
    if has_read_should_raise:
        storage_reads.append(StorageKey(0x42))

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=contract,
                storage_reads=storage_reads,
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            # no storage reads at slot 0x42
            contract: BalAccountExpectation(should_not_exist=[storage_reads_at_slots(0x42)]),
        }
    )

    if has_read_should_raise:
        with pytest.raises(Exception, match="Unexpected storage read found at slot"):
            expectation.verify_against(actual_bal)
    else:
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize("has_change_should_raise", [True, False])
def test_absence_validator_code_changes(has_change_should_raise):
    """Test code_changes_at_tx validator with present/absent changes."""
    alice = Address("0x000000000000000000000000000000000000000a")

    code_changes = [BalCodeChange(tx_index=1, new_code=b"\x00")]
    if has_change_should_raise:
        # add code change at tx 2 which should trigger failure
        code_changes.append(BalCodeChange(tx_index=2, new_code=b"\x60\x00"))

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                code_changes=code_changes,
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            # no code changes at tx 2
            alice: BalAccountExpectation(should_not_exist=[code_changes_at_tx(2)]),
        }
    )

    if has_change_should_raise:
        with pytest.raises(Exception, match="Unexpected code change found at tx 2"):
            expectation.verify_against(actual_bal)
    else:
        expectation.verify_against(actual_bal)


def test_multiple_absence_validators():
    """Test multiple absence validators working together."""
    contract = Address("0x000000000000000000000000000000000000000c")

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=contract,
                nonce_changes=[],
                balance_changes=[],
                storage_changes=[
                    BalStorageSlot(
                        slot=0x01,
                        slot_changes=[BalStorageChange(tx_index=1, post_value=0x99)],
                    )
                ],
                storage_reads=[StorageKey(0x01)],
                code_changes=[],
            ),
        ]
    )

    # Test that multiple validators all pass
    expectation = BlockAccessListExpectation(
        account_expectations={
            contract: BalAccountExpectation(
                storage_changes=[
                    BalStorageSlot(
                        slot=0x01,
                        slot_changes=[BalStorageChange(tx_index=1, post_value=0x99)],
                    )
                ],
                should_not_exist=[
                    nonce_changes_at_tx(1, 2),  # No nonce changes
                    balance_changes_at_tx(1, 2),  # No balance changes
                    storage_changes_at_slots(0x42, 0x43),  # These slots not changed
                    storage_reads_at_slots(0x42, 0x43),  # These slots not read
                    code_changes_at_tx(1, 2),  # No code changes
                ],
            ),
        }
    )

    expectation.verify_against(actual_bal)


def test_absence_validator_with_multiple_tx_indices():
    """Test absence validators with multiple transaction indices."""
    alice = Address("0x000000000000000000000000000000000000000a")

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=alice,
                nonce_changes=[
                    # nonce changes at tx 1 and 3
                    BalNonceChange(tx_index=1, post_nonce=1),
                    BalNonceChange(tx_index=3, post_nonce=2),
                ],
            ),
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            alice: BalAccountExpectation(
                nonce_changes=[
                    BalNonceChange(tx_index=1, post_nonce=1),
                    BalNonceChange(tx_index=3, post_nonce=2),
                ],
                should_not_exist=[
                    # should not be changes at tx 2 and 4
                    nonce_changes_at_tx(2, 4),
                ],
            ),
        }
    )

    expectation.verify_against(actual_bal)

    expectation_fail = BlockAccessListExpectation(
        account_expectations={
            alice: BalAccountExpectation(
                should_not_exist=[
                    # wrongly forbid change at txs 1 and 2 (1 exists, so should fail)
                    nonce_changes_at_tx(1, 2),
                ],
            ),
        }
    )

    with pytest.raises(Exception, match="Unexpected nonce change found at tx 1"):
        expectation_fail.verify_against(actual_bal)
