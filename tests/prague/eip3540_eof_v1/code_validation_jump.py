"""
Code validation of RJUMP, RJUMPI, RJUMPV opcodes tests
"""
from typing import List, Tuple

from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1 import SectionKind as Kind
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .constants import MAX_BYTECODE_SIZE, MAX_OPERAND_STACK_HEIGHT, MAX_RJUMPV_COUNT
from .opcodes import V1_EOF_OPCODES

VALID: List[Container] = []
INVALID: List[Container] = []

# Constants

MANY_RJUMP_COUNT = (MAX_BYTECODE_SIZE - 27) // 3
LONG_RJUMP = MAX_BYTECODE_SIZE - 34

VALID_CODE_SECTIONS: List[Tuple[str, Section]] = [
    (
        "long_rjump",
        Section(
            kind=Kind.CODE,
            data=(
                Op.ORIGIN
                + Op.RJUMPI(len(Op.RJUMP))
                + Op.RJUMP(len(Op.NOOP) * LONG_RJUMP)
                + (Op.NOOP * LONG_RJUMP)
                + Op.STOP
            ),
            max_stack_height=1,
        ),
    ),
    (
        "long_rjumpi",
        Section(
            kind=Kind.CODE,
            data=(
                Op.ORIGIN + Op.RJUMPI(len(Op.NOOP) * LONG_RJUMP) + (Op.NOOP * LONG_RJUMP) + Op.STOP
            ),
            max_stack_height=1,
        ),
    ),
    (
        "reachable_code_rjumpi",
        Section(
            kind=Kind.CODE,
            data=(Op.RJUMP(1) + Op.RETF + Op.ORIGIN + Op.RJUMPI(-5) + Op.RETF),
            max_stack_height=1,
        ),
    ),
    (
        "reachable_code_many_rjump",
        Section(
            kind=Kind.CODE,
            data=(
                (Op.RJUMP(len(Op.RJUMP)) * (MANY_RJUMP_COUNT - 1))
                + Op.RJUMP(-(len(Op.RJUMP) * (MANY_RJUMP_COUNT - 1)))
                + Op.STOP
            ),
            max_stack_height=0,
        ),
    ),
    (
        "max_branches_rjumpv_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(MAX_RJUMPV_COUNT, *[i for i in range(MAX_RJUMPV_COUNT)])
            + Op.STOP * MAX_RJUMPV_COUNT,
            max_stack_height=1,
        ),
    ),
    (
        "max_branches_rjumpv_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(MAX_RJUMPV_COUNT, *[i for i in range(1, MAX_RJUMPV_COUNT + 1)])
            + Op.STOP * (MAX_RJUMPV_COUNT + 1),
            max_stack_height=1,
        ),
    ),
    (
        "max_branches_rjumpv_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(MAX_RJUMPV_COUNT, *[i for i in range(MAX_RJUMPV_COUNT)])
            + Op.NOOP * (MAX_RJUMPV_COUNT - 1)
            + Op.STOP,
            max_stack_height=1,
        ),
    ),
]

for name, section in VALID_CODE_SECTIONS:
    # Valid code section as main code section of the container
    if section.code_inputs == 0 and section.code_outputs == 0:
        VALID.append(
            Container(
                name=f"valid_{name}_main_section",
                sections=[section],
            )
        )
    # Valid code section as secondary code section of the container
    VALID.append(
        Container(
            name=f"valid_{name}_secondary_section",
            sections=[
                Section(kind=Kind.CODE, data=Op.STOP),
                section,
            ],
        )
    )


INVALID_CODE_SECTIONS: List[Tuple[str, Section, str]] = [
    # RJUMP unreachable code
    (
        "unreachable_code",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(1) + Op.JUMPDEST + Op.RETF,
            max_stack_height=0,
        ),
        "UnreachableCode",
    ),
    (
        "unreachable_code_2",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(3) + Op.PUSH2(42) + Op.RETF,
            max_stack_height=1,
        ),
        "UnreachableCode",
    ),
    (
        "unreachable_code_3",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(1) + Op.RETF + Op.RJUMP(-4) + Op.RETF,
            max_stack_height=0,
        ),
        "UnreachableCode",
    ),
    (
        "unreachable_code_many_rjump",
        Section(
            kind=Kind.CODE,
            data=(
                (Op.RJUMP(len(Op.RJUMP)) * (MANY_RJUMP_COUNT - 2))
                + Op.RJUMP(-(len(Op.RJUMP) * (MANY_RJUMP_COUNT - 1)))
                + Op.RJUMP(-(len(Op.RJUMP) * (MANY_RJUMP_COUNT - 1)))
                + Op.STOP
            ),
            max_stack_height=0,
        ),
        "UnreachableCode",
    ),
    # RJUMP jumps out of bounds
    (
        "rjump_oob_1",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(-4) + Op.RETF,
            max_stack_height=0,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjump_oob_2",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(1) + Op.RETF,
            max_stack_height=0,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMP jumps to self immediate data
    (
        "rjump_self_immediate_data_1",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(-1) + Op.RETF,
            max_stack_height=0,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjump_self_immediate_data_2",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(-2) + Op.RETF,
            max_stack_height=0,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPI jumps out of bounds
    (
        "rjumpi_oob_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(-5) + Op.RETF,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_oob_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(1) + Op.RETF,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPI jumps to self immediate data
    (
        "rjumpi_self_immediate_data_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(-2) + Op.RETF,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(-1) + Op.RETF,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPV jumps out of bounds
    (
        "rjumpv_oob_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 0),
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpv_oob_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 1) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpv_oob_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 1) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPV jumps to self immediate data
    (
        "rjumpi_self_immediate_data_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, -1) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, -2) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, -3) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_4",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, 0, -5) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_5",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, -5, 0) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_6",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, -5, -1) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_7",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                -(1 + (MAX_RJUMPV_COUNT * 2)),
                *([0] * (MAX_RJUMPV_COUNT - 1)),
            )
            + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_8",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                *([0] * (MAX_RJUMPV_COUNT - 1)),
                -(1 + (MAX_RJUMPV_COUNT * 2)),
            )
            + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPV Invalid Count tests
    (
        "rjumpv_count_zero",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(0) + Op.STOP,
            max_stack_height=1,
        ),
        "InvalidRJUMPVCount",
    ),
    # RJUMPV Truncated Immediate Data
    (
        "rjumpv_count_one_truncated_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1),
            max_stack_height=1,
        ),
        "TruncatedImmediate",
    ),
    (
        "rjumpv_count_one_truncated_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1) + Op.STOP,
            max_stack_height=1,
        ),
        "TruncatedImmediate",
    ),
    (
        "rjumpv_count_one_terminating",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 0),
            max_stack_height=1,
        ),
        "InvalidCodeSectionTerminatingOpcode",
    ),
    (
        "rjumpv_count_two_truncated",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, 0) + Op.STOP,
            max_stack_height=1,
        ),
        "TruncatedImmediate",
    ),
    (
        "rjumpv_count_255_truncated",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(MAX_RJUMPV_COUNT, *([0] * (MAX_RJUMPV_COUNT - 1)))
            + Op.STOP,
            max_stack_height=1,
        ),
        "TruncatedImmediate",
    ),
    # RJUMP* path leads to underflow (before and after the jump)
    (
        "rjump_stack_underflow_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPI(len(Op.RJUMP))
            + Op.RJUMP(-(len(Op.RJUMP) + len(Op.RJUMPI)))
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjump_stack_underflow_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPI(len(Op.RJUMP))
            + Op.RJUMP(len(Op.STOP))
            + Op.STOP
            + Op.POP
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpi_stack_underflow_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(-len(Op.RJUMPI)) + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpi_stack_underflow_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.POP
            + Op.ORIGIN
            + Op.RJUMPI(-(len(Op.RJUMPI) + len(Op.ORIGIN) + len(Op.POP)))
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpi_stack_underflow_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(len(Op.STOP)) + Op.STOP + Op.POP + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpi_stack_underflow_4",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(len(Op.POP)) + Op.POP + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, -len(Op.RJUMPV(0, 0))) + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.POP
            + Op.ORIGIN
            + Op.RJUMPV(1, -(len(Op.RJUMPV(0, 0)) + len(Op.ORIGIN) + len(Op.POP)))
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                *([0] * (MAX_RJUMPV_COUNT - 1)),  # empty branches
                -(len(Op.RJUMPV(*([0] * (MAX_RJUMPV_COUNT + 1))))),  # last one leads to underflow
            )
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_4",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.POP
            + Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                *([0] * (MAX_RJUMPV_COUNT - 1)),  # empty branches
                # last one leads to underflow
                -(len(Op.RJUMPV(*([0] * (MAX_RJUMPV_COUNT + 1)))) + len(Op.ORIGIN) + len(Op.POP)),
            )
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_5",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.POP
            + Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                # first one leads to underflow
                -(len(Op.RJUMPV(*([0] * (MAX_RJUMPV_COUNT + 1)))) + len(Op.ORIGIN) + len(Op.POP)),
                *([0] * (MAX_RJUMPV_COUNT - 1)),  # empty branches
            )
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_6",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.POP
            + Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                *([0] * ((MAX_RJUMPV_COUNT - 1) // 2)),  # empty branches
                # middle one leads to underflow
                -(len(Op.RJUMPV(*([0] * (MAX_RJUMPV_COUNT + 1)))) + len(Op.ORIGIN) + len(Op.POP)),
                *([0] * ((MAX_RJUMPV_COUNT - 1) // 2)),  # empty branches
            )
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_7",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, len(Op.STOP)) + Op.STOP + Op.POP + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_8",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, 0, len(Op.STOP)) + Op.STOP + Op.POP + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_9",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            # last branch underflow
            + Op.RJUMPV(MAX_RJUMPV_COUNT, *([0] * (MAX_RJUMPV_COUNT - 1)), len(Op.STOP))
            + Op.STOP
            + Op.POP
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_10",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            # first branch underflow
            + Op.RJUMPV(MAX_RJUMPV_COUNT, len(Op.STOP), *([0] * (MAX_RJUMPV_COUNT - 1)))
            + Op.STOP
            + Op.POP
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_11",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            # middle branch underflow
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                *([0] * ((MAX_RJUMPV_COUNT - 1) // 2)),
                len(Op.STOP),
                *([0] * ((MAX_RJUMPV_COUNT - 1) // 2)),
            )
            + Op.STOP
            + Op.POP
            + Op.STOP,
            max_stack_height=1,
        ),
        "StackUnderflow",
    ),
    # TODO: RJUMPI/V validation checks all branches even when the input is a
    # known constant (e.g. PUSH0)
]

INVALID_OVERFLOW_CODE_SECTION: List[Tuple[str, Section, str]] = [
    # RJUMP* recursive stack increment
    (
        "rjump_stack_overflow_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPI(len(Op.ORIGIN) + len(Op.RJUMP))
            + Op.ORIGIN
            + Op.RJUMP(-(len(Op.RJUMP) + len(Op.ORIGIN)))
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
    (
        "rjumpi_stack_overflow_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.ORIGIN
            + Op.RJUMPI(-(len(Op.RJUMPI) + (len(Op.ORIGIN) * 2)))
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
    (
        "rjumpv_stack_overflow_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.ORIGIN
            + Op.RJUMPV(
                1,
                -(len(Op.RJUMPV(*([0] * 2))) + (len(Op.ORIGIN) * 2)),
            )
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
    (
        "rjumpv_stack_overflow_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.ORIGIN
            + Op.RJUMPV(
                2,
                0,
                -(len(Op.RJUMPV(*([0] * 3))) + (len(Op.ORIGIN) * 2)),
            )
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
    (
        "rjumpv_stack_overflow_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.ORIGIN
            + Op.RJUMPV(
                2,
                -(len(Op.RJUMPV(*([0] * 3))) + (len(Op.ORIGIN) * 2)),
                0,
            )
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
    (
        "rjumpv_stack_overflow_4",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                *([0] * (MAX_RJUMPV_COUNT - 1)),  # empty branches
                -(len(Op.RJUMPV(*([0] * (MAX_RJUMPV_COUNT + 1)))) + (len(Op.ORIGIN) * 2)),
            )
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
    (
        "rjumpv_stack_overflow_5",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                -(len(Op.RJUMPV(*([0] * (MAX_RJUMPV_COUNT + 1)))) + (len(Op.ORIGIN) * 2)),
                *([0] * (MAX_RJUMPV_COUNT - 1)),  # empty branches
            )
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
    (
        "rjumpv_stack_overflow_6",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.ORIGIN
            + Op.RJUMPV(
                MAX_RJUMPV_COUNT,
                *([0] * ((MAX_RJUMPV_COUNT - 1) // 2)),  # empty branches
                -(len(Op.RJUMPV(*([0] * (MAX_RJUMPV_COUNT + 1)))) + (len(Op.ORIGIN) * 2)),
                *([0] * ((MAX_RJUMPV_COUNT - 1) // 2)),  # empty branches
            )
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
]
MAX_STACK_HEIGHTS = [
    1,
    2,
    MAX_OPERAND_STACK_HEIGHT,
    MAX_OPERAND_STACK_HEIGHT + 1,
]
for name, section, error in INVALID_OVERFLOW_CODE_SECTION:
    for max_stack_height in MAX_STACK_HEIGHTS:
        INVALID_CODE_SECTIONS.append(
            (
                f"{name}_{max_stack_height}",
                section.with_max_stack_height(max_stack_height),
                error,
            )
        )

# Check that rjump cannot jump to the immediate data section of any opcode
OPCODES_WITH_IMMEDIATE = [op for op in V1_EOF_OPCODES if op.data_portion_length > 0]
for op in OPCODES_WITH_IMMEDIATE:
    op_stack_code = Op.ORIGIN * op.min_stack_height
    op_data = bytes([0] * op.data_portion_length)
    opcode_length = 1
    opcode_name = op._name_.lower()
    max_stack_height = op.min_stack_height - op.popped_stack_items + op.pushed_stack_items

    # RJUMP to opcode immediate data appearing earlier in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjump_start_immediate_data_opcode_{opcode_name}_1",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add items to stack necessary to not underflow
                    op_stack_code
                    + op
                    + op_data
                    # Code added to reach end at some point
                    + Op.ORIGIN
                    + Op.RJUMPI(len(Op.RJUMP))
                    # Jump under test
                    + Op.RJUMP(-(len(Op.RJUMP) + len(Op.RJUMPI) + len(Op.ORIGIN) + len(op_data)))
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )
    INVALID_CODE_SECTIONS.append(
        (
            f"rjump_end_immediate_data_opcode_{opcode_name}_1",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add items to stack necessary to not underflow
                    op_stack_code
                    + op
                    + op_data
                    # Code added to reach end at some point
                    + Op.ORIGIN
                    + Op.RJUMPI(len(Op.RJUMP))
                    # Jump under test
                    + Op.RJUMP(-(len(Op.RJUMP) + len(Op.RJUMPI) + len(Op.ORIGIN) + 1))
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )
    # RJUMP to opcode immediate data appearing later in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjump_start_immediate_data_opcode_{opcode_name}_2",
            Section(
                kind=Kind.CODE,
                data=(
                    # Code added to reach end at some point
                    Op.ORIGIN
                    + Op.RJUMPI(len(Op.RJUMP))
                    + Op.RJUMP(len(op_stack_code) + opcode_length)
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    # Jump
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )
    INVALID_CODE_SECTIONS.append(
        (
            f"rjump_end_immediate_data_opcode_{opcode_name}_2",
            Section(
                kind=Kind.CODE,
                data=(
                    # Code added to reach end at some point
                    Op.ORIGIN
                    + Op.RJUMPI(len(Op.RJUMP))
                    + Op.RJUMP(len(op_stack_code) + opcode_length + len(op_data) - 1)
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    # Jump
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )

    # RJUMPI to opcode immediate data appearing earlier in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpi_start_immediate_data_opcode_{opcode_name}_1",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add items to stack necessary to not underflow
                    op_stack_code
                    + op
                    + op_data
                    # Add at least 1 value to stack for RJUMPI
                    + Op.ORIGIN
                    # Jump
                    + Op.RJUMPI(-(len(Op.RJUMPI) + len(Op.ORIGIN) + len(op_data)))
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpi_end_immediate_data_opcode_{opcode_name}_1",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add items to stack necessary to not underflow
                    op_stack_code
                    + op
                    + op_data
                    # Add at least 1 value to stack for RJUMPI
                    + Op.ORIGIN
                    # Jump
                    + Op.RJUMPI(-(len(Op.RJUMPI) + len(Op.ORIGIN) + 1))
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )

    # RJUMPI to opcode immediate data appearing later in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpi_start_immediate_data_opcode_{opcode_name}_2",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add at least 1 value to stack for RJUMPI
                    Op.ORIGIN
                    # Jump
                    + Op.RJUMPI(len(op_stack_code) + opcode_length)
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpi_end_immediate_data_opcode_{opcode_name}_2",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add at least 1 value to stack for RJUMPI
                    Op.ORIGIN
                    # Jump
                    + Op.RJUMPI(len(op_stack_code) + opcode_length + len(op_data) - 1)
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )
    # RJUMPV to opcode immediate data appearing earlier in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpv_start_immediate_data_opcode_{opcode_name}_1",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add items to stack necessary to not underflow
                    op_stack_code
                    + op
                    + op_data
                    # Add at least 1 value to stack for RJUMPV
                    + Op.ORIGIN
                    # Jump
                    + Op.RJUMPV(
                        1,
                        -(len(Op.RJUMPV(0, 0)) + len(Op.ORIGIN) + len(op_data)),
                    )
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpv_end_immediate_data_opcode_{opcode_name}_1",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add items to stack necessary to not underflow
                    op_stack_code
                    + op
                    + op_data
                    # Add at least 1 value to stack for RJUMPV
                    + Op.ORIGIN
                    # Jump
                    + Op.RJUMPV(
                        1,
                        -(len(Op.RJUMPV(0, 0)) + len(Op.ORIGIN) + 1),
                    )
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )

    # RJUMPV to opcode immediate data appearing later in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpv_start_immediate_data_opcode_{opcode_name}_2",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add at least 1 value to stack for RJUMPV
                    Op.ORIGIN
                    # Jump
                    + Op.RJUMPV(
                        1,
                        (len(op_stack_code) + opcode_length),
                    )
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpv_end_immediate_data_opcode_{opcode_name}_2",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add at least 1 value to stack for RJUMPV
                    Op.ORIGIN
                    # Jump
                    + Op.RJUMPV(
                        1,
                        (len(op_stack_code) + opcode_length + len(op_data) - 1),
                    )
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    + Op.STOP
                ),
                max_stack_height=max_stack_height,
            ),
            "InvalidRelativeOffset",
        )
    )

# TODO:
# RJUMPV/RJUMPI path leaves out unreachable code (?)

for name, section, error in INVALID_CODE_SECTIONS:
    # Valid code section as main code section of the container
    if section.code_inputs == 0 and section.code_outputs == 0:
        INVALID.append(
            Container(
                name=f"invalid_{name}_main_section",
                sections=[section],
                validity_error=error,
            )
        )
    # Valid code section as secondary code section of the container
    INVALID.append(
        Container(
            name=f"invalid_{name}_secondary_section",
            sections=[
                Section(kind=Kind.CODE, data=Op.STOP),
                section,
            ],
            validity_error=error,
        )
    )
