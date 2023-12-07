"""
Define an entry point wrapper for pytest.
"""

import sys
from typing import List, Optional

from ethereum_test_tools import Opcodes as Op


def main():  # noqa: D103
    evm_bytes_hex_string = sys.argv[1]
    if evm_bytes_hex_string.startswith("0x"):
        evm_bytes_hex_string = evm_bytes_hex_string[2:]

    evm_bytes = bytearray(bytes.fromhex(evm_bytes_hex_string))

    opcodes_strings: List[str] = []

    while evm_bytes:
        opcode_byte = evm_bytes.pop(0)

        opcode: Optional[Op] = None
        for op in Op:
            if op.int() == opcode_byte:
                opcode = op
                break

        if opcode is None:
            raise ValueError(f"Unknown opcode: {opcode_byte}")

        if opcode.data_portion_length > 0:
            data_portion = evm_bytes[: opcode.data_portion_length]
            evm_bytes = evm_bytes[opcode.data_portion_length :]
            opcodes_strings.append(f'Op.{opcode._name_}("0x{data_portion.hex()}")')
        else:
            opcodes_strings.append(f"Op.{opcode._name_}")

    print(" + ".join(opcodes_strings))


if __name__ == "__main__":
    main()
