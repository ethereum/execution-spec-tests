""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "12ca2f0bd2f7380100e154aaaa0995c46cbb2710"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMP[0] + Op.STOP, max_stack_height=1),
                    Section.Data(data="aabb")
                ],
              )
              ,
              "ef0001010004020001000604000200008000016000e0000000aabb",
              None,
              id="eof1_section_order_0"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0002",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      #--- Error: Invalid Code Header ---#
                      0x04,
                      0x00,
                      0x02,
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x06,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0xaa,
                      0xbb,
                      0x60,
                      0x00,
                      0xe0,
                      0x00,
                      0x00,
                      0x00,
                    ]),
              )
              ,
              "ef000101000404000202000100060000800000aabb6000e0000000",
              EOFException.MISSING_CODE_HEADER,
              id="eof1_section_order_1"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0003",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      #--- Error: Invalid Types Header ---#
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x06,
                      0x01,
                      0x00,
                      0x04,
                      0x04,
                      0x00,
                      0x02,
                      0x00,
                      0x60,
                      0x00,
                      0xe0,
                      0x00,
                      0x00,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0xaa,
                      0xbb,
                    ]),
              )
              ,
              "ef00010200010006010004040002006000e000000000800000aabb",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_section_order_2"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0004",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      #--- Error: Invalid Types Header ---#
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x06,
                      0x04,
                      0x00,
                      0x02,
                      0x01,
                      0x00,
                      0x04,
                      0x00,
                      0x60,
                      0x00,
                      0xe0,
                      0x00,
                      0x00,
                      0x00,
                      0xaa,
                      0xbb,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                    ]),
              )
              ,
              "ef00010200010006040002010004006000e0000000aabb00800000",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_section_order_3"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0005",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      #--- Error: Invalid Types Header ---#
                      0x04,
                      0x00,
                      0x02,
                      0x01,
                      0x00,
                      0x04,
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x06,
                      0x00,
                      0xaa,
                      0xbb,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0x60,
                      0x00,
                      0xe0,
                      0x00,
                      0x00,
                      0x00,
                    ]),
              )
              ,
              "ef0001040002010004020001000600aabb008000006000e0000000",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_section_order_4"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0006",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      #--- Error: Invalid Types Header ---#
                      0x04,
                      0x00,
                      0x02,
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x06,
                      0x01,
                      0x00,
                      0x04,
                      0x00,
                      0xaa,
                      0xbb,
                      0x60,
                      0x00,
                      0xe0,
                      0x00,
                      0x00,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                    ]),
              )
              ,
              "ef0001040002020001000601000400aabb6000e000000000800000",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_section_order_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH0 * 4 + Op.EOFCREATE[0] + Op.STOP, max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0007_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  Section.Data(data="aabb")
                
                ],
              )
              ,
              "ef00010100040200010007030001001404000200008000045f5f5f5fec0000ef000101000402000100010400000000800000feaabb",
              None,
              id="eof1_section_order_6"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0008",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      #--- Error: Invalid Types Header ---#
                      0x03,
                      0x00,
                      0x01,
                      0x00,
                      0x14,
                      0x01,
                      0x00,
                      0x04,
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x07,
                      0x04,
                      0x00,
                      0x02,
                      0x00,
                      0xef,
                      0x00,
                      0x01,
                      0x01,
                      0x00,
                      0x04,
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x01,
                      0x04,
                      0x00,
                      0x00,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0xfe,
                      0x00,
                      0x80,
                      0x00,
                      0x04,
                      0x5f,
                      0x5f,
                      0x5f,
                      0x5f,
                      0xec,
                      0x00,
                      0x00,
                      0xaa,
                      0xbb,
                    ]),
              )
              ,
              "ef00010300010014010004020001000704000200ef000101000402000100010400000000800000fe008000045f5f5f5fec0000aabb",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_section_order_7"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0009",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      #--- Error: Invalid Code Header ---#
                      0x03,
                      0x00,
                      0x01,
                      0x00,
                      0x14,
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x07,
                      0x04,
                      0x00,
                      0x02,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x04,
                      0xef,
                      0x00,
                      0x01,
                      0x01,
                      0x00,
                      0x04,
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x01,
                      0x04,
                      0x00,
                      0x00,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0xfe,
                      0x5f,
                      0x5f,
                      0x5f,
                      0x5f,
                      0xec,
                      0x00,
                      0x00,
                      0xaa,
                      0xbb,
                    ]),
              )
              ,
              "ef0001010004030001001402000100070400020000800004ef000101000402000100010400000000800000fe5f5f5f5fec0000aabb",
              EOFException.MISSING_CODE_HEADER,
              id="eof1_section_order_8"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0010",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x07, #   Code Section 0 (Length: 7)
                      0x04, 0x00, 0x02, # Data Length: 2
                      #--- Error: Invalid Terminator ---#
                      0x03,
                      0x00,
                      0x01,
                      0x00,
                      0x14,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x04,
                      0x5f,
                      0x5f,
                      0x5f,
                      0x5f,
                      0xec,
                      0x00,
                      0x00,
                      0xaa,
                      0xbb,
                      0xef,
                      0x00,
                      0x01,
                      0x01,
                      0x00,
                      0x04,
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x01,
                      0x04,
                      0x00,
                      0x00,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0xfe,
                    ]),
              )
              ,
              "ef00010100040200010007040002030001001400008000045f5f5f5fec0000aabbef000101000402000100010400000000800000fe",
              EOFException.MISSING_TERMINATOR,
              id="eof1_section_order_9"
        ),
        
    ]
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
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
