"""
EOF JUMPF tests covering stack and code validation rules.
"""

import pytest

from ethereum_test_tools import (
    Account,
    Environment,
    EOFException,
    EOFStateTestFiller,
    EOFTestFiller,
    StateTestFiller,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import slot_code_worked, slot_conditional_result, value_code_worked
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4200.md"
REFERENCE_SPEC_VERSION = "17d4a8d12d2b5e0f2985c866376c16c8c6df7cba"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "calldata",
    [
        pytest.param(b"\0" * 32, id="c0"),
        pytest.param(b"\0" * 31 + b"\x01", id="c1"),
        pytest.param(b"\0" * 31 + b"\x03", id="c3"),
        pytest.param(b"\0" * 30 + b"\x10\x00", id="c256"),
        pytest.param(b"\xff" * 32, id="cmax"),
    ],
)
@pytest.mark.parametrize(
    "table_size",
    [
        pytest.param(1, id="t1"),
        pytest.param(3, id="t3"),
        pytest.param(256, id="t256"),
    ],
)
def test_rjumpv_condition(
    state_test: StateTestFiller,
    calldata: bytes,
    table_size: int,
):
    """Test RJUMPV contract switching based on external input"""
    value_fall_through = 0xFFFF
    value_base = 0x1000

    jump_table = b""
    for i in range(table_size):
        jump_table += int.to_bytes((i + 1) * 7, 2, "big")

    jump_targets = b""
    for i in range(table_size):
        jump_targets += Op.SSTORE(slot_conditional_result, i + value_base) + Op.STOP

    env = Environment()
    tx = Transaction(
        nonce=1,
        gas_limit=10_000_000,
        data=calldata,
    )
    pre = {
        TestAddress: Account(balance=10**18, nonce=tx.nonce),
        tx.to: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.PUSH0
                        + Op.CALLDATALOAD
                        + Op.RJUMPV
                        + int.to_bytes(table_size - 1, 1, "big")
                        + jump_table
                        + Op.SSTORE(slot_conditional_result, value_fall_through)
                        + Op.STOP
                        + jump_targets,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=2,
                    )
                ]
            ),
            nonce=1,
        ),
    }
    calldata_int = int.from_bytes(calldata, "big")
    post = {
        tx.to: Account(
            storage={
                slot_conditional_result: calldata_int + 0x1000
                if calldata_int < table_size
                else value_fall_through,
            }
        )
    }
    state_test(
        env=env,
        tx=tx,
        pre=pre,
        post=post,
    )


def test_rjumpv_forwards(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0008 (Valid) EOF with RJUMPV table size 1 (Positive)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(0)
                    + Op.RJUMPV[3]
                    + Op.NOOP
                    + Op.NOOP
                    + Op.STOP
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_backwards(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0009 (Valid) EOF with RJUMPV table size 1 (Negative)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(0)
                    + Op.RJUMPI[7]
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP
                    + Op.PUSH1(0)
                    + Op.RJUMPV[-13]
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_zero(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0010 (Valid) EOF with RJUMPV table size 1 (Zero)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(0)
                    + Op.RJUMPV[0]
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_size_3(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0011 (Valid) EOF with RJUMPV table size 3"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(0)
                    + Op.RJUMPV[3, 0, -10]
                    + Op.NOOP
                    + Op.NOOP
                    + Op.STOP
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_full_table(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0012 (Valid) EOF with RJUMPV table size 256 (Target 0)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(0)
                    + Op.RJUMPV[range(256)]
                    + Op.NOOP * 256
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_full_table_mid(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0013 (Valid) EOF with RJUMPV table size 256 (Target 100)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(100)
                    + Op.RJUMPV[range(256)]
                    + Op.NOOP * 256
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_full_table_end(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0014 (Valid) EOF with RJUMPV table size 256 (Target 254)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(254)
                    + Op.RJUMPV[range(256)]
                    + Op.NOOP * 256
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_full_table_last(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0015 (Valid) EOF with RJUMPV table size 256 (Target 256)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH2(256)
                    + Op.RJUMPV[range(256)]
                    + Op.NOOP * 256
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_max_forwards(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0016 (Valid) EOF with RJUMPV containing the maximum offset (32767)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.RJUMPV[32767]
                    + Op.NOOP * 32768
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjumpv_truncated(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0027 (Invalid) EOF code containing RJUMPV with max_index 0 but no immediates"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV + b"\0",
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.UNDEFINED_EXCEPTION,
    )


def test_rjumpv_truncated_1(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0028 (Invalid) EOF code containing truncated RJUMPV"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.UNDEFINED_EXCEPTION,
    )
    #     - data: |


def test_rjumpv_truncated_2(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0029 (Invalid) EOF code containing truncated RJUMPV"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV + b"\0\0",
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.UNDEFINED_EXCEPTION,
    )


def test_rjumpv_truncated_3(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0030 (Invalid) EOF code containing truncated RJUMPV"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV + b"\0\0",
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.UNDEFINED_EXCEPTION,
    )


def test_rjumpv_truncated_4(
    eof_test: EOFTestFiller,
):
    """EOF code containing truncated RJUMPV table"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV + b"\2\0\0\0\0",
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.UNDEFINED_EXCEPTION,
    )


def test_rjumpv_into_header(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0031 (Invalid) EOF code containing RJUMPV with target outside code bounds
    (Jumping into header)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV[-7] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_before_container(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0032 (Invalid) EOF code containing RJUMPV with target outside code bounds
    (Jumping to before code begin)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV[-15] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_data(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0033 (Invalid) EOF code containing RJUMPV with target outside code bounds
    (Jumping into data section)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV[2] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_after_container(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0034 (Invalid) EOF code containing RJUMPV with target outside code bounds
    (Jumping to after code end)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV[2] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_at_end(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0035 (Invalid) EOF code containing RJUMPV with target outside code bounds
    (Jumping to code end)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV[1] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_self(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0036 (Invalid) EOF code containing RJUMPV with target same RJUMPV immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMPV[-1] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_rjump(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0037 (Invalid) EOF code containing RJUMPV with target RJUMP immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.RJUMPV[5]
                    + Op.STOP
                    + Op.PUSH1(1)
                    + Op.RJUMP[-9]
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_rjumpi(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0038 (Invalid) EOF code containing RJUMPV with target RJUMPI immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.RJUMPV[5]
                    + Op.STOP
                    + Op.PUSH1(1)
                    + Op.RJUMPI[-9]
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_push(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0039 (Invalid) EOF code containing RJUMPV with target PUSH immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.RJUMPV[2]
                    + Op.STOP
                    + Op.PUSH1(1)
                    + Op.PUSH1(1)
                    + Op.SSTORE
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_rjumpv(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0040 (Invalid) EOF code containing RJUMPV with target other RJUMPV immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.RJUMPV[5]
                    + Op.STOP
                    + Op.PUSH1(1)
                    + Op.RJUMPV[0]
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_callf(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0041 (Invalid) EOF code containing RJUMPV with target CALLF immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(0) + Op.RJUMPV[2] + Op.CALLF[1] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.SSTORE(1, 1) + Op.RETF,
                    code_outputs=0,
                    max_stack_height=2,
                ),
            ]
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_dupn(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target DUPN immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.PUSH1(1)
                    + Op.PUSH1(0)
                    + Op.RJUMPV[1]
                    + Op.DUPN[1]
                    + Op.SSTORE
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=3,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_swapn(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target SWAPN immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.PUSH1(1)
                    + Op.PUSH1(0)
                    + Op.RJUMPV[1]
                    + Op.SWAPN[1]
                    + Op.SSTORE
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=3,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_exchange(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target EXCHANGE immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.PUSH1(2)
                    + Op.PUSH1(3)
                    + Op.PUSH1(0)
                    + Op.RJUMPV[1]
                    + Op.EXCHANGE[0x00]
                    + Op.SSTORE
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=4,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_eofcreate(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target EOFCREATE immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(0) + Op.RJUMPV[9] + Op.EOFCREATE[0](0, 0, 0, 0) + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                        sections=[
                            Section.Code(
                                code=Op.RETURNCONTRACT[0](0, 0),
                                code_outputs=NON_RETURNING_SECTION,
                                max_stack_height=2,
                            ),
                            Section.Container(
                                container=Container(
                                    sections=[
                                        Section.Code(
                                            code=Op.STOP,
                                            code_outputs=NON_RETURNING_SECTION,
                                        )
                                    ]
                                )
                            ),
                        ]
                    )
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjumpv_into_returncontract(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target RETURNCONTRACT immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.EOFCREATE[0](0, 0, 0, 0) + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                        sections=[
                            Section.Code(
                                code=Op.PUSH1(0) + Op.RJUMPV[5] + Op.RETURNCONTRACT[0](0, 0),
                                code_outputs=NON_RETURNING_SECTION,
                                max_stack_height=2,
                            ),
                            Section.Container(
                                container=Container(
                                    sections=[
                                        Section.Code(
                                            code=Op.STOP,
                                            code_outputs=NON_RETURNING_SECTION,
                                        )
                                    ]
                                )
                            ),
                        ]
                    )
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )
