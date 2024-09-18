"""
EEST Exception mapper
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from bidict import frozenbidict

from .exceptions import ExceptionBase, TransactionException, UndefinedException


@dataclass
class ExceptionMessage:
    """Defines a mapping between an exception and a message."""

    exception: ExceptionBase
    message: str


class ExceptionMapper(ABC):
    """
    Translate between EEST exceptions and error strings returned by client's t8n or other tools.
    """

    def __init__(self) -> None:
        # Ensure that the subclass has properly defined _mapping_data before accessing it
        assert self._mapping_data is not None, "_mapping_data must be defined in subclass"

        assert len(set(entry.exception for entry in self._mapping_data)) == len(
            self._mapping_data
        ), "Duplicate exception in _mapping_data"
        assert len(set(entry.message for entry in self._mapping_data)) == len(
            self._mapping_data
        ), "Duplicate message in _mapping_data"
        self.exception_to_message_map: frozenbidict = frozenbidict(
            {entry.exception: entry.message for entry in self._mapping_data}
        )

    @property
    @abstractmethod
    def _mapping_data(self):
        """This method should be overridden in the subclass to provide mapping data."""
        pass

    def exception_to_message(self, exception: ExceptionBase) -> str:
        """Takes an exception and returns a formatted string."""
        message = self.exception_to_message_map.get(exception, "Undefined")
        return message

    def message_to_exception(self, exception_string: str) -> ExceptionBase:
        """Takes a string and tries to find matching exception"""
        # TODO inform tester where to add the missing exception if get uses default
        exception = self.exception_to_message_map.inverse.get(
            exception_string, UndefinedException.UNDEFINED_EXCEPTION
        )
        return exception

    def check_transaction(self, tx_error_message: str | None, tx, tx_pos: int):
        """Verify transaction exception"""
        exception_info = f"TransactionException (pos={tx_pos}, nonce={tx.nonce})\n"

        if tx.error and not tx_error_message:
            raise Exception(f"{exception_info} Error: tx expected to fail succeeded")
        elif not tx.error and tx_error_message:
            raise Exception(f"{exception_info} Error: tx unexpectedly failed: {tx_error_message}")
        # TODO check exception list case
        elif isinstance(tx.error, TransactionException) and tx_error_message:
            expected_error_message = self.exception_to_message(tx.error)
            error_exception = self.message_to_exception(tx_error_message)

            define_message_hint = (
                f"No message defined for {tx.error}, please add it to {self.__class__.__name__}"
                if expected_error_message == "Undefined"
                else ""
            )
            define_exception_hint = (
                f"No exception defined for error message got, "
                f"please add it to {self.__class__.__name__}"
                if error_exception == UndefinedException.UNDEFINED_EXCEPTION
                else ""
            )

            if expected_error_message not in tx_error_message:
                raise Exception(
                    f"{exception_info}"
                    f"Error: exception mismatch:\n want = '{expected_error_message}' ({tx.error}),"
                    f"\n got  = '{tx_error_message}' ({error_exception})"
                    f"\n {define_message_hint}"
                    f"\n {define_exception_hint}"
                )
