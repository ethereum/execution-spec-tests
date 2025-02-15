"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_types.eof.v1.constants import MAX_INITCODE_SIZE

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "52ddbcdddcf72dd72427c319f2beddeb468e1737"


# Maximum nested containers EOFCREATE/RETURNCONTRACT
code = None
nextcode = Container(
    name="EOFV1_MINCONTAINER_0",
    sections=[
        Section.Code(code=Op.INVALID),
    ],
)

c = 0
while len(nextcode) < MAX_INITCODE_SIZE:
    next_name = f"EOFV1_MINCONTAINER_{c + 1}"
    init_name = f"EOFV1_INITCONTAINER_{c}"
    code = nextcode
    initcode = Container(
        name=init_name,
        sections=[
            Section.Code(code=Op.PUSH0 * 2 + Op.RETURNCONTRACT[0]),
            Section.Container(container=nextcode),
        ],
    )
    if len(initcode) > 0xFFFF:
        break
    nextcode = Container(
        name=next_name,
        sections=[
            Section.Code(code=Op.PUSH0 * 4 + Op.EOFCREATE[0] + Op.INVALID),
            Section.Container(container=initcode),
        ],
    )
    c += 1

max_nested_containers_eofcreate_returncontract_0 = code


@pytest.mark.parametrize(
    "container",
    [
        max_nested_containers_eofcreate_returncontract_0,
    ],
    ids=lambda c: c.name,
)
def test_max_nested_containers_eofcreate_returncontract(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test the maximum number of nested containers combining EOFCREATE and RETURNCONTRACT."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
