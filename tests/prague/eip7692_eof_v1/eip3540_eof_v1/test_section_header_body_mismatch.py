"""
EOF Container construction test
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
    "skip_header_listing, skip_body_listing, skip_types_body_listing, skip_types_header_listing,"
    "expected_code, expected_exception",
    [
        (
            # Data 16 test case of valid invalid eof ori filler
            True,  # second section is not in code header array
            True,  # second section is not in container's body (it's code bytes)
            False,  # but it's code input bytes still listed in container's body
            False,  # but it's code input bytes size still added to types section size
            "ef000101000802000100030400040000800001000000003050000bad60A7",
            EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
        (
            True,  # second section is not in code header array
            False,  # second section code is in container's body (3050000)
            False,  # but it's code input bytes still listed in container's body
            False,  # but it's code input bytes size still added to types section size
            "ef000101000802000100030400040000800001000000003050003050000bad60A7",
            EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
        (
            False,  # second section is mentioned in code header array (0003)
            True,  # second section is not in container's body (it's code bytes)
            False,  # but it's code input bytes still listed in container's body
            False,  # but it's code input bytes size still added to types section size
            "ef0001010008020002000300030400040000800001000000003050000bad60A7",
            EOFException.UNREACHABLE_CODE_SECTIONS,
        ),
        (
            False,  # second section is mentioned in code header array (0003)
            False,  # second section code is in container's body (3050000)
            False,  # but it's code input bytes still listed in container's body
            False,  # but it's code input bytes size still added to types section size
            "ef0001010008020002000300030400040000800001000000003050003050000bad60A7",
            EOFException.UNREACHABLE_CODE_SECTIONS,
        ),
        (
            # Data 17 test case of valid invalid eof ori filler
            True,  # second section is not in code header array
            True,  # second section is not in container's body (it's code bytes)
            True,  # it's code input bytes are not listed in container's body (00000000)
            False,  # but it's code input bytes size still added to types section size
            "ef0001010008020001000304000400008000013050000bad60a7",
            EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
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
