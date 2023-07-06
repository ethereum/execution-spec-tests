"""
abstract: Tests [EIP-6780: SELFDESTRUCT only in same transaction](https://eips.ethereum.org/EIPS/eip-6780)

    Tests for [EIP-6780: SELFDESTRUCT only in same transaction](https://eips.ethereum.org/EIPS/eip-6780).

"""  # noqa: E501

from typing import Any, Dict, List

import pytest

from ethereum_test_tools import Account, Environment, StateTestFiller, TestAddress, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6780.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

SELFDESTRUCT_EIP_NUMBER = 6780


@pytest.mark.parametrize(
    "eips",
    [
        [SELFDESTRUCT_EIP_NUMBER],
        [],
    ],
    ids=["eip-enabled", "eip-disabled"],
)
@pytest.mark.valid_from("Shanghai")
def test_create_selfdestruct_same_tx(state_test: StateTestFiller):
    """
    TODO test that if a contract is created and then selfdestructs in the same
    transaction the contract should not be created.
    """
    env = Environment(
        coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    post: Dict[Any, Any] = {}

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
    }

    """
    original code
    test_ops = [
        "6032",
        "601c",
        "6000",
        "39",  # codecopy
        # create account
        "6032",
        "6000",
        "6000",  # zero value
        "f0"
        # TODO call created account
        "6000",
        "6000",
        "6000",
        "6000",
        "6000",
        "85",  # dup the returned address
        "45",  # pass gas limit
        "f1",
        "00"  # STOP
        # payload:
        # copy inner payload to memory
        "6008",
        "600c",
        "6000",
        "39",  # codecopy
        # return payload
        "6008",
        "6000",
        "f3",
        # inner payload:
        "60016000556000ff",
    ]
    """
    code = Op.CODECOPY(0, 0x1C, 0x32)
    # create account
    code += Op.CREATE(0, 0, 0x32)
    # TODO call created account
    code += Op.PUSH0
    code += Op.PUSH0
    code += Op.PUSH0
    code += Op.PUSH0
    code += Op.PUSH0
    code += Op.DUP6  # dup the returned address
    code += Op.GASLIMIT
    code += Op.CALL()
    code += Op.STOP
    # payload:
    # copy inner payload to memory
    code += Op.CODECOPY(0, 0x0C, 0x08)
    # return payload
    # inner payload:
    code += Op.RETURN(0x00, 0x08)
    code += Op.SSTORE(0, 1)
    code += Op.PUSH0
    code += Op.SELFDESTRUCT

    post["0x5fef11c6545be552c986e9eaac3144ecf2258fd3"] = Account.NONEXISTENT

    tx = Transaction(
        ty=0x0,
        # data="".join(test_ops),
        data=code,
        chain_id=0x0,
        nonce=0,
        to=None,
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx], tag="6780-create-inside-tx")


@pytest.mark.parametrize(
    "eips",
    [
        [SELFDESTRUCT_EIP_NUMBER],
        [],
    ],
    ids=["eip-enabled", "eip-disabled"],
)
@pytest.mark.valid_from("Shanghai")
def test_selfdestruct_prev_created(state_test: StateTestFiller, eips: List[int]):
    """
    Test that if a previously created account that contains a selfdestruct is
    called, its balance is sent to the zero address.
    """
    eip_enabled = SELFDESTRUCT_EIP_NUMBER in eips

    env = Environment(
        coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )

    # original code: 0x60016000556000ff  # noqa: SC100
    code = Op.SSTORE(0, 1) + Op.SELFDESTRUCT(0)

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        "0x1111111111111111111111111111111111111111": Account(balance=1, code=code),
    }

    post: Dict[str, Account] = {
        "0x0000000000000000000000000000000000000000": Account(balance=1),
    }

    if eip_enabled:
        post["0x1111111111111111111111111111111111111111"] = Account(balance=0, code=code)
    else:
        post["0x1111111111111111111111111111111111111111"] = Account.NONEXISTENT  # type: ignore

    tx = Transaction(
        ty=0x0,
        data="",
        chain_id=0x0,
        nonce=0,
        to="0x1111111111111111111111111111111111111111",
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx], tag="6780-prev-created")
