"""Tests for EIP-7928 using the consistent data class pattern."""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.block_access_list import (
    BalAccountChange,
    BalBalanceChange,
    BalCodeChange,
    BalNonceChange,
    BalStorageChange,
    BalStorageSlot,
    BlockAccessList,
)

from .spec import ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version


@pytest.mark.valid_from("Amsterdam")
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


@pytest.mark.valid_from("Amsterdam")
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
    alice_account = pre[alice]
    assert alice_account is not None, "Alice account should exist"
    alice_initial_balance = alice_account.balance

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


@pytest.mark.valid_from("Amsterdam")
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


@pytest.mark.valid_from("Amsterdam")
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


@pytest.mark.valid_from("Amsterdam")
def test_bal_code_changes(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures changes to account code."""
    runtime_code = Op.STOP
    runtime_code_bytes = bytes(runtime_code)

    init_code = (
        Op.PUSH1(len(runtime_code_bytes))  # size = 1
        + Op.DUP1  # duplicate size for return
        + Op.PUSH1(0x0C)  # offset in init code where runtime code starts
        + Op.PUSH1(0x00)  # dest offset
        + Op.CODECOPY  # copy runtime code to memory
        + Op.PUSH1(0x00)  # memory offset for return
        + Op.RETURN  # return runtime code
        + runtime_code  # the actual runtime code to deploy
    )
    init_code_bytes = bytes(init_code)

    # Factory contract that uses CREATE to deploy
    factory_code = (
        # Push init code to memory
        Op.PUSH32(init_code_bytes)
        + Op.PUSH1(0x00)
        + Op.MSTORE  # Store at memory position 0
        # CREATE parameters: value, offset, size
        + Op.PUSH1(len(init_code_bytes))  # size of init code
        + Op.PUSH1(32 - len(init_code_bytes))  # offset in memory (account for padding)
        + Op.PUSH1(0x00)  # value = 0 (no ETH sent)
        + Op.CREATE  # Deploy the contract
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

    created_contract = compute_create_address(address=factory_contract, nonce=1)

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            factory_contract: Account(nonce=2),  # incremented by CREATE to 2
            created_contract: Account(
                code=runtime_code_bytes,
                storage={},
            ),
        },
        expected_block_access_list=BlockAccessList(
            account_changes=[
                BalAccountChange(
                    address=alice,
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                ),
                BalAccountChange(
                    address=factory_contract,
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=2)],
                ),
                BalAccountChange(
                    address=created_contract,
                    code_changes=[BalCodeChange(tx_index=1, new_code=runtime_code_bytes)],
                ),
            ]
        ),
    )
