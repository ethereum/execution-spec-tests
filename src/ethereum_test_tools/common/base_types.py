"""
Basic type primitives used to define other types.
"""

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
Address = Annotated[
    bytes,
    BeforeValidator(from_address),
    PlainSerializer(to_address),
]

from_hash = from_fixed_size_bytes(32)
to_hash = to_fixed_size_bytes(32)
Hash = Annotated[
    bytes,
    BeforeValidator(from_hash),
    PlainSerializer(to_hash),
]

from_bloom = from_fixed_size_bytes(256)
to_bloom = to_fixed_size_bytes(256)
Bloom = Annotated[
    bytes,
    BeforeValidator(from_bloom),
    PlainSerializer(to_bloom),
]

from_header_nonce = from_fixed_size_bytes(8)
to_header_nonce = to_fixed_size_bytes(8)
HeaderNonce = Annotated[
    bytes,
    BeforeValidator(from_header_nonce),
    PlainSerializer(to_header_nonce),
]


HexNumber = Annotated[
    int,
    BeforeValidator(to_hex_number),
    PlainSerializer(from_hex_number),
]
HexBytes = Annotated[
    bytes,
    BeforeValidator(to_bytes),
    PlainSerializer(from_bytes),
]
