"""
Ethereum Transient Storage EIP Tests
https://eips.ethereum.org/EIPS/eip-1153
"""

from typing import Dict, Union

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-1153.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize("call_type", [Op.CALL, Op.CALLCODE, Op.DELEGATECALL])
def test_tload_calls(state_test: StateTestFiller, call_type: Op):
    """
    Covered .json vectors:

    (04_tloadAfterCallFiller.yml)
    Loading a slot after a call to another contract is 0.

    (12_tloadDelegateCallFiller.yml)
    delegatecall reads transient storage in the context of the current address
    """
    address_to = Address("A00000000000000000000000000000000000000A")
    address_call = Address("B00000000000000000000000000000000000000B")

    # Storage variables
    str_a_tload_after_subcall_result = 0
    str_a_subcall_result = 1
    str_b_subcall_tload_result = 2
    str_b_subcall_updated_tload_result = 3

    def make_call(call_type: Op) -> bytes:
        if call_type == Op.DELEGATECALL or call_type == Op.STATICCALL:
            return call_type(Op.GAS(), address_call, 0, 32, 0, 0)
        else:
            return call_type(Op.GAS(), address_call, 0, 0, 32, 0, 0)

    pre = {
        address_to: Account(
            balance=1000000000000000000,
            nonce=0,
            code=Op.JUMPDEST()
            + Op.TSTORE(0, 10)
            + Op.SSTORE(str_a_subcall_result, make_call(call_type))
            + Op.SSTORE(str_a_tload_after_subcall_result, Op.TLOAD(0)),
            storage={
                str_a_subcall_result: 0xFF,
                str_a_tload_after_subcall_result: 0xFF,
            },
        ),
        address_call: Account(
            balance=7000000000000000000,
            nonce=0,
            code=Op.JUMPDEST()
            + Op.SSTORE(str_b_subcall_tload_result, Op.TLOAD(0))
            + Op.TSTORE(0, 20)
            + Op.SSTORE(str_b_subcall_updated_tload_result, Op.TLOAD(0)),
            storage={
                str_b_subcall_tload_result: 0xFF,
                str_b_subcall_updated_tload_result: 0xFF,
            },
        ),
        TestAddress: Account(
            balance=7000000000000000000,
            nonce=0,
            code="0x",
            storage={},
        ),
    }

    post: Dict[Address, Union[Account, object]] = {}

    post[address_to] = Account(
        storage={
            # other calls don't change context, there for tload updated in this account
            str_a_tload_after_subcall_result: 10 if call_type == Op.CALL else 20,
            str_a_subcall_result: 1,
            # since context unchanged the subcall works as if continued execution
            str_b_subcall_tload_result: 0 if call_type == Op.CALL else 10,
            str_b_subcall_updated_tload_result: 0 if call_type == Op.CALL else 20,
        }
    )

    post[address_call] = Account(
        storage={
            str_b_subcall_tload_result: 0 if call_type == Op.CALL else 0xFF,
            str_b_subcall_updated_tload_result: 20 if call_type == Op.CALL else 0xFF,
        }
    )

    tx = Transaction(
        nonce=0,
        to=address_to,
        gas_price=10,
        data=b"",
        gas_limit=5000000,
        value=0,
    )

    state_test(env=Environment(), pre=pre, post=post, tx=tx)
