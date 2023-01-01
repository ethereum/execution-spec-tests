from typing import List

from ethereum_test_tools import Code
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1 import SectionKind as Kind
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .opcodes import (
    INVALID_OPCODES,
    INVALID_TERMINATING_OPCODES,
    V1_EOF_OPCODES,
    VALID_TERMINATING_OPCODES,
)

VALID: List[Code | Container] = []
INVALID: List[Code | Container] = []


def make_valid_terminating_code(op: Op) -> bytes:
    out = bytes()
    for _ in range(op.popped_stack_items):
        # We need to push some items onto the stack so the code is valid
        # even with stack validation
        out += Op.ORIGIN
    out += op
    return out


# Create containers where each valid terminating opcode is at the end of the
# bytecode.
for op in VALID_TERMINATING_OPCODES:
    VALID.append(
        Container(
            name=f"valid_terminating_opcode_{str(op)}",
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=make_valid_terminating_code(op),
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=op.popped_stack_items,
                ),
            ],
        ),
    )


# Create containers where each invalid terminating opcode is located at the
# end of the bytecode.
# TODO: make sure all undefined opcodes are invalid
for op in INVALID_TERMINATING_OPCODES:
    INVALID.append(
        Container(
            name=f"invalid_terminating_opcode_0x{op.hex()}",
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=make_valid_terminating_code(op),
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=op.popped_stack_items,
                ),
            ],
        ),
    )

# Create containers containing a valid terminating opcode, but the
# invalid opcode somewhere in the bytecode.
for op in INVALID_OPCODES:
    INVALID.append(
        Container(
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=op + Op.STOP,
                ),
            ],
            name=f"invalid_terminating_opcode_0x{op.hex()}",
        ),
    )

# Create an invalid EOF container where the immediate operand of an opcode is
# truncated or terminates the bytecode.
OPCODES_WITH_IMMEDIATE = [
    op for op in V1_EOF_OPCODES if op.immediate_length > 0
]
for op in OPCODES_WITH_IMMEDIATE:
    # No immediate
    INVALID.append(
        Container(
            name=f"truncated_opcode_{op}_no_immediate",
            sections=[Section(kind=Kind.CODE, data=op)],
        ),
    )
    # Immediate minus one
    INVALID.append(
        Container(
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=op + (Op.STOP * (op.immediate_length - 1)),
                )
            ],
            name=f"truncated_opcode_{op}_terminating",
        ),
    )
    # Single byte as immediate
    if op.immediate_length > 1:
        INVALID.append(
            Container(
                name=f"truncated_opcode_{op}_one_byte",
                sections=[Section(kind=Kind.CODE, data=op + Op.STOP)],
            ),
        )


"""
EIP-4750 Valid and Invalid Containers
"""

VALID += [
    Container(
        sections=[Section(kind=Kind.CODE, data="0x00")] * 1024,
        name="max_code_sections_1024",
    ),
    #  Container(
    #      sections=(
    #          [
    #              Section(
    #                  kind=Kind.CODE,
    #                  data="0x00",
    #              )
    #          ]
    #          * 1024
    #      )
    #      + [
    #          Section(
    #              kind=Kind.DATA,
    #              data="0x00",
    #          ),
    #      ],
    #      name="eip_4750_max_code_sections_1024_and_data",
    #  ),
    #  Container(
    #      sections=[
    #          Section(
    #              kind=Kind.CODE,
    #              data="0x00",
    #          ),
    #          Section(
    #              kind=Kind.CODE,
    #              data="0x00",
    #              code_inputs=255,
    #              code_outputs=255,
    #          ),
    #      ],
    #      name="eip_4750_multiple_code_section_max_inputs_max_outputs",
    #  ),
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
]
