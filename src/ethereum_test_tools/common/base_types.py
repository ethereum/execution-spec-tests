"""
Basic type primitives used to define other types.
"""

from typing import Any, ClassVar, Optional, SupportsBytes, Type, TypeVar

from pydantic_core.core_schema import (
    CoreSchema,
    ValidationInfo,
    int_schema,
    plain_serializer_function_ser_schema,
    with_info_before_validator_function,
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


class Number(int):
    """
    Class that helps represent numbers in tests.
    """

    def __new__(cls, input: NumberConvertible | N):
        """
        Creates a new Number object.
        """
        return super(Number, cls).__new__(cls, to_number(input))

    @classmethod
    def __get_pydantic_core_schema__(cls, value, handle=None) -> CoreSchema:
        schema = with_info_before_validator_function(
            function=cls.__eth_pydantic_validate__, schema=int_schema()
        )
        schema["serialization"] = plain_serializer_function_ser_schema(cls.serialize)
        return schema

    def __str__(self) -> str:
        """
        Returns the string representation of the number.
        """
        return str(int(self))

    @classmethod
    def __eth_pydantic_validate__(
        cls, value: Any, info: Optional[ValidationInfo] = None
    ) -> "Number":
        """
        Validates the input and returns a Number object.
        """
        return cls(value)

    def hex(self) -> str:
        """
        Returns the hexadecimal representation of the number.
        """
        return hex(self)

    @staticmethod
    def serialize(value: int) -> str:
        """
        Returns the serialized representation of the number.
        """
        return str(value)

    @classmethod
    def or_none(cls: Type[N], input: N | NumberConvertible | None) -> N | None:
        """
        Converts the input to a Number while accepting None.
        """
        if input is None:
            return input
        return cls(input)


class HexNumber(Number):
    """
    Class that helps represent an hexadecimal numbers in tests.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, value, handle=None) -> CoreSchema:
        schema = with_info_before_validator_function(
            cls.__eth_pydantic_validate__,
            int_schema(serialization=plain_serializer_function_ser_schema(cls.serialize)),
        )
        return schema

    def __str__(self) -> str:
        """
        Returns the string representation of the number.
        """
        return self.hex()

    @staticmethod
    def serialize(value: int) -> str:
        """
        Returns the serialized representation of the number.
        """
        return hex(value)


class ZeroPaddedHexNumber(HexNumber):
    """
    Class that helps represent zero padded hexadecimal numbers in tests.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, value, handle=None) -> CoreSchema:
        schema = with_info_before_validator_function(cls.__eth_pydantic_validate__, int_schema())
        schema["serialization"] = plain_serializer_function_ser_schema(cls.serialize)
        return schema

    def hex(self) -> str:
        """
        Returns the hexadecimal representation of the number.
        """
        if self == 0:
            return "0x00"
        hex_str = hex(self)[2:]
        if len(hex_str) % 2 == 1:
            return "0x0" + hex_str
        return "0x" + hex_str

    @staticmethod
    def serialize(value: int) -> str:
        """
        Returns the serialized representation of the number.
        """
        if value == 0:
            return "0x00"
        hex_str = hex(value)[2:]
        if len(hex_str) % 2 == 1:
            return "0x0" + hex_str
        return "0x" + hex_str


class Bytes(bytes):
    """
    Class that helps represent bytes of variable length in tests.
    """

    def __new__(cls, input: BytesConvertible):
        """
        Creates a new Bytes object.
        """
        return super(Bytes, cls).__new__(cls, to_bytes(input))

    def __hash__(self) -> int:
        """
        Returns the hash of the bytes.
        """
        return super(Bytes, self).__hash__()

    def __str__(self) -> str:
        """
        Returns the hexadecimal representation of the bytes.
        """
        return self.hex()

    def hex(self, *args, **kwargs) -> str:
        """
        Returns the hexadecimal representation of the bytes.
        """
        return "0x" + super().hex(*args, **kwargs)

    @classmethod
    def or_none(cls, input: "Bytes | BytesConvertible | None") -> "Bytes | None":
        """
        Converts the input to a Bytes while accepting None.
        """
        if input is None:
            return input
        return cls(input)


T = TypeVar("T", bound="FixedSizeBytes")


class FixedSizeBytes(Bytes):
    """
    Class that helps represent bytes of fixed length in tests.
    """

    byte_length: ClassVar[int]

    def __class_getitem__(cls, length: int) -> Type["FixedSizeBytes"]:
        """
        Creates a new FixedSizeBytes class with the given length.
        """

        class Sized(cls):  # type: ignore
            byte_length = length

        return Sized

    def __new__(cls, input: FixedSizeBytesConvertible | T):
        """
        Creates a new FixedSizeBytes object.
        """
        return super(FixedSizeBytes, cls).__new__(cls, to_fixed_size_bytes(input, cls.byte_length))

    def __hash__(self) -> int:
        """
        Returns the hash of the bytes.
        """
        return super(FixedSizeBytes, self).__hash__()

    @classmethod
    def or_none(cls: Type[T], input: T | FixedSizeBytesConvertible | None) -> T | None:
        """
        Converts the input to a Fixed Size Bytes while accepting None.
        """
        if input is None:
            return input
        return cls(input)

    def __eq__(self, other: object) -> bool:
        """
        Compares two FixedSizeBytes objects to be equal.
        """
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
        """
        Compares two FixedSizeBytes objects to be not equal.
        """
        return not self.__eq__(other)


class Address(FixedSizeBytes[20]):  # type: ignore
    """
    Class that helps represent Ethereum addresses in tests.
    """

    pass


class Hash(FixedSizeBytes[32]):  # type: ignore
    """
    Class that helps represent hashes in tests.
    """

    pass


class Bloom(FixedSizeBytes[256]):  # type: ignore
    """
    Class that helps represent blooms in tests.
    """

    pass


class HeaderNonce(FixedSizeBytes[8]):  # type: ignore
    """
    Class that helps represent the header nonce in tests.
    """

    pass
