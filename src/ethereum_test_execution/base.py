"""Ethereum test execution base types."""

from abc import abstractmethod
from typing import ClassVar, Type

from ethereum_test_base_types import CamelModel
from ethereum_test_rpc import EthRPC


class BaseExecute(CamelModel):
    """Represents a base execution format."""

    # Execute format properties
    execute_format_name: ClassVar[str] = "unset"
    description: ClassVar[str] = "Unknown execute format; it has not been set."

    @abstractmethod
    def execute(self, eth_rpc: EthRPC):
        """Execute the format."""
        pass


class ExecuteFormatWithPytestID:
    """Represents an execution format with a custom pytest id."""

    format: Type[BaseExecute]
    pytest_id: str

    def __init__(
        self, execute_format: "Type[BaseExecute] | ExecuteFormatWithPytestID", pytest_id: str
    ):
        """Initialize the execute format with a custom pytest id."""
        self.format = (
            execute_format.format
            if isinstance(execute_format, ExecuteFormatWithPytestID)
            else execute_format
        )
        self.pytest_id = pytest_id

    @property
    def execute_format_name(self) -> str:
        """Get the execute format name."""
        return self.format.execute_format_name


# Type alias for a base execute class
ExecuteFormat = Type[BaseExecute]
