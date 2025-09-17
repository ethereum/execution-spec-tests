"""
abstract: Optimized BloatNet tests using CREATE2 pre-deployed contracts.

    This test uses CREATE2 factory-deployed contracts at deterministic addresses.
    Deploy contracts using: python3 scripts/deploy_bloatnet_simple.py --num-contracts 1838

    The CREATE2 pattern allows:
    - Contracts to be deployed from any account
    - Reuse across different test scenarios
    - Deterministic addresses regardless of deployer nonce
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Bytecode,
    Transaction,
    keccak256,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "DUMMY/bloatnet.md"
REFERENCE_SPEC_VERSION = "1.0"

# Gas cost constants - used to calculate required contracts for any gas limit
# See README.md for detailed breakdown of these costs
GAS_PER_CONTRACT_BALANCE_EXTCODESIZE = 2707  # BALANCE(cold) + EXTCODESIZE(warm)
GAS_PER_CONTRACT_BALANCE_EXTCODECOPY = 5007  # BALANCE(cold) + EXTCODECOPY(warm, 24KB)

# Configuration for CREATE2 pre-deployed contracts
# These values must match what the deployment script generates
# UPDATE THESE VALUES after running deploy_bloatnet_simple.py
FACTORY_ADDRESS = Address("0x07EADb2f6b02Bb9fE994c0AeFf106625c0d3C93f")  # UPDATE THIS
INIT_CODE_HASH = bytes.fromhex(
    "8eba8b9d04aea4e6f3d6601ad364021e8e37b6282a0f57e40c635ba7f80aa0cb"
)  # UPDATE THIS
NUM_DEPLOYED_CONTRACTS = 1838  # UPDATE THIS - current setup for 5M gas


def calculate_create2_address(factory: Address, salt: int, init_code_hash: bytes) -> Address:
    """Calculate CREATE2 address from factory, salt, and init code hash."""
    create2_input = b"\xff" + bytes(factory) + salt.to_bytes(32, "big") + init_code_hash
    addr_bytes = keccak256(create2_input)[12:]
    return Address(addr_bytes)


@pytest.mark.valid_from("Prague")
def test_bloatnet_balance_extcodesize(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
):
    """
    BloatNet test using BALANCE + EXTCODESIZE pattern.

    This test:
    1. Uses 100+ pre-deployed 24KB contracts
    2. Calls BALANCE (cold) then EXTCODESIZE (warm) on each
    3. Maximizes cache eviction by accessing many contracts
    4. Runs with benchmark gas values (5M, 50M, 500M)
    """
    gas_costs = fork.gas_costs()

    # Calculate gas costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Cost per contract access
    cost_per_contract = (
        3  # PUSH20 for address
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold BALANCE (2600)
        + gas_costs.G_BASE  # POP balance
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm EXTCODESIZE (100)
        + gas_costs.G_BASE  # POP code size
    )

    # Calculate how many contracts to access
    available_gas = gas_benchmark_value - intrinsic_gas - 1000  # Reserve for cleanup
    contracts_needed = int(available_gas // cost_per_contract)
    num_contracts = min(contracts_needed, NUM_DEPLOYED_CONTRACTS)

    # Log the calculation for transparency
    if contracts_needed > NUM_DEPLOYED_CONTRACTS:
        import warnings

        warnings.warn(
            f"Test needs {contracts_needed} contracts for "
            f"{gas_benchmark_value / 1_000_000:.1f}M gas, "
            f"but only {NUM_DEPLOYED_CONTRACTS} are deployed. "
            f"Deploy {contracts_needed - NUM_DEPLOYED_CONTRACTS} more contracts "
            f"for full test coverage.",
            stacklevel=2,
        )

    # Generate attack contract with unrolled loop
    attack_code = Bytecode()

    # Pre-calculate all contract addresses using CREATE2
    for i in range(num_contracts):
        addr = calculate_create2_address(FACTORY_ADDRESS, i, INIT_CODE_HASH)
        attack_code += (
            Op.PUSH20[int.from_bytes(bytes(addr), "big")]
            + Op.DUP1
            + Op.BALANCE
            + Op.POP
            + Op.EXTCODESIZE
            + Op.POP
        )

    # Success marker (benchmark tests typically run out of gas, but this is for smaller tests)
    attack_code += Op.PUSH1[1] + Op.PUSH0 + Op.SSTORE

    # Deploy attack contract
    attack_address = pre.deploy_contract(code=attack_code)

    # Attack transaction
    tx = Transaction(
        to=attack_address,
        gas_limit=gas_benchmark_value,
        sender=pre.fund_eoa(),
    )

    # Post-state: just verify attack contract exists
    # Benchmark tests run out of gas, so no success flag
    post = {
        attack_address: Account(storage={}),
    }

    blockchain_test(
        pre=pre,
        blocks=[Block(txs=[tx])],
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
    BloatNet test using BALANCE + EXTCODECOPY for maximum I/O.

    This test forces actual bytecode reads from disk by:
    1. Using BALANCE (cold) to warm the account
    2. Using EXTCODECOPY (warm) to read the full 24KB bytecode

    This pattern reads ~123x more data per gas than EXTCODESIZE.
    """
    gas_costs = fork.gas_costs()
    max_contract_size = fork.max_code_size()

    # Calculate costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Memory expansion for EXTCODECOPY
    max_memory_needed = max_contract_size * 10  # Limit to 10 contracts worth of memory
    memory_cost = fork.memory_expansion_gas_calculator()(new_bytes=max_memory_needed)

    # Cost per contract with EXTCODECOPY
    words_to_copy = (max_contract_size + 31) // 32  # 768 words for 24KB
    cost_per_contract = (
        3  # PUSH20 for address
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold BALANCE (2600)
        + gas_costs.G_BASE  # POP balance
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm EXTCODECOPY base (100)
        + gas_costs.G_COPY * words_to_copy  # Copy cost (3 * 768 = 2304)
        + gas_costs.G_BASE * 4  # PUSH operations and POP
    )

    # Calculate how many contracts to access
    available_gas = gas_benchmark_value - intrinsic_gas - memory_cost - 1000
    contracts_needed = int(available_gas // cost_per_contract)
    num_contracts = min(
        contracts_needed,
        NUM_DEPLOYED_CONTRACTS,
        10,  # Limit to avoid excessive memory usage in test
    )

    # Log the calculation for transparency
    if contracts_needed > NUM_DEPLOYED_CONTRACTS:
        import warnings

        warnings.warn(
            f"Test needs {contracts_needed} contracts for "
            f"{gas_benchmark_value / 1_000_000:.1f}M gas, "
            f"but only {NUM_DEPLOYED_CONTRACTS} are deployed. "
            f"Deploy {contracts_needed - NUM_DEPLOYED_CONTRACTS} more contracts "
            f"for full test coverage.",
            stacklevel=2,
        )

    # Generate attack contract
    attack_code = Bytecode()
    mem_offset = 0

    # Access each contract using CREATE2 addresses
    for i in range(num_contracts):
        addr = calculate_create2_address(FACTORY_ADDRESS, i, INIT_CODE_HASH)
        attack_code += (
            Op.PUSH20[int.from_bytes(bytes(addr), "big")]
            + Op.DUP1
            + Op.BALANCE
            + Op.POP
            # EXTCODECOPY(addr, mem_offset, 0, 24KB)
            + Op.PUSH2[max_contract_size]  # size
            + Op.PUSH1[0]  # code offset
            + Op.PUSH3[mem_offset]  # memory offset
            + Op.DUP4  # address
            + Op.EXTCODECOPY
            + Op.POP  # clean up address
        )
        mem_offset += max_contract_size

    # Deploy attack contract
    attack_address = pre.deploy_contract(code=attack_code)

    # Attack transaction
    tx = Transaction(
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
        blocks=[Block(txs=[tx])],
        post=post,
    )
