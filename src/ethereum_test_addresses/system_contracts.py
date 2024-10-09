"""
System contract addresses
"""

from enum import Enum

from ethereum_test_base_types import Address


class SystemContract(Address, Enum):
    """
    Enum that lists the addresses of the system contracts.
    """

    BEACON_ROOT_HISTORY = Address(
        0x000F3DF6D732807EF1319FB7B8BB8522D0BEAC02, label="beacon_root_history"
    )
    BLOCK_HISTORY = Address(0x0AAE40965E6800CD9B1F4B05FF21581047E3F91E, label="block_history")
    BEACON_DEPOSITS = Address(0x00000000219AB540356CBB839CBE05303D7705FA, label="beacon_deposits")
    WITHDRAWAL_REQUESTS = Address(
        0x00A3CA265EBCB825B45F985A16CEFB49958CE017, label="withdrawal_requests"
    )
    CONSOLIDATION_REQUESTS = Address(
        0x00B42DBF2194E931E80326D950320F7D9DBEAC02, label="consolidation_requests"
    )
