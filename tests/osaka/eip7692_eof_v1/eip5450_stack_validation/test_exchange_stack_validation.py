""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "9c7c91bf7b9b7af9e76248f7921a03ddc17f99ef"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[0] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80000",
              None,
              id="exchange_stack_validation_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[16] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81000",
              None,
              id="exchange_stack_validation_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[1] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80100",
              None,
              id="exchange_stack_validation_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[32] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e82000",
              None,
              id="exchange_stack_validation_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[2] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80200",
              None,
              id="exchange_stack_validation_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[112] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e87000",
              None,
              id="exchange_stack_validation_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[7] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80700",
              None,
              id="exchange_stack_validation_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[17] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81100",
              None,
              id="exchange_stack_validation_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[52] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e83400",
              None,
              id="exchange_stack_validation_8"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[67] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e84300",
              None,
              id="exchange_stack_validation_9"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0011',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[22] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81600",
              None,
              id="exchange_stack_validation_10"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0012',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[97] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e86100",
              None,
              id="exchange_stack_validation_11"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0013',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[128] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e88000",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_12"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0014',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[8] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80800",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_13"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0015',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[113] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e87100",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_14"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0016',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[23] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81700",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_15"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0017',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[68] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e84400",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_16"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0018',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[83] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e85300",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_17"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0019',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[53] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e83500",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_18"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0020',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[238] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ee00",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_19"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0021',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[239] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ef00",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_20"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0022',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[254] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8fe00",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_21"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0023',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 10 + Op.EXCHANGE[255] + Op.STOP, max_stack_height=10),
                    ],
              )
              ,
              "ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ff00",
              EOFException.STACK_UNDERFLOW,
              id="exchange_stack_validation_22"
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
