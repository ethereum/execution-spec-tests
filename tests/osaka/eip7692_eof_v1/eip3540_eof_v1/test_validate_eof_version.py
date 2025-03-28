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
            name="invalid_version_0",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0x00,
                    0xFF,
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
            expected_bytecode="ef00ff01000402000100030400040000800000600000aabbccdd",
            validity_error=[EOFException.INVALID_VERSION],
        ),
        Container(
            name="invalid_version_1",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0x00,
                    0x00,
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
            expected_bytecode="ef000001000402000100030400040000800000600000aabbccdd",
            validity_error=[EOFException.INVALID_VERSION],
        ),
        Container(
            name="invalid_version_2",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0x00,
                    0x02,
                ]
            ),
            expected_bytecode="ef0002",
            validity_error=[EOFException.INVALID_VERSION],
        ),
        Container(
            name="invalid_version_3",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0x00,
                    0xFF,
                ]
            ),
            expected_bytecode="ef00ff",
            validity_error=[EOFException.INVALID_VERSION],
        ),
        Container(
            name="invalid_version_4",
            raw_bytes=(
                [
                    # --- Error: Invalid Magic+Version ---#
                    0xEF,
                    0x00,
                    0x02,
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
            expected_bytecode="ef000201000402000100030400040000800000600000aabbccdd",
            validity_error=[EOFException.INVALID_VERSION],
        ),
    ],
    ids=lambda c: c.name,
)
def test_version(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EOF contracts containing invalid version."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
