"""
EOF CALLF execution tests
"""
import pytest

from ethereum_test_specs import StateTestFiller
from ethereum_test_tools import Account, EOFStateTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_types import Alloc, Environment, Transaction

from .. import EOF_FORK_NAME
from ..eip7620_eof_create.helpers import (
    value_canary_should_not_change,
    value_canary_to_be_overwritten,
)
from .helpers import slot_code_worked, slot_stack_canary, value_canary_written, value_code_worked

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4750.md"
REFERENCE_SPEC_VERSION = "14400434e1199c57d912082127b1d22643788d11"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


def test_callf_stack_size_1024(
    eof_state_test: EOFStateTestFiller,
):
    """Test stack reaching 1024 items in called function"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 1023
                    + Op.CALLF[1]
                    + Op.POP * 1023
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.RETURN(0, 0),
                    max_stack_height=1023,
                ),
                Section.Code(
                    Op.PUSH0 + Op.POP + Op.RETF,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=1,
                ),
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_callf_with_inputs_stack_size_1024(
    eof_state_test: EOFStateTestFiller,
):
    """Test stack reaching 1024 items in called function with inputs"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 1023
                    + Op.CALLF[1]
                    + Op.POP * 1023
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.RETURN(0, 0),
                    max_stack_height=1023,
                ),
                Section.Code(
                    Op.PUSH0 + Op.POP + Op.RETF,
                    code_inputs=3,
                    code_outputs=3,
                    max_stack_height=4,
                ),
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_callf_stack_size_1024_at_callf(
    eof_state_test: EOFStateTestFiller,
):
    """Test stack reaching 1024 items in called function at CALLF instruction"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 1023
                    + Op.CALLF[1]
                    + Op.POP * 1023
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.RETURN(0, 0),
                    max_stack_height=1023,
                ),
                Section.Code(
                    Op.CALLF[2] +
                    # stack has 1024 items
                    Op.POP + Op.RETF,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=1,
                ),
                Section.Code(
                    Op.PUSH0 + Op.RETF,  # stack has 1024 items
                    code_inputs=0,
                    code_outputs=1,
                    max_stack_height=1,
                ),
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_callf_stack_size_1024_at_push(
    eof_state_test: EOFStateTestFiller,
):
    """Test stack reaching 1024 items in nested called function at PUSH0 instruction"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 1022
                    + Op.CALLF[1]
                    + Op.POP * 1022
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.RETURN(0, 0),
                    max_stack_height=1022,
                ),
                Section.Code(
                    Op.PUSH0 +
                    # stack has 1023 items
                    Op.CALLF[2] + Op.POP + Op.RETF,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=1,
                ),
                Section.Code(
                    Op.PUSH0 +
                    # stack has 1024 items
                    Op.POP + Op.RETF,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=1,
                ),
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_callf_stack_overflow(
    eof_state_test: EOFStateTestFiller,
):
    """Test stack overflowing 1024 items in called function"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 1023
                    + Op.CALLF[1]
                    + Op.POP * 1023
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.RETURN(0, 0),
                    max_stack_height=1023,
                ),
                Section.Code(
                    Op.PUSH0 +
                    # Stack has 1024 items
                    Op.CALLF[2] + Op.POP + Op.RETF,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=1,
                ),
                Section.Code(
                    Op.PUSH0 +
                    # Runtime stack overflow
                    Op.POP + Op.RETF,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=1,
                ),
            ],
        ),
        container_post=Account(storage={slot_code_worked: 0}),
    )


def test_callf_with_inputs_stack_size_1024_at_push(
    eof_state_test: EOFStateTestFiller,
):
    """Test stack reaching 1024 items in nested called function with inputs at PUSH0 instruction"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 1022
                    + Op.CALLF[1]
                    + Op.POP * 1022
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.RETURN(0, 0),
                    max_stack_height=1022,
                ),
                Section.Code(
                    Op.PUSH0 +
                    # Stack has 1023 items
                    Op.CALLF[2] + Op.POP + Op.RETF,
                    code_inputs=3,
                    code_outputs=3,
                    max_stack_height=4,
                ),
                Section.Code(
                    Op.PUSH0 +
                    # Stack has 1024 items
                    Op.POP + Op.RETF,
                    code_inputs=3,
                    code_outputs=3,
                    max_stack_height=4,
                ),
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_callf_with_inputs_stack_overflow(
    eof_state_test: EOFStateTestFiller,
):
    """Test stack overflowing 1024 items in called function with inputs"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 1023
                    + Op.CALLF[1]
                    + Op.POP * 1023
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.RETURN(0, 0),
                    max_stack_height=1023,
                ),
                Section.Code(
                    Op.PUSH0 +
                    # Stack has 1024 items
                    Op.CALLF[2] + Op.POP + Op.RETF,
                    code_inputs=3,
                    code_outputs=3,
                    max_stack_height=4,
                ),
                Section.Code(
                    Op.PUSH0 +
                    # Runtime stackoverflow
                    Op.POP + Op.RETF,
                    code_inputs=3,
                    code_outputs=3,
                    max_stack_height=4,
                ),
            ],
        ),
        container_post=Account(storage={slot_code_worked: 0}),
    )


@pytest.mark.parametrize(
    ("stack_height", "inputs", "outputs", "failure"),
    (
        pytest.param(1020, 1, 3, False, id="1020"),
        pytest.param(1021, 1, 3, True, id="1021"),
    ),
)
def test_callf_sneaky_stack_overflow(
    stack_height: int,
    inputs: int,
    outputs: int,
    failure: bool,
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    CALLF where a normal execution would not overflow, but EIP-4750 CALLF rule #3 triggers.

    Code Section 0 - Mostly fills the stack
    Code Section 1 - jumper to 2, so container verification passes (we want a runtime failure)
    Code Section 2 - Could require too much stack, but doesn't as it JUMPFs to 3
    Code Section 3 - Writes canary values

    The intent is to catch implementations of CALLF that don't enforce rule #3
    """
    env = Environment()
    sender = pre.fund_eoa()
    contract_address = pre.deploy_contract(
        code=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0 * stack_height
                    + Op.CALLF[1]
                    + Op.POP * stack_height
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.RETURN(0, 0),
                    max_stack_height=stack_height + outputs - inputs,
                ),
                Section.Code(
                    Op.CALLF[2] + Op.POP + Op.RETF,
                    code_inputs=inputs,
                    code_outputs=outputs,
                    max_stack_height=outputs + 1,
                ),
                Section.Code(
                    Op.RJUMPI[4]
                    + Op.PUSH0
                    + Op.JUMPF[3]
                    + Op.PUSH0 * (outputs - inputs + 3)
                    + Op.POP
                    + Op.RETF,
                    code_inputs=inputs,
                    code_outputs=outputs + 1,
                    max_stack_height=outputs + 2,
                ),
                Section.Code(
                    Op.POP * inputs
                    + Op.SSTORE(slot_stack_canary, value_canary_written)
                    + Op.PUSH0 * (outputs + 1)
                    + Op.RETF,
                    code_inputs=inputs,
                    code_outputs=outputs + 1,
                    max_stack_height=outputs + 1,
                ),
            ],
        ),
        storage={
            slot_code_worked: (
                value_canary_should_not_change if failure else value_canary_to_be_overwritten
            ),
            slot_stack_canary: (
                value_canary_should_not_change if failure else value_canary_to_be_overwritten
            ),
        },
    )

    post = {
        contract_address: Account(
            storage={
                slot_code_worked: (
                    value_canary_should_not_change if failure else value_code_worked
                ),
                slot_stack_canary: (
                    value_canary_should_not_change if failure else value_canary_written
                ),
            }
        )
    }

    tx = Transaction(
        to=contract_address,
        gas_limit=10_000_000,
        gas_price=10,
        protected=False,
        sender=sender,
    )
    state_test(env=env, pre=pre, post=post, tx=tx)
