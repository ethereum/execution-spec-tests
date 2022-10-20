"""
Code object that is an interface to different
assembler/compiler backends.
"""
from re import sub
from typing import Union


class Code(str):
    """
    Generic code object.
    """
    bytecode: bytes = None

    def __init__(self, bytecode: bytes):
        self.bytecode = bytecode

    def assemble(self) -> bytes:
        """
        Assembles using `eas`.
        """
        return self.bytecode
    
    def __add__(self, value: Union[str, bytes, "Code"]) -> "Code":
        return Code(code_to_bytes(self) + code_to_bytes(value))

def code_to_bytes(code: Union[str, bytes, Code, None]) -> bytes:
    """
    Converts multiple types into bytecode.
    """

    if code is None:
        return bytes()

    if isinstance(code, Code):
        return code.assemble()

    if type(code) is bytes:
        return code
    
    if type(code) is str:
        # We can have a hex representation of bytecode with spaces for
        # readability
        code = sub("\s+", "", code)
        if code.startswith("0x"):
            return bytes.fromhex(code[2:])
        return bytes.fromhex(code)
    
    raise Exception(
        "invalid type for `code`"
    )

def code_to_hex(code: Union[str, bytes, Code, None]) -> str:
    """
    Converts multiple types into a bytecode hex string.
    """

    if code is None:
        return "0x"

    if isinstance(code, Code):
        return "0x" + code.assemble().hex()

    if type(code) is bytes:
        return "0x" + code.hex()
    
    if type(code) is str:
        # We can have a hex representation of bytecode with spaces for
        # readability
        code = sub("\s+", "", code)
        if code.startswith("0x"):
            return code
        return "0x" + code
    
    raise Exception(
        "invalid type for `code`"
    )