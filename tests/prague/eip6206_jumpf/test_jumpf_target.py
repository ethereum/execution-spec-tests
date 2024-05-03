"""
EOF JUMPF tests covering JUMPF target rules.
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
    "target_outputs",
    [NON_RETURNING_SECTION, 0, 2, 4],
    ids=lambda x: "to-%s" % ("N" if x == NON_RETURNING_SECTION else x),
)
@pytest.mark.parametrize(
    "current_outputs",
    [NON_RETURNING_SECTION, 0, 2, 4],
    ids=lambda x: "co-%s" % ("N" if x == NON_RETURNING_SECTION else x),
)
def test_jumpf_target_rules(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
    current_outputs: int,
    target_outputs: int,
):
    """
    Validate the target section rules of JUMPF, and execute valid cases.
    We are not testing stack so a lot of the logic is to get correct stack values.
    """
    current_non_returning = current_outputs == NON_RETURNING_SECTION
    current_height = 0 if current_non_returning else current_outputs

    target_non_returning = target_outputs == NON_RETURNING_SECTION
    target_height = 0 if target_non_returning else target_outputs

    delta = 0 if target_non_returning or current_non_returning else target_outputs - current_height
    current_extra_push = max(0, current_height - target_height)

    current_section = Section.Code(
        code=Op.PUSH0 * (current_height)
        + Op.CALLDATALOAD(0)
        + Op.RJUMPI[1]
        + (Op.STOP if current_non_returning else Op.RETF)
        + Op.PUSH0 * current_extra_push
        + Op.JUMPF[2],
        code_inputs=0,
        code_outputs=current_outputs,
        max_stack_height=current_height + max(1, current_extra_push),
    )
    target_section = Section.Code(
        code=((Op.PUSH0 * delta) if delta >= 0 else (Op.POP * -delta))
        + Op.CALLF[3]
        + (Op.STOP if target_non_returning else Op.RETF),
        code_inputs=current_height,
        code_outputs=target_outputs,
        max_stack_height=max(current_height, current_height + delta),
    )

    base_code = bytes(Op.JUMPF[1]) if current_non_returning else (Op.CALLF[1](0, 0) + Op.STOP)
    base_height = 0 if current_non_returning else 2 + current_outputs
    container = Container(
        name="target_co-%s_to-%s"
        % (
            "N" if current_non_returning else current_outputs,
            "N" if target_non_returning else target_outputs,
        ),
        sections=[
            Section.Code(
                code=base_code,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=base_height,
            ),
            current_section,
            target_section,
            Section.Code(
                code=Op.SSTORE(0, 1) + Op.RETF,
                code_inputs=0,
                code_outputs=0,
                max_stack_height=2,
            ),
        ],
    )

    if not target_non_returning and current_non_returning or current_outputs < target_outputs:
        # both as non-returning handled above
        container.validity_error = EOFException.UNDEFINED_EXCEPTION

    execute_tests(state_test, eof_test, container)
