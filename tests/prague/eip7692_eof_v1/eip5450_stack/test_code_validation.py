"""
Code validation of CALLF, JUMPF, RETF opcodes in conjunction with static relative jumps
"""

import itertools
from enum import Enum, auto, unique
from typing import Tuple

import pytest

from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_vm.bytecode import Bytecode

from .. import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "f20b164b00ae5553f7536a6d7a83a0f254455e09"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@unique
class RjumpKind(Enum):
    """
    Kinds of RJUMP* instruction snippets to generate.
    """

    EMPTY_RJUMP = auto()
    EMPTY_RJUMPI = auto()
    RJUMPI_OVER_PUSH = auto()
    RJUMPI_OVER_NOOP = auto()
    RJUMPI_OVER_STOP = auto()
    RJUMPI_OVER_PUSH_POP = auto()
    RJUMPI_OVER_POP = auto()
    RJUMPI_OVER_NEXT = auto()
    RJUMPI_OVER_NEXT_NESTED = auto()
    RJUMPI_TO_START = auto()
    RJUMPV_EMPTY_AND_OVER_NEXT = auto()
    RJUMPV_OVER_PUSH_AND_TO_START = auto()

    def __str__(self) -> str:
        """
        Returns the string representation of the enum
        """
        return f"{self.name}"


@unique
class RjumpSpot(Enum):
    """
    Possible spots in the code section layout where the RJUMP* is injected
    """

    BEGINNING = auto()
    BEFORE_TERMINATION = auto()

    def __str__(self) -> str:
        """
        Returns the string representation of the enum
        """
        return f"{self.name}"


def rjump_code_with(
    rjump_kind: RjumpKind | None, code_so_far_len: int, next_code_len: int
) -> Bytecode:
    """
    Unless `rjump_kind` is None generates a code snippet with an RJUMP* instruction.
    For some kinds `code_so_far_len` must be code length in bytes preceeding the snippet.
    For some kinds `next_code_len` must be code length in bytes of some code which follows.

    It is expected that the snippet and the jump target are valid, but the resulting code
    or its stack balance might not.
    """
    body = Bytecode()

    if rjump_kind == RjumpKind.EMPTY_RJUMP:
        body = Op.RJUMP[0]
    elif rjump_kind == RjumpKind.EMPTY_RJUMPI:
        body = Op.RJUMPI[0](1)
    elif rjump_kind == RjumpKind.RJUMPI_OVER_PUSH:
        body = Op.RJUMPI[1](0) + Op.PUSH0
    elif rjump_kind == RjumpKind.RJUMPI_OVER_NOOP:
        body = Op.RJUMPI[1](0) + Op.NOOP
    elif rjump_kind == RjumpKind.RJUMPI_OVER_STOP:
        body = Op.RJUMPI[1](0) + Op.STOP
    elif rjump_kind == RjumpKind.RJUMPI_OVER_PUSH_POP:
        body = Op.RJUMPI[2](0) + Op.PUSH0 + Op.POP
    elif rjump_kind == RjumpKind.RJUMPI_OVER_POP:
        body = Op.RJUMPI[1](0) + Op.POP + Op.PUSH0
    elif rjump_kind == RjumpKind.RJUMPI_OVER_NEXT:
        body = Op.RJUMPI[next_code_len](0)
    elif rjump_kind == RjumpKind.RJUMPI_OVER_NEXT_NESTED:
        rjump_inner = Op.RJUMPI[next_code_len](0)
        body = Op.RJUMPI[len(rjump_inner)](0) + rjump_inner
    elif rjump_kind == RjumpKind.RJUMPI_TO_START:
        rjumpi_len = len(Op.RJUMPI[0](0))
        body = Op.RJUMPI[-code_so_far_len - rjumpi_len](0)
    elif rjump_kind == RjumpKind.RJUMPV_EMPTY_AND_OVER_NEXT:
        body = Op.RJUMPV[[0, next_code_len]](0)
    elif rjump_kind == RjumpKind.RJUMPV_OVER_PUSH_AND_TO_START:
        rjumpv_two_destinations_len = len(Op.RJUMPV[[0, 0]](0))
        body = Op.RJUMPV[[1, -code_so_far_len - rjumpv_two_destinations_len]](0) + Op.PUSH0
    elif not rjump_kind:
        pass
    else:
        raise TypeError("unknown rjumps value" + str(rjump_kind))

    return body


def call_code_with(inputs, outputs, call: Bytecode) -> Bytecode:
    """
    Generates a code snippet with the `call` bytecode provided and its respective input/output
    management.

    `inputs` and `outputs` are understood as those of the code section we're generating for.
    """
    body = Bytecode()

    if call.popped_stack_items > inputs:
        body += Op.PUSH0 * (call.popped_stack_items - inputs)
    elif call.popped_stack_items < inputs:
        body += Op.POP * (inputs - call.popped_stack_items)

    body += call
    if call.pushed_stack_items < outputs:
        body += Op.PUSH0 * (outputs - call.pushed_stack_items)
    elif call.pushed_stack_items > outputs:
        body += Op.POP * (call.pushed_stack_items - outputs)

    return body


def section_code_with(
    inputs: int,
    outputs: int,
    rjump_kind: RjumpKind | None,
    rjump_spot: RjumpSpot,
    call: Bytecode | None,
    termination: Bytecode,
) -> Bytecode:
    """
    Generates a code section with RJUMP* and CALLF/RETF instructions.
    """
    code = Bytecode(min_stack_height=inputs, max_stack_height=inputs)

    if call:
        body = call_code_with(inputs, outputs, call)
    else:
        body = Op.POP * inputs + Op.PUSH0 * outputs

    if rjump_spot == RjumpSpot.BEGINNING:
        code += rjump_code_with(rjump_kind, 0, len(body))

    code += body

    if rjump_spot == RjumpSpot.BEFORE_TERMINATION:
        # next_code_len=0 avoids jumping over the termination which never validates
        code += rjump_code_with(rjump_kind, len(code), next_code_len=0)

    code += termination

    return code


num_sections = 3
possible_inputs_outputs = range(2)


@pytest.mark.parametrize(
    ["inputs", "outputs"],
    itertools.product(
        list(itertools.product(*([possible_inputs_outputs] * (num_sections - 1)))),
        list(itertools.product(*([possible_inputs_outputs] * (num_sections - 1)))),
    ),
)
@pytest.mark.parametrize(
    "rjump_kind",
    RjumpKind.__members__.values(),
)
# Parameter value fixed for first iteration, to cover the most important case.
@pytest.mark.parametrize("rjump_section_idx", [1])
@pytest.mark.parametrize(
    "rjump_spot",
    RjumpSpot.__members__.values(),
)
def test_eof_validity(
    eof_test: EOFTestFiller,
    inputs: Tuple[int, ...],
    outputs: Tuple[int, ...],
    rjump_kind: RjumpKind,
    rjump_section_idx: int,
    rjump_spot: RjumpSpot,
):
    """
    Test EOF container validaiton for EIP-4200 vs EIP-4750 interactions.

    Each test's code consists of `num_sections` code sections, which call into one another
    and then return. Code may include RJUMP* snippets of `rjump_kind` in various `rjump_spots`.
    """
    # Zeroth section has always 0 inputs and 0 outputs, so is excluded from param
    inputs = (0,) + inputs
    outputs = (0,) + outputs

    assert len(inputs) == len(outputs) == num_sections

    sections = []
    for section_idx in range(num_sections):
        if section_idx == 0:
            call = Op.CALLF[section_idx + 1]
            call.popped_stack_items = inputs[section_idx + 1]
            call.pushed_stack_items = outputs[section_idx + 1]
            call.min_stack_height = call.popped_stack_items
            call.max_stack_height = max(call.popped_stack_items, call.pushed_stack_items)
            termination = Op.STOP
        elif section_idx < num_sections - 1:
            call = Op.CALLF[section_idx + 1]
            call.popped_stack_items = inputs[section_idx + 1]
            call.pushed_stack_items = outputs[section_idx + 1]
            call.min_stack_height = call.popped_stack_items
            call.max_stack_height = max(call.popped_stack_items, call.pushed_stack_items)
            termination = Op.RETF
        else:
            call = None
            termination = Op.RETF

        code = section_code_with(
            inputs[section_idx],
            outputs[section_idx],
            rjump_kind if rjump_section_idx == section_idx else None,
            rjump_spot,
            call,
            termination,
        )
        if section_idx > 0:
            sections.append(
                Section.Code(
                    code,
                    code_inputs=inputs[section_idx],
                    code_outputs=outputs[section_idx],
                )
            )
        else:
            sections.append(Section.Code(code))
    eof_test(
        data=bytes(Container(sections=sections)),
        # `empty_rjump` acts as a sanity check, it is completely stack-neutral so
        # should always validate.`
    )
