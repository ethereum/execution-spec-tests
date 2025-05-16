"""Common constants, classes & functions local to EIP-4844 tests."""

from typing import List, Literal, Tuple

from ethereum_test_types.blob import Blob

from .spec import Spec, ref_spec_4844

INF_POINT = (0xC0 << 376).to_bytes(48, byteorder="big")
Z = 0x623CE31CF9759A5C8DAF3A357992F9F3DD7F9339D8998BC8E68373E54F00B75E
Z_Y_INVALID_ENDIANNESS: Literal["little", "big"] = "little"
Z_Y_VALID_ENDIANNESS: Literal["little", "big"] = "big"


def blobs_to_transaction_input(
    input_blobs: List[Blob],
) -> Tuple[List[bytes], List[bytes], List[bytes]]:
    """
    Return tuple of lists of blobs, kzg commitments formatted to be added to a network blob
    type transaction.
    """
    blobs: List[bytes] = []
    kzg_commitments: List[bytes] = []
    kzg_proofs: List[bytes] = []

    for blob in input_blobs:
        blobs.append(blob.data)
        kzg_commitments.append(blob.commitment)
        kzg_proofs.append(blob.proof)
    return (blobs, kzg_commitments, kzg_proofs)
