"""
Ethereum Transient Storage EIP Tests
https://eips.ethereum.org/EIPS/eip-1153
"""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
    call_return_code,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-1153.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


@pytest.mark.valid_from("Cancun")
@pytest.mark.with_all_call_opcodes
def test_tload_calls(state_test: StateTestFiller, pre: Alloc, call_opcode: Op):
    """
    Ported .json vectors:

    (04_tloadAfterCallFiller.yml)
    Loading a slot after a call to another contract is 0.

    (12_tloadDelegateCallFiller.yml)
    delegatecall reads transient storage in the context of the current address
    """
    if call_opcode in [Op.STATICCALL, Op.EXTSTATICCALL]:
        pytest.skip("STATICCALL and EXTSTATICCALL cannot SSTORE")
    # Storage variables
    slot_a_tload_after_subcall_result = 0
    slot_a_subcall_result = 1
    slot_b_subcall_tload_result = 2
    slot_b_subcall_updated_tload_result = 3

    address_call = pre.deploy_contract(
        code=(
            Op.SSTORE(slot_b_subcall_tload_result, Op.TLOAD(0))
            + Op.TSTORE(0, 20)
            + Op.SSTORE(slot_b_subcall_updated_tload_result, Op.TLOAD(0))
            + Op.STOP
        ),
        storage={
            slot_b_subcall_tload_result: 0xFF,
            slot_b_subcall_updated_tload_result: 0xFF,
        },
    )

    address_to = pre.deploy_contract(
        code=(
            Op.TSTORE(0, 10)
            + Op.SSTORE(slot_a_subcall_result, call_opcode(address=address_call, args_size=32))
            + Op.SSTORE(slot_a_tload_after_subcall_result, Op.TLOAD(0))
            + Op.STOP
        ),
        storage={
            slot_a_subcall_result: 0xFF,
            slot_a_tload_after_subcall_result: 0xFF,
        },
    )

    post = {
        address_to: Account(
            storage={
                # other calls don't change context, there for tload updated in this account
                slot_a_tload_after_subcall_result: 10
                if call_opcode in [Op.CALL, Op.EXTCALL]
                else 20,
                slot_a_subcall_result: call_return_code(call_opcode, True),
                # since context unchanged the subcall works as if continued execution
                slot_b_subcall_tload_result: 0 if call_opcode in [Op.CALL, Op.EXTCALL] else 10,
                slot_b_subcall_updated_tload_result: 0
                if call_opcode in [Op.CALL, Op.EXTCALL]
                else 20,
            }
        ),
        address_call: Account(
            storage={
                slot_b_subcall_tload_result: 0 if call_opcode in [Op.CALL, Op.EXTCALL] else 0xFF,
                slot_b_subcall_updated_tload_result: 20
                if call_opcode in [Op.CALL, Op.EXTCALL]
                else 0xFF,
            }
        ),
    }

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=address_to,
        gas_limit=500_000,
    )

    state_test(env=Environment(), pre=pre, post=post, tx=tx)
