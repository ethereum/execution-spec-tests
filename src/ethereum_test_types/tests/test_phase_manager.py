"""Test suite for TestPhaseManager functionality."""

import pytest

from ethereum_test_base_types import Address
from ethereum_test_tools import Block, Transaction

from ..phase_manager import TestPhase, TestPhaseManager


def test_test_phase_enum_values():
    """Test that TestPhase enum has correct values."""
    assert TestPhase.SETUP.value == "setup"
    assert TestPhase.EXECUTION.value == "execution"


def test_phase_manager_initialization():
    """Test TestPhaseManager initialization."""
    manager = TestPhaseManager()
    assert len(manager.setup_transactions) == 0
    assert len(manager.setup_blocks) == 0
    assert len(manager.execution_transactions) == 0
    assert len(manager.execution_blocks) == 0
    assert manager.get_current_phase() == TestPhase.EXECUTION


def test_phase_manager_accepts_args_kwargs():
    """Test that __init__ accepts arbitrary args and kwargs."""
    # These should not cause errors
    manager1 = TestPhaseManager()
    manager2 = TestPhaseManager("some_arg")
    manager3 = TestPhaseManager(some_kwarg="value")
    manager4 = TestPhaseManager("arg1", "arg2", kwarg1="val1", kwarg2="val2")

    # All should have the same initialization
    for manager in [manager1, manager2, manager3, manager4]:
        assert len(manager.setup_transactions) == 0
        assert len(manager.setup_blocks) == 0
        assert len(manager.execution_transactions) == 0
        assert len(manager.execution_blocks) == 0
        assert manager.get_current_phase() == TestPhase.EXECUTION


def test_add_transaction_execution_phase():
    """Test adding transaction in execution phase."""
    manager = TestPhaseManager()
    tx = Transaction(to=Address(0x123), value=100, gas_limit=21000)

    manager.add_transaction(tx)

    assert len(manager.execution_transactions) == 1
    assert manager.execution_transactions[0] == tx
    assert tx.test_phase == TestPhase.EXECUTION.value
    assert len(manager.setup_transactions) == 0


def test_add_transaction_setup_phase():
    """Test adding transaction in setup phase."""
    manager = TestPhaseManager()
    tx = Transaction(to=Address(0x456), value=50, gas_limit=21000)

    with manager.setup():
        manager.add_transaction(tx)

    assert len(manager.setup_transactions) == 1
    assert manager.setup_transactions[0] == tx
    assert tx.test_phase == TestPhase.SETUP.value
    assert len(manager.execution_transactions) == 0


def test_add_block_execution_phase():
    """Test adding block in execution phase."""
    manager = TestPhaseManager()
    tx1 = Transaction(to=Address(0x111), value=100, gas_limit=21000)
    tx2 = Transaction(to=Address(0x222), value=200, gas_limit=21000)
    block = Block(txs=[tx1, tx2])

    manager.add_block(block)

    assert len(manager.execution_blocks) == 1
    assert manager.execution_blocks[0] == block
    assert tx1.test_phase == TestPhase.EXECUTION.value
    assert tx2.test_phase == TestPhase.EXECUTION.value
    assert len(manager.setup_blocks) == 0


def test_add_block_setup_phase():
    """Test adding block in setup phase."""
    manager = TestPhaseManager()
    tx1 = Transaction(to=Address(0x333), value=100, gas_limit=21000)
    tx2 = Transaction(to=Address(0x444), value=200, gas_limit=21000)
    block = Block(txs=[tx1, tx2])

    with manager.setup():
        manager.add_block(block)

    assert len(manager.setup_blocks) == 1
    assert manager.setup_blocks[0] == block
    assert tx1.test_phase == TestPhase.SETUP.value
    assert tx2.test_phase == TestPhase.SETUP.value
    assert len(manager.execution_blocks) == 0


@pytest.mark.parametrize(
    ["num_setup_txs", "num_setup_blocks", "num_exec_txs", "num_exec_blocks"],
    [
        pytest.param(0, 0, 1, 0, id="exec_tx_only"),
        pytest.param(1, 0, 0, 0, id="setup_tx_only"),
        pytest.param(0, 1, 0, 0, id="setup_block_only"),
        pytest.param(0, 0, 0, 1, id="exec_block_only"),
        pytest.param(2, 1, 3, 2, id="mixed_operations"),
        pytest.param(5, 0, 0, 5, id="many_items"),
    ],
)
def test_mixed_operations(num_setup_txs, num_setup_blocks, num_exec_txs, num_exec_blocks):
    """Test mixed operations across phases."""
    manager = TestPhaseManager()

    # Add setup items
    with manager.setup():
        for i in range(num_setup_txs):
            tx = Transaction(to=Address(0x1000 + i), value=i * 10, gas_limit=21000)
            manager.add_transaction(tx)

        for i in range(num_setup_blocks):
            tx = Transaction(to=Address(0x2000 + i), value=i * 100, gas_limit=21000)
            block = Block(txs=[tx])
            manager.add_block(block)

    # Add execution items
    for i in range(num_exec_txs):
        tx = Transaction(to=Address(0x3000 + i), value=i * 20, gas_limit=21000)
        manager.add_transaction(tx)

    for i in range(num_exec_blocks):
        tx = Transaction(to=Address(0x4000 + i), value=i * 200, gas_limit=21000)
        block = Block(txs=[tx])
        manager.add_block(block)

    # Verify counts
    assert len(manager.setup_transactions) == num_setup_txs
    assert len(manager.setup_blocks) == num_setup_blocks
    assert len(manager.execution_transactions) == num_exec_txs
    assert len(manager.execution_blocks) == num_exec_blocks

    # Verify phase markers
    for tx in manager.setup_transactions:
        assert tx.test_phase == TestPhase.SETUP.value

    for block in manager.setup_blocks:
        for tx in block.txs:
            assert tx.test_phase == TestPhase.SETUP.value

    for tx in manager.execution_transactions:
        assert tx.test_phase == TestPhase.EXECUTION.value

    for block in manager.execution_blocks:
        for tx in block.txs:
            assert tx.test_phase == TestPhase.EXECUTION.value


def test_empty_block_handling():
    """Test handling of empty blocks."""
    manager = TestPhaseManager()
    empty_block = Block(txs=[])

    with manager.setup():
        manager.add_block(empty_block)

    assert len(manager.setup_blocks) == 1
    assert len(manager.setup_blocks[0].txs) == 0


def test_block_with_many_transactions():
    """Test block with many transactions gets all transactions marked."""
    manager = TestPhaseManager()

    # Create block with multiple transactions
    transactions = [
        Transaction(to=Address(0x100 + i), value=i * 10, gas_limit=21000) for i in range(5)
    ]
    block = Block(txs=transactions)

    with manager.setup():
        manager.add_block(block)

    # Verify all transactions in the block have the setup phase
    assert len(manager.setup_blocks) == 1
    setup_block = manager.setup_blocks[0]
    assert len(setup_block.txs) == 5

    for tx in setup_block.txs:
        assert tx.test_phase == TestPhase.SETUP.value


def test_phase_switching_preserves_existing_data():
    """Test that phase switching doesn't affect existing data."""
    manager = TestPhaseManager()

    # Add data in execution phase
    exec_tx1 = Transaction(to=Address(0x100), value=100, gas_limit=21000)
    manager.add_transaction(exec_tx1)

    # Switch to setup and add data
    with manager.setup():
        setup_tx = Transaction(to=Address(0x200), value=50, gas_limit=21000)
        manager.add_transaction(setup_tx)

    # Switch back to execution within setup phase
    with manager.execution():
        exec_tx2 = Transaction(to=Address(0x300), value=200, gas_limit=21000)
        manager.add_transaction(exec_tx2)

    # Add more data in execution phase after phase changes
    exec_tx3 = Transaction(to=Address(0x400), value=300, gas_limit=21000)
    manager.add_transaction(exec_tx3)

    # Verify data integrity
    assert len(manager.setup_transactions) == 1
    assert len(manager.execution_transactions) == 3

    assert manager.setup_transactions[0].value == 50
    exec_values = [tx.value for tx in manager.execution_transactions]
    assert exec_values == [100, 200, 300]


@pytest.mark.parametrize(
    ["manager_instance", "expected_phase"],
    [
        pytest.param(TestPhaseManager(), TestPhase.EXECUTION, id="new_instance"),
    ],
)
def test_manager_properties(manager_instance, expected_phase):
    """Test TestPhaseManager instance properties."""
    assert isinstance(manager_instance, TestPhaseManager)
    assert manager_instance.get_current_phase() == expected_phase
    assert hasattr(manager_instance, "setup_transactions")
    assert hasattr(manager_instance, "setup_blocks")
    assert hasattr(manager_instance, "execution_transactions")
    assert hasattr(manager_instance, "execution_blocks")
