"""
Code validation of RJUMP, RJUMPI, RJUMPV opcodes tests
"""
from typing import List, Tuple

from ethereum_test_tools import Code
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1 import SectionKind as Kind
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .opcodes import V1_EOF_OPCODES

VALID: List[Code | Container] = []
INVALID: List[Code | Container] = []

MAX_BYTECODE_SIZE = 24576
MANY_RJUMPS = (MAX_BYTECODE_SIZE - 27) // 3

VALID_CODE_SECTIONS: List[Tuple[str, Section]] = [
    (
        "reachable_code_rjumpi",
        Section(
            kind=Kind.CODE,
            data=(Op.RJUMP(1) + Op.RETF + Op.ORIGIN + Op.RJUMPI(-5) + Op.RETF),
        ),
    ),
    (
        # 5c0003 5c0003 5c0003 5c0003 5c0003 5c -15 00
        "reachable_code_many_rjump",
        Section(
            kind=Kind.CODE,
            data=(
                (Op.RJUMP(len(Op.RJUMP)) * (MANY_RJUMPS - 1))
                + Op.RJUMP(-(len(Op.RJUMP) * (MANY_RJUMPS - 1)))
                + Op.STOP
            ),
        ),
    ),
]

for (name, section) in VALID_CODE_SECTIONS:
    # Valid code section as main code section of the container
    section = section.with_auto_max_stack_height()
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
                section.with_auto_code_inputs_outputs(),
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
        ),
        "UnreachableCode",
    ),
    (
        "unreachable_code_2",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(3) + Op.PUSH2(42) + Op.RETF,
        ),
        "UnreachableCode",
    ),
    (
        "unreachable_code_3",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(1) + Op.RETF + Op.RJUMP(-4) + Op.RETF,
        ),
        "UnreachableCode",
    ),
    (
        "unreachable_code_many_rjump",
        Section(
            kind=Kind.CODE,
            data=(
                (Op.RJUMP(len(Op.RJUMP)) * (MANY_RJUMPS - 2))
                + Op.RJUMP(-(len(Op.RJUMP) * (MANY_RJUMPS - 1)))
                + Op.RJUMP(-(len(Op.RJUMP) * (MANY_RJUMPS - 1)))
                + Op.STOP
            ),
        ),
        "UnreachableCode",
    ),
    # RJUMP jumps out of bounds
    (
        "rjump_oob_1",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(-4) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjump_oob_2",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(1) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMP jumps to self immediate data
    (
        "rjump_self_immediate_data_1",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(-1) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjump_self_immediate_data_2",
        Section(
            kind=Kind.CODE,
            data=Op.RJUMP(-2) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPI jumps out of bounds
    (
        "rjumpi_oob_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(-5) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_oob_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(1) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPI jumps to self immediate data
    (
        "rjumpi_self_immediate_data_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(-2) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(-1) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPV jumps out of bounds
    (
        "rjumpv_oob_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 0),
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpv_oob_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 1) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpv_oob_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 1) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPV jumps to self immediate data
    (
        "rjumpi_self_immediate_data_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, -1) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, -2) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, -3) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_4",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, 0, -5) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_5",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, -5, 0) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_6",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, -5, -1) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_7",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(255, -(1 + (255 * 2)), *([0] * 254))
            + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_8",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(255, *([0] * 254), -(1 + (255 * 2)))
            + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
    # RJUMPV Invalid Count tests
    (
        "rjumpv_count_zero",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(0) + Op.STOP,
        ),
        "InvalidRJUMPVCount",
    ),
    # RJUMPV Truncated Immediate Data
    (
        "rjumpv_count_one_truncated_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1),
        ),
        "TruncatedImmediate",
    ),
    (
        "rjumpv_count_one_truncated_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1) + Op.STOP,
        ),
        "TruncatedImmediate",
    ),
    (
        "rjumpv_count_one_terminating",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 0),
        ),
        "InvalidCodeSectionTerminatingOpcode",
    ),
    (
        "rjumpv_count_two_truncated",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(2, 0) + Op.STOP,
        ),
        "TruncatedImmediate",
    ),
    (
        "rjumpv_count_255_truncated",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(255, *([0] * 254)) + Op.STOP,
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
        ),
        "StackUnderflow",
    ),
    (
        "rjumpi_stack_underflow_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(-len(Op.RJUMPI)) + Op.STOP,
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
        ),
        "StackUnderflow",
    ),
    (
        "rjumpi_stack_underflow_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPI(len(Op.STOP))
            + Op.STOP
            + Op.POP
            + Op.STOP,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpi_stack_underflow_4",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPI(len(Op.POP)) + Op.POP + Op.STOP,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_1",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, -len(Op.RJUMPV(0, 0))) + Op.STOP,
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
            + Op.RJUMPV(
                1, -(len(Op.RJUMPV(0, 0)) + len(Op.ORIGIN) + len(Op.POP))
            )
            + Op.STOP,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_3",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(
                255,
                *([0] * 254),  # 254 empty branches
                -(len(Op.RJUMPV(*([0] * 256)))),  # last one leads to underflow
            )
            + Op.STOP,
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
                255,
                *([0] * 254),  # 254 empty branches
                # last one leads to underflow
                -(len(Op.RJUMPV(*([0] * 256))) + len(Op.ORIGIN) + len(Op.POP)),
            )
            + Op.STOP,
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
                255,
                # first one leads to underflow
                -(len(Op.RJUMPV(*([0] * 256))) + len(Op.ORIGIN) + len(Op.POP)),
                *([0] * 254),  # 254 empty branches
            )
            + Op.STOP,
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
                255,
                *([0] * 127),  # 127 empty branches
                # middle one leads to underflow
                -(len(Op.RJUMPV(*([0] * 256))) + len(Op.ORIGIN) + len(Op.POP)),
                *([0] * 127),  # 127 empty branches
            )
            + Op.STOP,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_7",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(1, len(Op.STOP))
            + Op.STOP
            + Op.POP
            + Op.STOP,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_8",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(2, 0, len(Op.STOP))
            + Op.STOP
            + Op.POP
            + Op.STOP,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_9",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(255, *([0] * 254), len(Op.STOP))  # last branch underfl
            + Op.STOP
            + Op.POP
            + Op.STOP,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_10",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            + Op.RJUMPV(255, len(Op.STOP), *([0] * 254))  # 1st branch underfl
            + Op.STOP
            + Op.POP
            + Op.STOP,
        ),
        "StackUnderflow",
    ),
    (
        "rjumpv_stack_underflow_11",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN
            # middle branch underflow
            + Op.RJUMPV(255, *([0] * 127), len(Op.STOP), *([0] * 127))
            + Op.STOP
            + Op.POP
            + Op.STOP,
        ),
        "StackUnderflow",
    ),
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
                255,
                *([0] * 254),  # 254 empty branches
                -(len(Op.RJUMPV(*([0] * 256))) + (len(Op.ORIGIN) * 2)),
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
                255,
                -(len(Op.RJUMPV(*([0] * 256))) + (len(Op.ORIGIN) * 2)),
                *([0] * 254),  # 254 empty branches
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
                255,
                *([0] * 127),  # 127 empty branches
                -(len(Op.RJUMPV(*([0] * 256))) + (len(Op.ORIGIN) * 2)),
                *([0] * 127),  # 127 empty branches
            )
            + Op.STOP,
        ),
        "InvalidControlFlow",
    ),
    # TODO: RJUMPI/V validation checks all branches even when the input is a
    # known constant (e.g. PUSH0)
]

# Check that rjump cannot jump to the immediate data section of any opcode
OPCODES_WITH_IMMEDIATE = [
    op for op in V1_EOF_OPCODES if op.immediate_length > 0
]
for op in OPCODES_WITH_IMMEDIATE:
    op_stack_code = Op.ORIGIN * op.minimum_stack_height()
    op_data = bytes([0] * op.immediate_length)
    opcode_length = 1
    opcode_name = op._name_.lower()

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
                    + Op.RJUMP(
                        -(
                            len(Op.RJUMP)
                            + len(Op.RJUMPI)
                            + len(Op.ORIGIN)
                            + len(op_data)
                        )
                    )
                    + Op.STOP
                ),
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
                    + Op.RJUMP(
                        -(len(Op.RJUMP) + len(Op.RJUMPI) + len(Op.ORIGIN) + 1)
                    )
                    + Op.STOP
                ),
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
                    + Op.RJUMP(
                        len(op_stack_code) + opcode_length + len(op_data) - 1
                    )
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    # Jump
                    + Op.STOP
                ),
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
                    + Op.RJUMPI(
                        -(len(Op.RJUMPI) + len(Op.ORIGIN) + len(op_data))
                    )
                    + Op.STOP
                ),
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
                    + Op.RJUMPI(
                        len(op_stack_code) + opcode_length + len(op_data) - 1
                    )
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    + Op.STOP
                ),
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
                        -(
                            len(Op.RJUMPV(0, 0))
                            + len(Op.ORIGIN)
                            + len(op_data)
                        ),
                    )
                    + Op.STOP
                ),
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
                        (
                            len(op_stack_code)
                            + opcode_length
                            + len(op_data)
                            - 1
                        ),
                    )
                    # Add items to stack necessary to not underflow
                    + op_stack_code
                    + op
                    + op_data
                    + Op.STOP
                ),
            ),
            "InvalidRelativeOffset",
        )
    )

# TODO:
# RJUMPV/RJUMPI path leaves out unreachable code (?)

for (name, section, error) in INVALID_CODE_SECTIONS:
    # Valid code section as main code section of the container
    section = section.with_auto_max_stack_height()
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
                section.with_auto_code_inputs_outputs(),
            ],
            validity_error=error,
        )
    )
