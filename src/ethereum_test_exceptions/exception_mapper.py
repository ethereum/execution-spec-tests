"""
EEST Exception mapper
"""
from abc import ABC, abstractmethod

from .exceptions import ExceptionBase


class ExceptionMapper(ABC):
    """
    Translate between EEST exceptions and error strings returned by client's t8n or other tools.
    """

    @abstractmethod
    def exception_to_message(self, exception: ExceptionBase) -> str:
        """
        Translate an ExceptionBase instance to a string message.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def message_to_exception(self, exception_string: str) -> ExceptionBase:
        """
        Translate a string message to an ExceptionBase instance.
        Must be implemented by subclasses.
        """
        pass
