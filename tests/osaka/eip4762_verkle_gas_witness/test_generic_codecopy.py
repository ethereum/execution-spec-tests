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
    Initcode,
    TestAddress,
    TestAddress2,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

code_size = 128 * 31 + 60


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
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
        "within_chunks_account_header",
        "all_chunks_account_header",
        "contract_size_after_header_but_incomplete",
        "contract_size",
        "last_byte",
        "all_out_of_bounds",
        "partial_out_of_bounds_in_same_last_code_chunk",
        "partial_out_of_bounds_touching_further_non_existent_code_chunk",
    ],
)
def test_generic_codecopy(
    blockchain_test: BlockchainTestFiller, fork: str, instruction, offset, size
):
    """
    Test *CODECOPY witness.
    """
    _generic_codecopy(blockchain_test, fork, instruction, offset, size, 1)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "instruction",
    [
        Op.CODECOPY,
        Op.EXTCODECOPY,
    ],
)
def test_generic_codecopy_warm(
    blockchain_test: BlockchainTestFiller, fork: str, instruction, offset, size
):
    """
    Test *CODECOPY with WARM access.
    """
    _generic_codecopy(blockchain_test, fork, instruction, 0, code_size - 5, 2)


def _generic_codecopy(
    blockchain_test: BlockchainTestFiller, fork: str, instruction, offset, size, rep
):
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
        TestAddress2: Account(
            code=Op.CODECOPY(0, offset, size) * rep + Op.ORIGIN * (code_size - 7 * rep)
        ),
    }

    to: Address | None = TestAddress2
    data = None
    if instruction == Op.EXTCODECOPY:
        to = None
        data = Initcode(deploy_code=Op.EXTCODECOPY(TestAddress2, 0, offset, size)).bytecode

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=to,
        gas_limit=1_000_000,
        gas_price=10,
        data=data,
    )
    blocks = [Block(txs=[tx])]

    # TODO(verkle): define witness assertion
    witness_keys = ""

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness_keys=witness_keys,
    )
