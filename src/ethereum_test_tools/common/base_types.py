"""
Basic type primitives used to define other types.
"""

from pydantic import TypeAdapter
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from .conversions import (
    from_bytes,
    from_fixed_size_bytes,
    from_hex_number,
    to_bytes,
    to_fixed_size_bytes,
    to_hex_number,
)

from_address = from_fixed_size_bytes(20)
to_address = to_fixed_size_bytes(20)
AddressType = Annotated[
    bytes,
    BeforeValidator(from_address),
    PlainSerializer(to_address),
]
Address = TypeAdapter(AddressType).validate_python

from_hash = from_fixed_size_bytes(32)
to_hash = to_fixed_size_bytes(32)
HashType = Annotated[
    bytes,
    BeforeValidator(from_hash),
    PlainSerializer(to_hash),
]
Hash = TypeAdapter(HashType).validate_python

from_bloom = from_fixed_size_bytes(256)
to_bloom = to_fixed_size_bytes(256)
BloomType = Annotated[
    bytes,
    BeforeValidator(from_bloom),
    PlainSerializer(to_bloom),
]
Bloom = TypeAdapter(BloomType).validate_python

from_header_nonce = from_fixed_size_bytes(8)
to_header_nonce = to_fixed_size_bytes(8)
HeaderNonceType = Annotated[
    bytes,
    BeforeValidator(from_header_nonce),
    PlainSerializer(to_header_nonce),
]
HeaderNonce = TypeAdapter(HeaderNonceType).validate_python


HexNumberType = Annotated[
    int,
    BeforeValidator(to_hex_number),
    PlainSerializer(from_hex_number),
]
Number = TypeAdapter(HexNumberType).validate_python
HexNumber = Number
HexBytesType = Annotated[
    bytes,
    BeforeValidator(to_bytes),
    PlainSerializer(from_bytes),
]
Bytes = TypeAdapter(HexBytesType).validate_python
