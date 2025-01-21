"""EOF V1 Code Validation tests."""

from typing import List

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools.eof.v1 import AutoSection, Container, Section, SectionKind
from ethereum_test_tools.eof.v1.constants import MAX_INITCODE_SIZE
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .. import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7834.md"
REFERENCE_SPEC_VERSION = "821ffeb8c424b038984be2b7d373a5ef2eb33fa2"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)

smallest_runtime_subcontainer = Container(
    name="Runtime Subcontainer",
    sections=[
        Section.Code(code=Op.STOP),
    ],
)

VALID: List[Container] = [
    Container(
        name="small_metadata_section",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data="1122334455667788" * 4),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
    ),
    Container(
        name="large_data_section",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data="1122334455667788" * 3 * 1024),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
    ),
    Container(
        name="max_data_section",
        sections=[
            Section.Code(code=Op.STOP),
            # Hits the 49152 bytes limit for the entire container
            # Need to subtract an empty header size for the metadata section
            Section.Metadata(
                data=b"\x00" * (MAX_INITCODE_SIZE - len(smallest_runtime_subcontainer) - 3)
            ),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
    ),
    Container(
        name="DATALOADN_zero",
        sections=[
            Section.Code(
                code=Op.DATALOADN[0] + Op.POP + Op.STOP,
            ),
            Section.Metadata(data="aaffcc" * 16),
            Section.Data(data="1122334455667788" * 16),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
    ),
    Container(
        name="DATALOADN_middle",
        sections=[
            Section.Code(
                code=Op.DATALOADN[16] + Op.POP + Op.STOP,
            ),
            Section.Metadata(data="aaffcc" * 16),
            Section.Data(data="1122334455667788" * 16),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
    ),
    Container(
        name="DATALOADN_edge",
        sections=[
            Section.Code(
                code=Op.DATALOADN[128 - 32] + Op.POP + Op.STOP,
            ),
            Section.Metadata(data="aaffcc" * 16),
            Section.Data(data="1122334455667788" * 16),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
    ),
]

INVALID: List[Container] = [
    Container(
        name="empty_metadata_section",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data=""),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.ZERO_SECTION_SIZE,
    ),
    Container(
        name="empty_metadata_section_declared_with_size",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data="", custom_size=1),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.INVALID_SECTION_BODIES_SIZE,
    ),
    Container(
        name="nonempty_metadata_section_declared_with_0_size",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data="11", custom_size=0),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.ZERO_SECTION_SIZE,
    ),
    Container(
        name="DATALOADN_max_empty_data",
        sections=[
            Section.Code(
                code=Op.DATALOADN[0xFFFF - 32] + Op.POP + Op.STOP,
            ),
            Section.Metadata(data="aaffcc" * 16),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.INVALID_DATALOADN_INDEX,
    ),
    Container(
        name="DATALOADN_max_small_data",
        sections=[
            Section.Code(
                code=Op.DATALOADN[0xFFFF - 32] + Op.POP + Op.STOP,
            ),
            Section.Metadata(data="aaffcc" * 16),
            Section.Data(data="1122334455667788" * 16),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.INVALID_DATALOADN_INDEX,
    ),
    Container(
        name="DATALOADN_max_half_data",
        sections=[
            Section.Code(
                code=Op.DATALOADN[0xFFFF - 32] + Op.POP + Op.STOP,
            ),
            Section.Metadata(data="aaffcc" * 16),
            Section.Data(data=("1122334455667788" * 4 * 1024)[2:]),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.INVALID_DATALOADN_INDEX,
    ),
    Container(
        name="data_section_over_container_limit",
        sections=[
            Section.Code(code=Op.STOP),
            # Over the 49152 bytes limit for the entire container
            # Need to subtract an empty header size for the metadata section
            Section.Metadata(
                data=(b"12345678" * 6 * 1024)[len(smallest_runtime_subcontainer) + 3 - 1 :]
            ),
        ],
        # TODO: workaround until data section becomes kind 0xff
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.CONTAINER_SIZE_ABOVE_LIMIT,
    ),
    Container(
        name="missing_data_section",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data="11"),
        ],
        auto_data_section=False,
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_DATA_SECTION,
    ),
    Container(
        name="missing_data_section_with_subcontainer",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data="11"),
            Section.Container(container=Container()),
        ],
        auto_data_section=False,
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_DATA_SECTION,
    ),
    Container(
        name="missing_code_section",
        sections=[
            Section(kind=SectionKind.TYPE, data="0004"),
            Section.Metadata(data="11"),
        ],
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_CODE_HEADER,
    ),
    Container(
        name="missing_type_section",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data="11"),
        ],
        auto_type_section=AutoSection.NONE,
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_TYPE_HEADER,
    ),
    Container(
        name="metadata_at_pos_0",
        sections=[
            Section.Metadata(data="11"),
            Section(kind=SectionKind.TYPE, data="0004"),
            Section.Code(
                code=Op.STOP,
            ),
        ],
        auto_type_section=AutoSection.NONE,
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_TYPE_HEADER,
    ),
    Container(
        name="metadata_at_pos_1",
        sections=[
            Section(kind=SectionKind.TYPE, data="0004"),
            Section.Metadata(data="11"),
            Section.Code(
                code=Op.STOP,
            ),
        ],
        auto_type_section=AutoSection.NONE,
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_CODE_HEADER,
    ),
    Container(
        name="metadata_before_subcontainer",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Metadata(data="11"),
            Section.Container(container=Container()),
        ],
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_DATA_SECTION,
    ),
    Container(
        name="metadata_last",
        sections=[
            Section(kind=SectionKind.TYPE, data="0004"),
            Section.Code(
                code=Op.STOP,
            ),
            Section.Data(data=""),
            Section.Metadata(data="11"),
        ],
        auto_data_section=False,
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_TERMINATOR,
    ),
    Container(
        name="metadata_last_with_subcontainer",
        sections=[
            Section.Code(
                code=Op.STOP,
            ),
            Section.Container(container=Container()),
            Section.Data(data=""),
            Section.Metadata(data="11"),
        ],
        auto_data_section=False,
        auto_sort_sections=AutoSection.NONE,
        validity_error=EOFException.MISSING_TERMINATOR,
    ),
]

# FIXME: subcontainers (valid), multi code section, multi subcontainers, metadata in subcontainer
# FIXME: multiple metadata section headers


def container_name(c: Container):
    """Return the name of the container for use in pytest ids."""
    if hasattr(c, "name"):
        return c.name
    else:
        return c.__class__.__name__


@pytest.mark.parametrize(
    "container",
    VALID,
    ids=container_name,
)
def test_legacy_initcode_valid_eof_v1_contract(
    eof_test: EOFTestFiller,
    container: Container,
):
    """
    Test creating various types of valid EOF V1 contracts using legacy
    initcode and a contract creating transaction.
    """
    assert (
        container.validity_error is None
    ), f"Valid container with validity error: {container.validity_error}"
    eof_test(
        data=container,
    )


@pytest.mark.parametrize(
    "container",
    INVALID,
    ids=container_name,
)
def test_legacy_initcode_invalid_eof_v1_contract(
    eof_test: EOFTestFiller,
    container: Container,
):
    """
    Test creating various types of valid EOF V1 contracts using legacy
    initcode and a contract creating transaction.
    """
    assert container.validity_error is not None, "Invalid container without validity error"
    eof_test(
        data=container,
        expect_exception=container.validity_error,
    )
