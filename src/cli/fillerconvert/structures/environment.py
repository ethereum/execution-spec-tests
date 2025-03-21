"""Environment structure of ethereum/tests fillers."""

from pydantic import BaseModel, Field

from .common import AddressInFiller, ValueInFiller


class EnvironmentInStateTestFiller(BaseModel):
    """Class that represents an environment filler."""

    current_coinbase: AddressInFiller = Field(..., alias="currentCoinbase")
    current_difficulty: ValueInFiller = Field(..., alias="currentDifficulty")
    current_gas_limit: ValueInFiller = Field(..., alias="currentGasLimit")
    current_number: ValueInFiller = Field(..., alias="currentNumber")
    current_timestamp: ValueInFiller = Field(..., alias="currentTimestamp")

    current_base_fee: ValueInFiller | None = Field(None, alias="currentBaseFee")

    class Config:
        """Model Config."""

        extra = "forbid"
