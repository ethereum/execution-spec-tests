"""
abstract: Tests zkEVMs worst-case compute scenarios.
    Tests zkEVMs worst-case compute scenarios.

Tests running worst-case compute opcodes and precompile scenarios for zkEVMs.
"""

import math

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (Alloc, Block, BlockchainTestFiller,
                                 Environment, Transaction)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"

MAX_CODE_SIZE = 24 * 1024
KECCAK_RATE = 136


@pytest.mark.zkevm
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
    intrinsic_gasc_calculator = fork.transaction_intrinsic_cost_calculator()
    available_gas = gas_limit - intrinsic_gasc_calculator()

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
        available_gas_after_expansion = max(0, available_gas - mem_exp_gas_calculator(new_bytes=i))
        num_keccak_calls = available_gas_after_expansion // iteration_gas_cost
        num_keccak_permutations = num_keccak_calls * math.ceil(i / KECCAK_RATE)

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
    max_iters_loop = (MAX_CODE_SIZE - 3) // (4 + 1 + (optimal_input_length.bit_length() + 7) // 8)
    code = (
        Op.JUMPDEST
        + sum([Op.SHA3(0, optimal_input_length) + Op.POP] * max_iters_loop)
        + Op.PUSH0
        + Op.JUMP
    )
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
