"""
Test EVM Object Format Version 1
"""
from ethereum_test_tools import Code
from ethereum_test_tools.eof import LATEST_EOF_VERSION
from ethereum_test_tools.eof.v1 import (
    VERSION_MAX_SECTION_KIND,
    Container,
    Section,
)
from ethereum_test_tools.eof.v1 import SectionKind as Kind
from ethereum_test_tools.vm.opcode import Opcodes as Op

VALID = [
    Container(
        name="single_code_section",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
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

INVALID = [
    Code(name="incomplete_magic", bytecode=bytes([0xEF])),
    Code(name="no_version", bytecode=bytes([0xEF, 0x00])),
    Code(name="no_version", bytecode=bytes([0xEF, 0x00, 0x01])),
    Code(
        name="no_code_section_size", bytecode=bytes([0xEF, 0x00, 0x01, 0x01])
    ),
    Code(
        name="code_section_size_incomplete",
        bytecode=bytes([0xEF, 0x00, 0x01, 0x01, 0x00]),
    ),
    Code(
        name="no_data_section_size",
        bytecode=bytes([0xEF, 0x00, 0x01, 0x01, 0x00, 0x02, 0x02]),
    ),
    Code(
        name="data_section_size_incomplete",
        bytecode=bytes([0xEF, 0x00, 0x01, 0x01, 0x00, 0x02, 0x02, 0x00]),
    ),
    Container(
        name="no_sections",
        sections=[],
        auto_data_section=False,
        auto_type_section=False,
    ),
    Container(
        name="invalid_magic_01",
        custom_magic=0x01,
        sections=[Section(kind=Kind.CODE, data="0x00")],
    ),
    Container(
        name="invalid_magic_ff",
        custom_magic=0xFF,
        sections=[Section(kind=Kind.CODE, data="0x00")],
    ),
    Container(
        name="invalid_version_zero",
        custom_version=0x00,
        sections=[Section(kind=Kind.CODE, data="0x00")],
    ),
    Container(
        name="invalid_version_plus_one",
        custom_version=LATEST_EOF_VERSION + 1,
        sections=[Section(kind=Kind.CODE, data="0x00")],
    ),
    Container(
        name="invalid_version_high",
        custom_version=0xFF,
        sections=[Section(kind=Kind.CODE, data="0x00")],
    ),
    Container(
        name="no_code_section",
        sections=[Section(kind=Kind.DATA, data="0x00")],
    ),
    Container(
        name="too_many_code_sections",
        sections=[Section(kind=Kind.CODE, data="0x00")] * 1025,
    ),
    Code(
        name="zero_code_sections_header",
        bytecode=bytes(
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
    ),
    Container(
        name="no_section_terminator_1",
        custom_terminator=bytes(),
        sections=[Section(kind=Kind.CODE, data="0x00", custom_size=2)],
    ),
    Container(
        name="no_section_terminator_2",
        custom_terminator=bytes(),
        sections=[Section(kind=Kind.CODE, data="0x", custom_size=3)],
    ),
    Container(
        name="no_section_terminator_3",
        custom_terminator=bytes(),
        sections=[Section(kind=Kind.CODE, data="0x600000")],
    ),
    Container(
        name="no_code_section_contents",
        sections=[Section(kind=Kind.CODE, data="0x", custom_size=0x01)],
    ),
    Container(
        name="incomplete_code_section_contents",
        sections=[
            Section(kind=Kind.CODE, data="0x00", custom_size=0x02),
        ],
    ),
    Container(
        name="trailing_bytes_after_code_section",
        sections=[Section(kind=Kind.CODE, data="0x600000")],
        extra=bytes([0xDE, 0xAD, 0xBE, 0xEF]),
    ),
    Container(
        name="empty_code_section",
        sections=[Section(kind=Kind.CODE, data="0x")],
    ),
    Container(
        name="empty_code_section_with_non_empty_data",
        sections=[
            Section(kind=Kind.CODE, data="0x"),
            Section(kind=Kind.DATA, data="0xDEADBEEF"),
        ],
    ),
    Container(
        name="data_section_preceding_code_section",
        auto_data_section=False,
        sections=[
            Section(kind=Kind.DATA, data="0xDEADBEEF"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="data_section_without_code_section",
        sections=[Section(kind=Kind.DATA, data="0xDEADBEEF")],
    ),
    Container(
        name="no_section_terminator_3",
        custom_terminator=bytes(),
        sections=[Section(kind=Kind.CODE, data="0x030004")],
    ),
    Container(
        name="no_section_terminator_4",
        custom_terminator=bytes(),
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAABBCCDD"),
        ],
    ),
    Container(
        name="no_data_section_contents",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0x", custom_size=1),
        ],
    ),
    Container(
        name="data_section_contents_incomplete",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAABBCC", custom_size=4),
        ],
    ),
    Container(
        name="trailing_bytes_after_data_section",
        extra=bytes([0xEE]),
        sections=[
            Section(kind=Kind.CODE, data="0x600000"),
            Section(kind=Kind.DATA, data="0xAABBCCDD"),
        ],
    ),
    Container(
        name="multiple_data_sections",
        sections=[
            Section(kind=Kind.CODE, data="0x600000"),
            Section(kind=Kind.DATA, data="0xAABBCC"),
            Section(kind=Kind.DATA, data="0xAABBCC"),
        ],
    ),
    Container(
        name="multiple_code_and_data_sections_1",
        #  auto_type_section=False,
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAA"),
            Section(kind=Kind.DATA, data="0xAA"),
        ],
    ),
    Container(
        name="multiple_code_and_data_sections_2",
        #  auto_type_section=False,
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAA"),
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAA"),
        ],
    ),
    Container(
        name="code_section_out_of_order",
        #  auto_type_section=False,
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0xAA"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="unknown_section_1",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0x"),
            Section(kind=VERSION_MAX_SECTION_KIND + 1, data="0x01"),
        ],
    ),
    Container(
        name="unknown_section_2",
        sections=[
            Section(kind=VERSION_MAX_SECTION_KIND + 1, data="0x01"),
            Section(kind=Kind.DATA, data="0x"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="unknown_section_empty",
        sections=[
            Section(kind=Kind.CODE, data="0x00"),
            Section(kind=Kind.DATA, data="0x"),
            Section(kind=VERSION_MAX_SECTION_KIND + 1, data="0x"),
        ],
    ),
    Container(
        name="too_many_type_sections",
        sections=[
            Section(kind=Kind.TYPE, data="0x00000000"),
            Section(kind=Kind.TYPE, data="0x00000000"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
    ),
    Container(
        name="empty_type_section",
        sections=[
            Section(kind=Kind.TYPE, data="0x"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
    ),
    Container(
        name="type_section_too_small_1",
        sections=[
            Section(kind=Kind.TYPE, data="0x00"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
    ),
    Container(
        name="type_section_too_small_2",
        sections=[
            Section(kind=Kind.TYPE, data="0x000000"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
    ),
    Container(
        name="type_section_too_big",
        sections=[
            Section(kind=Kind.TYPE, data="0x0000000000"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
        auto_type_section=False,
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
                code_inputs=127,
                code_outputs=127,
                max_stack_height=127,
            ),
        ],
    ),
    Container(
        name="single_code_section_max_stack_size",
        sections=[
            Section(
                kind=Kind.CODE,
                data=Op.CALLER * 1023 + Op.POP * 1023 + Op.STOP,
                code_inputs=0,
                code_outputs=0,
                max_stack_height=1023,
            ),
        ],
    ),
]

INVALID += [
    Container(
        name="single_code_section_non_zero_inputs",
        sections=[Section(kind=Kind.CODE, data=Op.POP, code_inputs=1)],
    ),
    Container(
        name="single_code_section_non_zero_outputs",
        sections=[Section(kind=Kind.CODE, data=Op.PUSH0, code_outputs=1)],
    ),
    Container(
        name="multiple_code_section_non_zero_inputs",
        sections=[
            Section(kind=Kind.CODE, data=Op.POP, code_inputs=1),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="multiple_code_section_non_zero_outputs",
        sections=[
            Section(kind=Kind.CODE, data=Op.PUSH0, code_outputs=1),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="data_section_before_code_with_type",
        sections=[
            Section(kind=Kind.DATA, data="0xAA"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="data_section_listed_in_type",
        sections=[
            Section(kind=Kind.DATA, data="0x00", force_type_listing=True),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="code_sections_above_1024",
        sections=[Section(kind=Kind.CODE, data="0x00")] * 1025,
    ),
    Container(
        name="single_code_section_incomplete_type",
        sections=[
            Section(kind=Kind.TYPE, data="0x00"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="single_code_section_incomplete_type_2",
        sections=[
            Section(kind=Kind.TYPE, data="0x00", custom_size=2),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="single_code_section_oversized_type",
        sections=[  # why no work
            Section(kind=Kind.TYPE, data="0x0000000000"),
            Section(kind=Kind.CODE, data="0x00"),
        ],
    ),
    Container(
        name="single_code_section_input_too_large",
        sections=[
            Section(
                kind=Kind.CODE,
                data=Op.POP + Op.RETF,
                code_inputs=128,
                code_outputs=127,
                max_stack_height=0,
            ),
        ],
    ),
    Container(
        name="single_code_section_output_too_large",
        sections=[
            Section(
                kind=Kind.CODE,
                data=Op.CALLER + Op.RETF,
                code_inputs=127,
                code_outputs=128,
                max_stack_height=1,
            ),
        ],
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
    ),
]
