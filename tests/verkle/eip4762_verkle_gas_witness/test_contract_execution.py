"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.verkle.helpers import chunkify_code

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x04")


class Jump:
    """
    Represents a JUMP instruction to be inserted in the code.
    """

    def __init__(self, offset, pc):
        self.offset = offset
        self.pc = pc


class Jumpi(Jump):
    """
    Represents a JUMPI instruction to be inserted in the code.
    """

    def __init__(self, offset, pc, condition):
        Jump.__init__(self, offset, pc)
        self.condition = condition


def code_with_jumps(size, jumps: list[Jump | Jumpi] = []):
    """
    Returns the requested code with defined size, jumps, and PUSHNs.
    """
    code = Op.JUMPDEST * size
    result_code = bytes()
    last_offset = 0
    for j in jumps:
        result_code += bytes(code)[last_offset : j.offset]
        if isinstance(j, Jumpi):
            jump_code = bytes(Op.JUMPI(j.pc, 1 if j.condition else 0))
        elif isinstance(j, Jump):
            jump_code = bytes(Op.JUMP(j.pc))
        result_code += jump_code
        last_offset = j.offset + len(jump_code)

    result_code += bytes(code)[last_offset:]

    assert len(result_code) == size

    return result_code


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "bytecode, gas_limit, witness_code_chunk_ranges",
    [
        (  # only_code_in_account_header
            code_with_jumps(10),
            1_000_000,
            [[0, 0]],
        ),
        (  # chunks_both_in_and_out_account_header
            code_with_jumps(128 * 31 + 100),
            1_000_000,
            [[0, 131]],
        ),
        (  # touches_only_first_byte_code_chunk
            code_with_jumps(128 * 31 + 1),
            1_000_000,
            [[0, 128]],
        ),
        (  # touches_only_last_byte_code_chunk
            code_with_jumps(128 * 31 + 100, [Jump(10, 128 * 31 + 9)]),
            1_000_000,
            [[0, 0], [131, 131]],
        ),
        (  # pushn_with_data_in_chunk_that_cant_be_paid
            Op.PUSH0 * 30 + Op.PUSH1(42),
            21000,
            [[0, 0]],
        ),
        # (  # jump_to_jumpdest_in_pushn_data
        #     Op.PUSH0 * 10
        #     + Op.JUMP(10 + 3 + 1 + 1000 + 1)  # 3+1=PUSH2+JUMP
        #     + Op.PUSH0 * 1000
        #     + Op.PUSH1(0x5B)
        #     + Op.PUSH0 * 100,  # Add more code, but can't be executed due to the invalid jump
        #     1_000_000,
        #     [[0, 0], [32, 32]],
        # ),
        # (  # jumpi_to_jumpdest_in_pushn_data
        #     bytes(
        #         Op.PUSH0 * 10
        #         + Op.JUMPI(10 + 5 + 1 + 1000 + 1, 1)  # 5+1=PUSH1+PUSH2+JUMPI
        #         + Op.PUSH0 * 1000
        #         + Op.PUSH1(0x5B)
        #         + Op.PUSH0 * 100
        #     ),
        #     1_000_000,
        #     [[0, 0], [32, 32]],
        # ),
        # (  # jump_to_non_jumpdest_destiny
        #     bytes(
        #         Op.PUSH0 * 10 + Op.JUMP(10 + 3 + 1 + 1000) + Op.PUSH0 * 1000 + Op.ORIGIN
        #     ),  # 3+1=PUSH2+JUMP
        #     1_000_000,
        #     [[0, 0], [32, 32]],
        # ),
        # (  # jumpi_to_non_jumpdest_destiny
        #     bytes(
        #         Op.PUSH0 * 10 + Op.JUMPI(10 + 5 + 1 + 1000, 1) + Op.PUSH0 * 1000 + Op.ORIGIN
        #     ),  # 5+1=PUSH1+PUSH2+JUMPI
        #     1_000_000,
        #     [[0, 0], [32, 32]],
        # ),
        (  # linear_execution_stopping_at_first_byte_of_next_chunk
            code_with_jumps(128 * 31 + 1),
            1_000_000,
            [[0, 128]],
        ),
        (  # false_jumpi
            code_with_jumps(150 * 31 + 10, [Jumpi(50, 1000, False)]),
            1_000_000,
            [[0, 150]],
        ),
        (  # insufficient_gas_for_jump_instruction
            code_with_jumps(150 * 31, [Jump(10, 1000)]),
            21000 + 200 + 10 + 3,
            [[0, 0]],
        ),
        (  # insufficient_gas_for_jumpi_instruction
            code_with_jumps(150 * 31, [Jumpi(10, 1000, True)]),
            21000 + 200 + 10 + 3 + 3,
            [[0, 0]],
        ),
        (  # sufficient_gas_for_jump_instruction_but_not_for_code_chunk
            code_with_jumps(150 * 31, [Jump(10, 1000)]),
            21000 + 200 + 10 + 3 + 8,
            [[0, 0]],
        ),
        (  # sufficient_gas_for_jumpi_instruction_but_not_for_code_chunk
            code_with_jumps(150 * 31, [Jumpi(10, 1000, True)]),
            21000 + 200 + 10 + 3 + 3 + 10,
            [[0, 0]],
        ),
        (  # jump_outside_code_size
            code_with_jumps(150 * 31, [Jump(10, 150 * 31 + 42)]),
            1_000_000,
            [[0, 0]],
        ),
        (  # jumpi_outside_code_size
            code_with_jumps(150 * 31, [Jumpi(50, 150 * 31 + 42, True)]),
            1_000_000,
            [[0, 0]],
        ),
        (  # push20 with data split in two chunks
            Op.PUSH0 * (31 - (1 + 10)) + Op.PUSH20(0xAA),
            1_000_000,
            [[0, 1]],
        ),
        (  # push32 spanning three chunks
            Op.PUSH0 * (31 - 1) + Op.PUSH32(0xAA),
            1_000_000,
            [[0, 2]],
        ),
        (  # pushn with expected data past code size
            Op.PUSH0 * (31 - 5) + Op.PUSH20,
            1_000_000,
            [[0, 0]],
        ),
    ],
    ids=[
        "only_code_in_account_header",
        "chunks_both_in_and_out_account_header",
        "touches_only_first_byte_code_chunk",
        "touches_only_last_byte_code_chunk",
        "pushn_with_data_in_chunk_that_cant_be_paid",
        # "jump_to_jumpdest_in_pushn_data",
        # "jumpi_to_jumpdest_in_pushn_data",
        # "jump_to_non_jumpdest_destiny",
        # "jumpi_to_non_jumpdest_destiny",
        "linear_execution_stopping_at_first_byte_of_next_chunk",
        "false_jumpi",
        "insufficient_gas_for_jump_instruction",
        "insufficient_gas_for_jumpi_instruction",
        "sufficient_gas_for_jump_instruction_but_not_for_code_chunk",
        "sufficient_gas_for_jumpi_instruction_but_not_for_code_chunk",
        "jump_outside_code_size",
        "jumpi_outside_code_size",
        "push20_with_data_split_in_two_chunks",
        "push32_spanning_three_chunks",
        "pushn_with_expected_data_past_code_size",
    ],
)
def test_contract_execution_foo(
    blockchain_test: BlockchainTestFiller,
    bytecode: bytes,
    gas_limit: int,
    witness_code_chunk_ranges,
):
    """
    Test that contract execution generates expected witness.
    """
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(code=bytecode),
    }
    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=gas_limit,
        gas_price=10,
    )

    code_chunks = chunkify_code(bytecode)
    assert len(code_chunks) > 0

    witness_check = WitnessCheck()
    for address in [TestAddress, TestAddress2, env.fee_recipient]:
        witness_check.add_account_full(
            address=address,
            account=pre.get(address),
        )
    for chunk_ranges in witness_code_chunk_ranges:
        for chunk_number in range(chunk_ranges[0], chunk_ranges[1] + 1):
            witness_check.add_code_chunk(TestAddress2, chunk_number, code_chunks[chunk_number])

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
    )
