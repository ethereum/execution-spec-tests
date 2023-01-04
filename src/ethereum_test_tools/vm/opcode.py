"""
Ethereum Virtual Machine opcode definitions.
"""
from enum import Enum
from typing import Tuple, Union


class Opcode(bytes):
    """
    Represents a single Opcode instruction in the EVM, with extra
    metadata useful to parametrize tests.

    Parameters
    ----------
    - popped_stack_items: number of items the opcode pops from the stack
    - pushed_stack_items: number of items the opcode pushes to the stack
    - min_stack_height: minimum stack height required by the opcode
    - immediate_length: number of bytes after the opcode in the bytecode
        that represent data
    """

    popped_stack_items: int
    pushed_stack_items: int
    min_stack_height: int
    immediate_length: int
    variable_immediate_length: Tuple[int, ...] | None = None

    def __new__(
        cls,
        opcode_or_byte: Union[int, "Opcode"],
        *,
        popped_stack_items: int = 0,
        pushed_stack_items: int = 0,
        min_stack_height: int = 0,
        immediate_length: int = 0,
        variable_immediate_length: Tuple[int, ...] | None = None
    ):
        """
        Creates a new opcode instance.
        """
        if type(opcode_or_byte) is Opcode:
            # Required because Enum class calls the base class with the
            # instantiated object as parameter.
            return opcode_or_byte
        elif isinstance(opcode_or_byte, int):
            obj = super().__new__(cls, [opcode_or_byte])
            obj.popped_stack_items = popped_stack_items
            obj.pushed_stack_items = pushed_stack_items
            obj.min_stack_height = min_stack_height
            obj.immediate_length = immediate_length
            obj.variable_immediate_length = variable_immediate_length
            return obj

    def get_immediate_item_length(self, i: int) -> int:
        """
        Gets the byte length of an item that forms the immediate data after the
        opcode.
        Only useful for opcodes that have `variable_immediate_length` set.
        For other opcodes simply returns `immediate_length`.
        """
        if (
            self.variable_immediate_length is None
            or len(self.variable_immediate_length) == 0
        ):
            return self.immediate_length

        if i >= len(self.variable_immediate_length):
            return self.variable_immediate_length[-1]
        return self.variable_immediate_length[i]

    def minimum_stack_height(self) -> int:
        """
        Returns the minimum amount of stack items so that opcode execution
        does not produce a stack exception.
        """
        return max([self.min_stack_height, self.popped_stack_items])

    def __call__(self, *data_items: int) -> bytes:
        """
        Makes all opcode instances callable to return a bytes object containing
        the opcode byte plus a formatted data portion.

        This useful to automatically format, e.g., push opcodes and their
        data sections as `Opcodes.PUSH1(0x00)`.

        Data sign is automatically detected but for this reason the range
        of the input must be:
        `[-2^(data_portion_bits-1), 2^(data_portion_bits)]`
        where:
        `data_portion_bits == immediate_length * 8`
        """
        if len(data_items) == 0:
            return self

        data_portion = bytes()
        for i, data in enumerate(data_items):
            immediate_length = self.get_immediate_item_length(i)
            if immediate_length == 0:
                raise OverflowError(
                    "Attempted to append data to an opcode without data"
                    + "portion"
                )

            if data < 0:
                data_portion += data.to_bytes(
                    length=immediate_length, byteorder="big", signed=True
                )
            else:
                data_portion += data.to_bytes(
                    length=immediate_length, byteorder="big", signed=False
                )

        return self + data_portion

    def __len__(self) -> int:
        """
        Returns the total bytecode length of the opcode, taking into account
        its data portion.
        """
        return self.immediate_length + 1

    def __str__(self) -> str:
        """
        Returns the string representation of the opcode.
        """
        return hex(self.int())

    def int(self) -> int:
        """
        Returns the integer representation of the opcode.
        """
        return int.from_bytes(bytes=self, byteorder="big")


class Opcodes(Opcode, Enum):
    """
    Enum containing all known opcodes.

    Contains deprecated and not yet implemented opcodes.

    This enum is !! NOT !! meant to be iterated over by the tests. Instead,
    create a list with cherry-picked opcodes from this Enum within the test
    if iteration is needed.

    Do !! NOT !! remove or modify existing opcodes from this list.
    """

    STOP = Opcode(0x00)
    ADD = Opcode(0x01, popped_stack_items=2, pushed_stack_items=1)
    MUL = Opcode(0x02, popped_stack_items=2, pushed_stack_items=1)
    SUB = Opcode(0x03, popped_stack_items=2, pushed_stack_items=1)
    DIV = Opcode(0x04, popped_stack_items=2, pushed_stack_items=1)
    SDIV = Opcode(0x05, popped_stack_items=2, pushed_stack_items=1)
    MOD = Opcode(0x06, popped_stack_items=2, pushed_stack_items=1)
    SMOD = Opcode(0x07, popped_stack_items=2, pushed_stack_items=1)
    ADDMOD = Opcode(0x08, popped_stack_items=3, pushed_stack_items=1)
    MULMOD = Opcode(0x09, popped_stack_items=3, pushed_stack_items=1)
    EXP = Opcode(0x0A, popped_stack_items=2, pushed_stack_items=1)
    SIGNEXTEND = Opcode(0x0B, popped_stack_items=2, pushed_stack_items=1)

    LT = Opcode(0x10, popped_stack_items=2, pushed_stack_items=1)
    GT = Opcode(0x11, popped_stack_items=2, pushed_stack_items=1)
    SLT = Opcode(0x12, popped_stack_items=2, pushed_stack_items=1)
    SGT = Opcode(0x13, popped_stack_items=2, pushed_stack_items=1)
    EQ = Opcode(0x14, popped_stack_items=2, pushed_stack_items=1)
    ISZERO = Opcode(0x15, popped_stack_items=1, pushed_stack_items=1)
    AND = Opcode(0x16, popped_stack_items=2, pushed_stack_items=1)
    OR = Opcode(0x17, popped_stack_items=2, pushed_stack_items=1)
    XOR = Opcode(0x18, popped_stack_items=2, pushed_stack_items=1)
    NOT = Opcode(0x19, popped_stack_items=1, pushed_stack_items=1)
    BYTE = Opcode(0x1A, popped_stack_items=2, pushed_stack_items=1)
    SHL = Opcode(0x1B, popped_stack_items=2, pushed_stack_items=1)
    SHR = Opcode(0x1C, popped_stack_items=2, pushed_stack_items=1)
    SAR = Opcode(0x1D, popped_stack_items=2, pushed_stack_items=1)

    SHA3 = Opcode(0x20, popped_stack_items=2, pushed_stack_items=1)

    ADDRESS = Opcode(0x30, pushed_stack_items=1)
    BALANCE = Opcode(0x31, popped_stack_items=1, pushed_stack_items=1)
    ORIGIN = Opcode(0x32, pushed_stack_items=1)
    CALLER = Opcode(0x33, pushed_stack_items=1)
    CALLVALUE = Opcode(0x34, pushed_stack_items=1)
    CALLDATALOAD = Opcode(0x35, popped_stack_items=1, pushed_stack_items=1)
    CALLDATASIZE = Opcode(0x36, pushed_stack_items=1)
    CALLDATACOPY = Opcode(0x37, popped_stack_items=3)
    CODESIZE = Opcode(0x38, pushed_stack_items=1)
    CODECOPY = Opcode(0x39, popped_stack_items=3)
    GASPRICE = Opcode(0x3A, pushed_stack_items=1)
    EXTCODESIZE = Opcode(0x3B, popped_stack_items=1, pushed_stack_items=1)
    EXTCODECOPY = Opcode(0x3C, popped_stack_items=4)
    RETURNDATASIZE = Opcode(0x3D, pushed_stack_items=1)
    RETURNDATACOPY = Opcode(0x3E, popped_stack_items=3)
    EXTCODEHASH = Opcode(0x3F, popped_stack_items=1, pushed_stack_items=1)

    BLOCKHASH = Opcode(0x40, popped_stack_items=1, pushed_stack_items=1)
    COINBASE = Opcode(0x41, pushed_stack_items=1)
    TIMESTAMP = Opcode(0x42, pushed_stack_items=1)
    NUMBER = Opcode(0x43, pushed_stack_items=1)
    PREVRANDAO = Opcode(0x44, pushed_stack_items=1)
    GASLIMIT = Opcode(0x45, pushed_stack_items=1)
    CHAINID = Opcode(0x46, pushed_stack_items=1)
    SELFBALANCE = Opcode(0x47, pushed_stack_items=1)
    BASEFEE = Opcode(0x48, pushed_stack_items=1)

    POP = Opcode(0x50, popped_stack_items=1)
    MLOAD = Opcode(0x51, popped_stack_items=1, pushed_stack_items=1)
    MSTORE = Opcode(0x52, popped_stack_items=2)
    MSTORE8 = Opcode(0x53, popped_stack_items=2)
    SLOAD = Opcode(0x54, popped_stack_items=1, pushed_stack_items=1)
    SSTORE = Opcode(0x55, popped_stack_items=2)
    JUMP = Opcode(0x56, popped_stack_items=1)
    JUMPI = Opcode(0x57, popped_stack_items=2)
    PC = Opcode(0x58, pushed_stack_items=1)
    MSIZE = Opcode(0x59, pushed_stack_items=1)
    GAS = Opcode(0x5A, pushed_stack_items=1)
    JUMPDEST = Opcode(0x5B)
    RJUMP = Opcode(0x5C, immediate_length=2)
    RJUMPI = Opcode(0x5D, popped_stack_items=1, immediate_length=2)
    RJUMPV = Opcode(
        0x5E,
        popped_stack_items=1,
        variable_immediate_length=(1, 2),
    )
    CALLF = Opcode(0xB0, immediate_length=2)
    RETF = Opcode(0xB1)

    PUSH0 = Opcode(0x5F, pushed_stack_items=1)
    PUSH1 = Opcode(0x60, pushed_stack_items=1, immediate_length=1)
    PUSH2 = Opcode(0x61, pushed_stack_items=1, immediate_length=2)
    PUSH3 = Opcode(0x62, pushed_stack_items=1, immediate_length=3)
    PUSH4 = Opcode(0x63, pushed_stack_items=1, immediate_length=4)
    PUSH5 = Opcode(0x64, pushed_stack_items=1, immediate_length=5)
    PUSH6 = Opcode(0x65, pushed_stack_items=1, immediate_length=6)
    PUSH7 = Opcode(0x66, pushed_stack_items=1, immediate_length=7)
    PUSH8 = Opcode(0x67, pushed_stack_items=1, immediate_length=8)
    PUSH9 = Opcode(0x68, pushed_stack_items=1, immediate_length=9)
    PUSH10 = Opcode(0x69, pushed_stack_items=1, immediate_length=10)
    PUSH11 = Opcode(0x6A, pushed_stack_items=1, immediate_length=11)
    PUSH12 = Opcode(0x6B, pushed_stack_items=1, immediate_length=12)
    PUSH13 = Opcode(0x6C, pushed_stack_items=1, immediate_length=13)
    PUSH14 = Opcode(0x6D, pushed_stack_items=1, immediate_length=14)
    PUSH15 = Opcode(0x6E, pushed_stack_items=1, immediate_length=15)
    PUSH16 = Opcode(0x6F, pushed_stack_items=1, immediate_length=16)
    PUSH17 = Opcode(0x70, pushed_stack_items=1, immediate_length=17)
    PUSH18 = Opcode(0x71, pushed_stack_items=1, immediate_length=18)
    PUSH19 = Opcode(0x72, pushed_stack_items=1, immediate_length=19)
    PUSH20 = Opcode(0x73, pushed_stack_items=1, immediate_length=20)
    PUSH21 = Opcode(0x74, pushed_stack_items=1, immediate_length=21)
    PUSH22 = Opcode(0x75, pushed_stack_items=1, immediate_length=22)
    PUSH23 = Opcode(0x76, pushed_stack_items=1, immediate_length=23)
    PUSH24 = Opcode(0x77, pushed_stack_items=1, immediate_length=24)
    PUSH25 = Opcode(0x78, pushed_stack_items=1, immediate_length=25)
    PUSH26 = Opcode(0x79, pushed_stack_items=1, immediate_length=26)
    PUSH27 = Opcode(0x7A, pushed_stack_items=1, immediate_length=27)
    PUSH28 = Opcode(0x7B, pushed_stack_items=1, immediate_length=28)
    PUSH29 = Opcode(0x7C, pushed_stack_items=1, immediate_length=29)
    PUSH30 = Opcode(0x7D, pushed_stack_items=1, immediate_length=30)
    PUSH31 = Opcode(0x7E, pushed_stack_items=1, immediate_length=31)
    PUSH32 = Opcode(0x7F, pushed_stack_items=1, immediate_length=32)

    DUP1 = Opcode(0x80, pushed_stack_items=1, min_stack_height=1)
    DUP2 = Opcode(0x81, pushed_stack_items=1, min_stack_height=2)
    DUP3 = Opcode(0x82, pushed_stack_items=1, min_stack_height=3)
    DUP4 = Opcode(0x83, pushed_stack_items=1, min_stack_height=4)
    DUP5 = Opcode(0x84, pushed_stack_items=1, min_stack_height=5)
    DUP6 = Opcode(0x85, pushed_stack_items=1, min_stack_height=6)
    DUP7 = Opcode(0x86, pushed_stack_items=1, min_stack_height=7)
    DUP8 = Opcode(0x87, pushed_stack_items=1, min_stack_height=8)
    DUP9 = Opcode(0x88, pushed_stack_items=1, min_stack_height=9)
    DUP10 = Opcode(0x89, pushed_stack_items=1, min_stack_height=10)
    DUP11 = Opcode(0x8A, pushed_stack_items=1, min_stack_height=11)
    DUP12 = Opcode(0x8B, pushed_stack_items=1, min_stack_height=12)
    DUP13 = Opcode(0x8C, pushed_stack_items=1, min_stack_height=13)
    DUP14 = Opcode(0x8D, pushed_stack_items=1, min_stack_height=14)
    DUP15 = Opcode(0x8E, pushed_stack_items=1, min_stack_height=15)
    DUP16 = Opcode(0x8F, pushed_stack_items=1, min_stack_height=16)

    SWAP1 = Opcode(0x90, min_stack_height=2)
    SWAP2 = Opcode(0x91, min_stack_height=3)
    SWAP3 = Opcode(0x92, min_stack_height=4)
    SWAP4 = Opcode(0x93, min_stack_height=5)
    SWAP5 = Opcode(0x94, min_stack_height=6)
    SWAP6 = Opcode(0x95, min_stack_height=7)
    SWAP7 = Opcode(0x96, min_stack_height=8)
    SWAP8 = Opcode(0x97, min_stack_height=9)
    SWAP9 = Opcode(0x98, min_stack_height=10)
    SWAP10 = Opcode(0x99, min_stack_height=11)
    SWAP11 = Opcode(0x9A, min_stack_height=12)
    SWAP12 = Opcode(0x9B, min_stack_height=13)
    SWAP13 = Opcode(0x9C, min_stack_height=14)
    SWAP14 = Opcode(0x9D, min_stack_height=15)
    SWAP15 = Opcode(0x9E, min_stack_height=16)
    SWAP16 = Opcode(0x9F, min_stack_height=17)

    LOG0 = Opcode(0xA0, popped_stack_items=2)
    LOG1 = Opcode(0xA1, popped_stack_items=3)
    LOG2 = Opcode(0xA2, popped_stack_items=4)
    LOG3 = Opcode(0xA3, popped_stack_items=5)
    LOG4 = Opcode(0xA4, popped_stack_items=6)

    TLOAD = Opcode(0xB3, popped_stack_items=1, pushed_stack_items=1)
    TSTORE = Opcode(0xB4, popped_stack_items=2)

    CREATE = Opcode(0xF0, popped_stack_items=3, pushed_stack_items=1)
    CALL = Opcode(0xF1, popped_stack_items=7, pushed_stack_items=1)
    CALLCODE = Opcode(0xF2, popped_stack_items=7, pushed_stack_items=1)
    RETURN = Opcode(0xF3, popped_stack_items=2)
    DELEGATECALL = Opcode(0xF4, popped_stack_items=6, pushed_stack_items=1)
    CREATE2 = Opcode(0xF5, popped_stack_items=4, pushed_stack_items=1)

    STATICCALL = Opcode(0xFA, popped_stack_items=6, pushed_stack_items=1)

    REVERT = Opcode(0xFD, popped_stack_items=2)
    INVALID = Opcode(0xFE)

    SELFDESTRUCT = Opcode(0xFF, popped_stack_items=1)
    SENDALL = Opcode(0xFF, popped_stack_items=1)


OPCODE_MAP = {
    0x00: Opcodes.STOP,
    0x01: Opcodes.ADD,
    0x02: Opcodes.MUL,
    0x03: Opcodes.SUB,
    0x04: Opcodes.DIV,
    0x05: Opcodes.SDIV,
    0x06: Opcodes.MOD,
    0x07: Opcodes.SMOD,
    0x08: Opcodes.ADDMOD,
    0x09: Opcodes.MULMOD,
    0x0A: Opcodes.EXP,
    0x0B: Opcodes.SIGNEXTEND,
    0x10: Opcodes.LT,
    0x11: Opcodes.GT,
    0x12: Opcodes.SLT,
    0x13: Opcodes.SGT,
    0x14: Opcodes.EQ,
    0x15: Opcodes.ISZERO,
    0x16: Opcodes.AND,
    0x17: Opcodes.OR,
    0x18: Opcodes.XOR,
    0x19: Opcodes.NOT,
    0x1A: Opcodes.BYTE,
    0x1B: Opcodes.SHL,
    0x1C: Opcodes.SHR,
    0x1D: Opcodes.SAR,
    0x20: Opcodes.SHA3,
    0x30: Opcodes.ADDRESS,
    0x31: Opcodes.BALANCE,
    0x32: Opcodes.ORIGIN,
    0x33: Opcodes.CALLER,
    0x34: Opcodes.CALLVALUE,
    0x35: Opcodes.CALLDATALOAD,
    0x36: Opcodes.CALLDATASIZE,
    0x37: Opcodes.CALLDATACOPY,
    0x38: Opcodes.CODESIZE,
    0x39: Opcodes.CODECOPY,
    0x3A: Opcodes.GASPRICE,
    0x3B: Opcodes.EXTCODESIZE,
    0x3C: Opcodes.EXTCODECOPY,
    0x3D: Opcodes.RETURNDATASIZE,
    0x3E: Opcodes.RETURNDATACOPY,
    0x3F: Opcodes.EXTCODEHASH,
    0x40: Opcodes.BLOCKHASH,
    0x41: Opcodes.COINBASE,
    0x42: Opcodes.TIMESTAMP,
    0x43: Opcodes.NUMBER,
    0x44: Opcodes.PREVRANDAO,
    0x45: Opcodes.GASLIMIT,
    0x46: Opcodes.CHAINID,
    0x47: Opcodes.SELFBALANCE,
    0x48: Opcodes.BASEFEE,
    0x50: Opcodes.POP,
    0x51: Opcodes.MLOAD,
    0x52: Opcodes.MSTORE,
    0x53: Opcodes.MSTORE8,
    0x54: Opcodes.SLOAD,
    0x55: Opcodes.SSTORE,
    0x56: Opcodes.JUMP,
    0x57: Opcodes.JUMPI,
    0x58: Opcodes.PC,
    0x59: Opcodes.MSIZE,
    0x5A: Opcodes.GAS,
    0x5B: Opcodes.JUMPDEST,
    0x5C: Opcodes.RJUMP,
    0x5D: Opcodes.RJUMPI,
    0x5E: Opcodes.RJUMPV,
    0xB0: Opcodes.CALLF,
    0xB1: Opcodes.RETF,
    0x5F: Opcodes.PUSH0,
    0x60: Opcodes.PUSH1,
    0x61: Opcodes.PUSH2,
    0x62: Opcodes.PUSH3,
    0x63: Opcodes.PUSH4,
    0x64: Opcodes.PUSH5,
    0x65: Opcodes.PUSH6,
    0x66: Opcodes.PUSH7,
    0x67: Opcodes.PUSH8,
    0x68: Opcodes.PUSH9,
    0x69: Opcodes.PUSH10,
    0x6A: Opcodes.PUSH11,
    0x6B: Opcodes.PUSH12,
    0x6C: Opcodes.PUSH13,
    0x6D: Opcodes.PUSH14,
    0x6E: Opcodes.PUSH15,
    0x6F: Opcodes.PUSH16,
    0x70: Opcodes.PUSH17,
    0x71: Opcodes.PUSH18,
    0x72: Opcodes.PUSH19,
    0x73: Opcodes.PUSH20,
    0x74: Opcodes.PUSH21,
    0x75: Opcodes.PUSH22,
    0x76: Opcodes.PUSH23,
    0x77: Opcodes.PUSH24,
    0x78: Opcodes.PUSH25,
    0x79: Opcodes.PUSH26,
    0x7A: Opcodes.PUSH27,
    0x7B: Opcodes.PUSH28,
    0x7C: Opcodes.PUSH29,
    0x7D: Opcodes.PUSH30,
    0x7E: Opcodes.PUSH31,
    0x7F: Opcodes.PUSH32,
    0x80: Opcodes.DUP1,
    0x81: Opcodes.DUP2,
    0x82: Opcodes.DUP3,
    0x83: Opcodes.DUP4,
    0x84: Opcodes.DUP5,
    0x85: Opcodes.DUP6,
    0x86: Opcodes.DUP7,
    0x87: Opcodes.DUP8,
    0x88: Opcodes.DUP9,
    0x89: Opcodes.DUP10,
    0x8A: Opcodes.DUP11,
    0x8B: Opcodes.DUP12,
    0x8C: Opcodes.DUP13,
    0x8D: Opcodes.DUP14,
    0x8E: Opcodes.DUP15,
    0x8F: Opcodes.DUP16,
    0x90: Opcodes.SWAP1,
    0x91: Opcodes.SWAP2,
    0x92: Opcodes.SWAP3,
    0x93: Opcodes.SWAP4,
    0x94: Opcodes.SWAP5,
    0x95: Opcodes.SWAP6,
    0x96: Opcodes.SWAP7,
    0x97: Opcodes.SWAP8,
    0x98: Opcodes.SWAP9,
    0x99: Opcodes.SWAP10,
    0x9A: Opcodes.SWAP11,
    0x9B: Opcodes.SWAP12,
    0x9C: Opcodes.SWAP13,
    0x9D: Opcodes.SWAP14,
    0x9E: Opcodes.SWAP15,
    0x9F: Opcodes.SWAP16,
    0xA0: Opcodes.LOG0,
    0xA1: Opcodes.LOG1,
    0xA2: Opcodes.LOG2,
    0xA3: Opcodes.LOG3,
    0xA4: Opcodes.LOG4,
    0xB3: Opcodes.TLOAD,
    0xB4: Opcodes.TSTORE,
    0xF0: Opcodes.CREATE,
    0xF1: Opcodes.CALL,
    0xF2: Opcodes.CALLCODE,
    0xF3: Opcodes.RETURN,
    0xF4: Opcodes.DELEGATECALL,
    0xF5: Opcodes.CREATE2,
    0xFA: Opcodes.STATICCALL,
    0xFD: Opcodes.REVERT,
    0xFE: Opcodes.INVALID,
    0xFF: Opcodes.SENDALL,
}
