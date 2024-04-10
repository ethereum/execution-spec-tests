"""
EOF v1 specs
https://github.com/ipsilon/eof/blob/main/spec/eof.md
"""

from typing import List


class SupportBytes(bytes):
    _size: int

    def __new__(cls, value, bytes_size: int):
        instance = super().__new__(cls, [value])
        instance._size = bytes_size * 2
        return instance

    def __str__(self):
        # Convert each byte to its hexadecimal representation
        out = " ".join(f"{byte:02X}" for byte in self)
        out = f"{'0' * (self._size - len(out))}{out}" if len(out) < self._size else out
        return out


class SupportBytesDescriptor:
    """
    Required to be able to write _magic = 0xEF directly
    """

    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if isinstance(value, int):
            value = SupportBytes(value, self.size)
        elif not isinstance(value, SupportBytes):
            raise TypeError(f"Value for {self.name} must be an int or SupportBytes instance.")
        instance.__dict__[self.name] = value


class TypeSection:
    _inputs: SupportBytes
    _outputs: SupportBytes
    _max_stack_height: SupportBytes


class Header:
    _magic = SupportBytesDescriptor("_magic", 1)
    _version = SupportBytesDescriptor("_version", 2)

    _kind_types: SupportBytes
    _types_size: SupportBytes
    _kind_code: SupportBytes
    _num_code_sections: SupportBytes

    _code_size: List[SupportBytes]
    # [
    _kind_container: SupportBytes
    _num_container_sections: SupportBytes
    _container_size: List[SupportBytes]
    # ]

    _kind_data: SupportBytes
    _data_size: SupportBytes
    _terminator: SupportBytes

    def __init__(self):
        self._magic = 0xEF
        self._version = 0x01


class Body:
    _types_section: List[TypeSection]
    _code_section: List[SupportBytes]
    _container_section: List[SupportBytes]
    _data_section: SupportBytes


class EOFCode:
    _header: Header
    _body: Body

    def __init__(self):
        self._header = Header()
        self._body = Body()

    def __str__(self):
        # Print the bytes as string
        out = f"{self._header._magic}{self._header._version}"
        return out


def main():
    code = EOFCode()
    print(f"Hello: {code}")


main()
