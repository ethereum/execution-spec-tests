"""
Test suite for `ethereum_test_types.verkle.helpers` module.
"""

import pytest

from ..helpers import chunkify_code


@pytest.mark.parametrize(
    "code,expected_chunks",
    [
        pytest.param(
            "0x0102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F",
            [
                "0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
            ],
            id="basic-bytecode-no-padding",
        ),
        pytest.param(
            "0x0102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E",
            [
                "0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e00",
            ],
            id="bytecode-with-padding",
        ),
        pytest.param(
            "0x0102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F20212223",
            [
                "0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
                "0x0020212223000000000000000000000000000000000000000000000000000000",
            ],
            id="bytecode-longer-than-31-bytes",
        ),
        pytest.param(
            "0x0102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F20",
            [
                "0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
                "0x0020000000000000000000000000000000000000000000000000000000000000",
            ],
            id="exactly-32-bytes",
        ),
        pytest.param(
            "0x60FF0102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E",
            [
                "0x0060ff0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d",
                "0x001e000000000000000000000000000000000000000000000000000000000000",
            ],
            id="bytecode-with-push1",
        ),
        pytest.param(
            "0x61FFFF0102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E",
            [
                "0x0061ffff0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c",
                "0x001d1e0000000000000000000000000000000000000000000000000000000000",
            ],
            id="bytecode-with-push2",
        ),
        pytest.param(
            "0x01",
            [
                "0x0001000000000000000000000000000000000000000000000000000000000000",
            ],
            id="very-short-bytecode",
        ),
    ],
)
def test_chunkify_code(code: str, expected_chunks: list[str]):
    """
    Test `chunkify_code` from the helpers module.
    """
    code_bytes = bytes.fromhex(code[2:])
    expected_chunks_bytes = [bytes.fromhex(chunk[2:]) for chunk in expected_chunks]
    result = chunkify_code(code_bytes)
    assert len(result) == len(expected_chunks_bytes)
    for i in range(len(result)):
        assert result[i] == expected_chunks_bytes[i]
