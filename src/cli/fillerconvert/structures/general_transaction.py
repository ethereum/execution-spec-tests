"""General transaction structure of ethereum/tests fillers."""

from typing import Any, List

from pydantic import BaseModel, Field, model_validator

from ethereum_test_base_types import AccessList

from .common import AddressInFiller, CodeInFiller, Hash32InFiller, ValueInFiller


class DataWithAccessList(BaseModel):
    """Class that represents data with access list."""

    data: CodeInFiller
    access_list: List[AccessList] | None = None

    @model_validator(mode="wrap")
    @classmethod
    def wrap_data_only(cls, data: Any, handler) -> "DataWithAccessList":
        """Wrap data only if it is not a dictionary."""
        if not isinstance(data, dict) and not isinstance(data, DataWithAccessList):
            data = {"data": data}
        return handler(data)


class GeneralTransactionInFiller(BaseModel):
    """Class that represents general transaction in filler."""

    data: List[DataWithAccessList]
    gas_limit: List[ValueInFiller] = Field(..., alias="gasLimit")
    gas_price: ValueInFiller | None = Field(None, alias="gasPrice")
    nonce: ValueInFiller
    to: AddressInFiller
    value: List[ValueInFiller]
    secret_key: Hash32InFiller = Field(..., alias="secretKey")
