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

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

ExampleAddress = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0c")
precompile_address = Address("0x04")
system_contract_address = Address("0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "target, beneficiary_must_exist",
    [
        [ExampleAddress, True],
        [ExampleAddress, False],
        [TestAddress2, True],
        [precompile_address, False],
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
    [0, 1],
)
def test_self_destruct(
    blockchain_test: BlockchainTestFiller,
    target,
    beneficiary_must_exist,
    contract_balance,
):
    """
    Test SELFDESTRUCT witness.
    """
    _selfdestruct(
        blockchain_test,
        target,
        beneficiary_must_exist,
        contract_balance,
        contract_balance > 0,
        contract_balance > 0 and not beneficiary_must_exist,
    )


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.skip("TBD gas limit")
@pytest.mark.parametrize(
    "gas_limit, beneficiary_must_exist, beneficiary_add_basic_data, beneficiary_add_codehash",
    [
        ("TBD", True, False, False),
        ("TBD", True, False, False),
        ("TBD", False, False, False),
        ("TBD", False, True, False),
    ],
    ids=[
        "beneficiary_exist_not_enough_substract_contract_balance",
        "beneficiary_exist_not_enough_add_beneficiary_balance",
        "beneficiary_doesnt_exist_create_account_basic_data",
        "beneficiary_doesnt_exist_create_account_codehash",
    ],
)
def test_self_destruct_insufficient_gas(
    blockchain_test: BlockchainTestFiller,
    gas_limit,
    beneficiary_must_exist,
    beneficiary_add_basic_data,
    beneficiary_add_codehash,
):
    """
    Test SELFDESTRUCT insufficient gas.
    """
    _selfdestruct(
        blockchain_test,
        ExampleAddress,
        beneficiary_must_exist,
        100,
        beneficiary_add_basic_data,
        beneficiary_add_codehash,
        gas_limit=gas_limit,
        fail=True,
    )


def _selfdestruct(
    blockchain_test: BlockchainTestFiller,
    beneficiary: Address,
    beneficiary_must_exist: bool,
    contract_balance: int,
    beneficiary_add_basic_data: bool,
    beneficiary_add_codehash: bool,
    gas_limit=1_000_000,
    fail=False,
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
    if beneficiary_must_exist and beneficiary != TestAddress2:
        pre[beneficiary] = Account(balance=0xFF)

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=gas_limit,
        gas_price=10,
    )

    witness_check = WitnessCheck()
    for address in [TestAddress, TestAddress2, env.fee_recipeint]:
        witness_check.add_account_full(
            address=address,
            account=(None if address == env.fee_recipient else pre[address]),
        )
    if beneficiary_add_basic_data:
        witness_check.add_account_basic_data(beneficiary, pre.get(beneficiary))
    if beneficiary_add_codehash:
        witness_check.add_account_codehash(beneficiary, None)

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    post: Alloc = {}
    if not fail and contract_balance > 0 and beneficiary != TestAddress2:
        beneficiary_account = pre.get(beneficiary)
        beneficiary_balance = 0 if beneficiary_account is None else beneficiary_account.balance
        pre[TestAddress2]
        post = {
            TestAddress2: Account(code=pre[TestAddress2].code, balance=0),
            beneficiary: Account(balance=beneficiary_balance + contract_balance),
        }

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
    )
