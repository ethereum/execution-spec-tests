"""
abstract: Tests [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594)
    Tests [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594).
"""  # noqa: E501
import math

import ckzg

from .spec import Spec, ref_spec_7594

REFERENCE_SPEC_GIT_PATH = ref_spec_7594.git_path
REFERENCE_SPEC_VERSION = ref_spec_7594.version

def bytes_from_hex(hex_string):
    """Convert a hex string to bytes."""
    return bytes.fromhex(hex_string.replace("0x", ""))

def generate_blob_from_hex_byte(hex_byte: str) -> bytes | None:
    """Take a singular hex byte string and return a valid blob built from this byte."""
    # preparation (remove 0x if present)
    if "0x" in hex_byte:
        hex_byte = hex_byte.replace("0x", "", 1)

    # validity checks
    if len(hex_byte) != 2:
        print("You should have passed a singular hex byte like e.g. fe to this function")
        return None

    if int(hex_byte, 16) > 115:
        # TODO: figure out why this happens
        print("For some reason bytes larger than this will lead to errors later in compute_cells(), so it's not allowed for now.")  # noqa: E501
        return None

    hex_byte = hex_byte.lower()

    valid_chars = "0123456789abcdef"
    if (hex_byte[0] not in valid_chars) or (hex_byte[1] not in valid_chars):
        print("You should have passed a singular hex byte consisting of only two chars in 0-9 and a-f like e.g. fe to this function")  # noqa: E501
        return None


    # create blob
    exp = int(math.log2(Spec.BYTES_PER_BLOB))
    blob_string: str = "0x" + hex_byte * (2**exp)
    blob: bytes = bytes_from_hex(blob_string)

    return blob


def eest_blob_to_kzg_commitment(blob: bytes) -> bytes:
    """Take a blob and returns a cryptographic commitment to it. Note: Each cell seems to hold a copy of this commitment."""  # noqa: E501
    # sanity check
    expected_blob_length = 2**int(math.log2(Spec.BYTES_PER_BLOB))
    assert len(blob) == expected_blob_length, f"Expected blob of length {expected_blob_length} but got blob of length {len(blob)}"  # noqa: E501

    # calculate commitment
    ts = ckzg.load_trusted_setup("trusted_setup.txt", 0)
    commitment = ckzg.blob_to_kzg_commitment(blob, ts)

    assert len(commitment) == Spec.KZG_COMMITMENT_LENGTH, f"Expected {Spec.KZG_COMMITMENT_LENGTH} resulting commitments but got {len(commitment)} commitments"  # noqa: E501

    return commitment


def eest_compute_cells(blob: bytes) -> list[int]:
    """Take a blob and returns a list of cells that are derived from this blob."""
    ts = ckzg.load_trusted_setup("trusted_setup.txt", 0)

    cells = ckzg.compute_cells(blob, ts)

    assert len(cells) == 128

    return cells


def eest_compute_cells_and_kzg_proofs(blob: bytes) -> tuple[list[int], list[int]]:
    """Take a blob and returns a list of cells and a list of proofs derived from this blob."""
    ts = ckzg.load_trusted_setup("trusted_setup.txt", 0)

    cells, proofs = ckzg.compute_cells_and_kzg_proofs(blob, ts) # both returns are of type list

    assert len(cells) == 128
    assert len(proofs) == 128

    return cells, proofs


def eest_verify_cell_kzg_proof_batch(commitment: bytes, cell_indices: list, cells: list, proofs: list) -> bool:  # noqa: E501
    """Check whether all cell proofs are valid and returns True only if that is the case."""
    ts = ckzg.load_trusted_setup("trusted_setup.txt", 0)

    # sanity check
    assert len(cell_indices) == len(cells), f"Cell Indices list (detected length {len(cell_indices)}) and Cell list (detected length {len(cells)}) should have same length."  # noqa: E501

    # each cell refers to the same commitment
    commitments = [commitment] * len(cell_indices)

    is_valid = ckzg.verify_cell_kzg_proof_batch(commitments, cell_indices, cells, proofs, ts)

    return is_valid

# our equivalent of ckzg test_recover_cells_and_kzg_proofs
def eest_delete_cells_then_recover_them(cells: list[int], proofs: list[int], deletion_indices: list[int]):  # noqa: E501
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
    ts = ckzg.load_trusted_setup("trusted_setup.txt", 0)
    recovered_cells, recovered_proofs = ckzg.recover_cells_and_kzg_proofs(remaining_indices, remaining_cells, ts) # on success returns two lists of len 128  # noqa: E501

    # determine success/failure
    assert len(recovered_cells) == len(cells), f"Failed to recover cell list. Original cell list had length {len(cells)} but recovered cell list has length {len(recovered_cells)}"  # noqa: E501
    assert len(recovered_proofs) == len(proofs), f"Failed to recover proofs list. Original proofs list had length {len(proofs)} but recovered proofs list has length {len(recovered_proofs)}"  # noqa: E501

    for i in range(len(recovered_cells)):
        assert cells[i] == recovered_cells[i], f"Failed to correctly restore missing cells. At index {i} original cell was {cells[i]} but reconstructed cell does not match: {recovered_cells[i]}"  # noqa: E501
        assert proofs[i] == recovered_proofs[i], f"Failed to correctly restore missing proofs. At index {i} original proof was {proofs[i]} but reconstructed proof does not match: {recovered_proofs[i]}"  # noqa: E501

    # print("Successful reconstruction")


""" Example Usage
my_byte = "42" # 0x73 (115) or lower works, 0x74 (116) or higher fails
# generate blob
blob: bytes = generate_blob_from_hex_byte(my_byte)
# get cells and proofs
cells, proofs = eest_compute_cells_and_kzg_proofs(blob)
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
