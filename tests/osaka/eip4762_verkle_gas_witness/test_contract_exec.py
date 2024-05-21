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


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "bytecode",
    # Note: This is only containing 1 out of ~12 cases that we should create,
    # for now should be enough to serve as a sample for adjusting the testing library.
    [
        Op.ADD(Op.ADD(1, 2), 3) + Op.STOP * 1024,
    ],
    ids=["header_single_chunk"],
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
        verkle_conversion_ended=True,
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
