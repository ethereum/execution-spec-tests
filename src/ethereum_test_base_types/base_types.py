"""Basic type primitives used to define other types."""

from typing import Any, ClassVar, SupportsBytes, Type, TypeVar, cast

from Crypto.Hash import keccak
from pydantic import GetCoreSchemaHandler
from pydantic_core.core_schema import (
    PlainValidatorFunctionSchema,
    no_info_plain_validator_function,
    to_string_ser_schema,
)

from .conversions import (
    BytesConvertible,
    FixedSizeBytesConvertible,
    NumberConvertible,
    to_bytes,
    to_fixed_size_bytes,
    to_number,
)

N = TypeVar("N", bound="Number")


class ToStringSchema:
    """
    Type converter to add a simple pydantic schema that correctly parses
    and serializes the type.
    """

    @staticmethod
    def __get_pydantic_core_schema__(
        source_type: Any, handler: GetCoreSchemaHandler
    ) -> PlainValidatorFunctionSchema:
        """Call the class constructor without info and appends the serialization schema."""
        return no_info_plain_validator_function(
            source_type,
            serialization=to_string_ser_schema(),
        )


class Number(int, ToStringSchema):
    """Class that helps represent numbers in tests."""

    def __new__(cls, value: NumberConvertible | N):
        """Create a new Number object."""
        return super(Number, cls).__new__(cls, to_number(value))

    def __str__(self) -> str:
        """Return the string representation of the number."""
        return str(int(self))

    def hex(self) -> str:
        """Return the hexadecimal representation of the number."""
        return hex(self)

    @classmethod
    def or_none(cls: Type[N], value: N | NumberConvertible | None) -> N | None:
        """Convert the value to a Number while accepting None."""
        if value is None:
            return value
        return cls(value)


class HexNumber(Number):
    """Class that helps represent an hexadecimal numbers in tests."""

    def __str__(self) -> str:
        """Return the string representation of the number."""
        return self.hex()


class ZeroPaddedHexNumber(HexNumber):
    """Class that helps represent zero padded hexadecimal numbers in tests."""

    def hex(self) -> str:
        """Return the hexadecimal representation of the number."""
        if self == 0:
            return "0x00"
        hex_str = hex(self)[2:]
        if len(hex_str) % 2 == 1:
            return "0x0" + hex_str
        return "0x" + hex_str


NumberBoundTypeVar = TypeVar("NumberBoundTypeVar", Number, HexNumber, ZeroPaddedHexNumber)


class Bytes(bytes, ToStringSchema):
    """Class that helps represent bytes of variable length in tests."""

    def __new__(cls, value: BytesConvertible):
        """Create a new Bytes object."""
        if type(value) is cls:
            return value
        return super(Bytes, cls).__new__(cls, to_bytes(value))

    def __hash__(self) -> int:
        """Return the hash of the bytes."""
        return super(Bytes, self).__hash__()

    def __str__(self) -> str:
        """Return the hexadecimal representation of the bytes."""
        return self.hex()

    def hex(self, *args, **kwargs) -> str:
        """Return the hexadecimal representation of the bytes."""
        return "0x" + super().hex(*args, **kwargs)

    @classmethod
    def or_none(cls, value: "Bytes | BytesConvertible | None") -> "Bytes | None":
        """Convert the value to a Bytes while accepting None."""
        if value is None:
            return value
        return cls(value)

    def keccak256(self) -> "Bytes":
        """Return the keccak256 hash of the opcode byte representation."""
        k = keccak.new(digest_bits=256)
        return Bytes(k.update(bytes(self)).digest())


S = TypeVar("S", bound="FixedSizeHexNumber")


class FixedSizeHexNumber(int, ToStringSchema):
    """
    A base class that helps represent an integer as a fixed byte-length
    hexadecimal number.

    This class is used to dynamically generate subclasses of a specific byte
    length.
    """

    byte_length: ClassVar[int]
    max_value: ClassVar[int]

    def __class_getitem__(cls, length: int) -> Type["FixedSizeHexNumber"]:
        """Create a new FixedSizeHexNumber class with the given length."""

        class Sized:
            byte_length = length
            max_value = 2 ** (8 * length) - 1

        return cast(Type["FixedSizeHexNumber"], Sized)

    def __new__(cls, value: NumberConvertible | N):
        """Create a new Number object."""
        i = to_number(value)
        if i > cls.max_value:
            raise ValueError(f"Value {i} is too large for {cls.byte_length} bytes")
        if i < 0:
            i += cls.max_value + 1
            if i <= 0:
                raise ValueError(f"Value {i} is too small for {cls.byte_length} bytes")
        return super(FixedSizeHexNumber, cls).__new__(cls, i)

    def __str__(self) -> str:
        """Return the string representation of the number."""
        return self.hex()

    def hex(self) -> str:
        """Return the hexadecimal representation of the number."""
        if self == 0:
            return "0x00"
        hex_str = hex(self)[2:]
        if len(hex_str) % 2 == 1:
            return "0x0" + hex_str
        return "0x" + hex_str


class HashInt(FixedSizeHexNumber):
    """Class that helps represent hashes in tests."""

    byte_length: ClassVar[int] = 32
    max_value: ClassVar[int] = 2 ** (8 * byte_length) - 1


T = TypeVar("T", bound="FixedSizeBytes")


class FixedSizeBytes(Bytes):
    """Class that helps represent bytes of fixed length in tests."""

    byte_length: ClassVar[int]

    def __class_getitem__(cls, length: int) -> Type["FixedSizeBytes"]:
        """Create a new FixedSizeBytes class with the given length."""

        class Sized:
            byte_length: ClassVar[int] = length

        return cast(Type["FixedSizeBytes"], Sized)

    def __new__(cls, value: FixedSizeBytesConvertible | T):
        """Create a new FixedSizeBytes object."""
        if type(value) is cls:
            return value
        return super(FixedSizeBytes, cls).__new__(cls, to_fixed_size_bytes(value, cls.byte_length))

    def __hash__(self) -> int:
        """Return the hash of the bytes."""
        return super(FixedSizeBytes, self).__hash__()

    @classmethod
    def or_none(cls: Type[T], value: T | FixedSizeBytesConvertible | None) -> T | None:
        """Convert the input to a Fixed Size Bytes while accepting None."""
        if value is None:
            return value
        return cls(value)

    def __eq__(self, other: object) -> bool:
        """Compare two FixedSizeBytes objects to be equal."""
        if not isinstance(other, FixedSizeBytes):
            assert (
                isinstance(other, str)
                or isinstance(other, int)
                or isinstance(other, bytes)
                or isinstance(other, SupportsBytes)
            )
            other = self.__class__(other)
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        """Compare two FixedSizeBytes objects to be not equal."""
        return not self.__eq__(other)


class Address(FixedSizeBytes):
    """Class that helps represent Ethereum addresses in tests."""

    byte_length: ClassVar[int] = 20
    label: str | None = None


class Hash(FixedSizeBytes):
    """Class that helps represent hashes in tests."""

    byte_length: ClassVar[int] = 32
    pass


class Bloom(FixedSizeBytes):
    """Class that helps represent blooms in tests."""

    byte_length: ClassVar[int] = 256
    pass


class HeaderNonce(FixedSizeBytes):
    """Class that helps represent the header nonce in tests."""

    byte_length: ClassVar[int] = 8
    pass


class BLSPublicKey(FixedSizeBytes):
    """Class that helps represent BLS public keys in tests."""

    byte_length: ClassVar[int] = 48
    pass


class BLSSignature(FixedSizeBytes):
    """Class that helps represent BLS signatures in tests."""

    byte_length: ClassVar[int] = 96
    pass
