"""
abstract: Tests [EIP-7069: Revamped CALL instructions](https://eips.ethereum.org/EIPS/eip-7069)
    Tests for the RETURNDATALOAD instriction
"""  # noqa: E501

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .. import EOF_FORK_NAME
from . import REFERENCE_SPEC_GIT_PATH, REFERENCE_SPEC_VERSION
from .helpers import slot_code_worked, value_code_worked

REFERENCE_SPEC_GIT_PATH = REFERENCE_SPEC_GIT_PATH
REFERENCE_SPEC_VERSION = REFERENCE_SPEC_VERSION

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize("container_style", ["EOF", "Legacy"], ids=lambda x: x)
@pytest.mark.parametrize(
    "returndata",
    [
        b"",
        b"\x10" * 0x10,
        b"\x20" * 0x20,
        b"\x30" * 0x30,
    ],
    ids=lambda x: "len_%x" % len(x),
)
@pytest.mark.parametrize(
    "offset",
    [
        0,
        0x10,
        0x20,
        0x30,
    ],
    ids=lambda x: "offset_%x" % x,
)
@pytest.mark.parametrize(
    "size",
    [
        0,
        0x10,
        0x20,
        0x30,
    ],
    ids=lambda x: "size_%x" % x,
)
def test_returndatacopy_handling(
    state_test: StateTestFiller,
    container_style: str,
    returndata: bytes,
    offset: int,
    size: int,
):
    """
    Tests ReturnDataLoad including multiple offset conditions and differeing legacy vs. eof
    boundary conditions.

    entrypoint creates a "0xff" test area of memory, delegate calls to caller.
    Caller is either EOF or legacy, as per parameter.  Calls returner and copies the return data
    based on offset and size params.  Cases are expected to trigger boundary violations.

    Entrypoint copies the test area to storage slots, and the expected result is asserted.
    """
    env = Environment()
    address_entry_point = Address(0x1000000)
    address_caller = Address(0x1000001)
    address_returner = Address(0x1000002)
    tx = Transaction(to=address_entry_point, gas_limit=2_000_000, nonce=1)

    slot_result_start = 0x1000

    pre = {
        TestAddress: Account(balance=10**18, nonce=tx.nonce),
        address_entry_point: Account(
            nonce=1,
            code=Op.NOOP
            # First, create a "dirty" area, so we can check zero overwrite
            + Op.PUSH1(1)
            + Op.PUSH0
            + Op.SUB
            + Op.MSTORE(0x00, Op.DUP1)
            + Op.MSTORE(0x20, Op.DUP1)
            + Op.POP
            # call the contract under test
            + Op.DELEGATECALL(1_00_000, address_caller, 0, 0, 0, 0)
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            # store the return data
            + Op.SSTORE(slot_result_start, Op.MLOAD(0x0))
            + Op.SSTORE(slot_result_start + 1, Op.MLOAD(0x20))
            + Op.SSTORE(slot_code_worked, value_code_worked)
            + Op.STOP,
        ),
        address_returner: Account(
            nonce=1,
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.DATACOPY(0, 0, Op.DATASIZE) + Op.RETURN(0, Op.DATASIZE),
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    ),
                    Section.Data(data=returndata),
                ]
            ),
        ),
    }

    result = [0xFF] * 0x40
    result[0:size] = [0] * size
    extent = size - max(0, size + offset - len(returndata))
    if extent > 0 and len(returndata) > 0:
        result[0:extent] = [returndata[0]] * extent
    post = {
        address_entry_point: Account(
            storage={
                slot_code_worked: value_code_worked,
                slot_result_start: bytes(result[:0x20]),
                (slot_result_start + 0x1): bytes(result[0x20:]),
            }
        )
    }

    code_under_test: bytes = (
        Op.RETURNDATACOPY(0, offset, size)
        + Op.SSTORE(slot_code_worked, value_code_worked)
        + Op.RETURN(0, size)
    )
    match container_style:
        case "EOF":
            pre[address_caller] = Account(
                code=Container(
                    sections=[
                        Section.Code(
                            code=Op.EXTCALL(address_returner, 0, 0, 0) + code_under_test,
                            code_outputs=NON_RETURNING_SECTION,
                            max_stack_height=4,
                        )
                    ]
                )
            )
        case "Legacy":
            pre[address_caller] = Account(
                code=Op.CALL(500_000, address_returner, 0, 0, 0, 0, 0) + code_under_test,
            )
            if (offset + size) > len(returndata):
                post[address_entry_point] = Account(
                    storage={
                        slot_code_worked: value_code_worked,
                        slot_result_start: b"\xff" * 32,
                        slot_result_start + 1: b"\xff" * 32,
                    }
                )

    state_test(
        env=env,
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "returndata",
    [
        b"",
        b"\x10" * 0x10,
        b"\x20" * 0x20,
        b"\x30" * 0x30,
    ],
    ids=lambda x: "len_%x" % len(x),
)
@pytest.mark.parametrize(
    "offset",
    [
        0,
        0x10,
        0x20,
        0x30,
    ],
    ids=lambda x: "offset_%x" % x,
)
def test_returndataload_handling(
    state_test: StateTestFiller,
    returndata: bytes,
    offset: int,
):
    """
    Much simpler than returndatacopy, no memory or boosted call.  Returner is called
    and results are stored in storage slot, which is asserted for expected values.
    The parameters offset and return data are configured to test boundary conditions.
    """
    env = Environment()
    address_entry_point = Address(0x1000000)
    address_returner = Address(0x1000001)
    tx = Transaction(to=address_entry_point, gas_limit=2_000_000, nonce=1)

    slot_result_start = 0x1000

    pre = {
        TestAddress: Account(balance=10**18, nonce=tx.nonce),
        address_entry_point: Account(
            nonce=1,
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.EXTDELEGATECALL(address_returner, 0, 0)
                        + Op.SSTORE(slot_result_start, Op.RETURNDATALOAD(offset))
                        + Op.SSTORE(slot_code_worked, value_code_worked)
                        + Op.STOP,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    )
                ]
            ),
        ),
        address_returner: Account(
            nonce=1,
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.DATACOPY(0, 0, Op.DATASIZE) + Op.RETURN(0, Op.DATASIZE),
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    ),
                    Section.Data(data=returndata),
                ]
            ),
        ),
    }

    result = [0] * 0x20
    extent = 0x20 - max(0, 0x20 + offset - len(returndata))
    if extent > 0 and len(returndata) > 0:
        result[0:extent] = [returndata[0]] * extent
    print(result)
    post = {
        address_entry_point: Account(
            storage={
                slot_code_worked: value_code_worked,
                slot_result_start: bytes(result[:0x20]),
                (slot_result_start + 0x1): bytes(result[0x20:]),
            }
        )
    }

    state_test(
        env=env,
        pre=pre,
        tx=tx,
        post=post,
    )
