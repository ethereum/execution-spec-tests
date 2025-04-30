"""
abstract: Crafted tests for mainnet of [EIP-7623: Increase calldata cost](https://eips.ethereum.org/EIPS/eip-7623)
    Crafted tests for mainnet of [EIP-7623: Increase calldata cost](https://eips.ethereum.org/EIPS/eip-7623).
"""  # noqa: E501

import pytest

from ethereum_test_forks import Prague
from ethereum_test_tools import (
    AccessList,
    Address,
    Alloc,
    Hash,
    StateTestFiller,
    Transaction,
    add_kzg_version,
)
from ethereum_test_tools import Opcodes as Op

from ...cancun.eip4844_blobs.spec import Spec as EIP_4844_Spec
from .helpers import DataTestType
from .spec import ref_spec_7623

REFERENCE_SPEC_GIT_PATH = ref_spec_7623.git_path
REFERENCE_SPEC_VERSION = ref_spec_7623.version

pytestmark = [pytest.mark.valid_at("Prague"), pytest.mark.mainnet]


@pytest.mark.parametrize(
    "ty,protected,access_list,blob_versioned_hashes,authorization_list",
    [
        pytest.param(0, True, None, None, None, id="type_0_protected"),
        pytest.param(0, False, None, None, None, id="type_0_unprotected"),
        pytest.param(
            1,
            True,
            [AccessList(address=Address(1), storage_keys=[Hash(0)])],
            None,
            None,
            id="type_1",
        ),
        pytest.param(
            2,
            True,
            [AccessList(address=Address(1), storage_keys=[Hash(0)])],
            None,
            None,
            id="type_2",
        ),
        pytest.param(
            3,
            True,
            [AccessList(address=Address(1), storage_keys=[Hash(0)])],
            add_kzg_version(
                [Hash(x) for x in range(1)],
                EIP_4844_Spec.BLOB_COMMITMENT_VERSION_KZG,
            ),
            None,
            id="type_3",
            marks=pytest.mark.execute(
                pytest.mark.skip(reason="Blob txs not supported by execute")
            ),
        ),
        pytest.param(
            4,
            True,
            [AccessList(address=Address(1), storage_keys=[Hash(0)])],
            None,
            [Address(1)],
            id="type_4",
        ),
    ],
    indirect=["authorization_list"],
)
@pytest.mark.parametrize(
    "tx_gas_delta",
    [
        pytest.param(0, id="exact_gas"),
    ],
)
@pytest.mark.parametrize(
    "to",
    [
        pytest.param("eoa", id="to_eoa"),
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "data_test_type",
    [
        pytest.param(
            DataTestType.FLOOR_GAS_COST_GREATER_THAN_INTRINSIC_GAS,
            id="floor_gas_greater_than_intrinsic_gas",
        ),
    ],
)
def test_eip_7623(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
) -> None:
    """Test transaction validity for transactions without access lists and contract creation."""
    state_test(
        pre=pre,
        post={},
        tx=tx,
    )


@pytest.mark.parametrize(
    "to",
    [
        pytest.param("eoa", id="to_eoa"),
        pytest.param(None, id="contract_creating"),
        pytest.param(Op.STOP, id=""),
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "access_list",
    [
        pytest.param(
            None,
            id="no_access_list",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[])],
            id="single_access_list_no_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[Hash(0)])],
            id="single_access_list_single_storage_key",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[Hash(k) for k in range(10)])],
            id="single_access_list_multiple_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(a), storage_keys=[]) for a in range(10)],
            id="multiple_access_lists_no_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(a), storage_keys=[Hash(0)]) for a in range(10)],
            id="multiple_access_lists_single_storage_key",
        ),
        pytest.param(
            [
                AccessList(address=Address(a), storage_keys=[Hash(k) for k in range(10)])
                for a in range(10)
            ],
            id="multiple_access_lists_multiple_storage_keys",
        ),
    ],
)
@pytest.mark.parametrize(
    "ty",
    [pytest.param(1, id="type_1"), pytest.param(2, id="type_2")],
)
def test_transaction_validity_type_1_type_2(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
) -> None:
    """Test transaction validity for transactions with access lists and contract creation."""
    state_test(
        pre=pre,
        post={},
        tx=tx,
    )


@pytest.mark.parametrize(
    "access_list",
    [
        pytest.param(
            None,
            id="no_access_list",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[])],
            id="single_access_list_no_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[Hash(0)])],
            id="single_access_list_single_storage_key",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[Hash(k) for k in range(10)])],
            id="single_access_list_multiple_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(a), storage_keys=[]) for a in range(10)],
            id="multiple_access_lists_no_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(a), storage_keys=[Hash(0)]) for a in range(10)],
            id="multiple_access_lists_single_storage_key",
        ),
        pytest.param(
            [
                AccessList(address=Address(a), storage_keys=[Hash(k) for k in range(10)])
                for a in range(10)
            ],
            id="multiple_access_lists_multiple_storage_keys",
        ),
    ],
)
@pytest.mark.parametrize(
    # Blobs don't really have an effect because the blob gas does is not considered in the
    # intrinsic gas calculation, but we still test it to make sure that the transaction is
    # correctly processed.
    "blob_versioned_hashes",
    [
        pytest.param(
            add_kzg_version(
                [Hash(x) for x in range(1)],
                EIP_4844_Spec.BLOB_COMMITMENT_VERSION_KZG,
            ),
            id="single_blob",
        ),
        pytest.param(
            add_kzg_version(
                [Hash(x) for x in range(6)],
                EIP_4844_Spec.BLOB_COMMITMENT_VERSION_KZG,
            ),
            id="multiple_blobs",
        ),
    ],
)
@pytest.mark.parametrize(
    "ty",
    [pytest.param(3, id="type_3")],
)
def test_transaction_validity_type_3(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
) -> None:
    """
    Test transaction validity for transactions with access lists, blobs,
    but no contract creation.
    """
    state_test(
        pre=pre,
        post={},
        tx=tx,
    )


@pytest.mark.parametrize(
    "access_list",
    [
        pytest.param(
            None,
            id="no_access_list",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[])],
            id="single_access_list_no_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[Hash(0)])],
            id="single_access_list_single_storage_key",
        ),
        pytest.param(
            [AccessList(address=Address(1), storage_keys=[Hash(k) for k in range(10)])],
            id="single_access_list_multiple_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(a), storage_keys=[]) for a in range(10)],
            id="multiple_access_lists_no_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(a), storage_keys=[Hash(0)]) for a in range(10)],
            id="multiple_access_lists_single_storage_key",
        ),
        pytest.param(
            [
                AccessList(address=Address(a), storage_keys=[Hash(k) for k in range(10)])
                for a in range(10)
            ],
            id="multiple_access_lists_multiple_storage_keys",
        ),
    ],
)
@pytest.mark.parametrize(
    "authorization_list",
    [
        pytest.param(
            [Address(1)],
            id="single_authorization",
        ),
        pytest.param(
            [Address(i + 1) for i in range(10)],
            id="multiple_authorizations",
        ),
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "ty",
    [pytest.param(4, id="type_4")],
)
def test_transaction_validity_type_4(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
) -> None:
    """
    Test transaction validity for transactions with access lists, authorization lists, but no
    contract creation.
    """
    state_test(
        pre=pre,
        post={},
        tx=tx,
    )
