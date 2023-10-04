"""
Test EVM Object Format Version 1
"""
from typing import List

from ethereum_test_tools.eof import LATEST_EOF_VERSION
from ethereum_test_tools.eof.v1 import (
    VERSION_MAX_SECTION_KIND,
    Container,
    Section,
)
from ethereum_test_tools.eof.v1 import SectionKind as Kind
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .constants import (
    MAX_CODE_INPUTS,
    MAX_CODE_OUTPUTS,
    MAX_OPERAND_STACK_HEIGHT,
)

VALID: List[Container] = [
    Container(
        name="single_code_single_data_section",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0x00"),
        ],
    ),
    Container(
        name="max_code_sections",
        sections=[Section(kind=Kind.CODE, data="0x00")] * 1024,
    ),
]

INVALID: List[Container] = [
    Container(
        name="single_code_section_no_data_section",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="incomplete_magic",
        raw_bytes=bytes([0xEF]),
        validity_error="IncompleteMagic",
    ),
    Container(
        name="no_version",
        raw_bytes=bytes([0xEF, 0x00]),
        validity_error="InvalidVersion",
    ),
    Container(
        name="no_version",
        raw_bytes=bytes([0xEF, 0x00, 0x01]),
        validity_error="MissingTypeHeader",
    ),
    Container(
        name="no_type_section_size",
        raw_bytes=bytes(
            [0xEF, 0x00, 0x01, 0x01],
        ),
        validity_error="InvalidVersion",
    ),
    Container(
        name="code_section_size_incomplete_1",
        raw_bytes=bytes([0xEF, 0x00, 0x01, 0x01, 0x00, 0x04, 0x02]),
        validity_error="IncompleteCodeHeader",
    ),
    Container(
        name="code_section_size_incomplete_2",
        raw_bytes=bytes([0xEF, 0x00, 0x01, 0x01, 0x00, 0x04, 0x02, 0x00]),
        validity_error="IncompleteCodeHeader",
    ),
    Container(
        name="code_section_size_incomplete_3",
        raw_bytes=bytes(
            [0xEF, 0x00, 0x01, 0x01, 0x00, 0x04, 0x02, 0x00, 0x01]
        ),
        validity_error="IncompleteCodeHeader",
    ),
    Container(
        name="code_section_size_incomplete_4",
        raw_bytes=bytes(
            [0xEF, 0x00, 0x01, 0x01, 0x00, 0x04, 0x02, 0x00, 0x01]
        ),
        validity_error="IncompleteCodeHeader",
    ),
    Container(
        name="code_section_size_incomplete_5",
        raw_bytes=bytes(
            [0xEF, 0x00, 0x01, 0x01, 0x00, 0x04, 0x02, 0x00, 0x01, 0x00]
        ),
        validity_error="IncompleteCodeHeader",
    ),
    Container(
        name="no_data_section",
        raw_bytes=bytes(
            [0xEF, 0x00, 0x01, 0x01, 0x00, 0x04, 0x02, 0x00, 0x01, 0x00, 0x00]
        ),
        validity_error="IncompleteDataHeader",
    ),
    Container(
        name="no_data_section_size",
        raw_bytes=bytes(
            [
                0xEF,
                0x00,
                0x01,
                0x01,
                0x00,
                0x04,
                0x02,
                0x00,
                0x01,
                0x00,
                0x00,
                0x03,
            ]
        ),
        validity_error="IncompleteDataHeader",
    ),
    Container(
        name="data_section_size_incomplete",
        raw_bytes=bytes(
            [
                0xEF,
                0x00,
                0x01,
                0x01,
                0x00,
                0x04,
                0x02,
                0x00,
                0x01,
                0x00,
                0x00,
                0x03,
                0x00,
            ]
        ),
        validity_error="IncompleteDataHeader",
    ),
    Container(
        name="no_sections",
        sections=[],
        auto_data_section=False,
        auto_type_section=False,
        validity_error="MissingTypeHeader",
    ),
    Container(
        name="invalid_magic_01",
        custom_magic=0x01,
        sections=[Section(kind=Kind.CODE, data="0x00")],
        validity_error="InvalidMagic",
    ),
    Container(
        name="invalid_magic_ff",
        custom_magic=0xFF,
        sections=[Section(kind=Kind.CODE, data="0x00")],
        validity_error="InvalidMagic",
    ),
    Container(
        name="invalid_version_zero",
        custom_version=0x00,
        sections=[Section(kind=Kind.CODE, data="0x00")],
        validity_error="InvalidVersion",
    ),
    Container(
        name="invalid_version_plus_one",
        custom_version=LATEST_EOF_VERSION + 1,
        sections=[Section(kind=Kind.CODE, data="0x00")],
        validity_error="InvalidVersion",
    ),
    Container(
        name="invalid_version_high",
        custom_version=0xFF,
        sections=[Section(kind=Kind.CODE, data="0x00")],
        validity_error="InvalidVersion",
    ),
    Container(
        name="no_code_section",
        sections=[
            Section(kind=Kind.TYPE, data=bytes([0] * 4)),
            Section(kind=Kind.DATA, data="0x00"),
        ],
        auto_type_section=False,
        validity_error="MissingCodeHeader",
    ),
    Container(
        name="too_many_code_sections",
        sections=[Section(kind=Kind.CODE, data="0x00")] * 1025,
        validity_error="InvalidTypeSize",
    ),
    Container(
        name="zero_code_sections_header",
        raw_bytes=bytes(
            [
                0xEF,
                0x00,
                0x01,
                0x01,
                0x00,
                0x04,
                0x02,
                0x00,
                0x00,
                0x03,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        ),
        validity_error="InvalidCodeSection",
    ),
    Container(
        name="no_section_terminator_1",
        custom_terminator=bytes(),
        sections=[Section(kind=Kind.CODE, data="0x00", custom_size=2)],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="no_section_terminator_2",
        custom_terminator=bytes(),
        sections=[Section(kind=Kind.CODE, data="0x", custom_size=3)],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="no_section_terminator_3",
        custom_terminator=bytes(),
        sections=[Section(kind=Kind.CODE, data="0x600000")],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="no_code_section_contents",
        sections=[Section(kind=Kind.CODE, data="0x", custom_size=0x01)],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="incomplete_code_section_contents",
        sections=[
            Section(kind=Kind.CODE, data="0x00", custom_size=0x02),
        ],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="trailing_bytes_after_code_section",
        sections=[Section(kind=Kind.CODE, data="0x600000")],
        extra=bytes([0xDE, 0xAD, 0xBE, 0xEF]),
        validity_error="IncompleteContainer",
    ),
    Container(
        name="empty_code_section",
        sections=[Section(kind=Kind.CODE, data="0x")],
        validity_error="InvalidCodeSection",
    ),
    Container(
        name="empty_code_section_with_non_empty_data",
        sections=[
            Section(kind=Kind.CODE, data="0x"),
            Section(kind=Kind.DATA, data="0xDEADBEEF"),
        ],
        validity_error="InvalidCodeSection",
    ),
    Container(
        name="data_section_preceding_code_section",
        auto_data_section=False,
        sections=[
            Section(kind=Kind.DATA, data="0xDEADBEEF"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        validity_error="MissingCodeHeader",
    ),
    Container(
        name="data_section_without_code_section",
        sections=[Section(kind=Kind.DATA, data="0xDEADBEEF")],
        validity_error="MissingCodeHeader",
    ),
    Container(
        name="no_section_terminator_3",
        custom_terminator=bytes(),
        sections=[Section(kind=Kind.CODE, data="0x030004")],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="no_section_terminator_4",
        custom_terminator=bytes(),
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAABBCCDD"),
        ],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="no_data_section_contents",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0x", custom_size=1),
        ],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="data_section_contents_incomplete",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAABBCC", custom_size=4),
        ],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="trailing_bytes_after_data_section",
        extra=bytes([0xEE]),
        sections=[
            Section(kind=Kind.CODE, data="0x600000"),
            Section(kind=Kind.DATA, data="0xAABBCCDD"),
        ],
        validity_error="TrailingBytes",
    ),
    Container(
        name="multiple_data_sections",
        sections=[
            Section(kind=Kind.CODE, data="0x600000"),
            Section(kind=Kind.DATA, data="0xAABBCC"),
            Section(kind=Kind.DATA, data="0xAABBCC"),
        ],
        validity_error="MissingTerminator",
    ),
    Container(
        name="multiple_code_and_data_sections_1",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAA"),
            Section(kind=Kind.DATA, data="0xAA"),
        ],
        validity_error="MissingTerminator",
    ),
    Container(
        name="multiple_code_and_data_sections_2",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAA"),
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAA"),
        ],
        validity_error="MissingTerminator",
    ),
    Container(
        name="code_section_out_of_order",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAA"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        validity_error="MissingTerminator",
    ),
    Container(
        name="unknown_section_1",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0x"),
            Section(kind=VERSION_MAX_SECTION_KIND + 1, data="0x01"),
        ],
        validity_error="MissingTerminator",
    ),
    Container(
        name="unknown_section_2",
        sections=[
            Section(kind=VERSION_MAX_SECTION_KIND + 1, data="0x01"),
            Section(kind=Kind.DATA, data="0x"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        validity_error="MissingCodeHeader",
    ),
    Container(
        name="unknown_section_empty",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0x"),
            Section(kind=VERSION_MAX_SECTION_KIND + 1, data="0x"),
        ],
        validity_error="MissingTerminator",
    ),
    Container(
        name="no_type_section",
        sections=[
            Section(kind=Kind.CODE, data="0x00000000"),
            Section(kind=Kind.DATA, data="0x00"),
        ],
        auto_type_section=False,
        validity_error="MissingTypeHeader",
    ),
    Container(
        name="too_many_type_sections",
        sections=[
            Section(kind=Kind.TYPE, data="0x00000000"),
            Section(kind=Kind.TYPE, data="0x00000000"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
        validity_error="MissingCodeHeader",
    ),
    Container(
        name="empty_type_section",
        sections=[
            Section(kind=Kind.TYPE, data="0x"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
        validity_error="InvalidTypeSize",
    ),
    Container(
        name="type_section_too_small_1",
        sections=[
            Section(kind=Kind.TYPE, data="0x00"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
        validity_error="InvalidTypeSize",
    ),
    Container(
        name="type_section_too_small_2",
        sections=[
            Section(kind=Kind.TYPE, data="0x000000"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
        validity_error="InvalidTypeSize",
    ),
    Container(
        name="type_section_too_big",
        sections=[
            Section(kind=Kind.TYPE, data="0x0000000000"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
        validity_error="InvalidTypeSize",
    ),
]

# TODO: Max initcode as specified on EIP-3860

"""
EIP-4750 Valid and Invalid Containers
"""

VALID += [
    Container(
        name="max_code_sections_1024",
        sections=[Section(kind=Kind.CODE, data="0x00")] * 1024,
    ),
    Container(
        name="max_code_sections_1024_and_data",
        sections=([Section(kind=Kind.CODE, data="0x00")] * 1024)
        + [
            Section(kind=Kind.DATA, data="0x00"),
        ],
    ),
    Container(
        name="multiple_code_section_max_inputs_max_outputs",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(
                kind=Kind.CODE,
                data=Op.RETF,
                code_inputs=MAX_CODE_INPUTS,
                code_outputs=MAX_CODE_OUTPUTS,
                max_stack_height=MAX_CODE_INPUTS,
            ),
        ],
    ),
    Container(
        name="single_code_section_input_maximum",
        sections=[
            Section(
                kind=Kind.CODE,
                data=((Op.PUSH0 * MAX_CODE_INPUTS) + Op.CALLF(1) + Op.STOP),
                code_inputs=0,
                code_outputs=0,
                max_stack_height=MAX_CODE_INPUTS,
            ),
            Section(
                kind=Kind.CODE,
                data=(Op.POP * MAX_CODE_INPUTS) + Op.RETF,
                code_inputs=MAX_CODE_INPUTS,
                code_outputs=0,
                max_stack_height=MAX_CODE_INPUTS,
            ),
        ],
        validity_error="InvalidTypeBody",
    ),
    Container(
        name="single_code_section_output_maximum",
        sections=[
            Section(
                kind=Kind.CODE,
                data=(Op.CALLF(1) + Op.STOP),
                code_inputs=0,
                code_outputs=0,
                max_stack_height=MAX_CODE_OUTPUTS,
            ),
            Section(
                kind=Kind.CODE,
                data=(Op.PUSH0 * MAX_CODE_OUTPUTS) + Op.RETF,
                code_inputs=0,
                code_outputs=MAX_CODE_OUTPUTS,
                max_stack_height=MAX_CODE_OUTPUTS,
            ),
        ],
        validity_error="InvalidTypeBody",
    ),
    Container(
        name="single_code_section_max_stack_size",
        sections=[
            Section(
                kind=Kind.CODE,
                data=(Op.CALLER * MAX_OPERAND_STACK_HEIGHT)
                + (Op.POP * MAX_OPERAND_STACK_HEIGHT)
                + Op.STOP,
                code_inputs=0,
                code_outputs=0,
                max_stack_height=MAX_OPERAND_STACK_HEIGHT,
            ),
        ],
    ),
]

INVALID += [
    Container(
        name="single_code_section_non_zero_inputs",
        sections=[Section(kind=Kind.CODE, data=Op.POP, code_inputs=1)],
        validity_error="InvalidTypeBody",
    ),
    Container(
        name="single_code_section_non_zero_outputs",
        sections=[Section(kind=Kind.CODE, data=Op.PUSH0, code_outputs=1)],
        validity_error="InvalidTypeBody",
    ),
    Container(
        name="multiple_code_section_non_zero_inputs",
        sections=[
            Section(kind=Kind.CODE, data=Op.POP, code_inputs=1),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        validity_error="InvalidTypeBody",
    ),
    Container(
        name="multiple_code_section_non_zero_outputs",
        sections=[
            Section(kind=Kind.CODE, data=Op.PUSH0, code_outputs=1),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        validity_error="InvalidTypeBody",
    ),
    Container(
        name="data_section_before_code_with_type",
        sections=[
            Section(kind=Kind.DATA, data="0xAA"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        validity_error="MissingCodeHeader",
    ),
    Container(
        name="data_section_listed_in_type",
        sections=[
            Section(kind=Kind.DATA, data="0x00", force_type_listing=True),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        validity_error="InvalidTypeSize",
    ),
    Container(
        name="code_sections_above_1024",
        sections=[Section(kind=Kind.CODE, data="0x00")] * 1025,
        validity_error="InvalidTypeSize",
    ),
    Container(
        name="single_code_section_incomplete_type",
        sections=[
            Section(kind=Kind.TYPE, data="0x00"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
        validity_error="InvalidTypeSize",
    ),
    Container(
        name="single_code_section_incomplete_type_2",
        sections=[
            Section(kind=Kind.TYPE, data="0x00", custom_size=2),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        validity_error="IncompleteContainer",
    ),
    Container(
        name="single_code_section_input_too_large",
        sections=[
            Section(
                kind=Kind.CODE,
                data=(
                    (Op.PUSH0 * (MAX_CODE_INPUTS + 1)) + Op.CALLF(1) + Op.STOP
                ),
                code_inputs=0,
                code_outputs=0,
                max_stack_height=(MAX_CODE_INPUTS + 1),
            ),
            Section(
                kind=Kind.CODE,
                data=(Op.POP * (MAX_CODE_INPUTS + 1)) + Op.RETF,
                code_inputs=(MAX_CODE_INPUTS + 1),
                code_outputs=0,
                max_stack_height=0,
            ),
        ],
        validity_error="InvalidTypeBody",
    ),
    Container(
        name="single_code_section_output_too_large",
        sections=[
            Section(
                kind=Kind.CODE,
                data=(Op.CALLF(1) + Op.STOP),
                code_inputs=0,
                code_outputs=0,
                max_stack_height=(MAX_CODE_OUTPUTS + 1),
            ),
            Section(
                kind=Kind.CODE,
                data=(Op.PUSH0 * (MAX_CODE_OUTPUTS + 1)) + Op.RETF,
                code_inputs=0,
                code_outputs=(MAX_CODE_OUTPUTS + 1),
                max_stack_height=(MAX_CODE_OUTPUTS + 1),
            ),
        ],
        validity_error="InvalidTypeBody",
    ),
    Container(
        name="single_code_section_max_stack_size_too_large",
        sections=[
            Section(
                kind=Kind.CODE,
                data=Op.CALLER * 1024 + Op.POP * 1024 + Op.STOP,
                code_inputs=0,
                code_outputs=0,
                max_stack_height=1024,
            ),
        ],
        validity_error="InvalidTypeBody",
    ),
]
