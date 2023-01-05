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


VALID_CODE_SECTIONS: List[Tuple[str, Section]] = [
    (
        "reachable_code_rjumpi",
        Section(
            kind=Kind.CODE,
            data=(Op.RJUMP(1) + Op.RETF + Op.ORIGIN + Op.RJUMPI(-5) + Op.RETF),
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
    (
        "rjumpi_oob_1",
        Section(
            kind=Kind.CODE,
            data=Op.PUSH0 + Op.RJUMPI(-5) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_oob_2",
        Section(
            kind=Kind.CODE,
            data=Op.PUSH0 + Op.RJUMPI(1) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_1",
        Section(
            kind=Kind.CODE,
            data=Op.PUSH0 + Op.RJUMPI(-2) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
    (
        "rjumpi_self_immediate_data_2",
        Section(
            kind=Kind.CODE,
            data=Op.PUSH0 + Op.RJUMPI(-1) + Op.RETF,
        ),
        "InvalidRelativeOffset",
    ),
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
        "rjumpv_oob_2",
        Section(
            kind=Kind.CODE,
            data=Op.ORIGIN + Op.RJUMPV(1, 1) + Op.STOP,
        ),
        "InvalidRelativeOffset",
    ),
]

# Check that rjump cannot jump to the immediate data section of any opcode
OPCODES_WITH_IMMEDIATE = [
    op for op in V1_EOF_OPCODES if op.immediate_length > 0
]
for op in OPCODES_WITH_IMMEDIATE:
    op_stack_code = Op.ORIGIN * op.minimum_stack_height()
    op_data = bytes([0] * op.immediate_length)
    opcode_length = 1

    # RJUMP to opcode immediate data of opcode appearing earlier in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjump_start_immediate_data_opcode_{op._name_}_1",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add items to stack necessary to not underflow
                    op_stack_code
                    + op
                    + op_data
                    # Code added to reach end at some point
                    + Op.ORIGIN
                    + Op.RJUMPI(len(Op.RJUMP(0)))
                    # Jump under test
                    + Op.RJUMP(
                        -(
                            len(Op.RJUMP(0))
                            + len(Op.RJUMPI(0))
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
            f"rjump_end_immediate_data_opcode_{op._name_}_1",
            Section(
                kind=Kind.CODE,
                data=(
                    # Add items to stack necessary to not underflow
                    op_stack_code
                    + op
                    + op_data
                    # Code added to reach end at some point
                    + Op.ORIGIN
                    + Op.RJUMPI(len(Op.RJUMP(0)))
                    # Jump under test
                    + Op.RJUMP(
                        -(
                            len(Op.RJUMP(0))
                            + len(Op.RJUMPI(0))
                            + len(Op.ORIGIN)
                            + 1
                        )
                    )
                    + Op.STOP
                ),
            ),
            "InvalidRelativeOffset",
        )
    )
    # RJUMP to opcode immediate data of opcode appearing later in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjump_start_immediate_data_opcode_{op._name_}_2",
            Section(
                kind=Kind.CODE,
                data=(
                    # Code added to reach end at some point
                    Op.ORIGIN
                    + Op.RJUMPI(len(Op.RJUMP(0)))
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
            f"rjump_end_immediate_data_opcode_{op._name_}_2",
            Section(
                kind=Kind.CODE,
                data=(
                    # Code added to reach end at some point
                    Op.ORIGIN
                    + Op.RJUMPI(len(Op.RJUMP(0)))
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

    # RJUMPI to opcode immediate data of opcode appearing earlier in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpi_start_immediate_data_opcode_{op._name_}_1",
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
                        -(len(Op.RJUMPI(0)) + len(Op.ORIGIN) + len(op_data))
                    )
                    + Op.STOP
                ),
            ),
            "InvalidRelativeOffset",
        )
    )
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpi_end_immediate_data_opcode_{op._name_}_1",
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
                    + Op.RJUMPI(-(len(Op.RJUMPI(0)) + len(Op.ORIGIN) + 1))
                    + Op.STOP
                ),
            ),
            "InvalidRelativeOffset",
        )
    )

    # RJUMPI to opcode immediate data of opcode appearing later in code
    INVALID_CODE_SECTIONS.append(
        (
            f"rjumpi_start_immediate_data_opcode_{op._name_}_2",
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
            f"rjumpi_end_immediate_data_opcode_{op._name_}_2",
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

# TODO:
# RJUMPV count is not zero
# RJUMPV is not truncated
# RJUMPV jumps out of bounds
# RJUMPV path leads to underflow
# RJUMPV path leads to recursion
# RJUMPV path leaves out unreachable code
# RJUMPV path leads to opcode immediate data
# RJUMP does not jump to immediate data of self
# RJUMP does not jump to immediate data of some other opcode before the RJUMP
# RJUMP does not jump to immediate data of some other opcode after the RJUMP

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
