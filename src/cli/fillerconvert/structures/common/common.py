"""Common field types from ethereum/tests."""

import re
import subprocess
import tempfile

from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from ethereum_test_base_types import Address, Bytes, Hash, HexNumber


def parse_hex_number(i: str | int) -> int:
    """Check if the given string is a valid hex number."""
    if isinstance(i, int):
        return i
    if i.startswith("0x:bigint "):
        i = i[10:]
    if i.startswith("0x"):
        return int(i, 16)
    return int(i, 10)


def parse_code(code: str) -> bytes:
    """Check if the given string is a valid code."""
    compiled_code = ""
    if not isinstance(code, str):
        raise ValueError(f"Invalid code: {code}")
    if code.lstrip().startswith(":abi"):
        tokens = code.strip().split()
        if len(tokens) < 2:
            raise ValueError("Error parsing ABI code: " + code)
        abi = tokens[1]
        function_signature = function_signature_to_4byte_selector(abi)
        parameter_str = re.sub(r"^\w+", "", abi).strip()
        function_parameters = encode([parameter_str], [[int(t) for t in tokens[2:]]])
        return function_signature + function_parameters
    elif code.lstrip().startswith("{"):
        binary_path = "lllc"
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        result = subprocess.run([binary_path, tmp_path], capture_output=True, text=True)
        compiled_code = "".join(result.stdout.splitlines())
    elif code.lstrip().startswith(":raw 0x"):
        compiled_code = code.lstrip()[7:]
    if code.lstrip().startswith("0x"):
        compiled_code = code[2:]

    try:
        return bytes.fromhex(compiled_code)
    except ValueError as e:
        raise Exception(f'Error parsing code: "{code}"') from e


AddressInFiller = Annotated[Address, BeforeValidator(lambda a: Address(a, left_padding=True))]
ValueInFiller = Annotated[HexNumber, BeforeValidator(parse_hex_number)]
CodeInFiller = Annotated[Bytes, BeforeValidator(parse_code)]
Hash32InFiller = Annotated[Hash, BeforeValidator(lambda h: Hash(h, left_padding=True))]
