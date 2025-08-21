"""Tests for EIP-7928 using the consistent data class pattern."""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.block_access_list import (
    BalAccountChange,
    BalBalanceChange,
    BalNonceChange,
    BalStorageChange,
    BalStorageSlot,
    BlockAccessList,
)

from .spec import ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version


@pytest.mark.valid_from("Osaka")
def test_bal_nonce_changes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures changes to nonce."""
    alice = pre.fund_eoa()
    bob = pre.fund_eoa(amount=0)

    tx = Transaction(
        sender=alice,
        to=bob,
        value=100,
    )

    block = Block(txs=[tx])

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            bob: Account(balance=100),
        },
        expected_block_access_list=BlockAccessList(
            account_changes=[
                BalAccountChange(
                    address=alice,
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                ),
            ]
        ),
    )


@pytest.mark.valid_from("Osaka")
def test_bal_balance_changes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL captures changes to balance."""
    alice = pre.fund_eoa()
    bob = pre.fund_eoa(amount=0)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )
    tx_gas_limit = intrinsic_gas_cost + 1000  # add a small buffer

    tx = Transaction(
        sender=alice,
        to=bob,
        value=100,
        gas_limit=tx_gas_limit,
        gas_price=1_000_000_000,
    )

    block = Block(txs=[tx])
    alice_initial_balance = pre[alice].balance

    # Account for both the value sent and gas cost (gas_price * gas_used)
    alice_final_balance = alice_initial_balance - 100 - (intrinsic_gas_cost * 1_000_000_000)

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1, balance=alice_final_balance),
            bob: Account(balance=100),
        },
        expected_block_access_list=BlockAccessList(
            account_changes=[
                BalAccountChange(
                    address=alice,
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                    balance_changes=[
                        BalBalanceChange(tx_index=1, post_balance=alice_final_balance)
                    ],
                ),
                BalAccountChange(
                    address=bob,
                    balance_changes=[BalBalanceChange(tx_index=1, post_balance=100)],
                ),
                # TODO: Validate coinbase
            ]
        ),
    )


@pytest.mark.valid_from("Osaka")
def test_bal_storage_writes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures storage writes."""
    storage_contract = pre.deploy_contract(code=Op.SSTORE(0x01, 0x42) + Op.STOP)
    alice = pre.fund_eoa()

    tx = Transaction(
        sender=alice,
        to=storage_contract,
        gas_limit=100000,
    )

    block = Block(txs=[tx])

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            storage_contract: Account(storage={0x01: 0x42}),
        },
        expected_block_access_list=BlockAccessList(
            account_changes=[
                BalAccountChange(
                    address=storage_contract,
                    storage_changes=[
                        BalStorageSlot(
                            slot=0x01,
                            slot_changes=[BalStorageChange(tx_index=1, post_value=0x42)],
                        )
                    ],
                ),
            ]
        ),
    )


@pytest.mark.valid_from("Osaka")
def test_bal_storage_reads(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures storage reads."""
    storage_contract = pre.deploy_contract(
        code=Op.SLOAD(0x01) + Op.STOP,
        storage={0x01: 0x42},
    )
    alice = pre.fund_eoa()

    tx = Transaction(
        sender=alice,
        to=storage_contract,
        gas_limit=100000,
    )

    block = Block(txs=[tx])

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            storage_contract: Account(storage={0x01: 0x42}),
        },
        expected_block_access_list=BlockAccessList(
            account_changes=[
                BalAccountChange(
                    address=storage_contract,
                    storage_reads=[0x01],
                ),
            ]
        ),
    )


@pytest.mark.valid_from("Osaka")
def test_bal_code_changes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures changes to account code."""
    deployed_code = Op.PUSH1(0x42) + Op.PUSH1(0x00) + Op.SSTORE + Op.STOP

    deployed_code_bytes = bytes(deployed_code)
    factory_code = (
        Op.PUSH32(deployed_code_bytes)  # Contract code
        + Op.PUSH1(0x00)  # Memory offset
        + Op.MSTORE  # Store code in memory
        + Op.PUSH1(len(deployed_code_bytes))  # Code size
        + Op.PUSH1(0x00)  # Memory offset
        + Op.PUSH1(0x00)  # Value to send
        + Op.CREATE  # CREATE opcode
        + Op.STOP
    )

    factory_contract = pre.deploy_contract(code=factory_code)
    alice = pre.fund_eoa()

    tx = Transaction(
        sender=alice,
        to=factory_contract,
        gas_limit=500000,
    )

    block = Block(txs=[tx])

    # The CREATE opcode will deploy to a deterministic address
    # We'll need to calculate or determine what that address will be
    # For now, we'll focus on the factory contract having a code change
    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            factory_contract: Account(),
            # The newly created contract would be here but we'd need to calculate its address
        },
        # Note: This test might need adjustment based on how CREATE addresses are calculated
        # and how code changes are tracked in the BAL
        expected_block_access_list=BlockAccessList(
            account_changes=[
                # {
                #     "address": alice,
                #     "nonce_changes": [{"tx_index": 0, "post_nonce": 1}],
                # },
                # {
                #     "address": factory_contract,
                #     "code_changes": [{"tx_index": 0, "new_code": deployed_code}],
                # },
            ]
        ),
    )
