"""
Common conversion methods.
"""

from re import sub
from typing import Any, Callable, Optional, SupportsBytes, TypeAlias

BytesConvertible: TypeAlias = str | bytes | SupportsBytes
FixedSizeBytesConvertible: TypeAlias = str | bytes | SupportsBytes | int
NumberConvertible: TypeAlias = str | bytes | SupportsBytes | int


def int_or_none(input: Any, default: Optional[int] = None) -> int | None:
    """
    Converts an input to int or returns a default (None).
    """
    if input is None:
        return default
    if isinstance(input, int):
        return input
    return int(input, 0)


def str_or_none(input: Any, default: Optional[str] = None) -> str | None:
    """
    Converts an input to string or returns a default (None).
    """
    if input is None:
        return default
    if isinstance(input, str):
        return input
    return str(input)


def to_hex_number(input: NumberConvertible) -> int:
    """
    Convert a hex number to an integer
    """
    if isinstance(input, int):
        return input
    if isinstance(input, str):
        return int(input, 0)
    if isinstance(input, bytes) or isinstance(input, SupportsBytes):
        return int.from_bytes(input, byteorder="big")
    raise Exception("invalid type for `number`")


def from_hex_number(input: int) -> str:
    """
    Convert an integer to a hex number
    """
    assert isinstance(input, int)
    return f"0x{input:x}"


def to_bytes(input: BytesConvertible) -> bytes:
    """
    Convert a string to bytes
    """
    if isinstance(input, SupportsBytes) or isinstance(input, bytes):
        return bytes(input)

    if isinstance(input, str):
        # We can have a hex representation of bytes with spaces for
        # readability
        input = sub(r"\s+", "", input)
        if input.startswith("0x"):
            input = input[2:]
        if len(input) % 2 == 1:
            input = "0" + input
        return bytes.fromhex(input)

    raise Exception("invalid type for `bytes`")


def from_bytes(input: bytes) -> str:
    """
    Convert a bytes to a string
    """
    assert isinstance(input, bytes)
    return f"0x{input.hex()}"


def from_fixed_size_bytes(size: int) -> Callable[[FixedSizeBytesConvertible], bytes]:
    """
    Convert a bytes to a fixed size bytes
    """

    def _from_fixed_bytes(input: FixedSizeBytesConvertible) -> bytes:
        if isinstance(input, int):
            return int.to_bytes(input, length=size, byteorder="big")
        input = to_bytes(input)
        if len(input) > size:
            raise Exception(f"input is too large for fixed size bytes: {len(input)} > {size}")
        return bytes(input).rjust(size, b"\x00")

    return _from_fixed_bytes


def to_fixed_size_bytes(size: int) -> Callable[[bytes], str]:
    """
    Convert a fixed size bytes to a string
    """

    def _to_fixed_bytes(input: bytes) -> str:
        assert isinstance(input, bytes)
        assert len(input) == size
        return f"0x{input.hex()}"

    return _to_fixed_bytes
