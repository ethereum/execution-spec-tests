"""
Base pydantic classes used to define the models for Ethereum tests.
"""

from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Model = TypeVar("Model", bound=BaseModel)


class EthereumTestBaseModel(BaseModel):
    """
    Base model for all models for Ethereum tests.

    This is the root class that all type inherits from, and any pydantic
    configuration override that must apply to all models
    should be placed here.
    """

    def serialize(
        self,
        mode: Literal["json", "python"] = "json",
        by_alias: bool = True,
        exclude_none: bool = True,
    ) -> dict[str, Any]:
        """
        Serializes the model to the specified format with the given parameters.

        :param mode: The mode of serialization.
              If mode is 'json', the output will only contain JSON serializable types.
              If mode is 'python', the output may contain non-JSON-serializable Python objects.
        :param by_alias: Whether to use aliases for field names, default is True.
        :param exclude_none: Whether to exclude fields with None values, default is True.
        :return: The serialized representation of the model.
        """
        return self.model_dump(mode=mode, by_alias=by_alias, exclude_none=exclude_none)

    def __repr_args__(self):
        """
        Generate a list of attribute-value pairs for the object representation.

        This method serializes the model, retrieves the attribute names,
        and constructs a list of tuples containing attribute names and their corresponding values.
        Only attributes with non-None values are included in the list.

        This method is used by the __repr__ method to generate the object representation,
        and is used by `gentest` module to generate the test cases.

        See:
        - https://pydantic-docs.helpmanual.io/usage/models/#custom-repr
        - https://github.com/ethereum/execution-spec-tests/pull/901#issuecomment-2443296835

        Returns:
            List[Tuple[str, Any]]: A list of tuples where each tuple contains an attribute name
                                   and its corresponding non-None value.
        """
        attrs_names = self.serialize(by_alias=False).keys()
        attrs = ((s, getattr(self, s)) for s in attrs_names)

        # Convert field values based on their type.
        # This ensures consistency between JSON and Python object representations.
        # Should a custom `__repr__` be needed for a specific type, it can added in the
        # match statement below.
        # Otherwise, the default string representation is used.
        repr_attrs = []
        for a, v in attrs:
            match v:
                case list() | dict() | BaseModel():
                    repr_attrs.append((a, v))
                case _:
                    repr_attrs.append((a, str(v)))
        return repr_attrs


class CopyValidateModel(EthereumTestBaseModel):
    """
    Model that supports copying with validation.
    """

    def copy(self: Model, **kwargs) -> Model:
        """
        Creates a copy of the model with the updated fields that are validated.
        """
        return self.__class__(**(self.model_dump(exclude_unset=True) | kwargs))


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
