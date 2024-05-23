"""
EOF JUMPF tests covering simple cases.
"""
import pytest

from ethereum_test_tools import EOFException, EOFTestFiller, StateTestFiller
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import execute_tests, slot_code_worked, value_code_worked
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6206.md"
REFERENCE_SPEC_VERSION = "a1775816657df4093787fb9fe83c2f7cc17ecf47"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


def test_jumpf_forward(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
):
    """Test JUMPF jumping forward"""
    execute_tests(
        state_test,
        eof_test,
        Container(
            sections=[
                Section.Code(
                    code=Op.JUMPF[1],
                    code_outputs=NON_RETURNING_SECTION,
                ),
                Section.Code(
                    Op.SSTORE(slot_code_worked, value_code_worked) + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                ),
            ],
        ),
    )


def test_jumpf_backward(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
):
    """Tests JUMPF jumping backward"""
    execute_tests(
        state_test,
        eof_test,
        Container(
            sections=[
                Section.Code(
                    code=Op.CALLF[2] + Op.SSTORE(slot_code_worked, value_code_worked) + Op.STOP,
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.RETF,
                ),
                Section.Code(
                    code=Op.JUMPF[1],
                ),
            ],
        ),
    )


def test_jumpf_to_self(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
):
    """Tests JUMPF jumping to self"""
    execute_tests(
        state_test,
        eof_test,
        Container(
            sections=[
                Section.Code(
                    code=Op.SLOAD(slot_code_worked)
                    + Op.ISZERO
                    + Op.RJUMPI[1]
                    + Op.STOP
                    + Op.SSTORE(slot_code_worked, value_code_worked)
                    + Op.JUMPF[0],
                    code_outputs=NON_RETURNING_SECTION,
                    max_stack_height=2,
                )
            ],
        ),
    )


def test_jumpf_too_large(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
):
    """Tests JUMPF jumping to a section outside the max section range"""
    execute_tests(
        state_test,
        eof_test,
        Container(
            sections=[
                Section.Code(
                    code=Op.JUMPF[1025],
                    code_outputs=NON_RETURNING_SECTION,
                )
            ],
            validity_error=EOFException.UNDEFINED_EXCEPTION,
        ),
    )


def test_jumpf_way_too_large(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
):
    """Tests JUMPF jumping to uint64.MAX"""
    execute_tests(
        state_test,
        eof_test,
        Container(
            sections=[
                Section.Code(
                    code=Op.JUMPF[0xFFFF],
                    code_outputs=NON_RETURNING_SECTION,
                )
            ],
            validity_error=EOFException.UNDEFINED_EXCEPTION,
        ),
    )


def test_jumpf_to_nonexistent_section(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
):
    """Tests JUMPF jumping to valid section number but where the section does not exist"""
    execute_tests(
        state_test,
        eof_test,
        Container(
            sections=[
                Section.Code(
                    code=Op.JUMPF[5],
                    code_outputs=NON_RETURNING_SECTION,
                )
            ],
            validity_error=EOFException.UNDEFINED_EXCEPTION,
        ),
    )


def test_callf_to_non_returning_section(
    state_test: StateTestFiller,
    eof_test: EOFTestFiller,
):
    """Tests CALLF into a non-returning section"""
    execute_tests(
        state_test,
        eof_test,
        Container(
            sections=[
                Section.Code(
                    code=Op.CALLF[1],
                    code_outputs=NON_RETURNING_SECTION,
                ),
                Section.Code(
                    code=Op.STOP,
                    outputs=NON_RETURNING_SECTION,
                ),
            ],
            validity_error=EOFException.UNDEFINED_EXCEPTION,
        ),
    )
