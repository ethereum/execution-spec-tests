"""
Code validation of RJUMP, RJUMPI, RJUMPV opcodes tests
"""
from typing import List

from ethereum_test_tools import Code
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1 import SectionKind as Kind
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_tools.vm.opcode import opcode_map

VALID: List[Code | Container] = []
INVALID: List[Code | Container] = []


def code_to_container(name: str, code: bytes) -> Container:
    """
    Computes the type annotation for code and returns a container with the code
    as a code section.
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
        elif op == Op.RJUMPV:
            i += 1
            if i < len(code):
                count = code[i]
                i += count * 2
        else:
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


# TODO:
# RJUMPV count is not zero
# RJUMPV is not truncated
# RJUMPV jumps out of bounds
# RJUMPV path leads to underflow
# RJUMPV path leads to recursion
# RJUMPV path leaves out unreachable code
# RJUMP does not jump to immediate data of some other opcode
