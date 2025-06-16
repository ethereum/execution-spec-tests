"""Account structure of ethereum/tests fillers."""

from typing import Dict

from pydantic import BaseModel

from .common import CodeInFiller, ValueInFiller, ValueOrTagInFiller


class AccountInFiller(BaseModel):
    """Class that represents an account in filler."""

    balance: ValueInFiller
    code: CodeInFiller
    nonce: ValueInFiller
    storage: Dict[ValueInFiller, ValueOrTagInFiller]

    class Config:
        """Model Config."""

        extra = "forbid"
        arbitrary_types_allowed = True  # For CodeInFiller
