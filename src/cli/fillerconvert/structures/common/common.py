"""Common field types from ethereum/tests."""

import subprocess
import tempfile

from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated


def parse_address(s: str) -> str:
    """Check if the given string is a valid address."""
    if s.startswith("0x"):
        s = s[2:]
    b = bytes.fromhex(s)
    if len(b) < 20:
        b = b.rjust(20, b"\x00")
    return "0x" + b.hex()


def parse_hex_number(i: str) -> str:
    """Check if the given string is a valid hex number."""
    if i.startswith("0x:bigint "):
        i = i[10:]
    if i.startswith("0x"):
        return str(hex(int(i, 16)))
    return str(hex(int(i, 10)))


def parse_code(code: str) -> str:
    """Check if the given string is a valid code."""
    compiled_code = ""
    if code.lstrip().startswith("{"):
        binary_path = "lllc"
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        result = subprocess.run([binary_path, tmp_path], capture_output=True, text=True)
        compiled_code = "0x" + "".join(result.stdout.splitlines())
    if code.lstrip().startswith("0x"):
        compiled_code = code

    try:
        bytes.fromhex(compiled_code[2:])
    except ValueError:
        print(f"Parser failed to compile the code:  `{code}`, got: `{compiled_code}`")

    code = compiled_code
    return code


def parse_hash32(i: str) -> str:
    """Check if the given string is a valid hash32."""
    if i.startswith("0x"):
        i = i[2:]
    b = bytes.fromhex(i)
    assert len(b) == 32
    return "0x" + b.hex()


AddressInFiller = Annotated[str, BeforeValidator(parse_address)]
ValueInFiller = Annotated[str, BeforeValidator(parse_hex_number)]
CodeInFiller = Annotated[str, BeforeValidator(parse_code)]
Hash32InFiller = Annotated[str, BeforeValidator(parse_hash32)]
