"""
Ethereum Virtual Machine opcode definitions.
"""

from enum import Enum
from typing import List, Union

from ..common.base_types import FixedSizeBytes


def _get_int_size(n: int) -> int:
    """
    Returns the size of an integer in bytes.
    """
    if n < 0:
        # Negative numbers in the EVM are represented as two's complement of 32 bytes
        return 32
    byte_count = 0
    while n:
        byte_count += 1
        n >>= 8
    return byte_count


_push_opcodes_byte_list = [bytes([0x5F + x]) for x in range(33)]


class Opcode(bytes):
    """
    Represents a single Opcode instruction in the EVM, with extra metadata useful to parametrize
    tests.

    Parameters
    ----------
    - popped_stack_items: number of items the opcode pops from the stack
    - pushed_stack_items: number of items the opcode pushes to the stack
    - min_stack_height: minimum stack height required by the opcode
    - data_portion_length: number of bytes after the opcode in the bytecode
        that represent data
    """

    popped_stack_items: int
    pushed_stack_items: int
    min_stack_height: int
    data_portion_length: int
    _name_: str

    def __new__(
        cls,
        opcode_or_byte: Union[int, "Opcode"],
        *,
        popped_stack_items: int = 0,
        pushed_stack_items: int = 0,
        min_stack_height: int = 0,
        data_portion_length: int = 0,
    ):
        """
        Creates a new opcode instance.
        """
        if type(opcode_or_byte) is Opcode:
            # Required because Enum class calls the base class with the instantiated object as
            # parameter.
            return opcode_or_byte
        elif isinstance(opcode_or_byte, int):
            obj = super().__new__(cls, [opcode_or_byte])
            obj.popped_stack_items = popped_stack_items
            obj.pushed_stack_items = pushed_stack_items
            obj.min_stack_height = min_stack_height
            obj.data_portion_length = data_portion_length
            return obj

    def __call__(self, *args_t: Union[int, bytes, str, "Opcode", FixedSizeBytes]) -> bytes:
        """
        Makes all opcode instances callable to return formatted bytecode, which constitutes a data
        portion, that is located after the opcode byte, and pre-opcode bytecode, which is normally
        used to set up the stack.

        This useful to automatically format, e.g., push opcodes and their data sections as
        `Opcodes.PUSH1(0x00)`.

        Data sign is automatically detected but for this reason the range of the input must be:
        `[-2^(data_portion_bits-1), 2^(data_portion_bits)]` where: `data_portion_bits ==
        data_portion_length * 8`

        For the stack, the arguments are set up in the opposite order they are given, so the first
        argument is the last item pushed to the stack.

        The resulting stack arrangement does not take into account opcode stack element
        consumption, so the stack height is not guaranteed to be correct and the user must take
        this into consideration.

        Integers can also be used as stack elements, in which case they are automatically converted
        to PUSH operations, and negative numbers always use a PUSH32 operation.

        `FixedSizeBytes` can also be used as stack elements, which includes `Address` and `Hash`
        types, for each of which a PUSH operation is automatically generated, `PUSH20` and `PUSH32`
        respectively.

        Hex-strings will automatically be converted to bytes.

        """
        args: List[Union[int, bytes, str, "Opcode", FixedSizeBytes]] = list(args_t)
        pre_opcode_bytecode = bytes()
        data_portion = bytes()

        if self.data_portion_length > 0:
            # For opcodes with a data portion, the first argument is the data and the rest of the
            # arguments form the stack.
            if len(args) == 0:
                raise ValueError("Opcode with data portion requires at least one argument")
            data = args.pop(0)
            if isinstance(data, bytes) or isinstance(data, str):
                if isinstance(data, str):
                    if data.startswith("0x"):
                        data = data[2:]
                    data = bytes.fromhex(data)
                assert len(data) <= self.data_portion_length
                data_portion = data.rjust(self.data_portion_length, b"\x00")
            elif isinstance(data, int):
                signed = data < 0
                data_portion = data.to_bytes(
                    length=self.data_portion_length,
                    byteorder="big",
                    signed=signed,
                )
            else:
                raise TypeError("Opcode data portion must be either an int or bytes/hex string")

        # The rest of the arguments conform the stack.
        while len(args) > 0:
            data = args.pop()
            if isinstance(data, int) or isinstance(data, FixedSizeBytes):
                # We are going to push a constant to the stack.
                data_size = 0
                if isinstance(data, int):
                    signed = data < 0
                    data_size = _get_int_size(data)
                    if data_size > 32:
                        raise ValueError("Opcode stack data must be less than 32 bytes")
                    elif data_size == 0:
                        # Pushing 0 is done with the PUSH1 opcode for compatibility reasons.
                        data_size = 1
                    data = data.to_bytes(
                        length=data_size,
                        byteorder="big",
                        signed=signed,
                    )
                elif isinstance(data, FixedSizeBytes):
                    data_size = data.byte_length

                assert isinstance(data, bytes)
                assert data_size > 0
                pre_opcode_bytecode += _push_opcodes_byte_list[data_size]
                pre_opcode_bytecode += data
            elif isinstance(data, bytes) or isinstance(data, str):
                if isinstance(data, str):
                    if data.startswith("0x"):
                        data = data[2:]
                    data = bytes.fromhex(data)
                pre_opcode_bytecode += data

            else:
                raise TypeError("Opcode stack data must be either an int or a bytes/hex string")

        return pre_opcode_bytecode + self + data_portion

    def __len__(self) -> int:
        """
        Returns the total bytecode length of the opcode, taking into account its data portion.
        """
        return self.data_portion_length + 1

    def int(self) -> int:
        """
        Returns the integer representation of the opcode.
        """
        return int.from_bytes(bytes=self, byteorder="big")

    def __str__(self) -> str:
        """
        Return the name of the opcode, assigned at Enum creation.
        """
        return self._name_


OpcodeCallArg = Union[int, bytes, Opcode]


class Opcodes(Opcode, Enum):
    """
    Enum containing all known opcodes.

    Contains deprecated and not yet implemented opcodes.

    This enum is !! NOT !! meant to be iterated over by the tests. Instead, create a list with
    cherry-picked opcodes from this Enum within the test if iteration is needed.

    Do !! NOT !! remove or modify existing opcodes from this list.
    """

    STOP = Opcode(0x00)
    """
    STOP()
    ----

    Description
    ----
    Stop execution.

    Inputs
    ----
    - None

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    0

    Source: [evm.codes/#00](https://www.evm.codes/#00)
    """

    ADD = Opcode(0x01, popped_stack_items=2, pushed_stack_items=1)
    """
    ADD(a, b) = c
    ----

    Description
    ----
    Addition operation

    Inputs
    ----
    - a: first integer value to add
    - b: second integer value to add

    Outputs
    ----
    - c: integer result of the addition modulo 2**256

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#01](https://www.evm.codes/#01)
    """

    MUL = Opcode(0x02, popped_stack_items=2, pushed_stack_items=1)
    """
    MUL(a, b) = c
    ----

    Description
    ----
    Multiplication operation

    Inputs
    ----
    - a: first integer value to multiply
    - b: second integer value to multiply

    Outputs
    ----
    - c: integer result of the multiplication modulo 2**256

    Fork
    ----
    Frontier

    Gas
    ----
    5

    Source: [evm.codes/#02](https://www.evm.codes/#02)
    """

    SUB = Opcode(0x03, popped_stack_items=2, pushed_stack_items=1)
    """
    SUB(a, b) = c
    ----

    Description
    ----
    Subtraction operation

    Inputs
    ----
    - a: first integer value
    - b: second integer value

    Outputs
    ----
    - c: integer result of the subtraction modulo 2**256

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#03](https://www.evm.codes/#03)
    """

    DIV = Opcode(0x04, popped_stack_items=2, pushed_stack_items=1)
    """
    DIV(a, b) = c
    ----

    Description
    ----
    Division operation

    Inputs
    ----
    - a: numerator
    - b: denominator (must be non-zero)

    Outputs
    ----
    - c: integer result of the division

    Fork
    ----
    Frontier

    Gas
    ----
    5

    Source: [evm.codes/#04](https://www.evm.codes/#04)
    """

    SDIV = Opcode(0x05, popped_stack_items=2, pushed_stack_items=1)
    """
    SDIV(a, b) = c
    ----

    Description
    ----
    Signed division operation

    Inputs
    ----
    - a: signed numerator
    - b: signed denominator (must be non-zero)

    Outputs
    ----
    - c: signed integer result of the division

    Fork
    ----
    Frontier

    Gas
    ----
    5

    Source: [evm.codes/#05](https://www.evm.codes/#05)
    """

    MOD = Opcode(0x06, popped_stack_items=2, pushed_stack_items=1)
    """
    MOD(a, b) = c
    ----

    Description
    ----
    Modulo operation

    Inputs
    ----
    - a: integer numerator.
    - b: integer denominator

    Outputs
    ----
    - a % b: integer result of the integer modulo. If the denominator is 0, the result will be 0

    Fork
    ----
    Frontier

    Gas
    ----
    5

    Source: [evm.codes/#06](https://www.evm.codes/#06)
    """

    SMOD = Opcode(0x07, popped_stack_items=2, pushed_stack_items=1)
    """
    SMOD(a, b) = c
    ----

    Description
    ----
    Signed modulo remainder operation

    Inputs
    ----
    - a: integer numerator.
    - b: integer denominator.

    Outputs
    ----
    - a % b: integer result of the signed integer modulo. If the denominator is 0, the result will
      be 0

    Fork
    ----
    Frontier

    Gas
    ----
    5

    Source: [evm.codes/#07](https://www.evm.codes/#07)
    """

    ADDMOD = Opcode(0x08, popped_stack_items=3, pushed_stack_items=1)
    """
    ADDMOD(a, b, c) = d
    ----

    Description
    ----
    Modular addition operation with overflow check

    Inputs
    ----
    - a: first integer value
    - b: second integer value
    - c: integer denominator

    Outputs
    ----
    - (a + b) % N: integer result of the addition followed by a modulo. If the denominator is 0,
      the result will be 0

    Fork
    ----
    Frontier

    Gas
    ----
    8

    Source: [evm.codes/#08](https://www.evm.codes/#08)
    """

    MULMOD = Opcode(0x09, popped_stack_items=3, pushed_stack_items=1)
    """
    MULMOD(a, b, N) = d
    ----

    Description
    ----
    Modulo multiplication operation

    Inputs
    ----
    - a: first integer value to multiply.
    - b: second integer value to multiply.
    - N: integer denominator

    Outputs
    ----
    - d: (a * b) % N: integer result of the multiplication followed by a modulo. If the denominator
      is 0, the result will be 0

    Fork
    ----
    Frontier

    Gas
    ----
    8

    Source: [evm.codes/#09](https://www.evm.codes/#09)
    """

    EXP = Opcode(0x0A, popped_stack_items=2, pushed_stack_items=1)
    """
    EXP(base, exponent) = a ** exponent
    ----

    Description
    ----
    Exponential operation

    Inputs
    ----
    - base: integer base.
    - exponent: integer exponent

    Outputs
    ----
    - a ** exponent: integer result of the exponential operation modulo 2**256

    Fork
    ----
    Frontier

    Gas
    ----
    10

    Source: [evm.codes/#0A](https://www.evm.codes/#0A)
    """

    SIGNEXTEND = Opcode(0x0B, popped_stack_items=2, pushed_stack_items=1)
    """
    SIGNEXTEND(b, x) = y
    ----

    Description
    ----
    Sign extension operation

    Inputs
    ----
    - b: size in byte - 1 of the integer to sign extend
    - x: integer value to sign extend

    Outputs
    ----
    - y: integer result of the sign extend

    Fork
    ----
    Frontier

    Gas
    ----
    5

    Source: [evm.codes/#0B](https://www.evm.codes/#0B)
    """

    LT = Opcode(0x10, popped_stack_items=2, pushed_stack_items=1)
    """
    LT(a, b) = a < b
    ----

    Description
    ----
    Less-than comparison

    Inputs
    ----
    - a: first integer value
    - b: second integer value

    Outputs
    ----
    - a < b: 1 if the left side is smaller, 0 otherwise

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#10](https://www.evm.codes/#10)
    """

    GT = Opcode(0x11, popped_stack_items=2, pushed_stack_items=1)
    """
    GT(a, b) = a > b
    ----

    Description
    ----
    Greater-than comparison

    Inputs
    ----
    - a: left side integer
    - b: right side integer

    Outputs
    ----
    - a > b: 1 if the left side is bigger, 0 otherwise

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#11](https://www.evm.codes/#11)
    """

    SLT = Opcode(0x12, popped_stack_items=2, pushed_stack_items=1)
    """
    SLT(a, b) = a < b
    ----

    Description
    ----
    Signed less-than comparison

    Inputs
    ----
    - a: eft side signed integer
    - b: right side signed integer

    Outputs
    ----
    - a < b: 1 if the left side is smaller, 0 otherwise

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#12](https://www.evm.codes/#12)
    """

    SGT = Opcode(0x13, popped_stack_items=2, pushed_stack_items=1)
    """
    SGT(a, b) = a > b
    ----

    Description
    ----
    Signed greater-than comparison

    Inputs
    ----
    - a:  left side signed integer.
    - b: right side signed integer

    Outputs
    ----
    - a > b: 1 if the left side is bigger, 0 otherwise

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#13](https://www.evm.codes/#13)
    """

    EQ = Opcode(0x14, popped_stack_items=2, pushed_stack_items=1)
    """
    EQ(a, b) = a == b
    ----

    Description
    ----
    Equality comparison

    Inputs
    ----
    - a: left side integer
    - b: right side integer

    Outputs
    ----
    - a == b: 1 if the left side is equal to the right side, 0 otherwise

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#14](https://www.evm.codes/#14)
    """

    ISZERO = Opcode(0x15, popped_stack_items=1, pushed_stack_items=1)
    """
    ISZERO(a) = a == 0
    ----

    Description
    ----
    Is-zero comparison

    Inputs
    ----
    - a: integer

    Outputs
    ----
    - a == 0: 1 if a is 0, 0 otherwise

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#15](https://www.evm.codes/#15)
    """

    AND = Opcode(0x16, popped_stack_items=2, pushed_stack_items=1)
    """
    AND(a, b) = a & b
    ----

    Description
    ----
    Bitwise AND operation

    Inputs
    ----
    - a: first binary value.
    - b: second binary value

    Outputs
    ----
    - a & b: the bitwise AND result

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#16](https://www.evm.codes/#16)
    """

    OR = Opcode(0x17, popped_stack_items=2, pushed_stack_items=1)
    """
    OR(a, b) = a | b
    ----

    Description
    ----
    Bitwise OR operation

    Inputs
    ----
    - a: first binary value
    - b: second binary value

    Outputs
    ----
    - a | b: the bitwise OR result

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#17](https://www.evm.codes/#17)
    """

    XOR = Opcode(0x18, popped_stack_items=2, pushed_stack_items=1)
    """
    XOR(a, b) = a ^ b
    ----

    Description
    ----
    Bitwise XOR operation

    Inputs
    ----
    - a:  first binary value
    - b: second binary value

    Outputs
    ----
    - a ^ b: the bitwise XOR result

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#18](https://www.evm.codes/#18)
    """

    NOT = Opcode(0x19, popped_stack_items=1, pushed_stack_items=1)
    """
    NOT(a) = ~a
    ----

    Description
    ----
    Bitwise NOT operation

    Inputs
    ----
    - a: binary value

    Outputs
    ----
    - ~a: the bitwise NOT result

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#19](https://www.evm.codes/#19)
    """

    BYTE = Opcode(0x1A, popped_stack_items=2, pushed_stack_items=1)
    """
    BYTE(i, x) = y
    ----

    Description
    ----
    Extract a byte from the given position in the value

    Inputs
    ----
    - i: byte offset starting from the most significant byte.
    - x: 32-byte value

    Outputs
    ----
    - y: the indicated byte at the least significant position. If the byte offset is out of range,
      the result is 0

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#1A](https://www.evm.codes/#1A)
    """

    SHL = Opcode(0x1B, popped_stack_items=2, pushed_stack_items=1)
    """
    SHL(shift, value) = value << shift
    ----

    Description
    ----
    Shift left operation

    Inputs
    ----
    - shift: number of bits to shift to the left.
    - value: 32 bytes to shift

    Outputs
    ----
    - value << shift: the shifted value. If shift is bigger than 255, returns 0

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#1B](https://www.evm.codes/#1B)
    """

    SHR = Opcode(0x1C, popped_stack_items=2, pushed_stack_items=1)
    """
    SHR(shift, value) = value >> shift
    ----

    Description
    ----
    Logical shift right operation

    Inputs
    ----
    - shift: number of bits to shift to the right.
    - value: 32 bytes to shift

    Outputs
    ----
    - value >> shift: the shifted value. If shift is bigger than 255, returns 0

    Fork
    ----
    Constantinople

    Gas
    ----
    3

    Source: [evm.codes/#1C](https://www.evm.codes/#1C)
    """

    SAR = Opcode(0x1D, popped_stack_items=2, pushed_stack_items=1)
    """
    SAR(shift, value) = value >> shift
    ----

    Description
    ----
    Arithmetic shift right operation

    Inputs
    ----
    - shift: number of bits to shift to the right
    - value: integer to shift

    Outputs
    ----
    - value >> shift: the shifted value

    Fork
    ----
    Constantinople

    Gas
    ----
    3

    Source: [evm.codes/#1D](https://www.evm.codes/#1D)
    """

    SHA3 = Opcode(0x20, popped_stack_items=2, pushed_stack_items=1)
    """
    SHA3(start, length) = hash
    ----

    Description
    ----
    Compute Keccak-256 hash

    Inputs
    ----
    - offset: byte offset in the memory
    - size: byte size to read in the memory

    Outputs
    ----
    - hash: Keccak-256 hash of the given data in memory

    Fork
    ----
    Frontier

    Gas
    ----
    30

    Source: [evm.codes/#20](https://www.evm.codes/#20)
    """

    ADDRESS = Opcode(0x30, pushed_stack_items=1)
    """
    ADDRESS() = address
    ----

    Description
    ----
    Get address of currently executing account

    Inputs
    ----
    - None

    Outputs
    ----
    - address: the 20-byte address of the current account

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#30](https://www.evm.codes/#30)
    """

    BALANCE = Opcode(0x31, popped_stack_items=1, pushed_stack_items=1)
    """
    BALANCE(address) = balance
    ----

    Description
    ----
    Get the balance of the specified account

    Inputs
    ----
    - address: 20-byte address of the account to check

    Outputs
    ----
    - balance: balance of the given account in wei. Returns 0 if the account doesn't exist

    Fork
    ----
    Frontier

    Gas
    ----
    100

    Source: [evm.codes/#31](https://www.evm.codes/#31)
    """

    ORIGIN = Opcode(0x32, pushed_stack_items=1)
    """
    ORIGIN() = address
    ----

    Description
    ----
    Get execution origination address

    Inputs
    ----
    - None

    Outputs
    ----
    - address: the 20-byte address of the sender of the transaction. It can only be an account
      without code

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#32](https://www.evm.codes/#32)
    """

    CALLER = Opcode(0x33, pushed_stack_items=1)
    """
    CALLER() = address
    ----

    Description
    ----
    Get caller address

    Inputs
    ----
    - None

    Outputs
    ----
    - address: the 20-byte address of the caller account. This is the account that did the last
      call (except delegate call)

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#33](https://www.evm.codes/#33)
    """

    CALLVALUE = Opcode(0x34, pushed_stack_items=1)
    """
    CALLVALUE() = value
    ----

    Description
    ----
    Get deposited value by the instruction/transaction responsible for this execution

    Inputs
    ----
    - None

    Outputs
    ----
    - value: the value of the current call in wei

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#34](https://www.evm.codes/#34)
    """

    CALLDATALOAD = Opcode(0x35, popped_stack_items=1, pushed_stack_items=1)
    """
    CALLDATALOAD(i) = data[i]
    ----

    Description
    ----
    Get input data of current environment

    Inputs
    ----
    - i: byte offset in the calldata.

    Outputs
    ----
    - data[i]: 32-byte value starting from the given offset of the calldata. All bytes after the
      end of the calldata are set to 0

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#35](https://www.evm.codes/#35)
    """

    CALLDATASIZE = Opcode(0x36, pushed_stack_items=1)
    """
    CALLDATASIZE() = size
    ----

    Description
    ----
    Get size of input data in current environment

    Inputs
    ----
    - None

    Outputs
    ----
    - size: byte size of the calldata

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#36](https://www.evm.codes/#36)
    """

    CALLDATACOPY = Opcode(0x37, popped_stack_items=3)
    """
    CALLDATACOPY(destOffset, offset, size)
    ----

    Description
    ----
    Copy input data in current environment to memory

    Inputs
    ----
    - destOffset: byte offset in the memory where the result will be copied
    - offset: byte offset in the calldata to copy
    - size: byte size to copy

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#37](https://www.evm.codes/#37)
    """

    CODESIZE = Opcode(0x38, pushed_stack_items=1)
    """
    CODESIZE() = size
    ----

    Description
    ----
    Get size of code running in current environment

    Inputs
    ----
    - None

    Outputs
    ----
    - size: byte size of the code

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#38](https://www.evm.codes/#38)
    """

    CODECOPY = Opcode(0x39, popped_stack_items=3)
    """
    CODECOPY(destOffset, offset, size)
    ----

    Description
    ----
    Copy code running in current environment to memory

    Inputs
    ----
    - destOffset: byte offset in the memory where the result will be copied.
    - offset: byte offset in the code to copy.
    - size: byte size to copy

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#39](https://www.evm.codes/#39)
    """

    GASPRICE = Opcode(0x3A, pushed_stack_items=1)
    """
    GASPRICE() = price
    ----

    Description
    ----
    Get price of gas in current environment

    Outputs
    ----
    - price: gas price in wei per gas

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#3A](https://www.evm.codes/#3A)
    """

    EXTCODESIZE = Opcode(0x3B, popped_stack_items=1, pushed_stack_items=1)
    """
    EXTCODESIZE(account) = size
    ----

    Description
    ----
    Get size of an account’s code

    Inputs
    ----
    - address: 20-byte address of the contract to query

    Outputs
    ----
    - size: byte size of the code

    Fork
    ----
    Frontier

    Gas
    ----
    100

    Source: [evm.codes/#3C](https://www.evm.codes/#3B)
    """

    EXTCODECOPY = Opcode(0x3C, popped_stack_items=4)
    """
    EXTCODECOPY(addr, destOffset, offset, size)
    ----

    Description
    ----
    Copy an account’s code to memory

    Inputs
    ----
    - address: 20-byte address of the contract to query
    - destOffset: byte offset in the memory where the result will be copied
    - offset: byte offset in the code to copy
    - size: byte size to copy

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    minimum_word_size = (size + 31) / 32 static_gas = 0 dynamic_gas = 3 * minimum_word_size +
    memory_expansion_cost + address_access_cost

    Source: [evm.codes/#3C](https://www.evm.codes/#3C)
    """

    RETURNDATASIZE = Opcode(0x3D, pushed_stack_items=1)
    """
    RETURNDATASIZE() = size
    ----

    Description
    ----
    Get size of output data from the previous call from the current environment

    Outputs
    ----
    - size: byte size of the return data from the last executed sub context

    Fork
    ----
    Byzantium

    Gas
    ----
    2

    Source: [evm.codes/#3D](https://www.evm.codes/#3D)
    """

    RETURNDATACOPY = Opcode(0x3E, popped_stack_items=3)
    """
    RETURNDATACOPY(destOffset, offset, size)
    ----

    Description
    ----
    Copy output data from the previous call to memory

    Inputs
    ----
    - destOffset: byte offset in the memory where the result will be copied.
    - offset: byte offset in the return data from the last executed sub context to copy.
    - size: byte size to copy.

    Fork
    ----
    Byzantium

    Gas
    ----
    minimum_word_size = (size + 31) / 32

    Gas = 3 + 3 * minimum_word_size + memory_expansion_cost

    Source: [evm.codes/#3E](https://www.evm.codes/#3E)
    """

    EXTCODEHASH = Opcode(0x3F, popped_stack_items=1, pushed_stack_items=1)
    """
    EXTCODEHASH(address) = hash
    ----

    Description
    ----
    Get hash of an account’s code

    Inputs
    ----
    - address: 20-byte address of the account

    Outputs
    ----
    - hash: hash of the chosen account's code, the empty hash (0xc5d24601...) if the account has no
      code, or 0 if the account does not exist or has been destroyed

    Fork
    ----
    Constantinople

    Gas
    ----
    100

    Source: [evm.codes/#3F](https://www.evm.codes/#3F)
    """

    BLOCKHASH = Opcode(0x40, popped_stack_items=1, pushed_stack_items=1)
    """
    BLOCKHASH(block_number) = hash
    ----

    Description
    ----
    Get the hash of one of the 256 most recent complete blocks

    Inputs
    ----
    - blockNumber: block number to get the hash from. Valid range is the last 256 blocks (not
      including the current one). Current block number can be queried with NUMBER

    Outputs
    ----
    - hash: hash of the chosen block, or 0 if the block number is not in the valid range
    Fork
    ----
    Frontier

    Gas
    ----
    20

    Source: [evm.codes/#40](https://www.evm.codes/#40)
    """

    COINBASE = Opcode(0x41, pushed_stack_items=1)
    """
    COINBASE() = address
    ----

    Description
    ----
    Get the block’s beneficiary address

    Inputs
    ----
    - None

    Outputs
    ----
    - address: miner's 20-byte address

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#41](https://www.evm.codes/#41)
    """

    TIMESTAMP = Opcode(0x42, pushed_stack_items=1)
    """
    TIMESTAMP() = timestamp
    ----

    Description
    ----
    Get the block’s timestamp

    Inputs
    ----
    - None

    Outputs
    ----
    - timestamp: unix timestamp of the current block

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#42](https://www.evm.codes/#42)
    """

    NUMBER = Opcode(0x43, pushed_stack_items=1)
    """
    NUMBER() = blockNumber
    ----

    Description
    ----
    Get the block’s number

    Inputs
    ----
    - None

    Outputs
    ----
    - blockNumber: current block number

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#43](https://www.evm.codes/#43)
    """

    PREVRANDAO = Opcode(0x44, pushed_stack_items=1)
    """
    NUMBER() = prevRandao
    ----

    Description
    ----
    Get the previous block’s RANDAO mix

    Inputs
    ----
    - None

    Outputs
    ----
    - prevRandao: previous block's RANDAO mix

    Fork
    ----
    Merge

    Gas
    ----
    20

    Source: [evm.codes/#44](https://www.evm.codes/#44)
    """

    GASLIMIT = Opcode(0x45, pushed_stack_items=1)
    """
    GASLIMIT() = gasLimit
    ----

    Description
    ----
    Get the block’s gas limit

    Inputs
    ----
    - None

    Outputs
    ----
    - gasLimit: gas limit

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#45](https://www.evm.codes/#45)
    """

    CHAINID = Opcode(0x46, pushed_stack_items=1)
    """
    CHAINID() = chainId
    ----

    Description
    ----
    Get the chain ID

    Inputs
    ----
    - None

    Outputs
    ----
    - chainId: chain id of the network

    Fork
    ----
    Istanbul

    Gas
    ----
    2

    Source: [evm.codes/#46](https://www.evm.codes/#46)
    """

    SELFBALANCE = Opcode(0x47, pushed_stack_items=1)
    """
    SELFBALANCE() = balance
    ----

    Description
    ----
    Get balance of currently executing account

    Inputs
    ----
    - None

    Outputs
    ----
    - balance: balance of the current account in wei

    Fork
    ----
    Istanbul

    Gas
    ----
    5

    Source: [evm.codes/#47](https://www.evm.codes/#47)
    """
    BASEFEE = Opcode(0x48, pushed_stack_items=1)
    """
    BASEFEE() = baseFee
    ----

    Description
    ----
    Get the base fee

    Outputs
    ----
    - baseFee: base fee in wei

    Fork
    ----
    London

    Gas
    ----
    2

    Source: [evm.codes/#48](https://www.evm.codes/#48)
    """

    BLOBHASH = Opcode(0x49, popped_stack_items=1, pushed_stack_items=1)
    """
    BLOBHASH(index) = versionedHash
    ----

    Description
    ----
    Returns the versioned hash of a single blob contained in the type-3 transaction

    Inputs
    ----
    - index: index of the blob

    Outputs
    ----
    - versionedHash: versioned hash of the blob

    Fork
    ----
    Cancun

    Gas
    ----
    HASH_OPCODE_GAS

    Source: [eips.ethereum.org/EIPS/eip-4844](https://eips.ethereum.org/EIPS/eip-4844)
    """

    BLOBBASEFEE = Opcode(0x4A, popped_stack_items=0, pushed_stack_items=1)
    """
    BLOBBASEFEE() = fee
    ----

    Description
    ----
    Returns the value of the blob base-fee of the current block it is executing in

    Inputs
    ----
    - None

    Outputs
    ----
    - fee: base fee per blob gas

    Fork
    ----
    Cancun

    Gas
    ----
    2

    Source: [eips.ethereum.org/EIPS/eip-7516(https://eips.ethereum.org/EIPS/eip-7516)
    """

    POP = Opcode(0x50, popped_stack_items=1)
    """
    POP()
    ----

    Description
    ----
    Remove item from stack

    Inputs
    ----
    - None

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#50](https://www.evm.codes/#50)
    """

    MLOAD = Opcode(0x51, popped_stack_items=1, pushed_stack_items=1)
    """
    MLOAD(offset) = value
    ----

    Description
    ----
    Load word from memory

    Inputs
    ----
    - offset: offset in the memory in bytes

    Outputs
    ----
    - value: the 32 bytes in memory starting at that offset. If it goes beyond its current size
      (see MSIZE), writes 0s

    Fork
    ----
    Frontier

    Gas
    ----
    3 + memory_expansion_cost

    Source: [evm.codes/#51](https://www.evm.codes/#51)
    """

    MSTORE = Opcode(0x52, popped_stack_items=2)
    """
    MSTORE(offset, value)
    ----

    Description
    ----
    Save word to memory

    Inputs
    ----
    - offset: offset in the memory in bytes.
    - value: 32-byte value to write in the memory.

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    3 + memory_expansion_cost

    Source: [evm.codes/#52](https://www.evm.codes/#52)
    """

    MSTORE8 = Opcode(0x53, popped_stack_items=2)
    """
    MSTORE8(offset, value)
    ----

    Description
    ----
    Save byte to memory

    Inputs
    ----
    - offset: offset in the memory in bytes
    - value: 1-byte value to write in the memory (the least significant byte of the 32-byte stack
      value

    Fork
    ----
    Frontier

    Gas
    ----
    3 + memory_expansion_cost

    Source: [evm.codes/#53](https://www.evm.codes/#53)
    """

    SLOAD = Opcode(0x54, popped_stack_items=1, pushed_stack_items=1)
    """
    SLOAD(key) = value
    ----

    Description
    ----
    Load word from storage

    Inputs
    ----
    - key: 32-byte key in storage

    Outputs
    ----
    - value: 32-byte value corresponding to that key. 0 if that key was never written before

    Fork
    ----
    Frontier

    Gas
    ----
    warm: 100
    cold: 2100

    Source: [evm.codes/#54](https://www.evm.codes/#54)
    """

    SSTORE = Opcode(0x55, popped_stack_items=2)
    """
    SSTORE(key, value)
    ----

    Description
    ----
    Save word to storage

    Inputs
    ----
    - key: 32-byte key in storage
    - value: 32-byte value to store

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    set: 20000
    reset: 2900

    Source: [evm.codes/#55](https://www.evm.codes/#55)
    """

    JUMP = Opcode(0x56, popped_stack_items=1)
    """
    JUMP(counter)
    ----

    Description
    ----
    Alter the program counter

    Inputs
    ----
    - counter: byte offset in the deployed code where execution will continue from. Must be a
      JUMPDEST instruction.

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    8

    Source: [evm.codes/#56](https://www.evm.codes/#56)
    """

    JUMPI = Opcode(0x57, popped_stack_items=2)
    """
    JUMPI(counter, b)
    ----

    Description
    ----
    Conditionally alter the program counter

    Inputs
    ----
    - counter: byte offset in the deployed code where execution will continue from. Must be a
      JUMPDEST instruction.
    - b: the program counter will be altered with the new value only if this value is different
      from 0. Otherwise, the program counter is simply incremented and the next instruction will be
      executed.

    Fork
    ----
    Frontier

    Gas
    ----
    10

    Source: [evm.codes/#57](https://www.evm.codes/#57)
    """

    PC = Opcode(0x58, pushed_stack_items=1)
    """
    PC() = counter
    ----

    Description
    ----
    Get the value of the program counter prior to the increment corresponding to this instruction

    Inputs
    ----
    - None

    Outputs
    ----
    - counter: PC of this instruction in the current program.

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#58](https://www.evm.codes/#58)
    """

    MSIZE = Opcode(0x59, pushed_stack_items=1)
    """
    MSIZE() = size
    ----

    Description
    ----
    Get the size of active memory in bytes

    Outputs
    ----
    - size: current memory size in bytes (higher offset accessed until now + 1)

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#59](https://www.evm.codes/#59)
    """

    GAS = Opcode(0x5A, pushed_stack_items=1)
    """
    GAS() = gas_remaining
    ----

    Description
    ----
    Get the amount of available gas, including the corresponding reduction for the cost of this
    instruction

    Inputs
    ----
    - None

    Outputs
    ----
    - gas_remaining: remaining gas for the current call frame

    Fork
    ----
    Frontier

    Gas
    ----
    2

    Source: [evm.codes/#5A](https://www.evm.codes/#5A)
    """

    JUMPDEST = Opcode(0x5B)
    """
    JUMPDEST()
    ----

    Description
    ----
    Mark a valid destination for jumps

    Inputs
    ----
    - None

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    1

    Source: [evm.codes/#5B](https://www.evm.codes/#5B)
    """

    TLOAD = Opcode(0x5C, popped_stack_items=1, pushed_stack_items=1)
    """
    TLOAD(key) = value
    ----

    Description
    ----
    Load a value from the storage at the specified key.

    Inputs
    ----
    - key: The key in storage.

    Outputs
    ----
    - value: The value associated with the given key.

    Fork
    ----
    Cancun

    Gas
    ----
    100

    Source: [eips.ethereum.org/EIPS/eip-1153](https://eips.ethereum.org/EIPS/eip-1153)
    """

    TSTORE = Opcode(0x5D, popped_stack_items=2)
    """
    TSTORE(key, value)
    ----

    Description
    ----
    Store a value in the storage at the specified key.

    Inputs
    ----
    - key: The key in storage.
    - value: The value to be stored.

    Fork
    ----
    Cancun

    Gas
    ----
    100

    Source: [eips.ethereum.org/EIPS/eip-1153](https://eips.ethereum.org/EIPS/eip-1153)
    """

    MCOPY = Opcode(0x5E, popped_stack_items=3)
    """
    MCOPY(dst, src ,length)
    ----

    Description
    ----
    Copies memory

    Inputs
    ----
    - dst: byte offset in the memory where the result will be copied.
    - src: byte offset in the calldata to copy.
    - length: byte size to copy

    Outputs
    ----
    - None

    Fork
    ----
    Cancun

    Gas
    ----
    words_copied = (length + 31) // 32 g_verylow    = 3 g_copy       = 3 * words_copied +
    memory_expansion_cost gas_cost     = g_verylow + g_copy

    Source: [eips.ethereum.org/EIPS/eip-5656](https://eips.ethereum.org/EIPS/eip-5656)
    """

    RETF = Opcode(0x49)
    """
    RETF()
    ----

    Description
    ----
    Return from a function

    Inputs
    ----
    - None

    Outputs
    ----
    - None

    Fork
    ----


    Gas
    ----
    3

    Source: [evm.codes/#5F](https://www.evm.codes/#5F)
    """

    PUSH0 = Opcode(0x5F, pushed_stack_items=1)
    """
    PUSH0() = value
    ----

    Description
    ----
    Place value 0 on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, equal to 0

    Fork
    ----
    Shanghai

    Gas
    ----
    2

    Source: [evm.codes/#5F](https://www.evm.codes/#5F)
    """

    PUSH1 = Opcode(0x60, pushed_stack_items=1, data_portion_length=1)
    """
    PUSH1() = value
    ----

    Description
    ----
    Place 1 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#60](https://www.evm.codes/#60)
    """

    PUSH2 = Opcode(0x61, pushed_stack_items=1, data_portion_length=2)
    """
    PUSH2() = value
    ----

    Description
    ----
    Place 2 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#61](https://www.evm.codes/#61)
    """

    PUSH3 = Opcode(0x62, pushed_stack_items=1, data_portion_length=3)
    """
    PUSH3() = value
    ----

    Description
    ----
    Place 3 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#62](https://www.evm.codes/#62)
    """

    PUSH4 = Opcode(0x63, pushed_stack_items=1, data_portion_length=4)
    """
    PUSH4() = value
    ----

    Description
    ----
    Place 4 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#63](https://www.evm.codes/#63)
    """

    PUSH5 = Opcode(0x64, pushed_stack_items=1, data_portion_length=5)
    """
    PUSH5() = value
    ----

    Description
    ----
    Place 5 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#64](https://www.evm.codes/#64)
    """

    PUSH6 = Opcode(0x65, pushed_stack_items=1, data_portion_length=6)
    """
    PUSH6() = value
    ----

    Description
    ----
    Place 6 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#65](https://www.evm.codes/#65)
    """

    PUSH7 = Opcode(0x66, pushed_stack_items=1, data_portion_length=7)
    """
    PUSH7() = value
    ----

    Description
    ----
    Place 7 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#66](https://www.evm.codes/#66)
    """

    PUSH8 = Opcode(0x67, pushed_stack_items=1, data_portion_length=8)
    """
    PUSH8() = value
    ----

    Description
    ----
    Place 8 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#67](https://www.evm.codes/#67)
    """

    PUSH9 = Opcode(0x68, pushed_stack_items=1, data_portion_length=9)
    """
    PUSH9() = value
    ----

    Description
    ----
    Place 9 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#68](https://www.evm.codes/#68)
    """

    PUSH10 = Opcode(0x69, pushed_stack_items=1, data_portion_length=10)
    """
    PUSH10() = value
    ----

    Description
    ----
    Place 10 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#69](https://www.evm.codes/#69)
    """

    PUSH11 = Opcode(0x6A, pushed_stack_items=1, data_portion_length=11)
    """
    PUSH11() = value
    ----

    Description
    ----
    Place 11 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#6A](https://www.evm.codes/#6A)
    """

    PUSH12 = Opcode(0x6B, pushed_stack_items=1, data_portion_length=12)
    """
    PUSH12() = value
    ----

    Description
    ----
    Place 12 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#6B](https://www.evm.codes/#6B)
    """

    PUSH13 = Opcode(0x6C, pushed_stack_items=1, data_portion_length=13)
    """
    PUSH13() = value
    ----

    Description
    ----
    Place 13 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#6C](https://www.evm.codes/#6C)
    """

    PUSH14 = Opcode(0x6D, pushed_stack_items=1, data_portion_length=14)
    """
    PUSH14() = value
    ----

    Description
    ----
    Place 14 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier


    Gas
    ----
    3

    Source: [evm.codes/#6D](https://www.evm.codes/#6D)
    """

    PUSH15 = Opcode(0x6E, pushed_stack_items=1, data_portion_length=15)
    """
    PUSH15() = value
    ----

    Description
    ----
    Place 15 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#6E](https://www.evm.codes/#6E)
    """

    PUSH16 = Opcode(0x6F, pushed_stack_items=1, data_portion_length=16)
    """
    PUSH16() = value
    ----

    Description
    ----
    Place 16 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#6F](https://www.evm.codes/#6F)
    """

    PUSH17 = Opcode(0x70, pushed_stack_items=1, data_portion_length=17)
    """
    PUSH17() = value
    ----

    Description
    ----
    Place 17 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#70](https://www.evm.codes/#70)
    """

    PUSH18 = Opcode(0x71, pushed_stack_items=1, data_portion_length=18)
    """
    PUSH18() = value
    ----

    Description
    ----
    Place 18 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#71](https://www.evm.codes/#71)
    """

    PUSH19 = Opcode(0x72, pushed_stack_items=1, data_portion_length=19)
    """
    PUSH19() = value
    ----

    Description
    ----
    Place 19 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#72](https://www.evm.codes/#72)
    """

    PUSH20 = Opcode(0x73, pushed_stack_items=1, data_portion_length=20)
    """
    PUSH20() = value
    ----

    Description
    ----
    Place 20 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#73](https://www.evm.codes/#73)
    """

    PUSH21 = Opcode(0x74, pushed_stack_items=1, data_portion_length=21)
    """
    PUSH21() = value
    ----

    Description
    ----
    Place 21 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#74](https://www.evm.codes/#74)
    """

    PUSH22 = Opcode(0x75, pushed_stack_items=1, data_portion_length=22)
    """
    PUSH22() = value
    ----

    Description
    ----
    Place 22 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#75](https://www.evm.codes/#75)
    """

    PUSH23 = Opcode(0x76, pushed_stack_items=1, data_portion_length=23)
    """
    PUSH23() = value
    ----

    Description
    ----
    Place 23 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#76](https://www.evm.codes/#76)
    """

    PUSH24 = Opcode(0x77, pushed_stack_items=1, data_portion_length=24)
    """
    PUSH24() = value
    ----

    Description
    ----
    Place 24 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#77](https://www.evm.codes/#77)
    """

    PUSH25 = Opcode(0x78, pushed_stack_items=1, data_portion_length=25)
    """
    PUSH25() = value
    ----

    Description
    ----
    Place 25 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#78](https://www.evm.codes/#78)
    """

    PUSH26 = Opcode(0x79, pushed_stack_items=1, data_portion_length=26)
    """
    PUSH26() = value
    ----

    Description
    ----
    Place 26 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#79](https://www.evm.codes/#79)
    """

    PUSH27 = Opcode(0x7A, pushed_stack_items=1, data_portion_length=27)
    """
    PUSH27() = value
    ----

    Description
    ----
    Place 27 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#7A](https://www.evm.codes/#7A)
    """

    PUSH28 = Opcode(0x7B, pushed_stack_items=1, data_portion_length=28)
    """
    PUSH28() = value
    ----

    Description
    ----
    Place 28 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#7B](https://www.evm.codes/#7B)
    """

    PUSH29 = Opcode(0x7C, pushed_stack_items=1, data_portion_length=29)
    """
    PUSH29() = value
    ----

    Description
    ----
    Place 29 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#7C](https://www.evm.codes/#7C)
    """

    PUSH30 = Opcode(0x7D, pushed_stack_items=1, data_portion_length=30)
    """
    PUSH30() = value
    ----

    Description
    ----
    Place 30 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value, aligned to the right (put in the lowest significant bytes)

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#7D](https://www.evm.codes/#7D)
    """

    PUSH31 = Opcode(0x7E, pushed_stack_items=1, data_portion_length=31)
    """
    PUSH31() = value
    ----

    Description
    ----
    Place 31 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#7E](https://www.evm.codes/#7E)
    """

    PUSH32 = Opcode(0x7F, pushed_stack_items=1, data_portion_length=32)
    """
    PUSH32() = value
    ----

    Description
    ----
    Place 32 byte item on stack

    Inputs
    ----
    - None

    Outputs
    ----
    - value: pushed value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#7F](https://www.evm.codes/#7F)
    """

    DUP1 = Opcode(0x80, pushed_stack_items=1, min_stack_height=1)
    """
    DUP1(value) = value
    ----

    Description
    ----
    Duplicate 1st stack item

    Inputs
    ----
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value.
    - value: original value

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#80](https://www.evm.codes/#80)
    """

    DUP2 = Opcode(0x81, pushed_stack_items=1, min_stack_height=2)
    """
    DUP2(a, b) = b,a,b
    ----

    Description
    ----
    Duplicate 2nd stack item

    Inputs
    ----
    - a: ignored value.
    - b: value to duplicate.

    Outputs
    ----
    - b: duplicated value.
    - a: ignored value.
    - b: original value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#81](https://www.evm.codes/#81)
    """

    DUP3 = Opcode(0x82, pushed_stack_items=1, min_stack_height=3)
    """
    DUP15(a, b, c) = c, a, b, c
    ----

    Description
    ----
    Duplicate 3rd stack item

    Inputs
    ----
    - a: ignored value.
    - b: ignored value.
    - c: value to duplicate.

    Outputs
    ----
    - c: duplicated value.
    - a: ignored value.
    - b: ignored value.
    - c: original value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#82](https://www.evm.codes/#82)
    """

    DUP4 = Opcode(0x83, pushed_stack_items=1, min_stack_height=4)
    """
    DUP15(value1, value2, value3, value) = value, value2, value3, value
    ----

    Description
    ----
    Duplicate 4th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#83](https://www.evm.codes/#83)
    """

    DUP5 = Opcode(0x84, pushed_stack_items=1, min_stack_height=5)
    """
    DUP15(value1, value2, value3, value4, value) = value, value2, value3, value4, value
    ----

    Description
    ----
    Duplicate 5th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#84](https://www.evm.codes/#84)
    """

    DUP6 = Opcode(0x85, pushed_stack_items=1, min_stack_height=6)
    """
    DUP15(value1, value2, value3, value4, value5, value) = value, value2, value3, value4, value5,
    value
    ----

    Description
    ----
    Duplicate 6th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#85](https://www.evm.codes/#85)
    """

    DUP7 = Opcode(0x86, pushed_stack_items=1, min_stack_height=7)
    """
    DUP15(value1, value2, value3, value4, value5, value6, value) = value, value2, value3, value4,
    value5, value6, value
    ----

    Description
    ----
    Duplicate 7th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#86](https://www.evm.codes/#86)
    """

    DUP8 = Opcode(0x87, pushed_stack_items=1, min_stack_height=8)
    """
    DUP15(value1, value2, value3, value4, value5, value6, value7, value) = value, value2, value3,
    value4, value5, value6, value7, value
    ----

    Description
    ----
    Duplicate 8th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#87](https://www.evm.codes/#87)
    """

    DUP9 = Opcode(0x88, pushed_stack_items=1, min_stack_height=9)
    """
    DUP15(value1, value2, value3, value4, value5, value6, value7, value8, value) = value, value2,
    value3, value4, value5, value6, value7, value8, value
    ----

    Description
    ----
    Duplicate 9th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#88](https://www.evm.codes/#88)
    """
    DUP10 = Opcode(0x89, pushed_stack_items=1, min_stack_height=10)
    """
    DUP10(value1, value2, value3, value4, value5, value6, value7, value8, value9, value) = value,
    value2, value3, value4, value5, value6, value7, value8, value9, value
    ----

    Description
    ----
    Duplicate 10th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#89](https://www.evm.codes/#89)
    """

    DUP11 = Opcode(0x8A, pushed_stack_items=1, min_stack_height=11)
    """
    DUP11(value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value) =
    value, value2, value3, value4, value5, value6, value7, value8, value9, value10, value
    ----

    Description
    ----
    Duplicate 11th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#8A](https://www.evm.codes/#8A)
    """

    DUP12 = Opcode(0x8B, pushed_stack_items=1, min_stack_height=12)
    """
    DUP12(value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11,
    value) = value, value2, value3, value4, value5, value6, value7, value8, value9, value10,
    value11, value
    ----

    Description
    ----
    Duplicate 12th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#8B](https://www.evm.codes/#8B)
    """

    DUP13 = Opcode(0x8C, pushed_stack_items=1, min_stack_height=13)
    """
    DUP15(value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11,
    value12, value) = value, value2, value3, value4, value5, value6, value7, value8, value9,
    value10,value11, value12, value
    ----

    Description
    ----
    Duplicate 13th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#8C](https://www.evm.codes/#8C)
    """

    DUP14 = Opcode(0x8D, pushed_stack_items=1, min_stack_height=14)
    """
    DUP15(value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11,
    value12, value13, value) = value, value2, value3, value4, value5, value6, value7, value8,
    value9, value10, value11, value12, value13, value
    ----

    Description
    ----
    Duplicate 14th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#8D](https://www.evm.codes/#8D)
    """

    DUP15 = Opcode(0x8E, pushed_stack_items=1, min_stack_height=15)
    """
    DUP15(value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11,
    value12, value13, value14, value) = value, value2, value3, value4, value5, value6, value7,
    value8, value9, value10, value11, value12, value13, value14, value
    ----

    Description
    ----
    Duplicate 15th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#8E](https://www.evm.codes/#8E)
    """

    DUP16 = Opcode(0x8F, pushed_stack_items=1, min_stack_height=16)
    """
    DUP16(value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11,
    value12, value13, value14, value15, value) = value, value2, value3, value4, value5, value6,
    value7, value8, value9, value10, value11, value12, value13, value14, value15, value
    ----

    Description
    ----
    Duplicate 16th stack item

    Inputs
    ----
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Outputs
    ----
    - value: duplicated value
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - value: value to duplicate

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#8F](https://www.evm.codes/#8F)
    """

    SWAP1 = Opcode(0x90, min_stack_height=2)
    """
    SWAP1(a, b) = b, a
    ----

    Description
    ----
    Exchange the top stack item with the second stack item.

    Inputs
    ----
    - a: value to swap
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#90](https://www.evm.codes/#90)
    """

    SWAP2 = Opcode(0x91, min_stack_height=3)
    """
    SWAP2(a, value2, b) = b, value2, a
    ----

    Description
    ----
    Exchange 1st and 3rd stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value
    - ignored value
    - a: swapped value

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#91](https://www.evm.codes/#91)
    """

    SWAP3 = Opcode(0x92, min_stack_height=4)
    """
    SWAP3(a, value2, value3, b) = b value2, value3, a
    ----

    Description
    ----
    Exchange 1st and 4th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#92](https://www.evm.codes/#92)
    """

    SWAP4 = Opcode(0x93, min_stack_height=5)
    """
    SWAP4(a, value2, value3, value4, b) = b value2, value3, value4, a
    ----

    Description
    ----
    Exchange 1st and 5th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#93](https://www.evm.codes/#93)
    """

    SWAP5 = Opcode(0x94, min_stack_height=6)
    """
    SWAP5(a, value2, value3, value4, value5, b) = b, value2, value3, value4, value5, a
    ----

    Description
    ----
    Exchange 1st and 6th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#94](https://www.evm.codes/#94)
    """

    SWAP6 = Opcode(0x95, min_stack_height=7)
    """
    SWAP6(a, value2, value3, value4, value5, value6, b) = b, value2, value3, value4, value5,
    value6, a
    ----

    Description
    ----
    Exchange 1st and 7th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#95](https://www.evm.codes/#95)
    """

    SWAP7 = Opcode(0x96, min_stack_height=8)
    """
    SWAP7(a, value2, value3, value4, value5, value6, value7, b) = b, value2, value3, value4,
    value5, value6, value7, a
    ----

    Description
    ----
    Exchange 1st and 8th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#96](https://www.evm.codes/#96)
    """

    SWAP8 = Opcode(0x97, min_stack_height=9)
    """
    SWAP8(a, value2, value3, value4, value5, value6, value7, value8, b) = b, value2, value3,
    value4,value5, value6, value7, value8, a
    ----

    Description
    ----
    Exchange 1st and 9th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#97](https://www.evm.codes/#97)
    """

    SWAP9 = Opcode(0x98, min_stack_height=10)
    """
    SWAP9(a, value2, value3, value4, value5, value6, value7, value8, value9, b) = b, value2,
    value3,value4, value5, value6, value7, value8, value9, a
    ----

    Description
    ----
    Exchange 1st and 10th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#98](https://www.evm.codes/#98)
    """

    SWAP10 = Opcode(0x99, min_stack_height=11)
    """
    SWAP10(a, value2, value3, value4, value5, value6, value7, value8, value9, value10, b) =
    b, value2, value3, value4, value5, value6, value7, value8, value9, value10, a
    ----

    Description
    ----
    Exchange 1st and 11th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#99](https://www.evm.codes/#99)
    """

    SWAP11 = Opcode(0x9A, min_stack_height=12)
    """
    SWAP11(a, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11, b)
    = b, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11, a
    ----

    Description
    ----
    Exchange 1st and 12th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#9A](https://www.evm.codes/#9A)
    """

    SWAP12 = Opcode(0x9B, min_stack_height=13)
    """
    SWAP12(a, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11,
    value12, b) = b, value2, value3, value4, value5, value6, value7, value8, value9, value10,
    value11, value12, a
    ----

    Description
    ----
    Exchange 1st and 13th stack items

    Inputs
    ----
    - a: value to swap
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#9B](https://www.evm.codes/#9B)
    """

    SWAP13 = Opcode(0x9C, min_stack_height=14)
    """
    SWAP13(a, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10,
    value11, value12, b) = b, value1, value2, value3, value4, value5, value6, value7, value8,
    value9, value10, value11, value12,a)
    ----

    Description
    ----
    Exchange 1st and 14th stack items

    Inputs
    ----
    - a: value to swap.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap.

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#9C](https://www.evm.codes/#9C)
    """

    SWAP14 = Opcode(0x9D, min_stack_height=15)
    """
    SWAP14(a, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10,
    value11, value12, value13, b) = b, value1, value2, value3, value4, value5, value6, value7,
    value8, value9, value10, value11, value12, value13, a)
    ----

    Description
    ----
    Exchange 1st and 15th stack items

    Inputs
    ----
    - a: value to swap.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap.

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#9D](https://www.evm.codes/#9D)
    """

    SWAP15 = Opcode(0x9E, min_stack_height=16)
    """
    SWAP15(a, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10,
    value11, value12, value13, value14, b) = b, value1, value2, value3, value4, value5, value6,
    value7, value8, value9, value10, value11, value12, value13, value14, a)
    ----

    Description
    ----
    Exchange 1st and 16th stack items

    Inputs
    ----
    - a: value to swap.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap.

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#9E](https://www.evm.codes/#9E)
    """

    SWAP16 = Opcode(0x9F, min_stack_height=17)
    """
    SWAP16(a, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10,
    value11, value12, value13, value14, value15, b) = b, value1, value2, value3, value4, value5,
    value6, value7, value8, value9, value10, value11, value12, value13, value14, value15, a)
    ----

    Description
    ----
    Exchange 1st and 17th stack items

    Inputs
    ----
    - a: value to swap.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - b: value to swap.

    Outputs
    ----
    - b: swapped value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - ignored value.
    - a: swapped value.

    Fork
    ----
    Frontier

    Gas
    ----
    3

    Source: [evm.codes/#9F](https://www.evm.codes/#9F)
    """

    LOG0 = Opcode(0xA0, popped_stack_items=2)
    """
    LOG3(offset, size)
    ----

    Description
    ----
    Append log record with no topics

    Inputs
    ----
    - offset: byte offset in the memory in bytes
    - size: byte size to copy

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    375 + 375 * topic_count + 8 * size + memory_expansion_cost

    Source: [evm.codes/#A0](https://www.evm.codes/#A0)
    """

    LOG1 = Opcode(0xA1, popped_stack_items=3)
    """
    LOG1(offset, size, topic1)
    ----

    Description
    ----
    Append log record with one topics

    Inputs
    ----
    - offset: byte offset in the memory in bytes
    - size: byte size to copy
    - topic1: 32-byte value

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    375 + 375 * topic_count + 8 * size + memory_expansion_cost

    Source: [evm.codes/#A1](https://www.evm.codes/#A1)
    """

    LOG2 = Opcode(0xA2, popped_stack_items=4)
    """
    LOG2(offset, size, topic1, topic2)
    ----

    Description
    ----
    Append log record with two topics

    Inputs
    ----
    - offset: byte offset in the memory in bytes
    - size: byte size to copy
    - topic1: 32-byte value
    - topic2: 32-byte value

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    375 + 375 * topic_count + 8 * size + memory_expansion_cost

    Source: [evm.codes/#A2](https://www.evm.codes/#A2)
    """

    LOG3 = Opcode(0xA3, popped_stack_items=5)
    """
    LOG3(offset, size, topic1, topic2, topic3)
    ----

    Description
    ----
    Append log record with three topics

    Inputs
    ----
    - offset: byte offset in the memory in bytes
    - size: byte size to copy
    - topic1: 32-byte value
    - topic2: 32-byte value
    - topic3: 32-byte value

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    375 + 375 * topic_count + 8 * size + memory_expansion_cost

    Source: [evm.codes/#A3](https://www.evm.codes/#A3)
    """

    LOG4 = Opcode(0xA4, popped_stack_items=6)
    """
    LOG4(offset, size, topic1, topic2, topic3, topic4)
    ----

    Description
    ----
    Append log record with four topics

    Inputs
    ----
    - offset: byte offset in the memory in bytes
    - size: byte size to copy
    - topic1: 32-byte value
    - topic2: 32-byte value
    - topic3: 32-byte value
    - topic4: 32-byte value

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    375 + 375 * topic_count + 8 * size + memory_expansion_cost

    Source: [evm.codes/#A4](https://www.evm.codes/#A4)
    """

    RJUMP = Opcode(0xE0, data_portion_length=2)
    """
    RJUMP(destination)
    ----

    Description
    ----
    Jump to a relative position in code.

    Inputs
    ----
    - destination: The relative position to jump to.

    Fork
    ----
    
    """

    RJUMPI = Opcode(0xE1, popped_stack_items=1, data_portion_length=2)
    """
    RJUMPI()
    ----

    Description
    ----


    Inputs
    ----


    Outputs
    ----


    Fork
    ----

    Gas
    ----


    Source:

    """

    RJUMPV = Opcode(0xE2)
    """
    RJUMPV
    ----

    Description
    ----


    Inputs
    ----
    -

    Outputs
    ----
    -

    Fork
    ----


    Gas
    ----


    Source:
    """

    CREATE = Opcode(0xF0, popped_stack_items=3, pushed_stack_items=1)
    """
    CREATE(value, offset, length) = contract_address
    ----

    Description
    ----
    Create a new contract with the given code.

    Inputs
    ----
    - value: value in wei to send to the new account
    - offset: byte offset in the memory in bytes, the initialisation code for the new account
    - size: byte size to copy (size of the initialisation code)

    Outputs
    ----
    - contract_address: The address of the newly created contract.

    Fork
    ----
    Homestead

    Gas
    ----
    32000 + init_code_cost + memory_expansion_cost + deployment_code_execution_cost +
    code_deposit_cost

    Source: [evm.codes/#F0](https://www.evm.codes/#F0)
    """

    CALL = Opcode(0xF1, popped_stack_items=7, pushed_stack_items=1)
    """
    CALL(gas, address, value, argsOffset, argsSize, retOffset, retSize) = success
    ----

    Description
    ----
    Message-call into an account

    Inputs
    ----
    - gas: amount of gas to send to the sub context to execute. The gas that is not used by the sub
      context is returned to this one
    - address: the account which context to execute
    - value: value in wei to send to the account
    - argsOffset: byte offset in the memory in bytes, the calldata of the sub context
    - argsSize: byte size to copy (size of the calldata)
    - retOffset: byte offset in the memory in bytes, where to store the return data of the sub
      context
    - retSize: byte size to copy (size of the return data)

    Outputs
    ----
    - success: return 0 if the sub context reverted, 1 otherwise

    Fork
    ----
    Frontier

    Gas
    ----
    memory_expansion_cost + code_execution_cost + address_access_cost + positive_value_cost +
    value_to_empty_account_cost

    Source: [evm.codes/#F1](https://www.evm.codes/#F1)
    """

    CALLCODE = Opcode(0xF2, popped_stack_items=7, pushed_stack_items=1)
    """
    CALLCODE(gas, address, value, argsOffset, argsSize, retOffset, retSize) = success
    ----

    Description
    ----
    Message-call into this account with an alternative account's code. Executes code starting at
    the address to which the call is made.

    Inputs
    ----
    - gas: amount of gas to send to the sub context to execute. The gas that is not used by the sub
      context is returned to this one.
    - address: the account which code to execute
    - value: value in wei to send to the account
    - argsOffset: byte offset in the memory in bytes, the calldata of the sub context
    - argsSize: byte size to copy (size of the calldata)
    - retOffset: byte offset in the memory in bytes, where to store the return data of the sub
      context
    - retSize: byte size to copy (size of the return data)
    Outputs
    ----
    - success: return 0 if the sub context reverted, 1 otherwise

    Fork
    ----
    Frontier

    Gas
    ----
    memory_expansion_cost + code_execution_cost + address_access_cost + positive_value_cost

    Source: [evm.codes/#F2](https://www.evm.codes/#F2)
    """

    RETURN = Opcode(0xF3, popped_stack_items=2)
    """
    RETURN(offset, size)
    ----

    Description
    ----
    Halt execution returning output data.

    Inputs
    ----
    - offset: The memory offset to the output data.
    - size: The size of the output data.

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    memory_expansion_cost

    Source: [evm.codes/#F3](https://www.evm.codes/#F3)
    """

    DELEGATECALL = Opcode(0xF4, popped_stack_items=6, pushed_stack_items=1)
    """
    DELEGATECALL(gas, address, argsOffset, argsSize, retOffset, retSize) = success
    ----

    Description
    ----
    Message-call into this account with an alternative account’s code, but persisting the current
    values for sender and value

    Inputs
    ----
    - gas: amount of gas to send to the sub context to execute. The gas that is not used by the sub
      context is returned to this one
    - address: the account which code to execute
    - argsOffset: byte offset in the memory in bytes, the calldata of the sub context
    - argsSize: byte size to copy (size of the calldata)
    - retOffset: byte offset in the memory in bytes, where to store the return data of the sub
      context.
    - retSize: byte size to copy (size of the return data)

    Outputs
    ----
    - success: return 0 if the sub context reverted, 1 otherwise

    Fork
    ----
    Byzantium

    Gas
    ----
    memory_expansion_cost + code_execution_cost + address_access_cost

    Source: [evm.codes/#F4](https://www.evm.codes/#F4)
    """

    CREATE2 = Opcode(0xF5, popped_stack_items=4, pushed_stack_items=1)
    """
    CREATE2(value, offset, size, salt) = address
    ----

    Description
    ----
    Creates a new contract.

    Inputs
    ----
    - value: value in wei to send to the new account.
    - offset: byte offset in the memory in bytes, the initialisation code of the new account.
    - size: byte size to copy (size of the initialisation code).
    - salt: 32-byte value used to create the new account at a deterministic address

    Outputs
    ----
    - address: the address of the deployed contract, 0 if the deployment failed

    Fork
    ----
    Constantinople

    Gas
    ----
    minimum_word_size = (size + 31) / 32 init_code_cost = 2 * minimum_word_size hash_cost = 6 *
    minimum_word_size code_deposit_cost = 200 * deployed_code_size

    32000 + init_code_cost + hash_cost + memory_expansion_cost + deployment_code_execution_cost +
    code_deposit_cost

    Source: [evm.codes/#F5](https://www.evm.codes/#F5)
    """

    STATICCALL = Opcode(0xFA, popped_stack_items=6, pushed_stack_items=1)
    """
    STATICCALL(gas, address, argsOffset, argsSize, retOffset , retSize) = success
    ----

    Description
    ----
    Static message-call into an account

    Inputs
    ----
    - gas: amount of gas to send to the sub context to execute. The gas that is not used by the sub
      context is returned to this one.
    - address: the account which context to execute.
    - argsOffset: byte offset in the memory in bytes, the calldata of the sub context.
    - argsSize: byte size to copy (size of the calldata).
    - retOffset: byte offset in the memory in bytes, where to store the return data of the sub
      context.
    - retSize: byte size to copy (size of the return data)

    Outputs
    ----
    - success: return 0 if the sub context reverted, 1 otherwise

    Fork
    ----
    Byzantium

    Gas
    ----
    memory_expansion_cost + code_execution_cost + address_access_cost

    Source: [evm.codes/#FA](https://www.evm.codes/#FA)
    """

    REVERT = Opcode(0xFD, popped_stack_items=2)
    """
    REVERT(offset, length)
    ----

    Description
    ----
    Stop execution and revert changes.

    Inputs
    ----
    - offset: byte offset in the memory in bytes. The return data of the calling context.
    - size: byte size to copy (size of the return data).

    Fork
    ----
    Byzantium

    Gas
    ----
    0

    Source: [evm.codes/#FD](https://www.evm.codes/#FD)
    """

    INVALID = Opcode(0xFE)
    """
    INVALID()
    ----

    Description
    ----
    Invalid opcode.

    Inputs
    ----
    None

    Outputs
    ----
    None

    Fork
    ----
    Frontier

    Gas
    ----
    All the remaining gas in this context is consumed

    Source: [evm.codes/#FE](https://www.evm.codes/#FE)
    """

    SELFDESTRUCT = Opcode(0xFF, popped_stack_items=1)
    """
    SELFDESTRUCT(to)
    ----

    Description
    ----
    Halt execution and register the account for later deletion.

    Inputs
    ----
    - to: The address to which any remaining funds are transferred.

    Fork
    ----
    Frontier

    Gas
    ----
    5000

    Source: [evm.codes/#FF](https://www.evm.codes/#FF)
    """

    SENDALL = Opcode(0xFF, popped_stack_items=1)
    """
    SENDALL(to)
    ----

    Description
    ----
    Send all ether to the target address and halt execution.

    Inputs
    ----
    - to: Target address

    Outputs
    ----
    - None

    Fork
    ----
    Frontier

    Gas
    ----
    5000

    Source: [eips.ethereum.org/EIPS/eip-6780](https://eips.ethereum.org/EIPS/eip-6780)
    """
