"""
EVM account types definitions.
"""

from enum import Enum


class AccountType(str, Enum):
    """
    Enum representing the type of account.
    """

    EMPTY = "empty"
    EOA = "eoa"
    EOA_WITH_SET_CODE = "eoa_with_set_code"
    CONTRACT = "contract"
    EOF_V1_CONTRACT = "eof_v1_contract"

    def __str__(self) -> str:
        """
        Return the name of the EVM account type.
        """
        return self.name
