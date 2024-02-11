"""
Basic type primitives used to define other types.
"""

from itertools import count, cycle
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    SupportsBytes,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from .conversions import (
    BytesConvertible,
    FixedSizeBytesConvertible,
    NumberConvertible,
    to_bytes,
    to_fixed_size_bytes,
    to_number,
)
from .json import JSONEncoder, SupportsJSON

N = TypeVar("N", bound="Number")


class Number(int, SupportsJSON):
    """
    Class that helps represent numbers in tests.
    """

    def __new__(cls, input: NumberConvertible | N):
        """
        Creates a new Number object.
        """
        return super(Number, cls).__new__(cls, to_number(input))

    def __str__(self) -> str:
        """
        Returns the string representation of the number.
        """
        return str(int(self))

    def __json__(self, encoder: JSONEncoder) -> str:
        """
        Returns the JSON representation of the number.
        """
        return str(self)

    def hex(self) -> str:
        """
        Returns the hexadecimal representation of the number.
        """
        return hex(self)

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

    def __str__(self) -> str:
        """
        Returns the string representation of the number.
        """
        return self.hex()


class ZeroPaddedHexNumber(HexNumber):
    """
    Class that helps represent zero padded hexadecimal numbers in tests.
    """

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


class Bytes(bytes, SupportsJSON):
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

    def __json__(self, encoder: JSONEncoder) -> str:
        """
        Returns the JSON representation of the bytes.
        """
        return str(self)

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
        Compares two FixedSizeBytes objects.
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


C = TypeVar("C")


class DataclassGenerator(Iterable[C]):
    """
    Class that creates dataclass generators.
    """

    # Class fields
    _dataclass_type: ClassVar[Type]
    _list_fields: ClassVar[List[str]]
    _nonce_field: ClassVar[Optional[str]] = None

    # Instance fields
    arguments: Dict[str, Iterator[Any]]
    limit: int
    iterations: int = 0

    @classmethod
    def __class_getitem__(cls: type, C: Type) -> Type:
        """
        Creates a new dataclass generator.
        """
        _list_fields = []
        for field, field_type in get_type_hints(C).items():
            origin = get_origin(field_type)
            if origin == Union:
                for arg in get_args(field_type):
                    origin = get_origin(arg)
                    if (
                        origin is not None
                        and issubclass(origin, Iterable)
                        and origin != bytes
                        and origin != str
                    ):
                        _list_fields.append(field)
                        break
            elif (
                origin is not None
                and issubclass(origin, Iterable)
                and field_type != bytes
                and field_type != str
            ):
                _list_fields.append(field)

        class DataclassGeneratorSubclass(cls):
            pass

        DataclassGeneratorSubclass._dataclass_type = C
        DataclassGeneratorSubclass._list_fields = _list_fields

        return DataclassGeneratorSubclass

    def __init_subclass__(cls, *, nonce_field: Optional[str] = None) -> None:
        """
        Initializes the subclass.
        """
        cls._nonce_field = nonce_field

    def __init__(self, *, limit: int = 0, **kwargs: Any):
        """
        Initializes the dataclass generator.
        """
        iterator_count = 0
        self.arguments: Dict[str, Iterator[Any]] = {}

        for field in self._list_fields:
            if field in kwargs or f"{field}_list" in kwargs:
                if field in kwargs and f"{field}_list" in kwargs:
                    raise ValueError(f"cannot set both {field} and {field}_list")
                if field in kwargs:
                    self.arguments[field] = cycle([kwargs.pop(field)])
                else:
                    iterator_count += 1
                    value = kwargs.pop(f"{field}_list")
                    assert isinstance(
                        value, Iterable
                    ), f"value for {field}_list must be an iterable"
                    self.arguments[field] = iter(value)

        if self._nonce_field is not None:
            nonce = kwargs.pop(self._nonce_field, 0)

            if isinstance(nonce, int):
                nonce = count(nonce)
            elif isinstance(nonce, Iterable):
                iterator_count += 1
                nonce = iter(nonce)

            self.arguments[self._nonce_field] = nonce

        for arg in kwargs:
            value = kwargs[arg]
            if isinstance(value, Iterator):
                iterator_count += 1
                self.arguments[arg] = value
            elif (
                isinstance(value, Iterable)
                and not isinstance(value, str)
                and not isinstance(value, bytes)
            ):
                iterator_count += 1
                self.arguments[arg] = iter(value)
            else:
                self.arguments[arg] = cycle([value])

        assert iterator_count > 0 or limit > 0, "at least one field must be an iterable or limit"
        "must be set"
        self.limit = limit
        self.iterations = 0

    def __iter__(self) -> Iterator[C]:
        """
        Returns an iterator over the transactions.
        """
        return self

    def __next__(self) -> Type[C]:
        """
        Returns the next transaction in the sequence.
        """
        if self.limit > 0 and self.iterations >= self.limit:
            raise StopIteration

        self.iterations += 1

        kwargs = {arg: next(self.arguments[arg]) for arg in self.arguments}
        return self._dataclass_type(**kwargs)
