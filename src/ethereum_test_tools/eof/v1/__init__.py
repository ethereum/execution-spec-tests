"""
EVM Object Format Version 1 Libary to generate bytecode for testing purposes
"""
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional

from ...code import Code, code_to_bytes
from ..constants import EOF_HEADER_TERMINATOR, EOF_MAGIC

VERSION_NUMBER = bytes.fromhex("01")
VERSION_MAX_SECTION_KIND = 3


class SectionKind(IntEnum):
    """
    Enum class of V1 valid section kind values
    """

    TYPE = 1
    CODE = 2
    DATA = 3


@dataclass(kw_only=True)
class Section:
    """
    Class that represents a section in an EOF V1 container.
    """

    data: Code | str | bytes | List[Code | str | bytes] | None = None
    """
    Data to be contained by this section.
    Can be code, another EOF container or any other abstract data.
    """
    custom_size: int | None = None
    """
    Size value to be used in the header.
    If set to None, the header is built with length of the data.
    """
    kind: SectionKind | int
    """
    Kind of section that is represented by this object.
    Can be any `int` outside of the values defined by `SectionKind`
    for testing purposes.
    """
    force_type_listing: bool = False
    """
    Forces this section to appear in the TYPE section at the beginning of the
    container.
    """
    code_inputs: int = 0
    """
    Data stack items consumed by this code section (function)
    """
    code_outputs: int = 0
    """
    Data stack items produced by or expected at the end of this code section
    (function)
    """
    max_stack_height: int = 0
    """
    Maximum hieght data stack reaches during execution of code section.
    """

    def get_header(self) -> bytes:
        """
        Get formatted header for this section according to its contents.
        """
        size = self.custom_size
        if size is None:
            if self.data is None:
                raise Exception(
                    "Attempted to build header without section data"
                )
            if isinstance(self.data, list):
                out = len(self.data).to_bytes(2, byteorder="big")
                for data in self.data:
                    out += len(code_to_bytes(data)).to_bytes(2, byteorder="big")
                return self.kind.to_bytes(1, byteorder="big") + out
            else:
                size = len(code_to_bytes(self.data))
        if self.kind == SectionKind.CODE:
            return self.kind.to_bytes(1, byteorder="big") + bytes.fromhex("0001") + size.to_bytes(2, byteorder="big")
        else:
            return self.kind.to_bytes(1, byteorder="big") + size.to_bytes(2, byteorder="big")


@dataclass(kw_only=True)
class Container(Code):
    """
    Class that represents an EOF V1 container.
    """

    sections: List[Section]
    """
    List of sections in the container
    """
    custom_magic: Optional[int] = None
    """
    Custom magic value used to override the mandatory EOF value for testing
    purposes.
    """
    custom_version: Optional[int] = None
    """
    Custom version value used to override the mandatory EOF V1 value
    for testing purposes.
    """
    custom_terminator: Optional[bytes] = None
    """
    Custom terminator bytes used to terminate the header.
    """
    extra: Optional[bytes] = None
    """
    Extra data to be appended at the end of the container, which will
    not be considered part of any of the sections, for testing purposes.
    """
    auto_type_section: bool = True
    """
    Automatically generate a `TYPE` section based on the
    included `CODE` kind sections.
    """
    auto_data_section: bool = True
    """
    Automatically generate a `DATA` section.
    """
    force_type_section: bool = False
    """
    Force generate a `TYPE` section based on the included
    `CODE` kind sections, even when only one code section
    or zero.
    """

    def assemble(self) -> bytes:
        """
        Converts the EOF V1 Container into bytecode.
        """
        c = bytes.fromhex("EF")

        c += (
            EOF_MAGIC
            if self.custom_magic is None
            else self.custom_magic.to_bytes(1, "big")
        )

        c += (
            VERSION_NUMBER
            if self.custom_version is None
            else self.custom_version.to_bytes(1, "big")
        )

        # Copy the sections so we can add the `type` section
        sections = self.sections.copy()

        if (
            self.auto_type_section
            and len(sections) > 0
            and sections[0].kind != SectionKind.TYPE
        ) or self.force_type_section:
            type_section_data: bytes = bytes()
            for s in sections:
                if s.kind == SectionKind.CODE or s.force_type_listing:
                    type_section_data += s.code_inputs.to_bytes(
                        length=((s.code_inputs.bit_length() - 1) // 8 + 1)
                        if s.code_inputs > 0
                        else 1,
                        byteorder="big",
                    )
                    type_section_data += s.code_outputs.to_bytes(
                        length=((s.code_outputs.bit_length() - 1) // 8 + 1)
                        if s.code_outputs > 0
                        else 1,
                        byteorder="big",
                    )
                    type_section_data += s.max_stack_height.to_bytes(
                        length=((s.code_outputs.bit_length() - 1) // 8 + 1)
                        if s.code_outputs > 255
                        else 2,
                        byteorder="big",
                    )

            sections = [
                Section(
                    kind=SectionKind.TYPE,
                    data=type_section_data,
                )
            ] + sections

        if self.auto_data_section:
            if len(sections) > 2 and sections[2].kind == SectionKind.DATA:
                pass # already exists
            else:
                sections.append(Section(kind=SectionKind.DATA, data="0x"))

        # Add headers
        for s in sections:
            c += s.get_header()

        # Add header terminator
        if self.custom_terminator is not None:
            c += self.custom_terminator
        else:
            c += EOF_HEADER_TERMINATOR

        # Add section bodies
        for s in sections:
            c += code_to_bytes(s.data if s.data is not None else "0x") 

        # Add extra (garbage)
        if self.extra is not None:
            c += self.extra

        return c
