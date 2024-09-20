"""
Ethereum test execution format definitions.
"""
from enum import Enum


class ExecuteFormats(Enum):
    """
    Helper class to define execution formats.
    """

    UNSET_TEST_FORMAT = "unset_test_format"
    TRANSACTION_POST = "transaction_post"

    def description(self) -> str:
        """
        Return a human-readable description of the format.
        """
        return {
            ExecuteFormats.UNSET_TEST_FORMAT: "Unset test format",
            ExecuteFormats.TRANSACTION_POST: "Simple transaction-send then post-check",
        }[self]
