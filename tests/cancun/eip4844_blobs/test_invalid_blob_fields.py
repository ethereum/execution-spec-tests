"""
abstract: Tests invalid blob fields in [EIP-4844: Shard Blob Transactions](https://eips.ethereum.org/EIPS/eip-4844)

    Test cases for invalid blob fields in
    [EIP-4844: Shard Blob Transactions](https://eips.ethereum.org/EIPS/eip-4844).

note: Adding a new test

    Add a function that is named `test_<test_name>` and takes at least the following arguments:

    - blockchain_test
    - pre
    - tx
    - post

    Additional custom `pytest.fixture` fixtures can be added and parametrized for new test cases.

    There is no specific structure to follow within this test module.

"""  # noqa: E501

from typing import Dict, Mapping

import pytest

from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    EngineAPIError,
    TestAddress,
    Transaction,
    add_kzg_version,
    to_address,
    to_hash_bytes,
)

from .spec import Spec, SpecHelpers, ref_spec_4844

REFERENCE_SPEC_GIT_PATH = ref_spec_4844.git_path
REFERENCE_SPEC_VERSION = ref_spec_4844.version

pytestmark = pytest.mark.valid_from("Cancun")


@pytest.fixture
def pre():  # noqa: D103
    return {
        TestAddress: Account(balance=10**9),
        to_address(0x100): Account(balance=10**9),
    }


@pytest.fixture
def blob_tx():  # noqa: D103
    return Transaction(
        ty=Spec.BLOB_TX_TYPE,
        nonce=0,
        to=to_address(0x100),
        data=to_hash_bytes(0),
        gas_limit=3000000,
        access_list=[],
        max_fee_per_gas=10,
        max_fee_per_blob_gas=10,
        blob_versioned_hashes=add_kzg_version(
            [to_hash_bytes(x) for x in range(SpecHelpers.max_blobs_per_block())],
            Spec.BLOB_COMMITMENT_VERSION_KZG,
        ),
    )


@pytest.fixture(params=[2**64, 2**64 + 1, 2**256 - 1])
def overflown_uint_64(request):
    """
    Parameters that overflow a `uint64` field.
    """
    return request.param


@pytest.mark.parametrize(
    "excess_blob_gas_overflown, blob_gas_used_overflown",
    [
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_overflown_blob_header_fields(
    blockchain_test: BlockchainTestFiller,
    pre: Mapping[str, Account],
    blob_tx: Transaction,
    overflown_uint_64: int,
    excess_blob_gas_overflown: bool,
    blob_gas_used_overflown: bool,
):
    """
    Tests that a block with an overflown blob header is rejected.
    """
    invalid_fields = {}
    blob_block = Block(
        txs=[blob_tx],
        exception="Invalid params",
        engine_api_error_code=EngineAPIError.InvalidParams,
    )
    if excess_blob_gas_overflown:
        invalid_fields["excess_blob_gas"] = overflown_uint_64
        blob_block.excess_blob_gas = overflown_uint_64
    if blob_gas_used_overflown:
        invalid_fields["blob_gas_used"] = overflown_uint_64
        blob_block.blob_gas_used = overflown_uint_64

    blockchain_test(
        pre=pre,
        blocks=[blob_block],
        post={},
        invalid_fields=invalid_fields,
    )


def test_invalid_blob_tx_contract_creation(
    blockchain_test: BlockchainTestFiller,
    pre: Dict,
    blob_tx: Transaction,
):
    """
    Reject blocks that include blob transactions that have nil to value (contract creating).
    """
    blob_block = Block(
        txs=[blob_tx.with_fields(to=None, error="no_contract_creating_blob_txs")],
        exception="Invalid params",
        engine_api_error_code=EngineAPIError.InvalidParams,
    )
    blockchain_test(
        pre=pre,
        post={},
        blocks=[blob_block],
        invalid_fields={"to": None},
    )
