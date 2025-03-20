"""State test JSON loader."""

from typing import Callable, ClassVar, Dict, List, Literal

import pytest
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from ethereum_test_base_types import Address
from ethereum_test_forks import Fork, Frontier, Homestead
from ethereum_test_types import Alloc, Environment, Transaction

from .base_json import BaseJSONTest
from .state import StateTestFiller


def check_address(s: str | int) -> bytes:
    """Check if the given string is a valid address."""
    if isinstance(s, int):
        return s.to_bytes(20, "big")
    assert isinstance(s, str)
    if s.startswith("0x"):
        s = s[2:]
    b = bytes.fromhex(s)
    if len(b) < 20:
        b = b.rjust(20, b"\x00")
    return b


FillerAddress = Annotated[bytes, BeforeValidator(check_address)]


def check_hex_number(i: int | str) -> int:
    """Check if the given string is a valid hex number."""
    if isinstance(i, int):
        return i
    if i.startswith("0x:bigint "):
        i = i[10:]
    return int(i, 16)


HexNumber = Annotated[int, BeforeValidator(check_hex_number)]


def check_hash(s: str | int) -> bytes:
    """Check if the given string is a valid hash."""
    if isinstance(s, int):
        return s.to_bytes(32, "big")
    if s.startswith("0x"):
        s = s[2:]
    b = bytes.fromhex(s)
    assert len(b) == 32
    return b


Hash = Annotated[bytes, BeforeValidator(check_hash)]


def check_code(input_code: str | int) -> str:
    """Check if the given string is a valid code."""
    if isinstance(input_code, int):
        return hex(input_code)
    return input_code


Code = Annotated[str, BeforeValidator(check_code)]

CAMEL_CASE_CONFIG = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    from_attributes=True,
    extra="forbid",
)


class FillerEnvironment(BaseModel):
    """Class that represents an environment filler."""

    current_coinbase: FillerAddress
    current_difficulty: HexNumber | None = Field(None)
    current_gas_limit: HexNumber
    current_number: HexNumber
    current_timestamp: HexNumber
    current_base_fee: HexNumber | None = Field(None)
    current_random: Hash | None = Field(None)
    current_excess_blob_gas: HexNumber | None = Field(None)

    model_config = CAMEL_CASE_CONFIG


class Info(BaseModel):
    """Class that represents an info filler."""

    comment: str


class RemovedAccount(BaseModel):
    """Class that represents an empty account filler."""

    should_not_exist: bool = Field(..., alias="shouldnotexist")

    model_config = CAMEL_CASE_CONFIG


class Account(BaseModel):
    """Class that represents an account filler."""

    balance: HexNumber | None = Field(None)
    code: Code | None = Field(None)
    nonce: HexNumber | None = Field(None)
    storage: Dict[HexNumber, Literal["ANY"] | HexNumber] | None = Field(None)

    model_config = CAMEL_CASE_CONFIG


class AccessList(BaseModel):
    """Class that represents an access list."""

    address: FillerAddress
    storage_keys: List[HexNumber]

    model_config = CAMEL_CASE_CONFIG


class Data(BaseModel):
    """Class that represents the data portion of the test."""

    data: str
    access_list: List[AccessList]

    model_config = CAMEL_CASE_CONFIG


class FillerTransaction(BaseModel):
    """Class that represents a transaction filler."""

    data: List[str | Data]
    gas_limit: List[HexNumber]
    gas_price: HexNumber | None = Field(None)
    max_fee_per_gas: HexNumber | None = Field(None)
    max_priority_fee_per_gas: HexNumber | None = Field(None)
    nonce: HexNumber
    to: FillerAddress
    value: List[HexNumber]
    secret_key: Hash

    model_config = CAMEL_CASE_CONFIG


class Indexes(BaseModel):
    """Class that represents an index filler."""

    data: int | str | List[int | str] = Field(-1)
    gas: int | str | List[int | str] = Field(-1)
    value: int | str | List[int | str] = Field(-1)

    model_config = CAMEL_CASE_CONFIG


class Expect(BaseModel):
    """Class that represents an expect filler."""

    indexes: Indexes = Field(Indexes(data=-1, gas=-1, value=-1))
    network: List[str]
    result: Dict[FillerAddress, RemovedAccount | Account]
    expect_exception: Dict[str, str] | None = Field(None)

    model_config = CAMEL_CASE_CONFIG


class StateFiller(BaseJSONTest):
    """Class that represents a state test filler."""

    env: FillerEnvironment
    info: Info | None = Field(None, alias="_info")
    pre: Dict[FillerAddress, Account]
    transaction: FillerTransaction
    expect: List[Expect]
    exceptions: List[str] | None = Field(None)
    solidity: str | None = Field(None)
    verify: Dict | None = Field(None)
    verify_bc: Dict | None = Field(None, alias="verifyBC")

    format_name: ClassVar[str] = "state_filler"

    model_config = CAMEL_CASE_CONFIG

    def get_valid_from_fork(self) -> Fork | None:
        """Get the first fork this JSON filler supports."""
        return Homestead

    def get_valid_until_fork(self) -> Fork | None:
        """Get the last fork this JSON filler supports."""
        return None

    def fill_function(self) -> Callable:
        """Return the test function that can be used to fill the test."""

        @pytest.mark.parametrize("n", [1])
        @pytest.mark.valid_from("Homestead")
        def test_state_filler(
            state_test: StateTestFiller,
            fork: Fork,
            pre: Alloc,
            n: int,
        ):
            """
            Test the DUP1-DUP16 opcodes.

            Note: Test case ported from [ethereum/tests](https://github.com/ethereum/tests)
                Test ported from [ethereum/tests/GeneralStateTests/VMTests/vmTests/dup.json](https://github.com/ethereum/tests/blob/develop/GeneralStateTests/VMTests/vmTests/dup.json) by Ori Pomerantz.
            """  # noqa: E501
            env = Environment()
            sender = pre.fund_eoa()
            tx = Transaction(
                ty=0x0,
                nonce=0,
                to=Address(0x1000),
                gas_limit=500000,
                protected=False if fork in [Frontier, Homestead] else True,
                data="",
                sender=sender,
            )
            state_test(env=env, pre=pre, post={}, tx=tx)

        return test_state_filler
