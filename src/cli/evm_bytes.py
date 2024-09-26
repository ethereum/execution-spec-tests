"""
Define an entry point wrapper for pytest.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import click

from ethereum_test_base_types import ZeroPaddedHexNumber
from ethereum_test_vm import Macro
from ethereum_test_vm import Opcodes as Op

OPCODES_WITH_EMPTY_LINES_AFTER = {
    Op.STOP,
    Op.REVERT,
    Op.INVALID,
    Op.JUMP,
    Op.JUMPI,
}

OPCODES_WITH_EMPTY_LINES_BEFORE = {
    Op.JUMPDEST,
}


@dataclass(kw_only=True)
class OpcodeWithOperands:
    """Simple opcode with its operands."""

    opcode: Op | None
    operands: List[int] = field(default_factory=list)

    def format(self, assembly: bool) -> str:
        """Format the opcode with its operands."""
        if self.opcode is None:
            return ""
        if assembly:
            return self.format_assembly()
        if self.operands:
            operands = ", ".join(hex(operand) for operand in self.operands)
            return f"Op.{self.opcode._name_}[{operands}]"
        return f"Op.{self.opcode._name_}"

    def format_assembly(self) -> str:
        """Format the opcode with its operands as assembly."""
        if self.opcode is None:
            return ""
        opcode_name = self.opcode._name_.lower()
        if self.opcode.data_portion_length == 0:
            return f"{opcode_name}"
        elif self.opcode == Op.RJUMPV:
            operands = ", ".join(str(ZeroPaddedHexNumber(operand)) for operand in self.operands)
            return f"{opcode_name} {operands}"
        else:
            operands = ", ".join(str(ZeroPaddedHexNumber(operand)) for operand in self.operands)
            return f"{opcode_name} {operands}"


def process_evm_bytes(evm_bytes: bytes, assembly: bool = False) -> str:  # noqa: D103
    evm_bytes = bytearray(evm_bytes)

    opcodes: List[OpcodeWithOperands] = []

    while evm_bytes:
        opcode_byte = evm_bytes.pop(0)

        opcode: Op
        for op in Op:
            if not isinstance(op, Macro) and op.int() == opcode_byte:
                opcode = op
                break
        else:
            raise ValueError(f"Unknown opcode: {opcode_byte}")

        if opcode.data_portion_length > 0:
            opcodes.append(
                OpcodeWithOperands(
                    opcode=opcode,
                    operands=[int.from_bytes(evm_bytes[: opcode.data_portion_length], "big")],
                )
            )
            evm_bytes = evm_bytes[opcode.data_portion_length :]
        elif opcode == Op.RJUMPV:
            max_index = evm_bytes.pop(0)
            operands: List[int] = []
            for _ in range(max_index + 1):
                operands.append(int.from_bytes(evm_bytes[:2], "big"))
                evm_bytes = evm_bytes[2:]
        else:
            opcodes.append(OpcodeWithOperands(opcode=opcode))

    if assembly:
        opcodes_with_empty_lines: List[OpcodeWithOperands] = []
        for i, op_with_operands in enumerate(opcodes):
            if (
                op_with_operands.opcode in OPCODES_WITH_EMPTY_LINES_BEFORE
                and len(opcodes_with_empty_lines) > 0
                and opcodes_with_empty_lines[-1].opcode is not None
            ):
                opcodes_with_empty_lines.append(OpcodeWithOperands(opcode=None))
            opcodes_with_empty_lines.append(op_with_operands)
            if op_with_operands.opcode in OPCODES_WITH_EMPTY_LINES_AFTER and i < len(opcodes) - 1:
                opcodes_with_empty_lines.append(OpcodeWithOperands(opcode=None))
        return "\n".join(op.format(assembly) for op in opcodes_with_empty_lines)
    return " + ".join(op.format(assembly) for op in opcodes)


@click.command()
@click.option("-a", "--assembly", default=False, is_flag=True, help="Output the code as assembly.")
@click.argument("evm_bytes_hex_string_or_binary_file_path")
def main(evm_bytes_hex_string_or_binary_file_path: str, assembly: bool):
    """
    Convert the given EVM bytes hex string to an EEST Opcodes.

    \b
    EVM_BYTES_HEX_STRING: A hex string representing EVM bytes to be processed or a path to a binary
        file containing EVM bytes.
    ASSEMBLY: A flag to indicate whether to output the code as assembly.
    """  # noqa: D301
    if Path(evm_bytes_hex_string_or_binary_file_path).is_file():
        with open(evm_bytes_hex_string_or_binary_file_path, "rb") as f:
            evm_bytes = f.read()
    else:
        if evm_bytes_hex_string_or_binary_file_path.startswith("0x"):
            evm_bytes_hex_string_or_binary_file_path = evm_bytes_hex_string_or_binary_file_path[2:]

        evm_bytes = bytes.fromhex(evm_bytes_hex_string_or_binary_file_path)

    processed_output = process_evm_bytes(evm_bytes, assembly=assembly)
    click.echo(processed_output)


if __name__ == "__main__":
    main()
