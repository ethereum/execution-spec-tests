"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, ContainerKind, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "f20b164b00ae5553f7536a6d7a83a0f254455e09"


# Invalid 1024 RJUMPIs
rjumpis_1023 = Op.STOP()
offset = 1
for _ in range(0, 1023):
    rjumpis_1023 = Op.PUSH0 + Op.RJUMPI[offset] + Op.PUSH0 + rjumpis_1023
    offset += 5

rjumpis_1024 = Op.PUSH0 + Op.RJUMPI[offset] + Op.PUSH0 + rjumpis_1023

invalid_1024_rjumpis = Container(
    name="invalid_1024_rjumpis",
    sections=[
        Section.Code(code=rjumpis_1024, max_stack_height=1023),
    ],
    kind=ContainerKind.RUNTIME,
    validity_error=[
        EOFException.INVALID_MAX_STACK_HEIGHT,
    ],
)
# Construct series of RJUMPIs all targeting final STOP
# Stack range at STOP is [0, 1023]
valid_1023_rjumpis = Container(
    name="valid_1023_rjumpis",
    sections=[
        Section.Code(code=rjumpis_1023, max_stack_height=1023),
    ],
    kind=ContainerKind.RUNTIME,
)


@pytest.mark.parametrize(
    "container",
    [
        invalid_1024_rjumpis,
        valid_1023_rjumpis,
    ],
    ids=lambda c: c.name,
)
def test_stack_range_maximally_broad(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test stack range maximally broad."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
