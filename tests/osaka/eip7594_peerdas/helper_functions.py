"""
abstract: Tests [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594)
    Tests [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594).
"""  # noqa: E501
import base64 as b64
import json
from os.path import realpath
from pathlib import Path
from random import randrange, seed

import ckzg
from spec import Spec, ref_spec_7594

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
    seed(rng_seed)

    # generate blob
    ints: list[int] = [randrange(Spec.BLS_MODULUS) for _ in range(Spec.FIELD_ELEMENTS_PER_BLOB)]            # len: 4096  # noqa: E501
    encoded: list[bytes] = [i.to_bytes(Spec.BYTES_PER_FIELD_ELEMENT, Spec.KZG_ENDIANNESS) for i in ints]    # len: 4096  # noqa: E501
    blob: bytes = b"".join(encoded) # without 0x

    return blob

def eest_blob_to_kzg_commitment(blob: bytes) -> bytes:
    """Take a blob and returns a cryptographic commitment to it. Note: Each cell seems to hold a copy of this commitment."""  # noqa: E501
    # sanity check
    assert len(blob) == Spec.BYTES_PER_BLOB, f"Expected blob of length {Spec.BYTES_PER_BLOB} but got blob of length {len(blob)}"  # noqa: E501

    # calculate commitment
    commitment = ckzg.blob_to_kzg_commitment(blob, TRUSTED_SETUP)

    assert len(commitment) == Spec.BYTES_PER_COMMITMENT, f"Expected {Spec.BYTES_PER_COMMITMENT} resulting commitments but got {len(commitment)} commitments"  # noqa: E501

    return commitment

def eest_verify_cell_kzg_proof_batch(commitment: bytes, cell_indices: list, cells: list, proofs: list) -> bool:  # noqa: E501
    """Check whether all cell proofs are valid and returns True only if that is the case."""
    # sanity check
    assert len(cell_indices) == len(cells), f"Cell Indices list (detected length {len(cell_indices)}) and Cell list (detected length {len(cells)}) should have same length."  # noqa: E501

    # each cell refers to the same commitment
    commitments: list[bytes] = [commitment] * len(cell_indices)

    is_valid = ckzg.verify_cell_kzg_proof_batch(commitments, cell_indices, cells, proofs, TRUSTED_SETUP)  # noqa: E501

    return is_valid

# our equivalent of ckzg test_recover_cells_and_kzg_proofs
def eest_delete_cells_then_recover_them(cells: list[bytes], proofs: list[bytes], deletion_indices: list[int]):  # noqa: E501
    """
    Simulate the cell recovery process in user-specified scenario.

    Note: Requirement for successful reconstruction is having at least N of the 2N cells.

    Theoretical Usage: You pass a cell list with to 128 elements to this function along with a list of deletion indices.
    These cells will be deleted and then the ckzg recovery mechanism is used to repair the missing cells.
    If no assertion is triggered the reconstruction was successful.
    """  # noqa: E501
    # sanity checks
    assert len(cells) == 128, f"You are supposed to pass a full cell list with 128 elements to this function, but got list of length {len(cells)}"  # noqa: E501

    assert len(deletion_indices) < 129, f"You can't delete more than every cell (max len of deletion indices list is 128), but you passed a deletion indices list of length {len(deletion_indices)}"  # noqa: E501
    for i in deletion_indices:
        assert 0 <= i <= 127, f"Expected integers in range [0, 127], but got: {i}"

    # delete cells
    all_cell_indices: list[int] = list(range(128))
    remaining_indices: list[int] = [i for i in all_cell_indices if i not in deletion_indices]
    remaining_cells = [c for i, c in enumerate(cells) if i not in deletion_indices]

    # print(f"Cells: {cells}\nDeletion Indices: {deletion_indices}\nRemaining indices: {remaining_indices}\nRemaining cells: {remaining_cells}")  # noqa: E501

    # try to reconstruct cells
    recovered_cells, recovered_proofs = ckzg.recover_cells_and_kzg_proofs(remaining_indices, remaining_cells, TRUSTED_SETUP) # on success returns two lists of len 128  # noqa: E501

    # determine success/failure
    assert len(recovered_cells) == len(cells), f"Failed to recover cell list. Original cell list had length {len(cells)} but recovered cell list has length {len(recovered_cells)}"  # noqa: E501
    assert len(recovered_proofs) == len(proofs), f"Failed to recover proofs list. Original proofs list had length {len(proofs)} but recovered proofs list has length {len(recovered_proofs)}"  # noqa: E501

    for i in range(len(recovered_cells)):
        assert cells[i] == recovered_cells[i], f"Failed to correctly restore missing cells. At index {i} original cell was 0x{cells[i].hex()} but reconstructed cell does not match: 0x{recovered_cells[i].hex()}"  # noqa: E501
        assert proofs[i] == recovered_proofs[i], f"Failed to correctly restore missing proofs. At index {i} original proof was 0x{proofs[i].hex()} but reconstructed proof does not match: 0x{recovered_proofs[i].hex()}"  # noqa: E501

    # print("Successful reconstruction")

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
        b64_commitment_list: list[str] = [b64.b64encode(c).decode(self.encoding) for c in self.commitments]  # noqa: E501
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
        obj = cls(1337) # dummy object
        obj.name = data["name"]
        obj.blob = blob
        obj.commitments = commitments
        obj.cells = cells
        obj.proofs = proofs
        return obj

    def to_file(self):
        """Take an object, serialize it and write it to disk as json."""
        file_name: str = self.name + ".json"
        json_str: str = self.to_json()
        with open(file_name, "w", encoding=self.encoding) as f: # overwrite existing
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


for i in range(10):
    my_seed = i
    original = PersistentBlobGenerator(my_seed)
    json_str = original.to_json()
    restored = PersistentBlobGenerator.from_json(json_str)
    assert original.name == restored.name
    assert original.blob == restored.blob
    assert original.commitments == restored.commitments
    assert original.cells == restored.cells
    assert original.proofs == restored.proofs

    # write to file
    original.to_file()

    # read from file
    file_to_read = "blob_" + str(my_seed) + ".json"
    AnotherInstanceOfBlob: PersistentBlobGenerator = PersistentBlobGenerator.from_file(file_to_read)
    #       ensure object read from file matches original object
    assert original.name == AnotherInstanceOfBlob.name, f"Expected name {original.name} but got name {AnotherInstanceOfBlob.name}"
    assert original.blob == AnotherInstanceOfBlob.blob
    assert original.commitments == AnotherInstanceOfBlob.commitments
    assert original.cells == AnotherInstanceOfBlob.cells
    assert original.proofs == AnotherInstanceOfBlob.proofs

print("It works")

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

# - blob is now deterministically generated via seed
# - trusted_setup is only loaded once
# - rename constants to match deneb specs
# - removed two unnecessary wrapper functions
# - added read/write functions to class

# TODO: make PersistentBlobGenerator use a pydantic model
# TODO: uv lock

# ckzg.compute_cells(blob, TRUSTED_SETUP) returns a list of length 128
# ckzg.compute_cells_and_kzg_proofs(blob, TRUSTED_SETUP)
