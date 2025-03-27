"""General transaction structure of ethereum/tests fillers."""

from typing import Any, List

from pydantic import BaseModel, Field, model_validator

from ethereum_test_base_types import AccessList

from .common import AddressInFiller, CodeInFiller, Hash32InFiller, ValueInFiller


class DataWithAccessList(BaseModel):
    """Class that represents data with access list."""

    data: CodeInFiller
    access_list: List[AccessList] | None = Field(None, alias="accessList")

    class Config:
        """Model Config."""

        extra = "forbid"

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

    max_fee_per_gas: ValueInFiller | None = Field(None, alias="maxFeePerGas")
    max_priority_fee_per_gas: ValueInFiller | None = Field(None, alias="maxPriorityFeePerGas")

    max_fee_per_blob_gas: ValueInFiller | None = Field(None, alias="maxFeePerBlobGas")
    blob_versioned_hashes: List[Hash32InFiller] | None = Field(None, alias="blobVersionedHashes")

    class Config:
        """Model Config."""

        extra = "forbid"

    @model_validator(mode="after")
    @classmethod
    def check_fields(cls, data: "GeneralTransactionInFiller") -> "GeneralTransactionInFiller":
        """Validate all fields are set."""
        if data.gas_price is None:
            if data.max_fee_per_gas is None or data.max_priority_fee_per_gas is None:
                raise ValueError(
                    "If `gasPrice` is not set,"
                    " `maxFeePerGas` and `maxPriorityFeePerGas` must be set!"
                )
        return data
