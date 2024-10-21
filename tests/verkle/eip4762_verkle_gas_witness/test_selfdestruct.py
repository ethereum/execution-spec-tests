"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_forks import Fork, Verkle
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.verkle.helpers import chunkify_code

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

ExampleAddress = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0c")
precompile_address = Address("0x04")
system_contract_address = Address("0xfffffffffffffffffffffffffffffffffffffffe")


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "target, precreate_benficiary",
    [
        [ExampleAddress, True],
        [ExampleAddress, False],
        [TestAddress2, True],
        [precompile_address, True],
        [system_contract_address, False],
    ],
    ids=[
        "beneficiary_exists",
        "beneficiary_does_not_exist",
        "self_beneficiary",
        "precompile",
        "system_contract",
    ],
)
@pytest.mark.parametrize(
    "contract_balance",
    [
        0,
        1,
    ],
)
def test_self_destruct(
    blockchain_test: BlockchainTestFiller,
    target,
    precreate_benficiary,
    contract_balance,
):
    """
    Test SELFDESTRUCT witness.
    """
    _selfdestruct(
        blockchain_test,
        target,
        precreate_benficiary,
        contract_balance,
    )


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "gas_limit, precreate_beneficiary, beneficiary_basicdata, \
    beneficiary_codehash",
    [
        (26_203 + 2099, True, False, False),
        (26_203 + 2100, True, True, False),
        (26_203 + 2100 + 3500 + 3500 + 699, False, True, False),
        (26_203 + 2100 + 3500 + 3500 + 700, False, True, True),
    ],
    ids=[
        "existing_beneficiary_insufficient_beneficiary_basic_data",
        "existing_beneficiary_just_enough_beneficiary_basic_data",
        "non_existent_beneficiary_insufficient_beneficiary_codehash",
        "non_existent_beneficiary_just_enough_beneficiary_codehash",
    ],
)
def test_self_destruct_insufficient_gas(
    blockchain_test: BlockchainTestFiller,
    gas_limit,
    precreate_beneficiary,
    beneficiary_basicdata,
    beneficiary_codehash,
):
    """
    Test SELFDESTRUCT insufficient gas.
    """
    _selfdestruct(
        blockchain_test,
        ExampleAddress,
        precreate_beneficiary,
        100,
        gas_limit=gas_limit,
        fail=True,
        enough_gas_benficiary_basicdata=beneficiary_basicdata,
        enough_gas_beneficiary_codehash=beneficiary_codehash,
    )


def _selfdestruct(
    blockchain_test: BlockchainTestFiller,
    beneficiary: Address,
    precreate_benficiary: bool,
    contract_balance: int,
    gas_limit=1_000_000,
    enough_gas_benficiary_basicdata: bool = True,
    enough_gas_beneficiary_codehash: bool = True,
    fail=False,
    fork: Fork = Verkle,
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
        TestAddress2: Account(code=Op.SELFDESTRUCT(beneficiary), balance=contract_balance),
    }

    assert beneficiary != TestAddress
    if precreate_benficiary and beneficiary != TestAddress2:  # TestAddress2 is always created.
        pre[beneficiary] = Account(balance=0xFF)

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

    if enough_gas_benficiary_basicdata:
        if contract_balance > 0 or (
            beneficiary != precompile_address and beneficiary != system_contract_address
        ):
            beneficiary_account = (
                pre.get(beneficiary)
                if beneficiary != system_contract_address
                else Account(**fork.pre_allocation_blockchain()[system_contract_address])
            )
            witness_check.add_account_basic_data(beneficiary, beneficiary_account)
        if enough_gas_beneficiary_codehash and (
            contract_balance > 0
            and not precreate_benficiary
            and beneficiary != precompile_address
            and beneficiary != system_contract_address
        ):
            witness_check.add_account_codehash(beneficiary, pre.get(beneficiary))

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    post: Alloc = Alloc({})
    if not fail and contract_balance > 0 and beneficiary != TestAddress2:
        beneficiary_account = pre.get(beneficiary)
        beneficiary_balance = 0 if beneficiary_account is None else beneficiary_account.balance
        pre[TestAddress2]
        post = Alloc(
            {
                TestAddress2: Account(code=pre[TestAddress2].code, balance=0),
                beneficiary: Account(balance=beneficiary_balance + contract_balance),
            }
        )

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
    )
