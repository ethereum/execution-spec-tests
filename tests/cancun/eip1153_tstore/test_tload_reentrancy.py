"""
Ethereum Transient Storage EIP Tests
https://eips.ethereum.org/EIPS/eip-1153
"""

from typing import Dict, Union

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Case,
    Environment,
    Hash,
    StateTestFiller,
    Switch,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-1153.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"
address_code = Address("B00000000000000000000000000000000000000B")


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize("call_type", [Op.CALL, Op.CALLCODE, Op.DELEGATECALL, Op.STATICCALL])
@pytest.mark.parametrize("call_return", [Op.RETURN, Op.REVERT, Op.OOG])
@pytest.mark.parametrize("call_dest", [Op.ADDRESS(), address_code])
def test_tload_reentrancy(
    state_test: StateTestFiller, call_type: Op, call_return: Op, call_dest: bytes
):
    """
    Covered .json vectors:

    (05_tloadReentrancyFiller.yml)
    Reentrant calls access the same transient storage
    """

    address_to = Address("A00000000000000000000000000000000000000A")

    # Storages
    str_tload_in_subcall_result = 1
    str_tload_after_subcall_result = 2
    str_subcall_worked = 3

    # Function names
    do_load = 1
    do_reenter = 2

    def make_call(call_type: Op) -> bytes:
        if call_type == Op.DELEGATECALL or call_type == Op.STATICCALL:
            return call_type(Op.GAS(), call_dest, 0, 32, 32, 32)
        else:
            return call_type(Op.GAS(), call_dest, 0, 0, 32, 32, 32)

    subcall_code = Op.MSTORE(0, Op.TLOAD(0)) + call_return(0, 32)

    pre = {
        address_to: Account(
            balance=1000000000000000000,
            nonce=0,
            code=Switch(
                cases=[
                    Case(
                        condition=Op.EQ(Op.CALLDATALOAD(0), do_load),
                        action=subcall_code,
                    ),
                    Case(
                        condition=Op.EQ(Op.CALLDATALOAD(0), do_reenter),
                        action=Op.TSTORE(0, 44)
                        + Op.MSTORE(0, do_load)
                        + Op.MSTORE(32, 0xFF)
                        + Op.SSTORE(str_subcall_worked, make_call(call_type))
                        + Op.SSTORE(str_tload_in_subcall_result, Op.MLOAD(32))
                        + Op.SSTORE(str_tload_after_subcall_result, Op.TLOAD(0)),
                    ),
                ],
                default_action=b"",
            ),
            storage={
                str_tload_in_subcall_result: 0xFF,
                str_tload_after_subcall_result: 0xFF,
                str_subcall_worked: 0xFF,
            },
        ),
        address_code: Account(
            balance=0,
            nonce=0,
            code=subcall_code,
            storage={},
        ),
        TestAddress: Account(
            balance=7000000000000000000,
            nonce=0,
            code="0x",
            storage={},
        ),
    }

    post: Dict[Address, Union[Account, object]] = {}

    if call_dest == Op.ADDRESS:
        # if reentrancy
        post[address_to] = Account(
            storage={
                # if call OOG, we fail to obtain the result
                str_tload_in_subcall_result: 0xFF if call_return == Op.OOG else 44,
                str_tload_after_subcall_result: 44,
                str_subcall_worked: (
                    0 if call_return == Op.REVERT or call_return == Op.OOG else 1
                ),
            }
        )
    else:
        # if external call
        post[address_to] = Account(
            storage={
                str_tload_in_subcall_result: (
                    0xFF  # if call OOG, we fail to obtain the result
                    if call_return == Op.OOG
                    # else delegate and callcode are working in the same context so tload works
                    else 44 if call_type == Op.DELEGATECALL or call_type == Op.CALLCODE else 0
                ),
                # no subcall errors can change the tload result
                str_tload_after_subcall_result: 44,
                str_subcall_worked: (
                    0 if call_return == Op.REVERT or call_return == Op.OOG else 1
                ),
            }
        )
    tx = Transaction(
        nonce=0,
        to=address_to,
        gas_price=10,
        data=Hash(do_reenter),
        gas_limit=5000000,
        value=0,
    )

    state_test(env=Environment(), pre=pre, post=post, tx=tx)
