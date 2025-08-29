"""
abstract: Tests [BloatNet](https://bloatnet.info)
    Test cases for [BloatNet](https://bloatnet.info).
"""

import pytest

from ethereum_test_base_types import HashInt
from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Bytecode,
    Hash,
    Storage,
    Transaction,
    While,
    keccak256,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "DUMMY/eip-DUMMY.md"
REFERENCE_SPEC_VERSION = "0.1"

# Constants for CREATE2 address calculation
CREATE2_PREFIX = 0xFF
CREATE2_MEMORY_OFFSET = 0x1000  # Offset for CREATE2 calculation to avoid collision


def calculate_create2_address(deployer_address, salt: int, init_code: bytes):
    """Calculate CREATE2 deterministic address."""
    # Handle both string and Address types
    if isinstance(deployer_address, str):
        addr_hex = deployer_address[2:] if deployer_address.startswith("0x") else deployer_address
        deployer_bytes = bytes.fromhex(addr_hex)
    else:
        # Assume it's an Address object with bytes representation
        deployer_bytes = bytes(deployer_address)
    salt_bytes = salt.to_bytes(32, "big")
    init_code_hash = keccak256(init_code)

    packed = bytes([CREATE2_PREFIX]) + deployer_bytes + salt_bytes + init_code_hash
    address_hash = keccak256(packed)
    return Address(address_hash[-20:])


def generate_create2_address_calculation(
    factory_address,
    init_code_hash: bytes,
) -> Bytecode:
    """Generate EVM bytecode to calculate a CREATE2 address with salt on stack."""
    code = Bytecode()

    # Memory layout at CREATE2_MEMORY_OFFSET:
    # [0xFF][factory_address][salt][init_code_hash]
    base = CREATE2_MEMORY_OFFSET

    # Store 0xFF prefix at memory[base]
    code += Op.PUSH1(CREATE2_PREFIX) + Op.PUSH2(base) + Op.MSTORE8

    # Store factory address at memory[base+1:base+21]
    # Handle both string and Address types
    if isinstance(factory_address, str):
        addr_hex = factory_address[2:] if factory_address.startswith("0x") else factory_address
        factory_bytes = bytes.fromhex(addr_hex)
    else:
        # Assume it's an Address object with bytes representation
        factory_bytes = bytes(factory_address)
    code += Op.PUSH20(int.from_bytes(factory_bytes, "big")) + Op.PUSH2(base + 1) + Op.MSTORE

    # Store salt at memory[base+21:base+53] (base+0x15)
    # Assumes salt is already on stack
    code += Op.PUSH2(base + 0x15) + Op.MSTORE

    # Store init code hash at memory[base+53:base+85] (base+0x35)
    code += Op.PUSH32(int.from_bytes(init_code_hash, "big")) + Op.PUSH2(base + 0x35) + Op.MSTORE

    # Calculate keccak256 of 85 bytes starting at memory[base]
    code += Op.PUSH1(0x55) + Op.PUSH2(base) + Op.SHA3

    # The address is the last 20 bytes (already on stack)
    return code


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("final_storage_value", [0x02 << 248, 0x02])
def test_bloatnet(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    final_storage_value: int,
    gas_benchmark_value: int,
):
    """
    A test that calls a contract with many SSTOREs.

    The first block will have many SSTORES that go from 0 -> 1
    and the 2nd block will have many SSTORES that go from 1 -> 2
    """
    # Get gas costs for the current fork
    gas_costs = fork.gas_costs()

    # this is only used for computing the intinsic gas
    data = final_storage_value.to_bytes(32, "big").rstrip(b"\x00")

    storage = Storage()

    # Initial gas for PUSH0 + CALLDATALOAD + POP (at the end)
    totalgas = gas_costs.G_BASE * 2 + gas_costs.G_VERY_LOW
    totalgas = totalgas + fork.transaction_intrinsic_cost_calculator()(calldata=data)
    gas_increment = gas_costs.G_VERY_LOW * 2 + gas_costs.G_STORAGE_SET + gas_costs.G_COLD_SLOAD
    sstore_code = Op.PUSH0 + Op.CALLDATALOAD
    storage_slot: int = 0
    while totalgas + gas_increment < gas_benchmark_value:
        totalgas += gas_increment
        sstore_code = sstore_code + Op.SSTORE(storage_slot, Op.DUP1)
        storage[storage_slot] = final_storage_value
        storage_slot += 1

    sstore_code = sstore_code + Op.POP  # Drop last value on the stack

    sender = pre.fund_eoa()
    print(sender)
    contract_address = pre.deploy_contract(
        code=sstore_code,
        storage=Storage(),
    )

    tx_0_1 = Transaction(
        to=contract_address,
        gas_limit=gas_benchmark_value,
        data=(final_storage_value // 2).to_bytes(32, "big").rstrip(b"\x00"),
        value=0,
        sender=sender,
    )
    tx_1_2 = Transaction(
        to=contract_address,
        gas_limit=gas_benchmark_value,
        data=final_storage_value.to_bytes(32, "big").rstrip(b"\x00"),
        value=0,
        sender=sender,
    )

    post = {contract_address: Account(storage=storage)}

    blockchain_test(pre=pre, blocks=[Block(txs=[tx_0_1, tx_1_2])], post=post)


# Warm reads are very cheap, which means you can really fill a block
# with them. Only fill the block by a factor of SPEEDUP.
SPEEDUP: int = 100


@pytest.mark.valid_from("Prague")
def test_bloatnet_sload_warm(
    blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork, gas_benchmark_value: int
):
    """Test that loads warm storage locations many times."""
    gas_costs = fork.gas_costs()

    # Pre-fill storage with values
    num_slots = 100  # Number of storage slots to warm up
    storage = Storage({HashInt(i): HashInt(0xDEADBEEF + i) for i in range(num_slots)})

    # Calculate gas costs
    totalgas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # First pass - warm up all slots (cold access)
    warmup_gas = num_slots * (gas_costs.G_COLD_SLOAD + gas_costs.G_BASE)
    totalgas += warmup_gas

    # Calculate how many warm loads we can fit
    gas_increment = gas_costs.G_WARM_SLOAD + gas_costs.G_BASE  # Warm SLOAD + POP
    remaining_gas = gas_benchmark_value - totalgas
    num_warm_loads = remaining_gas // (SPEEDUP * gas_increment)

    # Build the complete code: warmup + repeated warm loads
    sload_code = Op.SLOAD(0) + Op.POP if num_slots > 0 else Op.STOP
    for i in range(1, num_slots):
        sload_code = sload_code + Op.SLOAD(i) + Op.POP
    for i in range(num_warm_loads):
        sload_code = sload_code + Op.SLOAD(i % num_slots) + Op.POP

    sender = pre.fund_eoa()
    contract_address = pre.deploy_contract(
        code=sload_code,
        storage=storage,
    )

    tx = Transaction(
        to=contract_address,
        gas_limit=gas_benchmark_value,
        data=b"",
        value=0,
        sender=sender,
    )

    post = {contract_address: Account(storage=storage)}
    blockchain_test(pre=pre, blocks=[Block(txs=[tx])], post=post)


@pytest.mark.valid_from("Prague")
def test_bloatnet_sload_cold(
    blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork, gas_benchmark_value: int
):
    """Test that loads many different cold storage locations."""
    gas_costs = fork.gas_costs()

    # Calculate gas costs and max slots
    totalgas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")
    # PUSH + Cold SLOAD + POP
    gas_increment = gas_costs.G_VERY_LOW + gas_costs.G_COLD_SLOAD + gas_costs.G_BASE
    max_slots = (gas_benchmark_value - totalgas) // gas_increment

    # Build storage and code for all slots
    storage = Storage({HashInt(i): HashInt(0xC0FFEE + i) for i in range(max_slots)})
    sload_code = Op.SLOAD(0) + Op.POP if max_slots > 0 else Op.STOP
    for i in range(1, max_slots):
        sload_code = sload_code + Op.SLOAD(i) + Op.POP

    sender = pre.fund_eoa()
    contract_address = pre.deploy_contract(
        code=sload_code,
        storage=storage,
    )

    tx = Transaction(
        to=contract_address,
        gas_limit=gas_benchmark_value,
        data=b"",
        value=0,
        sender=sender,
    )

    post = {contract_address: Account(storage=storage)}
    blockchain_test(pre=pre, blocks=[Block(txs=[tx])], post=post)


# Storage slot for success flag
SUCCESS_FLAG_SLOT = 0
SUCCESS_FLAG_VALUE = 42
EXTCODECOPY_MEMORY_OFFSET = 0x1000  # 4KB offset to avoid conflicts with address storage


@pytest.mark.valid_from("Prague")
def test_bloatnet_extcodesize_balance(
    blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork, gas_benchmark_value: int
):
    """
    Test that maximizes I/O reads by combining cold BALANCE with warm EXTCODESIZE calls.

    This test uses CREATE2 deterministic addressing to avoid bytecode size limitations.
    It deploys many 24kB contracts with unique bytecode, then:
    1. Calls BALANCE on all contracts (cold access) to warm them and fill cache
    2. Calls EXTCODESIZE on all contracts (warm access) hoping cache evictions force re-reads

    Goal: Maximum I/O read operations with minimum gas consumption.
    """
    gas_costs = fork.gas_costs()
    max_contract_size = fork.max_code_size()

    # Calculate costs for the attack transaction
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Calculate memory expansion cost for CREATE2 address calculation
    # CREATE2 uses memory at offset 0x1000 for 85 bytes
    memory_expansion_cost = fork.memory_expansion_gas_calculator()(
        new_bytes=CREATE2_MEMORY_OFFSET + 85
    )

    # Cost per iteration with CREATE2 address calculation
    # Additional cost for CREATE2 address calculation (~75 gas)
    create2_calc_cost = (
        gas_costs.G_VERY_LOW * 8  # Memory operations (MSTORE/MSTORE8)
        + 30
        + 6 * 3  # KECCAK256 for 85 bytes
        + gas_costs.G_VERY_LOW * 10  # Stack operations
    )

    cost_per_iteration = (
        create2_calc_cost  # CREATE2 address calculation
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold BALANCE
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm EXTCODESIZE (same account)
        + gas_costs.G_BASE * 2  # POPs for results
        + gas_costs.G_VERY_LOW * 3  # Loop overhead (DUP, PUSH1, ADD)
    )

    # Access costs in attack transaction
    final_storage_cost = (
        gas_costs.G_STORAGE_RESET + gas_costs.G_COLD_SLOAD + gas_costs.G_VERY_LOW * 2
    )
    available_gas_for_access = (
        gas_benchmark_value - intrinsic_gas - final_storage_cost - memory_expansion_cost
    )

    # Calculate maximum contracts we can access
    # Reserve some gas for the final SSTORE operation
    reserved_gas = 50000  # Reserve 50k gas for final operations and safety
    available_gas_for_loops = available_gas_for_access - reserved_gas
    # Use 98% of calculated contracts (less conservative)
    num_contracts = int(available_gas_for_loops // cost_per_iteration * 0.98)

    # Generate unique bytecode for deployment (will be same for all to simplify init_code_hash)
    deploy_bytecode = Bytecode(Op.STOP)  # First byte is STOP for safety
    pattern_count = 0
    while len(deploy_bytecode) < max_contract_size - 100:
        unique_value = Hash(pattern_count)
        deploy_bytecode += Op.PUSH32[unique_value] + Op.POP
        pattern_count += 1
    while len(deploy_bytecode) < max_contract_size:
        deploy_bytecode += Op.JUMPDEST

    assert len(deploy_bytecode) == max_contract_size, (
        f"Contract size mismatch: {len(deploy_bytecode)}"
    )

    # Init code that returns the bytecode
    init_code = Op.CODECOPY(0, 0, Op.CODESIZE) + Op.RETURN(0, Op.CODESIZE) + deploy_bytecode
    init_code_hash = keccak256(bytes(init_code))

    # Factory address that would deploy contracts with CREATE2
    factory_address = pre.deploy_contract(code=Op.STOP)  # Simple factory placeholder

    # Pre-deploy all contracts at CREATE2 addresses using sequential salts
    deployed_contracts = []  # Track for post-state validation
    for salt in range(num_contracts):
        # Calculate the CREATE2 address
        create2_addr = calculate_create2_address(factory_address, salt, bytes(init_code))
        # Deploy at the calculated address
        pre[create2_addr] = Account(code=deploy_bytecode)
        deployed_contracts.append(create2_addr)

    # Create the attack contract that calculates CREATE2 addresses and calls operations
    attack_code = Bytecode()

    # Pre-compute the CREATE2 calculation bytecode
    create2_calc = generate_create2_address_calculation(factory_address, init_code_hash)

    # Main loop: iterate through all contracts
    attack_code += Op.PUSH0  # Counter starts at 0
    attack_code += While(
        body=(
            # Calculate CREATE2 address for current salt (counter)
            Op.DUP1  # Duplicate counter (salt)
            + create2_calc  # Calculate CREATE2 address (consumes salt, leaves address)
            # Call BALANCE (cold access) - this warms the account
            + Op.DUP1  # Duplicate address
            + Op.BALANCE  # Get balance
            + Op.POP  # Discard balance result
            # Call EXTCODESIZE (warm access) - hoping cache was evicted
            + Op.EXTCODESIZE  # Get code size (address already on stack)
            + Op.POP  # Discard code size result
            # Increment counter
            + Op.PUSH1[1]
            + Op.ADD
        ),
        condition=Op.GT(num_contracts, Op.DUP1),  # num_contracts > counter
    )
    attack_code += Op.POP  # Clean up counter
    # Store success flag for validation
    attack_code += Op.SSTORE(SUCCESS_FLAG_SLOT, SUCCESS_FLAG_VALUE)

    # Pre-initialize storage slot 0 to avoid cold SSTORE cost
    attack_address = pre.deploy_contract(code=attack_code, storage={SUCCESS_FLAG_SLOT: 1})

    # Attack transaction
    attack_tx = Transaction(
        to=attack_address,
        gas_limit=gas_benchmark_value,
        sender=pre.fund_eoa(),
    )

    # Post-state validation
    post = {
        # Verify attack completed successfully
        attack_address: Account(storage={SUCCESS_FLAG_SLOT: SUCCESS_FLAG_VALUE}),
    }

    # Verify all pre-deployed contracts still exist with their code intact
    # We check that they have nonce=1 (contracts were deployed)
    for contract_address in deployed_contracts:
        post[contract_address] = Account(
            nonce=1,  # Contract exists and was deployed
        )

    blockchain_test(
        pre=pre,
        blocks=[
            Block(txs=[attack_tx]),  # Execute the attack
        ],
        post=post,
        exclude_full_post_state_in_output=True,  # Reduce output size
    )


@pytest.mark.valid_from("Prague")
def test_bloatnet_extcodecopy_balance(
    blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork, gas_benchmark_value: int
):
    """
    Test that maximizes actual I/O reads using BALANCE + EXTCODECOPY combination.

    This test uses CREATE2 deterministic addressing to avoid bytecode size limitations.
    It achieves maximum data reads from disk by:
    1. Pre-deploying many 24KB contracts with unique bytecode
    2. Calling BALANCE (cold) to warm the account - reads metadata (~200 bytes)
    3. Calling EXTCODECOPY (warm) to read the full 24KB bytecode

    The BALANCE + EXTCODECOPY pattern is optimal because:
    - BALANCE warms the account, reducing EXTCODECOPY base cost from 2600 to 100
    - EXTCODECOPY forces reading the actual bytecode from disk (not just metadata)
    - Total cost: ~5129 gas per contract for 24KB of data read (including CREATE2 calculation)

    This test reads 123x more data per contract than BALANCE + EXTCODESIZE pattern.
    """
    gas_costs = fork.gas_costs()
    max_contract_size = fork.max_code_size()

    # Calculate costs for the attack transaction
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Calculate memory expansion cost for CREATE2 address calculation
    # CREATE2 uses memory at offset 0x1000 for 85 bytes
    memory_expansion_cost = fork.memory_expansion_gas_calculator()(
        new_bytes=CREATE2_MEMORY_OFFSET + 85
    )

    # Cost per iteration with CREATE2 address calculation
    # Additional cost for CREATE2 address calculation (~75 gas)
    create2_calc_cost = (
        gas_costs.G_VERY_LOW * 8  # Memory operations (MSTORE/MSTORE8)
        + 30
        + 6 * 3  # KECCAK256 for 85 bytes
        + gas_costs.G_VERY_LOW * 10  # Stack operations
    )

    # EXTCODECOPY copies full 24KB to memory
    words_to_copy = (max_contract_size + 31) // 32  # 768 words for 24KB
    cost_per_iteration = (
        create2_calc_cost  # CREATE2 address calculation
        + gas_costs.G_VERY_LOW  # DUP1 for address
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Cold BALANCE (2600)
        + gas_costs.G_BASE  # POP balance result
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm EXTCODECOPY base (100)
        + gas_costs.G_COPY * words_to_copy  # Copy cost (3 * 768 = 2304)
        + gas_costs.G_BASE  # POP address
        + gas_costs.G_VERY_LOW * 3  # Loop overhead (PUSH1, ADD, DUP for condition)
    )

    # Calculate memory expansion cost for EXTCODECOPY destination
    # EXTCODECOPY writes 24KB at offset 0x1000
    extcodecopy_memory_expansion = fork.memory_expansion_gas_calculator()(
        new_bytes=EXTCODECOPY_MEMORY_OFFSET + max_contract_size
    )
    # CREATE2 calculation also uses memory (already accounted in memory_expansion_cost)

    # Access costs in attack transaction
    final_storage_cost = (
        gas_costs.G_STORAGE_RESET + gas_costs.G_COLD_SLOAD + gas_costs.G_VERY_LOW * 2
    )
    available_gas_for_access = (
        gas_benchmark_value
        - intrinsic_gas
        - final_storage_cost
        - memory_expansion_cost
        - extcodecopy_memory_expansion
    )

    # Calculate maximum contracts we can access
    # This test scales automatically: ~1000 contracts at 90M gas, ~10,000 at 900M gas
    # Reserve some gas for the final SSTORE operation
    reserved_gas = 50000  # Reserve 50k gas for final operations and safety
    available_gas_for_loops = available_gas_for_access - reserved_gas
    # Use 98% of calculated contracts (less conservative)
    num_contracts = int(available_gas_for_loops // cost_per_iteration * 0.98)

    # Generate base bytecode template
    base_bytecode = Bytecode(Op.STOP)  # First byte is STOP for safety
    pattern_count = 0
    while len(base_bytecode) < max_contract_size - 100:
        unique_value = Hash(pattern_count)
        base_bytecode += Op.PUSH32[unique_value] + Op.POP
        pattern_count += 1
    while len(base_bytecode) < max_contract_size:
        base_bytecode += Op.JUMPDEST

    assert len(base_bytecode) == max_contract_size, (
        f"Base bytecode size mismatch: {len(base_bytecode)}"
    )

    # Init code that returns the bytecode
    init_code = Op.CODECOPY(0, 0, Op.CODESIZE) + Op.RETURN(0, Op.CODESIZE) + base_bytecode
    init_code_hash = keccak256(bytes(init_code))

    # Factory address for CREATE2
    factory_address = pre.deploy_contract(code=Op.STOP)  # Simple factory placeholder

    # Pre-deploy all contracts at CREATE2 addresses with unique bytecode
    deployed_contracts = []  # Track for post-state validation
    for salt in range(num_contracts):
        # Generate unique bytecode for this contract
        bytecode = Bytecode(Op.STOP)
        pattern_count = 0
        while len(bytecode) < max_contract_size - 100:
            unique_value = Hash(salt * 1000000 + pattern_count)
            bytecode += Op.PUSH32[unique_value] + Op.POP
            pattern_count += 1
        while len(bytecode) < max_contract_size:
            bytecode += Op.JUMPDEST

        assert len(bytecode) == max_contract_size, f"Contract size mismatch: {len(bytecode)}"

        # Calculate CREATE2 address using the base init code
        # Note: In real implementation, each contract has unique bytecode but same init structure
        create2_addr = calculate_create2_address(factory_address, salt, bytes(init_code))

        # Deploy at the calculated address with unique bytecode
        pre[create2_addr] = Account(code=bytecode)
        deployed_contracts.append(create2_addr)

    # Create the attack contract that calculates CREATE2 addresses and calls operations
    attack_code = Bytecode()

    # Pre-compute the CREATE2 calculation bytecode
    create2_calc = generate_create2_address_calculation(factory_address, init_code_hash)

    # Main loop: BALANCE + EXTCODECOPY for each contract
    attack_code += Op.PUSH0  # Counter starts at 0
    attack_code += While(
        body=(
            # Calculate CREATE2 address for current salt (counter)
            Op.DUP1  # Duplicate counter (salt)
            + create2_calc  # Calculate CREATE2 address (consumes salt, leaves address)
            # Call BALANCE (cold access) - warms the account
            + Op.DUP1  # Duplicate address for BALANCE
            + Op.BALANCE  # Get balance (cold, 2600 gas)
            + Op.POP  # Discard balance result
            # Call EXTCODECOPY (warm access) - reads full 24KB bytecode
            + Op.EXTCODECOPY(
                address=Op.DUP1,  # Use the same address (now warm)
                dest_offset=EXTCODECOPY_MEMORY_OFFSET,  # Copy to high memory
                offset=0,  # Start from beginning of bytecode
                size=max_contract_size,  # Copy full 24KB
            )
            + Op.POP  # Clean up address
            # Increment counter
            + Op.PUSH1[1]
            + Op.ADD
        ),
        condition=Op.GT(num_contracts, Op.DUP1),  # Fixed: num_contracts > counter
    )
    attack_code += Op.POP  # Clean up counter
    # Store success flag for validation
    attack_code += Op.SSTORE(SUCCESS_FLAG_SLOT, SUCCESS_FLAG_VALUE)

    # Pre-initialize storage slot 0 to avoid cold SSTORE cost
    attack_address = pre.deploy_contract(code=attack_code, storage={SUCCESS_FLAG_SLOT: 1})

    # Attack transaction
    attack_tx = Transaction(
        to=attack_address,
        gas_limit=gas_benchmark_value,
        sender=pre.fund_eoa(),
    )

    # Post-state validation
    post = {
        # Verify attack completed successfully
        attack_address: Account(storage={SUCCESS_FLAG_SLOT: SUCCESS_FLAG_VALUE}),
    }

    # Verify all pre-deployed contracts still exist
    for contract_address in deployed_contracts:
        post[contract_address] = Account(
            nonce=1,  # Contract exists and was deployed
        )

    blockchain_test(
        pre=pre,
        blocks=[
            Block(txs=[attack_tx]),  # Execute the attack
        ],
        post=post,
        exclude_full_post_state_in_output=True,  # Reduce output size
    )
