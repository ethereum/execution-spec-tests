"""
Ethereum Transient Storage EIP Tests
https://eips.ethereum.org/EIPS/eip-1153
"""

from enum import Enum

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Case,
    Environment,
    EVMCodeType,
    Hash,
    StateTestFiller,
    Switch,
    Transaction,
    call_return_code,
)
from ethereum_test_tools.vm.opcode import Bytecode
from ethereum_test_tools.vm.opcode import Macros as Om
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-1153.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


class CallDestType(Enum):
    """Call dest type"""

    REENTRANCY = 1
    EXTERNAL_CALL = 2


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize("call_return", [Op.RETURN, Op.REVERT, Om.OOG])
@pytest.mark.parametrize("call_dest_type", [CallDestType.REENTRANCY, CallDestType.EXTERNAL_CALL])
@pytest.mark.with_all_call_opcodes
def test_tload_reentrancy(
    state_test: StateTestFiller,
    pre: Alloc,
    call_opcode: Op,
    call_return: Op,
    call_dest_type: CallDestType,
    evm_code_type: EVMCodeType,
):
    """
    Ported .json vectors:

    (05_tloadReentrancyFiller.yml)
    Reentrant calls access the same transient storage
    """
    tload_value = 44
    empty_value = 0

    # Storage variables
    slot_tload_in_subcall_result = 1
    slot_tload_after_subcall_result = 2
    slot_subcall_worked = 3
    slot_code_worked = 4

    # Function names
    do_load = 1
    do_reenter = 2
    call_dest_address: Bytecode | Address
    call_dest_address = Op.ADDRESS()

    subcall_code = Op.MSTORE(0, Op.TLOAD(0)) + call_return(0, 32)
    if call_return not in [Op.RETURN, Op.REVERT]:
        subcall_code += Op.STOP

    address_code = pre.deploy_contract(code=subcall_code)
    if call_dest_type == CallDestType.EXTERNAL_CALL:
        call_dest_address = address_code

    address_to = pre.deploy_contract(
        code=Switch(
            cases=[
                Case(
                    condition=Op.EQ(Op.CALLDATALOAD(0), do_load),
                    action=subcall_code,
                    terminating=True,
                ),
                Case(
                    condition=Op.EQ(Op.CALLDATALOAD(0), do_reenter),
                    action=Op.TSTORE(0, tload_value)
                    + Op.MSTORE(0, do_load)
                    + Op.MSTORE(32, 0xFF)
                    + Op.SSTORE(
                        slot_subcall_worked,
                        call_opcode(address=call_dest_address, args_size=32),
                    )
                    + Op.RETURNDATACOPY(32, 0, Op.RETURNDATASIZE)
                    + Op.SSTORE(slot_tload_in_subcall_result, Op.MLOAD(32))
                    + Op.SSTORE(slot_tload_after_subcall_result, Op.TLOAD(0))
                    + Op.SSTORE(slot_code_worked, 1),
                ),
            ],
            default_action=None,
            evm_code_type=evm_code_type,
        )
        + Op.STOP,
        storage={
            slot_tload_in_subcall_result: 0xFF,
            slot_tload_after_subcall_result: 0xFF,
            slot_subcall_worked: 0xFF,
            slot_code_worked: 0xFF,
        },
    )
    success = call_return == Op.RETURN
    revert = call_return == Op.REVERT

    if call_dest_type == CallDestType.REENTRANCY:
        post = {
            address_to: Account(
                storage={
                    slot_code_worked: 1,
                    # if call OOG, we fail to obtain the result
                    slot_tload_in_subcall_result: 0xFF if call_return == Om.OOG else tload_value,
                    slot_tload_after_subcall_result: tload_value,
                    slot_subcall_worked: call_return_code(call_opcode, success, revert=revert),
                }
            )
        }
    else:
        post = {
            address_to: Account(
                storage={
                    slot_code_worked: 1,
                    slot_tload_in_subcall_result: (
                        0xFF  # if call OOG, we fail to obtain the result
                        if call_return == Om.OOG
                        # else delegate and callcode are working in the same context so tload works
                        else (
                            tload_value
                            if call_opcode in [Op.DELEGATECALL, Op.CALLCODE, Op.EXTDELEGATECALL]
                            else empty_value
                        )
                    ),
                    # no subcall errors can change the tload result
                    slot_tload_after_subcall_result: 44,
                    slot_subcall_worked: call_return_code(call_opcode, success, revert=revert),
                }
            )
        }

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=address_to,
        data=Hash(do_reenter),
        gas_limit=5_000_000,
    )

    state_test(env=Environment(), pre=pre, post=post, tx=tx)
