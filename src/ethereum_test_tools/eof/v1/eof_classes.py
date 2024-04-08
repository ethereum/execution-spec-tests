"""
EOF v1 specs
https://github.com/ipsilon/eof/blob/main/spec/eof.md
"""

from typing import Generic, TypeVar, List

class Byte:
    def __init__(self, value=0):
        self._value = None  # Initialize _value; will be set properly via the property setter
        self.value = value  # Use the property setter to initialize value

    @property
    def value(self):
        """Property getter for the byte value."""
        return self._value

    @value.setter
    def value(self, new_value):
        """Property setter for the byte value, with validation to ensure it fits in a byte."""
        if not isinstance(new_value, int):
            raise TypeError("Value must be an integer")
        if not 0 <= new_value <= 255:
            raise ValueError("Value must be between 0 and 255 inclusive")
        self._value = new_value

    def __repr__(self):
        """String representation for debugging."""
        return f"Byte({self.value})"

class Bytes2:
    def __init__(self, value=0):
        self._value = None  # Initialize _value; will be set properly via the property setter
        self.value = value  # Use the property setter to initialize value

    @property
    def value(self):
        """Property getter for the two-byte value."""
        return self._value

    @value.setter
    def value(self, new_value):
        """Property setter for the two-byte value, with validation to ensure it fits in two bytes."""
        if not isinstance(new_value, int):
            raise TypeError("Value must be an integer")
        if not 0 <= new_value <= 65535:
            raise ValueError("Value must be between 0 and 65535 inclusive")
        self._value = new_value

    def __repr__(self):
        """String representation for debugging."""
        return f"TwoBytes({self.value})"

# Define a type variable; this will allow our class to be generic.
T = TypeVar('T')

class NonEmptyList(List[T], Generic[T]):
    def __init__(self, initial_elements: List[T]):
        if not initial_elements:
            raise ValueError("Initial list must contain at least one element.")
        super().__init__(initial_elements)

    def pop(self, index=-1) -> T:
        if len(self) <= 1:
            raise ValueError("Cannot pop the last element from a NonEmptyList.")
        return super().pop(index)

    def remove(self, value: T) -> None:
        if len(self) <= 1:
            raise ValueError("Cannot remove the last element from a NonEmptyList.")
        super().remove(value)

    def clear(self) -> None:
        raise ValueError("Cannot clear a NonEmptyList.")

    def __delitem__(self, key) -> None:
        if len(self) <= 1:
            raise ValueError("Cannot delete the last element from a NonEmptyList.")
        super().__delitem__(key)

    
class TypeSection:
    inputs: Byte
    outputs: Byte
    max_stack_height: Bytes2
    
class Header:
    magic: Bytes2
    version: Byte
    kind_types: Byte
    types_size: Bytes2
    kind_code: Byte
    num_code_sections: Bytes2

    code_size: NonEmptyList[Bytes2]
    # [
    kind_container: Byte
    num_container_sections: Bytes2
    container_size: NonEmptyList[Bytes2]
    # ]

    kind_data: Byte
    data_size: Bytes2
    terminator: Byte

class Body:
    types_section: NonEmptyList[TypeSection]
    code_section: NonEmptyList[bytes]
    container_section: List[bytes]
    data_section: bytes

class container:
    header: Header
    body: Body
