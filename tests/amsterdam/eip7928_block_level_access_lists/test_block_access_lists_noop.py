"""Test cases for effective no-op or no-op adjacent operations in EIP-7928."""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
)
from ethereum_test_tools import (
    Opcodes as Op,
)
from ethereum_test_types.block_access_list import (
    BalAccountExpectation,
    BalBalanceChange,
    BalNonceChange,
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
    intrinsic_gas_cost = intrinsic_gas_calculator()

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
    intrinsic_gas_cost = intrinsic_gas_calculator()

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


def test_bal_pure_contract_call(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
):
    """Test that BAL captures contract access for pure computation calls."""
    alice = pre.fund_eoa()
    pure_contract = pre.deploy_contract(code=Op.ADD(0x3, 0x2))

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    gas_limit = intrinsic_gas_calculator() + 5_000  # Buffer

    tx = Transaction(sender=alice, to=pure_contract, gas_limit=gas_limit, gas_price=0xA)

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                ),
                # Ensure called contract is tracked
                pure_contract: BalAccountExpectation.empty(),
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
        intrinsic_gas_calculator()
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
                storage_contract: BalAccountExpectation(
                    storage_reads=[0x01],
                    storage_changes=[],
                ),
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
def test_bal_aborted_storage_access(
    pre: Alloc, blockchain_test: BlockchainTestFiller, abort_opcode: Op
):
    """Ensure BAL captures storage access in aborted transactions correctly."""
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


@pytest.mark.parametrize(
    "account_access_opcode",
    [
        pytest.param(lambda target_addr: Op.BALANCE(target_addr), id="balance"),
        pytest.param(lambda target_addr: Op.EXTCODESIZE(target_addr), id="extcodesize"),
        pytest.param(lambda target_addr: Op.EXTCODECOPY(target_addr, 0, 0, 32), id="extcodecopy"),
        pytest.param(lambda target_addr: Op.EXTCODEHASH(target_addr), id="extcodehash"),
        pytest.param(lambda target_addr: Op.CALL(0, target_addr, 50, 0, 0, 0, 0), id="call"),
        pytest.param(
            lambda target_addr: Op.CALLCODE(0, target_addr, 0, 0, 0, 0, 0), id="callcode"
        ),
        pytest.param(
            lambda target_addr: Op.DELEGATECALL(0, target_addr, 0, 0, 0, 0), id="delegatecall"
        ),
        pytest.param(
            lambda target_addr: Op.STATICCALL(0, target_addr, 0, 0, 0, 0), id="staticcall"
        ),
    ],
)
@pytest.mark.parametrize(
    "abort_opcode",
    [
        pytest.param(Op.REVERT(0, 0), id="revert"),
        pytest.param(Op.INVALID, id="invalid"),
    ],
)
def test_bal_aborted_account_access(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    account_access_opcode,
    abort_opcode: Op,
):
    """Ensure BAL captures account access in aborted transactions."""
    alice = pre.fund_eoa()
    target_contract = pre.deploy_contract(code=Op.STOP)

    abort_contract = pre.deploy_contract(
        balance=100,
        code=account_access_opcode(target_contract) + abort_opcode,
    )

    tx = Transaction(sender=alice, to=abort_contract, gas_limit=5_000_000, gas_price=0xA)

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)]
                ),
                target_contract: BalAccountExpectation.empty(),
                abort_contract: BalAccountExpectation.empty(),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={},
    )
