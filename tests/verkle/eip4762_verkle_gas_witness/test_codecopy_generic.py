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
    Bytecode,
    Environment,
    Initcode,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.verkle.helpers import chunkify_code

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

code_size = 200 * 31 + 60


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "instruction",
    [
        Op.CODECOPY,
        Op.EXTCODECOPY,
    ],
)
@pytest.mark.parametrize(
    "offset, size",
    [
        (0, 0),
        (0, 127 * 31),
        (0, 128 * 31),
        (0, code_size - 5),
        (0, code_size),
        (code_size - 1, 1),
        (code_size, 1),
        (code_size - 1, 1 + 1),
        (code_size - 1, 1 + 31),
    ],
    ids=[
        "zero_bytes",
        "chunks_only_account_header",
        "all_chunks_account_header",
        "contract_size_after_header_but_incomplete",
        "contract_size",
        "last_byte",
        "all_out_of_bounds",
        "partial_out_of_bounds_in_same_last_code_chunk",
        "partial_out_of_bounds_touching_further_non_existent_code_chunk",
    ],
)
def test_generic_codecopy(blockchain_test: BlockchainTestFiller, instruction, offset, size):
    """
    Test *CODECOPY witness.
    """
    start = offset if offset < size else size
    end = offset + size if offset + size < code_size else code_size
    witness_code_chunks = range(0, 0)
    if start < size and start != end:
        start_chunk = start // 31
        end_chunk = (end - 1) // 31
        witness_code_chunks = range(start_chunk, end_chunk + 1)

    _generic_codecopy(
        blockchain_test,
        instruction,
        offset,
        size,
        witness_code_chunks,
        witness_target_basic_data=True,
    )


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "instruction",
    [
        Op.CODECOPY,
        Op.EXTCODECOPY,
    ],
)
def test_generic_codecopy_warm(blockchain_test: BlockchainTestFiller, instruction):
    """
    Test *CODECOPY with WARM access.
    """
    witness_code_chunks = range(0, (code_size - 5) // 31 + 1)
    _generic_codecopy(
        blockchain_test,
        instruction,
        0,
        code_size - 5,
        witness_code_chunks,
        witness_target_basic_data=True,
        warm=True,
    )


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.skip("Pending to fill TBD gas limit")
@pytest.mark.parametrize(
    "gas_limit, witness_code_chunks",
    [
        ("TBD", range(0, 0)),
        ("TBD", range(0, 150)),
    ],
    ids=[
        "not_enough_for_even_first_chunk",
        "partial_code_range",
    ],
)
# TODO(verkle): consider reusing code from test_generic_codecopy.py.
def test_codecopy_insufficient_gas(
    blockchain_test: BlockchainTestFiller, gas_limit, witness_code_chunks
):
    """
    Test CODECOPY with insufficient gas.
    """
    _generic_codecopy(
        blockchain_test,
        Op.CODECOPY,
        0,
        code_size,
        witness_code_chunks,
        witness_target_basic_data=True,
        gas_limit=gas_limit,
    )


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.skip("Pending to fill TBD gas limit")
@pytest.mark.parametrize(
    "gas_limit, witness_target_basic_data, witness_code_chunks",
    [
        ("TBD", False, range(0, 0)),
        ("TBD", True, range(0, 0)),
        ("TBD", True, range(0, 150)),
    ],
    ids=[
        "insufficient_for_target_basic_data",
        "not_enough_for_even_first_chunk",
        "partial_code_range",
    ],
)
# TODO(verkle): consider reusing code from test_generic_codecopy.py.
def test_extcodecopy_insufficient_gas(
    blockchain_test: BlockchainTestFiller,
    gas_limit,
    witness_target_basic_data,
    witness_code_chunks,
):
    """
    Test EXTCODECOPY with insufficient gas.
    """
    _generic_codecopy(
        blockchain_test,
        Op.CODECOPY,
        0,
        code_size,
        witness_code_chunks,
        witness_target_basic_data=witness_target_basic_data,
        gas_limit=gas_limit,
    )


def _generic_codecopy(
    blockchain_test: BlockchainTestFiller,
    instr: Op,
    offset: int,
    size: int,
    witness_code_chunks,
    witness_target_basic_data,
    warm=False,
    gas_limit=1_000_000,
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    repeat = 2 if warm else 1
    codecopy_code = Op.CODECOPY(0, offset, size) * repeat
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(code=codecopy_code + Op.PUSH0 * (code_size - len(codecopy_code))),
    }

    to: Address | None = TestAddress2
    data = Bytecode()
    if instr == Op.EXTCODECOPY:
        to = None
        extcodecopy_code = Op.EXTCODECOPY(TestAddress2, 0, offset, size) * repeat
        data = Initcode(deploy_code=extcodecopy_code)

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=to,
        gas_limit=gas_limit,
        gas_price=10,
        data=data,
    )

    tx_target_addr = (
        TestAddress2
        if instr == Op.CODECOPY
        else compute_create_address(address=TestAddress, nonce=0)
    )
    code_chunks = chunkify_code(pre[TestAddress2].code)

    # TODO: fix tests
    witness_check = WitnessCheck()
    for address in [TestAddress, tx_target_addr, env.fee_recipient]:
        witness_check.add_account_full(
            address=address,
            account=(pre[address] if address == TestAddress else None),
        )
    if witness_target_basic_data:
        witness_check.add_account_basic_data(TestAddress2, pre[TestAddress2])

    for chunk_num in witness_code_chunks:
        witness_check.add_code_chunk(TestAddress2, chunk_num, code_chunks[chunk_num])

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        blocks=blocks,
        post={},
    )
