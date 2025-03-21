"""Expect section structure of ethereum/tests fillers."""

from enum import Enum
from typing import Dict, List, Literal

from pydantic import BaseModel, BeforeValidator, Field, ValidationInfo, field_validator
from typing_extensions import Annotated

from ethereum_test_forks import Fork, get_forks

from .common import AddressInFiller, CodeInFiller, ValueInFiller


class Indexes(BaseModel):
    """Class that represents an index filler."""

    data: int | List[int] = Field(-1)
    gas: int | List[int] = Field(-1)
    value: int | List[int] = Field(-1)


class AccountInExpectSection(BaseModel):
    """Class that represents an account in expect section filler."""

    balance: ValueInFiller | None = Field(None)
    code: CodeInFiller | None = Field(None)
    nonce: ValueInFiller | None = Field(None)
    storage: Dict[ValueInFiller, ValueInFiller | Literal["ANY"]] | None = Field(None)
    expected_to_not_exist: str | None = Field(None, alias="shouldnotexist")


class CMP(Enum):
    """Comparison action."""

    GT = 1
    LT = 2
    LE = 3
    GE = 4
    EQ = 5


class ExpectSectionInStateTestFiller(BaseModel):
    """Expect section in state test filler."""

    indexes: Indexes = Field(default_factory=Indexes)
    network: List[str]
    result: Dict[AddressInFiller, AccountInExpectSection]

    @field_validator("network", mode="before")
    @classmethod
    def parse_networks(cls, network: List[str], info: ValidationInfo) -> List[str]:
        """Parse networks into array of forks."""
        parsed_forks: List[str] = []
        all_forks_by_name = [fork.name() for fork in get_forks()]
        for net in network:
            action: CMP = CMP.EQ
            fork: str = net
            if net[:1] == "<":
                action = CMP.LT
                fork = net[1:]
            if net[:1] == ">":
                action = CMP.GT
                fork = net[1:]
            if net[:2] == "<=":
                action = CMP.LE
                fork = net[2:]
            if net[:2] == ">=":
                action = CMP.GE
                fork = net[2:]

            if action == CMP.EQ:
                parsed_forks.append(net)
                continue

            try:
                idx = all_forks_by_name.index(fork)
            except ValueError:
                raise ValueError(f"Unsupported fork: {fork}") from Exception

            if action == CMP.GE:
                parsed_forks = all_forks_by_name[idx:]
            elif action == CMP.GT:
                parsed_forks = all_forks_by_name[idx + 1 :]
            elif action == CMP.LE:
                parsed_forks = all_forks_by_name[: idx + 1]
            elif action == CMP.LT:
                parsed_forks = all_forks_by_name[:idx]

        return parsed_forks

    def has_index(self, d: int, g: int, v: int) -> bool:
        """Check if there is index set in indexes."""
        d_match: bool = False
        g_match: bool = False
        v_match: bool = False
        if isinstance(self.indexes.data, int):
            d_match = True if self.indexes.data == -1 or self.indexes.data == d else False
        if isinstance(self.indexes.gas, int):
            g_match = True if self.indexes.gas == -1 or self.indexes.gas == g else False
        if isinstance(self.indexes.value, int):
            v_match = True if self.indexes.value == -1 or self.indexes.value == v else False
        return d_match and g_match and v_match
