"""JSON encoding and decoding for Ethereum types."""

from typing import Any, AnyStr, List

from pydantic import BaseModel, RootModel


def to_json(
    value: BaseModel | RootModel | AnyStr | List[BaseModel | RootModel | AnyStr],
) -> Any:
    """Convert a model to its json data representation."""
    if isinstance(value, list):
        return [to_json(item) for item in value]
    elif isinstance(value, (BaseModel, RootModel)):
        return value.model_dump(mode="json", by_alias=True, exclude_none=True)
    else:
        return str(value)
