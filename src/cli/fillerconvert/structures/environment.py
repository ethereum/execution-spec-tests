"""Environment structure of ethereum/tests fillers."""

from pydantic import BaseModel, Field, model_validator

from .common import AddressInFiller, ValueInFiller


class EnvironmentInStateTestFiller(BaseModel):
    """Class that represents an environment filler."""

    current_coinbase: AddressInFiller = Field(..., alias="currentCoinbase")
    current_gas_limit: ValueInFiller = Field(..., alias="currentGasLimit")
    current_number: ValueInFiller = Field(..., alias="currentNumber")
    current_timestamp: ValueInFiller = Field(..., alias="currentTimestamp")

    current_difficulty: ValueInFiller | None = Field(None, alias="currentDifficulty")
    current_random: ValueInFiller | None = Field(None, alias="currentRandom")
    current_base_fee: ValueInFiller | None = Field(None, alias="currentBaseFee")

    class Config:
        """Model Config."""

        extra = "forbid"

    @model_validator(mode="after")
    @classmethod
    def check_fields(cls, data: "EnvironmentInStateTestFiller") -> "EnvironmentInStateTestFiller":
        """Validate all fields are set."""
        if data.current_difficulty is None:
            if data.current_random is None:
                raise ValueError("If `currentDifficulty` is not set, `currentRandom` must be set!")
        return data
