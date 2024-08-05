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

from ..temp_verkle_helpers import Witness

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x04")
system_contract_address = Address("0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02")
example_address = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0c")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "target",
    [
        example_address,
        precompile_address,
        system_contract_address,
    ],
)
@pytest.mark.parametrize("warm", [True, False])
def test_balance(blockchain_test: BlockchainTestFiller, fork: str, target, warm):
    """
    Test BALANCE witness with/without WARM access.
    """
    _balance(blockchain_test, fork, target, [target], warm=warm)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize("target", [example_address, precompile_address])
def test_balance_insufficient_gas(blockchain_test: BlockchainTestFiller, fork: str, target):
    """
    Test BALANCE with insufficient gas.
    """
    _balance(blockchain_test, fork, target, [], 1_042)


def _balance(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    target: Address,
    exp_addr_basic_data: list[Address],
    gas_limit=1_000_000,
    warm=False,
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
        TestAddress2: Account(code=Op.BALANCE(target) * (2 if warm else 1) + Op.PUSH0 + Op.SSTORE),
        target: Account(balance=0xF1),
        precompile_address: Account(balance=0xF2),
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

    post = {
        TestAddress2: Account(code=pre[TestAddress2].code, storage={0: pre[target].balance}),
    }

    witness = Witness()
    witness.add_account_full(env.fee_recipient, None)
    witness.add_account_full(TestAddress, pre[TestAddress])
    witness.add_account_full(TestAddress2, pre[TestAddress2])
    for addr in exp_addr_basic_data:
        witness.add_account_basic_data(addr, pre[addr])

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
        witness=witness,
    )
