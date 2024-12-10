"""
abstract: Test [EIP-7623: Increase calldata cost](https://eips.ethereum.org/EIPS/eip-7623)
    Test transaction validity on [EIP-7623: Increase calldata cost](https://eips.ethereum.org/EIPS/eip-7623).
"""  # noqa: E501

from enum import Enum
from typing import Callable, List, Sequence

import pytest

from ethereum_test_forks import Fork, Prague
from ethereum_test_tools import (
    EOA,
    AccessList,
    Address,
    Alloc,
    AuthorizationTuple,
    Bytes,
    Hash,
    StateTestFiller,
    Transaction,
    TransactionException,
    add_kzg_version,
)

from ...cancun.eip4844_blobs.spec import Spec as EIP_4844_Spec
from .spec import ref_spec_7623

REFERENCE_SPEC_GIT_PATH = ref_spec_7623.git_path
REFERENCE_SPEC_VERSION = ref_spec_7623.version

ENABLE_FORK = Prague
pytestmark = [pytest.mark.valid_from(str(ENABLE_FORK))]


class DataTestType(Enum):
    """
    Enum for the different types of data tests.
    """

    FLOOR_GAS_COST_LESS_THAN_OR_EQUAL_TO_INTRINSIC_GAS = 0
    FLOOR_GAS_COST_GREATER_THAN_INTRINSIC_GAS = 1


@pytest.fixture
def sender(pre: Alloc) -> EOA:
    """
    Create the sender account.
    """
    return pre.fund_eoa()


@pytest.fixture
def to() -> Address | None:
    """
    Create the sender account.
    """
    return Address(1)


@pytest.fixture
def protected() -> bool:
    """
    Whether the transaction is protected or not. Only valid for type-0 transactions.
    """
    return True


@pytest.fixture
def access_list() -> List[AccessList] | None:
    """
    Access list for the transaction.
    """
    return None


@pytest.fixture
def authorization_list(
    request: pytest.FixtureRequest,
    pre: Alloc,
) -> List[AuthorizationTuple] | None:
    """
    Authorization list for the transaction.

    This fixture needs to be parametrized indirectly in order to generate the authorizations with
    valid signers using `pre` in this function, and the parametrized value should be a list of
    addresses.
    """
    if not hasattr(request, "param"):
        return None
    if request.param is None:
        return None
    return [
        AuthorizationTuple(signer=pre.fund_eoa(), address=address) for address in request.param
    ]


@pytest.fixture
def blob_versioned_hashes() -> Sequence[Hash] | None:
    """
    Versioned hashes for the transaction.
    """
    return None


@pytest.fixture
def contract_creating_tx(to: Address | None) -> bool:
    """
    Gas delta for the transaction, used to generate an invalid transaction.
    """
    return to is None


def floor_cost_find(
    floor_data_gas_cost_calculator: Callable[[int], int],
    intrinsic_gas_cost_calculator: Callable[[int], int],
) -> int:
    """
    Find the minimum amount of tokens that will trigger the floor gas cost, by using a binary
    search and the intrinsic gas cost and floor data calculators.
    """
    # Start with 1000 tokens and if the intrinsic gas cost is greater than the floor gas cost,
    # multiply the number of tokens by 2 until it's not.
    tokens = 1000
    while floor_data_gas_cost_calculator(tokens) < intrinsic_gas_cost_calculator(tokens):
        tokens *= 2

    # Binary search to find the minimum number of tokens that will trigger the floor gas cost.
    left = 0
    right = tokens
    while left < right:
        tokens = (left + right) // 2
        if floor_data_gas_cost_calculator(tokens) < intrinsic_gas_cost_calculator(tokens):
            left = tokens + 1
        else:
            right = tokens
    tokens = left

    if floor_data_gas_cost_calculator(tokens) > intrinsic_gas_cost_calculator(tokens):
        tokens -= 1

    # Verify that increasing the tokens by one would always trigger the floor gas cost.
    assert (
        floor_data_gas_cost_calculator(tokens) <= intrinsic_gas_cost_calculator(tokens)
    ) and floor_data_gas_cost_calculator(tokens + 1) > intrinsic_gas_cost_calculator(
        tokens + 1
    ), "invalid case"

    return tokens


@pytest.fixture
def tx_data(
    fork: Fork,
    data_test_type: DataTestType,
    access_list: List[AccessList] | None,
    authorization_list: List[AuthorizationTuple] | None,
    contract_creating_tx: bool,
) -> Bytes:
    """
    All tests in this file use data that is generated dynamically depending on the case and the
    attributes of the transaction in order to reach the edge cases where the floor gas cost is
    equal or barely greater than the intrinsic gas cost.

    We have two different types of tests:
    - FLOOR_GAS_COST_LESS_THAN_OR_EQUAL_TO_INTRINSIC_GAS: The floor gas cost is less than or equal
        to the intrinsic gas cost, which means that the size of the tokens in the data are not
        enough to trigger the floor gas cost.
    - FLOOR_GAS_COST_GREATER_THAN_INTRINSIC_GAS: The floor gas cost is greater than the intrinsic
        gas cost, which means that the size of the tokens in the data are enough to trigger the
        floor gas cost.

    E.g. Given a transaction with a single access list and a single storage key, its intrinsic gas
    cost (as of Prague fork) can be calculated as:
    - 21,000 gas for the transaction
    - 2,400 gas for the access list
    - 1,900 gas for the storage key
    - 16 gas for each non-zero byte in the data
    - 4 gas for each zero byte in the data

    Its floor data gas cost can be calculated as:
    - 21,000 gas for the transaction
    - 40 gas for each non-zero byte in the data
    - 10 gas for each zero byte in the data

    Notice that the data included in the transaction affects both the intrinsic gas cost and the
    floor data cost, but at different rates.

    The purpose of this function is to find the exact amount of data where the floor data gas
    cost starts exceeding the intrinsic gas cost.

    After a binary search we find that adding 717 tokens of data (179 non-zero bytes +
    1 zero byte) triggers the floor gas cost.

    Therefore, this function will return a Bytes object with 179 non-zero bytes and 1 zero byte
    for `FLOOR_GAS_COST_GREATER_THAN_INTRINSIC_GAS` and a Bytes object with 179 non-zero bytes
    and no zero bytes for `FLOOR_GAS_COST_LESS_THAN_OR_EQUAL_TO_INTRINSIC_GAS`
    """

    def tokens_to_data(tokens: int) -> Bytes:
        return Bytes(b"\x01" * (tokens // 4) + b"\x00" * (tokens % 4))

    fork_intrinsic_cost_calculator = fork.transaction_intrinsic_cost_calculator()

    def transaction_intrinsic_cost_calculator(tokens: int) -> int:
        return fork_intrinsic_cost_calculator(
            calldata=tokens_to_data(tokens),
            contract_creation=contract_creating_tx,
            access_list=access_list,
            authorization_list_or_count=authorization_list,
            return_cost_deducted_prior_execution=True,
        )

    fork_data_floor_cost_calculator = fork.transaction_data_floor_cost_calculator()

    def transaction_data_floor_cost_calculator(tokens: int) -> int:
        return fork_data_floor_cost_calculator(data=tokens_to_data(tokens))

    # Start with zero data and check the difference in the gas calculator between the
    # intrinsic gas cost and the floor gas cost.
    if transaction_data_floor_cost_calculator(0) >= transaction_intrinsic_cost_calculator(0):
        # Special case which is a transaction with no extra intrinsic gas costs other than the
        # data cost, any data will trigger the floor gas cost.
        if data_test_type == DataTestType.FLOOR_GAS_COST_LESS_THAN_OR_EQUAL_TO_INTRINSIC_GAS:
            return Bytes(b"")
        else:
            return Bytes(b"\0")

    tokens = floor_cost_find(
        floor_data_gas_cost_calculator=transaction_data_floor_cost_calculator,
        intrinsic_gas_cost_calculator=transaction_intrinsic_cost_calculator,
    )

    if data_test_type == DataTestType.FLOOR_GAS_COST_GREATER_THAN_INTRINSIC_GAS:
        return tokens_to_data(tokens + 1)
    return tokens_to_data(tokens)


@pytest.fixture
def tx_gas_delta() -> int:
    """
    Gas delta to modify the gas amount included with the transaction.

    If negative, the transaction will be invalid because the intrinsic gas cost is greater than the
    gas limit.

    This value operates regardless of whether the floor data gas cost is reached or not.

    If the value is greater than zero, the transaction will also be valid and the test will check
    that transaction processing does not consume more gas than it should.
    """
    return 0


@pytest.fixture
def tx_gas(
    fork: Fork,
    tx_data: Bytes,
    access_list: List[AccessList] | None,
    authorization_list: List[AuthorizationTuple] | None,
    contract_creating_tx: bool,
    tx_gas_delta: int,
) -> int:
    """
    Gas limit for the transaction.

    The calculated value takes into account the normal intrinsic gas cost and the floor data gas
    cost.

    The gas delta is added to the intrinsic gas cost to generate different test scenarios.
    """
    intrinsic_gas_cost_calculator = fork.transaction_intrinsic_cost_calculator()
    return (
        intrinsic_gas_cost_calculator(
            calldata=tx_data,
            contract_creation=contract_creating_tx,
            access_list=access_list,
            authorization_list_or_count=authorization_list,
        )
        + tx_gas_delta
    )


@pytest.fixture
def tx_error(tx_gas_delta: int) -> TransactionException | None:
    """
    Transaction error, only expected if the gas delta is negative.
    """
    return TransactionException.INTRINSIC_GAS_TOO_LOW if tx_gas_delta < 0 else None


@pytest.fixture
def tx(
    sender: EOA,
    ty: int,
    tx_data: Bytes,
    to: Address | None,
    protected: bool,
    access_list: List[AccessList] | None,
    authorization_list: List[AuthorizationTuple] | None,
    blob_versioned_hashes: Sequence[Hash] | None,
    tx_gas: int,
    tx_error: TransactionException | None,
) -> Transaction:
    """
    Create the transaction used in each test.
    """
    return Transaction(
        ty=ty,
        sender=sender,
        data=tx_data,
        to=to,
        protected=protected,
        access_list=access_list,
        authorization_list=authorization_list,
        gas_limit=tx_gas,
        blob_versioned_hashes=blob_versioned_hashes,
        error=tx_error,
    )


# All tests in this file are parametrized with the following parameters:
pytestmark += [
    pytest.mark.parametrize(
        "tx_gas_delta",
        [
            # Test the case where the included gas is greater than the intrinsic gas to verify that
            # the data floor does not consume more gas than it should.
            pytest.param(1, id="extra_gas"),
            pytest.param(0, id="exact_gas"),
            pytest.param(-1, id="insufficient_gas"),
        ],
    ),
    pytest.mark.parametrize(
        "data_test_type",
        [
            pytest.param(
                DataTestType.FLOOR_GAS_COST_LESS_THAN_OR_EQUAL_TO_INTRINSIC_GAS,
                id="floor_gas_less_than_or_equal_to_intrinsic_gas",
            ),
            pytest.param(
                DataTestType.FLOOR_GAS_COST_GREATER_THAN_INTRINSIC_GAS,
                id="floor_gas_greater_than_intrinsic_gas",
            ),
        ],
    ),
]


@pytest.mark.parametrize(
    "protected",
    [
        pytest.param(True, id="protected"),
        pytest.param(False, id="unprotected"),
    ],
)
@pytest.mark.parametrize(
    "ty",
    [pytest.param(0, id="type_0")],
)
@pytest.mark.parametrize(
    "to",
    [
        pytest.param(None, id="contract_creating"),
        pytest.param(Address(1), id=""),
    ],
)
def test_transaction_validity_type_0(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
) -> None:
    """
    Test transaction validity for transactions without access lists and contract creation.
    """
    state_test(
        pre=pre,
        post={},
        tx=tx,
    )


@pytest.mark.parametrize(
    "to",
    [
        pytest.param(None, id="contract_creating"),
        pytest.param(Address(1), id=""),
    ],
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
    """
    Test transaction validity for transactions with access lists and contract creation.
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
    Test transaction validity for transactions with access lists, blobs, but no contract creation.
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
