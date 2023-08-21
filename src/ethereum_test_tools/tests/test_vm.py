"""
Test suite for `ethereum_test_tools.vm` module.
"""

from typing import Tuple

import pytest

from ..vm.opcode import Opcodes as Op
from ..vm.opcode import _rjumpv_encoder


@pytest.mark.parametrize(
    "opcodes,expected",
    [
        (
            Op.PUSH1(0x01),
            bytes(
                [
                    0x60,
                    0x01,
                ]
            ),
        ),
        (
            Op.PUSH1("0x01"),
            bytes(
                [
                    0x60,
                    0x01,
                ]
            ),
        ),
        (
            Op.PUSH1(0xFF),
            bytes(
                [
                    0x60,
                    0xFF,
                ]
            ),
        ),
        (
            Op.PUSH1(-1),
            bytes(
                [
                    0x60,
                    0xFF,
                ]
            ),
        ),
        (
            Op.PUSH1(-2),
            bytes(
                [
                    0x60,
                    0xFE,
                ]
            ),
        ),
        (
            Op.PUSH20(0x01),
            bytes([0x73] + [0x00] * 19 + [0x01]),
        ),
        (
            Op.PUSH32(0xFF),
            bytes([0x7F] + [0x00] * 31 + [0xFF]),
        ),
        (
            Op.PUSH32(-1),
            bytes([0x7F] + [0xFF] * 32),
        ),
        (
            Op.SSTORE(
                -1,
                Op.CALL(
                    Op.GAS,
                    Op.ADDRESS,
                    Op.PUSH1(0x20),
                    0,
                    0,
                    0x20,
                    0x1234,
                ),
            ),
            bytes(
                [
                    0x61,
                    0x12,
                    0x34,
                    0x60,
                    0x20,
                    0x60,
                    0x00,
                    0x60,
                    0x00,
                    0x60,
                    0x20,
                    0x30,
                    0x5A,
                    0xF1,
                    0x7F,
                ]
                + [0xFF] * 32
                + [0x55]
            ),
        ),
    ],
)
def test_opcodes(opcodes: bytes, expected: bytes):
    """
    Test that the `opcodes` are transformed into bytecode as expected.
    """
    assert bytes(opcodes) == expected


def test_opcodes_repr():
    """
    Test that the `repr` of an `Op` is the same as its name.
    """
    assert f"{Op.CALL}" == "CALL"
    assert f"{Op.DELEGATECALL}" == "DELEGATECALL"
    assert str(Op.ADD) == "ADD"


@pytest.mark.parametrize(
    "inputs,expected",
    [
        (
            (1, 2, 3),
            bytes(
                [
                    0x03,
                    0x00,
                    0x01,
                    0x00,
                    0x02,
                    0x00,
                    0x03,
                ]
            ),
        ),
        (
            (),
            bytes(
                [
                    0x00,
                ]
            ),
        ),
        (
            (-1, -2, -3),
            bytes(
                [
                    0x03,
                    0xFF,
                    0xFF,
                    0xFF,
                    0xFE,
                    0xFF,
                    0xFD,
                ]
            ),
        ),
    ],
)
def test_rjumpv_encoder(inputs: Tuple[int, ...], expected: bytes):
    """
    Test RJUMPV encoder.
    """
    assert bytes(_rjumpv_encoder(*inputs)) == expected
