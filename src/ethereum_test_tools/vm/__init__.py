"""
Ethereum Virtual Machine related definitions and utilities.
"""
from .opcode import Opcode, Opcodes, OpcodeCallArg

__all__ = (
    "Opcode",
    "OpcodeCallArg",
    "Opcodes",
)
