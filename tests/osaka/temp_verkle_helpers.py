"""
VERKLE HELPERS

NOTE: This file is temporary, probably it should live in other place in the library
"""

from enum import Enum
from typing import ClassVar

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

    PRESENT: ClassVar[None] = None


def vkt_key_header(address: Address, entry: AccountHeaderEntry):
    """
    Return the Verkle Tree key for the address for the given address and entry.
    """
    # TODO(verkle):
    #   Must call `evm transition verkle-key <address-hex>` which returns a
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
    #   Must call `evm transition verkle-key <address-hex> <storage-slot-hex>` which returns a
    #   32-byte key in hex.
    tree_key = {}

    return tree_key


def vkt_key_code_chunk(address, chunk_number):
    """
    Return the Verkle Tree key corresponding to the chunk_numberfor the given address.
    """
    # TODO(verkle):
    #   Must call `evm transition code-chunk-key <address-hex> <chunk-number>` which returns a
    #   32-byte key in hex.
    tree_key = {}

    return tree_key


def vkt_chunkify(bytecode):
    """
    Return the chunkification of the provided bytecode.
    """
    # TODO(verkle):
    #   Must call `evm transition verkle-chunkify-code <bytecode-hex>` which returns a hex of
    #   the chunkified code. The returned byte length is a multiple of 32. `code_chunks` must be
    #   a list of 32-byte chunks (i.e: partition the returned bytes into 32-byte bytes)
    code_chunks = {}

    return code_chunks


def vkt_add_all_headers_present(witness_keys, addr):
    """
    Adds to witness_keys that all account headers entries should be present.
    """
    witness_keys[vkt_key_header(addr, AccountHeaderEntry.VERSION)] = AccountHeaderEntry.PRESENT
    witness_keys[vkt_key_header(addr, AccountHeaderEntry.BALANCE)] = AccountHeaderEntry.PRESENT
    witness_keys[vkt_key_header(addr, AccountHeaderEntry.NONCE)] = AccountHeaderEntry.PRESENT
    witness_keys[vkt_key_header(addr, AccountHeaderEntry.CODE_HASH)] = AccountHeaderEntry.PRESENT
    witness_keys[vkt_key_header(addr, AccountHeaderEntry.CODE_SIZE)] = AccountHeaderEntry.PRESENT
