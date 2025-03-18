"""General transaction structure of ethereum/tests fillers."""

from typing import List

from pydantic import BaseModel, Field

from .common import AddressInFiller, CodeInFiller, Hash32InFiller, ValueInFiller


class GeneralTransactionInFiller(BaseModel):
    """Class that represents general transaction in filler."""

    data: List[CodeInFiller]
    gas_limit: List[ValueInFiller] = Field(..., alias="gasLimit")
    gas_price: ValueInFiller = Field(..., alias="gasPrice")
    nonce: ValueInFiller
    to: AddressInFiller
    value: List[ValueInFiller]
    secret_key: Hash32InFiller = Field(..., alias="secretKey")
