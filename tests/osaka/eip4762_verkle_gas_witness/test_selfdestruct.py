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

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x09")
ExampleAddress = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0c")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("target", [ExampleAddress, precompile_address])
@pytest.mark.parametrize("contract_balance", [0, 1])
def test_balance(blockchain_test: BlockchainTestFiller, fork: str, target, contract_balance):
    """
    Test SELFDESTRUCT witness.
    """
    exp_witness = None  # TODO(verkle)
    _selfdestruct(blockchain_test, fork, target, exp_witness, contract_balance)


def _selfdestruct(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    target,
    exp_witness,
    contract_balance,
    gas_limit=1_000_000,
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(code=Op.SELFDESTRUCT(target), value=contract_balance),
        target: Account(balance=0xFF),
    }

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=gas_limit,
        gas_price=10,
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
