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
    Bytecode,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.verkle.helpers import chunkify_code

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x04")
system_contract_address = Address("0xfffffffffffffffffffffffffffffffffffffffe")
EmptyAddress = Address("0xFFFFFFf6D732807Ef1319fB7B8bB8522d0BeacFF")


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
def test_extcodesize(blockchain_test: BlockchainTestFiller, target, bytecode):
    """
    Test EXTCODESIZE witness.
    """
    witness_check_extra = WitnessCheck(fork=Verkle)
    if target == EmptyAddress:
        witness_check_extra.add_account_basic_data(target, None)
    elif target != precompile_address and target != system_contract_address:
        account = Account(code=bytecode)
        witness_check_extra.add_account_basic_data(target, account)

    _extcodesize(blockchain_test, target, bytecode, witness_check_extra)


@pytest.mark.valid_from("Verkle")
def test_extcodesize_insufficient_gas(blockchain_test: BlockchainTestFiller):
    """
    Test EXTCODESIZE with insufficient gas.
    """
    _extcodesize(
        blockchain_test,
        TestAddress2,
        Op.PUSH0 * 1000,
        WitnessCheck(fork=Verkle),
        gas_limit=53_540,
        fails=True,
    )


@pytest.mark.valid_from("Verkle")
def test_extcodesize_warm(blockchain_test: BlockchainTestFiller):
    """
    Test EXTCODESIZE with WARM cost.
    """
    bytecode = Op.ADD(1, 2) * 10
    account = Account(code=bytecode)
    witness_check_extra = WitnessCheck(fork=Verkle)
    witness_check_extra.add_account_basic_data(TestAddress2, account)
    _extcodesize(blockchain_test, TestAddress2, bytecode, witness_check_extra, warm=True)


def _extcodesize(
    blockchain_test: BlockchainTestFiller,
    target: Address,
    bytecode: Bytecode,
    witness_check_extra: WitnessCheck,
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
        TestAddress2: Account(
            code=Op.EXTCODESIZE(target) * (2 if warm else 1) + Op.PUSH0 + Op.SSTORE
        ),
    }
    if len(bytecode) > 0:
        pre[TestAddress2] = Account(code=bytecode)

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=gas_limit,
        gas_price=10,
    )

    post = {}
    if not fails:
        post[TestAddress2] = Account(code=pre[TestAddress2].code, storage={0: 0x424242})

    witness_check = witness_check_extra
    witness_check.add_account_full(env.fee_recipient, None)
    witness_check.add_account_full(TestAddress, pre[TestAddress])
    witness_check.add_account_full(TestAddress2, pre[TestAddress2])

    code_chunks = chunkify_code(pre[TestAddress2].code)
    for i, chunk in enumerate(code_chunks, start=0):
        witness_check.add_code_chunk(address=TestAddress2, chunk_number=i, value=chunk)

    if not fails:
        witness_check.add_storage_slot(address=TestAddress2, storage_slot=0, value=None)

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
    )
