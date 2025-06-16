"""Common field types from ethereum/tests."""

import re
import subprocess
import tempfile
from functools import cached_property
from typing import Any, List, Union

from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector
from pydantic import BaseModel, Field, field_validator
from pydantic.functional_validators import BeforeValidator
from pydantic_core import core_schema
from typing_extensions import Annotated

from ethereum_test_base_types import Address, Hash, HexNumber

from .compile_yul import compile_yul


def parse_hex_number(i: str | int) -> int:
    """Check if the given string is a valid hex number."""
    if i == "" or i == "0x":
        return 0
    if isinstance(i, int):
        return i
    if i.startswith("0x:bigint "):
        i = i[10:]
        return int(i, 16)
    if i.startswith("0x") or any(char in "abcdef" for char in i.lower()):
        return int(i, 16)
    return int(i, 10)


def parse_value_or_address_tag(value: Any) -> Union[HexNumber, str]:
    """Parse either a hex number or an address tag for storage values."""
    if not isinstance(value, str):
        # Non-string values should be converted to HexNumber normally
        return HexNumber(parse_hex_number(value))

    # Check if it matches address tag pattern: <type:name:0xaddress> or <type:0xaddress>
    tag_pattern = r"^<(eoa|contract):.+>$"
    if re.match(tag_pattern, value.strip()):
        # Return the tag string as-is for later resolution
        return value.strip()
    else:
        # Parse as hex number
        return HexNumber(parse_hex_number(value))


def parse_args_from_string_into_array(stream: str, pos: int, delim: str = " "):
    """Parse YUL options into array."""
    args = []
    arg = ""
    # Loop until end of stream or until encountering newline or '{'
    while pos < len(stream) and stream[pos] not in ("\n", "{"):
        if stream[pos] == delim:
            args.append(arg)
            arg = ""
        else:
            arg += stream[pos]
        pos += 1
    if arg:
        args.append(arg)
    return args, pos


class CodeInFillerSource:
    """Not compiled code source in test filler."""

    code_label: str | None
    code_raw: Any

    def __init__(self, code: Any, label: str | None = None):
        """Instantiate."""
        self.code_label = label
        self.code_raw = code

    @cached_property
    def compiled(self) -> bytes:
        """Compile the code from source to bytes."""
        if isinstance(self.code_raw, int):
            # Users pass code as int (very bad)
            hex_str = format(self.code_raw, "02x")
            return bytes.fromhex(hex_str)

        if not isinstance(self.code_raw, str):
            raise ValueError(f"parse_code(code: str) code is not string: {self.code_raw}")
        if len(self.code_raw) == 0:
            return b""

        compiled_code = ""

        raw_marker = ":raw 0x"
        raw_index = self.code_raw.find(raw_marker)
        abi_marker = ":abi"
        abi_index = self.code_raw.find(abi_marker)
        yul_marker = ":yul"
        yul_index = self.code_raw.find(yul_marker)

        # Parse :raw
        if raw_index != -1:
            compiled_code = self.code_raw[raw_index + len(raw_marker) :]

        # Parse :yul
        elif yul_index != -1:
            option_start = yul_index + len(yul_marker)
            options: list[str] = []
            native_yul_options: str = ""

            if self.code_raw[option_start:].lstrip().startswith("{"):
                # No yul options, proceed to code parsing
                source_start = option_start
            else:
                opt, source_start = parse_args_from_string_into_array(
                    self.code_raw, option_start + 1
                )
                for arg in opt:
                    if arg == "object" or arg == '"C"':
                        native_yul_options += arg + " "
                    else:
                        options.append(arg)

            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
                tmp.write(native_yul_options + self.code_raw[source_start:])
                tmp_path = tmp.name
            compiled_code = compile_yul(
                source_file=tmp_path,
                evm_version=options[0] if len(options) >= 1 else None,
                optimize=options[1] if len(options) >= 2 else None,
            )[2:]

        # Parse :abi
        elif abi_index != -1:
            abi_encoding = self.code_raw[abi_index + len(abi_marker) + 1 :]
            tokens = abi_encoding.strip().split()
            abi = tokens[0]
            function_signature = function_signature_to_4byte_selector(abi)
            parameter_str = re.sub(r"^\w+", "", abi).strip()

            parameter_types = parameter_str.strip("()").split(",")
            if len(tokens) > 1:
                function_parameters = encode(
                    [parameter_str],
                    [
                        [
                            int(t.lower(), 0) & ((1 << 256) - 1)  # treat big ints as 256bits
                            if parameter_types[t_index] == "uint"
                            else int(t.lower(), 0) > 0  # treat positive values as True
                            if parameter_types[t_index] == "bool"
                            else False and ValueError("unhandled parameter_types")
                            for t_index, t in enumerate(tokens[1:])
                        ]
                    ],
                )
                return function_signature + function_parameters
            return function_signature

        # Parse plain code 0x
        elif self.code_raw.lstrip().startswith("0x"):
            compiled_code = self.code_raw[2:].lower()

        # Parse lllc code
        elif self.code_raw.lstrip().startswith("{") or self.code_raw.lstrip().startswith("(asm"):
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
                tmp.write(self.code_raw)
                tmp_path = tmp.name

            # - using lllc
            result = subprocess.run(["lllc", tmp_path], capture_output=True, text=True)

            # - using docker:
            #   If the running machine does not have lllc installed, we can use docker to run lllc,
            #   but we need to start a container first, and the process is generally slower.
            # from .docker import get_lllc_container_id
            # result = subprocess.run(
            #     ["docker", "exec", get_lllc_container_id(), "lllc", tmp_path[5:]],
            #     capture_output=True,
            #     text=True,
            # )
            compiled_code = "".join(result.stdout.splitlines())
        else:
            raise Exception(f'Error parsing code: "{self.code_raw}"')

        try:
            return bytes.fromhex(compiled_code)
        except ValueError as e:
            raise Exception(f'Error parsing compile code: "{self.code_raw}"') from e


def parse_code_label(code) -> CodeInFillerSource:
    """Parse label from code."""
    label_marker = ":label"
    label_index = code.find(label_marker)

    # Parse :label into code options
    label = None
    if label_index != -1:
        space_index = code.find(" ", label_index + len(label_marker) + 1)
        if space_index == -1:
            label = code[label_index + len(label_marker) + 1 :]
        else:
            label = code[label_index + len(label_marker) + 1 : space_index]
    return CodeInFillerSource(code, label)


class AddressTag:
    """Represents an address tag like <eoa:sender> or <contract:token>."""

    def __init__(self, tag_type: str, tag_name: str, original_string: str):
        """Initialize address tag."""
        self.tag_type = tag_type  # "eoa" or "contract"
        self.tag_name = tag_name  # e.g., "sender", "token"
        self.original_string = original_string

    def __str__(self) -> str:
        """Return original tag string."""
        return self.original_string

    def __repr__(self) -> str:
        """Return debug representation."""
        return f"AddressTag(type={self.tag_type}, name={self.tag_name})"

    def __eq__(self, other) -> bool:
        """Check equality based on original string."""
        if isinstance(other, AddressTag):
            return self.original_string == other.original_string
        return False

    def __hash__(self) -> int:
        """Hash based on original string for use as dict key."""
        return hash(self.original_string)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> core_schema.CoreSchema:
        """Pydantic core schema for AddressTag."""
        return core_schema.str_schema()


def parse_address_or_tag(value: Any) -> Union[Address, AddressTag]:
    """Parse either a regular address or an address tag."""
    if not isinstance(value, str):
        # Non-string values should be converted to Address normally
        return Address(value, left_padding=True)

    # Check if it matches tag pattern:
    # - <eoa:0x...> or <contract:0x...>
    # - <eoa:name:0x...> or <contract:name:0x...>
    tag_pattern = r"^<(eoa|contract):(.+)>$"
    match = re.match(tag_pattern, value.strip())

    if match:
        tag_type = match.group(1)
        # The tag_name is everything after the type and colon
        # Could be "0x1234..." or "sender:0x1234..."
        tag_name = match.group(2)

        return AddressTag(tag_type, tag_name, value.strip())
    else:
        # Regular address string
        return Address(value, left_padding=True)


def parse_address_or_tag_for_access_list(value: Any) -> Union[Address, str]:
    """
    Parse either a regular address or an address tag, keeping tags as strings for later
    resolution.
    """
    if not isinstance(value, str):
        # Non-string values should be converted to Address normally
        return Address(value, left_padding=True)

    # Check if it matches a tag pattern
    tag_pattern = r"^<(eoa|contract):.+>$"
    if re.match(tag_pattern, value.strip()):
        # Return the tag string as-is for later resolution
        return value.strip()
    else:
        # Regular address string
        return Address(value, left_padding=True)


def validate_address_or_tag_string(value: Union[Address, str]) -> Union[Address, str]:
    """Validate and normalize address or tag as string for later resolution."""
    if isinstance(value, str):
        return value.strip()
    else:
        return Address(value, left_padding=True)


def parse_hash32_or_sender_key_tag(value: Any) -> Union[Hash, str]:
    """Parse either a regular hash or a sender key tag for later resolution."""
    if isinstance(value, str) and value.strip().startswith("<sender:key:"):
        return value.strip()
    return Hash(value, left_padding=True)


AddressInFiller = Annotated[Address, BeforeValidator(lambda a: Address(a, left_padding=True))]
AddressOrTagInFiller = Annotated[
    Union[Address, str], BeforeValidator(validate_address_or_tag_string)
]
ValueOrTagInFiller = Annotated[Union[HexNumber, str], BeforeValidator(parse_value_or_address_tag)]
Hash32OrTagInFiller = Annotated[Union[Hash, str], BeforeValidator(parse_hash32_or_sender_key_tag)]
ValueInFiller = Annotated[HexNumber, BeforeValidator(parse_hex_number)]
CodeInFiller = Annotated[CodeInFillerSource, BeforeValidator(parse_code_label)]
Hash32InFiller = Annotated[Hash, BeforeValidator(lambda h: Hash(h, left_padding=True))]


class AccessListInFiller(BaseModel):
    """Access List for transactions in fillers that can contain address tags."""

    address: Union[Address, str]  # Can be an address or a tag string
    storage_keys: List[Hash] = Field([], alias="storageKeys")

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, v):
        """Allow both addresses and tags."""
        return parse_address_or_tag_for_access_list(v)

    class Config:
        """Model config."""

        populate_by_name = True
