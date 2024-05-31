"""
EOF JUMPF tests covering stack and code validation rules.
"""

import pytest

from ethereum_test_tools import Account, EOFException, EOFStateTestFiller, EOFTestFiller
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import slot_code_worked, value_code_worked
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4200.md"
REFERENCE_SPEC_VERSION = "17d4a8d12d2b5e0f2985c866376c16c8c6df7cba"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


def test_rjump_positive_negative(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0001 (Valid) EOF code containing RJUMP (Positive, Negative)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.RJUMPI[3]
                    + Op.RJUMP[7]
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP
                    + Op.RJUMP[-10],
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjump_positive_negative_with_data(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0001 (Valid) EOF code containing RJUMP (Positive, Negative)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.RJUMPI[3]
                    + Op.RJUMP[7]
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP
                    + Op.RJUMP[-10],
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                ),
                Section.Data(data=b"\xde\xad\xbe\xef"),
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjump_zero(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0002 (Valid) EOF code containing RJUMP (Zero)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[0] + Op.SSTORE(slot_code_worked, value_code_worked) + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjump_maxes(
    eof_state_test: EOFStateTestFiller,
):
    """EOF1V4200_0003 EOF with RJUMP containing the maximum positive and negative offset (32767)"""
    eof_state_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.RJUMPI[3]  # The push/jumpi is to allow the NOOPs to be forward referenced
                    + Op.RJUMP[0x7FFF]
                    + Op.NOOP * (0x7FFF - 7)
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.STOP
                    + Op.RJUMP[0x8000],
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
        container_post=Account(storage={slot_code_worked: value_code_worked}),
    )


def test_rjump_truncated_rjump(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0001 (Invalid) EOF code containing truncated RJUMP"""
    eof_test(
        data=Container(
            sections=[Section.Code(code=Op.RJUMP, code_outputs=NON_RETURNING_SECTION)],
        ),
        expect_exception=EOFException.UNDEFINED_EXCEPTION,
    )


def test_rjump_truncated_rjump_2(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0002 (Invalid) EOF code containing truncated RJUMP"""
    eof_test(
        data=Container(
            sections=[Section.Code(code=Op.RJUMP + Op.STOP, code_outputs=NON_RETURNING_SECTION)],
        ),
        expect_exception=EOFException.UNDEFINED_EXCEPTION,
    )


def test_rjump_into_header(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0003 (Invalid) EOF code containing RJUMP with target outside code bounds
    (Jumping into header)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(code=Op.RJUMP[-5], code_outputs=NON_RETURNING_SECTION),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_before_header(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0004 (Invalid) EOF code containing RJUMP with target outside code bounds
    (Jumping before code begin)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[-23],
                    code_outputs=NON_RETURNING_SECTION,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_data(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0005 (Invalid) EOF code containing RJUMP with target outside code bounds
    (Jumping into data section)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[2],
                    code_outputs=NON_RETURNING_SECTION,
                ),
                Section.Data(data=b"\xaa\xbb\xcc"),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_outside_other_section_before(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target outside code bounds (prior code section)"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.JUMPF[1],
                    code_outputs=NON_RETURNING_SECTION,
                ),
                Section.Code(
                    code=Op.RJUMP[-6],
                    code_outputs=NON_RETURNING_SECTION,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_outside_other_section_after(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target outside code bounds (Subsequent code section)"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.JUMPF[1],
                    code_outputs=NON_RETURNING_SECTION,
                ),
                Section.Code(
                    code=Op.RJUMP[3] + Op.JUMPF[2],
                    code_outputs=NON_RETURNING_SECTION,
                ),
                Section.Code(
                    code=Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_after_container(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0006 (Invalid) EOF code containing RJUMP with target outside code bounds
    (Jumping after code end)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[2],
                    code_outputs=NON_RETURNING_SECTION,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_to_code_end(
    eof_test: EOFTestFiller,
):
    """
    EOF1I4200_0007 (Invalid) EOF code containing RJUMP with target outside code bounds
    (Jumping to code end)
    """
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[1] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_self(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0008 (Invalid) EOF code containing RJUMP with target self RJUMP immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[-1],
                    code_outputs=NON_RETURNING_SECTION,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_rjump(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0009 (Invalid) EOF code containing RJUMP with target other RJUMP immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[1] + Op.RJUMP[0],
                    code_outputs=NON_RETURNING_SECTION,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_rjumpi(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0010 (Invalid) EOF code containing RJUMP with target RJUMPI immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[5] + Op.STOP + Op.PUSH1(1) + Op.RJUMPI[-6] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_push(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0011 (Invalid) EOF code containing RJUMP with target PUSH immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1) + Op.RJUMP[-4],
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_rjumpv(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0012 (Invalid) EOF code containing RJUMP with target RJUMPV immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[5] + Op.STOP + Op.PUSH1(1) + Op.RJUMPV[0] + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=1,
                )
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_callf(
    eof_test: EOFTestFiller,
):
    """EOF1I4200_0013 (Invalid) EOF code containing RJUMP with target CALLF immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[2] + Op.CALLF(1) + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                ),
                Section.Code(
                    code=Op.SSTORE(1, 1) + Op.RETF,
                    code_outputs=0,
                    max_stack_height=2,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_dupn(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target DUPN immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.PUSH1(1)
                    + Op.RJUMP[1]
                    + Op.DUPN[1]
                    + Op.SSTORE
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_swapn(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target SWAPN immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.PUSH1(1)
                    + Op.PUSH1(1)
                    + Op.RJUMP[1]
                    + Op.SWAPN[1]
                    + Op.SSTORE
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
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
                    + Op.RJUMP[1]
                    + Op.EXCHANGE[0x00]
                    + Op.SSTORE
                    + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=3,
                ),
            ],
        ),
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_rjump_into_eofcreate(
    eof_test: EOFTestFiller,
):
    """EOF code containing RJUMP with target EOFCREATE immediate"""
    eof_test(
        data=Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[1] + Op.EOFCREATE[0](0, 0, 0, 0) + Op.STOP,
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


def test_rjump_into_returncontract(
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
                                code=Op.RJUMP[5] + Op.RETURNCONTRACT[0](0, 0),
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
