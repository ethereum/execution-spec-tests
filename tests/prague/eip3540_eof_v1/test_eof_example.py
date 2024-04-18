"""
EOF Classes example use
"""

import pytest

from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools.eof.v1 import AutoSection, Container, Section, SectionKind

from .constants import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


def test_eof_example(eof_test: EOFTestFiller):
    """
    Example of PYSPECs EOF classes
    """

    # Lets construct an EOF container code
    eof_code = Container(
        name="valid_container_example",
        sections=[
            # TYPES section is constructed automatically based on CODE
            # CODE section
            Section(
                kind=SectionKind.CODE,
                data="0x5fe3000100",  # this is the actual bytecode to be deployed in the body
                code_inputs=0,  # define code header (in body) input bytes
                code_outputs=128,  # define code header (in body) output bytes (128 = 0x80 non ret)
                max_stack_height=1,  # define code header (in body) stack size
            ),
            # There can be multiple code sections
            Section(
                kind=SectionKind.CODE,
                data="0x50E3000250E4",
                code_inputs=1,
                code_outputs=0,
                max_stack_height=1,
            ),
            Section(
                kind=SectionKind.CODE,
                data="0x3080e300035050e4",
                code_inputs=0,
                code_outputs=1,
                max_stack_height=3,
            ),
            Section(
                kind=SectionKind.CODE,
                data="80e4",
                code_inputs=2,
                code_outputs=3,
                max_stack_height=3,
            ),
            # DATA section
            Section(kind=SectionKind.DATA, data="0xef"),
        ],
        # This will construct a valid EOF container with this bytes
        # 0xef0001010010020004000500060008000204000000008000010100000100010003020300035fe300010050
        # e3000250e43080e300035050e480e4
    )

    eof_test(
        data=bytes(eof_code),
        expect_exception=eof_code.validity_error,
    )


def test_eof_example_custom_fields(eof_test: EOFTestFiller):
    """
    Example of PYSPECs EOF class tuning
    """

    # if you need to overwrite certain structure bytes, you can use customization
    # this is useful for unit testing the eof structure format, you can reorganize sections
    # and overwrite the header bytes for testing purposes
    # most of the combinations are covered by the unit tests

    # This features are subject for development and will change in the future

    eof_code = Container(
        name="valid_container_example_2",
        custom_magic=0x00,  # magic can be overwritten for test purposes, (default is 0x00)
        custom_version=0x01,  # version can be overwritten for testing purposes (default is 0x01)
        custom_terminator=bytes([0]),  # terminator byte can be overwritten (default is 0x00)
        extra=None,  # extra bytes to be trailed after the container body bytes (default is None)
        sections=[
            # TYPES section is constructed automatically based on CODE
            # CODE section
            Section(
                kind=SectionKind.CODE,
                data="0x600200",  # this is the actual bytecode to be deployed in the body
                code_inputs=0,  # define code header (in body) input bytes
                code_outputs=128,  # define code header (in body) output bytes (128 = 0x80 non ret)
                max_stack_height=1,  # define code header (in body) stack size
            ),
            # DATA section
            Section(
                kind=SectionKind.DATA,
                data="0xef",
                # custom_size overrides the size bytes, so you can put only 1 byte into data
                # but still make the header size of 2 to produce invalid section
                # if custom_size != len(data), the section will be invalid
                custom_size=1,
            ),
        ],
        # auto generate types section based on provided code sections
        # AutoSection.ONLY_BODY - means the section will be generated only for the body bytes
        # AutoSection.ONLY_BODY - means the section will be generated only for the header bytes
        auto_type_section=AutoSection.AUTO,
        # auto generate default data section (0x empty), by default is True
        auto_data_section=True,
        # auto sort section by order 01 02 03 04
        # AutoSection.ONLY_BODY - means the sorting will be done only for the body bytes
        # AutoSection.ONLY_BODY - means the section will be done only for the header bytes
        auto_sort_sections=AutoSection.AUTO,
    )

    eof_test(
        data=bytes(eof_code),
        expect_exception=eof_code.validity_error,
    )
