"""
VERKLE HELPERS

NOTE: This file is temporary, probably it should live in other place in the library
"""

from enum import Enum

from ethereum_test_tools import Address


class AccountHeaderEntry(Enum):
    """
    Represents all the data entries in an account header.
    """

    VERSION = 0
    BALANCE = 1
    NONCE = 2
    CODE_HASH = 3
    CODE_SIZE = 4


def vkt_key_header(address: Address, entry: AccountHeaderEntry):
    """
    Return the Verkle Tree key for the address for the given address and entry.
    """
    # TODO(verkle):
    #   Must call `evm block verkle-key <address-hex>` which returns a
    #   32-byte key in hex.
    tree_key = {}

    # We override the least-significant byte of the returned address with the
    # provided sub-index.
    tree_key[31] = entry

    return tree_key


def vkt_key_storage_slot(address, storage_slot):
    """
    Return the Verkle Tree key for the address for the given address storage slot.
    """
    # TODO(verkle):
    #   Must call `evm block verkle-key <address-hex> <storage-slot-hex>` which returns a
    #   32-byte key in hex.
    tree_key = {}

    return tree_key
