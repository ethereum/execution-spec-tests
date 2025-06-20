"""Helper functions for the EIP-7907 meter contract code size tests."""

from ethereum_test_tools import Bytecode


def create_large_contract(
    *,
    size: int,
    padding_byte: bytes = b"\0",
    prefix: Bytecode | None = None,
) -> bytes:
    """Create a large contract with the given size and prefix."""
    if prefix is None:
        prefix = Bytecode()
    return bytes(prefix + padding_byte * (size - len(prefix)))
