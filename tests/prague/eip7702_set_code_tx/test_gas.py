"""
abstract: Tests related to gas of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702)
    Tests related to gas of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702).
"""  # noqa: E501

from enum import Enum, auto
from itertools import cycle
from typing import Dict, Generator, Iterator, List, Tuple

import pytest

from ethereum_test_tools import (
    EOA,
    AccessList,
    Account,
    Address,
    Alloc,
    AuthorizationTuple,
    Bytecode,
    Bytes,
    CodeGasMeasure,
    Environment,
)
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    StateTestFiller,
    Storage,
    Transaction,
    TransactionException,
    eip_2028_transaction_data_cost,
    named_pytest_param,
)

from .spec import Spec, ref_spec_7702

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version

pytestmark = pytest.mark.valid_from("Prague")

# Enum classes used to parametrize the tests


class SignerType(Enum):
    """
    Different cases of authorization lists for testing gas cost of set-code transactions.
    """

    SINGLE_SIGNER = auto()
    MULTIPLE_SIGNERS = auto()


class AuthorizationInvalidityType(Enum):
    """
    Different types of invalidity for the authorization list.
    """

    NONE = auto()
    INVALID_NONCE = auto()
    REPEATED_NONCE = auto()
    INVALID_CHAIN_ID = auto()


class AddressType(Enum):
    """
    Different types of addresses used to specify the type of authority that signs an authorization,
    and the type of address to which the authority authorizes to set the code to.
    """

    EMPTY_ACCOUNT = auto()
    EOA = auto()
    CONTRACT = auto()


class ChainIDType(Enum):
    """
    Different types of chain IDs used in the authorization list.
    """

    GENERIC = auto()
    CHAIN_SPECIFIC = auto()


class AccessListType(Enum):
    """
    Different cases of access lists for testing gas cost of set-code transactions.
    """

    EMPTY = auto()
    CONTAINS_AUTHORITY = auto()
    CONTAINS_SET_CODE_ADDRESS = auto()
    CONTAINS_AUTHORITY_AND_SET_CODE_ADDRESS = auto()

    def contains_authority(self) -> bool:
        """
        Return True if the access list contains the authority address.
        """
        return self in {
            AccessListType.CONTAINS_AUTHORITY,
            AccessListType.CONTAINS_AUTHORITY_AND_SET_CODE_ADDRESS,
        }

    def contains_set_code_address(self) -> bool:
        """
        Return True if the access list contains the address to which the authority authorizes to
        set the code to.
        """
        return self in {
            AccessListType.CONTAINS_SET_CODE_ADDRESS,
            AccessListType.CONTAINS_AUTHORITY_AND_SET_CODE_ADDRESS,
        }


# Fixtures used to parametrize the tests


@pytest.fixture()
def authority_iterator(
    pre: Alloc,
    sender: EOA,
    authority_type: AddressType | List[AddressType],
    self_sponsored: bool,
) -> Iterator[Tuple[Address, bool, bool]]:
    """
    Fixture to return the generator for the authority addresses.
    """
    authority_type_iterator = (
        cycle([authority_type])
        if isinstance(authority_type, AddressType)
        else cycle(authority_type)
    )

    def generator(
        authority_type_iterator: Iterator[AddressType],
    ) -> Generator[Tuple[Address, bool, bool], None, None]:
        for i, current_authority_type in enumerate(authority_type_iterator):
            match current_authority_type:
                case AddressType.EMPTY_ACCOUNT:
                    assert (
                        not self_sponsored
                    ), "Self-sponsored empty-account authority is not supported"
                    yield pre.fund_eoa(0), True, True
                case AddressType.EOA:
                    if i == 0 and self_sponsored:
                        yield sender, True, False
                    else:
                        yield pre.fund_eoa(), True, False
                case AddressType.CONTRACT:
                    assert (
                        not self_sponsored or i > 0
                    ), "Self-sponsored contract authority is not supported"
                    authority = pre.fund_eoa()
                    authority_account = pre[authority]
                    assert authority_account is not None
                    authority_account.code = Bytes(Op.STOP)
                    yield authority, False, False
                case _:
                    raise ValueError(f"Unsupported authority type: {current_authority_type}")

    return generator(authority_type_iterator)


@pytest.fixture
def authorization_list_with_validity(
    signer_type: SignerType,
    authorization_invalidity_type: AuthorizationInvalidityType,
    authorizations_count: int,
    chain_id_type: ChainIDType,
    authority_iterator: Iterator[Tuple[Address, bool, bool]],
    authorize_to_address: Address,
    self_sponsored: bool,
) -> List[Tuple[AuthorizationTuple, bool, bool]]:
    """
    Fixture to return the authorization list for the given case.
    """
    chain_id = 0 if chain_id_type == ChainIDType.GENERIC else 1
    if authorization_invalidity_type == AuthorizationInvalidityType.INVALID_CHAIN_ID:
        chain_id = 2

    match signer_type:
        case SignerType.SINGLE_SIGNER:
            signer, valid_authority, empty = next(authority_iterator)
            authorization_list = []
            for i in range(authorizations_count):
                # Get the nonce of the authorization
                match authorization_invalidity_type:
                    case AuthorizationInvalidityType.INVALID_NONCE:
                        nonce = 0 if self_sponsored else 1
                    case AuthorizationInvalidityType.REPEATED_NONCE:
                        nonce = 1 if self_sponsored else 0
                    case _:
                        nonce = i if not self_sponsored else i + 1

                # Get the validity of the authorization
                match authorization_invalidity_type:
                    case AuthorizationInvalidityType.NONE:
                        valid = valid_authority
                    case AuthorizationInvalidityType.REPEATED_NONCE:
                        valid = i == 0
                    case _:
                        valid = False

                authorization_list.append(
                    (
                        AuthorizationTuple(
                            chain_id=chain_id,
                            address=authorize_to_address,
                            nonce=nonce,
                            signer=signer,
                        ),
                        valid,
                        empty,
                    )
                )
            return authorization_list

        case SignerType.MULTIPLE_SIGNERS:
            if authorization_invalidity_type == AuthorizationInvalidityType.REPEATED_NONCE:
                # Reuse the first two authorities for the repeated nonce case
                authority_iterator = cycle([next(authority_iterator), next(authority_iterator)])

            authorization_list = []
            for i in range(authorizations_count):
                signer, valid_authority, empty = next(authority_iterator)
                if self_sponsored and i == 0:
                    if authorization_invalidity_type == AuthorizationInvalidityType.INVALID_NONCE:
                        nonce = 0
                    else:
                        nonce = 1
                else:
                    if authorization_invalidity_type == AuthorizationInvalidityType.INVALID_NONCE:
                        nonce = 1
                    else:
                        nonce = 0
                if authorization_invalidity_type == AuthorizationInvalidityType.NONE or (
                    authorization_invalidity_type == AuthorizationInvalidityType.REPEATED_NONCE
                    and i <= 1
                ):
                    valid = valid_authority
                else:
                    valid = False
                authorization_list.append(
                    (
                        AuthorizationTuple(
                            chain_id=chain_id,
                            address=authorize_to_address,
                            nonce=nonce,
                            signer=signer,
                        ),
                        valid,
                        empty,
                    )
                )
            return authorization_list
        case _:
            raise ValueError(f"Unsupported authorization list case: {signer_type}")


@pytest.fixture
def authorization_list(
    authorization_list_with_validity: List[Tuple[AuthorizationTuple, bool, bool]],
) -> List[AuthorizationTuple]:
    """
    Fixture to return the authorization list for the given case.
    """
    return [authorization_tuple for authorization_tuple, _, _ in authorization_list_with_validity]


@pytest.fixture()
def authorize_to_address(request: pytest.FixtureRequest, pre: Alloc) -> Address:
    """
    Fixture to return the address to which the authority authorizes to set the code to.
    """
    match request.param:
        case AddressType.EMPTY_ACCOUNT:
            return pre.fund_eoa(0)
        case AddressType.EOA:
            return pre.fund_eoa(1)
        case AddressType.CONTRACT:
            return pre.deploy_contract(Op.STOP)
    raise ValueError(f"Unsupported authorization address case: {request.param}")


@pytest.fixture()
def access_list(
    access_list_case: AccessListType,
    authorization_list_with_validity: List[Tuple[AuthorizationTuple, bool, bool]],
) -> List[AccessList]:
    """
    Fixture to return the access list for the given case.
    """
    access_list: List[AccessList] = []
    if access_list_case == AccessListType.EMPTY:
        return access_list
    if access_list_case.contains_authority():
        for authorization_tuple, _, _ in authorization_list_with_validity:
            already_added = False
            for al in access_list:
                if al.address == authorization_tuple.signer:
                    already_added = True
                    break
            if not already_added:
                access_list.append(
                    AccessList(address=authorization_tuple.signer, storage_keys=[0])
                )
    if access_list_case.contains_set_code_address():
        for authorization_tuple, _, _ in authorization_list_with_validity:
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
def sender(pre: Alloc) -> EOA:
    """
    Fixture to return the sender address.
    """
    return pre.fund_eoa()


# Helper functions to parametrize the tests


def gas_test_parametrize(*, include_many: bool = True, include_data: bool = True):
    """
    Return the parametrize decorator that can be used in all gas test functions.
    """
    MULTIPLE_AUTHORIZATIONS_COUNT = 2
    MANY_AUTHORIZATIONS_COUNT = 5_000

    gas_test_argument_names, gas_test_param = named_pytest_param(
        signer_type=SignerType.SINGLE_SIGNER,
        authorization_invalidity_type=AuthorizationInvalidityType.NONE,
        authorizations_count=1,
        chain_id_type=ChainIDType.GENERIC,
        authorize_to_address=AddressType.EMPTY_ACCOUNT,
        access_list_case=AccessListType.EMPTY,
        self_sponsored=False,
        authority_type=AddressType.EMPTY_ACCOUNT,
        data=b"",
    )

    test_case_list = [
        # TODO: Chain ID type: 0 or correct chain ID
        gas_test_param(
            signer_type=SignerType.SINGLE_SIGNER,
            authorizations_count=1,
            id="single_valid_authorization_single_signer",
        ),
        gas_test_param(
            signer_type=SignerType.SINGLE_SIGNER,
            authorizations_count=1,
            chain_id_type=ChainIDType.CHAIN_SPECIFIC,
            id="single_valid_chain_specific_authorization_single_signer",
        ),
        gas_test_param(
            signer_type=SignerType.SINGLE_SIGNER,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            id="multiple_valid_authorizations_single_signer",
        ),
        gas_test_param(
            signer_type=SignerType.SINGLE_SIGNER,
            authorization_invalidity_type=AuthorizationInvalidityType.INVALID_NONCE,
            authorizations_count=1,
            id="single_invalid_nonce_authorization_single_signer",
        ),
        gas_test_param(
            signer_type=SignerType.SINGLE_SIGNER,
            authorization_invalidity_type=AuthorizationInvalidityType.INVALID_CHAIN_ID,
            authorizations_count=1,
            id="single_invalid_authorization_invalid_chain_id_single_signer",
        ),
        gas_test_param(
            signer_type=SignerType.SINGLE_SIGNER,
            authorization_invalidity_type=AuthorizationInvalidityType.INVALID_NONCE,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            id="multiple_invalid_nonce_authorizations_single_signer",
        ),
        gas_test_param(
            signer_type=SignerType.MULTIPLE_SIGNERS,
            authorization_invalidity_type=AuthorizationInvalidityType.INVALID_NONCE,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            id="multiple_invalid_nonce_authorizations_multiple_signers",
        ),
        gas_test_param(
            signer_type=SignerType.SINGLE_SIGNER,
            authorization_invalidity_type=AuthorizationInvalidityType.INVALID_CHAIN_ID,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            id="multiple_invalid_chain_id_authorizations_single_signer",
        ),
        gas_test_param(
            signer_type=SignerType.MULTIPLE_SIGNERS,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            id="multiple_valid_authorizations_multiple_signers",
        ),
        gas_test_param(
            signer_type=SignerType.SINGLE_SIGNER,
            authorization_invalidity_type=AuthorizationInvalidityType.REPEATED_NONCE,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            id="first_valid_then_single_repeated_nonce_authorization",
        ),
        gas_test_param(
            signer_type=SignerType.MULTIPLE_SIGNERS,
            authorization_invalidity_type=AuthorizationInvalidityType.REPEATED_NONCE,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT * 2,
            id="first_valid_then_single_repeated_nonce_authorizations_multiple_signers",
        ),
        gas_test_param(
            authorize_to_address=AddressType.EOA,
            id="single_valid_authorization_to_eoa",
        ),
        gas_test_param(
            authorize_to_address=AddressType.CONTRACT,
            id="single_valid_authorization_to_contract",
        ),
        gas_test_param(
            access_list_case=AccessListType.CONTAINS_AUTHORITY,
            id="single_valid_authorization_with_authority_in_access_list",
        ),
        gas_test_param(
            access_list_case=AccessListType.CONTAINS_SET_CODE_ADDRESS,
            id="single_valid_authorization_with_set_code_address_in_access_list",
        ),
        gas_test_param(
            access_list_case=AccessListType.CONTAINS_AUTHORITY_AND_SET_CODE_ADDRESS,
            id="single_valid_authorization_with_authority_and_set_code_address_in_access_list",
        ),
        gas_test_param(
            authority_type=AddressType.EOA,
            id="single_valid_authorization_eoa_authority",
        ),
        gas_test_param(
            authority_type=AddressType.EOA,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            id="multiple_valid_authorizations_eoa_authority",
        ),
        gas_test_param(
            self_sponsored=True,
            authority_type=AddressType.EOA,
            id="single_valid_authorization_eoa_self_sponsored_authority",
        ),
        gas_test_param(
            self_sponsored=True,
            authority_type=AddressType.EOA,
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            id="multiple_valid_authorizations_eoa_self_sponsored_authority",
        ),
        gas_test_param(
            authority_type=AddressType.CONTRACT,
            marks=pytest.mark.pre_alloc_modify,
            id="single_valid_authorization_invalid_contract_authority",
        ),
        gas_test_param(
            signer_type=SignerType.MULTIPLE_SIGNERS,
            authority_type=[AddressType.EMPTY_ACCOUNT, AddressType.CONTRACT],
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            marks=pytest.mark.pre_alloc_modify,
            id="multiple_authorizations_empty_account_then_contract_authority",
        ),
        gas_test_param(
            signer_type=SignerType.MULTIPLE_SIGNERS,
            authority_type=[AddressType.EOA, AddressType.CONTRACT],
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            marks=pytest.mark.pre_alloc_modify,
            id="multiple_authorizations_eoa_then_contract_authority",
        ),
        gas_test_param(
            self_sponsored=True,
            signer_type=SignerType.MULTIPLE_SIGNERS,
            authority_type=[AddressType.EOA, AddressType.CONTRACT],
            authorizations_count=MULTIPLE_AUTHORIZATIONS_COUNT,
            marks=pytest.mark.pre_alloc_modify,
            id="multiple_authorizations_eoa_self_sponsored_then_contract_authority",
        ),
    ]
    if include_data:
        test_case_list += [
            gas_test_param(
                data=b"\x01",
                id="single_valid_authorization_with_single_non_zero_byte_data",
            ),
            gas_test_param(
                data=b"\x00",
                id="single_valid_authorization_with_single_zero_byte_data",
            ),
        ]
    if include_many:

        test_case_list += [
            gas_test_param(
                signer_type=SignerType.SINGLE_SIGNER,
                authorizations_count=MANY_AUTHORIZATIONS_COUNT,
                id="many_valid_authorizations_single_signer",
            ),
            gas_test_param(
                signer_type=SignerType.MULTIPLE_SIGNERS,
                authorizations_count=MANY_AUTHORIZATIONS_COUNT,
                id="many_valid_authorizations_multiple_signers",
            ),
            gas_test_param(
                signer_type=SignerType.SINGLE_SIGNER,
                authorization_invalidity_type=AuthorizationInvalidityType.REPEATED_NONCE,
                authorizations_count=MANY_AUTHORIZATIONS_COUNT,
                id="first_valid_then_many_duplicate_authorizations",
            ),
        ]
    return pytest.mark.parametrize(
        gas_test_argument_names,
        test_case_list,
        indirect=["authorize_to_address"],
    )


# Tests


@gas_test_parametrize()
def test_gas_cost(
    state_test: StateTestFiller,
    pre: Alloc,
    authorization_list_with_validity: List[Tuple[AuthorizationTuple, bool, bool]],
    authorization_list: List[AuthorizationTuple],
    data: bytes,
    access_list: List[AccessList],
    sender: EOA,
):
    """
    Test gas at the execution start of a set-code transaction in multiple scenarios.
    """
    intrinsic_gas = (
        21_000
        + eip_2028_transaction_data_cost(data)
        + 1900 * sum(len(al.storage_keys) for al in access_list)
        + 2400 * len(access_list)
    )
    # Calculate the intrinsic gas cost of the authorizations, by default the
    # full empty account cost is charged for each authorization.
    intrinsic_gas += Spec.PER_EMPTY_ACCOUNT_COST * len(authorization_list_with_validity)

    discounted_authorizations = 0
    seen_authority = set()
    for authorization_tuple, valid, empty in authorization_list_with_validity:
        if valid:
            if not empty:
                seen_authority.add(authorization_tuple.signer)
            if authorization_tuple.signer in seen_authority:
                discounted_authorizations += 1
            else:
                seen_authority.add(authorization_tuple.signer)

    discount_gas = (
        Spec.PER_EMPTY_ACCOUNT_COST - Spec.PER_AUTH_BASE_COST
    ) * discounted_authorizations

    # We need a minimum amount of gas to execute the transaction, and the discount gas
    # can actually be used to pay for this, but it's not always enough.
    gas_opcode_cost = 2
    push_opcode_cost = 3
    sstore_opcode_cost = 20_000
    cold_storage_cost = 2_100

    min_execute_gas = gas_opcode_cost + push_opcode_cost + sstore_opcode_cost + cold_storage_cost
    extra_gas = max(0, min_execute_gas - discount_gas)

    expected_gas_measure = discount_gas + extra_gas - gas_opcode_cost

    test_code_storage = Storage()
    test_code = Op.SSTORE(test_code_storage.store_next(expected_gas_measure), Op.GAS) + Op.STOP
    test_code_address = pre.deploy_contract(test_code)

    tx_gas_limit = intrinsic_gas + extra_gas
    tx = Transaction(
        gas_limit=tx_gas_limit,
        to=test_code_address,
        value=0,
        data=data,
        authorization_list=authorization_list,
        access_list=access_list,
        sender=sender,
    )

    state_test(
        env=Environment(gas_limit=max(tx_gas_limit, 30_000_000)),
        pre=pre,
        tx=tx,
        post={
            test_code_address: Account(storage=test_code_storage),
        },
    )


@gas_test_parametrize(
    include_many=False,
    include_data=False,
)
def test_account_warming(
    state_test: StateTestFiller,
    pre: Alloc,
    authorization_list_with_validity: List[Tuple[AuthorizationTuple, bool, bool]],
    authorization_list: List[AuthorizationTuple],
    access_list_case: AccessListType,
    access_list: List[AccessList],
    authorize_to_address: Address,
    data: bytes,
    sender: EOA,
):
    """
    Test warming of the authority and authorized accounts for set-code transactions.
    """
    overhead_cost = 3

    addresses_to_check: Dict[Address, bool] = {}

    for authorization_tuple, valid, _ in authorization_list_with_validity:
        authority = authorization_tuple.signer
        assert authority is not None, "authority address is not set"
        if authority not in addresses_to_check:
            addresses_to_check[authority] = valid or access_list_case.contains_authority()

    if authorize_to_address not in addresses_to_check:
        addresses_to_check[authorize_to_address] = access_list_case.contains_set_code_address()

    callee_storage = Storage()
    callee_code: Bytecode = sum(  # type: ignore
        (
            CodeGasMeasure(
                code=Op.EXTCODESIZE(check_address),
                overhead_cost=overhead_cost,
                extra_stack_items=1,
                sstore_key=callee_storage.store_next(100 if warm else 2600),
                stop=False,
            )
            for check_address, warm in addresses_to_check.items()
        )
    )
    callee_code += Op.STOP
    callee_address = pre.deploy_contract(callee_code, storage=callee_storage.canary())

    tx = Transaction(
        gas_limit=1_000_000,
        to=callee_address,
        authorization_list=authorization_list,
        access_list=access_list,
        sender=sender,
        data=data,
    )
    post = {
        callee_address: Account(
            storage=callee_storage,
        ),
    }

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@gas_test_parametrize()
@pytest.mark.parametrize(
    "valid",
    [True, False],
)
def test_intrinsic_gas_cost(
    state_test: StateTestFiller,
    pre: Alloc,
    authorization_list: List[AuthorizationTuple],
    data: bytes,
    access_list: List[AccessList],
    sender: EOA,
    valid: bool,
):
    """
    Test sending a transaction with the exact intrinsic gas required and also insufficient
    gas.
    """
    intrinsic_gas = (
        21_000
        + eip_2028_transaction_data_cost(data)
        + 1900 * sum(len(al.storage_keys) for al in access_list)
        + 2400 * len(access_list)
    )
    # Calculate the intrinsic gas cost of the authorizations, by default the
    # full empty account cost is charged for each authorization.
    intrinsic_gas += Spec.PER_EMPTY_ACCOUNT_COST * len(authorization_list)

    tx_gas = intrinsic_gas
    if not valid:
        tx_gas -= 1

    test_code = Op.STOP
    test_code_address = pre.deploy_contract(test_code)

    tx = Transaction(
        gas_limit=tx_gas,
        to=test_code_address,
        value=0,
        data=data,
        authorization_list=authorization_list,
        access_list=access_list,
        sender=sender,
        error=TransactionException.INTRINSIC_GAS_TOO_LOW if not valid else None,
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={},
    )
