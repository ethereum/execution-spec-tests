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
from ethereum_test_tools.vm.opcode import Macros as Om
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-1153.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"
address_code = Address("B00000000000000000000000000000000000000B")


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize("call_type", [Op.CALL, Op.CALLCODE, Op.DELEGATECALL, Op.STATICCALL])
@pytest.mark.parametrize("call_return", [Op.RETURN, Op.REVERT, Om.OOG])
@pytest.mark.parametrize("call_dest", [Op.ADDRESS(), address_code])
def test_tstore_reentrancy(
    state_test: StateTestFiller, call_type: Op, call_return: Op, call_dest: bytes
):
    """
    Covered .json vectors:

    (06_tstoreInReentrancyCallFiller.yml)
    Reentrant calls access the same transient storage

    (07_tloadAfterReentrancyStoreFiller.yml)
    Successfully returned calls do not revert transient storage writes

    (08_revertUndoesTransientStoreFiller.yml)
    Revert undoes the transient storage writes from a call.

    (09_revertUndoesAllFiller.yml)
    Revert undoes all the transient storage writes to the same key from the failed call.

    (11_tstoreDelegateCallFiller.yml)
    delegatecall manipulates transient storage in the context of the current address.

    (13_tloadStaticCallFiller.yml)
    Transient storage cannot be manipulated in a static context, tstore reverts

    (20_oogUndoesTransientStoreInCallFiller.yml)
    Out of gas undoes the transient storage writes from a call.
    """
    address_to = Address("A00000000000000000000000000000000000000A")
    tload_value_set_before_call = 80
    tload_value_set_in_call = 90

    # Storage cells
    str_tload_before_call = 0
    str_tload_in_subcall_result = 1
    str_tload_after_call = 2
    str_subcall_worked = 3
    str_tload_1_after_call = 4
    str_tstore_overwrite = 5
    str_code_worked = 6

    # Function names
    do_tstore = 1
    do_reenter = 2

    def make_call(call_type: Op) -> bytes:
        if call_type == Op.DELEGATECALL or call_type == Op.STATICCALL:
            return call_type(Op.GAS(), call_dest, 0, 32, 32, 32)
        else:
            return call_type(Op.GAS(), call_dest, 0, 0, 32, 32, 32)

    subcall_code = (
        Op.TSTORE(0, 89)
        + Op.TSTORE(0, tload_value_set_in_call)
        + Op.TSTORE(1, 11)
        + Op.TSTORE(1, 12)
        + Op.MSTORE(0, Op.TLOAD(0))
        + call_return(0, 32)
    )

    pre = {
        address_to: Account(
            balance=1000000000000000000,
            nonce=0,
            code=Switch(
                cases=[
                    Case(
                        condition=Op.EQ(Op.CALLDATALOAD(0), do_tstore),
                        action=subcall_code,
                    ),
                    Case(
                        condition=Op.EQ(Op.CALLDATALOAD(0), do_reenter),
                        action=Op.TSTORE(0, tload_value_set_before_call)
                        + Op.SSTORE(str_tload_before_call, Op.TLOAD(0))
                        + Op.MSTORE(0, do_tstore)
                        + Op.MSTORE(32, 0xFF)
                        + Op.SSTORE(str_subcall_worked, make_call(call_type))
                        + Op.SSTORE(str_tload_in_subcall_result, Op.MLOAD(32))
                        + Op.SSTORE(str_tload_after_call, Op.TLOAD(0))
                        + Op.SSTORE(str_tload_1_after_call, Op.TLOAD(1))
                        + Op.TSTORE(0, 50)
                        + Op.SSTORE(str_tstore_overwrite, Op.TLOAD(0))
                        + Op.SSTORE(str_code_worked, 1),
                    ),
                ],
                default_action=b"",
            ),
            storage={
                str_tload_before_call: 0xFF,
                str_tload_in_subcall_result: 0xFF,
                str_tload_after_call: 0xFF,
                str_subcall_worked: 0xFF,
                str_tload_1_after_call: 0xFF,
                str_tstore_overwrite: 0xFF,
                str_code_worked: 0xFF,
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

    def failing_calls() -> bool:
        return call_type == Op.STATICCALL or call_return == Op.REVERT or call_return == Om.OOG

    def successful_delegate_or_callcode() -> bool:
        return (
            (call_type == Op.DELEGATECALL or call_type == Op.CALLCODE)
            and call_return != Op.REVERT
            and call_return != Om.OOG
        )

    if call_dest == Op.ADDRESS():
        # if reentrancy
        post[address_to] = Account(
            storage={
                str_code_worked: 1,
                str_tload_before_call: tload_value_set_before_call,
                str_tload_in_subcall_result: (
                    # we fail to obtain in call result if it fails
                    0xFF
                    if call_type == Op.STATICCALL or call_return == Om.OOG
                    else tload_value_set_in_call
                ),
                # reentrant tstore overrides value in upper level
                str_tload_after_call: (
                    tload_value_set_before_call if failing_calls() else tload_value_set_in_call
                ),
                str_tload_1_after_call: 0 if failing_calls() else 12,
                str_tstore_overwrite: 50,
                # tstore in static call not allowed
                str_subcall_worked: 0 if failing_calls() else 1,
            }
        )
    else:
        post[address_to] = Account(
            # if external call
            storage={
                str_code_worked: 1,
                str_tload_before_call: tload_value_set_before_call,
                str_tload_in_subcall_result: (
                    # we fail to obtain in call result if it fails
                    0xFF
                    if call_type == Op.STATICCALL or call_return == Om.OOG
                    else tload_value_set_in_call
                ),
                # external tstore overrides value in upper level only in delegate and callcode
                str_tload_after_call: (
                    tload_value_set_in_call
                    if successful_delegate_or_callcode()
                    else tload_value_set_before_call
                ),
                str_tload_1_after_call: 12 if successful_delegate_or_callcode() else 0,
                str_tstore_overwrite: 50,
                # tstore in static call not allowed, reentrancy means external call here
                str_subcall_worked: 0 if failing_calls() else 1,
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
