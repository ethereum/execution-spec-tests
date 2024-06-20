"""
EOF v1 validation code
"""

import pytest
from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools import EOFException, Opcodes as Op, UndefinedOpcodes as UOp
from ethereum_test_tools.eof.v1 import Container, ContainerKind, Section

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        
        pytest.param(
                Container(
                    name="EOF1V00001",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x00] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80000",
                None,
                id="exchange_stack_validation_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x10] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81000",
                None,
                id="exchange_stack_validation_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x01] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80100",
                None,
                id="exchange_stack_validation_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x20] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e82000",
                None,
                id="exchange_stack_validation_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x02] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80200",
                None,
                id="exchange_stack_validation_5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x70] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e87000",
                None,
                id="exchange_stack_validation_6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x07] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80700",
                None,
                id="exchange_stack_validation_7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x11] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81100",
                None,
                id="exchange_stack_validation_8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x34] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e83400",
                None,
                id="exchange_stack_validation_9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x43] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e84300",
                None,
                id="exchange_stack_validation_10",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x16] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81600",
                None,
                id="exchange_stack_validation_11",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00012",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x61] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e86100",
                None,
                id="exchange_stack_validation_12",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00013",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x80] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e88000",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_13",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00014",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x08] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80800",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_14",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00015",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x71] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e87100",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_15",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00016",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x17] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81700",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_16",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00017",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x44] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e84400",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_17",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00018",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x53] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e85300",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_18",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00019",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0x35] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e83500",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_19",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00020",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0xee] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ee00",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_20",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00021",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0xef] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ef00",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_21",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00022",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0xfe] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8fe00",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_22",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00023",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 10 + Op.EXCHANGE[0xff] + Op.STOP, max_stack_height=10),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ff00",
                EOFException.STACK_UNDERFLOW,
                id="exchange_stack_validation_23",
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
    if expected_hex_bytecode[0:2] == "0x":
        expected_hex_bytecode = expected_hex_bytecode[2:]
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
