"""
abstract: Tests related to gas of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702)
    Tests related to gas of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702).
"""  # noqa: E501

from enum import Enum
from itertools import count
from typing import Generator, Iterator, List

import pytest

from ethereum_test_tools import (
    EOA,
    AccessList,
    Account,
    Address,
    Alloc,
    AuthorizationTuple,
    Bytes,
    CodeGasMeasure,
    Environment,
)
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    StateTestFiller,
    Storage,
    Transaction,
    eip_2028_transaction_data_cost,
)

from .spec import Spec, ref_spec_7702

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version

pytestmark = pytest.mark.valid_from("Prague")

auth_account_start_balance = 0


class AuthorizationListCases(Enum):
    """
    Different cases of authorization lists for testing gas cost of set-code transactions.
    """

    VALID_SAME_SIGNER = "valid_same_signer"
    INVALID_SAME_SIGNER = "invalid_same_signer"
    VALID_DIFFERENT_SIGNERS = "valid_multiple_signers"
    FIRST_VALID_THEN_DUPLICATES = "first_valid_then_duplicates"


@pytest.fixture
def authorization_list(
    authorization_list_case: AuthorizationListCases,
    authorizations_count: int,
    authority_iterator: Iterator[Address],
    authorize_to_address: Address,
    self_sponsored: bool,
) -> List[AuthorizationTuple]:
    """
    Fixture to return the authorization list for the given case.
    """
    match authorization_list_case:
        case AuthorizationListCases.VALID_SAME_SIGNER:
            signer = next(authority_iterator)
            return [
                AuthorizationTuple(
                    address=authorize_to_address,
                    nonce=i + (1 if self_sponsored else 0),
                    signer=signer,
                )
                for i in range(authorizations_count)
            ]
        case AuthorizationListCases.INVALID_SAME_SIGNER:
            signer = next(authority_iterator)
            return [
                AuthorizationTuple(
                    address=authorize_to_address,
                    nonce=(0 if self_sponsored else 1),
                    signer=signer,
                )
                for _ in range(authorizations_count)
            ]
        case AuthorizationListCases.VALID_DIFFERENT_SIGNERS:
            return [
                AuthorizationTuple(
                    address=authorize_to_address,
                    nonce=1 if i == 0 and self_sponsored else 0,
                    signer=next(authority_iterator),
                )
                for i in range(authorizations_count)
            ]
        case AuthorizationListCases.FIRST_VALID_THEN_DUPLICATES:
            signer = next(authority_iterator)
            return [
                AuthorizationTuple(
                    address=authorize_to_address,
                    nonce=1 if self_sponsored else 0,
                    signer=signer,
                )
                for _ in range(authorizations_count)
            ]
        case _:
            raise ValueError(f"Unsupported authorization list case: {authorization_list_case}")


@pytest.fixture
def valid_authorizations(
    authorization_list_case: AuthorizationListCases,
    authorizations_count: int,
) -> int:
    """
    Fixture to return the number of valid authorizations in the authorization list.
    """
    match authorization_list_case:
        case (
            AuthorizationListCases.VALID_SAME_SIGNER
            | AuthorizationListCases.VALID_DIFFERENT_SIGNERS
        ):
            return authorizations_count
        case AuthorizationListCases.INVALID_SAME_SIGNER:
            return 0
        case AuthorizationListCases.FIRST_VALID_THEN_DUPLICATES:
            return 1
        case _:
            raise ValueError(f"Unsupported authorization list case: {authorization_list_case}")


class AuthorizationAddressCases(Enum):
    """
    Different cases of address to which the authority authorizes to set the code to.
    """

    EMPTY_ACCOUNT = "set_to_empty_account"
    EOA = "set_to_eoa"
    CONTRACT = "set_to_contract"


@pytest.fixture()
def authorize_to_address(request: pytest.FixtureRequest, pre: Alloc) -> Address:
    """
    Fixture to return the address to which the authority authorizes to set the code to.
    """
    match request.param:
        case AuthorizationAddressCases.EMPTY_ACCOUNT:
            return pre.fund_eoa(0)
        case AuthorizationAddressCases.EOA:
            return pre.fund_eoa(1)
        case AuthorizationAddressCases.CONTRACT:
            return pre.deploy_contract(Op.STOP)
    raise ValueError(f"Unsupported authorization address case: {request.param}")


class AuthorityTypes(Enum):
    """
    Different cases of authority. Contract requires the authority address collision so cannot be
    reproduced in live networks.
    """

    EMPTY_ACCOUNT = "empty_account"
    EOA = "eoa"
    CONTRACT = "contract"


class AccessListCases(Enum):
    """
    Different cases of access lists for testing gas cost of set-code transactions.
    """

    EMPTY_ACCESS_LIST = "empty_access_list"
    AUTHORITY = "authority_in_access_list"
    SET_CODE_ADDRESS = "set_code_address_in_access_list"
    AUTHORITY_AND_SET_CODE_ADDRESS = "authority_and_set_code_address_in_access_list"


@pytest.fixture()
def access_list(
    access_list_case: AccessListCases,
    authorization_list: List[AuthorizationTuple],
) -> List[AccessList]:
    """
    Fixture to return the access list for the given case.
    """
    access_list: List[AccessList] = []
    if access_list_case == AccessListCases.EMPTY_ACCESS_LIST:
        return access_list
    if (
        access_list_case == AccessListCases.AUTHORITY
        or access_list_case == AccessListCases.AUTHORITY_AND_SET_CODE_ADDRESS
    ):
        for authorization_tuple in authorization_list:
            already_added = False
            for al in access_list:
                if al.address == authorization_tuple.signer:
                    already_added = True
                    break
            if not already_added:
                access_list.append(
                    AccessList(address=authorization_tuple.signer, storage_keys=[0])
                )
    if (
        access_list_case == AccessListCases.SET_CODE_ADDRESS
        or access_list_case == AccessListCases.AUTHORITY_AND_SET_CODE_ADDRESS
    ):
        for authorization_tuple in authorization_list:
            already_added = False
            for al in access_list:
                if al.address == authorization_tuple.address:
                    already_added = True
                    break
            if not already_added:
                access_list.append(
                    AccessList(address=authorization_tuple.address, storage_keys=[0])
                )

    return access_list


@pytest.fixture()
def authority_iterator(
    pre: Alloc,
    sender: EOA,
    authority_type: AuthorityTypes,
    self_sponsored: bool,
) -> Iterator[Address]:
    """
    Fixture to return the generator for the authority addresses.
    """

    def generator() -> Generator[Address, None, None]:
        match authority_type:
            case AuthorityTypes.EMPTY_ACCOUNT:
                assert (
                    not self_sponsored
                ), "Self-sponsored empty-account authority is not supported"
                for _ in count():
                    yield pre.fund_eoa(0)
            case AuthorityTypes.EOA:
                for i in count():
                    if i == 0 and self_sponsored:
                        yield sender
                    else:
                        yield pre.fund_eoa()
            case AuthorityTypes.CONTRACT:
                assert not self_sponsored, "Self-sponsored contract authority is not supported"
                for _ in count():
                    authority = pre.fund_eoa()
                    authority_account = pre[authority]
                    assert authority_account is not None
                    authority_account.code = Bytes(Op.STOP)
                    yield authority
        raise ValueError(f"Unsupported authority type: {authority_type}")

    return generator()


@pytest.fixture()
def sender(pre: Alloc) -> EOA:
    """
    Fixture to return the sender address.
    """
    return pre.fund_eoa()


@pytest.mark.parametrize(
    "authorization_list_case,authorizations_count",
    [
        pytest.param(AuthorizationListCases.VALID_SAME_SIGNER, 1, id="valid_single_authorization"),
        pytest.param(
            AuthorizationListCases.VALID_SAME_SIGNER, 2, id="valid_multiple_authorizations"
        ),
        pytest.param(
            AuthorizationListCases.INVALID_SAME_SIGNER, 1, id="invalid_single_authorization"
        ),
        pytest.param(
            AuthorizationListCases.INVALID_SAME_SIGNER, 2, id="invalid_multiple_authorizations"
        ),
        pytest.param(
            AuthorizationListCases.VALID_DIFFERENT_SIGNERS,
            2,
            id="valid_different_signer_authorizations",
        ),
        pytest.param(
            AuthorizationListCases.FIRST_VALID_THEN_DUPLICATES,
            2,
            id="first_valid_then_duplicates_authorizations",
        ),
    ],
)
@pytest.mark.parametrize(
    "authorize_to_address",
    list(AuthorizationAddressCases),
    ids=lambda case: case.value,
    indirect=True,
)
@pytest.mark.parametrize(
    "access_list_case",
    list(AccessListCases),
    ids=lambda case: case.value,
)
@pytest.mark.parametrize(
    "data",
    [
        pytest.param(b"", id="empty_data"),
        pytest.param(b"\x01", id="non_zero_data"),
        pytest.param(b"\x00", id="zero_data"),
    ],
)
@pytest.mark.parametrize(
    "self_sponsored,authority_type",
    [
        pytest.param(False, AuthorityTypes.EMPTY_ACCOUNT, id="empty_account_authority"),
        pytest.param(False, AuthorityTypes.EOA, id="eoa_authority"),
        pytest.param(True, AuthorityTypes.EOA, id="self_sponsored_eoa_authority"),
        pytest.param(
            False,
            AuthorityTypes.CONTRACT,
            marks=pytest.mark.pre_alloc_modify,
            id="contract_authority",
        ),
    ],
)
def test_gas_cost(
    state_test: StateTestFiller,
    pre: Alloc,
    authorization_list_case: AuthorizationListCases,
    authority_type: AuthorityTypes,
    authorization_list: List[AuthorizationTuple],
    valid_authorizations: int,
    data: bytes,
    access_list: List[AccessList],
    sender: EOA,
):
    """
    Test gas cost of a set-code transaction in different scenarios:

    - Set code to an account with a single authorization tuple.
    - Set code to an account with multiple authorization tuples.
    """
    start_gas = 10_000_000
    intrinsic_gas = (
        21_000
        + eip_2028_transaction_data_cost(data)
        + 1900 * sum(len(al.storage_keys) for al in access_list)
        + 2400 * len(access_list)
        + 2  # Op.GAS cost
    )
    # Calculate the intrinsic gas cost of the authorizations, by default the
    # full empty account cost is charged for each authorization.
    intrinsic_gas += Spec.PER_EMPTY_ACCOUNT_COST * len(authorization_list)

    # Determine the amount of authorizations that have a discount
    if authority_type == AuthorityTypes.CONTRACT:
        # No authorization is valid (code not empty), hence no discount
        discounted_authorizations = 0
    elif authority_type == AuthorityTypes.EOA:
        # all valid authorizations (correct nonce) have a discount
        discounted_authorizations = valid_authorizations
    elif authorization_list_case in [
        AuthorizationListCases.VALID_SAME_SIGNER,
    ]:
        # all but the first valid authorization have a discount (on the first one, the account
        # is empty, but then the nonce is incremented)
        discounted_authorizations = valid_authorizations - 1
    else:
        discounted_authorizations = 0

    intrinsic_gas -= (
        Spec.PER_EMPTY_ACCOUNT_COST - Spec.PER_AUTH_BASE_COST
    ) * discounted_authorizations

    test_code_storage = Storage()
    test_code = (
        Op.SSTORE(test_code_storage.store_next(start_gas - intrinsic_gas), Op.GAS) + Op.STOP
    )
    test_code_address = pre.deploy_contract(test_code)

    tx = Transaction(
        gas_limit=start_gas,
        to=test_code_address,
        value=0,
        data=data,
        authorization_list=authorization_list,
        access_list=access_list,
        sender=sender,
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            test_code_address: Account(storage=test_code_storage),
        },
    )


@pytest.mark.parametrize(
    "authorization_list_case,authorizations_count",
    [
        pytest.param(AuthorizationListCases.VALID_SAME_SIGNER, 1, id="valid_single_authorization"),
        pytest.param(
            AuthorizationListCases.INVALID_SAME_SIGNER, 1, id="invalid_single_authorization"
        ),
    ],
)
@pytest.mark.parametrize(
    "authorize_to_address",
    list(AuthorizationAddressCases),
    ids=lambda case: case.value,
    indirect=True,
)
@pytest.mark.parametrize(
    "self_sponsored,authority_type",
    [
        pytest.param(False, AuthorityTypes.EMPTY_ACCOUNT, id="empty_account_authority"),
        pytest.param(False, AuthorityTypes.EOA, id="eoa_authority"),
        pytest.param(True, AuthorityTypes.EOA, id="self_sponsored_eoa_authority"),
        pytest.param(
            False,
            AuthorityTypes.CONTRACT,
            marks=pytest.mark.pre_alloc_modify,
            id="contract_authority",
        ),
    ],
)
@pytest.mark.parametrize(
    "access_list_case",
    [
        AccessListCases.EMPTY_ACCESS_LIST,
        AccessListCases.AUTHORITY,
    ],
    ids=lambda case: case.value,
)
def test_account_warming(
    state_test: StateTestFiller,
    pre: Alloc,
    authorization_list: List[AuthorizationTuple],
    access_list_case: AccessListCases,
    access_list: List[AccessList],
    authorize_to_address: Address,
    authority_type: AuthorityTypes,
    valid_authorizations: int,
    self_sponsored: bool,
    sender: EOA,
):
    """
    Test account warming for set-code transactions.
    """
    authority = authorization_list[0].signer
    assert authority is not None, "authority address is not set"
    overhead_cost = 3

    authority_warm = False
    if authority_type != AuthorityTypes.CONTRACT:
        if valid_authorizations > 0:
            authority_warm = True
        if self_sponsored:
            authority_warm = True
    if access_list_case == AccessListCases.AUTHORITY:
        authority_warm = True

    authorize_to_warm = False

    callee_storage = Storage()
    callee_code = CodeGasMeasure(
        code=Op.EXTCODESIZE(authority),
        overhead_cost=overhead_cost,
        extra_stack_items=1,
        sstore_key=callee_storage.store_next(100 if authority_warm else 2600),
        stop=False,
    ) + CodeGasMeasure(
        code=Op.EXTCODESIZE(authorize_to_address),
        overhead_cost=overhead_cost,
        extra_stack_items=1,
        sstore_key=callee_storage.store_next(100 if authorize_to_warm else 2600),
    )
    callee_address = pre.deploy_contract(callee_code, storage=callee_storage.canary())

    tx = Transaction(
        gas_limit=100_000,
        to=callee_address,
        authorization_list=authorization_list,
        access_list=access_list,
        sender=sender,
    )
    post = {
        callee_address: Account(
            storage=callee_storage,
        ),
    }
    if valid_authorizations > 0:
        post[authority] = Account(
            nonce=2 if self_sponsored else 1 if authority_type != AuthorityTypes.CONTRACT else 0,
        )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


def test_intrinsic_gas_cost(
    state_test: StateTestFiller,
    pre: Alloc,
    authorization_list_case: AuthorizationListCases,
    data: bytes,
    access_list_case: AccessListCases,
    mid_tx_value_transfer_amount: int,
    authority_in_trie: bool,
    valid: bool,
):
    """
    Test sending a transaction with the exact intrinsic gas required and also insufficient
    gas.
    """
    # TODO: Implement
    pass
