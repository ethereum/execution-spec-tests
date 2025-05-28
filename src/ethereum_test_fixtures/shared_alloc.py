"""Shared pre-allocation models for test fixture generation."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ethereum_test_base_types import EthereumTestRootModel
from ethereum_test_types import Alloc, Environment


class SharedPreStateGroup(BaseModel):
    """
    Shared pre-state group for tests with identical Environment and fork values.

    Groups tests by a hash of their fixture Environment and fork to enable
    shared pre-allocation optimization.
    """

    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    test_count: int = Field(0, description="Number of tests in this group")
    pre_account_count: int = Field(0, description="Number of accounts in the pre-allocation")
    test_ids: List[str] = Field(default_factory=list, alias="testIds")
    fork: str = Field(..., alias="network")
    environment: Environment = Field(..., description="Grouping environment for this test group")
    pre: Optional[Alloc] = Field(None)


class SharedPreState(EthereumTestRootModel):
    """Root model mapping pre-state hashes to test groups."""

    root: Dict[str, SharedPreStateGroup]

    def __setitem__(self, key: str, value: Any):
        """Set item in root dict."""
        self.root[key] = value

    @classmethod
    def from_raw_dict(cls, data: Dict[str, Any]) -> "SharedPreState":
        """Create SharedPreState from raw dict (keys already strings)."""
        return cls(root=data)

    def __getitem__(self, item):
        """Get item from root dict."""
        return self.root[item]

    def __iter__(self):
        """Iterate over root dict."""
        return iter(self.root)

    def __contains__(self, item):
        """Check if item in root dict."""
        return item in self.root

    def __len__(self):
        """Get length of root dict."""
        return len(self.root)

    def keys(self):
        """Get keys from root dict."""
        return self.root.keys()

    def values(self):
        """Get values from root dict."""
        return self.root.values()

    def items(self):
        """Get items from root dict."""
        return self.root.items()
