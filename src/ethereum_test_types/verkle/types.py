"""
Useful Verkle types for generating Ethereum tests.
"""

from typing import Dict, List

from pydantic import Field, RootModel, field_validator

from ethereum_test_base_types import CamelModel, HexNumber, PaddedFixedSizeBytes

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
    current_value: Hash | None = Field(default_factory=None)
    new_value: Hash | None = Field(default_factory=None)


class StemStateDiff(CamelModel):
    """
    Definition of a Stem State Difference.

    Represents the state difference for a specific stem in a Verkle tree.
    Includes a list of differences for its suffixes.
    """

    stem: Hash
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
