"""
EOF Classes example use
"""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

from .. import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
            # Check that code that uses a new style relative jump succeeds
            Container(
                name="EOF1V0008",
                sections=[
                    Section.Code(
                        code=Op.PUSH0
                        + Op.RJUMPI[3]
                        + Op.RJUMP[3]
                        + Op.RJUMP[3]
                        + Op.RJUMP[-6]
                        + Op.STOP,
                    ),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef0001010004020001000E04000400008000015FE10003E00003E00003E0FFFA000bad60A7",
            None,
            id="rjump_valid",
        ),
        pytest.param(
            # Check that code that uses a new style conditional jump succeeds
            Container(
                name="EOF1V0011",
                sections=[
                    Section.Code(
                        code=Op.PUSH1(1) + Op.RJUMPI[1] + Op.NOOP + Op.STOP,
                    ),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef0001010004020001000704000400008000016001E100015B000bad60A7",
            None,
            id="rjumpi_valid",
        ),
        pytest.param(
            # Check that jump tables work
            Container(
                name="EOF1V0013",
                sections=[
                    Section.Code(
                        code=Op.PUSH1(1)
                        + Op.RJUMPV[2, 0]
                        + Op.ADDRESS
                        + Op.POP
                        + Op.ADDRESS
                        + Op.POP
                        + Op.STOP,
                    ),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef0001010004020001000D04000400008000016001E2010002000030503050000bad60A7",
            None,
            id="jump_tables_valid",
        ),
        pytest.param(
            # Check that jumps into the middle on an opcode are not allowed
            Container(
                name="EOF1I0019",
                sections=[
                    Section.Code(
                        code=Op.PUSH1(1)
                        + Op.RJUMPV[b"\x02\x00\x02\xFF\xFF"]
                        + Op.ADDRESS
                        + Op.POP
                        + Op.ADDRESS
                        + Op.POP
                        + Op.STOP,
                    ),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef0001010004020001000D04000400008000016001E2020002FFFF30503050000bad60A7",
            EOFException.INVALID_RJUMP_DESTINATION,
            id="rjump_invalid",
        ),
        pytest.param(
            # TODO why here is expected an exception by the comment but test is valid
            # Check that you can't get to the same opcode with two different stack heights
            Container(
                name="EOF1I0020",
                sections=[
                    Section.Code(
                        code=Op.PUSH1(1) + Op.RJUMPI[1] + Op.ADDRESS + Op.NOOP + Op.STOP,
                    ),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef0001010004020001000804000400008000016001E10001305B000bad60A7",
            None,
            id="jump_to_opcode_ok",
        ),
        pytest.param(
            # Check that jumps into the middle on an opcode are not allowed
            Container(
                name="EOF1I0019",
                sections=[
                    Section.Code(code=Op.RJUMP[3] + Op.RJUMP[2] + Op.RJUMP[-6] + Op.STOP),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef0001010004020001000A0400040000800000E00003E00002E0FFFA000bad60A7",
            EOFException.INVALID_RJUMP_DESTINATION,
            id="rjump_3_2_m6_fails",
        ),
        pytest.param(
            # Check that jumps into the middle on an opcode are not allowed
            Container(
                name="EOF1I0019",
                sections=[
                    Section.Code(
                        code=Op.PUSH1(0)
                        + Op.PUSH1(0)
                        + Op.PUSH1(0)
                        + Op.RJUMPI[3]
                        + Op.RJUMPI[2]
                        + Op.RJUMPI[-6]
                        + Op.STOP,
                    ),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef000101000402000100100400040000800003600060006000E10003E10002E1FFFA000bad60A7",
            EOFException.INVALID_RJUMP_DESTINATION,
            id="push1_0_0_0_rjump_3_2_m6_fails",
        ),
    ],
)
def test_example_valid_invalid(
    eof_test: EOFTestFiller,
    eof_code: Container,
    expected_hex_bytecode: str,
    exception: EOFException | None,
):
    """
    Verify eof container construction and exception
    """
    # TODO remove this after Container class implementation is reliable
    assert bytes(eof_code).hex() == bytes.fromhex(expected_hex_bytecode).hex()

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
