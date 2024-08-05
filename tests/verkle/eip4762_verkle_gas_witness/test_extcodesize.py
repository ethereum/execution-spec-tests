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
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..temp_verkle_helpers import Witness

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x04")
system_contract_address = Address("0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02")
EmptyAddress = Address("0xFFFFFFf6D732807Ef1319fB7B8bB8522d0BeacFF")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "target, bytecode",
    [
        (EmptyAddress, ""),
        (TestAddress2, Op.ADD(1, 2) * 10),
        (precompile_address, ""),
        (system_contract_address, ""),
    ],
    ids=[
        "empty_code",
        "non_empty_code",
        "precompile",
        "system_contract",
    ],
)
def test_extcodesize(blockchain_test: BlockchainTestFiller, fork: str, target, bytecode):
    """
    Test EXTCODESIZE witness.
    """
    witness = Witness()
    if target != precompile_address and target != system_contract_address:
        account = Account(code=bytecode)
        witness.add_account_basic_data(target, account)

    _extcodesize(blockchain_test, fork, target, bytecode, witness)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
def test_extcodesize_insufficient_gas(blockchain_test: BlockchainTestFiller, fork: str):
    """
    Test EXTCODESIZE with insufficient gas.
    """
    _extcodesize(
        blockchain_test,
        fork,
        TestAddress2,
        Op.PUSH0 * 1000,
        Witness(),
        gas_limit=1_042,
        fails=True,
    )


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
def test_extcodesize_warm(blockchain_test: BlockchainTestFiller, fork: str):
    """
    Test EXTCODESIZE with WARM cost.
    """
    bytecode = Op.ADD(1, 2) * 10
    account = Account(code=bytecode)
    witness = Witness()
    witness.add_account_basic_data(TestAddress2, account)
    _extcodesize(blockchain_test, fork, TestAddress2, bytecode, witness, warm=True)


def _extcodesize(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    target: Address,
    bytecode: bytes,
    extra_witness: Witness,
    gas_limit=1_000_000,
    warm=False,
    fails=False,
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
    }
    if len(bytecode) > 0:
        pre[TestAddress2] = Account(code=bytecode)

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=Address("0x00"),
        gas_limit=gas_limit,
        gas_price=10,
        data=Initcode(
            deploy_code=Op.EXTCODESIZE(target) * (2 if warm else 1) + Op.PUSH0 + Op.SSTORE
        ).bytecode,
    )
    blocks = [Block(txs=[tx])]

    post = {}
    if not fails:
        contract_address = compute_create_address(TestAddress, tx.nonce)
        post[contract_address] = Account(storage={0: len(bytecode)})

    witness = Witness()
    witness.add_account_full(env.fee_recipient, None)
    witness.add_account_full(TestAddress, pre[TestAddress])
    witness.merge(extra_witness)

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness=witness,
    )
