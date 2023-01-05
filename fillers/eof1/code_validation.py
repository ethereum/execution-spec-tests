"""
EOF v1 code validation tests
"""

from typing import List

from ethereum_test_tools import Code
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1 import SectionKind as Kind
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .opcodes import (
    INVALID_OPCODES,
    INVALID_TERMINATING_OPCODES,
    V1_EOF_DEPRECATED_OPCODES,
    V1_EOF_OPCODES,
    VALID_TERMINATING_OPCODES,
)

VALID: List[Code | Container] = []
INVALID: List[Code | Container] = []


def make_valid_stack_opcode(op: Op) -> bytes:
    """
    Builds bytecode with the specified op at the end and the proper number of
    stack items to not underflow.
    """
    out = bytes()
    # We need to push some items onto the stack so the code is valid
    # even with stack validation
    out += Op.ORIGIN * op.minimum_stack_height()
    out += op
    return out


# Create containers where each valid terminating opcode is at the end of the
# bytecode.
for op in VALID_TERMINATING_OPCODES:
    # Valid terminating opcode at the end of the section
    VALID.append(
        Container(
            name=f"valid_terminating_opcode_{op._name_}",
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=make_valid_stack_opcode(op),
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=op.minimum_stack_height(),
                ),
            ],
        ),
    )
    # Two valid terminating opcodes in sequence
    # resulting in unreachable code
    INVALID.append(
        Container(
            name=f"unreachable_code_after_opcode_{op._name_}",
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=make_valid_stack_opcode(op) + Op.STOP,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=op.minimum_stack_height(),
                ),
            ],
        ),
    )

# Create containers where each valid non-terminating opcodes is used somewhere
# in the code, with also a valid terminating opcode at the end (STOP).
for op in V1_EOF_OPCODES:
    if op not in VALID_TERMINATING_OPCODES and op != Op.RJUMPV:
        max_stack_height = max(
            op.minimum_stack_height(),
            op.minimum_stack_height()
            - op.popped_stack_items
            + op.pushed_stack_items,
        )
        VALID.append(
            Container(
                name=f"valid_opcode_{op._name_}",
                sections=[
                    Section(
                        kind=Kind.CODE,
                        data=make_valid_stack_opcode(op)
                        + bytes([0x00]) * op.immediate_length
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=0,
                        max_stack_height=max_stack_height,
                    ),
                ],
            ),
        )

# Create containers where each invalid terminating opcode is located at the
# end of the bytecode.
for op in INVALID_TERMINATING_OPCODES:
    max_stack_height = max(
        op.minimum_stack_height(),
        op.minimum_stack_height()
        - op.popped_stack_items
        + op.pushed_stack_items,
    )
    INVALID.append(
        Container(
            name=f"invalid_terminating_opcode_{op._name_}",
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=make_valid_stack_opcode(op),
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=max_stack_height,
                ),
            ],
        ),
    )

# Create containers containing a valid terminating opcode, but a
# invalid opcode somewhere in the bytecode.
for invalid_op_byte in INVALID_OPCODES:
    INVALID.append(
        Container(
            name=f"invalid_opcode_0x{invalid_op_byte.hex()}",
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=invalid_op_byte + Op.STOP,
                ),
            ],
        ),
    )

# Create containers containing a valid terminating opcode, but a
# deprecated opcode somewhere in the bytecode.
# We need to add the proper stack items so the stack validation does not
# produce a false positive.
for op in V1_EOF_DEPRECATED_OPCODES:
    max_stack_height = max(
        op.minimum_stack_height(),
        op.minimum_stack_height()
        - op.popped_stack_items
        + op.pushed_stack_items,
    )
    INVALID.append(
        Container(
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=make_valid_stack_opcode(op) + Op.STOP,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=max_stack_height,
                ),
            ],
            name=f"deprecated_opcode_{op._name_}",
        ),
    )

# Create an invalid EOF container where the immediate operand of an opcode is
# truncated or terminates the bytecode.
# Also add required stack items so we are really testing the immediate length
# check.
OPCODES_WITH_IMMEDIATE = [
    op for op in V1_EOF_OPCODES if op.immediate_length > 0
]
for op in OPCODES_WITH_IMMEDIATE:
    max_stack_height = max(
        op.minimum_stack_height(),
        op.minimum_stack_height()
        - op.popped_stack_items
        + op.pushed_stack_items,
    )
    stack_code = Op.ORIGIN * op.minimum_stack_height()
    # No immediate
    INVALID.append(
        Container(
            name=f"truncated_opcode_{op}_no_immediate",
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=stack_code + op,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=max_stack_height,
                )
            ],
        ),
    )
    # Immediate minus one
    if op.immediate_length > 1:
        INVALID.append(
            Container(
                sections=[
                    Section(
                        kind=Kind.CODE,
                        data=stack_code
                        + op
                        + (Op.STOP * (op.immediate_length - 1)),
                        code_inputs=0,
                        code_outputs=0,
                        max_stack_height=max_stack_height,
                    )
                ],
                name=f"truncated_opcode_{op}_terminating",
            ),
        )
    # Single byte as immediate
    if op.immediate_length > 2:
        INVALID.append(
            Container(
                name=f"truncated_opcode_{op}_one_byte",
                sections=[
                    Section(
                        kind=Kind.CODE,
                        data=stack_code + op + Op.STOP,
                        code_inputs=0,
                        code_outputs=0,
                        max_stack_height=max_stack_height,
                    )
                ],
            ),
        )

# Special cases required for truncated Op.RJUMPV
if Op.RJUMPV in V1_EOF_OPCODES:
    max_stack_height = Op.RJUMPV.minimum_stack_height()
    stack_opcodes = Op.ORIGIN * max_stack_height
    # COUNT=0 truncated
    INVALID.append(
        Container(
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=stack_opcodes + Op.RJUMPV(0),
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=max_stack_height,
                )
            ],
            name="truncated_rjumpv_count_0",
        ),
    )
    # COUNT=1 truncated
    INVALID.append(
        Container(
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=stack_opcodes + Op.RJUMPV(1),
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=max_stack_height,
                )
            ],
            name="truncated_rjumpv_count_1",
        ),
    )
    # COUNT=2 truncated
    INVALID.append(
        Container(
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=stack_opcodes + Op.RJUMPV(2, 0),
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=max_stack_height,
                )
            ],
            name="truncated_rjumpv_count_2",
        ),
    )
    # COUNT=255 truncated
    INVALID.append(
        Container(
            sections=[
                Section(
                    kind=Kind.CODE,
                    data=stack_opcodes + Op.RJUMPV(255, *([0] * 254)),
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=max_stack_height,
                )
            ],
            name="truncated_rjumpv_count_255",
        ),
    )


# Check all opcodes that can underflow the stack
OPCODES_WITH_MINIMUM_STACK_HEIGHT = [
    op for op in V1_EOF_OPCODES if op.minimum_stack_height() > 0
]
for op in OPCODES_WITH_MINIMUM_STACK_HEIGHT:
    underflow_stack_opcodes = Op.ORIGIN * (op.minimum_stack_height() - 1)
    # Test using different max stack heights
    for max_stack_height in [
        op.minimum_stack_height() - 1,
        op.minimum_stack_height(),
    ]:
        if op in VALID_TERMINATING_OPCODES:
            INVALID.append(
                Container(
                    name=f"underflow_stack_opcode_{op}"
                    + f"_max_stack_height_{max_stack_height}",
                    sections=[
                        Section(
                            kind=Kind.CODE,
                            data=underflow_stack_opcodes + op,
                            code_inputs=0,
                            code_outputs=0,
                            max_stack_height=max_stack_height,
                        )
                    ],
                ),
            )
        else:
            INVALID.append(
                Container(
                    name=f"underflow_stack_opcode_{op}"
                    + f"_max_stack_height_{max_stack_height}",
                    sections=[
                        Section(
                            kind=Kind.CODE,
                            data=underflow_stack_opcodes + op + Op.STOP,
                            code_inputs=0,
                            code_outputs=0,
                            max_stack_height=max_stack_height,
                        )
                    ],
                ),
            )

# Check all opcodes that can overflow the stack
OPCODES_WITH_PUSH_STACK_ITEMS = [
    op
    for op in V1_EOF_OPCODES
    if op.pushed_stack_items > op.popped_stack_items
]
for op in OPCODES_WITH_PUSH_STACK_ITEMS:
    pass
