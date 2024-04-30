"""
EOF Classes example use
"""

import pytest

from ethereum_test_tools import EOFTestFiller, Opcode
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Bytes, Container, EOFException, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION

from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


def test_EOF1V0001(eof_test: EOFTestFiller):
    """
    Check that simple EOF1 deploys
    """

    eof_code = Container(
        name="EOF1V0001",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0xef"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef000101000402000100030400010000800001305000ef").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=None,
    )


@pytest.mark.xfail(reason="Evmone failing this test, need to fix!")
def test_EOF1V0016(eof_test: EOFTestFiller):
    """
    Check that EOF1 with too many or too few bytes fails
    """

    eof_code = Container(
        name="EOF1V0016",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad", custom_size=4),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef0001010004020001000304000400008000013050000bad").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=EOFException.INVALID_SECTION_BODIES_SIZE,
    )


def test_EOF1I0006(eof_test: EOFTestFiller):
    """
    Check that EOF1 with too many or too few bytes fails
    """

    eof_code = Container(
        name="EOF1I0006",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A70BAD", custom_size=4),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef0001010004020001000304000400008000013050000bad60A70BAD").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=EOFException.INVALID_SECTION_BODIES_SIZE,
    )


def test_EOF1V0001_2(eof_test: EOFTestFiller):
    """
    Check that data section size is valid
    """

    eof_code = Container(
        name="EOF1V0001",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef0001010004020001000304000400008000013050000bad60A7").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=None,
    )


def test_EOF1I0008(eof_test: EOFTestFiller):
    """
    Check that EOF1 with an illegal opcode fails
    """

    eof_code = Container(
        name="EOF1I0008",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Opcode(0xEF) + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef00010100040200010003040004000080000130ef000bad60A7").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=EOFException.UNDEFINED_INSTRUCTION,
    )


def test_EOF1V0004(eof_test: EOFTestFiller):
    """
    Check that valid EOF1 can include 0xFE, the designated invalid opcode
    """

    eof_code = Container(
        name="EOF1V0004",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.INVALID,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef0001010004020001000304000400008000013050fe0bad60A7").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=None,
    )


def test_EOF1I0005(eof_test: EOFTestFiller):
    """
    Check that EOF1 with a bad end of sections number fails
    """

    eof_code = Container(
        name="EOF1I0005",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0xef"),
        ],
        header_terminator=Bytes(b"\xFF"),
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef00010100040200010003040001ff00800001305000ef").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=EOFException.MISSING_TERMINATOR,
    )


def test_EOF1V0008(eof_test: EOFTestFiller):
    """
    Check that code that uses a new style relative jump (E0) succeeds
    """

    eof_code = Container(
        name="EOF1V0008",
        sections=[
            Section.Code(
                code=Op.PUSH0 + Op.RJUMPI[3] + Op.RJUMP[3] + Op.RJUMP[3] + Op.RJUMP[-6] + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex(
            "ef0001010004020001000E04000400008000015FE10003E00003E00003E0FFFA000bad60A7"
        ).hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=None,
    )


def test_EOF1I0023(eof_test: EOFTestFiller):
    """
    Sections with unreachable code fail
    """

    eof_code = Container(
        name="EOF1I0023",
        sections=[
            Section.Code(
                code=Op.RJUMP[1] + Op.NOOP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=0,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef000101000402000100050400040000800000E000015B000bad60A7").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=EOFException.UNREACHABLE_INSTRUCTIONS,
    )


def test_EOF1V0011(eof_test: EOFTestFiller):
    """
    Check that code that uses a new style conditional jump (5D) succeeds
    """

    eof_code = Container(
        name="EOF1V0011",
        sections=[
            Section.Code(
                code=Op.PUSH1(1) + Op.RJUMPI[1] + Op.NOOP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef0001010004020001000704000400008000016001E100015B000bad60A7").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=None,
    )


@pytest.mark.xfail(reason="Evmone failing this test, need to fix!")
def test_EOF1V0014(eof_test: EOFTestFiller):
    """
    Sections that end with a legit terminating opcode are OK
    """

    eof_code = Container(
        name="EOF1V0014",
        sections=[
            Section.Code(
                code=Op.PUSH0
                + Op.CALLDATALOAD
                + Op.RJUMPV[0, 3, 6, 9]
                + Op.JUMPF[1]
                + Op.JUMPF[2]
                + Op.JUMPF[3]
                + Op.CALLF[4]
                + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Code(
                code=Op.PUSH0 + Op.PUSH0 + Op.RETURN,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
            Section.Code(
                code=Op.PUSH0 + Op.PUSH0 + Op.REVERT,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
            Section.Code(
                code=Op.INVALID,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=0,
            ),
            Section.Code(
                code=Op.RETF,
                code_inputs=0,
                code_outputs=0,
                max_stack_height=0,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO why ori expected this to have 3 args e2030000000300060009 ??
    # TODO JUMPF instruction was e5 but we have it b1
    assert str(bytes(Op.RJUMPV[0, 3, 6, 9]).hex()) == "e2040000000300060009"

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex(
            "EF0001010014020005001900030003000100010400040000800001008000020080000200800000000"
            "000005f35e2040000000300060009b10001b10002b10003e30004005f5ff35f5ffdfee40bad60a7"
        ).hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=None,
    )


@pytest.mark.xfail(reason="Pyspec RJUMPV implementation could be off!")
def test_EOF1V0013(eof_test: EOFTestFiller):
    """
    Jump tables work
    """
    eof_code = Container(
        name="EOF1V0013",
        sections=[
            Section.Code(
                code=Op.PUSH1(1)
                + Op.RJUMPV[1, 2, 0]
                + Op.ADDRESS
                + Op.POP
                + Op.ADDRESS
                + Op.POP
                + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO why ori expected this to have 1 args e20100020000  and we make e202...??
    assert str(bytes(Op.RJUMPV[2, 0]).hex()) == "e20100020000"

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex(
            "ef0001010004020001000D04000400008000016001E2010002000030503050000bad60A7"
        ).hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=None,
    )


def test_EOF1I0019(eof_test: EOFTestFiller):
    """
    Check that jumps into the middle on an opcode are not allowed
    """
    eof_code = Container(
        name="EOF1I0019",
        sections=[
            Section.Code(
                code=Op.PUSH1(1)
                + Op.RJUMPV[2, -1]
                + Op.ADDRESS
                + Op.POP
                + Op.ADDRESS
                + Op.POP
                + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    assert str(bytes(Op.RJUMPV[2, -1]).hex()) == "e2020002ffff"

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex(
            "ef0001010004020001000D04000400008000016001E2020002FFFF30503050000bad60A7"
        ).hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=EOFException.INVALID_RJUMP_DESTINATION,
    )


def test_EOF1I0020(eof_test: EOFTestFiller):
    """
    Check that you can't get to the same opcode with two different stack heights
    """
    eof_code = Container(
        name="EOF1I0020",
        sections=[
            Section.Code(
                code=Op.PUSH1(1) + Op.RJUMPI[1] + Op.ADDRESS + Op.NOOP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert (
        bytes(eof_code).hex()
        == bytes.fromhex("ef0001010004020001000804000400008000016001E10001305B000bad60A7").hex()
    )

    eof_test(
        data=eof_code,
        expect_exception=None,
    )
