"""Classes to manage tags in static state tests."""

import re
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Generic, Mapping, TypeVar

from pydantic import BaseModel, model_validator

from ethereum_test_base_types import Address, Bytes, Hash, HexNumber
from ethereum_test_types import EOA, compute_create2_address, compute_create_address

TagDict = Dict[str, Address | EOA]

T = TypeVar("T", bound=Address | Hash)


class Tag(BaseModel, Generic[T]):
    """Tag."""

    name: str
    type: ClassVar[str] = ""
    regex_pattern: ClassVar[re.Pattern] = re.compile(r"<\w+:(\w+)(:[^>]+)?")

    def __hash__(self) -> int:
        """Hash based on original string for use as dict key."""
        return hash(f"{self.__class__.__name__}:{self.name}")

    @model_validator(mode="before")
    @classmethod
    def validate_from_string(cls, data: Any) -> Any:
        """Validate the generic tag from string: <tag_kind:name:0x...>."""
        if isinstance(data, str):
            if m := cls.regex_pattern.match(data):
                name = m.group(1)
                return {"name": name}
        return data

    def resolve(self, tags: TagDict) -> T:
        """Resolve the tag."""
        raise NotImplementedError("Subclasses must implement this method")


class TagDependentData(ABC):
    """Data for resolving tags."""

    @abstractmethod
    def tag_dependencies(self) -> Mapping[str, Tag]:
        """Get tag dependencies."""
        pass


class AddressTag(Tag[Address]):
    """Address tag."""

    def resolve(self, tags: TagDict) -> Address:
        """Resolve the tag."""
        assert self.name in tags, f"Tag {self.name} not found in tags"
        return Address(tags[self.name])


class ContractTag(AddressTag):
    """Contract tag."""

    type: ClassVar[str] = "contract"
    regex_pattern: ClassVar[re.Pattern] = re.compile(r"<contract:(\w+)(:0x.+)?>")


class CreateTag(AddressTag):
    """Contract derived from a another contract via CREATE."""

    create_type: str
    nonce: HexNumber | None = None
    salt: HexNumber | None = None
    initcode: Bytes | None = None

    type: ClassVar[str] = "contract"
    regex_pattern: ClassVar[re.Pattern] = re.compile(r"<(create|create2):(\w+):(\w+):?(\w+)?>")

    @model_validator(mode="before")
    @classmethod
    def validate_from_string(cls, data: Any) -> Any:
        """Validate the create tag from string: <create:name:nonce>."""
        if isinstance(data, str):
            if m := cls.regex_pattern.match(data):
                create_type = m.group(1)
                name = m.group(2)
                kwargs = {
                    "create_type": create_type,
                    "name": name,
                }
                if create_type == "create":
                    kwargs["nonce"] = m.group(3)
                elif create_type == "create2":
                    kwargs["salt"] = m.group(3)
                    kwargs["initcode"] = m.group(4)
                return kwargs
        return data

    def resolve(self, tags: TagDict) -> Address:
        """Resolve the tag."""
        assert self.name in tags, f"Tag {self.name} not found in tags"
        if self.create_type == "create":
            assert self.nonce is not None, "Nonce is required for create"
            return compute_create_address(address=tags[self.name], nonce=self.nonce)
        elif self.create_type == "create2":
            assert self.salt is not None, "Salt is required for create2"
            assert self.initcode is not None, "Init code is required for create2"
            return compute_create2_address(
                address=tags[self.name], salt=self.salt, initcode=self.initcode
            )
        else:
            raise ValueError(f"Invalid create type: {self.create_type}")


class SenderTag(AddressTag):
    """Sender tag."""

    type: ClassVar[str] = "eoa"
    regex_pattern: ClassVar[re.Pattern] = re.compile(r"<eoa:(\w+)(:0x.+)?>")


class SenderKeyTag(Tag[EOA]):
    """Sender eoa tag."""

    type: ClassVar[str] = "eoa"
    regex_pattern: ClassVar[re.Pattern] = re.compile(r"<eoa:(\w+)(:0x.+)?>")

    def resolve(self, tags: TagDict) -> EOA:
        """Resolve the tag."""
        assert self.name in tags, f"Tag {self.name} not found in tags"
        eoa = tags[self.name]
        assert isinstance(eoa, EOA), f"Tag {self.name} is not an EOA"
        return eoa
