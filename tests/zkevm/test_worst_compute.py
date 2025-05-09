"""
abstract: Tests zkEVMs worst-case compute scenarios.
    Tests zkEVMs worst-case compute scenarios.

Tests running worst-case compute opcodes and precompile scenarios for zkEVMs.
"""

import math
import os

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"

MAX_CODE_SIZE = 24 * 1024
KECCAK_RATE = 136
OPCODE_GAS_LIMIT = 100_000


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "gas_limit",
    [
        36_000_000,
    ],
)
def test_worst_keccak(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_limit: int,
):
    """Test running a block with as many KECCAK256 permutations as possible."""
    env = Environment(gas_limit=gas_limit)

    # Intrinsic gas cost is paid once.
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    available_gas = gas_limit - intrinsic_gas_calculator()

    gsc = fork.gas_costs()
    mem_exp_gas_calculator = fork.memory_expansion_gas_calculator()

    # Discover the optimal input size to maximize keccak-permutations, not keccak calls.
    # The complication of the discovery arises from the non-linear gas cost of memory expansion.
    max_keccak_perm_per_block = 0
    optimal_input_length = 0
    for i in range(1, 1_000_000, 32):
        iteration_gas_cost = (
            2 * gsc.G_VERY_LOW  # PUSHN + PUSH1
            + gsc.G_KECCAK_256  # KECCAK256 static cost
            + math.ceil(i / 32) * gsc.G_KECCAK_256_WORD  # KECCAK256 dynamic cost
            + gsc.G_BASE  # POP
        )
        # From the available gas, we substract the mem expansion costs considering we know the
        # current input size length i.
        available_gas_after_expansion = max(0, available_gas - mem_exp_gas_calculator(new_bytes=i))
        # Calculate how many calls we can do.
        num_keccak_calls = available_gas_after_expansion // iteration_gas_cost
        # KECCAK does 1 permutation every 136 bytes.
        num_keccak_permutations = num_keccak_calls * math.ceil(i / KECCAK_RATE)

        # If we found an input size that is better (reg permutations/gas), then save it.
        if num_keccak_permutations > max_keccak_perm_per_block:
            max_keccak_perm_per_block = num_keccak_permutations
            optimal_input_length = i

    # max_iters_loop contains how many keccak calls can be done per loop.
    # The loop is as big as possible bounded by the maximum code size.
    #
    # The loop structure is: JUMPDEST + [attack iteration] + PUSH0 + JUMP
    #
    # Now calculate available gas for [attack iteration]:
    #   Numerator = MAX_CODE_SIZE-3. The -3 is for the JUMPDEST, PUSH0 and JUMP.
    #   Denominator = (PUSHN + PUSH1 + KECCAK256 + POP) + PUSH1_DATA + PUSHN_DATA
    # TODO: the testing framework uses PUSH1(0) instead of PUSH0 which is suboptimal for the
    # attack, whenever this is fixed adjust accordingly.
    start_code = Op.JUMPDEST + Op.PUSH20[optimal_input_length]
    loop_code = Op.POP(Op.SHA3(Op.PUSH0, Op.DUP1))
    end_code = Op.POP + Op.JUMP(Op.PUSH0)
    max_iters_loop = (MAX_CODE_SIZE - (len(start_code) + len(end_code))) // len(loop_code)
    code = start_code + (loop_code * max_iters_loop) + end_code
    if len(code) > MAX_CODE_SIZE:
        # Must never happen, but keep it as a sanity check.
        raise ValueError(f"Code size {len(code)} exceeds maximum code size {MAX_CODE_SIZE}")

    code_address = pre.deploy_contract(code=bytes(code))

    tx = Transaction(
        to=code_address,
        gas_limit=gas_limit,
        gas_price=10,
        sender=pre.fund_eoa(),
        data=[],
        value=0,
    )

    blockchain_test(
        env=env,
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )


@pytest.mark.zkevm
@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "gas_limit",
    [
        Environment().gas_limit,
    ],
)
def test_worst_modexp(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_limit: int,
):
    """Test running a block with as many MODEXP calls as possible."""
    env = Environment(gas_limit=gas_limit)

    base_mod_length = 32
    exp_length = 32

    base = 2 ** (8 * base_mod_length) - 1
    mod = 2 ** (8 * base_mod_length) - 2  # Prevents base == mod
    exp = 2 ** (8 * exp_length) - 1

    # MODEXP calldata
    calldata = (
        Op.MSTORE(0 * 32, base_mod_length)
        + Op.MSTORE(1 * 32, exp_length)
        + Op.MSTORE(2 * 32, base_mod_length)
        + Op.MSTORE(3 * 32, base)
        + Op.MSTORE(4 * 32, exp)
        + Op.MSTORE(5 * 32, mod)
    )

    # EIP-2565
    mul_complexity = math.ceil(base_mod_length / 8) ** 2
    iter_complexity = exp.bit_length() - 1
    gas_cost = math.floor((mul_complexity * iter_complexity) / 3)
    attack_block = Op.POP(Op.STATICCALL(gas_cost, 0x5, 0, 32 * 6, 0, 0))

    # The attack contract is: JUMPDEST + [attack_block]* + PUSH0 + JUMP
    jumpdest = Op.JUMPDEST
    jump_back = Op.JUMP(len(calldata))
    max_iters_loop = (MAX_CODE_SIZE - len(calldata) - len(jumpdest) - len(jump_back)) // len(
        attack_block
    )
    code = calldata + jumpdest + sum([attack_block] * max_iters_loop) + jump_back
    if len(code) > MAX_CODE_SIZE:
        # Must never happen, but keep it as a sanity check.
        raise ValueError(f"Code size {len(code)} exceeds maximum code size {MAX_CODE_SIZE}")

    code_address = pre.deploy_contract(code=code)

    tx = Transaction(
        to=code_address,
        gas_limit=gas_limit,
        sender=pre.fund_eoa(),
    )

    blockchain_test(
        env=env,
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )


@pytest.mark.zkevm
@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "gas_limit",
    [36_000_000],
)
def test_jumps(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_limit: int,
):
    """Test with many JUMPs"""
    env = Environment(gas_limit=gas_limit)

    # Intrinsic gas cost is paid once
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    available_gas = gas_limit - intrinsic_gas_calculator()

    def opcode_block(pos):
        # could squeeze out a tiny bit more by using PUSH1 for pos < 256...
        return Op.PUSH2(3 + 5 * pos) + Op.JUMP + Op.JUMPDEST

    gsc = fork.gas_costs()
    # Gas cost breakdown for PUSH2 + JUMP + JUMPDEST pattern:
    # - PUSH2: G_VERY_LOW (3) - pushes a 2-byte value onto the stack
    # - JUMP: G_MID (8) - jumps to the destination
    # - JUMPDEST: G_JUMPDEST (1) - marks a valid jump destination
    # Total: 3 + 8 + 1 = 12 gas per iteration
    iteration_gas_cost = gsc.G_VERY_LOW + gsc.G_MID + gsc.G_JUMPDEST

    # Bytes per iteration calculation:
    # - PUSH2: 3 bytes (1 for opcode + 2 for the value)
    # - JUMP: 1 byte (opcode)
    # - JUMPDEST: 1 byte (opcode)
    # Total: 5 bytes per iteration
    bytes_per_iter = 5

    # Calculate max iterations based on code size and gas constraints
    max_iters_by_size = MAX_CODE_SIZE // bytes_per_iter
    max_iters_by_gas = available_gas // iteration_gas_cost
    num_iters = int(min(max_iters_by_size, max_iters_by_gas))

    print(f"num_iters: {num_iters}")

    # Create code with repeated pattern
    code = bytes(sum(opcode_block(pos) for pos in range(num_iters)))

    # Calculate utilization percentages for logging
    code_size_pct = (len(code) / MAX_CODE_SIZE) * 100
    gas_used = num_iters * iteration_gas_cost
    gas_pct = (gas_used / available_gas) * 100 if available_gas > 0 else None

    # Log the results to stdout instead of a file
    bytecode_values = f"{len(code)}/{MAX_CODE_SIZE}"
    gas_values = f"{gas_used}/{available_gas}"
    print(
        f"{'MANY JUMPS':<30} {bytecode_values:>15} ({code_size_pct:6.2f}%)  {gas_values:>20} ({gas_pct:6.2f}%)  {bytes_per_iter:>4}  {num_iters:>10}"
    )

    if len(code) > MAX_CODE_SIZE:
        raise ValueError(f"Code size {len(code)} exceeds maximum code size {MAX_CODE_SIZE}")

    code_address = pre.deploy_contract(code=code)

    tx = Transaction(
        to=code_address,
        gas_limit=gas_limit,
        gas_price=10,
        sender=pre.fund_eoa(),
        data=[],
        value=0,
    )

    blockchain_test(
        env=env,
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )


@pytest.mark.zkevm
@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "gas_limit",
    [36_000_000],
)
def test_many_jumps(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_limit: int,
):
    """
    Test executing a jump-intensive contract using multiple direct transactions.
    This spreads the execution across multiple transactions in a single block.
    """
    env = Environment(gas_limit=gas_limit)

    # Create jump-intensive contract code
    def opcode_block(pos):
        return Op.PUSH2(3 + 5 * pos) + Op.JUMP + Op.JUMPDEST

    gas_costs = fork.gas_costs()
    loop_cost = gas_costs.G_VERY_LOW + gas_costs.G_MID + gas_costs.G_JUMPDEST
    bytes_per_iter = 5  # PUSH2(3) + JUMP(1) + JUMPDEST(1)

    # Calculate number of jump iterations to include
    max_iters_by_size = MAX_CODE_SIZE // bytes_per_iter
    max_iters_by_gas = gas_limit // (loop_cost * 2)  # Conservative estimate
    num_iters = int(min(max_iters_by_size, max_iters_by_gas))

    print(f"num_iters in jump contract: {num_iters}")

    # Create and deploy the jump-intensive contract
    jump_code = bytes(sum(opcode_block(pos) for pos in range(num_iters)))
    jump_address = pre.deploy_contract(code=jump_code)

    # Determine how many transactions to include
    # We'll use a reasonable number that fits within a block
    num_txs = 591  # maximal for current setup

    # Create a list of transactions, all calling the same jump contract
    txs = [
        Transaction(
            to=jump_address,
            gas_limit=gas_limit // num_txs,  # Distribute gas across transactions
            gas_price=10**9,
            sender=pre.fund_eoa(),
        )
        for _ in range(num_txs)
    ]

    print(f"Jump contract size: {len(jump_code)} bytes")
    print(f"Creating {num_txs} transactions to the jump contract")

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=[Block(txs=txs)],
    )
