"""
abstract: Tests zkEVMs worst-case compute scenarios.
    Tests zkEVMs worst-case compute scenarios.

Tests running worst-case compute opcodes and precompile scenarios for zkEVMs.
"""

import math

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (Address, Alloc, Block, BlockchainTestFiller,
                                 Bytecode, Environment, Transaction)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"

MAX_CODE_SIZE = 24 * 1024
KECCAK_RATE = 136


@pytest.mark.valid_from("Cancun")
def test_worst_keccak(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
):
    """Test running a block with as many KECCAK256 permutations as possible."""
    env = Environment()

    # Intrinsic gas cost is paid once.
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    available_gas = env.gas_limit - intrinsic_gas_calculator()

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
        gas_limit=env.gas_limit,
        sender=pre.fund_eoa(),
    )

    blockchain_test(
        env=env,
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "address,static_cost,per_word_dynamic_cost,bytes_per_unit_of_work",
    [
        pytest.param(0x02, 60, 12, 64, id="SHA2-256"),
        pytest.param(0x03, 600, 120, 64, id="RIPEMD-160"),
        pytest.param(0x04, 15, 3, 1, id="IDENTITY"),
    ],
)
def test_worst_precompile_only_data_input(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    address: Address,
    static_cost: int,
    per_word_dynamic_cost: int,
    bytes_per_unit_of_work: int,
):
    """Test running a block with as many precompile calls which have a single `data` input."""
    env = Environment()

    # Intrinsic gas cost is paid once.
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    available_gas = env.gas_limit - intrinsic_gas_calculator()

    gsc = fork.gas_costs()
    mem_exp_gas_calculator = fork.memory_expansion_gas_calculator()

    # Discover the optimal input size to maximize precompile work, not precompile calls.
    max_work = 0
    optimal_input_length = 0
    for input_length in range(1, 1_000_000, 32):
        parameters_gas = (
            gsc.G_BASE  # PUSH0 = arg offset
            + gsc.G_BASE  # PUSH0 = arg size
            + gsc.G_BASE  # PUSH0 = arg size
            + gsc.G_VERY_LOW  # PUSH0 = arg offset
            + gsc.G_VERY_LOW  # PUSHN = address
            + gsc.G_BASE  # GAS
        )
        iteration_gas_cost = (
            parameters_gas
            + +static_cost  # Precompile static cost
            + math.ceil(input_length / 32) * per_word_dynamic_cost  # Precompile dynamic cost
            + gsc.G_BASE  # POP
        )
        # From the available gas, we substract the mem expansion costs considering we know the
        # current input size length.
        available_gas_after_expansion = max(
            0, available_gas - mem_exp_gas_calculator(new_bytes=input_length)
        )
        # Calculate how many calls we can do.
        num_calls = available_gas_after_expansion // iteration_gas_cost
        total_work = num_calls * math.ceil(input_length / bytes_per_unit_of_work)

        # If we found an input size that is better (reg permutations/gas), then save it.
        if total_work > max_work:
            max_work = total_work
            optimal_input_length = input_length

    calldata = Op.CODECOPY(0, 0, optimal_input_length)
    attack_block = Op.POP(Op.STATICCALL(Op.GAS, address, 0, optimal_input_length, 0, 0))
    code = code_loop_precompile_call(calldata, attack_block)

    code_address = pre.deploy_contract(code=code)

    tx = Transaction(
        to=code_address,
        gas_limit=env.gas_limit,
        sender=pre.fund_eoa(),
    )

    blockchain_test(
        env=env,
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )


@pytest.mark.valid_from("Cancun")
def test_worst_modexp(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
):
    """Test running a block with as many MODEXP calls as possible."""
    env = Environment()

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
    code = code_loop_precompile_call(calldata, attack_block)

    code_address = pre.deploy_contract(code=code)

    tx = Transaction(
        to=code_address,
        gas_limit=env.gas_limit,
        sender=pre.fund_eoa(),
    )

    blockchain_test(
        env=env,
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "gas_limit",
    [
        Environment().gas_limit,
    ],
)
@pytest.mark.parametrize(
    "precompile_address,precompile_gas_cost,input,length",
    [
        pytest.param(
            0x01,
            3_000,
            [
                0x38D18ACB67D25C8BB9942764B62F18E17054F66A817BD4295423ADF9ED98873E,
                27,
                0x38D18ACB67D25C8BB9942764B62F18E17054F66A817BD4295423ADF9ED98873E,
                0x789D1DD423D25F0772D2748D60F7E4B81BB14D086EBA8E8E8EFB6DCFF8A4AE02,
            ],
            32 * 4,
            id="ecrecover",
        ),
        pytest.param(
            0x06,
            150,
            [
                0x18B18ACFB4C2C30276DB5411368E7185B311DD124691610C5D3B74034E093DC9,
                0x063C909C4720840CB5134CB9F59FA749755796819658D32EFC0D288198F37266,
                0x07C2B7F58A84BD6145F00C9C2BC0BB1A187F20FF2C92963A88019E7C6A014EED,
                0x06614E20C147E940F2D70DA3F74C9A17DF361706A4485C742BD6788478FA17D7,
            ],
            32 * 4,
            id="bn128add",
        ),
        pytest.param(
            0x07,
            6_000,
            [
                0x1A87B0584CE92F4593D161480614F2989035225609F08058CCFA3D0F940FEBE3,
                0x1A2F3C951F6DADCC7EE9007DFF81504B0FCD6D7CF59996EFDC33D92BF7F9F8F6,
                0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            ],
            32 * 4,
            id="bn128mul",
        ),
        pytest.param(
            0x08,
            45_000 + 2 * 34_000,
            [
                0x1C76476F4DEF4BB94541D57EBBA1193381FFA7AA76ADA664DD31C16024C43F59,
                0x3034DD2920F673E204FEE2811C678745FC819B55D3E9D294E45C9B03A76AEF41,
                0x209DD15EBFF5D46C4BD888E51A93CF99A7329636C63514396B4A452003A35BF7,
                0x04BF11CA01483BFA8B34B43561848D28905960114C8AC04049AF4B6315A41678,
                0x2BB8324AF6CFC93537A2AD1A445CFD0CA2A71ACD7AC41FADBF933C2A51BE344D,
                0x120A2A4CF30C1BF9845F20C6FE39E07EA2CCE61F0C9BB048165FE5E4DE877550,
                0x111E129F1CF1097710D41C4AC70FCDFA5BA2023C6FF1CBEAC322DE49D1B6DF7C,
                0x103188585E2364128FE25C70558F1560F4F9350BAF3959E603CC91486E110936,
                0x198E9393920D483A7260BFB731FB5D25F1AA493335A9E71297E485B7AEF312C2,
                0x1800DEEF121F1E76426A00665E5C4479674322D4F75EDADD46DEBD5CD992F6ED,
                0x090689D0585FF075EC9E99AD690C3395BC4B313370B38EF355ACDADCD122975B,
                0x12C85EA5DB8C6DEB4AAB71808DCB408FE3D1E7690C43D37B4CE6CC0166FA7DAA,
            ],
            32 * 12,
            id="bn128pairing",
        ),
        pytest.param(
            0x09,
            0xFFFF,
            [
                0x0000FFFF48C9BDF267E6096A3BA7CA8485AE67BB2BF894FE72F36E3CF1361D5F,
                0x3AF54FA5D182E6AD7F520E511F6C3E2B8C68059B6BBD41FBABD9831F79217E13,
                0x19CDE05B61626300000000000000000000000000000000000000000000000000,
                0x0000000000000000000000000000000000000000000000000000000000000000,
                0x0000000000000000000000000000000000000000000000000000000000000000,
                0x0000000000000000000000000000000000000000000000000000000000000000,
                0x0000000000000000000000000000000000000000000000000000000000000000,
                0x0000000000000000000000000000000000000000000000000000000000000000,
                0x0000000003000000000000000000000000000001000000000000000000000000,
            ],
            213,
            id="blake2f",
        ),
        pytest.param(
            0x0A,
            50_000,
            [
                0x01E798154708FE7789429634053CBF9F99B619F9F084048927333FCE637F549B,
                0x564C0A11A0F704F4FC3E8ACFE0F8245F0AD1347B378FBF96E206DA11A5D36306,
                0x24D25032E67A7E6A4910DF5834B8FE70E6BCFEEAC0352434196BDF4B2485D5A1,
                0x8F59A8D2A1A625A17F3FEA0FE5EB8C896DB3764F3185481BC22F91B4AAFFCCA2,
                0x5F26936857BC3A7C2539EA8EC3A952B7873033E038326E87ED3E1276FD140253,
                0xFA08E9FC25FB2D9A98527FC22A2C9612FBEAFDAD446CBC7BCDBDCD780AF2C16A,
            ],
            192,
            id="point_evaluation",
        ),
    ],
)
def test_worst_precompile_fixed_cost(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_limit: int,
    precompile_address: Address,
    precompile_gas_cost: Address,
    input: list[int],
    length: int,
):
    """Test running a block filled with a precompile with fixed cost."""
    env = Environment(gas_limit=gas_limit)

    # Calldata
    calldata = sum([Op.MSTORE(i * 32, input) for i, input in enumerate(input)])

    attack_block = Op.POP(Op.STATICCALL(precompile_gas_cost, precompile_address, 0, length, 0, 0))
    code = code_loop_precompile_call(calldata, attack_block)
    code_address = pre.deploy_contract(code=bytes(code))

    tx = Transaction(
        to=code_address,
        gas_limit=env.gas_limit,
        sender=pre.fund_eoa(),
    )

    blockchain_test(
        env=env,
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )


def code_loop_precompile_call(calldata: Bytecode, attack_block: Bytecode):
    """Create a code loop that calls a precompile with the given calldata."""
    # The attack contract is: CALLDATA_PREP + #JUMPDEST + [attack_block]* + JUMP(#)
    jumpdest = Op.JUMPDEST
    jump_back = Op.JUMP(len(calldata))
    max_iters_loop = (MAX_CODE_SIZE - len(calldata) - len(jumpdest) - len(jump_back)) // len(
        attack_block
    )
    code = calldata + jumpdest + sum([attack_block] * max_iters_loop) + jump_back
    if len(code) > MAX_CODE_SIZE:
        # Must never happen, but keep it as a sanity check.
        raise ValueError(f"Code size {len(code)} exceeds maximum code size {MAX_CODE_SIZE}")

    return code
