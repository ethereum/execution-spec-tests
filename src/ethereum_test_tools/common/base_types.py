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
    Type converter to add a simple pydantic schema that correctly parses and serializes the type.
    """

    @staticmethod
    def __get_pydantic_core_schema__(
        source_type: Any, handler: GetCoreSchemaHandler
    ) -> PlainValidatorFunctionSchema:
        """
        Calls the class constructor without info and appends the serialization schema.
        """
        return no_info_plain_validator_function(
            source_type,
            serialization=to_string_ser_schema(),
        )


class Number(int, ToStringSchema):
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


NumberBoundTypeVar = TypeVar("NumberBoundTypeVar", Number, HexNumber, ZeroPaddedHexNumber)


class Bytes(bytes, ToStringSchema):
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
        """
        Creates a new FixedSizeHexNumber class with the given length.
        """

        class Sized(cls):  # type: ignore
            byte_length = length
            max_value = 2 ** (8 * length) - 1

        return Sized

    def __new__(cls, input: NumberConvertible | N):
        """
        Creates a new Number object.
        """
        i = to_number(input)
        if i > cls.max_value:
            raise ValueError(f"Value {i} is too large for {cls.byte_length} bytes")
        if i < 0:
            i += cls.max_value + 1
            if i <= 0:
                raise ValueError(f"Value {i} is too small for {cls.byte_length} bytes")
        return super(FixedSizeHexNumber, cls).__new__(cls, i)

    def __str__(self) -> str:
        """
        Returns the string representation of the number.
        """
        return self.hex()

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


class HashInt(FixedSizeHexNumber[32]):  # type: ignore
    """
    Class that helps represent hashes in tests.
    """

    pass


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


C = TypeVar("C")


class ModelIterator(Iterator[C]):
    """
    Class that creates model iterators.
    """

    # Instance fields
    limit: int
    iterations: int
    iterators: Dict[str, Iterator[Any]]

    # Class fields
    _model: ClassVar[Type]
    _max_iterations: ClassVar[int] = 1000

    def __init_subclass__(cls, *, model: Type[C], max_iterations: int = 1000) -> None:
        """
        Initializes the subclass.

        Model might behave incorrectly if it has a field named `limit`.
        """
        cls._model = model
        cls._max_iterations = max_iterations

    def __init__(self, iterators: Dict[str, Iterator[Any]], limit: int):
        """
        Initializes the model iterator.
        """
        self.iterators = iterators
        self.limit = limit
        self.iterations = 0

    def __next__(self) -> C:
        """
        Returns the next model element in the sequence.
        """
        if self.limit >= 0 and self.iterations >= self.limit:
            raise StopIteration
        if self.iterations > self._max_iterations:
            raise ValueError(f"exceeded maximum number of iterations ({self._max_iterations})")
        self.iterations += 1
        args = {arg: next(iterator) for arg, iterator in self.iterators.items()}
        return self._model(**args)


class ModelGenerator(Iterable[C]):
    """
    Class that creates model generators.
    """

    # Class fields
    _model_iterator: ClassVar[Type[ModelIterator]]
    _iterable_fields: ClassVar[List[str]]
    _index_field: ClassVar[Optional[str]] = None
    _iter_suffix: ClassVar[str] = "_iter"

    # Instance fields
    iterators: Dict[str, Iterator[Any]]
    limits: Iterator[int]
    current_limit: int
    current_iterations: int = 0

    @staticmethod
    def _field_type_is_iterable(field: str, field_type: Any) -> bool:
        origin = get_origin(field_type)
        types: List[Any] = (
            [get_origin(arg) for arg in get_args(field_type)] if origin == Union else [origin]
        )
        return any(
            t is not None and t != bytes and t != str and t != ClassVar and issubclass(t, Iterable)
            for t in types
        )

    def __init_subclass__(
        cls,
        *,
        model: Type[C],
        index_field: Optional[str] = None,
        max_iterations: int = 1000,
    ) -> None:
        """
        Initializes the subclass.

        Model might behave incorrectly if it has a field named `limit`.
        """
        cls._iterable_fields = [
            field
            for field, field_type in get_type_hints(model).items()
            if cls._field_type_is_iterable(field, field_type)
        ]
        cls._index_field = index_field
        cls._model_iterator = type(
            f"{model.__name__}Iterator",
            (ModelIterator,),
            {},
            model=model,
            max_iterations=max_iterations,
        )

    def __init__(self, *, limit: int | Iterable[int] | Iterator[int] = -1, **kwargs: Any):
        """
        Initializes the model generator.
        """
        self.iterators: Dict[str, Iterator[Any]] = {}
        for field in self._iterable_fields:
            field_with_suffix = f"{field}{self._iter_suffix}"
            if field in kwargs or field_with_suffix in kwargs:
                if field in kwargs and field_with_suffix in kwargs:
                    raise ValueError(f"cannot set both {field} and {field_with_suffix}")
                if field in kwargs:
                    self.iterators[field] = cycle([kwargs.pop(field)])
                else:
                    value = kwargs.pop(field_with_suffix)
                    assert value is not None, f"value for {field_with_suffix} cannot be None"
                    assert not isinstance(
                        value, ModelGenerator
                    ), f"""
                        Iter value for {field_with_suffix} in {self.__class__.__name__} cannot
                        be a ModelGenerator ({value.__class__.__name__}).
                        Use the normal field name without the suffix ({field}) instead.
                        """
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
                index_value = iter(index_value)
            self.iterators[self._index_field] = index_value

        for arg, value in kwargs.items():
            if value is not None and isinstance(value, Iterator):
                self.iterators[arg] = value
            elif (
                value is not None
                and isinstance(value, Iterable)
                and not isinstance(value, str)
                and not isinstance(value, bytes)
            ):
                self.iterators[arg] = iter(value)
            else:
                self.iterators[arg] = cycle([value])

        self.limits = iter(cycle([limit])) if isinstance(limit, int) else iter(limit)

    def __iter__(self) -> Iterator[C]:
        """
        Returns an iterator over the elements.
        """
        try:
            current_limit = next(self.limits)
        except StopIteration:
            current_limit = -1
        return self._model_iterator(self.iterators, current_limit)
