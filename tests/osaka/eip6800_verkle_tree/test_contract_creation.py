"""
abstract: Tests [EIP-6800: Ethereum state using a unified verkle tree]
(https://eips.ethereum.org/EIPS/eip-6800)
    Tests for [EIP-6800: Ethereum state using a unified verkle tree]
    (https://eips.ethereum.org/EIPS/eip-6800).
"""

import pytest
from ethereum.crypto.hash import keccak256

from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    Initcode,
    TestAddress,
    Transaction,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..temp_verkle_helpers import (
    AccountHeaderEntry,
    vkt_chunkify,
    vkt_key_code_chunk,
    vkt_key_header,
)


@pytest.mark.valid_from("Osaka")
@pytest.mark.parametrize(
    "bytecode",
    [
        "",
        Op.STOP * 1024,
    ],
    ids=["empty", "non_empty"],
)
@pytest.mark.parametrize(
    "value",
    [0, 1],
    ids=["zero", "non_zero"],
)
def test_contract_creation(state_test, fork, value, bytecode):
    """
    Test that contract creation works as expected.
    """
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
        verkle_conversion_ended=True,
    )
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=Address(""),
        gas_limit=100000000,
        gas_price=10,
        value=value,
        data=Initcode(deploy_code=bytecode),
    )

    contract_address = compute_create_address(TestAddress, tx.nonce)
    code_chunks = vkt_chunkify(bytecode)

    post = {}
    post[vkt_key_header(contract_address, AccountHeaderEntry.VERSION)] = 0
    post[vkt_key_header(contract_address, AccountHeaderEntry.BALANCE)] = value
    post[vkt_key_header(contract_address, AccountHeaderEntry.CODE_HASH)] = keccak256(bytecode)
    post[vkt_key_header(contract_address, AccountHeaderEntry.CODE_SIZE)] = len(bytecode)
    for i, chunk in enumerate(code_chunks):
        post[vkt_key_code_chunk(contract_address, i)] = chunk

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )
