"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4750.md"
REFERENCE_SPEC_VERSION = "14400434e1199c57d912082127b1d22643788d11"


# Container containing 256 code sections, section index 2 is unreachable
unreachable_code_sections_23 = Container(
    name="unreachable_code_sections_23",
    sections=[
        Section.Code(code=Op.JUMPF[1]),
        Section.Code(code=Op.JUMPF[1]),
    ]
    + [Section.Code(code=Op.JUMPF[i + 1]) for i in range(2, 255)]
    + [Section.Code(code=Op.NOOP * 3 + Op.STOP)],
    validity_error=[EOFException.UNREACHABLE_CODE_SECTIONS],
)
# Container containing 256 code sections, section index 255 is unreachable
unreachable_code_sections_24 = Container(
    name="unreachable_code_sections_24",
    sections=[
        Section.Code(code=Op.JUMPF[1]),
    ]
    + [Section.Code(code=Op.JUMPF[i + 1]) for i in range(1, 254)]
    + [Section.Code(code=Op.JUMPF[254])]
    + [Section.Code(code=Op.NOOP * 3 + Op.STOP)],
    validity_error=[EOFException.UNREACHABLE_CODE_SECTIONS],
)

@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="unreachable1",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.INVALID),
            ],
            expected_bytecode="ef000101000802000200010001040000000080000000800000fefe",
        ),
        Container(
            name="unreachable1_selfjumpf",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.JUMPF[1]),
            ],
            expected_bytecode="ef000101000802000200010003040000000080000000800000fee50001",
        ),
        Container(
            name="unreachable1_selfcallf",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.CALLF[1] + Op.STOP),
            ],
            expected_bytecode="ef000101000802000200010004040000000080000000800000fee3000100",
        ),
        Container(
            name="unreachable1_jumpf0",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.JUMPF[0]),
            ],
            expected_bytecode="ef000101000802000200010003040000000080000000800000fee50000",
        ),
        Container(
            name="unreachable1_callf0",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.CALLF[0] + Op.STOP),
            ],
            expected_bytecode="ef000101000802000200010004040000000080000000800000fee3000000",
        ),
        Container(
            name="unreachable1_selfcall_jumpf0",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.CALLF[1] + Op.JUMPF[0]),
            ],
            expected_bytecode="ef000101000802000200010006040000000080000000800000fee30001e50000",
        ),
        Container(
            name="unreachable12_of3_2jumpf1",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.STOP),
                Section.Code(code=Op.JUMPF[1]),
            ],
            expected_bytecode="ef000101000c02000300010001000304000000008000000080000000800000fe00e50001",
        ),
        Container(
            name="unreachable12_of3_2callf1",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.STOP),
                Section.Code(code=Op.CALLF[1] + Op.STOP),
            ],
            expected_bytecode="ef000101000c02000300010001000404000000008000000080000000800000fe00e3000100",
        ),
        Container(
            name="unreachable12_of3_jumpf_loop",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.JUMPF[2]),
                Section.Code(code=Op.JUMPF[1]),
            ],
            expected_bytecode="ef000101000c02000300010003000304000000008000000080000000800000fee50002e50001",
        ),
        Container(
            name="unreachable12_of3_callf_loop_stop",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.CALLF[2] + Op.STOP),
                Section.Code(code=Op.CALLF[1] + Op.STOP),
            ],
            expected_bytecode="ef000101000c02000300010004000404000000008000000080000000800000fee3000200e3000100",
        ),
        Container(
            name="unreachable12_of3_callf_loop_retf",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.CALLF[2] + Op.RETF, code_outputs=0),
                Section.Code(code=Op.CALLF[1] + Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c02000300010004000404000000008000000000000000000000fee30002e4e30001e4",
        ),
        Container(
            name="unreachable12_of3_callf_loop_mixed",
            sections=[
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.CALLF[2] + Op.STOP),
                Section.Code(code=Op.CALLF[1] + Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c02000300010004000404000000008000000080000000000000fee3000200e30001e4",
        ),
        Container(
            name="unreachable2_of3",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP),
                Section.Code(code=Op.RETF, code_outputs=0),
                Section.Code(code=Op.INVALID),
            ],
            expected_bytecode="ef000101000c02000300040001000104000000008000000000000000800000e3000100e4fe",
        ),
        Container(
            name="unreachable1_of3",
            sections=[
                Section.Code(code=Op.CALLF[2] + Op.STOP),
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c02000300040001000104000000008000000080000000000000e3000200fee4",
        ),
        Container(
            name="unreachable1_of4",
            sections=[
                Section.Code(code=Op.CALLF[3] + Op.STOP),
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.RETF, code_outputs=0),
                Section.Code(code=Op.CALLF[2] + Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101001002000400040001000100040400000000800000008000000000000000000000e3000300fee4e30002e4",
        ),
        Container(
            name="unreachable2_of3_retf",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.STOP),
                Section.Code(code=Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c02000300030001000104000000008000000080000000000000e5000100e4",
        ),
        Container(
            name="unreachable2_255",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.JUMPF[1]),  # self-reference
            ]
            + [Section.Code(code=Op.JUMPF[i]) for i in range(3, 255)]  # unreachable
            + [Section.Code(code=Op.STOP)],  # unreachable
            validity_error=[EOFException.UNREACHABLE_CODE_SECTIONS],
        ),
        Container(
            name="unreachable255",
            sections=[Section.Code(Op.JUMPF[1]) for i in range(1, 255)]
            + [
                Section.Code(Op.JUMPF[254]),  # self-reference
                Section.Code(Op.STOP),  # unreachable
            ],
            validity_error=[EOFException.UNREACHABLE_CODE_SECTIONS],
        ),
        Container(
            name="unreachable_code_sections_18",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP),
                Section.Code(code=Op.NOOP + Op.RETF, code_outputs=0),
                Section.Code(code=Op.INVALID),
            ],
            expected_bytecode="ef000101000c02000300040002000104000000008000000000000000800000e30001005be4fe",
        ),
        Container(
            name="unreachable_code_sections_19",
            sections=[
                Section.Code(code=Op.CALLF[2] + Op.STOP),
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.NOOP + Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c02000300040001000204000000008000000080000000000000e3000200fe5be4",
        ),
        Container(
            name="unreachable_code_sections_20",
            sections=[
                Section.Code(code=Op.CALLF[3] + Op.STOP),
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.NOOP + Op.RETF, code_outputs=0),
                Section.Code(code=Op.CALLF[2] + Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101001002000400040001000200040400000000800000008000000000000000000000e3000300fe5be4e30002e4",
        ),
        Container(
            name="selfjumpf0_unreachable1",
            sections=[
                Section.Code(code=Op.JUMPF[0]),
                Section.Code(code=Op.JUMPF[1]),
            ],
            expected_bytecode="ef000101000802000200030003040000000080000000800000e50000e50001",
        ),
        Container(
            name="unreachable_code_sections_22",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.STOP),
                Section.Code(code=Op.NOOP + Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c02000300030001000204000000008000000080000000000000e50001005be4",
        ),
        unreachable_code_sections_23,
        unreachable_code_sections_24,
        Container(
            name="unreachable_code_sections_25",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.JUMPF[2]),
            ],
            expected_bytecode="ef000101000c02000300030003000304000000008000000080000000800000e50001e50001e50002",
        ),
        Container(
            name="unreachable_code_sections_26",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.JUMPF[2]),
                Section.Code(code=Op.INVALID),
                Section.Code(code=Op.JUMPF[4]),
                Section.Code(code=Op.JUMPF[3]),
            ],
            expected_bytecode="ef000101001402000500030003000100030003040000000080000000800000008000000080000000800000e50001e50002fee50004e50003",
        ),
        Container(
            name="unreachable_code_section_in_subcontainer_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                      name="unreachable_code_section_in_subcontainer_0_D1I0",
                      sections=[
                          Section.Code(code=Op.INVALID),
                          Section.Code(code=Op.INVALID),
                      ],
                  )
                ),
            ],
            expected_bytecode="ef0001010004020001000b030001001b04000000008000046000600060006000ec0000ef000101000802000200010001040000000080000000800000fefe",
            validity_error=[EOFException.UNREACHABLE_CODE_SECTIONS],
        ),
        Container(
            name="unreachable_code_section_in_subcontainer_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                      name="unreachable_code_section_in_subcontainer_1_D1I0",
                      sections=[
                          Section.Code(code=Op.JUMPF[1]),
                          Section.Code(code=Op.JUMPF[2]),
                          Section.Code(code=Op.INVALID),
                          Section.Code(code=Op.JUMPF[4]),
                          Section.Code(code=Op.JUMPF[3]),
                      ],
                  )
                ),
            ],
            expected_bytecode="ef0001010004020001000b030001003804000000008000046000600060006000ec0000ef000101001402000500030003000100030003040000000080000000800000008000000080000000800000e50001e50002fee50004e50003",
            validity_error=[EOFException.UNREACHABLE_CODE_SECTIONS],
        ),
    ],
    ids=lambda c: c.name,
)
def test_unreachable_code_sections(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test eof contracts containing unreachable code sections."""
    eof_test(
        container=container,
        expect_exception=[EOFException.UNREACHABLE_CODE_SECTIONS],
    )


