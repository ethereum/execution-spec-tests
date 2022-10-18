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

    def assemble(self) -> bytes:
        """
        Assembles using `eas`.
        """
        return bytes()

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