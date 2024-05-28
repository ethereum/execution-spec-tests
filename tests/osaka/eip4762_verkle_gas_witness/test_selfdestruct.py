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
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x09")
ExampleAddress = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0c")

contract_address = compute_create_address(TestAddress, 0)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "target, target_exists",
    [
        [ExampleAddress, True],
        [ExampleAddress, False],
        [precompile_address, True],
        [contract_address, True],
    ],
    ids=[
        "target_exists",
        "target_does_not_exist",
        "precompile",
        "beneficiary_equal_contract",
    ],
)
@pytest.mark.parametrize("contract_balance", [0, 1])
def test_balance(
    blockchain_test: BlockchainTestFiller, fork: str, target, target_exists, contract_balance
):
    """
    Test SELFDESTRUCT witness.
    """
    exp_witness = None  # TODO(verkle)
    _selfdestruct(blockchain_test, fork, target, target_exists, contract_balance, exp_witness)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "gas_limit",
    [
        "TBD",
        "TBD",
        "TBD",
        "TBD",
    ],
    ids=[
        "fail_cover_staticcost_plus_read_contract_basicdata",
        "fail_write_contract_basicdata",
        "fail_write_beneficiary_basicdata",
        "fail_write_beneficiary_code",
    ],
)
def test_balance_insufficient_gas(
    blockchain_test: BlockchainTestFiller, fork: str, target, gas_limit
):
    """
    Test SELFDESTRUCT insufficient gas.
    """
    exp_witness = None  # TODO(verkle)
    _selfdestruct(blockchain_test, fork, target, False, 1, exp_witness, gas_limit)


def _selfdestruct(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    target,
    target_exists,
    contract_balance,
    exp_witness,
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
    }
    if target != TestAddress:
        pre[target] = Account(balance=0xFF, nonce=1 if target_exists else 0)

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
