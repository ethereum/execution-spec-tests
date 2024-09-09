"""
Helper functions/classes used to generate Ethereum tests.
"""

from typing import List

from ethereum_test_types.verkle.types import Hash


def chunkify_code(code: bytes) -> List[Hash]:
    """
    Verkle utility function to chunkify account code into 32-byte chunks.

    Used to generate code chunks for Witness state diff verification.
    """
    code = bytes(code)
    if len(code) % 31 != 0:
        code += b"\x00" * (31 - (len(code) % 31))
    bytes_to_exec_data = [0] * (len(code) + 32)
    pos = 0
    while pos < len(code):
        # if PUSH1 <= code[pos] <= PUSH32
        if 0x60 <= code[pos] <= 0x7F:
            push_data_bytes = code[pos] - 0x5F  # PUSH_OFFSET
        else:
            push_data_bytes = 0
        pos += 1
        for x in range(push_data_bytes):
            bytes_to_exec_data[pos + x] = push_data_bytes - x
        pos += push_data_bytes

    chunks = []
    for pos in range(0, len(code), 31):
        exec_data_prefix = bytes([min(bytes_to_exec_data[pos], 31)])
        chunk = exec_data_prefix + code[pos : pos + 31]
        chunk = chunk.ljust(32, b"\x00")
        chunks.append(Hash(chunk))
    return chunks
