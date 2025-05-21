"""
abstract: Tests [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594)
    Tests [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594).
"""  # noqa: E501

import random
import sys
from enum import Enum
from hashlib import sha256
from os.path import abspath, dirname, join, realpath
from pathlib import Path
from typing import List

import ckzg

from ethereum_test_base_types.base_types import Bytes, Hash
from ethereum_test_base_types.pydantic import CamelModel

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))  # TODO: find better workaround
from tests.osaka.eip7594_peerdas.spec import Spec, ref_spec_7594

TRUSTED_SETUP_FILE_NAME = "blob_trusted_setup.txt"
TRUSTED_SETUP_PATH = Path(realpath(__file__)).parent / TRUSTED_SETUP_FILE_NAME
TRUSTED_SETUP = ckzg.load_trusted_setup(str(TRUSTED_SETUP_PATH), 0)
print(f"{TRUSTED_SETUP_FILE_NAME} has been loaded")

REFERENCE_SPEC_GIT_PATH = ref_spec_7594.git_path
REFERENCE_SPEC_VERSION = ref_spec_7594.version


def get_eest_root_folder(marker_files=("pyproject.toml", ".git", "tests", "src")) -> Path:
    """Search for a folder where all files/folders listed above exist (root of project)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if all((parent / marker).exists() for marker in marker_files):
            return parent
    raise RuntimeError("Project root folder of execution-spec-tests was not found")


eest_root = get_eest_root_folder()


class Blob(CamelModel):
    """Class representing a full blob."""

    data: Bytes
    commitment: Bytes
    proof: List[Bytes] | Bytes  # Bytes < Osaka, List[Bytes] >= Osaka
    cells: List[Bytes] | None  # None (in json: null)  < Osaka, List[Bytes] >= Osaka

    versioned_hash: Hash
    name: str  # blob_<fork>_<seed>
    fork: str
    seed: int
    timestamp: int

    @staticmethod
    def get_filepath(fork: str, seed: int):
        """Return the Path to the blob that would be created with these parameters."""
        would_be_filename: str = "blob_" + fork + "_" + str(seed) + ".json"
        assert fork in ["cancun", "prague", "osaka"], f"Fork {fork} not implemented yet"

        if fork == "osaka":
            would_be_static_blob_path: Path = (
                eest_root
                / "tests"
                / "osaka"
                / "eip7594_peerdas"
                / "static_blobs"
                / would_be_filename
            )
        elif fork == "prague":
            would_be_static_blob_path = (
                eest_root / "tests" / "prague" / "static_blobs" / would_be_filename
            )
        elif fork == "cancun":
            would_be_static_blob_path = (
                eest_root
                / "tests"
                / "cancun"
                / "eip4844_blobs"
                / "static_blobs"
                / would_be_filename
            )
        return would_be_static_blob_path

    @staticmethod
    def NewBlob(fork: str, seed: int = 0, timestamp: int = 0) -> "Blob":  # noqa: N802
        """Construct Blob instances. Fork-specific logic is encapsulated within nested functions."""  # noqa: E501
        # if this blob already exists then load from file
        blob_location: Path = Blob.get_filepath(fork, seed)
        if blob_location.exists():
            print(f"Blob exists already, reading it from file {blob_location}")
            return Blob.LoadBlobFromFile(str(blob_location))

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
            seed=seed,
            timestamp=timestamp,
        )

    @staticmethod
    def LoadBlobFromFile(file_path: str) -> "Blob":  # noqa: N802
        """Read a .json file and reconstruct object it represents. You can load a blob either via just filename or via absolute path or via relative path (cwd is ./src/ethereum_test_types)."""  # noqa: E501
        if ".json" not in file_path:
            file_path = file_path + ".json"

        # determine whether user passed only filename or entire path
        if file_path.startswith("blob_"):
            parts = file_path.split("_")
            detected_fork = parts[1]
            detected_seed = parts[2].removesuffix(".json")
            assert detected_seed.isdigit(), (
                f"Failed to extract seed from filename. Ended up with seed {detected_seed} given filename {file_path}"  # noqa: E501
            )
            file_path = Blob.get_filepath(detected_fork, int(detected_seed))

        assert Path(file_path).exists(), (
            f"Tried to load static blob from file but {file_path} does not exist"
        )

        with open(file_path, "r", encoding="utf-8") as f:
            json_str: str = f.read()

        # reconstruct object
        return Blob.model_validate_json(json_str)

    def write_to_file(self):
        """Take a blob object, serialize it and write it to disk as json."""
        json_str = self.model_dump_json()
        output_location = Blob.get_filepath(self.fork, self.seed)

        # warn if existing static_blob gets overwritten
        if output_location.exists():
            print(f"Blob {output_location} already exists. It will be overwritten.")

        with open(output_location, "w", encoding="utf-8") as f:  # overwrite existing
            f.write(json_str)

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


# TODO: instead of defining fork via string pass fork object and derive string
# TODO: generate 10 static blobs for osaka, and 10 for cancun/prague, location is folder of respective eips
# TODO: remove uv lock and pyproject.toml changes from this PR, then make separate pr for adding czkg dependency
# TODO: update test_blob_txs_full.py to make use of actual blobs

# fork: str = "prague"
myseed: int = 1337  # fork+seed is the unique ID of a blob
b: Blob = Blob.NewBlob("prague", myseed)
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
    "blob_" + "prague" + "_" + str(myseed)
)  # or just put filename blob_osaka_1337
assert b.data == c.data
assert b.commitment == c.commitment
assert b.proof == c.proof
assert b.cells == c.cells
assert b.versioned_hash == c.versioned_hash
assert b.name == c.name
assert b.fork == c.fork
assert b.timestamp == c.timestamp

e: Blob = Blob.NewBlob("prague", myseed)
print("Line above should say blob already existed and was loaded from file")
f: Blob = Blob.NewBlob("cancun", myseed)
f.write_to_file()
g: Blob = Blob.NewBlob("cancun", myseed)
print("Line above should say blob already existed and was loaded from file")
h: Blob = Blob.NewBlob("osaka", myseed)
h.write_to_file()
zz: Blob = Blob.NewBlob("osaka", myseed)
print("Line above should say blob already existed and was loaded from file")

# you can load a blob either via just filename or via absolute path or via relative path (cwd is ./src/ethereum_test_types)  # noqa: E501
yyy: Blob = Blob.LoadBlobFromFile("blob_cancun_1337.json")
# yyyy: Blob = Blob.LoadBlobFromFile(
#     "/home/user/Documents/execution-spec-tests/tests/cancun/eip4844_blobs/static_blobs/blob_cancun_1337.json"  # noqa: E501
# )  # you must replace user with ur actual username as $USER not supported here
yyyyy: Blob = Blob.LoadBlobFromFile(
    "../../tests/cancun/eip4844_blobs/static_blobs/blob_cancun_1337.json"
)


# # test proof corruption
# #   osaka
# d: Blob = Blob.NewBlob("osaka", seed + 10)
# oldValue = d.proof[0][5]
# for m in Blob.ProofCorruptionMode:
#     d.corrupt_proof(m)
# print("proof corruption works (osaka):", oldValue != d.proof[0][5])
# #   prague
# e: Blob = Blob.NewBlob("prague", seed + 11)
# oldValue = e.proof[5]
# for m in Blob.ProofCorruptionMode:
#     e.corrupt_proof(m)
# print("proof corruption works (prague):", oldValue != e.proof[5])
print("pydantic model works")

# ckzg.compute_cells(blob, TRUSTED_SETUP) returns a list of length 128
# ckzg.compute_cells_and_kzg_proofs(blob, TRUSTED_SETUP)
