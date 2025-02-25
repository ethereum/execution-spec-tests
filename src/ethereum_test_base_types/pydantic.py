"""Base pydantic classes used to define the models for Ethereum tests."""

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, RootModel
from pydantic.alias_generators import to_camel

from .mixins import ModelCustomizationsMixin

Model = TypeVar("Model", bound=BaseModel)

RootModelRootType = TypeVar("RootModelRootType")


class EthereumTestBaseModel(BaseModel, ModelCustomizationsMixin):
    """Base model for all models for Ethereum tests."""

    pass


class EthereumTestRootModel(RootModel[RootModelRootType], ModelCustomizationsMixin):
    """Base model for all models for Ethereum tests."""

    root: Any


class CopyValidateModel(EthereumTestBaseModel):
    """Model that supports copying with validation."""

    def _convert_kwargs_to_alias(self, kwargs: dict) -> dict:
        converted = {}
        for key, value in kwargs.items():
            field = self.__class__.model_fields.get(key)
            converted[field.alias if field and field.alias else key] = value
        return converted

    def copy(self: Model, **kwargs) -> Model:
        """Create a copy of the model with the updated fields that are validated."""
        alias_kwargs = self._convert_kwargs_to_alias(kwargs)
        return self.__class__(
            **(self.model_dump(exclude_unset=True, by_alias=True) | alias_kwargs)
        )


class CamelModel(CopyValidateModel):
    """
    A base model that converts field names to camel case when serializing.

    For example, the field name `current_timestamp` in a Python model will be represented
    as `currentTimestamp` when it is serialized to json.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        validate_default=True,
    )
