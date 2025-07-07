"""Account structure of ethereum/tests fillers."""

from typing import Any, Dict, Mapping

from pydantic import BaseModel

from ethereum_test_base_types import EthereumTestRootModel, HexNumber
from ethereum_test_types import Alloc

from .common import (
    AddressOrTagInFiller,
    CodeInFiller,
    ContractTag,
    SenderTag,
    Tag,
    TagDependentData,
    TagDict,
    ValueInFiller,
    ValueOrTagInFiller,
)


class StorageInPre(EthereumTestRootModel):
    """Class that represents a storage in pre-state."""

    root: Dict[ValueInFiller, ValueOrTagInFiller]

    def tag_dependencies(self) -> Mapping[str, Tag]:
        """Get tag dependencies."""
        tag_dependencies: Dict[str, Tag] = {}
        for k, v in self.root.items():
            if isinstance(k, Tag):
                tag_dependencies[k.name] = k
            if isinstance(v, Tag):
                tag_dependencies[v.name] = v
        return tag_dependencies

    def resolve(self, tags: TagDict) -> Dict[ValueInFiller, ValueInFiller]:
        """Resolve the storage."""
        resolved_storage: Dict[ValueInFiller, ValueInFiller] = {}
        for key, value in self.root.items():
            if isinstance(value, Tag):
                resolved_storage[key] = HexNumber(int.from_bytes(value.resolve(tags), "big"))
            else:
                resolved_storage[key] = value
        return resolved_storage


class AccountInFiller(BaseModel, TagDependentData):
    """Class that represents an account in filler."""

    balance: ValueInFiller | None = None
    code: CodeInFiller | None = None
    nonce: ValueInFiller | None = None
    storage: StorageInPre | None = None

    class Config:
        """Model Config."""

        extra = "forbid"
        arbitrary_types_allowed = True  # For CodeInFiller

    def tag_dependencies(self) -> Mapping[str, Tag]:
        """Get tag dependencies."""
        tag_dependencies: Dict[str, Tag] = {}
        if self.storage is not None:
            tag_dependencies.update(self.storage.tag_dependencies())
        if self.code is not None and isinstance(self.code, CodeInFiller):
            tag_dependencies.update(self.code.tag_dependencies())
        return tag_dependencies

    def resolve(self, tags: TagDict) -> Dict[str, Any]:
        """Resolve the account."""
        account_properties: Dict[str, Any] = {}
        if self.balance is not None:
            account_properties["balance"] = self.balance
        if self.code is not None:
            if compiled_code := self.code.compiled(tags):
                account_properties["code"] = compiled_code
        if self.nonce is not None:
                account_properties["nonce"] = self.nonce
        if self.storage is not None:
            if resolved_storage := self.storage.resolve(tags):
                account_properties["storage"] = resolved_storage
        return account_properties


class PreInFiller(EthereumTestRootModel):
    """Class that represents a pre-state in filler."""

    root: Dict[AddressOrTagInFiller, AccountInFiller]

    def setup(self, pre: Alloc, all_dependencies: Dict[str, Tag]) -> TagDict:
        """Resolve the pre-state."""
        max_tries = len(self.root)

        unresolved_accounts_in_pre = dict(self.root)
        resolved_accounts: TagDict = {}

        while max_tries > 0:
            # Naive approach to resolve accounts
            unresolved_accounts_keys = list(unresolved_accounts_in_pre.keys())
            for address_or_tag in unresolved_accounts_keys:
                account = unresolved_accounts_in_pre[address_or_tag]
                tag_dependencies = account.tag_dependencies()
                # check if all tag dependencies are resolved
                if all(dependency in resolved_accounts for dependency in tag_dependencies):
                    account_properties = account.resolve(resolved_accounts)
                    if isinstance(address_or_tag, Tag):
                        if isinstance(address_or_tag, ContractTag):
                            resolved_accounts[address_or_tag.name] = pre.deploy_contract(
                                **account_properties,
                                label=address_or_tag.name,
                            )
                        elif isinstance(address_or_tag, SenderTag):
                            if "balance" in account_properties:
                                account_properties["amount"] = account_properties.pop("balance")
                            resolved_accounts[address_or_tag.name] = pre.fund_eoa(
                                **account_properties,
                                label=address_or_tag.name,
                            )
                        else:
                            raise ValueError(f"Unknown tag type: {address_or_tag}")
                    else:
                        raise ValueError(f"Unknown tag type: {address_or_tag}")
                    del unresolved_accounts_in_pre[address_or_tag]

            max_tries -= 1
        assert len(unresolved_accounts_in_pre) == 0, (
            f"Unresolved accounts: {unresolved_accounts_in_pre}, probably a circular dependency"
        )
        for extra_dependency in all_dependencies:
            if extra_dependency not in resolved_accounts:
                if all_dependencies[extra_dependency].type != "eoa":
                    raise ValueError(f"Contract dependency {extra_dependency} not found in pre")
                # Assume the extra EOA is an empty account
                resolved_accounts[extra_dependency] = pre.fund_eoa(
                    amount=0, label=extra_dependency
                )
        return resolved_accounts
