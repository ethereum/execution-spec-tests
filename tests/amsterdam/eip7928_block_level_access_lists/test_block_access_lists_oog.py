"""
Tests for EIP-7928 Block Access Lists with out-of-gas scenarios.

Block access lists (BAL) are generated via a client's state tracing journal. Residual journal
entries may persist when opcodes run out of gas, resulting in a bloated BAL payload.

Issues identified in:
https://github.com/paradigmxyz/reth/issues/17765
https://github.com/bluealloy/revm/pull/2903

These tests ensure out-of-gas operations are not recorded in BAL, preventing consensus issues.
"""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
    TransactionException,
)
from ethereum_test_types.block_access_list import (
    BlockAccessListExpectation,
)

from .spec import ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version


pytestmark = pytest.mark.valid_from("Amsterdam")

@pytest.mark.exception_test
def test_bal_oog_sstore(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL handles OOG before SSTORE execution correctly."""
    from ethereum_test_tools import Bytecode, Opcodes as Op

    alice = pre.fund_eoa(amount=1_000_000)

    # Create contract that attempts SSTORE to cold storage slot 0x01
    storage_contract_code = Bytecode(
        Op.PUSH1(0x42) +  # Value to store
        Op.PUSH1(0x01) +  # Storage slot (cold)
        Op.SSTORE +       # Store value in slot - this will OOG
        Op.STOP
    )

    storage_contract = pre.deploy_contract(code=storage_contract_code)

    # Calculate intrinsic gas cost for the transaction
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    # Set gas limit to allow intrinsic cost but insufficient for cold SSTORE
    # Cold SSTORE costs 22,100 gas (20,000 + 2,100 for cold access)
    insufficient_gas = intrinsic_gas_cost + 21_000  # Not enough for cold SSTORE

    tx = Transaction(
        sender=alice,
        to=storage_contract,
        gas_limit=insufficient_gas,
        error=TransactionException.GASLIMIT_OVERFLOW,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                storage_contract: None            }
        ),
        exception=TransactionException.GASLIMIT_OVERFLOW,
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            # Alice's nonce should increment (transaction processed but failed)
            alice: Account(nonce=1),
            # Storage contract should remain unchanged (no storage writes)
            storage_contract: Account(storage={}),
        },
    )


@pytest.mark.exception_test
def test_bal_oog_sload(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL handles OOG before SLOAD execution correctly."""
    from ethereum_test_tools import Bytecode, Opcodes as Op
    
    alice = pre.fund_eoa(amount=1_000_000)
    
    # Create contract that attempts SLOAD from cold storage slot 0x01
    storage_contract_code = Bytecode(
        Op.PUSH1(0x01) +  # Storage slot (cold)
        Op.SLOAD +        # Load value from slot - this will OOG
        Op.STOP
    )
    
    storage_contract = pre.deploy_contract(code=storage_contract_code)

    # Calculate intrinsic gas cost for the transaction
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    # Set gas limit to allow intrinsic cost but insufficient for cold SLOAD
    # Cold SLOAD costs 2,100 gas
    insufficient_gas = intrinsic_gas_cost + 2_000  # Not enough for cold SLOAD

    tx = Transaction(
        sender=alice,
        to=storage_contract,
        gas_limit=insufficient_gas,
        error=TransactionException.GASLIMIT_OVERFLOW,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                storage_contract: None  # MUST NOT contain slot 0x01 in storage_reads
            }
        ),
        exception=TransactionException.GASLIMIT_OVERFLOW,
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            storage_contract: Account(storage={}),
        },
    )


@pytest.mark.exception_test
def test_bal_oog_balance(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL handles OOG before BALANCE execution correctly."""
    from ethereum_test_tools import Bytecode, Opcodes as Op
    
    alice = pre.fund_eoa(amount=1_000_000)
    bob = pre.fund_eoa(amount=1_000)
    
    # Create contract that attempts to check Bob's balance
    balance_checker_code = Bytecode(
        Op.PUSH20(bob) +  # Bob's address
        Op.BALANCE +      # Check balance - this will OOG
        Op.STOP
    )
    
    balance_checker = pre.deploy_contract(code=balance_checker_code)

    # Calculate intrinsic gas cost
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    # Set gas limit insufficient for cold BALANCE (2,600 gas)
    insufficient_gas = intrinsic_gas_cost + 2_500

    tx = Transaction(
        sender=alice,
        to=balance_checker,
        gas_limit=insufficient_gas,
        error=TransactionException.GASLIMIT_OVERFLOW,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                balance_checker: None,  # Caller included
                bob: None,  # Target MUST NOT be included
            }
        ),
        exception=TransactionException.GASLIMIT_OVERFLOW,
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            bob: Account(balance=1_000),
            balance_checker: Account(),
        },
    )


@pytest.mark.exception_test
def test_bal_oog_extcodesize(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL handles OOG before EXTCODESIZE execution correctly."""
    from ethereum_test_tools import Bytecode, Opcodes as Op
    
    alice = pre.fund_eoa(amount=1_000_000)
    
    # Create target contract with some code
    target_contract = pre.deploy_contract(code=Bytecode(Op.STOP))
    
    # Create contract that attempts to check target's code size
    codesize_checker_code = Bytecode(
        Op.PUSH20(target_contract) +  # Target contract address
        Op.EXTCODESIZE +              # Check code size - this will OOG
        Op.STOP
    )
    
    codesize_checker = pre.deploy_contract(code=codesize_checker_code)

    # Calculate intrinsic gas cost
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    # Set gas limit insufficient for cold EXTCODESIZE (2,600 gas)
    insufficient_gas = intrinsic_gas_cost + 2_500

    tx = Transaction(
        sender=alice,
        to=codesize_checker,
        gas_limit=insufficient_gas,
        error=TransactionException.GASLIMIT_OVERFLOW,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                codesize_checker: None,  # Caller included
                target_contract: None,   # Target MUST NOT be included
            }
        ),
        exception=TransactionException.GASLIMIT_OVERFLOW,
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


@pytest.mark.exception_test
def test_bal_oog_call(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL handles OOG before CALL execution correctly."""
    from ethereum_test_tools import Bytecode, Opcodes as Op
    
    alice = pre.fund_eoa(amount=1_000_000)
    bob = pre.fund_eoa(amount=1_000)
    
    # Create contract that attempts to call Bob
    call_contract_code = Bytecode(
        Op.PUSH1(0) +     # retSize
        Op.PUSH1(0) +     # retOffset  
        Op.PUSH1(0) +     # argsSize
        Op.PUSH1(0) +     # argsOffset
        Op.PUSH1(0) +     # value
        Op.PUSH20(bob) +  # address
        Op.PUSH1(0) +     # gas (will use all available)
        Op.CALL +         # Call - this will OOG
        Op.STOP
    )
    
    call_contract = pre.deploy_contract(code=call_contract_code)

    # Calculate intrinsic gas cost
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    # Set gas limit insufficient for cold CALL (2,600 gas for account access)
    insufficient_gas = intrinsic_gas_cost + 2_500

    tx = Transaction(
        sender=alice,
        to=call_contract,
        gas_limit=insufficient_gas,
        error=TransactionException.GASLIMIT_OVERFLOW,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                call_contract: None,  # Caller included
                bob: None,            # Target MUST NOT be included
            }
        ),
        exception=TransactionException.GASLIMIT_OVERFLOW,
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            alice: Account(nonce=1),
            bob: Account(balance=1_000),
            call_contract: Account(),
        },
    )


@pytest.mark.exception_test
def test_bal_oog_delegatecall(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL handles OOG before DELEGATECALL execution correctly."""
    from ethereum_test_tools import Bytecode, Opcodes as Op
    
    alice = pre.fund_eoa(amount=1_000_000)
    
    # Create target contract
    target_contract = pre.deploy_contract(code=Bytecode(Op.STOP))
    
    # Create contract that attempts delegatecall to target
    delegatecall_contract_code = Bytecode(
        Op.PUSH1(0) +               # retSize
        Op.PUSH1(0) +               # retOffset
        Op.PUSH1(0) +               # argsSize
        Op.PUSH1(0) +               # argsOffset
        Op.PUSH20(target_contract) + # address
        Op.PUSH1(0) +               # gas
        Op.DELEGATECALL +           # Delegatecall - this will OOG
        Op.STOP
    )
    
    delegatecall_contract = pre.deploy_contract(code=delegatecall_contract_code)

    # Calculate intrinsic gas cost
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    # Set gas limit insufficient for cold DELEGATECALL (2,600 gas)
    insufficient_gas = intrinsic_gas_cost + 2_500

    tx = Transaction(
        sender=alice,
        to=delegatecall_contract,
        gas_limit=insufficient_gas,
        error=TransactionException.GASLIMIT_OVERFLOW,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                delegatecall_contract: None,  # Caller included
                target_contract: None,        # Target MUST NOT be included
            }
        ),
        exception=TransactionException.GASLIMIT_OVERFLOW,
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


@pytest.mark.exception_test
def test_bal_oog_extcodecopy(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL handles OOG before EXTCODECOPY execution correctly."""
    from ethereum_test_tools import Bytecode, Opcodes as Op
    
    alice = pre.fund_eoa(amount=1_000_000)
    
    # Create target contract with some code
    target_contract = pre.deploy_contract(code=Bytecode(Op.PUSH1(0x42) + Op.STOP))
    
    # Create contract that attempts to copy code from target
    extcodecopy_contract_code = Bytecode(
        Op.PUSH1(10) +              # size
        Op.PUSH1(0) +               # codeOffset
        Op.PUSH1(0) +               # destOffset
        Op.PUSH20(target_contract) + # address
        Op.EXTCODECOPY +            # Copy code - this will OOG
        Op.STOP
    )
    
    extcodecopy_contract = pre.deploy_contract(code=extcodecopy_contract_code)

    # Calculate intrinsic gas cost
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    # Set gas limit insufficient for cold EXTCODECOPY (2,600 gas + copy costs)
    insufficient_gas = intrinsic_gas_cost + 2_500

    tx = Transaction(
        sender=alice,
        to=extcodecopy_contract,
        gas_limit=insufficient_gas,
        error=TransactionException.GASLIMIT_OVERFLOW,
    )

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                extcodecopy_contract: None,  # Caller included
                target_contract: None,       # Target MUST NOT be included
            }
        ),
        exception=TransactionException.GASLIMIT_OVERFLOW,
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
