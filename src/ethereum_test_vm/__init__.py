"""
Ethereum Virtual Machine related definitions and utilities.
"""

from .bytecode import Bytecode
from .evm_types import EVMCodeType
from .opcode import Macro, Macros, Opcode, OpcodeCallArg, Opcodes, UndefinedOpcodes

__all__ = (
    "Bytecode",
    "EVMCodeType",
    "Macro",
    "Macros",
    "Opcode",
    "OpcodeCallArg",
    "Opcodes",
    "UndefinedOpcodes",
)
