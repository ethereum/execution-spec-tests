"""
Tests for EIP-7928 Block Access Lists with single-opcode success and OOG
scenarios.

Block access lists (BAL) are generated via a client's state tracing journal.
Residual journal entries may persist when opcodes run out of gas, resulting
in a bloated BAL payload.

Issues identified in:
https://github.com/paradigmxyz/reth/issues/17765
https://github.com/bluealloy/revm/pull/2903

These tests ensure out-of-gas operations are not recorded in BAL,
preventing consensus issues.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
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
    BalStorageChange,
    BalStorageSlot,
    BlockAccessListExpectation,
)
from ethereum_test_vm import Bytecode

from .spec import ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version


pytestmark = pytest.mark.valid_from("Amsterdam")


@pytest.mark.parametrize(
    "fails_at_sstore", [True, False], ids=["oog_at_sstore", "successful_sstore"]
)
def test_bal_sstore_and_oog(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    fails_at_sstore: bool,
):
    """
    Ensure BAL handles SSTORE and OOG during SSTORE appropriately.
    """
    alice = pre.fund_eoa()
    gas_costs = fork.gas_costs()

    # Create contract that attempts SSTORE to cold storage slot 0x01
    storage_contract_code = Bytecode(
        Op.PUSH1(0x42)  # Value to store
        + Op.PUSH1(0x01)  # Storage slot (cold)
        + Op.SSTORE  # Store value in slot - this will OOG
        + Op.STOP
    )

    storage_contract = pre.deploy_contract(code=storage_contract_code)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator()

    # Costs:
    # - PUSH1 (value and slot) = G_VERY_LOW * 2
    # - SSTORE cold (to zero slot) = G_STORAGE_SET + G_COLD_SLOAD
    sstore_cold_cost = gas_costs.G_STORAGE_SET + gas_costs.G_COLD_SLOAD
    push_cost = gas_costs.G_VERY_LOW * 2
    tx_gas_limit = intrinsic_gas_cost + push_cost + sstore_cold_cost

    if fails_at_sstore:
        # subtract 1 gas to ensure OOG at SSTORE
        tx_gas_limit -= 1

    tx = Transaction(
        sender=alice,
        to=storage_contract,
        gas_limit=tx_gas_limit,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                storage_contract: BalAccountExpectation(
                    storage_changes=[]
                    if fails_at_sstore
                    else [
                        BalStorageSlot(
                            slot=0x01,
                            slot_changes=[BalStorageChange(tx_index=1, post_value=0x42)],
                        ),
                    ]
                )
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            storage_contract: Account(storage={} if fails_at_sstore else {0x01: 0x42}),
        },
    )


@pytest.mark.parametrize(
    "fails_at_sload",
    [True, False],
    ids=["oog_at_sload", "successful_sload"],
)
def test_bal_sload_and_oog(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    fails_at_sload: bool,
):
    """
    Ensure BAL handles SLOAD and OOG during SLOAD appropriately.
    """
    alice = pre.fund_eoa()
    gas_costs = fork.gas_costs()

    # Create contract that attempts SLOAD from cold storage slot 0x01
    storage_contract_code = Bytecode(
        Op.PUSH1(0x01)  # Storage slot (cold)
        + Op.SLOAD  # Load value from slot - this will OOG
        + Op.STOP
    )

    storage_contract = pre.deploy_contract(code=storage_contract_code)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator()

    # Costs:
    # - PUSH1 (slot) = G_VERY_LOW
    # - SLOAD cold = G_COLD_SLOAD
    push_cost = gas_costs.G_VERY_LOW
    sload_cold_cost = gas_costs.G_COLD_SLOAD
    tx_gas_limit = intrinsic_gas_cost + push_cost + sload_cold_cost

    if fails_at_sload:
        # subtract 1 gas to ensure OOG at SLOAD
        tx_gas_limit -= 1

    tx = Transaction(
        sender=alice,
        to=storage_contract,
        gas_limit=tx_gas_limit,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                storage_contract: BalAccountExpectation(
                    storage_reads=[] if fails_at_sload else [0x01],
                )
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            storage_contract: Account(storage={}),
        },
    )


@pytest.mark.parametrize(
    "fails_at_balance", [True, False], ids=["oog_at_balance", "successful_balance"]
)
def test_bal_balance_and_oog(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    fails_at_balance: bool,
):
    """Ensure BAL handles BALANCE and OOG during BALANCE appropriately."""
    alice = pre.fund_eoa()
    bob = pre.fund_eoa()
    gas_costs = fork.gas_costs()

    # Create contract that attempts to check Bob's balance
    balance_checker_code = Bytecode(
        Op.PUSH20(bob)  # Bob's address
        + Op.BALANCE  # Check balance (cold access)
        + Op.STOP
    )

    balance_checker = pre.deploy_contract(code=balance_checker_code)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator()

    # Costs:
    # - PUSH20 = G_VERY_LOW
    # - BALANCE cold = G_COLD_ACCOUNT_ACCESS
    push_cost = gas_costs.G_VERY_LOW
    balance_cold_cost = gas_costs.G_COLD_ACCOUNT_ACCESS
    tx_gas_limit = intrinsic_gas_cost + push_cost + balance_cold_cost

    if fails_at_balance:
        # subtract 1 gas to ensure OOG at BALANCE
        tx_gas_limit -= 1

    tx = Transaction(
        sender=alice,
        to=balance_checker,
        gas_limit=tx_gas_limit,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                balance_checker: BalAccountExpectation.empty(),
                # Bob should only appear in BAL if BALANCE succeeded
                **({} if fails_at_balance else {bob: BalAccountExpectation.empty()}),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            bob: Account(),
            balance_checker: Account(),
        },
    )


@pytest.mark.parametrize(
    "fails_at_extcodesize", [True, False], ids=["oog_at_extcodesize", "successful_extcodesize"]
)
def test_bal_extcodesize_and_oog(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    fails_at_extcodesize: bool,
):
    """
    Ensure BAL handles EXTCODESIZE and OOG during EXTCODESIZE appropriately.
    """
    alice = pre.fund_eoa()
    gas_costs = fork.gas_costs()

    # Create target contract with some code
    target_contract = pre.deploy_contract(code=Bytecode(Op.STOP))

    # Create contract that checks target's code size
    codesize_checker_code = Bytecode(
        Op.PUSH20(target_contract)  # Target contract address
        + Op.EXTCODESIZE  # Check code size (cold access)
        + Op.STOP
    )

    codesize_checker = pre.deploy_contract(code=codesize_checker_code)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator()

    # Costs:
    # - PUSH20 = G_VERY_LOW
    # - EXTCODESIZE cold = G_COLD_ACCOUNT_ACCESS
    push_cost = gas_costs.G_VERY_LOW
    extcodesize_cold_cost = gas_costs.G_COLD_ACCOUNT_ACCESS
    tx_gas_limit = intrinsic_gas_cost + push_cost + extcodesize_cold_cost

    if fails_at_extcodesize:
        # subtract 1 gas to ensure OOG at EXTCODESIZE
        tx_gas_limit -= 1

    tx = Transaction(
        sender=alice,
        to=codesize_checker,
        gas_limit=tx_gas_limit,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                codesize_checker: BalAccountExpectation.empty(),
                # Target should only appear if EXTCODESIZE succeeded
                **(
                    {}
                    if fails_at_extcodesize
                    else {target_contract: BalAccountExpectation.empty()}
                ),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            codesize_checker: Account(),
            target_contract: Account(),
        },
    )


@pytest.mark.parametrize("fails_at_call", [True, False], ids=["oog_at_call", "successful_call"])
def test_bal_call_and_oog(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    fails_at_call: bool,
):
    """Ensure BAL handles CALL and OOG during CALL appropriately."""
    alice = pre.fund_eoa()
    bob = pre.fund_eoa()
    gas_costs = fork.gas_costs()

    # Create contract that attempts to call Bob
    call_contract_code = Bytecode(
        Op.PUSH1(0)  # retSize
        + Op.PUSH1(0)  # retOffset
        + Op.PUSH1(0)  # argsSize
        + Op.PUSH1(0)  # argsOffset
        + Op.PUSH1(0)  # value
        + Op.PUSH20(bob)  # address
        + Op.PUSH2(0xFFFF)  # gas (provide enough for the call)
        + Op.CALL  # Call (cold account access)
        + Op.STOP
    )

    call_contract = pre.deploy_contract(code=call_contract_code)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator()

    # Costs:
    # - 7 PUSH operations = G_VERY_LOW * 7
    # - CALL cold = G_COLD_ACCOUNT_ACCESS (minimum for account access)
    push_cost = gas_costs.G_VERY_LOW * 7
    call_cold_cost = gas_costs.G_COLD_ACCOUNT_ACCESS
    tx_gas_limit = intrinsic_gas_cost + push_cost + call_cold_cost

    if fails_at_call:
        # subtract 1 gas to ensure OOG at CALL
        tx_gas_limit -= 1

    tx = Transaction(
        sender=alice,
        to=call_contract,
        gas_limit=tx_gas_limit,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                call_contract: BalAccountExpectation.empty(),
                # Bob should only appear if CALL succeeded
                **({} if fails_at_call else {bob: BalAccountExpectation.empty()}),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            call_contract: Account(),
        },
    )


@pytest.mark.parametrize(
    "fails_at_delegatecall", [True, False], ids=["oog_at_delegatecall", "successful_delegatecall"]
)
def test_bal_delegatecall_and_oog(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    fails_at_delegatecall: bool,
):
    """
    Ensure BAL handles DELEGATECALL and OOG during DELEGATECALL
    appropriately.
    """
    alice = pre.fund_eoa()
    gas_costs = fork.gas_costs()

    # Create target contract
    target_contract = pre.deploy_contract(code=Bytecode(Op.STOP))

    # Create contract that attempts delegatecall to target
    delegatecall_contract_code = Bytecode(
        Op.PUSH1(0)  # retSize
        + Op.PUSH1(0)  # retOffset
        + Op.PUSH1(0)  # argsSize
        + Op.PUSH1(0)  # argsOffset
        + Op.PUSH20(target_contract)  # address
        + Op.PUSH2(0xFFFF)  # gas (provide enough for the call)
        + Op.DELEGATECALL  # Delegatecall (cold account access)
        + Op.STOP
    )

    delegatecall_contract = pre.deploy_contract(code=delegatecall_contract_code)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator()

    # Costs:
    # - 6 PUSH operations = G_VERY_LOW * 6
    # - DELEGATECALL cold = G_COLD_ACCOUNT_ACCESS
    push_cost = gas_costs.G_VERY_LOW * 6
    delegatecall_cold_cost = gas_costs.G_COLD_ACCOUNT_ACCESS
    tx_gas_limit = intrinsic_gas_cost + push_cost + delegatecall_cold_cost

    if fails_at_delegatecall:
        # subtract 1 gas to ensure OOG at DELEGATECALL
        tx_gas_limit -= 1

    tx = Transaction(
        sender=alice,
        to=delegatecall_contract,
        gas_limit=tx_gas_limit,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                delegatecall_contract: BalAccountExpectation.empty(),
                # Target should only appear if DELEGATECALL succeeded
                **(
                    {}
                    if fails_at_delegatecall
                    else {target_contract: BalAccountExpectation.empty()}
                ),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            delegatecall_contract: Account(),
            target_contract: Account(),
        },
    )


@pytest.mark.parametrize(
    "fails_at_extcodecopy", [True, False], ids=["oog_at_extcodecopy", "successful_extcodecopy"]
)
def test_bal_extcodecopy_and_oog(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    fails_at_extcodecopy: bool,
):
    """
    Ensure BAL handles EXTCODECOPY and OOG during EXTCODECOPY appropriately.
    """
    alice = pre.fund_eoa()
    gas_costs = fork.gas_costs()

    # Create target contract with some code
    target_contract = pre.deploy_contract(code=Bytecode(Op.PUSH1(0x42) + Op.STOP))

    # Create contract that attempts to copy code from target
    extcodecopy_contract_code = Bytecode(
        Op.PUSH1(0)  # size - copy 0 bytes to minimize memory expansion cost
        + Op.PUSH1(0)  # codeOffset
        + Op.PUSH1(0)  # destOffset
        + Op.PUSH20(target_contract)  # address
        + Op.EXTCODECOPY  # Copy code (cold access + base cost)
        + Op.STOP
    )

    extcodecopy_contract = pre.deploy_contract(code=extcodecopy_contract_code)

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator()

    # Costs:
    # - 4 PUSH operations = G_VERY_LOW * 4
    # - EXTCODECOPY cold = G_COLD_ACCOUNT_ACCESS + G_COPY (base cost)
    push_cost = gas_costs.G_VERY_LOW * 4
    extcodecopy_cold_cost = gas_costs.G_COLD_ACCOUNT_ACCESS + gas_costs.G_COPY
    tx_gas_limit = intrinsic_gas_cost + push_cost + extcodecopy_cold_cost

    if fails_at_extcodecopy:
        # subtract 1 gas to ensure OOG at EXTCODECOPY
        tx_gas_limit -= 1

    tx = Transaction(
        sender=alice,
        to=extcodecopy_contract,
        gas_limit=tx_gas_limit,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                extcodecopy_contract: BalAccountExpectation.empty(),
                # Target should only appear if EXTCODECOPY succeeded
                **(
                    {}
                    if fails_at_extcodecopy
                    else {target_contract: BalAccountExpectation.empty()}
                ),
            }
        ),
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            extcodecopy_contract: Account(),
            target_contract: Account(),
        },
    )
