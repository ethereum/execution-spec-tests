"""Tests for EIP-7928 for EIP-2930 transactions."""

import pytest

from ethereum_test_tools import (
    AccessList,
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Hash,
    Transaction,
)
from ethereum_test_tools import Opcodes as Op
from ethereum_test_types.block_access_list import (
    BalAccountExpectation,
    BalNonceChange,
    BalStorageChange,
    BalStorageSlot,
    BlockAccessListExpectation,
)

from .spec import ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version

pytestmark = pytest.mark.valid_from("Amsterdam")


def test_bal_2930_slot_listed_but_untouched(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL excludes untouched access list storage slots."""
    alice = pre.fund_eoa()
    pure_calculator = pre.deploy_contract(
        # Pure add operation
        Op.ADD(35, 7)
    )

    access_list = AccessList(
        address=pure_calculator,
        storage_keys=[Hash(0x1)],
    )

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    gas_limit = (
        intrinsic_gas_calculator(
            calldata=b"",
            contract_creation=False,
            access_list=[access_list],
        )
        + 1000
    )  # intrinsic + buffer

    tx = Transaction(
        ty=1, sender=alice, to=pure_calculator, gas_limit=gas_limit, access_list=[access_list]
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                ),
                # The address excluded from BAL since state is not accessed
                pure_calculator: None,
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
        },
    )


def test_bal_2930_slot_listed_and_unlisted_writes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """
    Ensure BAL includes storage writes regardless of access list presence.
    """
    alice = pre.fund_eoa()
    storage_writer = pre.deploy_contract(code=Op.SSTORE(0x01, 0x42) + Op.SSTORE(0x02, 0x43))

    # Access list only includes slot 0x01, but contract writes to both
    # 0x01 and 0x02
    access_list = AccessList(
        address=storage_writer,
        storage_keys=[Hash(0x01)],
    )

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    gas_limit = (
        intrinsic_gas_calculator(
            calldata=b"",
            contract_creation=False,
            access_list=[access_list],
        )
        + 50000
    )  # intrinsic + buffer for storage writes

    tx = Transaction(
        ty=1, sender=alice, to=storage_writer, gas_limit=gas_limit, access_list=[access_list]
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                ),
                storage_writer: BalAccountExpectation(
                    storage_changes=[
                        BalStorageSlot(
                            slot=0x01,
                            slot_changes=[BalStorageChange(tx_index=1, post_value=0x42)],
                        ),
                        BalStorageSlot(
                            slot=0x02,
                            slot_changes=[BalStorageChange(tx_index=1, post_value=0x43)],
                        ),
                    ],
                ),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            storage_writer: Account(storage={0x01: 0x42, 0x02: 0x43}),
        },
    )


def test_bal_2930_slot_listed_and_unlisted_reads(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL includes storage reads regardless of access list presence."""
    alice = pre.fund_eoa()
    storage_reader = pre.deploy_contract(
        code=Op.SLOAD(0x01) + Op.SLOAD(0x02),
        storage={0x01: 0x42, 0x02: 0x43},  # Pre-populate storage with values
    )

    # Access list only includes slot 0x01, but contract reads from both
    # 0x01 and 0x02
    access_list = AccessList(
        address=storage_reader,
        storage_keys=[Hash(0x01)],
    )

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    gas_limit = (
        intrinsic_gas_calculator(
            calldata=b"",
            contract_creation=False,
            access_list=[access_list],
        )
        + 50000
    )  # intrinsic + buffer for storage reads

    tx = Transaction(
        ty=1, sender=alice, to=storage_reader, gas_limit=gas_limit, access_list=[access_list]
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                ),
                storage_reader: BalAccountExpectation(
                    storage_reads=[0x01, 0x02],
                ),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            storage_reader: Account(storage={0x01: 0x42, 0x02: 0x43}),
        },
    )
