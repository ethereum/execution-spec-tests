"""
VERKLE HELPERS

NOTE: This file is temporary, probably it should live in other place in the library
"""

from enum import Enum
from typing import ClassVar, Dict

from ethereum.crypto.hash import keccak256

from ethereum_test_tools import Account, Address, Hash


class AccountHeaderEntry(Enum):
    """
    Represents all the data entries in an account header.
    """

    BASIC_DATA = 0
    CODEHASH = 1

    PRESENT: ClassVar[None] = None


class Witness:
    """
    Witness is a list of witness key-values.
    """

    # TODO(verkle): "Hash" as value type isn't the right name but correct underlying type.
    # Change to appropriate type.
    witness: Dict[Hash, Hash | None]

    def add_account_full(self, addr: Address, account: Account):
        """
        Add the full account present witness for the given address.
        """
        self.add_account_basic_data(addr, account)
        self.add_account_codehash(addr, Hash(keccak256(account.code)))

    def add_account_basic_data(self, address: Address, account: Account | None):
        """
        Adds the basic data witness for the given address.
        """
        if account is None:
            self.witness[_account_key(address, AccountHeaderEntry.BASIC_DATA)] = None
            return

        # | Name        | Offset | Size |
        # | ----------- | ------ | ---- |
        # | `version`   | 0      | 1    |
        # | `nonce`     | 4      | 8    |
        # | `code_size` | 12     | 4    |
        # | `balance`   | 16     | 16   |
        basic_data_value = Hash(0)  # TODO(verkle): encode as little_endian(table_above)
        self.witness[_account_key(address, AccountHeaderEntry.BASIC_DATA)] = basic_data_value

    def add_account_codehash(self, address: Address, codehash: Hash):
        """
        Adds the CODEHASH witness for the given address.
        """
        self.witness[_account_key(address, AccountHeaderEntry.CODEHASH)] = codehash

    def add_storage_slot(self, address, storage_slot, value):
        """
        Adds the storage slot witness for the given address and storage slot.
        """
        # TODO(verkle):
        #   Must call `evm transition verkle-key <address-hex> <storage-slot-hex>` which returns a
        #   32-byte key in hex.
        tree_key = {}

        self.witness[tree_key] = value

    def add_code_chunk(self, address, chunk_number, value):
        """
        Adds the code chunk witness for the given address and chunk number.
        """
        # TODO(verkle):
        #   Must call `evm transition code-chunk-key <address-hex> <chunk-number>` which returns a
        #   32-byte key in hex.
        tree_key = {}

        self.witness[tree_key] = value

    def merge(self, other):
        """
        Merge the provided witness into this witness.
        """
        self.witness.update(other.witness)


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


def _account_key(address: Address, entry: AccountHeaderEntry):
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
