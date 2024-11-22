"""
Base types for Pydantic json test fixtures
"""

import re
from typing import Generic, TypeVar

from pydantic import RootModel, model_validator

T = TypeVar("T", bound="FixedHash")


class FixedHash(RootModel[str], Generic[T]):
    """Base class for fixed-length hashes."""

    _length_in_bytes: int

    @model_validator(mode="after")
    def validate_hex_hash(self):
        """
        Validate that the field is a 0x-prefixed hash of specified byte length.
        """
        expected_length = 2 + 2 * self._length_in_bytes  # 2 for '0x' + 2 hex chars per byte
        if not self.root.startswith("0x"):
            raise ValueError("The hash must start with '0x'.")
        if len(self.root) != expected_length:
            raise ValueError(
                f"The hash must be {expected_length} characters long "
                f"(2 for '0x' and {2 * self._length_in_bytes} hex characters)."
            )
        if not re.fullmatch(rf"0x[a-fA-F0-9]{{{2 * self._length_in_bytes}}}", self.root):
            raise ValueError(
                f"The hash must be a valid hexadecimal string of "
                f"{2 * self._length_in_bytes} characters after '0x'."
            )


class FixedHash32(FixedHash):
    """FixedHash32 type (32 bytes)"""

    _length_in_bytes = 32


class FixedHash20(FixedHash):
    """FixedHash20 type (20 bytes)"""

    _length_in_bytes = 20


class FixedHash8(FixedHash):
    """FixedHash8 type (8 bytes)"""

    _length_in_bytes = 8


class FixedHash256(FixedHash):
    """FixedHash256 type (256 bytes)"""

    _length_in_bytes = 256


class PrefixedEvenHex(RootModel[str]):
    """Class to validate a hexadecimal integer encoding in test files."""

    def __eq__(self, other):
        """
        For python str comparison
        """
        if isinstance(other, str):
            return self.root == other
        return NotImplemented

    @model_validator(mode="after")
    def validate_hex_integer(self):
        """
        Validate that the field is a hexadecimal integer with specific rules:
        - Must start with '0x'.
        - Must be even in length after '0x'.
        - Cannot be '0x0', '0x0000', etc. (minimum is '0x00').
        """
        # Ensure it starts with '0x'
        if not self.root.startswith("0x"):
            raise ValueError("The value must start with '0x'.")

        # Extract the hex portion (after '0x')
        hex_part = self.root[2:]

        # Ensure the length of the hex part is even
        if len(hex_part) % 2 != 0:
            raise ValueError(
                "The hexadecimal value must have an even number of characters after '0x'."
            )

        # Special rule: Only '0x00' is allowed; disallow '0x0000', '0x0001', etc.
        if hex_part.startswith("00") and hex_part != "00":
            raise ValueError("Leading zeros are not allowed except for '0x00'.")

        # Ensure it's a valid hexadecimal string
        if not re.fullmatch(r"[a-fA-F0-9]+", hex_part):
            raise ValueError("The value must be a valid hexadecimal string.")

        return self


class DataBytes(RootModel[str]):
    """Class to validate DataBytes."""

    @model_validator(mode="after")
    def validate_data_bytes(self):
        """
        Validate that the field follows the rules for DataBytes:
        - Must start with '0x'.
        - Can be empty (just '0x').
        - Must be even in length after '0x'.
        - Allows prefixed '00' values (e.g., '0x00000001').
        - Must be a valid hexadecimal string.
        """
        # Ensure it starts with '0x'
        if not self.root.startswith("0x"):
            raise ValueError("The value must start with '0x'.")

        # Extract the hex portion (after '0x')
        hex_part = self.root[2:]

        # Allow empty '0x'
        if len(hex_part) == 0:
            return self

        # Ensure the length of the hex part is even
        if len(hex_part) % 2 != 0:
            raise ValueError(
                "The hexadecimal value must have an even number of characters after '0x'."
            )

        # Ensure it's a valid hexadecimal string
        if not re.fullmatch(r"[a-fA-F0-9]*", hex_part):  # `*` allows empty hex_part for '0x'
            raise ValueError("The value must be a valid hexadecimal string.")

        return self
