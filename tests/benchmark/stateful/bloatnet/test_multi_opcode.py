"""
abstract: BloatNet bench cases extracted from https://hackmd.io/9icZeLN7R0Sk5mIjKlZAHQ.

   The idea of all these tests is to stress client implementations to find out
   where the limits of processing are focusing specifically on state-related
   operations.
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
from ethereum_test_vm import Bytecode
from ethereum_test_vm import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "DUMMY/bloatnet.md"
REFERENCE_SPEC_VERSION = "1.0"


# BLOATNET ARCHITECTURE:
#
#   [Initcode Contract]        [Factory Contract]              [24KB Contracts]
#         (9.5KB)                    (116B)                     (N x 24KB each)
#           │                          │                              │
#           │  EXTCODECOPY             │   CREATE2(salt++)            │
#           └──────────────►           ├──────────────────►     Contract_0
#                                      ├──────────────────►     Contract_1
#                                      ├──────────────────►     Contract_2
#                                      └──────────────────►     Contract_N
#
#   [Attack Contract] ──STATICCALL──► [Factory.getConfig()]
#           │                              returns: (N, hash)
#           └─► Loop(i=0 to N):
#                 1. Generate CREATE2 addr: keccak256(0xFF|factory|i|hash)[12:]
#                 2. BALANCE(addr)    → 2600 gas (cold access)
#                 3. EXTCODESIZE(addr) → 100 gas (warm access)
#
# HOW IT WORKS:
#   1. Factory uses EXTCODECOPY to load initcode, avoiding PC-relative jumps
#   2. Each CREATE2 deployment produces unique 24KB bytecode (via ADDRESS)
#   3. All contracts share same initcode hash for deterministic addresses
#   4. Attack rapidly accesses all contracts, stressing client's state handling


@pytest.mark.parametrize(
    "balance_first",
    [True, False],
    ids=["balance_extcodesize", "extcodesize_balance"],
)
@pytest.mark.valid_from("Prague")
def test_bloatnet_balance_extcodesize(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
    balance_first: bool,
):
    """
    BloatNet test using BALANCE + EXTCODESIZE with "on-the-fly" CREATE2
    address generation.

    This test:
    1. Assumes contracts are already deployed via the factory (salt 0 to N-1)
    2. Generates CREATE2 addresses dynamically during execution
    3. Calls BALANCE and EXTCODESIZE (order controlled by balance_first param)
    4. Maximizes cache eviction by accessing many contracts
    """
    gas_costs = fork.gas_costs()

    # Calculate gas costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Cost per contract access with CREATE2 address generation
    cost_per_contract = (
        gas_costs.G_KECCAK_256  # SHA3 static cost for address generation (30)
        + gas_costs.G_KECCAK_256_WORD * 3  # SHA3 dynamic cost (85 bytes = 3 words * 6)
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold access (2600)
        + gas_costs.G_BASE  # POP first result (2)
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm access (100)
        + gas_costs.G_BASE  # POP second result (2)
        + gas_costs.G_BASE  # DUP1 before first op (3)
        + gas_costs.G_VERY_LOW * 4  # PUSH1 operations (4 * 3)
        + gas_costs.G_LOW  # MLOAD for salt (3)
        + gas_costs.G_VERY_LOW  # ADD for increment (3)
        + gas_costs.G_LOW  # MSTORE salt back (3)
        + 10  # While loop overhead
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

    # Log test requirements - deployed count read from factory storage
    print(
        f"Test needs {contracts_needed} contracts for "
        f"{gas_benchmark_value / 1_000_000:.1f}M gas. "
        f"Factory storage will be checked during execution."
    )

    # Define operations that differ based on parameter
    balance_op = Op.POP(Op.BALANCE)
    extcodesize_op = Op.POP(Op.EXTCODESIZE)
    benchmark_ops = (
        (balance_op + extcodesize_op) if balance_first else (extcodesize_op + balance_op)
    )

    # Build attack contract that reads config from factory and performs attack
    attack_code = (
        # Call getConfig() on factory to get num_deployed and init_code_hash
        Op.STATICCALL(
            gas=Op.GAS,
            address=factory_address,
            args_offset=0,
            args_size=0,
            ret_offset=96,
            ret_size=64,
        )
        # Check if call succeeded
        + Op.ISZERO
        + Op.PUSH2(0x1000)  # Jump to error handler if failed (far jump)
        + Op.JUMPI
        # Load results from memory
        # Memory[96:128] = num_deployed_contracts
        # Memory[128:160] = init_code_hash
        + Op.MLOAD(96)  # Load num_deployed_contracts
        + Op.MLOAD(128)  # Load init_code_hash
        # Setup memory for CREATE2 address generation
        # Memory layout at 0: 0xFF + factory_addr(20) + salt(32) + hash(32)
        + Op.MSTORE(0, factory_address)  # Store factory address at memory position 0
        + Op.MSTORE8(11, 0xFF)  # Store 0xFF prefix at position (32 - 20 - 1)
        + Op.MSTORE(32, 0)  # Store salt at position 32
        # Stack now has: [num_contracts, init_code_hash]
        + Op.PUSH1(64)  # Push memory position
        + Op.MSTORE  # Store init_code_hash at memory[64]
        # Stack now has: [num_contracts]
        # Main attack loop - iterate through all deployed contracts
        + While(
            body=(
                # Generate CREATE2 addr: keccak256(0xFF+factory+salt+hash)
                Op.SHA3(11, 85)  # Generate CREATE2 address from memory[11:96]
                # The address is now on the stack
                + Op.DUP1  # Duplicate for second operation
                + benchmark_ops  # Execute operations in specified order
                # Increment salt for next iteration
                + Op.MSTORE(32, Op.ADD(Op.MLOAD(32), 1))  # Increment and store salt
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


@pytest.mark.parametrize(
    "balance_first",
    [True, False],
    ids=["balance_extcodecopy", "extcodecopy_balance"],
)
@pytest.mark.valid_from("Prague")
def test_bloatnet_balance_extcodecopy(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
    balance_first: bool,
):
    """
    BloatNet test using BALANCE + EXTCODECOPY with on-the-fly CREATE2
    address generation.

    This test forces actual bytecode reads from disk by:
    1. Assumes contracts are already deployed via the factory
    2. Generating CREATE2 addresses dynamically during execution
    3. Using BALANCE and EXTCODECOPY (order controlled by balance_first param)
    4. Reading 1 byte from the END of the bytecode to force full contract load
    """
    gas_costs = fork.gas_costs()
    max_contract_size = fork.max_code_size()

    # Calculate costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Cost per contract with EXTCODECOPY and CREATE2 address generation
    cost_per_contract = (
        gas_costs.G_KECCAK_256  # SHA3 static cost for address generation (30)
        + gas_costs.G_KECCAK_256_WORD * 3  # SHA3 dynamic cost (85 bytes = 3 words * 6)
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold access (2600)
        + gas_costs.G_BASE  # POP first result (2)
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm access base (100)
        + gas_costs.G_COPY * 1  # Copy cost for 1 byte (3)
        + gas_costs.G_BASE * 2  # DUP1 before first op, DUP4 for address (6)
        + gas_costs.G_VERY_LOW * 8  # PUSH operations (8 * 3 = 24)
        + gas_costs.G_LOW * 2  # MLOAD for salt twice (6)
        + gas_costs.G_VERY_LOW * 2  # ADD operations (6)
        + gas_costs.G_LOW  # MSTORE salt back (3)
        + gas_costs.G_BASE  # POP after second op (2)
        + 10  # While loop overhead
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

    # Log test requirements - deployed count read from factory storage
    print(
        f"Test needs {contracts_needed} contracts for "
        f"{gas_benchmark_value / 1_000_000:.1f}M gas. "
        f"Factory storage will be checked during execution."
    )

    # Define operations that differ based on parameter
    balance_op = Op.POP(Op.BALANCE)
    extcodecopy_op = (
        Op.PUSH1(1)  # size (1 byte)
        + Op.PUSH2(max_contract_size - 1)  # code offset (last byte)
        + Op.ADD(Op.MLOAD(32), 96)  # unique memory offset
        + Op.DUP4  # address (duplicated earlier)
        + Op.EXTCODECOPY
        + Op.POP  # clean up address
    )
    benchmark_ops = (
        (balance_op + extcodecopy_op) if balance_first else (extcodecopy_op + balance_op)
    )

    # Build attack contract that reads config from factory and performs attack
    attack_code = (
        # Call getConfig() on factory to get num_deployed and init_code_hash
        Op.STATICCALL(
            gas=Op.GAS,
            address=factory_address,
            args_offset=0,
            args_size=0,
            ret_offset=96,
            ret_size=64,
        )
        # Check if call succeeded
        + Op.ISZERO
        + Op.PUSH2(0x1000)  # Jump to error handler if failed (far jump)
        + Op.JUMPI
        # Load results from memory
        # Memory[96:128] = num_deployed_contracts
        # Memory[128:160] = init_code_hash
        + Op.MLOAD(96)  # Load num_deployed_contracts
        + Op.MLOAD(128)  # Load init_code_hash
        # Setup memory for CREATE2 address generation
        # Memory layout at 0: 0xFF + factory_addr(20) + salt(32) + hash(32)
        + Op.MSTORE(0, factory_address)  # Store factory address at memory position 0
        + Op.MSTORE8(11, 0xFF)  # Store 0xFF prefix at position (32 - 20 - 1)
        + Op.MSTORE(32, 0)  # Store salt at position 32
        # Stack now has: [num_contracts, init_code_hash]
        + Op.PUSH1(64)  # Push memory position
        + Op.MSTORE  # Store init_code_hash at memory[64]
        # Stack now has: [num_contracts]
        # Main attack loop - iterate through all deployed contracts
        + While(
            body=(
                # Generate CREATE2 address
                Op.SHA3(11, 85)  # Generate CREATE2 address from memory[11:96]
                # The address is now on the stack
                + Op.DUP1  # Duplicate for later operations
                + benchmark_ops  # Execute operations in specified order
                # Increment salt for next iteration
                + Op.MSTORE(32, Op.ADD(Op.MLOAD(32), 1))  # Increment and store salt
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


@pytest.mark.parametrize(
    "balance_first",
    [True, False],
    ids=["balance_extcodehash", "extcodehash_balance"],
)
@pytest.mark.valid_from("Prague")
def test_bloatnet_balance_extcodehash(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
    balance_first: bool,
):
    """
    BloatNet test using BALANCE + EXTCODEHASH with on-the-fly CREATE2
    address generation.

    This test:
    1. Assumes contracts are already deployed via the factory
    2. Generates CREATE2 addresses dynamically during execution
    3. Calls BALANCE and EXTCODEHASH (order controlled by balance_first param)
    4. Forces client to compute code hash for 24KB bytecode
    """
    gas_costs = fork.gas_costs()

    # Calculate gas costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Cost per contract access with CREATE2 address generation
    cost_per_contract = (
        gas_costs.G_KECCAK_256  # SHA3 static cost for address generation (30)
        + gas_costs.G_KECCAK_256_WORD * 3  # SHA3 dynamic cost (85 bytes = 3 words * 6)
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold access (2600)
        + gas_costs.G_BASE  # POP first result (2)
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm access (100)
        + gas_costs.G_BASE  # POP second result (2)
        + gas_costs.G_BASE  # DUP1 before first op (3)
        + gas_costs.G_VERY_LOW * 4  # PUSH1 operations (4 * 3)
        + gas_costs.G_LOW  # MLOAD for salt (3)
        + gas_costs.G_VERY_LOW  # ADD for increment (3)
        + gas_costs.G_LOW  # MSTORE salt back (3)
        + 10  # While loop overhead
    )

    # Calculate how many contracts to access based on available gas
    available_gas = gas_benchmark_value - intrinsic_gas - 1000  # Reserve for cleanup
    contracts_needed = int(available_gas // cost_per_contract)

    # Deploy factory using stub contract
    factory_address = pre.deploy_contract(
        code=Bytecode(),
        stub="bloatnet_factory",
    )

    # Log test requirements
    print(
        f"Test needs {contracts_needed} contracts for "
        f"{gas_benchmark_value / 1_000_000:.1f}M gas. "
        f"Factory storage will be checked during execution."
    )

    # Define operations that differ based on parameter
    balance_op = Op.POP(Op.BALANCE)
    extcodehash_op = Op.POP(Op.EXTCODEHASH)
    benchmark_ops = (
        (balance_op + extcodehash_op) if balance_first else (extcodehash_op + balance_op)
    )

    # Build attack contract that reads config from factory and performs attack
    attack_code = (
        # Call getConfig() on factory to get num_deployed and init_code_hash
        Op.STATICCALL(
            gas=Op.GAS,
            address=factory_address,
            args_offset=0,
            args_size=0,
            ret_offset=96,
            ret_size=64,
        )
        # Check if call succeeded
        + Op.ISZERO
        + Op.PUSH2(0x1000)  # Jump to error handler if failed
        + Op.JUMPI
        # Load results from memory
        + Op.MLOAD(96)  # Load num_deployed_contracts
        + Op.MLOAD(128)  # Load init_code_hash
        # Setup memory for CREATE2 address generation
        + Op.MSTORE(0, factory_address)
        + Op.MSTORE8(11, 0xFF)
        + Op.MSTORE(32, 0)  # Initial salt
        + Op.PUSH1(64)
        + Op.MSTORE  # Store init_code_hash
        # Main attack loop
        + While(
            body=(
                # Generate CREATE2 address
                Op.SHA3(11, 85)
                + Op.DUP1  # Duplicate for second operation
                + benchmark_ops  # Execute operations in specified order
                # Increment salt
                + Op.MSTORE(32, Op.ADD(Op.MLOAD(32), 1))
            ),
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


# ERC20 function selectors
BALANCEOF_SELECTOR = 0x70A08231  # balanceOf(address)
APPROVE_SELECTOR = 0x095EA7B3  # approve(address,uint256)


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "sload_percent,sstore_percent",
    [
        pytest.param(50, 50, id="50-50"),
        pytest.param(70, 30, id="70-30"),
        pytest.param(90, 10, id="90-10"),
    ],
)
def test_mixed_sload_sstore(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
    address_stubs,
    sload_percent: int,
    sstore_percent: int,
):
    """
    BloatNet mixed SLOAD/SSTORE benchmark with configurable operation ratios.

    This test:
    1. Auto-discovers ERC20 contracts from stubs
    2. Divides gas budget evenly across all contracts
    3. For each contract, divides gas into SLOAD and SSTORE portions by
       percentage
    4. Executes balanceOf (SLOAD) and approve (SSTORE) calls per the ratio
    5. Stresses clients with combined read/write operations on large
       contracts
    """
    gas_costs = fork.gas_costs()

    # Calculate gas costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    num_contracts = len(address_stubs.root)

    # Cost per SLOAD iteration (balanceOf call)
    sload_cost_per_iteration = (
        # Attack contract loop overhead
        gas_costs.G_VERY_LOW * 2  # MLOAD counter (3*2)
        + gas_costs.G_VERY_LOW * 2  # MSTORE selector (3*2)
        + gas_costs.G_VERY_LOW * 3  # MLOAD + MSTORE address (3*3)
        + gas_costs.G_BASE  # POP (2)
        + gas_costs.G_BASE * 3  # SUB + MLOAD + MSTORE for counter decrement (2*3)
        + gas_costs.G_BASE * 2  # ISZERO * 2 for loop condition (2*2)
        + gas_costs.G_MID  # JUMPI (8)
        # CALL to ERC20 contract
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm CALL to same contract (100)
        # Inside ERC20 balanceOf
        + gas_costs.G_VERY_LOW  # PUSH4 selector (3)
        + gas_costs.G_BASE  # EQ selector match (2)
        + gas_costs.G_MID  # JUMPI to function (8)
        + gas_costs.G_JUMPDEST  # JUMPDEST at function start (1)
        + gas_costs.G_VERY_LOW * 2  # CALLDATALOAD arg (3*2)
        + gas_costs.G_KECCAK_256  # keccak256 static (30)
        + gas_costs.G_KECCAK_256_WORD * 2  # keccak256 dynamic for 64 bytes (2*6)
        + gas_costs.G_COLD_SLOAD  # Cold SLOAD (2100)
        + gas_costs.G_VERY_LOW * 3  # MSTORE result + RETURN setup (3*3)
    )

    # Cost per SSTORE iteration (approve call)
    sstore_cost_per_iteration = (
        # Attack contract loop body operations
        gas_costs.G_VERY_LOW  # MSTORE selector at memory[32] (3)
        + gas_costs.G_LOW  # MLOAD counter (5)
        + gas_costs.G_VERY_LOW  # MSTORE spender at memory[64] (3)
        + gas_costs.G_LOW  # MLOAD counter (5)
        + gas_costs.G_VERY_LOW  # MSTORE amount at memory[96] (3)
        # CALL to ERC20 contract
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm CALL base cost (100)
        + gas_costs.G_BASE  # POP call result (2)
        # Counter decrement
        + gas_costs.G_LOW  # MLOAD counter (5)
        + gas_costs.G_VERY_LOW  # PUSH1 1 (3)
        + gas_costs.G_VERY_LOW  # SUB (3)
        + gas_costs.G_VERY_LOW  # MSTORE counter back (3)
        # While loop condition check
        + gas_costs.G_LOW  # MLOAD counter (5)
        + gas_costs.G_BASE  # ISZERO (2)
        + gas_costs.G_BASE  # ISZERO (2)
        + gas_costs.G_MID  # JUMPI back to loop start (8)
        # Inside ERC20 approve function
        + gas_costs.G_VERY_LOW  # PUSH4 selector (3)
        + gas_costs.G_BASE  # EQ selector match (2)
        + gas_costs.G_MID  # JUMPI to function (8)
        + gas_costs.G_JUMPDEST  # JUMPDEST at function start (1)
        + gas_costs.G_VERY_LOW  # CALLDATALOAD spender (3)
        + gas_costs.G_VERY_LOW  # CALLDATALOAD amount (3)
        + gas_costs.G_KECCAK_256  # keccak256 static (30)
        + gas_costs.G_KECCAK_256_WORD * 2  # keccak256 dynamic for 64 bytes (12)
        + gas_costs.G_STORAGE_SET  # SSTORE to zero slot (20000)
        + gas_costs.G_VERY_LOW  # PUSH1 1 for return value (3)
        + gas_costs.G_VERY_LOW  # MSTORE return value (3)
        + gas_costs.G_VERY_LOW  # PUSH1 32 for return size (3)
        + gas_costs.G_VERY_LOW  # PUSH1 0 for return offset (3)
    )

    # Calculate gas budget per contract
    available_gas = gas_benchmark_value - intrinsic_gas
    gas_per_contract = available_gas // num_contracts

    # For each contract, split gas by percentage
    sload_gas_per_contract = (gas_per_contract * sload_percent) // 100
    sstore_gas_per_contract = (gas_per_contract * sstore_percent) // 100

    # Calculate calls per contract per operation
    sload_calls_per_contract = int(sload_gas_per_contract // sload_cost_per_iteration)
    sstore_calls_per_contract = int(sstore_gas_per_contract // sstore_cost_per_iteration)

    # Deploy all discovered ERC20 contracts using stubs
    erc20_addresses = []
    for stub_name in address_stubs.root:
        addr = pre.deploy_contract(
            code=Bytecode(),
            stub=stub_name,
        )
        erc20_addresses.append(addr)

    # Log test requirements
    print(
        f"Total gas budget: {gas_benchmark_value / 1_000_000:.1f}M gas. "
        f"~{gas_per_contract / 1_000_000:.1f}M gas per contract "
        f"({sload_percent}% SLOAD, {sstore_percent}% SSTORE). "
        f"Per contract: {sload_calls_per_contract} balanceOf calls, "
        f"{sstore_calls_per_contract} approve calls."
    )

    # Build attack code that loops through each contract
    attack_code: Bytecode = (
        Op.JUMPDEST  # Entry point
        # Store selectors once for all contracts (saves gas)
        + Op.MSTORE(offset=0, value=BALANCEOF_SELECTOR)
        + Op.MSTORE(offset=100, value=APPROVE_SELECTOR)
    )

    for erc20_address in erc20_addresses:
        # For each contract, execute SLOAD operations (balanceOf)
        attack_code += (
            # Initialize counter in memory[32] = number of balanceOf calls
            Op.MSTORE(offset=32, value=sload_calls_per_contract)
            # Loop for balanceOf calls
            + While(
                condition=Op.MLOAD(32) + Op.ISZERO + Op.ISZERO,
                body=(
                    # Call balanceOf(address) on ERC20 contract
                    # args_offset=28 reads: selector from MEM[28:32] + address
                    # from MEM[32:64]
                    Op.CALL(
                        address=erc20_address,
                        value=0,
                        args_offset=28,
                        args_size=36,
                        ret_offset=0,
                        ret_size=0,
                    )
                    + Op.POP  # Discard CALL success status
                    # Decrement counter
                    + Op.MSTORE(offset=32, value=Op.SUB(Op.MLOAD(32), 1))
                ),
            )
        )

        # For each contract, execute SSTORE operations (approve)
        attack_code += (
            # Initialize counter in memory[132] = number of approve calls
            Op.MSTORE(offset=132, value=sstore_calls_per_contract)
            # Loop for approve calls
            + While(
                condition=Op.MLOAD(132) + Op.ISZERO + Op.ISZERO,
                body=(
                    # Store spender address at memory[164] (use counter)
                    Op.MSTORE(offset=164, value=Op.MLOAD(132))
                    # Store amount at memory[196] (use counter as amount)
                    + Op.MSTORE(offset=196, value=Op.MLOAD(132))
                    # Call approve(spender, amount) on ERC20 contract
                    # args_offset=128 reads: selector from MEM[128:132] +
                    # spender from MEM[132:164] + amount from MEM[164:196]
                    + Op.CALL(
                        address=erc20_address,
                        value=0,
                        args_offset=128,
                        args_size=68,
                        ret_offset=0,
                        ret_size=0,
                    )
                    + Op.POP  # Discard CALL success status
                    # Decrement counter
                    + Op.MSTORE(offset=132, value=Op.SUB(Op.MLOAD(132), 1))
                ),
            )
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
