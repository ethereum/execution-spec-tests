"""Test cases for effective no-op or no-op adjacent operations in EIP-7928."""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import Alloc, Block, BlockchainTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.block_access_list import (
    BalAccountExpectation,
    BalBalanceChange,
    BalNonceChange,
    BalStorageChange,
    BalStorageSlot,
    BlockAccessListExpectation,
)

from .spec import ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version

pytestmark = pytest.mark.valid_from("Amsterdam")


def test_bal_self_transfer(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Test that BAL correctly handles self-transfers."""
    start_balance = 1_000_000
    alice = pre.fund_eoa(amount=start_balance)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    tx = Transaction(
        sender=alice, to=alice, gas_limit=intrinsic_gas_cost, value=100, gas_price=0xA
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                    balance_changes=[
                        BalBalanceChange(
                            tx_index=1,
                            post_balance=start_balance - intrinsic_gas_cost * tx.gas_price,
                        )
                    ],
                )
            }
        ),
    )

    blockchain_test(pre=pre, blocks=[block], post={})


def test_bal_zero_value_transfer(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Test that BAL correctly handles zero-value transfers."""
    start_balance = 1_000_000
    alice = pre.fund_eoa(amount=start_balance)
    bob = pre.fund_eoa(amount=100)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    tx = Transaction(sender=alice, to=bob, gas_limit=intrinsic_gas_cost, value=0, gas_price=0xA)

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                    balance_changes=[
                        BalBalanceChange(
                            tx_index=1,
                            post_balance=start_balance - intrinsic_gas_cost * tx.gas_price,
                        )
                    ],
                ),
                # Include the address; omit from balance_changes.
                bob: BalAccountExpectation(balance_changes=[]),
            }
        ),
    )

    blockchain_test(pre=pre, blocks=[block], post={})


def test_bal_noop_storage_write(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
):
    """Test that BAL correctly handles no-op storage write."""
    alice = pre.fund_eoa()
    storage_contract = pre.deploy_contract(code=Op.SSTORE(0x01, 0x42), storage={0x01: 0x42})

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    gas_limit = (
        intrinsic_gas_calculator(
            calldata=b"",
            contract_creation=False,
            access_list=[],
        )
        # Sufficient gas for write
        + fork.gas_costs().G_COLD_SLOAD
        + fork.gas_costs().G_COLD_ACCOUNT_ACCESS
        + fork.gas_costs().G_STORAGE_SET
        + fork.gas_costs().G_BASE * 10  # Buffer for push
    )

    tx = Transaction(sender=alice, to=storage_contract, gas_limit=gas_limit, gas_price=0xA)

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                ),
                storage_contract: BalAccountExpectation(storage_changes=[]),
            }
        ),
    )

    blockchain_test(pre=pre, blocks=[block], post={})


@pytest.mark.parametrize(
    "abort_opcode",
    [
        pytest.param(Op.REVERT(0, 0), id="revert"),
        pytest.param(Op.INVALID, id="invalid"),
    ],
)
def test_bal_aborted_transaction_storage_access(
    pre: Alloc, blockchain_test: BlockchainTestFiller, abort_opcode: Op
):
  """Ensure BAL captures storage access in aborted transactions correctly"""
    alice = pre.fund_eoa()

    storage_contract = pre.deploy_contract(
        code=Op.SLOAD(0x01) + Op.SSTORE(0x02, 0x42) + abort_opcode,
        storage={0x01: 0x10},  # Pre-existing value in slot 0x01
    )

    tx = Transaction(sender=alice, to=storage_contract, gas_limit=5_000_000, gas_price=0xA)

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)]
                ),
                storage_contract: BalAccountExpectation(
                    storage_changes=[],
                    storage_reads=[0x01, 0x02],
                ),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={},
    )


def test_bal_aborted_transaction(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
):
    """Ensure BAL captures aborted transactions correctly."""
    alice = pre.fund_eoa()
    bob = pre.fund_eoa(amount=0)

    # TargetContract: simple contract
    call_target = pre.deploy_contract(code=Op.STOP)
    staticcall_target = pre.deploy_contract(code=Op.STOP)
    delegatecall_target = pre.deploy_contract(code=Op.STOP)

    # AbortContract: reads storage, writes storage, then reverts
    abort_contract = pre.deploy_contract(
        balance=100,
        code=(
            # Act 1: Read storage
            Op.SLOAD(0x01)
            # Act 2: Write to storage
            + Op.SSTORE(0x02, 0x42)
            # Act 3: Send 100 wei to bob
            + Op.CALL(0, bob, 100, 0, 0, 0, 0)
            # Act 4: Call
            + Op.CALL(0, call_target, 0, 0, 0, 0, 0)
            # Act 5: create contract
            + Op.STATICCALL(0, staticcall_target, 0, 0, 0, 0)
            # + Op.created_contract()
            + Op.DELEGATECALL(0, delegatecall_target, 0, 0, 0, 0)
            # Final act: Abort!
            + Op.REVERT(0, 0)  # Abort the transaction
        ),
        storage={0x01: 0x10},  # Pre-existing value in slot 0x01
    )

    tx = Transaction(sender=alice, to=abort_contract, gas_limit=5_000_000, gas_price=0xA)

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                bob: BalAccountExpectation(
                    balance_changes=[BalBalanceChange(tx_index=1, post_balance=100)]
                ),
                abort_contract: BalAccountExpectation(
                    storage_reads=[0x01],
                    storage_changes=[
                        BalStorageSlot(
                            slot=0x02, slot_changes=[BalStorageChange(tx_index=1, post_value=0x42)]
                        )
                    ],
                ),
                call_target: BalAccountExpectation(),
                staticcall_target: BalAccountExpectation(),
                # delegatecall_target: BalAccountExpectation(),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={},
    )
