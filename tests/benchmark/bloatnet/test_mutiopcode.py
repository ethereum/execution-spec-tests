"""
abstract: BloatNet bench cases extracted from https://hackmd.io/9icZeLN7R0Sk5mIjKlZAHQ.

   The idea of all these tests is to stress client implementations to find out where the limits of
   processing are focusing specifically on state-related operations.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
    While,
)
from ethereum_test_vm import Bytecode, Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "DUMMY/bloatnet.md"
REFERENCE_SPEC_VERSION = "1.0"


# CREATE2 FACTORY:
#   - Pre-deployed contract that creates 24KB contracts via CREATE2
#   - Uses counter (slot 0) as salt for deterministic addresses
#   - Stores init code hash (slot 1) for CREATE2 address calculation
#   - Each call to factory deploys one contract and increments counter
#   - Address calculation: keccak256(0xFF + factory_addr + salt + init_code_hash)[12:]
#   - Storage layout:
#     - Slot 0: Number of deployed contracts (counter)
#     - Slot 1: Init code hash (32 bytes) - hash of the initcode used for CREATE2
#     - The factory MUST store the correct init code hash that was used to deploy contracts\


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

    # Calculate how many contracts to access based on available gas
    available_gas = gas_benchmark_value - intrinsic_gas - 1000  # Reserve for cleanup
    contracts_needed = int(available_gas // cost_per_contract)

    # Deploy factory using stub contract - NO HARDCODED VALUES
    # The stub "bloatnet_factory" must be provided via --address-stubs flag
    # The factory at that address MUST have:
    # - Slot 0: Number of deployed contracts
    # - Slot 1: Init code hash for CREATE2 address calculation
    factory_address = pre.deploy_contract(
        code=Bytecode(),  # Required parameter, but will be ignored for stubs
        stub="bloatnet_factory",
    )

    # Log test requirements - actual deployed count will be read from factory storage
    print(
        f"Test needs {contracts_needed} contracts for "
        f"{gas_benchmark_value / 1_000_000:.1f}M gas. "
        f"Factory storage will be checked during execution."
    )

    # Build attack contract that reads config from factory and performs attack
    attack_code = (
        # Read number of deployed contracts from factory storage slot 0
        Op.PUSH1(0)  # Storage slot 0
        + Op.PUSH20(factory_address)  # Factory address
        + Op.SLOAD  # Load num_deployed_contracts
        + Op.DUP1  # Keep a copy for later use

        # Read init code hash from factory storage slot 1
        + Op.PUSH1(1)  # Storage slot 1
        + Op.PUSH20(factory_address)  # Factory address
        + Op.SLOAD  # Load init_code_hash

        # Setup memory for CREATE2 address generation
        # Memory layout: 0xFF + factory_address(20) + salt(32) + init_code_hash(32)
        + Op.PUSH20(factory_address)
        + Op.PUSH1(0)
        + Op.MSTORE  # Store factory address at memory position 0
        + Op.PUSH1(0xFF)
        + Op.PUSH1(11)  # Position for 0xFF prefix (32 - 20 - 1)
        + Op.MSTORE8  # Store 0xFF prefix

        + Op.PUSH1(0)  # Initial salt value
        + Op.PUSH1(32)
        + Op.MSTORE  # Store salt at position 32

        # Stack now has: [num_contracts, init_code_hash]
        + Op.PUSH1(64)
        + Op.MSTORE  # Store init_code_hash at position 64

        # Stack now has: [num_contracts]
        # Calculate how many contracts we can actually access with available gas
        + Op.GAS  # Get current gas
        + Op.PUSH2(cost_per_contract)  # Gas per contract access
        + Op.DIV  # Calculate max possible contracts
        + Op.DUP2  # Get num_deployed_contracts
        + Op.GT  # Check if we can access all deployed contracts
        + Op.PUSH1(0)  # Jump destination for no limit
        + Op.JUMPI
        + Op.POP  # Remove num_deployed_contracts
        + Op.GAS
        + Op.PUSH2(cost_per_contract)
        + Op.DIV  # Use gas-limited count
        + Op.JUMPDEST
        # Main attack loop - stack has [num_contracts_to_access]
        + While(
            body=(
                # Generate CREATE2 address: keccak256(0xFF + factory + salt + init_code_hash)
                Op.PUSH1(85)  # Size to hash (1 + 20 + 32 + 32)
                + Op.PUSH1(11)  # Start position (0xFF prefix)
                + Op.SHA3  # Generate CREATE2 address
                # The address is now on the stack
                + Op.DUP1  # Duplicate for EXTCODESIZE
                + Op.BALANCE  # Cold access
                + Op.POP
                + Op.EXTCODESIZE  # Warm access
                + Op.POP
                # Increment salt for next iteration
                + Op.PUSH1(32)  # Salt position
                + Op.MLOAD  # Load current salt
                + Op.PUSH1(1)
                + Op.ADD  # Increment
                + Op.PUSH1(32)
                + Op.MSTORE  # Store back
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
        skip_gas_used_validation=True,
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

    # Deploy factory using stub contract - NO HARDCODED VALUES
    # The stub "bloatnet_factory" must be provided via --address-stubs flag
    # The factory at that address MUST have:
    # - Slot 0: Number of deployed contracts
    # - Slot 1: Init code hash for CREATE2 address calculation
    factory_address = pre.deploy_contract(
        code=Bytecode(),  # Required parameter, but will be ignored for stubs
        stub="bloatnet_factory",
    )

    # Log test requirements - actual deployed count will be read from factory storage
    print(
        f"Test needs {contracts_needed} contracts for "
        f"{gas_benchmark_value / 1_000_000:.1f}M gas. "
        f"Factory storage will be checked during execution."
    )

    # Build attack contract that reads config from factory and performs attack
    attack_code = (
        # Read number of deployed contracts from factory storage slot 0
        Op.PUSH1(0)  # Storage slot 0
        + Op.PUSH20(factory_address)  # Factory address
        + Op.SLOAD  # Load num_deployed_contracts
        + Op.DUP1  # Keep a copy for later use

        # Read init code hash from factory storage slot 1
        + Op.PUSH1(1)  # Storage slot 1
        + Op.PUSH20(factory_address)  # Factory address
        + Op.SLOAD  # Load init_code_hash

        # Setup memory for CREATE2 address generation
        # Memory layout: 0xFF + factory_address(20) + salt(32) + init_code_hash(32)
        + Op.PUSH20(factory_address)
        + Op.PUSH1(0)
        + Op.MSTORE  # Store factory address at memory position 0
        + Op.PUSH1(0xFF)
        + Op.PUSH1(11)  # Position for 0xFF prefix (32 - 20 - 1)
        + Op.MSTORE8  # Store 0xFF prefix

        + Op.PUSH1(0)  # Initial salt value
        + Op.PUSH1(32)
        + Op.MSTORE  # Store salt at position 32

        # Stack now has: [num_contracts, init_code_hash]
        + Op.PUSH1(64)
        + Op.MSTORE  # Store init_code_hash at position 64

        # Stack now has: [num_contracts]
        # Calculate how many contracts we can actually access with available gas
        + Op.GAS  # Get current gas
        + Op.PUSH2(cost_per_contract)  # Gas per contract access with EXTCODECOPY
        + Op.DIV  # Calculate max possible contracts
        + Op.DUP2  # Get num_deployed_contracts
        + Op.GT  # Check if we can access all deployed contracts
        + Op.PUSH1(0)  # Jump destination for no limit
        + Op.JUMPI
        + Op.POP  # Remove num_deployed_contracts
        + Op.GAS
        + Op.PUSH2(cost_per_contract)
        + Op.DIV  # Use gas-limited count
        + Op.JUMPDEST
        # Main attack loop - stack has [num_contracts_to_access]
        + While(
            body=(
                # Generate CREATE2 address
                Op.PUSH1(85)  # Size to hash (1 + 20 + 32 + 32)
                + Op.PUSH1(11)  # Start position (0xFF prefix)
                + Op.SHA3  # Generate CREATE2 address
                # The address is now on the stack
                + Op.DUP1  # Duplicate for later operations
                + Op.BALANCE  # Cold access
                + Op.POP
                # EXTCODECOPY(addr, mem_offset, last_byte_offset, 1)
                # Read the LAST byte to force full contract load
                + Op.PUSH1(1)  # size (1 byte)
                + Op.PUSH2(max_contract_size - 1)  # code offset (last byte)
                # Use salt as memory offset to avoid overlap
                + Op.PUSH1(32)  # Salt position
                + Op.MLOAD  # Get current salt
                + Op.PUSH2(96)  # Base memory offset
                + Op.ADD  # Unique memory position
                + Op.DUP4  # address (duplicated earlier)
                + Op.EXTCODECOPY
                + Op.POP  # Clean up address
                # Increment salt for next iteration
                + Op.PUSH1(32)  # Salt position
                + Op.MLOAD  # Load current salt
                + Op.PUSH1(1)
                + Op.ADD  # Increment
                + Op.PUSH1(32)
                + Op.MSTORE  # Store back
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
        skip_gas_used_validation=True,
    )
