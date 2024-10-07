"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_forks import Verkle
from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_forks import Fork
from ethereum_test_types.verkle.helpers import chunkify_code

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x04")
system_contract_address = Address("0xfffffffffffffffffffffffffffffffffffffffe")
example_address = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0c")


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
def test_balance(blockchain_test: BlockchainTestFiller, fork: Fork, target, warm):
    """
    Test BALANCE witness with/without WARM access.
    """
    _balance(blockchain_test, fork, target, True, warm=warm)


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "target",
    [
        example_address,
        precompile_address,
    ],
)
@pytest.mark.parametrize(
    " gas, exp_target_basic_data",
    [
        (21_203 + 2099, False),
        (21_203 + 2100, True),
    ],
)
def test_balance_insufficient_gas(
    blockchain_test: BlockchainTestFiller, fork: Fork, target, gas, exp_target_basic_data
):
    """
    Test BALANCE with insufficient gas.
    """
    _balance(blockchain_test, fork, target, exp_target_basic_data, gas, fails=True)


def _balance(
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    target: Address,
    exp_target_basic_data: bool,
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
        TestAddress2: Account(code=Op.BALANCE(target) * (2 if warm else 1) + Op.PUSH0 + Op.SSTORE),
        precompile_address: Account(balance=0xF0),
    }

    if target != precompile_address and target != system_contract_address:
        pre[target] = Account(balance=0xF2)

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=gas_limit,
        gas_price=10,
    )

    witness_check = WitnessCheck(fork=Verkle)
    for address in [TestAddress, TestAddress2, env.fee_recipient]:
        witness_check.add_account_full(address=address, account=pre.get(address))

    code_chunks = chunkify_code(pre[TestAddress2].code)
    for i, chunk in enumerate(code_chunks, start=0):
        witness_check.add_code_chunk(address=TestAddress2, chunk_number=i, value=chunk)

    target_account = (
        pre[target]
        if target != system_contract_address
        else Account(**fork.pre_allocation_blockchain()[system_contract_address])
    )

    if exp_target_basic_data:
        witness_check.add_account_basic_data(address=target, account=target_account)

    if not fails:
        witness_check.add_storage_slot(address=TestAddress2, storage_slot=0, value=None)

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    post = {
        TestAddress2: Account(code=pre[TestAddress2].code, storage={0: target_account.balance}),
    }

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
    )
