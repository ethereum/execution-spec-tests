"""Ethereum test types for serialization and encoding."""

from typing import Any, ClassVar, List

import ethereum_rlp as eth_rlp
from ethereum_types.numeric import Uint

from ethereum_test_base_types import Bytes


def to_serializable_element(v: Any) -> Any:
    """Return a serializable element that can be passed to `eth_rlp.encode`."""
    if isinstance(v, int):
        return Uint(v)
    elif isinstance(v, bytes):
        return v
    elif isinstance(v, list):
        return [to_serializable_element(v) for v in v]
    elif isinstance(v, RLPSerializable):
        if v.signable:
            v.sign()
        return v.to_list(signing=False)
    raise Exception(f"Unable to serialize element {v} of type {type(v)}.")


class RLPSerializable:
    """Class that adds RLP serialization to another class."""

    signable: ClassVar[bool] = False
    rlp_fields: ClassVar[List[str]]
    rlp_signing_fields: ClassVar[List[str]]

    def get_rlp_fields(self) -> List[str]:
        """
        Return a list containing the ordered names of the list that need be included
        in the list of RLP fields to serialize for the RLP object.

        Function can be overridden to customize the logic to return the fields.

        By default, rlp_fields class variable is used.
        """
        return self.rlp_fields

    def get_rlp_signing_fields(self) -> List[str]:
        """
        Return a list contained the ordered names of the list that need be included
        in the list of RLP fields to serialize for the object signature.

        Function can be overridden to customize the logic to return the fields.

        By default, rlp_signing_fields class variable is used.
        """
        return self.rlp_signing_fields

    def get_rlp_prefix(self) -> bytes:
        """
        Return a prefix that has to be appended to the serialized object.

        By default, an empty string is returned.
        """
        return b""

    def get_rlp_signing_prefix(self) -> bytes:
        """
        Return a prefix that has to be appended to the serialized signing object.

        By default, an empty string is returned.
        """
        return b""

    def sign(self):
        """Sign the current object for further serialization."""
        raise NotImplementedError(f'Object "{self.__class__.__name__}" cannot be signed.')

    def to_list(self, signing: bool = False) -> List[Any]:
        """
        Return an RLP serializable list that can be passed to `eth_rlp.encode`.

        Can be for signing purposes or the entire object.
        """
        field_list: List[str]
        if signing:
            if not self.signable:
                raise Exception(f'Object "{self.__class__.__name__}" does not support signing')
            field_list = self.get_rlp_signing_fields()
        else:
            if self.signable:
                self.sign()
            field_list = self.get_rlp_fields()

        values_list: List[Any] = []
        for field in field_list:
            assert hasattr(self, field), (
                f'Unable to rlp serialize field "{field}" '
                f'in object type "{self.__class__.__name__}"'
            )
            try:
                values_list.append(to_serializable_element(getattr(self, field)))
            except Exception as e:
                raise Exception(
                    f'Unable to rlp serialize field "{field}" '
                    f'in object type "{self.__class__.__name__}"'
                ) from e
        return values_list

    def rlp_signing_envelope(self) -> Bytes:
        """Return the signing serialized envelope used for signing."""
        return Bytes(self.get_rlp_signing_prefix() + eth_rlp.encode(self.to_list(signing=True)))

    def rlp(self) -> Bytes:
        """Return the serialized object."""
        return Bytes(self.get_rlp_prefix() + eth_rlp.encode(self.to_list(signing=False)))


class SignableRLPSerializable(RLPSerializable):
    """Class that adds RLP serialization to another class with signing support."""

    signable: ClassVar[bool] = True

    def sign(self):
        """Sign the current object for further serialization."""
        raise NotImplementedError(f'Object "{self.__class__.__name__}" needs to implement `sign`.')
