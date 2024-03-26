"""
Test suite for ethereum_test_tools.exceptions
"""

import pytest

from ..exceptions import BlockException, TransactionException


@pytest.mark.parametrize(
    "exception, expected",
    [
        (
            TransactionException.INSUFFICIENT_ACCOUNT_FUNDS,
            "TransactionException.INSUFFICIENT_ACCOUNT_FUNDS",
        ),
        (
            TransactionException.INITCODE_SIZE_EXCEEDED,
            "TransactionException.INITCODE_SIZE_EXCEEDED",
        ),
        (BlockException.INCORRECT_BLOB_GAS_USED, "BlockException.INCORRECT_BLOB_GAS_USED"),
        (BlockException.INCORRECT_BLOCK_FORMAT, "BlockException.INCORRECT_BLOCK_FORMAT"),
    ],
)
def test_exceptions_string_conversion(
    exception: BlockException | TransactionException, expected: str
):
    """
    Test that the exceptions are unique and have the correct string representation.
    """
    assert str(exception) == expected


@pytest.mark.parametrize(
    "exception,expected",
    [
        (
            BlockException.INCORRECT_BLOB_GAS_USED
            | TransactionException.INSUFFICIENT_ACCOUNT_FUNDS,
            "BlockException.INCORRECT_BLOB_GAS_USED|"
            "TransactionException.INSUFFICIENT_ACCOUNT_FUNDS",
        ),
        (
            BlockException.INCORRECT_BLOB_GAS_USED
            | TransactionException.INSUFFICIENT_ACCOUNT_FUNDS
            | TransactionException.INITCODE_SIZE_EXCEEDED,
            "BlockException.INCORRECT_BLOB_GAS_USED"
            "|TransactionException.INITCODE_SIZE_EXCEEDED"
            "|TransactionException.INSUFFICIENT_ACCOUNT_FUNDS",
        ),
        (
            TransactionException.INSUFFICIENT_ACCOUNT_FUNDS
            | BlockException.INCORRECT_BLOB_GAS_USED,
            "BlockException.INCORRECT_BLOB_GAS_USED"
            "|TransactionException.INSUFFICIENT_ACCOUNT_FUNDS",
        ),
        (
            TransactionException.INSUFFICIENT_ACCOUNT_FUNDS
            | BlockException.INCORRECT_BLOB_GAS_USED
            | BlockException.INCORRECT_BLOB_GAS_USED,
            "BlockException.INCORRECT_BLOB_GAS_USED"
            "|TransactionException.INSUFFICIENT_ACCOUNT_FUNDS",
        ),
    ],
)
def test_exceptions_or(exception, expected: str):
    """
    Test that the exceptions can be combined using the | operator.
    """
    assert str(exception) == expected
