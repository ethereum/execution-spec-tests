"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools.eof.v1 import Container

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="invalid_prefix_0",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0xFF,
                    0x01,
                    0x01,
                    0x00,
                    0x04,
                    0x02,
                    0x00,
                    0x01,
                    0x00,
                    0x03,
                    0x04,
                    0x00,
                    0x04,
                    0x00,
                    0x00,
                    0x80,
                    0x00,
                    0x00,
                    0x60,
                    0x00,
                    0x00,
                    0xAA,
                    0xBB,
                    0xCC,
                    0xDD,
                ]
            ),
            expected_bytecode="efff0101000402000100030400040000800000600000aabbccdd",
            validity_error=[EOFException.INVALID_MAGIC],
        ),
        Container(
            name="invalid_prefix_1",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0x00,
                ]
            ),
            expected_bytecode="00",
            validity_error=[EOFException.INVALID_MAGIC],
        ),
        Container(
            name="invalid_prefix_2",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xFE,
                ]
            ),
            expected_bytecode="fe",
            validity_error=[EOFException.INVALID_MAGIC],
        ),
        Container(
            name="invalid_prefix_3",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0x01,
                    0x01,
                ]
            ),
            expected_bytecode="ef0101",
            validity_error=[EOFException.INVALID_MAGIC],
        ),
        Container(
            name="invalid_prefix_4",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0xEF,
                    0x01,
                ]
            ),
            expected_bytecode="efef01",
            validity_error=[EOFException.INVALID_MAGIC],
        ),
        Container(
            name="invalid_prefix_5",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0xFF,
                    0x01,
                ]
            ),
            expected_bytecode="efff01",
            validity_error=[EOFException.INVALID_MAGIC],
        ),
    ],
    ids=lambda c: c.name,
)
def test_prefix(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test bytecode containing invalid prefix."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
