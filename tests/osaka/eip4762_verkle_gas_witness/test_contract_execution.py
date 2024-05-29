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
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..temp_verkle_helpers import vkt_add_all_headers_present, vkt_chunkify, vkt_key_code_chunk

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x09")


def code_with_jumps(size, jumps: list[tuple[int, int]] = [], pushns: list[int] = []):
    """
    Returns the requested code with defined size, jumps and PUSHNs

    Args:
        size: The total size of the code.
        jumps: A list of tuples of the form (offset, pc), where to insert JUMP instructions.
        pushns: A list of tuples of the form (pc), where to insert PUSHN instructions.
    """
    code = Op.PUSH0 * size
    for offset, pc in jumps:
        code[offset] = Op.JUMP(pc)
        code[pc] = Op.JUMPDEST

    return code


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "bytecode, gas_limit",
    [
        (code_with_jumps(10), 1_000_000),
        (code_with_jumps(128 * 31 + 100), 1_000_000),
        (code_with_jumps(128 * 31 + 1), 1_000_000),
        (code_with_jumps(128 * 31 + 100, [(10, 128 * 31 + 100)]), 1_000_000),
        (Op.PUSH0 * 30 + Op.PUSH1(42), 42),
        (Op.PUSH0 * 10 + Op.JUMP(10 + 2 + 1 + 1000) + Op.PUSH0 * 1000 + Op.PUSH1(0x5B), 1_000_000),
        (code_with_jumps(128 * 31), 1_000_000),
    ],
    ids=[
        "only_code_in_account_header",
        "chunks_both_in_and_out_account_header",
        "toches_only_first_byte_code_chunk",
        "toches_only_last_byte_code_chunk",
        "pushn_with_data_in_chunk_that_cant_be_paid",
        "jump_to_jumpdest_in_pushn_data",
        "linear_execution_stopping_at_first_byte_of_next_chunk",
    ],
)
def test_transfer(blockchain_test: BlockchainTestFiller, fork: str, bytecode):
    """
    Test that value transfer generates a correct witness.
    """
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    sender_balance = 1000000000000000000000
    pre = {
        TestAddress: Account(balance=sender_balance),
        TestAddress2: Account(code=bytecode),
    }
    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=100000000,
        gas_price=10,
    )
    blocks = [Block(txs=[tx])]

    code_chunks = vkt_chunkify(bytecode)
    assert len(code_chunks) > 1

    witness_keys = {
        vkt_key_code_chunk(TestAddress2, 0): code_chunks[0],
    }
    vkt_add_all_headers_present(witness_keys, TestAddress)
    vkt_add_all_headers_present(witness_keys, TestAddress2)

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness_keys=witness_keys,
    )
