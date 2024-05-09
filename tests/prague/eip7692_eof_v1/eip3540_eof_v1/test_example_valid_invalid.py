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


@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
            # Check that simple EOF1 deploys
            Container(
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
            ),
            "ef000101000402000100030400010000800001305000ef",
            None,
            id="simple_eof_1_deploy",
        ),
        pytest.param(
            # Check that EOF1 undersize data is ok (4 declared, 2 provided)
            # https://github.com/ipsilon/eof/blob/main/spec/eof.md#data-section-lifecycle
            Container(
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
            ),
            "ef0001010004020001000304000400008000013050000bad",
            None,
            id="undersize_data_ok",
        ),
        pytest.param(
            # Check that EOF1 with too many or too few bytes fails
            Container(
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
            ),
            "ef0001010004020001000304000400008000013050000bad60A70BAD",
            EOFException.INVALID_SECTION_BODIES_SIZE,
            id="oversize_data_fail",
        ),
        pytest.param(
            # Check that data section size is valid
            Container(
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
            ),
            "ef0001010004020001000304000400008000013050000bad60A7",
            None,
            id="data_ok",
        ),
        pytest.param(
            # Check that EOF1 with an illegal opcode fails
            Container(
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
            ),
            "ef00010100040200010003040004000080000130ef000bad60A7",
            EOFException.UNDEFINED_INSTRUCTION,
            id="illegal_opcode_fail",
        ),
        pytest.param(
            # Check that valid EOF1 can include 0xFE, the designated invalid opcode
            Container(
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
            ),
            "ef0001010004020001000304000400008000013050fe0bad60A7",
            None,
            id="fe_opcode_ok",
        ),
        pytest.param(
            # Check that EOF1 with a bad end of sections number fails
            Container(
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
            ),
            "ef00010100040200010003040001ff00800001305000ef",
            EOFException.MISSING_TERMINATOR,
            id="headers_terminator_invalid",
        ),
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
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef0001010004020001000E04000400008000015FE10003E00003E00003E0FFFA000bad60A7",
            None,
            id="rjump_valid",
        ),
        pytest.param(
            # Sections with unreachable code fail
            Container(
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
            ),
            "ef000101000402000100050400040000800000E000015B000bad60A7",
            EOFException.UNREACHABLE_INSTRUCTIONS,
            id="unreachable_code",
        ),
        pytest.param(
            # Check that code that uses a new style conditional jump succeeds
            Container(
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
            ),
            "ef0001010004020001000704000400008000016001E100015B000bad60A7",
            None,
            id="rjumpi_valid",
        ),
        pytest.param(
            # Sections that end with a legit terminating opcode are OK
            Container(
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
            ),
            "EF0001010014020005001900030003000100010400040000800001008000020080000200800000000"
            "000005f35e2030000000300060009e50001e50002e50003e30004005f5ff35f5ffdfee40bad60a7",
            None,
            id="rjumpv_section_terminator_valid",
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
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
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
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
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
                        code=Op.RJUMPI[1](1) + Op.ADDRESS + Op.NOOP + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
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
                    Section.Code(
                        code=Op.RJUMP[3] + Op.RJUMP[2] + Op.RJUMP[-6] + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=0,
                    ),
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
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    ),
                    Section.Data("0x0bad60A7"),
                ],
            ),
            "ef000101000402000100100400040000800003600060006000E10003E10002E1FFFA000bad60A7",
            EOFException.INVALID_RJUMP_DESTINATION,
            id="push1_0_0_0_rjump_3_2_m6_fails",
        ),
        pytest.param(
            # Check that that code that uses removed opcodes fails (Data 18)
            Container(
                name="EOF1I0015",
                sections=[
                    Section.Code(
                        code=Op.JUMP(3) + Op.JUMPDEST + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("0xef"),
                ],
            ),
            "ef0001010004020001000504000100008000016003565B00ef",
            EOFException.UNDEFINED_INSTRUCTION,
            id="jump_jumpdest_fails",
        ),
        pytest.param(
            # Check that that code that uses removed opcodes fails (Data 19)
            Container(
                name="EOF1I0015",
                sections=[
                    Section.Code(
                        code=Op.JUMPI(3, 1) + Op.JUMPDEST + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("0xef"),
                ],
            ),
            "ef00010100040200010007040001000080000160016003575B00ef",
            EOFException.UNDEFINED_INSTRUCTION,
            id="jumpi_jumpdest_fails",
        ),
        pytest.param(
            # Check that that code that uses removed opcodes fails (Data 20)
            Container(
                name="EOF1I0015",
                sections=[
                    Section.Code(
                        code=Op.SELFDESTRUCT(1) + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("0xef"),
                ],
            ),
            "ef0001010004020001000404000100008000016001ff00ef",
            EOFException.UNDEFINED_INSTRUCTION,
            id="selfdestruct_fails",
        ),
        pytest.param(
            # Check that that code that uses removed opcodes fails (Data 21)
            Container(
                name="EOF1I0015",
                sections=[
                    Section.Code(
                        code=Op.SELFDESTRUCT(1) + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=7,
                        skip_body_listing=True,
                    ),
                    Section.Data("", custom_size=1),
                ],
            ),
            "ef000101000402000100040400010000800007",
            EOFException.INVALID_SECTION_BODIES_SIZE,
            id="bodies_bytes_missing",
        ),
        pytest.param(
            # Check that that code that uses removed opcodes fails (Data 22)
            Container(
                name="EOF1I0015",
                sections=[
                    Section.Code(
                        code=Op.CALLCODE(7, 6, 5, 4, 3, 2, 1) + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("ef"),
                ],
            ),
            "ef0001010004020001001004000100008000016001600260036004600560066007f200ef",
            EOFException.UNDEFINED_INSTRUCTION,
            id="callcode_fails",
        ),
        pytest.param(
            # Check that code that uses new relative jumps to outside the section fails
            Container(
                name="EOF1I0016",
                sections=[
                    Section.Code(
                        code=Op.JUMP(3) + Op.JUMPDEST + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("ef"),
                ],
            ),
            "ef0001010004020001000504000100008000016003565b00ef",
            EOFException.UNDEFINED_INSTRUCTION,
            id="jump_outside_section_fails",
        ),
        pytest.param(
            # Check that valid EOF1 with two code sections deploys
            # Check that return values are allowed on code sections that aren't zero (Data24)
            Container(
                name="EOF1V0002+EOF1V0006",
                sections=[
                    Section.Code(
                        code=Op.ADDRESS + Op.CALLF[1] + Op.POP + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.POP + Op.ADDRESS + Op.RETF,
                        code_inputs=1,
                        code_outputs=1,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "EF00010100080200020006000304000400008000010101000130e3000150005030e40bad60a7",
            None,
            id="return_allowed_on_nonzero_sections",
        ),
        pytest.param(
            # Check return values on code sections affect maxStackHeight of the caller (Data25)
            Container(
                name="EOF1V0012",
                sections=[
                    Section.Code(
                        code=Op.CALLF[1] + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.ADDRESS + Op.RETF,
                        code_inputs=0,
                        code_outputs=1,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "ef000101000802000200040002040004000080000100010001E300010030E40bad60A7",
            None,
            id="return_values_from_section_affect_stack_height_of_caller",
        ),
        pytest.param(
            # Check sections that end with a non-terminator opcode fail (Data 26)
            Container(
                name="EOF1I0024",
                sections=[
                    Section.Code(
                        code=Op.CALLF[1],
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.ADDRESS,
                        code_inputs=0,
                        code_outputs=1,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "ef000101000802000200030001040004000080000100010001E30001300bad60A7",
            EOFException.MISSING_STOP_OPCODE,
            id="non_terminating_opcode_in_section_code_fails",
        ),
        pytest.param(
            # Check sections that end with a non-terminator opcode fail (Data 26b)
            Container(
                name="EOF1I0024",
                sections=[
                    Section.Code(
                        code=Op.CALLF[1] + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.ADDRESS,
                        code_inputs=0,
                        code_outputs=1,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "ef000101000802000200040001040004000080000100010001E3000100300bad60A7",
            EOFException.INVALID_NON_RETURNING_FLAG,
            id="non_terminating_opcode_in_section_code_fails",
        ),
        pytest.param(
            # Check stack underflow caused by a function call (Data 27)
            Container(
                name="EOF1I0022",
                sections=[
                    Section.Code(
                        code=Op.CALLF[1] + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.POP + Op.RETF,
                        code_inputs=1,
                        code_outputs=0,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "ef000101000802000200040002040004000080000101000001E300010050E40bad60A7",
            EOFException.STACK_UNDERFLOW,
            id="stack_underflow_by_function_call",
        ),
        pytest.param(
            # Check data stack height of 1023 is valid (Data 28)
            Container(
                name="EOF1V0015",
                sections=[
                    Section.Code(
                        code=Op.CALLF[2] * 10 + Op.CALLF[1] * 2 + Op.ADDRESS * 3 + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1023,
                    ),
                    Section.Code(
                        code=Op.ADDRESS * 10 + Op.RETF,
                        code_inputs=0,
                        code_outputs=10,
                        max_stack_height=10,
                    ),
                    Section.Code(
                        code=Op.CALLF[1] * 10 + Op.RETF,
                        code_inputs=0,
                        code_outputs=100,
                        max_stack_height=100,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "ef000101000C0200030028000B001F04000400008003ff000a000a00640064E30002E30002E30002"
            "E30002E30002E30002E30002E30002E30002E30002E30001E3000130303000303030303030303030"
            "30E4E30001E30001E30001E30001E30001E30001E30001E30001E30001E30001E40bad60A7",
            None,
            id="stack_height_1023_valid",
        ),
        pytest.param(
            # Check data stack height of 1024 is invalid (Data 29)
            Container(
                name="EOF1I0025",
                sections=[
                    Section.Code(
                        code=Op.CALLF[2] * 10 + Op.CALLF[1] * 2 + Op.ADDRESS * 4 + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1024,
                    ),
                    Section.Code(
                        code=Op.ADDRESS * 10 + Op.RETF,
                        code_inputs=0,
                        code_outputs=10,
                        max_stack_height=10,
                    ),
                    Section.Code(
                        code=Op.CALLF[1] * 10 + Op.RETF,
                        code_inputs=0,
                        code_outputs=100,
                        max_stack_height=100,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "ef000101000C0200030029000B001F0400040000800400000a000a00640064E30002E30002E30002"
            "E30002E30002E30002E30002E30002E30002E30002E30001E300013030303000303030303030303030"
            "30E4E30001E30001E30001E30001E30001E30001E30001E30001E30001E30001E40bad60A7",
            EOFException.STACK_OVERFLOW,
            id="stack_height_1024_invalid",
        ),
        pytest.param(
            # Check data stack height of 1024 is invalid (Data 29b)
            Container(
                name="EOF1I0025",
                sections=[
                    Section.Code(
                        code=Op.CALLF[2] * 10 + Op.CALLF[1] * 2 + Op.ADDRESS * 4 + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1023,
                    ),
                    Section.Code(
                        code=Op.ADDRESS * 10 + Op.RETF,
                        code_inputs=0,
                        code_outputs=10,
                        max_stack_height=10,
                    ),
                    Section.Code(
                        code=Op.CALLF[1] * 10 + Op.RETF,
                        code_inputs=0,
                        code_outputs=100,
                        max_stack_height=100,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "ef000101000C0200030029000B001F04000400008003ff000a000a00640064E30002E30002E30002"
            "E30002E30002E30002E30002E30002E30002E30002E30001E300013030303000303030303030303030"
            "30E4E30001E30001E30001E30001E30001E30001E30001E30001E30001E30001E40bad60A7",
            EOFException.INVALID_MAX_STACK_HEIGHT,
            id="stack_height_1024_invalid",
        ),
        pytest.param(
            # Check that valid EOF1 with four code sections deploys (Data 30)
            Container(
                name="EOF1V0003",
                sections=[
                    Section.Code(
                        code=Op.ADDRESS + Op.CALLF[1] + Op.CALLF[3] + Op.CALLF[2] + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.POP + Op.ADDRESS + Op.RETF,
                        code_inputs=1,
                        code_outputs=1,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.ADDRESS + Op.POP + Op.RETF,
                        code_inputs=0,
                        code_outputs=0,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.POP + Op.ADDRESS + Op.RETF,
                        code_inputs=1,
                        code_outputs=1,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "EF0001010010020004000b000300030003040004000080000101010001000000010101000130e30001"
            "e30003e30002005030e43050e45030e40bad60a7",
            None,
            id="four_code_sections_valid",
        ),
        pytest.param(
            # Check that EOF1 with the right maxStackDepth deploys (Data 31)
            Container(
                name="EOF1V0005",
                sections=[
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.POP
                        + Op.PUSH0
                        + Op.CALLDATALOAD
                        + Op.RJUMPV[0, 3, 6]
                        + Op.JUMPF[1]
                        + Op.JUMPF[2]
                        + Op.JUMPF[3],
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.ADDRESS + Op.ADDRESS + Op.POP + Op.POP + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=2,
                    ),
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.ADDRESS
                        + Op.ADDRESS
                        + Op.POP
                        + Op.POP
                        + Op.POP
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    ),
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.POP
                        + Op.ADDRESS
                        + Op.POP
                        + Op.ADDRESS
                        + Op.POP
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "EF00010100100200040015000500070007040004000080000100800002008000030080000130505f35"
            "e202000000030006e50001e50002e50003303050500030303050505000305030503050000bad60a7",
            None,
            id="max_stack_depth_correct",
        ),
        pytest.param(
            # Check that that function calls to code sections that exist are allowed (Data 32)
            Container(
                name="EOF1V0007",
                sections=[
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.POP
                        + Op.PUSH0
                        + Op.CALLDATALOAD
                        + Op.RJUMPV[0, 3]
                        + Op.JUMPF[1]
                        + Op.JUMPF[3],
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.JUMPF[2],
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=0,
                    ),
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.ADDRESS
                        + Op.ADDRESS
                        + Op.POP
                        + Op.POP
                        + Op.POP
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    ),
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.POP
                        + Op.ADDRESS
                        + Op.POP
                        + Op.ADDRESS
                        + Op.POP
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "EF00010100100200040010000300070007040004000080000100800000008000030080000130505f35"
            "e20100000003e50001e50003e5000230303050505000305030503050000bad60a7",
            None,
            id="function_call_to_code_sections_valid",
        ),
        pytest.param(
            # Check that function calls to code sections that don't exist fail (Data 33)
            Container(
                name="EOF1I0011",
                sections=[
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.POP
                        + Op.PUSH0
                        + Op.CALLDATALOAD
                        + Op.RJUMPV[0, 3, 6]
                        + Op.JUMPF[1]
                        + Op.JUMPF[2]
                        + Op.JUMPF[3],
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.JUMPF[15],
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=0,
                    ),
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.ADDRESS
                        + Op.ADDRESS
                        + Op.POP
                        + Op.POP
                        + Op.POP
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    ),
                    Section.Code(
                        code=Op.ADDRESS
                        + Op.POP
                        + Op.ADDRESS
                        + Op.POP
                        + Op.ADDRESS
                        + Op.POP
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "EF00010100100200040015000300070007040004000080000100800000008000030080000130505f35"
            "e202000000030006e50001e50002e50003e5000f30303050505000305030503050000bad60a7",
            EOFException.INVALID_CODE_SECTION_INDEX,
            id="function_call_to_nonexistent_sections_fail",
        ),
        pytest.param(
            # Check that code sections that cause stack underflow fail (Data 34)
            Container(
                name="EOF1I0012",
                sections=[
                    Section.Code(
                        code=Op.ADDRESS + Op.POP + Op.JUMPF[1] + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.POP + Op.POP + Op.STOP,
                        code_inputs=2,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=2,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "EF0001010008020002000600030400040000800001028000023050e50001005050000bad60a7",
            EOFException.STACK_UNDERFLOW,
            id="section_cause_stack_underflow",
        ),
        pytest.param(
            # Check that we can't return more values than we declare (Data 35)
            Container(
                name="EOF1I0013",
                sections=[
                    Section.Code(
                        code=Op.ADDRESS + Op.POP + Op.CALLF[1] + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=1,
                    ),
                    Section.Code(
                        code=Op.ADDRESS + Op.ADDRESS + Op.RETF,
                        code_inputs=0,
                        code_outputs=1,
                        max_stack_height=2,
                    ),
                    Section.Data("0bad60a7"),
                ],
            ),
            "EF0001010008020002000600030400040000800001000100023050e30001003030e40bad60a7",
            EOFException.STACK_HIGHER_THAN_OUTPUTS,
            id="return_more_than_declared",
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


@pytest.mark.parametrize(
    "skip_header_listing, skip_body_listing, skip_types_body_listing, skip_types_header_listing,"
    "expected_code, expected_exception",
    [
        (
            # Data 16 test case of valid invalid eof ori filler
            True,  # second section is not in code header array
            True,  # second section is not in container's body (it's code bytes)
            False,  # but it's code input bytes still listed in container's body
            False,  # but it's code input bytes size still added to types section size
            "ef000101000802000100030400040000800001000000003050000bad60A7",
            EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
        (
            True,  # second section is not in code header array
            False,  # second section code is in container's body (3050000)
            False,  # but it's code input bytes still listed in container's body
            False,  # but it's code input bytes size still added to types section size
            "ef000101000802000100030400040000800001000000003050003050000bad60A7",
            EOFException.INVALID_SECTION_BODIES_SIZE,
        ),
        (
            False,  # second section is mentioned in code header array (0003)
            True,  # second section is not in container's body (it's code bytes)
            False,  # but it's code input bytes still listed in container's body
            False,  # but it's code input bytes size still added to types section size
            "ef0001010008020002000300030400040000800001000000003050000bad60A7",
            EOFException.UNREACHABLE_CODE_SECTIONS,
        ),
        (
            False,  # second section is mentioned in code header array (0003)
            False,  # second section code is in container's body (3050000)
            False,  # but it's code input bytes still listed in container's body
            False,  # but it's code input bytes size still added to types section size
            "ef0001010008020002000300030400040000800001000000003050003050000bad60A7",
            EOFException.UNREACHABLE_CODE_SECTIONS,
        ),
        (
            # Data 17 test case of valid invalid eof ori filler
            True,  # second section is not in code header array
            True,  # second section is not in container's body (it's code bytes)
            True,  # it's code input bytes are not listed in container's body (00000000)
            False,  # but it's code input bytes size still added to types section size
            "ef0001010008020001000304000400008000013050000bad60a7",
            EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
        (
            True,  # second section is not in code header array
            True,  # second section is not in container's body (it's code bytes)
            True,  # it's code input bytes are not listed in container's body (00000000)
            True,  # and it is bytes size is not counted in types header
            "ef0001010004020001000304000400008000013050000bad60a7",
            None,
        ),
    ],
)
def test_code_section_header_body_mismatch(
    eof_test: EOFTestFiller,
    skip_header_listing: bool,
    skip_body_listing: bool,
    skip_types_body_listing: bool,
    skip_types_header_listing: bool,
    expected_code: str,
    expected_exception: EOFException | None,
):
    """
    Inconsistent number of code sections (between types and code)
    """
    eof_code = Container(
        name="EOF1I0018",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=1,
            ),
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
                code_inputs=0,
                code_outputs=0,
                max_stack_height=0,
                # weather to not mention it in code section header list
                skip_header_listing=skip_header_listing,
                # weather to not print it's code in containers body
                skip_body_listing=skip_body_listing,
                # weather to not print it's input bytes in containers body
                skip_types_body_listing=skip_types_body_listing,
                # weather to not calculate it's input bytes size in types section's header
                skip_types_header_listing=skip_types_header_listing,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert bytes(eof_code).hex() == bytes.fromhex(expected_code).hex()

    eof_test(
        data=eof_code,
        expect_exception=expected_exception,
    )
