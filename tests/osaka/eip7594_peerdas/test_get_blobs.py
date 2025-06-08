"""
abstract: Tests get blobs engine endpoint for [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594)
    Test get blobs engine endpoint for [EIP-7594: PeerDAS - Peer Data Availability Sampling](https://eips.ethereum.org/EIPS/eip-7594).

"""  # noqa: E501

from typing import List, Optional

import pytest
from hive.client import ClientType

from ethereum_test_forks import Fork, Osaka
from ethereum_test_tools import (
    Address,
    Alloc,
    Blob,
    BlobsTestFiller,
    NetworkWrappedTransaction,
    Transaction,
)

from ...cancun.eip4844_blobs.common import INF_POINT
from ...cancun.eip4844_blobs.spec import Spec as Spec4844
from ...cancun.eip4844_blobs.spec import SpecHelpers, ref_spec_4844

CELLS_PER_EXT_BLOB = 128

REFERENCE_SPEC_GIT_PATH = ref_spec_4844.git_path
REFERENCE_SPEC_VERSION = ref_spec_4844.version


@pytest.fixture
def destination_account(pre: Alloc) -> Address:
    """Destination account for the blob transactions."""
    return pre.fund_eoa(amount=0)


@pytest.fixture
def tx_value() -> int:
    """
    Value contained by the transactions sent during test.

    Can be overloaded by a test case to provide a custom transaction value.
    """
    return 1


@pytest.fixture
def tx_gas() -> int:
    """Gas allocated to transactions sent during test."""
    return 21_000


@pytest.fixture
def tx_calldata() -> bytes:
    """Calldata in transactions sent during test."""
    return b""


@pytest.fixture(autouse=True)
def parent_excess_blobs() -> int:
    """
    Excess blobs of the parent block.

    Can be overloaded by a test case to provide a custom parent excess blob
    count.
    """
    return 10  # Defaults to a blob gas price of 1.


@pytest.fixture(autouse=True)
def parent_blobs() -> int:
    """
    Blobs of the parent blob.

    Can be overloaded by a test case to provide a custom parent blob count.
    """
    return 0


@pytest.fixture
def excess_blob_gas(
    fork: Fork,
    parent_excess_blobs: int | None,
    parent_blobs: int | None,
) -> int | None:
    """
    Calculate the excess blob gas of the block under test from the parent block.

    Value can be overloaded by a test case to provide a custom excess blob gas.
    """
    if parent_excess_blobs is None or parent_blobs is None:
        return None
    excess_blob_gas = fork.excess_blob_gas_calculator()
    return excess_blob_gas(
        parent_excess_blobs=parent_excess_blobs,
        parent_blob_count=parent_blobs,
    )


@pytest.fixture
def blob_gas_price(
    fork: Fork,
    excess_blob_gas: int | None,
) -> int | None:
    """Return blob gas price for the block of the test."""
    if excess_blob_gas is None:
        return None

    get_blob_gas_price = fork.blob_gas_price_calculator()
    return get_blob_gas_price(
        excess_blob_gas=excess_blob_gas,
    )


@pytest.fixture
def txs_versioned_hashes(txs_blobs: List[List[Blob]]) -> List[List[bytes]]:
    """List of blob versioned hashes derived from the blobs."""
    return [[blob.versioned_hash() for blob in blob_tx] for blob_tx in txs_blobs]


@pytest.fixture
def tx_max_fee_per_blob_gas(  # noqa: D103
    blob_gas_price: Optional[int],
) -> int:
    """
    Max fee per blob gas for transactions sent during test.

    By default, it is set to the blob gas price of the block.

    Can be overloaded by a test case to test rejection of transactions where
    the max fee per blob gas is insufficient.
    """
    if blob_gas_price is None:
        # When fork transitioning, the default blob gas price is 1.
        return 1
    return blob_gas_price


@pytest.fixture
def tx_wrapper_version() -> int | None:
    """Return wrapper version used for the transactions sent during test."""
    return 1


@pytest.fixture
def txs_blobs(id_matcher) -> List[List[Blob]]:
    """Extract blobs from the resolved test case."""
    return id_matcher.values[0]


@pytest.fixture(autouse=True)
def txs(
    pre: Alloc,
    destination_account: Optional[Address],
    tx_gas: int,
    tx_value: int,
    tx_calldata: bytes,
    tx_max_fee_per_blob_gas: int,
    txs_versioned_hashes: List[List[bytes]],
    txs_blobs: List[List[Blob]],
    tx_wrapper_version: int | None,
) -> List[NetworkWrappedTransaction | Transaction]:
    """Prepare the list of transactions that are sent during the test."""
    if len(txs_blobs) != len(txs_versioned_hashes):
        raise ValueError("txs_blobs and txs_versioned_hashes should have the same length")
    txs: List[NetworkWrappedTransaction | Transaction] = []
    for tx_blobs, tx_versioned_hashes in zip(txs_blobs, txs_versioned_hashes, strict=False):
        tx = Transaction(
            ty=Spec4844.BLOB_TX_TYPE,
            sender=pre.fund_eoa(),
            to=destination_account,
            value=tx_value,
            gas_limit=tx_gas,
            data=tx_calldata,
            max_fee_per_blob_gas=tx_max_fee_per_blob_gas,
            access_list=[],
            blob_versioned_hashes=tx_versioned_hashes,
        )
        network_wrapped_tx = NetworkWrappedTransaction(
            tx=tx,
            blobs=tx_blobs,
            wrapper_version=tx_wrapper_version,
        )
        txs.append(network_wrapped_tx)
    return txs


def get_max_blobs_per_tx(fork: Fork, client_type: Optional[ClientType] = None) -> int:
    """Get max blobs per tx considering both fork and client."""
    # https://github.com/ethereum/go-ethereum/issues/31792
    # https://github.com/ethereum/go-ethereum/pull/31837
    if client_type and "go-ethereum" in client_type.name and fork >= Osaka:
        return 7
    return fork.max_blobs_per_block()


def generate_full_blob_tests(
    fork: Fork,
    client_type: Optional[ClientType] = None,
) -> List:
    """
    Return a list of tests for invalid blob transactions due to insufficient max fee per blob gas
    parametrized for each different fork.
    """
    blob_size = Spec4844.FIELD_ELEMENTS_PER_BLOB * SpecHelpers.BYTES_PER_FIELD_ELEMENT
    max_blobs_per_block = fork.max_blobs_per_block()
    max_blobs_per_tx = get_max_blobs_per_tx(fork, client_type)
    return [
        pytest.param(
            [  # Txs
                [  # Blobs per transaction
                    Blob(
                        data=bytes(blob_size),
                        kzg_commitment=INF_POINT,
                        kzg_cell_proofs=[INF_POINT] * CELLS_PER_EXT_BLOB,
                    ),
                ]
            ],
            id="single_blob_transaction",
        ),
        pytest.param(
            [  # Txs
                [  # Blobs per transaction
                    Blob(
                        data=bytes(blob_size),
                        kzg_commitment=INF_POINT,
                        kzg_cell_proofs=[INF_POINT] * CELLS_PER_EXT_BLOB,
                    )
                    for _ in range(max_blobs_per_tx)
                ]
            ],
            id="max_blobs_transaction",
        ),
        pytest.param(
            [  # Txs
                [  # Blobs per transaction
                    Blob(
                        data=bytes(blob_size),
                        kzg_commitment=INF_POINT,
                        kzg_cell_proofs=[INF_POINT] * CELLS_PER_EXT_BLOB,
                    )
                ]
                for _ in range(max_blobs_per_block)
            ],
            id="single_blob_max_txs",
        ),
    ]


@pytest.fixture
def id_matcher(request, fork: Fork, client_type: ClientType):
    """
    Match test case ID to actual test case for client aware test execution.
    This runs at test execution time when we have access to both the fork and client type.
    """
    requested_id = request.param
    all_test_cases = generate_full_blob_tests(fork, client_type)
    for test_case in all_test_cases:
        if test_case.id == requested_id:
            return test_case
    raise ValueError(f"Test case {requested_id} not found")


@pytest.mark.parametrize(
    "id_matcher",
    [
        "single_blob_transaction",
        "max_blobs_transaction",
        "single_blob_max_txs",
    ],
    indirect=True,
)
@pytest.mark.valid_from("Cancun")
def test_get_blobs(
    blobs_test: BlobsTestFiller,
    pre: Alloc,
    txs: List[NetworkWrappedTransaction | Transaction],
):
    """
    Test valid blob combinations where one or more txs in the block
    serialized version contain a full blob (network version) tx.
    """
    blobs_test(pre=pre, txs=txs)
