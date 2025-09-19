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
    BlockAccessListValidationError,
    absence_validators,
)
from ethereum_test_types.block_access_list.absence_validators import (
    no_balance_changes,
    no_code_changes,
    no_nonce_changes,
    no_storage_changes,
    no_storage_reads,
)


def test_address_exclusion_validation_passes():
    """Test that address exclusion works when address is not in BAL."""
    alice = Address(0xA)
    bob = Address(0xB)

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
    alice = Address(0xA)
    bob = Address(0xB)

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

    with pytest.raises(BlockAccessListValidationError, match="should not be in BAL but was found"):
        expectation.verify_against(actual_bal)


def test_empty_list_validation():
    """Test that empty list validates correctly."""
    alice = Address(0xA)

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
    alice = Address(0xA)

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

    with pytest.raises(
        BlockAccessListValidationError,
        match="Expected balance_changes to be empty",
    ):
        expectation.verify_against(actual_bal)


def test_partial_validation():
    """Test that unset fields are not validated."""
    alice = Address(0xA)

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
    contract = Address(0xC)

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
    alice = Address(0xA)
    bob = Address(0xB)

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

    with pytest.raises(
        BlockAccessListValidationError, match="Expected address .* not found in actual BAL"
    ):
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize(
    "addresses,error_message",
    [
        (
            [
                Address(0xB),
                Address(0xA),  # should come first
            ],
            "BAL addresses not in lexicographic order per EIP-7928",
        ),
        (
            [
                Address(0x1),
                Address(0x3),
                Address(0x2),
            ],
            "BAL addresses not in lexicographic order per EIP-7928",
        ),
    ],
)
def test_actual_bal_address_ordering_validation(addresses, error_message):
    """Test that actual BAL must have addresses in lexicographic order."""
    # Create BAL with addresses in the given order
    actual_bal = BlockAccessList(
        [BalAccountChange(address=addr, nonce_changes=[]) for addr in addresses]
    )

    expectation = BlockAccessListExpectation(account_expectations={})

    with pytest.raises(BlockAccessListValidationError, match=error_message):
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize(
    "storage_slots,error_message",
    [
        (
            [StorageKey(0x02), StorageKey(0x01)],  # 0x02 before 0x01
            "Storage slots not in lexicographic order",
        ),
        (
            [StorageKey(0x01), StorageKey(0x03), StorageKey(0x02)],
            "Storage slots not in lexicographic order",
        ),
    ],
)
def test_actual_bal_storage_slot_ordering(storage_slots, error_message):
    """Test that actual BAL must have storage slots in lexicographic order."""
    addr = Address(0xA)

    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=addr,
                storage_changes=[
                    BalStorageSlot(slot=slot, slot_changes=[]) for slot in storage_slots
                ],
            )
        ]
    )

    expectation = BlockAccessListExpectation(account_expectations={})

    with pytest.raises(BlockAccessListValidationError, match=error_message):
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize(
    "storage_reads,error_message",
    [
        ([StorageKey(0x02), StorageKey(0x01)], "Storage reads not in lexicographic order"),
        (
            [StorageKey(0x01), StorageKey(0x03), StorageKey(0x02)],
            "Storage reads not in lexicographic order",
        ),
    ],
)
def test_actual_bal_storage_reads_ordering(storage_reads, error_message):
    """Test that actual BAL must have storage reads in lexicographic order."""
    addr = Address(0xA)

    actual_bal = BlockAccessList([BalAccountChange(address=addr, storage_reads=storage_reads)])

    expectation = BlockAccessListExpectation(account_expectations={})

    with pytest.raises(BlockAccessListValidationError, match=error_message):
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize(
    "field_name",
    ["nonce_changes", "balance_changes", "code_changes"],
)
def test_actual_bal_tx_indices_ordering(field_name):
    """Test that actual BAL must have tx indices in ascending order."""
    addr = Address(0xA)

    tx_indices = [2, 3, 1]  # out of order

    changes = []
    if field_name == "nonce_changes":
        changes = [BalNonceChange(tx_index=idx, post_nonce=1) for idx in tx_indices]
    elif field_name == "balance_changes":
        changes = [BalBalanceChange(tx_index=idx, post_balance=100) for idx in tx_indices]
    elif field_name == "code_changes":
        changes = [BalCodeChange(tx_index=idx, new_code=b"code") for idx in tx_indices]

    actual_bal = BlockAccessList([BalAccountChange(address=addr, **{field_name: changes})])

    expectation = BlockAccessListExpectation(account_expectations={})

    with pytest.raises(
        BlockAccessListValidationError,
        match="tx_indices not in ascending order",
    ):
        expectation.verify_against(actual_bal)


def test_expected_addresses_auto_sorted():
    """
    Test that expected addresses are automatically sorted before comparison.

    The BAL *Expectation address order should not matter for the dict.
    We DO, however, validate that the actual BAL (from t8n) is sorted correctly.
    """
    alice = Address(0xA)
    bob = Address(0xB)
    charlie = Address(0xC)

    actual_bal = BlockAccessList(
        [
            BalAccountChange(address=alice, nonce_changes=[]),
            BalAccountChange(address=bob, nonce_changes=[]),
            BalAccountChange(address=charlie, nonce_changes=[]),
        ]
    )

    # expectation order should not matter for the dict though we DO validate
    # that the _actual_ BAL (from t8n) is sorted correctly
    expectation = BlockAccessListExpectation(
        account_expectations={
            charlie: BalAccountExpectation(nonce_changes=[]),
            alice: BalAccountExpectation(nonce_changes=[]),
            bob: BalAccountExpectation(nonce_changes=[]),
        }
    )

    expectation.verify_against(actual_bal)


@pytest.mark.parametrize(
    "expected_slots,should_pass",
    [
        # Correct order - should pass
        ([StorageKey(0x01), StorageKey(0x02), StorageKey(0x03)], True),
        # Partial subset in correct order - should pass
        ([StorageKey(0x01), StorageKey(0x03)], True),
        # Out of order - should fail
        ([StorageKey(0x01), StorageKey(0x03), StorageKey(0x02)], False),
        # Wrong order from start - should fail
        ([StorageKey(0x02), StorageKey(0x01)], False),
    ],
)
def test_expected_storage_slots_ordering(expected_slots, should_pass):
    """Test that expected storage slots must be defined in correct order."""
    addr = Address(0xA)

    # Actual BAL with storage slots in correct order
    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=addr,
                storage_changes=[
                    BalStorageSlot(slot=StorageKey(0x01), slot_changes=[]),
                    BalStorageSlot(slot=StorageKey(0x02), slot_changes=[]),
                    BalStorageSlot(slot=StorageKey(0x03), slot_changes=[]),
                ],
            )
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            addr: BalAccountExpectation(
                storage_changes=[
                    BalStorageSlot(slot=slot, slot_changes=[]) for slot in expected_slots
                ],
            ),
        }
    )

    if should_pass:
        expectation.verify_against(actual_bal)
    else:
        with pytest.raises(
            BlockAccessListValidationError,
            match="not found or not in correct order",
        ):
            expectation.verify_against(actual_bal)


@pytest.mark.parametrize(
    "expected_reads,should_pass",
    [
        # Correct order - should pass
        ([StorageKey(0x01), StorageKey(0x02), StorageKey(0x03)], True),
        # Partial subset in correct order - should pass
        ([StorageKey(0x02), StorageKey(0x03)], True),
        # Out of order - should fail
        ([StorageKey(0x03), StorageKey(0x02)], False),
        # Wrong order with all elements - should fail
        ([StorageKey(0x01), StorageKey(0x03), StorageKey(0x02)], False),
    ],
)
def test_expected_storage_reads_ordering(expected_reads, should_pass):
    """Test that expected storage reads must be defined in correct order."""
    addr = Address(0xA)

    # Actual BAL with storage reads in correct order
    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=addr,
                storage_reads=[StorageKey(0x01), StorageKey(0x02), StorageKey(0x03)],
            )
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            addr: BalAccountExpectation(storage_reads=expected_reads),
        }
    )

    if should_pass:
        expectation.verify_against(actual_bal)
    else:
        with pytest.raises(
            BlockAccessListValidationError,
            match="not found or not in correct order",
        ):
            expectation.verify_against(actual_bal)


@pytest.mark.parametrize(
    "expected_tx_indices,should_pass",
    [
        # Correct order - should pass
        ([1, 2, 3], True),
        # Partial subset in correct order - should pass
        ([1, 3], True),
        # Single element - should pass
        ([2], True),
        # Out of order - should fail
        ([2, 1], False),
        # Wrong order with all elements - should fail
        ([1, 3, 2], False),
    ],
)
def test_expected_tx_indices_ordering(expected_tx_indices, should_pass):
    """Test that expected tx indices must be defined in correct order."""
    addr = Address(0xA)

    # actual BAL with tx indices in correct order
    actual_bal = BlockAccessList(
        [
            BalAccountChange(
                address=addr,
                nonce_changes=[
                    BalNonceChange(tx_index=1, post_nonce=1),
                    BalNonceChange(tx_index=2, post_nonce=2),
                    BalNonceChange(tx_index=3, post_nonce=3),
                ],
            )
        ]
    )

    expectation = BlockAccessListExpectation(
        account_expectations={
            addr: BalAccountExpectation(
                nonce_changes=[
                    BalNonceChange(tx_index=idx, post_nonce=idx) for idx in expected_tx_indices
                ],
            ),
        }
    )

    if should_pass:
        expectation.verify_against(actual_bal)
    else:
        with pytest.raises(
            BlockAccessListValidationError,
            match="not found or not in correct order",
        ):
            expectation.verify_against(actual_bal)


@pytest.mark.parametrize("has_change_should_raise", [True, False])
def test_absence_validator_nonce_changes(has_change_should_raise):
    """Test nonce_changes_at_tx validator with present/absent changes."""
    alice = Address(0xA)

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
            alice: BalAccountExpectation(should_not_exist=[no_nonce_changes({2})])
        }
    )

    if has_change_should_raise:
        with pytest.raises(Exception, match="Unexpected nonce change found at tx 0x2"):
            expectation.verify_against(actual_bal)
    else:
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize("has_change_should_raise", [True, False])
def test_absence_validator_balance_changes(has_change_should_raise):
    """Test balance_changes_at_tx validator with present/absent changes."""
    alice = Address(0xA)

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
                should_not_exist=[no_balance_changes({2})],
            ),
        }
    )

    if has_change_should_raise:
        with pytest.raises(
            Exception,
            match="Unexpected balance change found at tx 0x2",
        ):
            expectation.verify_against(actual_bal)
    else:
        expectation.verify_against(actual_bal)


@pytest.mark.parametrize("has_change_should_raise", [True, False])
def test_absence_validator_storage_changes(has_change_should_raise):
    """Test storage_changes_at_slots validator with present/absent changes."""
    contract = Address(0xC)

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
            contract: BalAccountExpectation(should_not_exist=[no_storage_changes(slots={0x42})]),
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
    contract = Address(0xC)

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
            contract: BalAccountExpectation(should_not_exist=[no_storage_reads({0x42})]),
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
    alice = Address(0xA)

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
            alice: BalAccountExpectation(should_not_exist=[no_code_changes({2})]),
        }
    )

    if has_change_should_raise:
        with pytest.raises(Exception, match="Unexpected code change found at tx 0x2"):
            expectation.verify_against(actual_bal)
    else:
        expectation.verify_against(actual_bal)


def test_multiple_absence_validators():
    """Test multiple absence validators working together."""
    contract = Address(0xC)

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
                    no_nonce_changes({1, 2}),  # No nonce changes at tx 1 or 2
                    no_balance_changes({1, 2}),  # No balance changes at tx 1 or 2
                    no_storage_changes(slots={0x42, 0x43}),  # These slots not changed
                    no_storage_reads({0x42, 0x43}),  # These slots not read
                    no_code_changes({1, 2}),  # No code changes at tx 1 or 2
                ],
            ),
        }
    )

    expectation.verify_against(actual_bal)


def test_absence_validator_with_multiple_tx_indices():
    """Test absence validators with multiple transaction indices."""
    alice = Address(0xA)

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
                    no_nonce_changes({2, 4}),
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
                    no_nonce_changes({1, 2}),
                ],
            ),
        }
    )

    with pytest.raises(Exception, match="Unexpected nonce change found at tx 0x1"):
        expectation_fail.verify_against(actual_bal)


@pytest.mark.parametrize(
    "validator_func,field_name,changes,error_pattern",
    [
        (
            no_nonce_changes(),
            "nonce_changes",
            [BalNonceChange(tx_index=1, post_nonce=1)],
            "Unexpected nonce change found at tx",
        ),
        (
            no_balance_changes(),
            "balance_changes",
            [BalBalanceChange(tx_index=2, post_balance=100)],
            "Unexpected balance change found at tx",
        ),
        (
            no_code_changes(),
            "code_changes",
            [BalCodeChange(tx_index=3, new_code=b"\x60\x00")],
            "Unexpected code change found at tx",
        ),
        (
            no_storage_reads(),
            "storage_reads",
            [StorageKey(0x42)],
            "Unexpected storage read found at slot",
        ),
        (
            no_storage_changes(),
            "storage_changes",
            [
                BalStorageSlot(
                    slot=0x01, slot_changes=[BalStorageChange(tx_index=1, post_value=99)]
                )
            ],
            "Unexpected storage change found at slot",
        ),
    ],
)
def test_absence_validator_forbids_all(validator_func, field_name, changes, error_pattern):
    """Test that validators without specific indices/slots forbid ALL changes."""
    addr = Address(0xA)

    actual_bal = BlockAccessList([BalAccountChange(address=addr, **{field_name: changes})])

    expectation = BlockAccessListExpectation(
        account_expectations={
            addr: BalAccountExpectation(should_not_exist=[validator_func]),
        }
    )

    with pytest.raises(Exception, match=error_pattern):
        expectation.verify_against(actual_bal)


def test_all_absence_validators_use_validate_call():
    """Test that all exported absence validators use @validate_call decorator."""
    validator_names = [name for name in absence_validators.__all__ if name != "AbsenceValidator"]

    for name in validator_names:
        func = getattr(absence_validators, name)

        assert hasattr(func, "__wrapped__"), (
            f"{name} is not decorated with `@validate_call`. "
            "All validators must use `@validate_call(validate_return=True)`."
        )
