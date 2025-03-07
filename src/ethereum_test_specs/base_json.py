"""Base class to parse test cases written in JSON/YAML."""

from abc import abstractmethod
from typing import Any, Callable, ClassVar, Dict, List, Sequence, Type, Union

from pydantic import BaseModel, TypeAdapter, ValidatorFunctionWrapHandler, model_validator

from ethereum_test_fixtures import FixtureFormat, LabeledFixtureFormat
from ethereum_test_forks import Fork


class BaseJSONTest(BaseModel):
    """Represents a base class that reads cases from JSON/YAML files."""

    formats: ClassVar[List[Type["BaseJSONTest"]]] = []
    formats_type_adapter: ClassVar[TypeAdapter]

    format_name: ClassVar[str] = ""

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | LabeledFixtureFormat]] = []

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """
        Register all subclasses of BaseJSONTest with a fixture format name set
        as possible fixture formats.
        """
        if cls.format_name:
            # Register the new fixture format
            BaseJSONTest.formats.append(cls)
            if len(BaseJSONTest.formats) > 1:
                BaseJSONTest.formats_type_adapter = TypeAdapter(
                    Union[tuple(BaseJSONTest.formats)],
                )
            else:
                BaseJSONTest.formats_type_adapter = TypeAdapter(cls)

    @model_validator(mode="wrap")
    @classmethod
    def _parse_into_subclass(cls, v: Any, handler: ValidatorFunctionWrapHandler) -> "BaseJSONTest":
        """Parse the fixture into the correct subclass."""
        if cls is BaseJSONTest:
            return BaseJSONTest.formats_type_adapter.validate_python(v)
        return handler(v)

    @abstractmethod
    def get_valid_from_fork(self) -> Fork | None:
        """Get the first fork this JSON filler supports."""
        raise NotImplementedError

    @abstractmethod
    def get_valid_until_fork(self) -> Fork | None:
        """Get the last fork this JSON filler supports."""
        raise NotImplementedError

    @abstractmethod
    def fill_function(self) -> Callable:
        """Return the test function that can be used to fill the test."""
        raise NotImplementedError

    @staticmethod
    def remove_comments(data: Dict) -> Dict:
        """Remove comments from a dictionary."""
        result = {}
        for k, v in data.items():
            if isinstance(k, str) and k.startswith("//"):
                continue
            if isinstance(v, dict):
                v = BaseJSONTest.remove_comments(v)
            elif isinstance(v, list):
                v = [BaseJSONTest.remove_comments(i) if isinstance(i, dict) else i for i in v]
            result[k] = v
        return result

    @model_validator(mode="before")
    @classmethod
    def remove_comments_from_model(cls, data: Any) -> Any:
        """
        Check if the config field is populated, otherwise use the root-level field values for
        backwards compatibility.
        """
        if isinstance(data, dict):
            return BaseJSONTest.remove_comments(data)
        return data
