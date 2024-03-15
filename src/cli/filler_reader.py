"""
Simple CLI tool that reads filler files in the `ethereum/tests` format.
"""

import argparse
import json
from glob import glob
from pathlib import Path
from typing import Dict, List, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated


def check_address(s: str | int) -> bytes:
    """
    Check if the given string is a valid address.
    """
    if isinstance(s, int):
        return s.to_bytes(20, "big")
    assert isinstance(s, str)
    if s.startswith("0x"):
        s = s[2:]
    b = bytes.fromhex(s)
    if len(b) < 20:
        b = b.rjust(20, b"\x00")
    return b


Address = Annotated[bytes, BeforeValidator(check_address)]


def check_hex_number(i: int | str) -> int:
    """
    Check if the given string is a valid hex number.
    """
    if isinstance(i, int):
        return i
    if i.startswith("0x:bigint "):
        i = i[10:]
    return int(i, 16)


HexNumber = Annotated[int, BeforeValidator(check_hex_number)]


def check_hash(s: str | int) -> bytes:
    """
    Check if the given string is a valid hash.
    """
    if isinstance(s, int):
        return s.to_bytes(32, "big")
    if s.startswith("0x"):
        s = s[2:]
    b = bytes.fromhex(s)
    assert len(b) == 32
    return b


Hash = Annotated[bytes, BeforeValidator(check_hash)]


def check_code(input: str | int) -> str:
    """
    Check if the given string is a valid code.
    """
    if isinstance(input, int):
        return hex(input)
    return input


Code = Annotated[str, BeforeValidator(check_code)]

CAMEL_CASE_CONFIG = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    from_attributes=True,
    extra="forbid",
)


class Environment(BaseModel):
    """
    Class that represents an environment filler.
    """

    current_coinbase: Address
    current_difficulty: HexNumber | None = Field(None)
    current_gas_limit: HexNumber
    current_number: HexNumber
    current_timestamp: HexNumber
    current_base_fee: HexNumber | None = Field(None)
    current_random: Hash | None = Field(None)
    current_excess_blob_gas: HexNumber | None = Field(None)

    model_config = CAMEL_CASE_CONFIG


class Info(BaseModel):
    """
    Class that represents an info filler.
    """

    comment: str


class RemovedAccount(BaseModel):
    """
    Class that represents an empty account filler.
    """

    should_not_exist: bool = Field(..., alias="shouldnotexist")

    model_config = CAMEL_CASE_CONFIG


class Account(BaseModel):
    """
    Class that represents an account filler.
    """

    balance: HexNumber | None = Field(None)
    code: Code | None = Field(None)
    nonce: HexNumber | None = Field(None)
    storage: Dict[HexNumber, Literal["ANY"] | HexNumber] | None = Field(None)

    model_config = CAMEL_CASE_CONFIG


class AccessList(BaseModel):
    """
    Class that represents an access list.
    """

    address: Address
    storage_keys: List[HexNumber]

    model_config = CAMEL_CASE_CONFIG


class Data(BaseModel):
    """
    Class that represents the data portion of the test.
    """

    data: str
    access_list: List[AccessList]

    model_config = CAMEL_CASE_CONFIG


class Transaction(BaseModel):
    """
    Class that represents a transaction filler.
    """

    data: List[str | Data]
    gas_limit: List[HexNumber]
    gas_price: HexNumber | None = Field(None)
    max_fee_per_gas: HexNumber | None = Field(None)
    max_priority_fee_per_gas: HexNumber | None = Field(None)
    nonce: HexNumber
    to: Address
    value: List[HexNumber]
    secret_key: Hash

    model_config = CAMEL_CASE_CONFIG


class Indexes(BaseModel):
    """
    Class that represents an index filler.
    """

    data: int | str | List[int | str] = Field(-1)
    gas: int | str | List[int | str] = Field(-1)
    value: int | str | List[int | str] = Field(-1)

    model_config = CAMEL_CASE_CONFIG


class Expect(BaseModel):
    """
    Class that represents an expect filler.
    """

    indexes: Indexes = Field(Indexes(data=-1, gas=-1, value=-1))
    network: List[str]
    result: Dict[Address, RemovedAccount | Account]
    expect_exception: Dict[str, str] | None = Field(None)

    model_config = CAMEL_CASE_CONFIG


class StateTest(BaseModel):
    """
    Class that represents a state test filler.
    """

    env: Environment
    info: Info | None = Field(None, alias="_info")
    pre: Dict[Address, Account]
    transaction: Transaction
    expect: List[Expect]
    exceptions: List[str] | None = Field(None)
    solidity: str | None = Field(None)
    verify: Dict | None = Field(None)
    verify_bc: Dict | None = Field(None, alias="verifyBC")

    model_config = CAMEL_CASE_CONFIG


def remove_comments(d: dict) -> dict:
    """
    Remove comments from a dictionary.
    """
    result = {}
    for k, v in d.items():
        if isinstance(k, str) and k.startswith("//"):
            continue
        if isinstance(v, dict):
            v = remove_comments(v)
        elif isinstance(v, list):
            v = [remove_comments(i) if isinstance(i, dict) else i for i in v]
        result[k] = v
    return result


class StateFiller(BaseModel):
    """
    Class that represents a state test filler.
    """

    tests: Dict[str, StateTest]

    @classmethod
    def from_json(cls, path: Path) -> None:
        """
        Read the state filler from a JSON file.
        """
        with open(path, "r") as f:
            o = json.load(f)
            StateFiller(tests=remove_comments(o))

    @classmethod
    def from_yml(cls, path: Path) -> None:
        """
        Read the state filler from a YML file.
        """
        with open(path, "r") as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            StateFiller(tests=remove_comments(o))


def main() -> None:
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="Filler parser.")

    parser.add_argument(
        "mode", type=str, help="The type of filler we are trying to parse: blockchain/state."
    )
    parser.add_argument("folder_path", type=Path, help="The path to the JSON/YML filler directory")

    args = parser.parse_args()

    files = glob(str(args.folder_path / "**" / "*.json")) + glob(
        str(args.folder_path / "**" / "*.yml")
    )

    filler_cls = StateFiller
    if args.mode == "blockchain":
        raise NotImplementedError("Blockchain filler not implemented yet.")

    for file in files:
        print(file)
        if file.endswith(".json"):
            filler_cls.from_json(Path(file))
        elif file.endswith(".yml"):
            filler_cls.from_yml(Path(file))
