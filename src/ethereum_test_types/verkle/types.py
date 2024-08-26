"""
Useful Verkle types for generating Ethereum tests.
"""

from enum import Enum
from hashlib import sha3_256 as keccak256
from typing import Any, Dict, List, Optional

from pydantic import Field, RootModel, field_validator
from pydantic.functional_serializers import model_serializer

from ethereum_test_base_types import Address, CamelModel, HexNumber, PaddedFixedSizeBytes
from ethereum_test_types import Alloc
from evm_transition_tool import TransitionTool

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

    Used as an intermediary check between blocks to verify the correctness of the state transition.
    """

    # TODO: use this properly
    t8n = TransitionTool

    class AccountHeaderEntry(Enum):
        """
        Represents all the data entries in an account header.
        """

        BASIC_DATA = 0
        CODEHASH = 1

    def __init__(self) -> None:
        """
        A dictionary of witness key-values pairs to check against a witness state diff returned by
        the EVM transition tool.
        """
        self.witness_check: Dict[Hash, Hash | None] = {}

    def add_account_full(self, address: Address, account: Alloc, t8n: TransitionTool):
        """
        Adds the address, nonce, balance and code.
        """
        self.add_account_basic_data(address, account, t8n)
        account_data = account[address]
        if account_data and account_data.code:
            code_hash = Hash(keccak256(account_data.code).digest())
            self.add_account_codehash(address, code_hash, t8n)

    def add_account_basic_data(
        self, address: Address, account: Optional[Alloc], t8n: TransitionTool
    ):
        """
        Adds the basic data witness for the given address.
        """
        if account is None:
            self.witness_check[
                self._account_key(address, WitnessCheck.AccountHeaderEntry.BASIC_DATA, t8n)
            ] = None
            return
        # Placeholder: Encode basic data as little_endian based on the account table structure
        basic_data_value = Hash(0)
        self.witness_check[
            self._account_key(address, WitnessCheck.AccountHeaderEntry.BASIC_DATA, t8n)
        ] = basic_data_value

    def add_account_codehash(
        self, address: Address, codehash: Optional[Hash], t8n: TransitionTool
    ):
        """
        Adds the code hash witness for the given address.
        """
        self.witness_check[
            self._account_key(address, WitnessCheck.AccountHeaderEntry.CODEHASH, t8n)
        ] = codehash

    def add_storage_slot(
        self, address: Address, storage_slot: HexNumber, value: Optional[Hash], t8n: TransitionTool
    ):
        """
        Adds the storage slot witness for the given address and storage slot.
        """
        tree_key = self._storage_key(address, storage_slot, t8n)
        self.witness_check[tree_key] = value

    def add_code_chunk(
        self, address: Address, chunk_number: HexNumber, value: Optional[Hash], t8n: TransitionTool
    ):
        """
        Adds the code chunk witness for the given address and chunk number.
        """
        tree_key = self._code_chunk_key(address, chunk_number, t8n)
        self.witness_check[tree_key] = value

    def _account_key(
        self, address: Address, entry: AccountHeaderEntry, t8n: TransitionTool
    ) -> Hash:
        """
        Returns a VerkleTree key for the address and account header entry.
        """
        tree_key_str = t8n.get_verkle_single_key(address)
        tree_key = bytearray.fromhex(tree_key_str[2:])
        entry_bytes = entry.value.to_bytes(2, byteorder="big")
        tree_key[-2:] = entry_bytes
        return Hash(bytes(tree_key))

    def _storage_key(self, address: Address, storage_slot: HexNumber, t8n: TransitionTool) -> Hash:
        """
        Returns a VerkleTree key for the storage of a given address.
        """
        storage_tree_key = t8n.get_verkle_single_key(address, storage_slot)
        return Hash(storage_tree_key)

    def _code_chunk_key(
        self, address: Address, code_chunk: HexNumber, t8n: TransitionTool
    ) -> Hash:
        """
        Returns a VerkleTree key for the code chunk number of a given address.
        """
        code_chunk_tree_key = t8n.get_verkle_code_chunk_key(address, code_chunk)
        return Hash(code_chunk_tree_key)
