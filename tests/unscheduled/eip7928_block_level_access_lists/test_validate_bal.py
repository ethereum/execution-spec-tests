"""Tests for validating EIP-7928: Block-level Access Lists (BAL)."""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
)

from .spec import ACTIVATION_FORK_NAME, ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version


@pytest.mark.valid_from(ACTIVATION_FORK_NAME)
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
        block_access_list={
            "account_changes": [
                {
                    "address": alice,
                    "nonce_changes": [{"tx_index": 0, "post_nonce": 1}],
                },
            ]
        },
    )


@pytest.mark.valid_from(ACTIVATION_FORK_NAME)
def test_bal_balance_changes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures changes to balance."""
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
        block_access_list={
            "account_changes": [
                {
                    "address": alice,
                    "balance_changes": [
                        {
                            "tx_index": 0,
                            "post_balance": pre[alice].balance - 100,
                        }
                    ],
                },
                {
                    "address": bob,
                    "balance_changes": [{"tx_index": 0, "post_balance": 100}],
                },
                # TODO: Validate coinbase
            ]
        },
    )


@pytest.mark.valid_from(ACTIVATION_FORK_NAME)
def test_bal_storage_writes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures storage writes."""
    from ethereum_test_tools.vm.opcode import Opcodes as Op

    # Alice calls contract that writes to storage slot 0x01
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
        block_access_list={
            "account_changes": [
                {
                    "address": storage_contract,
                    "storage_changes": [
                        {
                            "slot": 0x01,
                            "slot_changes": [
                                {
                                    "tx_index": 0,
                                    "post_value": 0x42,
                                }
                            ],
                        }
                    ],
                },
            ]
        },
    )


@pytest.mark.valid_from(ACTIVATION_FORK_NAME)
def test_bal_storage_reads(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures storage reads."""
    from ethereum_test_tools.vm.opcode import Opcodes as Op

    storage_contract = pre.deploy_contract(
        code=Op.SLOAD(0x01) + Op.STOP,
        storage={0x01: 0x42},  # Pre-populate storage
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
        block_access_list={
            "account_changes": [
                {
                    "address": storage_contract,
                    "storage_reads": [0x01],
                },
            ]
        },
    )


@pytest.mark.valid_from(ACTIVATION_FORK_NAME)
def test_bal_code_changes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures changes to account code."""
    from ethereum_test_tools.vm.opcode import Opcodes as Op

    deployed_code = Op.PUSH1(0x42) + Op.PUSH1(0x00) + Op.SSTORE + Op.STOP

    factory_code = (
        Op.PUSH32(deployed_code)  # Contract code
        + Op.PUSH1(0x00)  # Memory offset
        + Op.MSTORE  # Store code in memory
        + Op.PUSH1(len(deployed_code))  # Code size
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
        gas_limit=200000,
    )

    block = Block(txs=[tx])

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
        },
        block_access_list={
            "account_changes": [
                {
                    "address": alice,
                    "nonce_changes": [{"tx_index": 0, "post_nonce": 1}],
                },
                {
                    "address": factory_contract,
                    "code_changes": [{"tx_index": 0, "new_code": deployed_code}],
                },
            ]
        },
    )
