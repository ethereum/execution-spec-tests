"""Common conversion methods."""

from re import sub
from typing import Any, List, Optional, SupportsBytes, TypeAlias

BytesConvertible: TypeAlias = str | bytes | SupportsBytes | List[int]
FixedSizeBytesConvertible: TypeAlias = str | bytes | SupportsBytes | List[int] | int
NumberConvertible: TypeAlias = str | bytes | SupportsBytes | int


def int_or_none(value: Any, default: Optional[int] = None) -> int | None:
    """Convert a value to int or returns a default (None)."""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    return int(value, 0)


def str_or_none(value: Any, default: Optional[str] = None) -> str | None:
    """Convert a value to string or returns a default (None)."""
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return str(value)


def to_bytes(value: BytesConvertible) -> bytes:
    """Convert multiple types into bytes."""
    if value is None:
        raise Exception("Cannot convert `None` input to `bytes`")

    if isinstance(value, SupportsBytes) or isinstance(value, bytes) or isinstance(value, list):
        return bytes(value)

    if isinstance(value, str):
        # We can have a hex representation of bytes with spaces for readability
        value = sub(r"\s+", "", value)
        if value.startswith("0x"):
            value = value[2:]
        if len(value) % 2 == 1:
            value = "0" + value
        return bytes.fromhex(value)

    raise Exception("Invalid type for `bytes`")


def to_fixed_size_bytes(value: FixedSizeBytesConvertible, size: int) -> bytes:
    """Convert multiple types into fixed-size bytes."""
    if isinstance(value, int):
        return int.to_bytes(value, length=size, byteorder="big", signed=value < 0)
    value = to_bytes(value)
    if len(value) > size:
        raise Exception(f"Input is too large for fixed size bytes: {len(value)} > {size}")
    return bytes(value).rjust(size, b"\x00")


def to_hex(value: BytesConvertible) -> str:
    """Convert multiple types into a bytes hex string."""
    return "0x" + to_bytes(value).hex()


def to_number(value: NumberConvertible) -> int:
    """Convert multiple types into a number."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    if isinstance(value, bytes) or isinstance(value, SupportsBytes):
        return int.from_bytes(value, byteorder="big")
    raise Exception("Invalid type for `number`")


def to_fixed_size_hex(value: FixedSizeBytesConvertible, size: int) -> str:
    """Convert multiple types into a bytes hex string."""
    return "0x" + to_fixed_size_bytes(value, size).hex()
