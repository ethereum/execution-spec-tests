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
    compute_create2_address,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x09")
ExampleAddress = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0c")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "target",
    [
        ExampleAddress,
        precompile_address,
    ],
)
def test_balance(blockchain_test: BlockchainTestFiller, fork: str, target):
    """
    Test BALANCE witness.
    """
    exp_witness = None  # TODO(verkle)
    _balance(blockchain_test, fork, target, exp_witness)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "target",
    [
        ExampleAddress,
        precompile_address,
    ],
)
def test_balance_insufficient_gas(blockchain_test: BlockchainTestFiller, fork: str, target):
    """
    Test BALANCE with insufficient gas.
    """
    exp_witness = None  # TODO(verkle)
    _balance(blockchain_test, fork, target, exp_witness, 1_042)


def _balance(
    blockchain_test: BlockchainTestFiller, fork: str, target, exp_witness, gas_limit=1_000_000
):
    """
    Test BALANCE witness.
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
        TestAddress2: Account(code=Op.BALANCE(target)),
        target: Account(balance=0xF1),
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
