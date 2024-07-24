"""
EOF Classes example use
"""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

from .. import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
            # Check that simple EOF1 deploys
            Container(
                name="EOF1V0001",
                sections=[
                    Section.Code(
                        code=Op.ADDRESS + Op.POP + Op.STOP,
                    ),
                    Section.Data("0xef"),
                ],
            ),
            "ef000101000402000100030400010000800001305000ef",
            None,
            id="simple_eof_1_deploy",
        ),
    ],
)
def test_example_valid_invalid(
    eof_test: EOFTestFiller,
    eof_code: Container,
    expected_hex_bytecode: str,
    exception: EOFException | None,
):
    """
    Verify eof container construction and exception
    """
    # TODO remove this after Container class implementation is reliable
    assert bytes(eof_code).hex() == bytes.fromhex(expected_hex_bytecode).hex()

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )


@pytest.mark.parametrize(
    "skip_header_listing, skip_body_listing, skip_types_body_listing, skip_types_header_listing,"
    "expected_code, expected_exception",
    [
        (
            True,  # second section is not in code header array
            True,  # second section is not in container's body (it's code bytes)
            True,  # it's code input bytes are not listed in container's body (00000000)
            True,  # and it is bytes size is not counted in types header
            "ef0001010004020001000304000400008000013050000bad60a7",
            None,
        ),
    ],
)
def test_code_section_header_body_mismatch(
    eof_test: EOFTestFiller,
    skip_header_listing: bool,
    skip_body_listing: bool,
    skip_types_body_listing: bool,
    skip_types_header_listing: bool,
    expected_code: str,
    expected_exception: EOFException | None,
):
    """
    Inconsistent number of code sections (between types and code)
    """
    eof_code = Container(
        name="EOF1I0018",
        sections=[
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
            ),
            Section.Code(
                code=Op.ADDRESS + Op.POP + Op.STOP,
                code_inputs=0,
                code_outputs=0,
                max_stack_height=0,
                # weather to not mention it in code section header list
                skip_header_listing=skip_header_listing,
                # weather to not print it's code in containers body
                skip_body_listing=skip_body_listing,
                # weather to not print it's input bytes in containers body
                skip_types_body_listing=skip_types_body_listing,
                # weather to not calculate it's input bytes size in types section's header
                skip_types_header_listing=skip_types_header_listing,
            ),
            Section.Data("0x0bad60A7"),
        ],
    )

    # TODO remove this after Container class implementation is reliable
    assert bytes(eof_code).hex() == bytes.fromhex(expected_code).hex()

    eof_test(
        data=eof_code,
        expect_exception=expected_exception,
    )
