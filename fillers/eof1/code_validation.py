"""
EOF v1 code validation tests
"""

from typing import List

from ethereum_test_tools import Code
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1 import SectionKind as Kind
from ethereum_test_tools.vm.opcode import Opcode, Opcodes as Op, opcode_map

from .opcodes import (
    INVALID_OPCODES,
    INVALID_TERMINATING_OPCODES,
    V1_EOF_OPCODES,
    VALID_TERMINATING_OPCODES,
)

VALID: List[Code | Container] = []
INVALID: List[Code | Container] = []


def make_valid_terminating_code(op: Op) -> bytes:
    """
    Builds bytecode with the specified op at the end and the proper number of
    stack items to not underflow.
    """
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


def code_to_container(name: str, code: bytes) -> Container:
    """
    Computes the type annotation for code and returns a container with the code as a code section.
    """
    i = 0
    stack_height = 0
    min_stack_height = 0
    max_stack_height = 0

    # compute type annotation
    while i < len(code):
        op = opcode_map.get(code[i])
        if op is None:
            raise Exception("unknown opcode" + hex(code[i]))

        i += 1 + op.immediate_length

        stack_height -= op.popped_stack_items
        min_stack_height = min(stack_height, min_stack_height)
        stack_height += op.pushed_stack_items
        max_stack_height = max(stack_height, max_stack_height)

    return Container(
        name=name,
        sections=[
            Section(kind=Kind.CODE, data=Op.STOP),
            Section(
                kind=Kind.CODE,
                data=code,
                code_inputs=abs(min_stack_height),
                code_outputs=stack_height,
                max_stack_height=max_stack_height,
            ),
        ],
    )


VALID_CODE = [
    (
        "reachable_code_rjumpi",
        Op.RJUMP(1) + Op.RETF + Op.ORIGIN + Op.RJUMPI(-5) + Op.RETF,
    ),
]

for (name, code) in VALID_CODE:
    VALID.append(code_to_container(name, code))

INVALID_CODE = [
    ("unreachable_code", Op.RJUMP(1) + Op.JUMPDEST + Op.RETF),
    ("unreachable_code_2", Op.RJUMP(3) + Op.PUSH2(42) + Op.RETF),
    ("unreachable_code_3", Op.RJUMP(1) + Op.RETF + Op.RJUMP(-4) + Op.RETF),
    ("rjump_oob_1", Op.RJUMP(-4) + Op.RETF),
    ("rjump_oob_2", Op.RJUMP(1) + Op.RETF),
    ("rjumpi_oob_1", Op.PUSH0 + Op.RJUMPI(-5) + Op.RETF),
    ("rjumpi_oob_2", Op.PUSH0 + Op.RJUMPI(1) + Op.RETF),
]

for (name, code) in INVALID_CODE:
    INVALID.append(code_to_container(name, code))
