"""EEST Exception mapper."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic

from bidict import frozenbidict
from pydantic import BaseModel, BeforeValidator, ValidationInfo

from .exceptions import ExceptionBase, ExceptionBoundTypeVar, UndefinedException


@dataclass
class ExceptionMessage:
    """Defines a mapping between an exception and a message."""

    exception: ExceptionBase
    message: str


class ExceptionMapper(ABC):
    """
    Translate between EEST exceptions and error strings returned by client's
    t8n or other tools.
    """

    mapper_name: str

    def __init__(self) -> None:
        """Initialize the exception mapper."""
        # Ensure that the subclass has properly defined _mapping_data before accessing it
        assert self._mapping_data is not None, "_mapping_data must be defined in subclass"

        assert len({entry.exception for entry in self._mapping_data}) == len(self._mapping_data), (
            "Duplicate exception in _mapping_data"
        )
        assert len({entry.message for entry in self._mapping_data}) == len(self._mapping_data), (
            "Duplicate message in _mapping_data"
        )
        self.exception_to_message_map: frozenbidict = frozenbidict(
            {entry.exception: entry.message for entry in self._mapping_data}
        )
        self.mapper_name = self.__class__.__name__

    @property
    @abstractmethod
    def _mapping_data(self):
        """Should be overridden in the subclass to provide mapping data."""
        pass

    def message_to_exception(self, exception_string: str) -> ExceptionBase | UndefinedException:
        """Match a formatted string to an exception."""
        for entry in self._mapping_data:
            if entry.message in exception_string:
                return entry.exception
        return UndefinedException(exception_string, mapper_name=self.mapper_name)


class ExceptionWithMessage(BaseModel, Generic[ExceptionBoundTypeVar]):
    """
    Class that contains the exception along with the verbatim message from the external
    tool/client.
    """

    exception: ExceptionBoundTypeVar
    message: str


def mapper_validator(v: str, info: ValidationInfo) -> Dict[str, Any] | UndefinedException | None:
    """
    Use the exception mapper that must be included in the context to map the exception
    from the external tool.
    """
    if v is None:
        return v
    assert isinstance(info.context, dict), f"Invalid context provided: {info.context}"
    exception_mapper = info.context.get("exception_mapper")
    assert isinstance(exception_mapper, ExceptionMapper), (
        f"Invalid mapper provided {exception_mapper}"
    )
    exception = exception_mapper.message_to_exception(v)
    if isinstance(exception, UndefinedException):
        return exception
    return {
        "exception": exception,
        "message": v,
    }


ExceptionMapperValidator = BeforeValidator(mapper_validator)
"""
Validator that can be used to annotate a pydantic field in a model that is meant to be
parsed from an external tool or client.

The annotated type must be an union that can include `None`, `UndefinedException` and a
custom model as:
```
class BlockExceptionWithMessage(ExceptionWithMessage[BlockException]):
    pass
```
where `BlockException` can be any derivation of `ExceptionBase`.

The `message` attribute is the verbatim message received from the external tool or client,
and can be used to be printed for extra context information in case of failures.
"""
