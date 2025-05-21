"""
abstract: Tests [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594)
    Tests [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594).
"""  # noqa: E501

import base64 as b64
import json
import random
from enum import Enum
from hashlib import sha256
from os.path import realpath
from pathlib import Path
from typing import List

import ckzg
from spec import Spec, ref_spec_7594  # TODO: make .spec

from ethereum_test_base_types.base_types import Bytes, Hash
from ethereum_test_base_types.pydantic import CamelModel

TRUSTED_SETUP_FILE_NAME = "trusted_setup.txt"
TRUSTED_SETUP_PATH = Path(realpath(__file__)).parent / TRUSTED_SETUP_FILE_NAME
TRUSTED_SETUP = ckzg.load_trusted_setup(str(TRUSTED_SETUP_PATH), 0)

REFERENCE_SPEC_GIT_PATH = ref_spec_7594.git_path
REFERENCE_SPEC_VERSION = ref_spec_7594.version


def bytes_from_hex(hex_string):
    """Convert a hex string to bytes."""
    return bytes.fromhex(hex_string.replace("0x", ""))


def generate_blob_from_seed(rng_seed: int) -> bytes | None:
    """Take a seed and deterministically returns a valid blob generated from this seed."""
    # apply RNG seed
    random.seed(rng_seed)

    # generate blob
    ints: list[int] = [
        random.randrange(Spec.BLS_MODULUS) for _ in range(Spec.FIELD_ELEMENTS_PER_BLOB)
    ]  # len: 4096  # noqa: E501
    encoded: list[bytes] = [
        i.to_bytes(Spec.BYTES_PER_FIELD_ELEMENT, Spec.KZG_ENDIANNESS) for i in ints
    ]  # len: 4096  # noqa: E501
    blob: bytes = b"".join(encoded)  # without 0x

    return blob


def eest_blob_to_kzg_commitment(blob: bytes) -> bytes:
    """Take a blob and returns a cryptographic commitment to it. Note: Each cell seems to hold a copy of this commitment."""  # noqa: E501
    # sanity check
    assert len(blob) == Spec.BYTES_PER_BLOB, (
        f"Expected blob of length {Spec.BYTES_PER_BLOB} but got blob of length {len(blob)}"
    )

    # calculate commitment
    commitment = ckzg.blob_to_kzg_commitment(blob, TRUSTED_SETUP)

    assert len(commitment) == Spec.BYTES_PER_COMMITMENT, (
        f"Expected {Spec.BYTES_PER_COMMITMENT} resulting commitments but got {len(commitment)} commitments"  # noqa: E501
    )

    return commitment


def eest_verify_cell_kzg_proof_batch(
    commitment: bytes, cell_indices: list, cells: list, proofs: list
) -> bool:  # noqa: E501
    """Check whether all cell proofs are valid and returns True only if that is the case."""
    # sanity check
    assert len(cell_indices) == len(cells), (
        f"Cell Indices list (detected length {len(cell_indices)}) and Cell list (detected length {len(cells)}) should have same length."  # noqa: E501
    )

    # each cell refers to the same commitment
    commitments: list[bytes] = [commitment] * len(cell_indices)

    is_valid = ckzg.verify_cell_kzg_proof_batch(
        commitments, cell_indices, cells, proofs, TRUSTED_SETUP
    )

    return is_valid


# our equivalent of ckzg test_recover_cells_and_kzg_proofs
def eest_delete_cells_then_recover_them(
    cells: list[bytes], proofs: list[bytes], deletion_indices: list[int]
):  # noqa: E501
    """
    Simulate the cell recovery process in user-specified scenario.

    Note: Requirement for successful reconstruction is having at least N of the 2N cells.

    Theoretical Usage: You pass a cell list with to 128 elements to this function along with a list of deletion indices.
    These cells will be deleted and then the ckzg recovery mechanism is used to repair the missing cells.
    If no assertion is triggered the reconstruction was successful.
    """  # noqa: E501
    # sanity checks
    assert len(cells) == 128, (
        f"You are supposed to pass a full cell list with 128 elements to this function, but got list of length {len(cells)}"  # noqa: E501
    )

    assert len(deletion_indices) < 129, (
        f"You can't delete more than every cell (max len of deletion indices list is 128), but you passed a deletion indices list of length {len(deletion_indices)}"  # noqa: E501
    )
    for i in deletion_indices:
        assert 0 <= i <= 127, f"Expected integers in range [0, 127], but got: {i}"

    # delete cells
    all_cell_indices: list[int] = list(range(128))
    remaining_indices: list[int] = [i for i in all_cell_indices if i not in deletion_indices]
    remaining_cells = [c for i, c in enumerate(cells) if i not in deletion_indices]

    # try to reconstruct cells
    recovered_cells, recovered_proofs = ckzg.recover_cells_and_kzg_proofs(
        remaining_indices, remaining_cells, TRUSTED_SETUP
    )  # on success returns two lists of len 128  # noqa: E501

    # determine success/failure
    assert len(recovered_cells) == len(cells), (
        f"Failed to recover cell list. Original cell list had length {len(cells)} but recovered cell list has length {len(recovered_cells)}"  # noqa: E501
    )
    assert len(recovered_proofs) == len(proofs), (
        f"Failed to recover proofs list. Original proofs list had length {len(proofs)} but recovered proofs list has length {len(recovered_proofs)}"  # noqa: E501
    )

    for i in range(len(recovered_cells)):
        assert cells[i] == recovered_cells[i], (
            f"Failed to correctly restore missing cells. At index {i} original cell was 0x{cells[i].hex()} but reconstructed cell does not match: 0x{recovered_cells[i].hex()}"  # noqa: E501
        )
        assert proofs[i] == recovered_proofs[i], (
            f"Failed to correctly restore missing proofs. At index {i} original proof was 0x{proofs[i].hex()} but reconstructed proof does not match: 0x{recovered_proofs[i].hex()}"  # noqa: E501
        )


class PersistentBlobGenerator:
    """PersistentBlobGenerator takes an rng seed and returns a valid blob deterministically derived from it."""  # noqa: E501

    # e.g. PersistentBlobGenerator(42) creates blob_42.json in cwd and contains blob, commitment, cells and proofs. 42 stands for the rng seed used  # noqa: E501
    encoding: str = "utf-8"

    def __init__(self, rng_seed: int = 0):
        """Construct."""
        # safely derive blob from input
        blob: bytes | None = generate_blob_from_seed(rng_seed)
        assert blob is not None, f"PersistentBlobGenerator received invalid rng_seed: {rng_seed}"

        commitment: bytes = eest_blob_to_kzg_commitment(blob)
        cells, proofs = ckzg.compute_cells_and_kzg_proofs(blob, TRUSTED_SETUP)

        # populate instance
        self.name: str = "blob_" + str(rng_seed)
        self.blob: bytes = blob
        self.commitments: list[bytes] = [commitment] * len(cells)
        self.cells: list[bytes] = cells
        self.proofs: list[bytes] = proofs

    def to_json(self) -> str:
        """Convert object to json-compatible string."""
        # json does not support bytes, so we b64 encode these fields into strings
        #       blob: bytes -> str
        b64_blob_str: str = b64.b64encode(self.blob).decode(self.encoding)
        #       commitments: list[bytes] -> list[str]
        b64_commitment_list: list[str] = [
            b64.b64encode(c).decode(self.encoding) for c in self.commitments
        ]  # noqa: E501
        #       cells: list[bytes] -> list[str]
        b64_cell_list: list[str] = [b64.b64encode(c).decode(self.encoding) for c in self.cells]
        #       proofs: list[bytes] -> list[str]
        b64_proofs_list: list[str] = [b64.b64encode(c).decode(self.encoding) for c in self.proofs]

        json_dict = {
            "name": self.name,
            "b64_blob": b64_blob_str,
            "b64_commitments": b64_commitment_list,
            "b64_cells": b64_cell_list,
            "b64_proofs": b64_proofs_list,
        }

        return json.dumps(json_dict)

    @classmethod
    def from_json(cls, json_str: str) -> "PersistentBlobGenerator":
        """Take json and reconstruct blob it represents."""
        data = json.loads(json_str)

        # convert b64 blob back to bytes
        blob: bytes = b64.b64decode(data["b64_blob"])
        # convert b64 commitments back to list[bytes]
        commitments: list[bytes] = [b64.b64decode(s) for s in data["b64_commitments"]]
        # convert b64 cells back to list[bytes]
        cells: list[bytes] = [b64.b64decode(s) for s in data["b64_cells"]]
        # convert b64 proofs back to list[bytes]
        proofs: list[bytes] = [b64.b64decode(s) for s in data["b64_proofs"]]

        # get data
        obj = cls(1337)  # dummy object
        obj.name = data["name"]
        obj.blob = blob
        obj.commitments = commitments
        obj.cells = cells
        obj.proofs = proofs
        return obj

    def to_file(self):
        """Take an object, serialize it and write it to disk as json."""
        file_name = self.name + ".json"
        json_str = self.to_json()
        with open(file_name, "w", encoding=self.encoding) as f:  # overwrite existing
            f.write(json_str)

    @classmethod
    def from_file(cls, file_name: str) -> "PersistentBlobGenerator":
        """Read a .json file and reconstruct object it represents."""
        # read json
        with open(file_name, "r", encoding=cls.encoding) as f:
            json_str: str = f.read()

        # reconstruct object
        obj: PersistentBlobGenerator = cls.from_json(json_str)
        return obj


class Blob(CamelModel):
    """Class representing a full blob."""

    data: Bytes
    commitment: Bytes
    proof: List[Bytes] | Bytes  # Bytes < Osaka, List[Bytes] >= Osaka
    cells: List[Bytes] | None  # None (in json: null)  < Osaka, List[Bytes] >= Osaka

    versioned_hash: Hash
    name: str  # blob_<fork>_<seed>
    fork: str
    timestamp: int

    @staticmethod
    def NewBlob(fork: str, seed: int = 0, timestamp: int = 0) -> "Blob":  # noqa: N802
        """Construct Blob instances. Fork-specific logic is encapsulated within nested functions."""
        # TODO: if this blob already exists then load from file

        allowed_forks: List[str] = ["cancun", "prague", "osaka"]
        assert fork in allowed_forks, (
            f"You tried to generate a blob for fork {fork} but blobs only exists in: {allowed_forks}"  # noqa: E501
        )

        def generate_blob_data(rng_seed: int = 0) -> Bytes:
            """Calculate blob data deterministically via provided seed."""
            # apply RNG seed
            random.seed(rng_seed)

            # generate blob
            ints: list[int] = [
                random.randrange(Spec.BLS_MODULUS) for _ in range(Spec.FIELD_ELEMENTS_PER_BLOB)
            ]
            encoded: list[bytes] = [
                i.to_bytes(Spec.BYTES_PER_FIELD_ELEMENT, Spec.KZG_ENDIANNESS) for i in ints
            ]
            blob: bytes = b"".join(encoded)  # without 0x

            return Bytes(blob)

        def get_versioned_hash(commitment: Bytes, version: int = 1) -> Hash:
            """Calculate versioned hash for a given blob."""
            # TODO: is this in specs or made up by us? do we need it?
            return Hash(bytes([version]) + sha256(commitment).digest()[1:])

        def get_name(seed: int) -> str:
            """Derive blob name from the seed that generates its data."""
            return "blob_" + fork + "_" + str(seed)

        def get_commitment(data: Bytes) -> Bytes:
            """Take a blob and returns a cryptographic commitment to it. Note: Each cell seems to hold a copy of this commitment."""  # noqa: E501
            # sanity check
            assert len(data) == Spec.BYTES_PER_BLOB, (
                f"Expected blob of length {Spec.BYTES_PER_BLOB} but got blob of length {len(data)}"
            )

            # calculate commitment
            commitment = ckzg.blob_to_kzg_commitment(data, TRUSTED_SETUP)

            assert len(commitment) == Spec.BYTES_PER_COMMITMENT, (
                f"Expected {Spec.BYTES_PER_COMMITMENT} resulting commitments but got {len(commitment)} commitments"  # noqa: E501
            )

            return commitment

        def get_proof(data: Bytes) -> List[Bytes] | Bytes:
            if fork in ["cancun", "prague"]:
                z = 2  # 2 is one of many possible valid field elements z (https://github.com/ethereum/consensus-specs/blob/ad884507f7a1d5962cd3dfb5f7b3e41aab728c55/tests/core/pyspec/eth2spec/test/utils/kzg_tests.py#L58-L66)
                z_valid_size: bytes = z.to_bytes(Spec.BYTES_PER_FIELD_ELEMENT, byteorder="big")
                proof, _ = ckzg.compute_kzg_proof(data, z_valid_size, TRUSTED_SETUP)
                return proof

            if fork in ["osaka"]:
                _, proofs = ckzg.compute_cells_and_kzg_proofs(
                    data, TRUSTED_SETUP
                )  # returns List[byte] of length 128
                return proofs  # List[bytes] # TODO: how to convert List[bytes] to List[Bytes], do we even care about bytes vs Bytes?  # noqa: E501

            raise AssertionError(f"get_proof() has not been implemented yet for fork: {fork}")

        def get_cells(data: Bytes) -> List[Bytes] | None:
            if fork in ["cancun", "prague"]:
                return None

            if fork in ["osaka"]:
                cells, _ = ckzg.compute_cells_and_kzg_proofs(
                    data, TRUSTED_SETUP
                )  # returns List[byte] of length 128
                return cells  # List[bytes] # TODO: how to convert List[bytes] to List[Bytes]

            raise AssertionError(f"get_cells() has not been implemented yet for fork: {fork}")

        # populate blob fields
        data: Bytes = generate_blob_data(seed)
        commitment: Bytes = get_commitment(data)
        proof: List[Bytes] | Bytes = get_proof(data)
        cells: List[Bytes] | None = get_cells(data)
        versioned_hash: Hash = get_versioned_hash(commitment)
        name: str = get_name(seed)

        return Blob(
            data=data,
            commitment=commitment,
            proof=proof,
            cells=cells,
            versioned_hash=versioned_hash,
            name=name,
            fork=fork,
            timestamp=timestamp,
        )

    @staticmethod
    def LoadBlobFromFile(file_name: str) -> "Blob":  # noqa: N802
        """Read a .json file and reconstruct object it represents."""
        # TODO: file_name should match location defined in write_to_file
        if ".json" not in file_name:
            file_name = file_name + ".json"

        with open(file_name, "r", encoding="utf-8") as f:
            json_str: str = f.read()

        # reconstruct object
        return Blob.model_validate_json(json_str)

    def verify_cell_kzg_proof_batch(self, cell_indices: list) -> bool:  # noqa: E501
        """Check whether all cell proofs are valid and returns True only if that is the case."""
        assert self.fork in ["osaka"], (
            f"verify_cell_kzg_proof_batch() is not available for fork: {self.fork}"
        )

        assert self.cells is not None, ""  # TODO: write message

        assert len(cell_indices) == len(self.cells), (
            f"Cell Indices list (detected length {len(cell_indices)}) and Cell list (detected length {len(self.cells)}) should have same length."  # noqa: E501
        )

        # each cell refers to the same commitment
        commitments: list[bytes] = [self.commitment] * len(cell_indices)

        is_valid = ckzg.verify_cell_kzg_proof_batch(
            commitments, cell_indices, self.cells, self.proof, TRUSTED_SETUP
        )

        return is_valid

    def delete_cells_then_recover_them(self, deletion_indices: list[int]):
        """
        Simulate the cell recovery process in user-specified scenario.

        Note: Requirement for successful reconstruction is having at least N of the 2N cells.

        Theoretical Usage: You pass a cell list with to 128 elements to this function along with a list of deletion indices.
        These cells will be deleted and then the ckzg recovery mechanism is used to repair the missing cells.
        If no assertion is triggered the reconstruction was successful.
        """  # noqa: E501
        assert self.fork in ["osaka"], (
            f"delete_cells_then_recover_them() is not available for fork: {self.fork}"
        )

        assert self.cells is not None, "..."  # TODO: write text

        assert isinstance(self.proof, list), (
            "This function only works when self.proof is a list, but it seems to be of type bytes (not a list)"  # noqa: E501
        )

        assert len(self.cells) == 128, (
            f"You are supposed to pass a full cell list with 128 elements to this function, but got list of length {len(self.cells)}"  # noqa: E501
        )

        assert len(deletion_indices) < 129, (
            f"You can't delete more than every cell (max len of deletion indices list is 128), but you passed a deletion indices list of length {len(deletion_indices)}"  # noqa: E501
        )
        for i in deletion_indices:
            assert 0 <= i <= 127, f"Expected integers in range [0, 127], but got: {i}"

        # delete cells
        all_cell_indices: list[int] = list(range(128))
        remaining_indices: list[int] = [i for i in all_cell_indices if i not in deletion_indices]
        remaining_cells = [c for i, c in enumerate(self.cells) if i not in deletion_indices]

        recovered_cells, recovered_proofs = ckzg.recover_cells_and_kzg_proofs(
            remaining_indices, remaining_cells, TRUSTED_SETUP
        )  # on success returns two lists of len 128  # noqa: E501

        # determine success/failure
        assert len(recovered_cells) == len(self.cells), (
            f"Failed to recover cell list. Original cell list had length {len(self.cells)} but recovered cell list has length {len(recovered_cells)}"  # noqa: E501
        )
        assert len(recovered_proofs) == len(self.proof), (
            f"Failed to recover proofs list. Original proofs list had length {len(self.proof)} but recovered proofs list has length {len(recovered_proofs)}"  # noqa: E501
        )

        for i in range(len(recovered_cells)):
            assert self.cells[i] == recovered_cells[i], (
                f"Failed to correctly restore missing cells. At index {i} original cell was 0x{self.cells[i].hex()} but reconstructed cell does not match: 0x{recovered_cells[i].hex()}"  # noqa: E501
            )
            assert self.proof[i] == recovered_proofs[i], (
                f"Failed to correctly restore missing proofs. At index {i} original proof was 0x{self.proof[i].hex()} but reconstructed proof does not match: 0x{recovered_proofs[i].hex()}"  # noqa: E501
            )

    def write_to_file(self):
        """Take an object, serialize it and write it to disk as json."""
        # TODO: file_name should hold relative path instead of forcing cwd, e.g. if this is called from types.py where should blob be created?  # noqa: E501
        file_name = self.name + ".json"
        json_str = self.model_dump_json()
        with open(file_name, "w", encoding="utf-8") as f:  # overwrite existing
            f.write(json_str)

    class ProofCorruptionMode(Enum):
        """Define what the proof corruption modes do. For Osaka and later each Bytes object in the list is manipulated this way."""  # noqa: E501

        CORRUPT_FIRST_BYTE = 1  # corrupts a single byte (index 0)
        CORRUPT_LAST_BYTE = 2  # corrupts a single byte (last valid index)
        CORRUPT_TO_ALL_ZEROES = 3  # sets all proof bytes to 0
        CORRUPT_ALL_BYTES = 4  # corrupts all bytes

    def corrupt_proof(self, mode: ProofCorruptionMode):
        """Corrupt the proof field, supports different corruption modes."""

        def corrupt_byte(b: bytes) -> Bytes:
            """Bit-flip all bits of provided byte using XOR to guarantee change."""
            if len(b) != 1:
                raise ValueError("Input must be a single byte")
            return Bytes(bytes([b[0] ^ 0xFF]))

        # osaka and later
        if self.fork in ["osaka"]:
            assert isinstance(self.proof, list), (
                "proof was expected to be a list but it isn't"
            )  # make mypy happy

            if mode == self.ProofCorruptionMode.CORRUPT_FIRST_BYTE:
                for i in range(len(self.proof)):
                    b: Bytes = self.proof[i]
                    corrupted: Bytes = Bytes(corrupt_byte(b[:1]) + b[1:])
                    self.proof[i] = corrupted
            elif mode == self.ProofCorruptionMode.CORRUPT_LAST_BYTE:
                for i in range(len(self.proof)):
                    b = self.proof[i]
                    corrupted = Bytes(b[:-1] + corrupt_byte(b[-1:]))
                    self.proof[i] = corrupted
            elif mode == self.ProofCorruptionMode.CORRUPT_TO_ALL_ZEROES:
                for i in range(len(self.proof)):
                    self.proof[i] = Bytes(bytes(len(self.proof[i])))
            elif mode == self.ProofCorruptionMode.CORRUPT_ALL_BYTES:
                for i in range(len(self.proof)):
                    b = self.proof[i]
                    corrupted_bytes = Bytes(b"".join(corrupt_byte(bytes([byte])) for byte in b))
                    self.proof[i] = corrupted_bytes
            return

        # pre-osaka (cancun and prague)
        assert self.fork in ["cancun", "prague"], (
            f"You need to adjust corrupt_proof to handle fork {self.fork}"
        )
        assert isinstance(self.proof, Bytes), "proof was expected to be Bytes but it isn't"

        if mode == self.ProofCorruptionMode.CORRUPT_FIRST_BYTE:
            self.proof = Bytes(corrupt_byte(self.proof[:1]) + self.proof[1:])
        elif mode == self.ProofCorruptionMode.CORRUPT_LAST_BYTE:
            self.proof = Bytes(self.proof[:-1] + corrupt_byte(self.proof[-1:]))
        elif mode == self.ProofCorruptionMode.CORRUPT_TO_ALL_ZEROES:
            self.proof = Bytes(bytes(len(self.proof)))
        elif mode == self.ProofCorruptionMode.CORRUPT_ALL_BYTES:
            self.proof = Bytes(b"".join(corrupt_byte(bytes([byte])) for byte in self.proof))


# TODO: test corrupt_proof() for all modes and forks fusaka and <fusaka
# TODO: instead of defining fork via string pass fork object and derive string
# TODO: figure out how to have TRUSTED_LOAD be loaded only once per process but not whenever types is imported (maybe use typing ClassVar)
# TODO: move code into types folder, import blob in init.py, update filepath references to static blobs
# TODO: generate 10 static blobs for osaka, and 10 for cancun/prague, location is folder of respective eips
# TODO: in NewBlob: read existing static blob if fork+seed already blob already exists
# TODO: remove uv lock and pyproject.toml changes from this PR, then make separate pr for adding czkg dependency
# TODO: update test_blob_txs_full.py to make use of actual blobs

fork: str = "prague"
seed: int = 1337  # fork+seed is the unique ID of a blob
b: Blob = Blob.NewBlob(fork, seed)
json_str: str = b.model_dump_json()
restored: Blob = Blob.model_validate_json(json_str)
assert b.data == restored.data
assert b.commitment == restored.commitment
assert b.proof == restored.proof
assert b.cells == restored.cells
assert b.versioned_hash == restored.versioned_hash
assert b.name == restored.name
assert b.fork == restored.fork
assert b.timestamp == restored.timestamp
print(type(b.proof), len(b.proof))
print(Spec.BYTES_PER_FIELD_ELEMENT)
print(len(b.data))

b.write_to_file()
c: Blob = Blob.LoadBlobFromFile(
    "blob_" + fork + "_" + str(seed)
)  # or just put filename blob_osaka_1337
assert b.data == c.data
assert b.commitment == c.commitment
assert b.proof == c.proof
assert b.cells == c.cells
assert b.versioned_hash == c.versioned_hash
assert b.name == c.name
assert b.fork == c.fork
assert b.timestamp == c.timestamp
print("pydantic model works")


""" Example Usage
# generate blob
blob: bytes | None = generate_blob_from_seed(5)
assert blob is not None, "blob is None"
# get cells and proofs
cells, proofs = ckzg.compute_cells_and_kzg_proofs(blob, TRUSTED_SETUP)
# delete some cells and recover them again
deletion_indices: list[int] = [5, 42, 100]
eest_delete_cells_then_recover_them(cells, proofs, deletion_indices)
# get commitment
commitment: bytes = eest_blob_to_kzg_commitment(blob)
# verify all cell proofs
my_cell_indices: list[int] = list(range(128))
# change byte at index 8 to a different value (e.g. 3a) to ensure that verification now fails
#commitment = bytes((lambda b: (b.__setitem__(8, 0x3a), b)[1])(bytearray(commitment)))
is_valid = eest_verify_cell_kzg_proof_batch(commitment, my_cell_indices, cells, proofs)
print("Success")
"""

# ckzg.compute_cells(blob, TRUSTED_SETUP) returns a list of length 128
# ckzg.compute_cells_and_kzg_proofs(blob, TRUSTED_SETUP)
