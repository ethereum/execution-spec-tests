"""
Test suite for vm.opcode.
"""

from ..vm.opcode import Opcodes as Op


def test_opcode():
    # Test immediate items
    assert bytes([0x60, 0x01]) == Op.PUSH1(1)
    assert bytes([0x7F] + [0x00] * 31 + [0x01]) == Op.PUSH32(1)

    assert bytes([0x5E, 0x01]) == Op.RJUMPV(1)
    assert bytes([0x5E, 0x01, 0x00, 0x02]) == Op.RJUMPV(1, 2)
    assert bytes([0x5E, 0x01, 0x00, 0x02, 0x00, 0x03]) == Op.RJUMPV(1, 2, 3)
    assert bytes([0x5E, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]) == Op.RJUMPV(
        255, 0xFFFF, 0xFFFF
    )
