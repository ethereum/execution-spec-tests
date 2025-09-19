"""
abstract: BloatNet bench cases extracted from https://hackmd.io/9icZeLN7R0Sk5mIjKlZAHQ.

   The idea of all these tests is to stress client implementations to find out where the limits of
   processing are focusing specifically on state-related operations.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
    While,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "DUMMY/bloatnet.md"
REFERENCE_SPEC_VERSION = "1.0"


# Configuration for CREATE2 factory - UPDATE THESE after running deploy script
# These values come from deploy_create2_factory_refactored.py output
FACTORY_ADDRESS = Address("0x847a04f0a1FfC4E68CC80e7D870Eb4eC51235CE8")  # UPDATE THIS
INIT_CODE_HASH = bytes.fromhex(
    "9e1a230bdc29e66a6027083ec52c6724e7e6cac4a8e59c1c9a852c0a1e954b45"
)  # UPDATE THIS
NUM_DEPLOYED_CONTRACTS = 370  # UPDATE THIS - number of contracts deployed via factory


@pytest.mark.valid_from("Prague")
def test_bloatnet_balance_extcodesize(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
):
    """
    BloatNet test using BALANCE + EXTCODESIZE with "on-the-fly" CREATE2 address generation.

    This test:
    1. Assumes contracts are already deployed via the factory (salt 0 to N-1)
    2. Generates CREATE2 addresses dynamically during execution
    3. Calls BALANCE (cold) then EXTCODESIZE (warm) on each
    4. Maximizes cache eviction by accessing many contracts
    """
    gas_costs = fork.gas_costs()

    # Calculate gas costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Cost per contract access with CREATE2 address generation
    cost_per_contract = (
        gas_costs.G_KECCAK_256  # SHA3 static cost for address generation
        + gas_costs.G_KECCAK_256_WORD * 3  # SHA3 dynamic cost (85 bytes)
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold BALANCE (2600)
        + gas_costs.G_BASE  # POP balance
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm EXTCODESIZE (100)
        + gas_costs.G_BASE  # POP code size
        + 20  # Overhead for memory operations and loop control
    )

    # Calculate how many contracts to access
    available_gas = gas_benchmark_value - intrinsic_gas - 1000  # Reserve for cleanup
    contracts_needed = int(available_gas // cost_per_contract)

    # Limit to actually deployed contracts
    num_contracts = min(contracts_needed, NUM_DEPLOYED_CONTRACTS)

    if contracts_needed > NUM_DEPLOYED_CONTRACTS:
        import warnings

        warnings.warn(
            f"Test needs {contracts_needed} contracts for "
            f"{gas_benchmark_value / 1_000_000:.1f}M gas, "
            f"but only {NUM_DEPLOYED_CONTRACTS} are deployed. "
            f"Deploy {contracts_needed} contracts for full test coverage.",
            stacklevel=2,
        )

    # Generate attack contract with on-the-fly CREATE2 address calculation
    attack_code = (
        # Setup memory for CREATE2 address generation
        # Memory layout: 0xFF + factory_address(20) + salt(32) + init_code_hash(32)
        Op.MSTORE(0, FACTORY_ADDRESS)
        + Op.MSTORE8(32 - 20 - 1, 0xFF)  # Prefix for CREATE2
        + Op.MSTORE(32, 0)  # Initial salt (start from 0)
        + Op.MSTORE(64, INIT_CODE_HASH)  # Init code hash
        # Limit counter for number of contracts to access
        + Op.PUSH2(num_contracts)
        # Main attack loop
        + While(
            body=(
                # Generate CREATE2 address: keccak256(0xFF + factory + salt + init_code_hash)
                Op.SHA3(32 - 20 - 1, 85)  # Hash 85 bytes starting from 0xFF
                # The address is now on the stack
                + Op.DUP1  # Duplicate for EXTCODESIZE
                + Op.BALANCE  # Cold access
                + Op.POP
                + Op.EXTCODESIZE  # Warm access
                + Op.POP
                # Increment salt for next iteration
                + Op.MSTORE(32, Op.ADD(Op.MLOAD(32), 1))
            ),
            # Continue while we haven't reached the limit
            condition=Op.DUP1 + Op.PUSH1(1) + Op.SWAP1 + Op.SUB + Op.DUP1 + Op.ISZERO + Op.ISZERO,
        )
        + Op.POP  # Clean up counter
    )

    # Deploy attack contract
    attack_address = pre.deploy_contract(code=attack_code)

    # Run the attack
    attack_tx = Transaction(
        to=attack_address,
        gas_limit=gas_benchmark_value,
        sender=pre.fund_eoa(),
    )

    # Post-state: just verify attack contract exists
    post = {
        attack_address: Account(storage={}),
    }

    blockchain_test(
        pre=pre,
        blocks=[Block(txs=[attack_tx])],
        post=post,
    )


@pytest.mark.valid_from("Prague")
def test_bloatnet_balance_extcodecopy(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
):
    """
    BloatNet test using BALANCE + EXTCODECOPY with on-the-fly CREATE2 address generation.

    This test forces actual bytecode reads from disk by:
    1. Assumes contracts are already deployed via the factory
    2. Generating CREATE2 addresses dynamically during execution
    3. Using BALANCE (cold) to warm the account
    4. Using EXTCODECOPY (warm) to read 1 byte from the END of the bytecode
    """
    gas_costs = fork.gas_costs()
    max_contract_size = fork.max_code_size()

    # Calculate costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Cost per contract with EXTCODECOPY and CREATE2 address generation
    cost_per_contract = (
        gas_costs.G_KECCAK_256  # SHA3 static cost for address generation
        + gas_costs.G_KECCAK_256_WORD * 3  # SHA3 dynamic cost (85 bytes)
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold BALANCE (2600)
        + gas_costs.G_BASE  # POP balance
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm EXTCODECOPY base (100)
        + gas_costs.G_COPY * 1  # Copy cost for 1 byte (3)
        + gas_costs.G_BASE * 4  # PUSH operations and POP
        + 20  # Overhead
    )

    # Calculate how many contracts to access
    available_gas = gas_benchmark_value - intrinsic_gas - 1000
    contracts_needed = int(available_gas // cost_per_contract)

    # Limit to actually deployed contracts
    num_contracts = min(contracts_needed, NUM_DEPLOYED_CONTRACTS)

    if contracts_needed > NUM_DEPLOYED_CONTRACTS:
        import warnings

        warnings.warn(
            f"Test needs {contracts_needed} contracts for "
            f"{gas_benchmark_value / 1_000_000:.1f}M gas, "
            f"but only {NUM_DEPLOYED_CONTRACTS} are deployed. "
            f"Deploy {contracts_needed} contracts for full test coverage.",
            stacklevel=2,
        )

    # Generate attack contract with on-the-fly CREATE2 address calculation
    attack_code = (
        # Setup memory for CREATE2 address generation
        Op.MSTORE(0, FACTORY_ADDRESS)
        + Op.MSTORE8(32 - 20 - 1, 0xFF)
        + Op.MSTORE(32, 0)  # Initial salt (start from 0)
        + Op.MSTORE(64, INIT_CODE_HASH)
        # Counter for number of contracts
        + Op.PUSH2(num_contracts)
        # Main attack loop
        + While(
            body=(
                # Generate CREATE2 address
                Op.SHA3(32 - 20 - 1, 85)
                # The address is now on the stack
                + Op.DUP1  # Duplicate for later operations
                + Op.BALANCE  # Cold access
                + Op.POP
                # EXTCODECOPY(addr, mem_offset, last_byte_offset, 1)
                # Read the LAST byte to force full contract load
                + Op.PUSH1(1)  # size (1 byte)
                + Op.PUSH2(max_contract_size - 1)  # code offset (last byte)
                # Use salt as memory offset to avoid overlap
                + Op.MLOAD(32)  # Get current salt
                + Op.PUSH2(96)  # Base memory offset
                + Op.ADD  # Unique memory position
                + Op.DUP4  # address (duplicated earlier)
                + Op.EXTCODECOPY
                + Op.POP  # Clean up address
                # Increment salt
                + Op.MSTORE(32, Op.ADD(Op.MLOAD(32), 1))
            ),
            # Continue while counter > 0
            condition=Op.DUP1 + Op.PUSH1(1) + Op.SWAP1 + Op.SUB + Op.DUP1 + Op.ISZERO + Op.ISZERO,
        )
        + Op.POP  # Clean up counter
    )

    # Deploy attack contract
    attack_address = pre.deploy_contract(code=attack_code)

    # Run the attack
    attack_tx = Transaction(
        to=attack_address,
        gas_limit=gas_benchmark_value,
        sender=pre.fund_eoa(),
    )

    # Post-state
    post = {
        attack_address: Account(storage={}),
    }

    blockchain_test(
        pre=pre,
        blocks=[Block(txs=[attack_tx])],
        post=post,
    )
