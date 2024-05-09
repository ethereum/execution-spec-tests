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
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..temp_verkle_helpers import vkt_add_all_headers_present, vkt_chunkify, vkt_key_code_chunk

precompile_address = Address("0x09")


@pytest.mark.valid_from("Osaka")
@pytest.mark.parametrize(
    "bytecode",
    # Note: This is only containing 1 out of ~12 cases that we should create,
    # for now should be enough to serve as a sample for adjusting the testing library.
    [
        Op.ADD(Op.ADD(1, 2), 3) + Op.STOP * 1024,
    ],
    ids=["header_single_chunk"],
)
def test_transfer(state_test, fork, bytecode):
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
    code_chunks = vkt_chunkify(bytecode)
    assert len(code_chunks) > 1

    witness_keys = {}
    vkt_add_all_headers_present(witness_keys, TestAddress)
    vkt_add_all_headers_present(witness_keys, TestAddress2)
    witness_keys[vkt_key_code_chunk(TestAddress2, 0)] = code_chunks[0]

    state_test(
        env=env,
        pre=pre,
        tx=tx,
        witness_keys=witness_keys,
    )
