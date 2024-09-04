"""
Useful Verkle types for generating Ethereum tests.
"""

from enum import Enum
from hashlib import sha3_256 as keccak256
from typing import Any, Dict, List, Optional, Tuple

from pydantic import Field, RootModel, field_validator
from pydantic.functional_serializers import model_serializer

from ethereum_test_base_types import Address, CamelModel, HexNumber, PaddedFixedSizeBytes
from ethereum_test_types import Account

IPA_PROOF_DEPTH = 8


class Hash(PaddedFixedSizeBytes[32]):  # type: ignore
    """
    Class that helps represent an padded Hash.
    """

    pass


class Stem(PaddedFixedSizeBytes[31]):  # type: ignore
    """
    Class that helps represent Verkle Tree Stem.
    """

    pass


class IpaProof(CamelModel):
    """
    Definition of an Inner Product Argument (IPA) proof.

    A cryptographic proof primarily used to demonstrate the correctness of an inner product
    relation between vectors committed to with polynomial commitments. Used to effectively prove
    membership or non-membership of elements in the Verkle tree.
    """

    cl: List[Hash]
    cr: List[Hash]
    final_evaluation: Hash

    @classmethod
    @field_validator("cl", "cr")
    def check_list_length(cls, v):
        """Validates the length of the left/right vector commitment lists."""
        if len(v) != IPA_PROOF_DEPTH:
            raise ValueError(f"List must contain exactly {IPA_PROOF_DEPTH} items")
        return v


class VerkleProof(CamelModel):
    """
    Definition of a Verkle Proof.

    A Verkle proof is used to prove the membership or non-membership of elements in a Verkle tree.
    It contains the necessary commitments and evaluations to verify the correctness of the elements
    in the tree.
    """

    other_stems: List[Stem]
    depth_extension_present: HexNumber
    commitments_by_path: List[Hash]
    d: Hash
    ipa_proof: IpaProof | None = Field(None)


class SuffixStateDiff(CamelModel):
    """
    Definition of a Suffix State Difference.

    Represents the state difference for a specific suffix in a Verkle tree node.
    Includes the current value and the new value for the suffix.
    """

    suffix: int
    current_value: Hash | None
    new_value: Hash | None

    @model_serializer(mode="wrap")
    def custom_serializer(self, handler) -> Dict[str, Any]:
        """
        Custom serializer to include None (null) values for current/new value.
        """
        output = handler(self)
        if self.current_value is None:
            output["currentValue"] = None
        if self.new_value is None:
            output["newValue"] = None
        return output


class StemStateDiff(CamelModel):
    """
    Definition of a Stem State Difference.

    Represents the state difference for a specific stem in a Verkle tree.
    Includes a list of differences for its suffixes.
    """

    stem: Stem
    suffix_diffs: List[SuffixStateDiff]


class StateDiff(RootModel):
    """
    Definition of a State Difference.

    Represents the overall state differences in a Verkle tree.
    This is a list of state differences for various stems.
    """

    root: List[StemStateDiff]

    def __iter__(self):
        """Returns an iterator over the State Diff"""
        return iter(self.__root__)

    def __getitem__(self, item):
        """Returns an item from the State Diff"""
        return self.__root__[item]


class Witness(CamelModel):
    """
    Definition of an Execution Witness.

    Contains all the necessary data to verify the correctness of a blockchain state transition.
    This includes the state differences indicating changes in the Verkle tree, the Verkle proof for
    proving element membership or non-membership, and the parent state root which provides the root
    hash of the state tree before the current block execution.
    """

    state_diff: StateDiff
    verkle_proof: VerkleProof
    # parent_state_root: Hash


class VerkleTree(RootModel[Dict[Hash, Hash]]):
    """
    Definition of a Verkle Tree.

    A Verkle Tree is a data structure used to efficiently prove the membership or non-membership
    of elements in a state. This class represents the Verkle Tree as a dictionary, where each key
    and value is a Hash (32 bytes). The root attribute holds this dictionary, providing a mapping
    of the tree's key/values.
    """

    root: Dict[Hash, Hash] = Field(default_factory=dict)


class WitnessCheck:
    """
    Definition of a Witness Check.

    Used as an intermediary class to store all the necessary items required to check
    during the filling process of a blockchain test.
    """

    version: int = 0

    class AccountHeaderEntry(Enum):
        """
        Represents all the data entries in an account header.
        """

        BASIC_DATA = 0
        CODEHASH = 1

    def __init__(self) -> None:
        """
        Initializes a WitnessCheck instance.
        """
        self.account_entries: List[
            Tuple[Address, WitnessCheck.AccountHeaderEntry, Optional[Hash]]
        ] = []
        self.storage_slots: List[Tuple[Address, int, Optional[Hash]]] = []
        self.code_chunks: List[Tuple[Address, int, Optional[Hash]]] = []

    def __repr__(self) -> str:
        """
        Provides a detailed string representation of the WitnessCheck object for debugging.
        """
        return (
            f"WitnessCheck(\n"
            f"  account_entries={self.account_entries},\n"
            f"  storage_slots={self.storage_slots},\n"
            f"  code_chunks={self.code_chunks}\n"
            f")"
        )

    def add_account_full(self, address: Address, account: Account | None) -> None:
        """
        Adds the address, nonce, balance, and code. Delays actual key computation until later.
        """
        self.add_account_basic_data(address, account)
        if account and account.code:
            code_hash = Hash(keccak256(account.code).digest())
            self.add_account_codehash(address, code_hash)

    def add_account_basic_data(self, address: Address, account: Account | None) -> None:
        """
        Adds the basic data witness for the given address.
        """
        if account is None:
            self.account_entries.append(
                (address, WitnessCheck.AccountHeaderEntry.BASIC_DATA, None)
            )
        else:  # Use big-endian encoding for basic data items
            basic_data_value = bytearray(32)

            # Set version to 0 (1 byte at offset 0)
            basic_data_value[0] = self.version

            # Bytes 1..4 are reserved for future use, leave them as 0

            # Set code_size (3 bytes at offset 5)
            code_size_bytes = len(account.code).to_bytes(3, byteorder="big")
            basic_data_value[5:8] = code_size_bytes

            # Set nonce (8 bytes at offset 8)
            nonce_bytes = account.nonce.to_bytes(8, byteorder="big")
            basic_data_value[8:16] = nonce_bytes

            # Set balance (16 bytes at offset 16) - encode as big-endian
            balance_bytes = account.balance.to_bytes(16, byteorder="big")
            basic_data_value[16:32] = balance_bytes

            # Append the encoded basic data to account_entries
            self.account_entries.append(
                (
                    address,
                    WitnessCheck.AccountHeaderEntry.BASIC_DATA,
                    Hash(bytes(basic_data_value)),
                )
            )

    def add_account_codehash(self, address: Address, codehash: Optional[Hash]) -> None:
        """
        Adds the code hash witness for the given address.
        """
        self.account_entries.append((address, WitnessCheck.AccountHeaderEntry.CODEHASH, codehash))

    def add_storage_slot(self, address: Address, storage_slot: int, value: Optional[Hash]) -> None:
        """
        Adds the storage slot witness for the given address and storage slot.
        """
        self.storage_slots.append((address, storage_slot, value))

    def add_code_chunk(self, address: Address, chunk_number: int, value: Optional[Hash]) -> None:
        """
        Adds the code chunk witness for the given address and chunk number.
        """
        self.code_chunks.append((address, chunk_number, value))
