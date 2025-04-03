"""Helper functions."""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal

import pytest

from ethereum_clis import Result
from ethereum_test_exceptions import (
    BlockException,
    ExceptionBase,
    ExceptionWithMessage,
    TransactionException,
    UndefinedException,
)
from ethereum_test_types import Transaction, TransactionReceipt


class UnexpectedSuccessError(Exception):
    """Exception used when the transaction expected to fail succeeded instead."""

    def __init__(self, ty: Literal["Block", "Transaction"], **kwargs):
        """Initialize the unexpected success exception."""
        message = (
            f"\nUnexpected success on {ty} ({kwargs}):\n  What: {ty} expected to fail succeeded!"
        )
        super().__init__(message)


class UnexpectedFailError(Exception):
    """Exception used when a transaction/block expected to succeed failed instead."""

    def __init__(
        self,
        ty: Literal["Block", "Transaction"],
        message: str,
        exception: ExceptionBase | UndefinedException,
        **kwargs,
    ):
        """Initialize the exception."""
        message = (
            f"Unexpected fail on {ty} ({kwargs}):"
            f"\n   What: {ty} unexpectedly failed!"
            f'\n  Error: "{message}" ({exception})'
        )
        super().__init__(message)


class UndefinedExceptionError(Exception):
    """Exception used when the exception is undefined."""

    def __init__(
        self,
        ty: Literal["Block", "Transaction"],
        want_exception: ExceptionBase | List[ExceptionBase],
        got_exception: UndefinedException,
        **kwargs,
    ):
        """Initialize the exception."""
        message = (
            f"Exception mismatch on {ty} ({kwargs}):"
            f"\n   What: {ty} exception mismatch!"
            f"\n   Want: {want_exception}"
            f'\n    Got: "{got_exception}"'
            "\n No exception defined for error message got, please add it to "
            f"{got_exception.mapper_name}"
        )
        super().__init__(message)


class ExceptionMismatchError(Exception):
    """
    Exception used when the actual block/transaction error string differs from
    the expected one.
    """

    def __init__(
        self,
        ty: Literal["Block", "Transaction"],
        want_exception: ExceptionBase | List[ExceptionBase],
        got_exception: ExceptionBase,
        got_message: str,
        **kwargs,
    ):
        """Initialize the exception."""
        message = (
            f"Exception mismatch on {ty} ({kwargs}):"
            f"\n   What: {ty} exception mismatch!"
            f"\n   Want: {want_exception}"
            f'\n    Got: "{got_exception}" ({got_message})'
        )
        super().__init__(message)


class TransactionReceiptMismatchError(Exception):
    """Exception used when the actual transaction receipt differs from the expected one."""

    def __init__(
        self,
        index: int,
        field_name: str,
        expected_value: Any,
        actual_value: Any,
    ):
        """Initialize the exception."""
        message = (
            f"\nTransactionReceiptMismatch (pos={index}):"
            f"\n   What: {field_name} mismatch!"
            f"\n   Want: {expected_value}"
            f"\n    Got: {actual_value}"
        )
        super().__init__(message)


@dataclass
class ExceptionInfo:
    """Info to print transaction exception error messages."""

    ty: Literal["Block", "Transaction"]
    expected_exception: List[ExceptionBase] | ExceptionBase | None
    actual_exception: ExceptionBase | UndefinedException | None
    message: str | None
    strict_match: bool
    context: Dict[str, Any]

    def __init__(
        self,
        *,
        ty: Literal["Block", "Transaction"],
        expected_exception: List[ExceptionBase] | ExceptionBase | None,
        actual_exception: ExceptionWithMessage | UndefinedException | None,
        strict_match: bool = False,
        context: Dict[str, Any],
    ):
        """Initialize the exception."""
        self.ty = ty
        self.expected_exception = expected_exception
        self.actual_exception = (
            actual_exception.exception
            if isinstance(actual_exception, ExceptionWithMessage)
            else actual_exception
        )
        if self.actual_exception is None:
            self.message = None
        else:
            self.message = (
                actual_exception.message
                if isinstance(actual_exception, ExceptionWithMessage)
                else str(actual_exception)
            )
        self.strict_match = strict_match
        self.context = context

    def verify(self: "ExceptionInfo"):
        """Verify the exception."""
        expected_exception, actual_exception = (
            self.expected_exception,
            self.actual_exception,
        )
        if expected_exception and not actual_exception:
            raise UnexpectedSuccessError(ty=self.ty, **self.context)
        elif not expected_exception and actual_exception:
            assert self.message is not None
            raise UnexpectedFailError(
                ty=self.ty,
                message=self.message,
                exception=actual_exception,
                **self.context,
            )
        elif expected_exception and actual_exception:
            if isinstance(actual_exception, UndefinedException):
                raise UndefinedExceptionError(
                    ty=self.ty,
                    want_exception=expected_exception,
                    actual_exception=actual_exception,
                    **self.context,
                )
            if self.strict_match:
                if actual_exception not in expected_exception:
                    got_message = self.message
                    assert got_message is not None
                    raise ExceptionMismatchError(
                        ty=self.ty,
                        want_exception=expected_exception,
                        got_exception=actual_exception,
                        got_message=got_message,
                        **self.context,
                    )
            else:
                pass


class TransactionExceptionInfo(ExceptionInfo):
    """Info to print transaction exception error messages."""

    def __init__(
        self,
        tx: Transaction,
        tx_index: int,
        **kwargs,
    ):
        """Initialize the exception."""
        super().__init__(
            ty="Transaction",
            expected_exception=tx.error,  # type: ignore
            strict_match=False,  # TODO: set to True when EELS t8n returns correct error messages
            context={"index": tx_index, "nonce": tx.nonce},
            **kwargs,
        )


class BlockExceptionInfo(ExceptionInfo):
    """Info to print block exception error messages."""

    def __init__(
        self,
        block_number: int,
        **kwargs,
    ):
        """Initialize the exception."""
        super().__init__(
            ty="Block",
            strict_match=True,
            context={"number": block_number},
            **kwargs,
        )


def verify_transaction_receipt(
    transaction_index: int,
    expected_receipt: TransactionReceipt | None,
    actual_receipt: TransactionReceipt | None,
):
    """
    Verify the actual receipt against the expected one.

    If the expected receipt is None, validation is skipped.

    Only verifies non-None values in the expected receipt if any.
    """
    if expected_receipt is None:
        return
    assert actual_receipt is not None
    if (
        expected_receipt.gas_used is not None
        and actual_receipt.gas_used != expected_receipt.gas_used
    ):
        raise TransactionReceiptMismatchError(
            index=transaction_index,
            field_name="gas_used",
            expected_value=expected_receipt.gas_used,
            actual_value=actual_receipt.gas_used,
        )
    # TODO: Add more fields as needed


def verify_transactions(
    *,
    txs: List[Transaction],
    result: Result,
) -> List[int]:
    """
    Verify accepted and rejected (if any) transactions against the expected outcome.
    Raises exception on unexpected rejections, unexpected successful txs, or successful txs with
    unexpected receipt values.
    """
    rejected_txs: Dict[int, ExceptionWithMessage | UndefinedException] = {
        rejected_tx.index: rejected_tx.error for rejected_tx in result.rejected_transactions
    }

    receipt_index = 0
    for i, tx in enumerate(txs):
        error_message = rejected_txs[i] if i in rejected_txs else None
        info = TransactionExceptionInfo(
            tx=tx,
            tx_index=i,
            actual_exception=error_message,
        )
        info.verify()
        if error_message is None:
            verify_transaction_receipt(i, tx.expected_receipt, result.receipts[receipt_index])
            receipt_index += 1

    return list(rejected_txs.keys())


def verify_block(
    *,
    block_number: int,
    expected_exception: List[TransactionException | BlockException]
    | TransactionException
    | BlockException
    | None,
    result: Result,
):
    """Verify the block exception against the expected one."""
    info = BlockExceptionInfo(
        block_number=block_number,
        expected_exception=expected_exception,
        actual_exception=result.block_exception,
    )
    info.verify()


def is_slow_test(request: pytest.FixtureRequest) -> bool:
    """Check if the test is slow."""
    if hasattr(request, "node"):
        return request.node.get_closest_marker("slow") is not None
    return False
