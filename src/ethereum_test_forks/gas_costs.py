"""
Defines the data class that will contain gas cost constants on each fork.
"""

from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class GasCosts:
    """
    Class that contains the gas cost constants for any fork.
    """

    G_JUMPDEST: int | None = None
    G_BASE: int | None = None
    G_VERY_LOW: int | None = None
    G_LOW: int | None = None
    G_MID: int | None = None
    G_HIGH: int | None = None
    G_WARM_ACCOUNT_ACCESS: int | None = None
    G_COLD_ACCOUNT_ACCESS: int | None = None
    G_ACCESS_LIST_ADDRESS: int | None = None
    G_ACCESS_LIST_STORAGE: int | None = None
    G_WARM_SLOAD: int | None = None
    G_COLD_SLOAD: int | None = None
    G_STORAGE_SET: int | None = None
    G_STORAGE_RESET: int | None = None

    R_STORAGE_CLEAR: int | None = None

    G_SELF_DESTRUCT: int | None = None
    G_CREATE: int | None = None

    G_CODE_DEPOSIT_BYTE: int | None = None
    G_INITCODE_WORD: int | None = None

    G_CALL_VALUE: int | None = None
    G_CALL_STIPEND: int | None = None
    G_NEW_ACCOUNT: int | None = None

    G_EXP: int | None = None
    G_EXP_BYTE: int | None = None

    G_MEMORY: int | None = None

    G_TX_DATA_ZERO: int | None = None
    G_TX_DATA_NON_ZERO: int | None = None

    G_TRANSACTION: int | None = None
    G_TRANSACTION_CREATE: int | None = None

    G_LOG: int | None = None
    G_LOG_DATA: int | None = None
    G_LOG_TOPIC: int | None = None

    G_KECCAK_256: int | None = None
    G_KECCAK_256_WORD: int | None = None

    G_COPY: int | None = None
    G_BLOCKHASH: int | None = None
