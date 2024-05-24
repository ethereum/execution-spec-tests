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

precompile_address = Address("0x09")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "call_instruction",
    [
        Op.CALL,
        Op.CALLCODE,
        Op.DELEGATECALL,
        Op.STATICCALL,
        # TODO(verkle): add AUTHCALL when/if supported in mainnet.
    ],
)
def test_calls_insufficient_gas(
    blockchain_test: BlockchainTestFiller, fork: str, call_instruction
):
    """
    Test *CALL charge warm cost on second call.
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
        TestAddress2: Account(code=Op.ADD(1, 2)),
    }

    if call_instruction == Op.CALL or call_instruction == Op.CALLCODE:
        call = call_instruction(1_000, TestAddress2, 0, 0, 0, 0, 32)
        tx_data = Initcode(deploy_code=call + call)
    if call_instruction == Op.DELEGATECALL or call_instruction == Op.STATICCALL:
        call = call_instruction(1_000, TestAddress2, 0, 0, 0, 32)
        tx_data = Initcode(deploy_code=call + call)
    # TODO(verkle): AUTHCALL

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=Address("0x00"),
        gas_limit=100000000,
        gas_price=10,
        value=0,
        data=tx_data,
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
