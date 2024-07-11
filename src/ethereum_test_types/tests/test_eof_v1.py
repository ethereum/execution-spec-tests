"""
Test suite for `code.eof.v1` module.
"""

from typing import List, Tuple

import pytest

from ..eof.v1 import AutoSection, Container, Section, SectionKind
from ..vm import Bytecode
from ..vm import Opcodes as Op

test_cases: List[Tuple[str, Container, str]] = [
    (
        "No sections",
        Container(
            auto_data_section=False,
            auto_type_section=AutoSection.NONE,
            sections=[],
        ),
        "ef0001 00",
    ),
    (
        "Single code section",
        Container(
            sections=[
                Section.Code(Op.STOP),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 04 0000 00 00800000 00",
    ),
    (
        "Single code section, single container section",
        Container(
            sections=[
                Section.Code(Op.EXP),
                Section.Container(Container(raw_bytes=b"\x0b")),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 03 0001 0001 04 0000 00 00800002 0A 0B",
    ),
    (
        "Single code section, single container section, single data",
        Container(
            sections=[
                Section.Code(Op.EXP),
                Section.Container(Container(raw_bytes=b"\x0b")),
                Section.Data("0x0C"),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 03 0001 0001 04 0001 00 00800002 0A 0B 0C",
    ),
    (
        "Single code section, single container section, single data 2",
        Container(
            sections=[
                Section.Code(Op.EXP),
                Section.Data("0x0C"),
                Section.Container(Container(raw_bytes=b"\x0b")),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 03 0001 0001 04 0001 00 00800002 0A 0B 0C",
    ),
    (
        "Single code section, multiple container section, single data",
        Container(
            sections=[
                Section.Code(Op.EXP),
                Section.Container(Container(raw_bytes=b"\x0b")),
                Section.Data("0x0C"),
                Section.Container(Container(raw_bytes=b"\x0d")),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 03 0002 0001 0001 04 0001 00 00800002 0A 0B 0D 0C",
    ),
    (
        "Single code section, multiple container sections",
        Container(
            sections=[
                Section.Code(Op.STOP),
                Section.Container(Container(raw_bytes=b"\0\1")),
                Section.Container(Container(raw_bytes=b"\0")),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 03 0002 0002 0001 04 0000 00 00800000 00 0001 00",
    ),
    (
        "No code section",
        Container(
            sections=[Section.Data("0x00")],
        ),
        "ef0001 01 0000 04 0001 00 00",
    ),
    (
        "Single data section",
        Container(
            auto_type_section=AutoSection.NONE,
            sections=[
                Section.Data("0x00"),
            ],
        ),
        "ef0001 04 0001 00 00",
    ),
    (
        "Custom invalid section",
        Container(
            auto_data_section=False,
            auto_type_section=AutoSection.NONE,
            sections=[
                Section(
                    kind=0xFE,
                    data="0x00",
                ),
            ],
        ),
        "ef0001 fe 0001 00 00",
    ),
    (
        "Multiple sections",
        Container(
            sections=[
                Section.Code(Op.EXP),
                Section.Data("0x0f"),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 04 0001 00 00800002 0a 0f",
    ),
    (
        "Multiple type sections",
        Container(
            sections=[
                Section(
                    kind=SectionKind.TYPE,
                    data="0x00000000",
                ),
                Section(
                    kind=SectionKind.TYPE,
                    data="0x00000000",
                ),
                Section.Code(Op.STOP),
            ],
            auto_type_section=AutoSection.NONE,
        ),
        "ef0001 01 0004 01 0004 02 0001 0001 04 0000 00 00000000 00000000 00",
    ),
    (
        "Invalid Magic",
        Container(
            magic=b"\xEF\xFE",
            sections=[
                Section.Code(Op.STOP),
            ],
        ),
        "effe01 01 0004 02 0001 0001 04 0000 00 00800000 00",
    ),
    (
        "Invalid Version",
        Container(
            version=b"\x02",
            sections=[
                Section.Code(Op.STOP),
            ],
        ),
        "ef0002 01 0004 02 0001 0001 04 0000 00 00800000 00",
    ),
    (
        "Section Invalid size Version",
        Container(
            sections=[
                Section.Code(
                    Op.STOP,
                    custom_size=0xFFFF,
                ),
            ],
        ),
        "ef0001 01 0004 02 0001 ffff 04 0000 00 00800000 00",
    ),
    (
        "Nested EOF",
        Container(
            sections=[
                Section.Code(Op.STOP),
                Section(
                    kind=SectionKind.CONTAINER,
                    data=Container(
                        sections=[Section.Code(Op.ADD)],
                    ),
                ),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 03 0001 0014 04 0000 00 00800000 00"
        "ef0001 01 0004 02 0001 0001 04 0000 00 00800002 01",
    ),
    (
        "Nested EOF in Data",
        Container(
            sections=[
                Section.Code(Op.STOP),
                Section.Data(
                    data=Container(
                        sections=[Section.Code(Op.ADD)],
                    ),
                ),
            ],
        ),
        "ef0001 01 0004 02 0001 0001 04 0014 00 00800000 00"
        "ef0001 01 0004 02 0001 0001 04 0000 00 00800002 01",
    ),
    (
        "Incomplete code section",
        Container(
            sections=[
                Section.Code(
                    code=Bytecode(),
                    custom_size=0x02,
                ),
            ],
        ),
        "ef0001 01 0004 02 0001 0002 04 0000 00 00800000",
    ),
    (
        "Trailing bytes after code section",
        Container(
            sections=[
                Section.Code(Op.PUSH1[0] + Op.STOP),
            ],
            extra=bytes.fromhex("deadbeef"),
        ),
        "ef0001 01 0004 02 0001 0003 04 0000 00 00800001 600000 deadbeef",
    ),
    (
        "Multiple code sections",
        Container(
            sections=[
                Section.Code(Op.PUSH1[0] + Op.STOP),
                Section.Code(Op.PUSH1[0] + Op.STOP),
            ],
        ),
        """
            ef0001 01 0008 02 0002 0003 0003 04 0000 00
            00800001 00800001
            600000
            600000
            """,
    ),
    (
        "No section terminator",
        Container(
            sections=[
                Section.Code(Op.PUSH1[0] + Op.STOP),
            ],
            header_terminator=bytes(),
        ),
        "ef0001 01 0004 02 0001 0003 04 0000 00800001 600000",
    ),
    (
        "No auto type section",
        Container(
            auto_type_section=AutoSection.NONE,
            sections=[
                Section.Code(Op.STOP),
            ],
        ),
        "ef0001 02 0001 0001 04 0000 00 00",
    ),
    (
        "Data section in types",
        Container(
            sections=[
                Section.Code(Op.STOP),
                Section.Data(
                    data="0x00",
                    force_type_listing=True,
                ),
            ],
        ),
        """
            ef0001 01 0008 02 0001 0001 04 0001 00
            00800000 00800000
            00 00
            """,
    ),
    (
        "Code section inputs",
        Container(
            sections=[
                Section.Code(
                    Op.STOP,
                    code_inputs=1,
                ),
            ],
        ),
        """
            ef0001 01 0004 02 0001 0001 04 0000 00
            01800000
            00
            """,
    ),
    (
        "Code section inputs 2",
        Container(
            sections=[
                Section.Code(
                    Op.STOP,
                    code_inputs=0xFF,
                ),
            ],
        ),
        """
            ef0001 01 0004 02 0001 0001 04 0000 00
            ff800000
            00
            """,
    ),
    (
        "Code section outputs",
        Container(
            sections=[
                Section.Code(
                    Op.STOP,
                    code_outputs=1,
                ),
            ],
        ),
        """
            ef0001 01 0004 02 0001 0001 04 0000 00
            00010000
            00
            """,
    ),
    (
        "Code section outputs 2",
        Container(
            sections=[
                Section.Code(
                    Op.STOP,
                    code_outputs=0xFF,
                ),
            ],
        ),
        """
            ef0001 01 0004 02 0001 0001 04 0000 00
            00ff0000
            00
            """,
    ),
    (
        "Code section max stack height",
        Container(
            sections=[
                Section.Code(
                    Op.STOP,
                    max_stack_height=0x0201,
                ),
            ],
        ),
        """
            ef0001 01 0004 02 0001 0001 04 0000 00
            00800201
            00
            """,
    ),
    (
        "Code section max stack height 2",
        Container(
            sections=[
                Section.Code(
                    Op.STOP,
                    max_stack_height=0xFFFF,
                ),
            ],
        ),
        """
            ef0001 01 0004 02 0001 0001 04 0000 00
            0080FFFF
            00
            """,
    ),
    (
        "Code section max stack height 3",
        Container(
            sections=[
                Section.Code(
                    Op.STOP,
                    max_stack_height=0xFFFF,
                ),
                Section.Code(Op.STOP),
            ],
        ),
        """
            ef0001 01 0008 02 0002 0001 0001 04 0000 00
            0080FFFF 00800000
            00
            00
            """,
    ),
    (
        "Custom type section",
        Container(
            sections=[
                Section(
                    kind=SectionKind.TYPE,
                    data=Op.STOP,
                ),
                Section.Code(Op.STOP),
            ],
        ),
        "ef0001 01 0001 02 0001 0001 04 0000 00 00 00",
    ),
    (
        "EIP-4750 Single code section oversized type",
        Container(
            sections=[
                Section(
                    kind=SectionKind.TYPE,
                    data="0x0000000000",
                ),
                Section.Code(Op.STOP),
            ],
        ),
        "ef0001 01 0005 02 0001 0001 04 0000 00 0000000000 00",
    ),
    (
        "Empty type section",
        Container(
            sections=[
                Section(kind=SectionKind.TYPE, data="0x"),
                Section.Code(Op.STOP),
            ],
            auto_type_section=AutoSection.NONE,
        ),
        "ef0001 01 0000 02 0001 0001 04 0000 00 00",
    ),
    (
        "Check that simple valid EOF1 deploys",
        Container(
            sections=[
                Section.Code(
                    Op.ADDRESS + Op.POP + Op.STOP,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=1,
                ),
                Section.Data("0xef"),
            ],
            auto_type_section=AutoSection.AUTO,
        ),
        """
        # EOF deployed code
        ef0001  # Magic followed by version
        010004  # One code segment
        020001  # One code segment
            0003  #   code seg 0: 3 bytes
        040001  # One byte data segment
        00      # End of header
                # Code segment 0 header
            00  # Zero inputs
            80  # Non-Returning Function
            0001  # Max stack height 1
                # Code segment 0 code
            30 #  1 ADDRESS
            50 #  2 POP
            00 #  3 STOP
            # Data segment
            ef
        """,
    ),
    (
        "Data Section custom_size parameter overwrites bytes size",
        Container(
            sections=[
                Section.Code(
                    Op.ADDRESS + Op.POP + Op.STOP,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=1,
                ),
                Section.Data("0x0bad", custom_size=4),
            ],
            auto_type_section=AutoSection.AUTO,
        ),
        """
      # EOF deployed code
      ef0001  # Magic followed by version
      010004  # One code segment
      020001  # One code segment
        0003  #   code seg 0: 3 bytes
      040004  # Four byte data segment
      00      # End of header
              # Code segment 0 header
          00  # Zero inputs
          80  # Non-Returning Function
        0001  # Max stack height 1
              # Code segment 0 code
           30 #  1 ADDRESS
           50 #  2 POP
           00 #  3 STOP
              # Data segment
           0bad  # 2 bytes instead of four
        """,
    ),
    (
        "Multiple code segments",
        Container(
            sections=[
                Section.Code(
                    Op.PUSH0
                    + Op.CALLDATALOAD
                    + Op.RJUMPV[0, 3, 6, 9]
                    + Op.JUMPF[1]
                    + Op.JUMPF[2]
                    + Op.JUMPF[3]
                    + Op.CALLF[4]
                    + Op.STOP,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=1,
                ),
                Section.Code(
                    Op.RETURN(Op.PUSH0, Op.PUSH0),
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=2,
                ),
                Section.Code(
                    Op.REVERT(Op.PUSH0, Op.PUSH0),
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=2,
                ),
                Section.Code(
                    Op.INVALID,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=0,
                ),
                Section.Code(
                    Op.RETF,
                    code_inputs=0,
                    code_outputs=0,
                    max_stack_height=0,
                ),
                Section.Data("0x0bad60a7", custom_size=4),
            ],
            auto_type_section=AutoSection.AUTO,
        ),
        """
      # EOF deployed code
      EF0001 # Magic and Version ( 1 )
     010014 # Types length ( 20 )
     020005 # Total code sections ( 5 )
       0019 # Code section  0 , 25  bytes
       0003 # Code section  1 , 3  bytes
       0003 # Code section  2 , 3  bytes
       0001 # Code section  3 , 1  bytes
       0001 # Code section  4 , 1  bytes
     040004 # Data section length ( 4 )
         00 # Terminator (end of header)
            # Code 0 types
         00 # 0 inputs
         80 # 0 outputs (Non-returning function)
       0001 # max stack: 1
            # Code 1 types
         00 # 0 inputs
         80 # 0 outputs (Non-returning function)
       0002 # max stack: 2
            # Code 2 types
         00 # 0 inputs
         80 # 0 outputs (Non-returning function)
       0002 # max stack: 2
            # Code 3 types
         00 # 0 inputs
         80 # 0 outputs (Non-returning function)
       0000 # max stack: 0
            # Code 4 types
         00 # 0 inputs
         00 # 0 outputs
       0000 # max stack: 0
            # Code section 0
         5f # [0] PUSH0
         35 # [1] CALLDATALOAD
     e2030000000300060009 # [2] RJUMPV(0,3,6,9)
     e50001 # [12] JUMPF(1)
     e50002 # [15] JUMPF(2)
     e50003 # [18] JUMPF(3)
     e30004 # [21] CALLF(4)
         00 # [24] STOP
            # Code section 1
         5f # [0] PUSH0
         5f # [1] PUSH0
         f3 # [2] RETURN
            # Code section 2
         5f # [0] PUSH0
         5f # [1] PUSH0
         fd # [2] REVERT
            # Code section 3
         fe # [0] INVALID
            # Code section 4
         e4 # [0] RETF
            # Data section
     0bad60a7
        """,
    ),
    (
        "Custom Types Section overrides code",
        Container(
            sections=[
                Section(kind=SectionKind.TYPE, data="0x00700002", custom_size=8),
                Section(
                    kind=SectionKind.CODE,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=1,
                    data="0x305000",
                ),
                Section(kind=SectionKind.DATA, data="0x0bad60A7"),
            ],
        ),
        """
      # EOF deployed code
      ef0001  # Magic followed by version
      010008  # Two code segments
      020001  # One code segment
        0003  #   code seg 0: 3 bytes
      040004  # Four byte data segment
      00      # End of header
              # Code segment 0 header
          00  # Zero inputs
          70  # Non-Returning Function
        0002  # Max stack height 1
              # Code segment 0 code
           30 #  1 ADDRESS
           50 #  2 POP
           00 #  3 STOP
              # Data segment
           0bad60A7  # 4 bytes (valid)
        """,
    ),
    (
        "Type section wrong order, but only in HEADER",
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=1,
                    data="0x305000",
                ),
                Section(
                    kind=SectionKind.TYPE,
                    data="0x00800001",
                ),
                Section(kind=SectionKind.DATA, data="0xef"),
            ],
            auto_sort_sections=AutoSection.ONLY_BODY,
        ),
        """
      # EOF deployed code
      ef0001  # Magic followed by bad version
      020001  # One code segment
        0003  #   code seg 0: 3 bytes
      010004  # One code segment
      040001  # One byte data segment
      00      # End of header
              # Code segment 0 header
          00  # Zero inputs
          80  # Non-Returning Function
        0001  # Max stack height 1
              # Code segment 0 code
           30 #  1 ADDRESS
           50 #  2 POP
           00 #  3 STOP
              # Data segment
           ef
        """,
    ),
    (
        "Type section wrong order, but only in BODY",
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=1,
                    data="0x305000",
                ),
                Section(
                    kind=SectionKind.TYPE,
                    data="0x00800001",
                ),
                Section(kind=SectionKind.DATA, data="0xef"),
            ],
            auto_sort_sections=AutoSection.ONLY_HEADER,
        ),
        """
      # EOF deployed code
      ef0001  # Magic followed by bad version
      010004  # One code segment
      020001  # One code segment
        0003  #   code seg 0: 3 bytes
      040001  # One byte data segment
      00      # End of header
              # Code segment 0 code
           30 #  1 ADDRESS
           50 #  2 POP
           00 #  3 STOP
              # Code segment 0 header
          00  # Zero inputs
          80  # Non-Returning Function
        0001  # Max stack height 1
              # Data segment
           ef
        """,
    ),
    (
        "Type section missing, but only in HEADER",
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=1,
                    data="0x305000",
                ),
                Section(kind=SectionKind.DATA, data="0xef"),
            ],
            auto_type_section=AutoSection.ONLY_BODY,
        ),
        """
      # EOF deployed code
      ef0001  # Magic followed by bad version
      020001  # One code segment
        0003  #   code seg 0: 3 bytes
      040001  # One byte data segment
      00      # End of header
              # Code segment 0 header
          00  # Zero inputs
          80  # Non-Returning Function
        0001  # Max stack height 1
              # Code segment 0 code
           30 #  1 ADDRESS
           50 #  2 POP
           00 #  3 STOP
              # Data segment
           ef
        """,
    ),
    (
        "Type section missing, but only in BODY",
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    code_inputs=0,
                    code_outputs=128,  # Non returning
                    max_stack_height=1,
                    data="0x305000",
                ),
                Section(kind=SectionKind.DATA, data="0xef"),
            ],
            auto_type_section=AutoSection.ONLY_HEADER,
        ),
        """
      # EOF deployed code
      ef0001  # Magic followed by bad version
      010004  # Types section
      020001  # One code segment
        0003  #   code seg 0: 3 bytes
      040001  # One byte data segment
      00      # End of header
              # Code segment 0 header
              # Code segment 0 code
           30 #  1 ADDRESS
           50 #  2 POP
           00 #  3 STOP
              # Data segment
           ef
        """,
    ),
]


@pytest.mark.parametrize(
    ["container", "hex"],
    [(x[1], x[2]) for x in test_cases],
    ids=[x[0] for x in test_cases],
)
def test_eof_v1_assemble(container: Container, hex: str):
    """
    Test `ethereum_test.types.code`.
    """
    expected_string = remove_comments_from_string(hex)
    expected_bytes = bytes.fromhex(expected_string.replace(" ", "").replace("\n", ""))
    assert (
        bytes(container) == expected_bytes
    ), f"""
    Container: {bytes(container).hex()}
    Expected : {expected_bytes.hex()}
    """


def remove_comments_from_string(input_string):
    """
    Remove comments from a string and leave only valid hex characters.
    """
    # Split the string into individual lines
    lines = input_string.split("\n")

    # Process each line to remove text following a '#'
    cleaned_lines = []
    for line in lines:
        # Find the index of the first '#' character
        comment_start = line.find("#")

        # If a '#' is found, slice up to that point; otherwise, take the whole line
        if comment_start != -1:
            cleaned_line = line[:comment_start].rstrip()
        else:
            cleaned_line = line

        # Only add non-empty lines if needed
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line)

    # Join the cleaned lines back into a single string
    cleaned_string = "\n".join(cleaned_lines)
    return cleaned_string


@pytest.mark.parametrize(
    ["section", "expected_code_inputs", "expected_code_outputs", "expected_max_stack_height"],
    [
        (Section.Code(Op.STOP), 0, 0x80, 0),
        (Section.Code(Op.STOP, code_inputs=1), 1, 0x80, 0),
        (Section.Code(Op.STOP, code_outputs=1), 0, 1, 0),
        (Section.Code(Op.STOP, max_stack_height=1), 0, 0x80, 1),
        (Section.Code(Op.STOP, code_inputs=1, code_outputs=1, max_stack_height=1), 1, 1, 1),
        (Section.Code(Op.ADD(0, 1) + Op.STOP), 0, 0x80, 2),
        (Section.Function(Op.ADD(0, 1) + Op.RETF), 0, 1, 2),
        (Section.Function(Op.ADD + Op.RETF, code_inputs=2), 2, 1, 2),
        (Section.Function(Op.PUSH0 + Op.POP + Op.RETF, code_inputs=3), 3, 3, 4),
        (Section.Function(Op.POP * 3 + Op.PUSH0 * 3 + Op.RETF), 3, 3, 3),
    ],
)
def test_section_inputs_outputs_stack_calculations(
    section: Section,
    expected_code_inputs: int,
    expected_code_outputs: int,
    expected_max_stack_height: int,
):
    """
    Test code section stack properties settings.
    """
    assert section.code_inputs == expected_code_inputs
    assert section.code_outputs == expected_code_outputs
    assert section.max_stack_height == expected_max_stack_height
