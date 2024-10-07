"""
Helper functions
"""

from dataclasses import dataclass
from typing import Dict, List

from ethereum_test_exceptions import ExceptionMapper, TransactionException, UndefinedException
from ethereum_test_types import Transaction
from evm_transition_tool import Result


@dataclass
class TransactionExceptionInfo:
    """Info to print transaction exception error messages"""

    error_message: str | None
    transaction_ind: int
    tx: Transaction


def verify_transaction_exception(
    exception_mapper: ExceptionMapper, info: TransactionExceptionInfo
):
    """Verify transaction exception"""
    exception_info = f"TransactionException (pos={info.transaction_ind}, nonce={info.tx.nonce})\n"
    expected_error: bool = info.tx.error is not None or (
        isinstance(info.tx.error, list) and len(info.tx.error) != 0
    )

    # info.tx.error is expected error code defined in .py test
    if expected_error and not info.error_message:
        raise Exception(f"{exception_info} Error: tx expected to fail succeeded")
    elif not expected_error and info.error_message:
        raise Exception(f"{exception_info} Error: tx unexpectedly failed: {info.error_message}")
    elif expected_error and info.error_message:

        if isinstance(info.tx.error, List):
            for expected_exception in info.tx.error:
                expected_error_msg = exception_mapper.exception_to_message(expected_exception)
                if expected_error_msg in info.error_message:
                    # One of expected exceptions is found in tx error string, no error
                    return

        if isinstance(info.tx.error, List):
            expected_exception = info.tx.error[0]
        elif info.tx.error is None:
            return  # will never happen but removes python logic check
        else:
            expected_exception = info.tx.error

        expected_error_msg = exception_mapper.exception_to_message(expected_exception)
        error_exception = exception_mapper.message_to_exception(info.error_message)
        exception_mapper_name = exception_mapper.__class__.__name__

        define_message_hint = (
            f"No message defined for {expected_exception}, please add it to {exception_mapper_name}"
            if expected_error_msg == "Undefined"
            else ""
        )
        define_exception_hint = (
            f"No exception defined for error message got, "
            f"please add it to {exception_mapper.__class__.__name__}"
            if error_exception == UndefinedException.UNDEFINED_EXCEPTION
            else ""
        )

        if expected_error_msg not in info.error_message:
            raise Exception(
                f"{exception_info}"
                f"Error: exception mismatch:\n want = '{expected_error_msg}' ({expected_exception}),"
                f"\n got  = '{info.error_message}' ({error_exception})"
                f"\n {define_message_hint}"
                f"\n {define_exception_hint}"
            )


def verify_transactions(
    exception_mapper: ExceptionMapper, txs: List[Transaction], result: Result
) -> List[int]:
    """
    Verify rejected transactions (if any) against the expected outcome.
    Raises exception on unexpected rejections or unexpected successful txs.
    """
    rejected_txs: Dict[int, str] = {
        rejected_tx.index: rejected_tx.error for rejected_tx in result.rejected_transactions
    }

    for i, tx in enumerate(txs):
        error_message = rejected_txs[i] if i in rejected_txs else None
        info = TransactionExceptionInfo(error_message=error_message, transaction_ind=i, tx=tx)
        verify_transaction_exception(exception_mapper=exception_mapper, info=info)

    return list(rejected_txs.keys())
