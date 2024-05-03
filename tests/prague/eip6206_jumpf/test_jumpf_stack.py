"""
EOF JUMPF tests covering stack validation rules.
"""
import pytest

from ethereum_test_tools import EOFException, EOFTestFiller, StateTestFiller
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import execute_tests
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6206.md"
REFERENCE_SPEC_VERSION = "a1775816657df4093787fb9fe83c2f7cc17ecf47"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "target_inputs",
    [0, 2, 4],
    ids=lambda x: "ti-%d" % x,
)
@pytest.mark.parametrize(
    "stack_height",
    [0, 2, 4],
    ids=lambda x: "h-%d" % x,
)
def test_jumpf_stack_non_returning_rules(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
    target_inputs: int,
    stack_height: int,
):
    """
    Tests for JUMPF validation stack rules.  Non-returning section cases.
    Valid cases are executed.
    """
    container = Container(
        name="stack-non-retuning_h-%d_ti-%d" % (stack_height, target_inputs),
        sections=[
            Section.Code(
                code=Op.JUMPF[1],
                code_outputs=NON_RETURNING_SECTION,
            ),
            Section.Code(
                code=Op.PUSH0 * stack_height + Op.JUMPF[2],
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=stack_height,
            ),
            Section.Code(
                code=Op.POP * target_inputs + Op.SSTORE(0, 1) + Op.STOP,
                code_inputs=target_inputs,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=max(2, target_inputs),
            ),
        ],
    )

    if stack_height < target_inputs:
        container.validity_error = EOFException.UNDEFINED_EXCEPTION

    execute_tests(state_test, eof_test, container)


@pytest.mark.parametrize(
    "current_outputs",
    [0, 2, 4],
    ids=lambda x: "co-%d" % x,
)
@pytest.mark.parametrize(
    "target_outputs",
    [0, 2, 4],
    ids=lambda x: "to-%d" % x,
)
@pytest.mark.parametrize(
    "target_inputs",
    [0, 2, 4],
    ids=lambda x: "to-%d" % x,
)
@pytest.mark.parametrize("stack_diff", [-1, 0, 1], ids=["less-stack", "same-stack", "more-stack"])
def test_jumpf_stack_returning_rules(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
    current_outputs: int,
    target_outputs: int,
    target_inputs: int,
    stack_diff: int,
):
    """
    Tests for JUMPF validation stack rules.  Returning section cases.
    Valid cases are executed.
    """
    if target_outputs > current_outputs:
        # These create invalid containers without JUMPF validation, Don't test.
        return
    if target_inputs == 0 and stack_diff < 0:
        # Code generation is impossible for this configuration.  Don't test.
        return

    target_delta = target_outputs - target_inputs
    container = Container(
        name="stack-retuning_co-%d_to-%d_ti-%d_diff-%d"
        % (current_outputs, target_outputs, target_inputs, stack_diff),
        sections=[
            Section.Code(
                code=Op.CALLF[1] + Op.SSTORE(0, 1) + Op.STOP,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2 + current_outputs,
            ),
            Section.Code(
                code=Op.PUSH0 * max(0, target_inputs + stack_diff) + Op.JUMPF[2],
                code_outputs=current_outputs,
                max_stack_height=target_inputs,
            ),
            Section.Code(
                code=(Op.POP * -target_delta if target_delta < 0 else Op.PUSH0 * target_delta)
                + Op.RETF,
                code_inputs=target_inputs,
                code_outputs=target_outputs,
                max_stack_height=max(target_inputs, target_outputs),
            ),
        ],
    )

    if stack_diff != current_outputs - target_outputs:
        container.validity_error = EOFException.UNDEFINED_EXCEPTION

    execute_tests(state_test, eof_test, container)
