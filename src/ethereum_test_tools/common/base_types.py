"""
Basic type primitives used to define other types.
"""

from itertools import count, cycle
from typing import (
    Any,
    ClassVar,
    Dict,
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


class DataclassGenerator(Iterator[C]):
    """
    Class that creates dataclass generators.
    """

    # Class fields
    _dataclass: ClassVar[Type]
    _iterable_fields: ClassVar[List[str]]
    _index_field: ClassVar[Optional[str]] = None
    _iter_suffix: ClassVar[str] = "_iter"

    # Instance fields
    iterators: Dict[str, Iterator[Any]]
    limit: int
    chunk_size: int
    new_chunk: bool = True
    iterations: int = 0

    @staticmethod
    def _field_type_is_iterable(field_type: Any) -> bool:
        origin = get_origin(field_type)
        types: List[Any] = (
            [get_origin(arg) for arg in get_args(field_type)] if origin == Union else [origin]
        )
        return any(
            t is not None and t != bytes and t != str and issubclass(t, Iterable) for t in types
        )

    def __init_subclass__(cls, *, dataclass: Type[C], index_field: Optional[str] = None) -> None:
        """
        Initializes the subclass.

        Dataclass might behave incorrectly if it has fields named `limit` or `chunk_size`.
        """
        cls._dataclass = dataclass
        cls._iterable_fields = [
            field
            for field, field_type in get_type_hints(dataclass).items()
            if cls._field_type_is_iterable(field_type)
        ]
        cls._index_field = index_field

    def __init__(self, *, limit: int = 0, chunk_size: int = 0, **kwargs: Any):
        """
        Initializes the dataclass generator.
        """
        any_finite_iterator = False
        self.iterators: Dict[str, Iterator[Any]] = {}

        for field in self._iterable_fields:
            field_with_suffix = f"{field}{self._iter_suffix}"
            if field in kwargs or field_with_suffix in kwargs:
                if field in kwargs and field_with_suffix in kwargs:
                    raise ValueError(f"cannot set both {field} and {field_with_suffix}")
                if field in kwargs:
                    self.iterators[field] = cycle([kwargs.pop(field)])
                else:
                    any_finite_iterator = True
                    value = kwargs.pop(field_with_suffix)
                    assert value is not None, f"value for {field_with_suffix} cannot be None"
                    if isinstance(value, Iterator):
                        self.iterators[field] = value
                    elif isinstance(value, Iterable):
                        self.iterators[field] = iter(value)
                    else:
                        raise ValueError(
                            f"value for {field_with_suffix} must be an iterator or iterable"
                        )

        if self._index_field:
            index_value = kwargs.pop(self._index_field, 0)
            if isinstance(index_value, int):
                index_value = count(index_value)
            elif isinstance(index_value, Iterable):
                any_finite_iterator = True
                index_value = iter(index_value)
            self.iterators[self._index_field] = index_value

        for arg, value in kwargs.items():
            if value is not None and isinstance(value, Iterator):
                any_finite_iterator = True
                self.iterators[arg] = value
            elif (
                value is not None
                and isinstance(value, Iterable)
                and not isinstance(value, str)
                and not isinstance(value, bytes)
            ):
                any_finite_iterator = True
                self.iterators[arg] = iter(value)
            else:
                self.iterators[arg] = cycle([value])

        assert (
            any_finite_iterator or limit > 0 or chunk_size > 0
        ), "at least one field must be an iterable, or limit or chunk_size must be set"
        self.limit = limit
        self.chunk_size = chunk_size
        self.iterations = 0

    def __iter__(self) -> Iterator[C]:
        """
        Returns an iterator over the elements.
        """
        return self

    def __next__(self) -> C:
        """
        Returns the next dataclass element in the sequence.
        """
        if self.limit > 0 and self.iterations >= self.limit:
            raise StopIteration

        if self.chunk_size > 0 and self.iterations % self.chunk_size == 0 and not self.new_chunk:
            self.new_chunk = True
            raise StopIteration

        self.new_chunk = False
        self.iterations += 1

        return self._dataclass(**{arg: next(iterator) for arg, iterator in self.iterators.items()})
