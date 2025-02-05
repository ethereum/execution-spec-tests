"""Test payload building when type-4 transactions are sent to the client."""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    AuthorizationTuple,
    Payload,
    PayloadBuildingTestFiller,
    Storage,
    TransactionException,
    TransactionWithPost,
)
from ethereum_test_tools import Opcodes as Op

from .spec import Spec, ref_spec_7702

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version

pytestmark = pytest.mark.valid_from("Prague")


def test_single_type_4_transaction(
    payload_building_test: PayloadBuildingTestFiller,
    pre: Alloc,
):
    """Test payload building with a single type-4 transaction."""
    storage = Storage()

    auth_signer = pre.fund_eoa()
    sender = pre.fund_eoa()

    set_code = (
        Op.SSTORE(storage.store_next(sender), Op.ORIGIN)
        + Op.SSTORE(storage.store_next(sender), Op.CALLER)
        + Op.SSTORE(storage.store_next(1), Op.CALLVALUE)
        + Op.STOP
    )
    set_code_to_address = pre.deploy_contract(
        set_code,
    )

    tx = TransactionWithPost(
        gas_limit=500_000,
        to=auth_signer,
        value=1,
        max_priority_fee_per_gas=1,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=sender,
        post={
            set_code_to_address: Account(
                storage={k: 0 for k in storage},
            ),
            auth_signer: Account(
                nonce=1,
                code=Spec.delegation_designation(set_code_to_address),
                storage=storage,
            ),
        },
    )

    payload_building_test(
        pre=pre,
        steps=[
            tx,
            Payload(
                sorted_transactions=[tx],
            ),
        ],
    )


def test_accounts_with_delegation_set_can_only_have_one_in_flight_transaction(
    payload_building_test: PayloadBuildingTestFiller,
    pre: Alloc,
):
    """Test that an account with a delegation set can only have one in-flight transaction."""
    storage = Storage()

    auth_signer = pre.fund_eoa()
    sender = pre.fund_eoa()

    set_code = (
        Op.SSTORE(storage.store_next(sender), Op.ORIGIN)
        + Op.SSTORE(storage.store_next(sender), Op.CALLER)
        + Op.SSTORE(storage.store_next(1), Op.CALLVALUE)
        + Op.STOP
    )
    set_code_to_address = pre.deploy_contract(
        set_code,
    )

    set_code_tx = TransactionWithPost(
        gas_limit=500_000,
        to=auth_signer,
        value=1,
        max_priority_fee_per_gas=1,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=sender,
        post={
            set_code_to_address: Account(
                storage={k: 0 for k in storage},
            ),
            auth_signer: Account(
                nonce=1,
                code=Spec.delegation_designation(set_code_to_address),
                storage=storage,
            ),
        },
    )

    tx_from_set_code_1 = TransactionWithPost(
        gas_limit=100_000,
        to=Address(1),
        value=0,
        max_priority_fee_per_gas=1,
        sender=auth_signer,
        nonce=1,
    )
    tx_from_set_code_2 = TransactionWithPost(
        gas_limit=100_000,
        to=Address(2),
        value=0,
        max_priority_fee_per_gas=1,
        sender=auth_signer,
        error=TransactionException.SEND_RAW_TRANSACTION_ERROR,
        nonce=2,
    )

    payload_building_test(
        pre=pre,
        steps=[
            set_code_tx,
            Payload(
                sorted_transactions=[set_code_tx],
            ),
            tx_from_set_code_1,
            tx_from_set_code_2,
        ],
    )


@pytest.mark.parametrize(
    "auth_nonce",
    [
        0,
        1,
    ],
)
def test_set_code_tx_should_be_rejected_if_any_authority_has_a_known_pooled_tx(
    payload_building_test: PayloadBuildingTestFiller,
    pre: Alloc,
    auth_nonce: int,
):
    """
    Test that a set code transaction should be rejected if any authority has a known pooled
    transaction.
    """
    storage = Storage()

    auth_signer = pre.fund_eoa()
    sender = pre.fund_eoa()

    set_code = (
        Op.SSTORE(storage.store_next(sender), Op.ORIGIN)
        + Op.SSTORE(storage.store_next(sender), Op.CALLER)
        + Op.SSTORE(storage.store_next(1), Op.CALLVALUE)
        + Op.STOP
    )
    set_code_to_address = pre.deploy_contract(
        set_code,
    )

    tx_from_set_code = TransactionWithPost(
        gas_limit=100_000,
        to=Address(1),
        value=2,
        max_priority_fee_per_gas=1,
        sender=auth_signer,
        post={
            Address(1): Account(
                balance=2,
            ),
        },
    )

    set_code_tx = TransactionWithPost(
        gas_limit=500_000,
        to=auth_signer,
        value=1,
        max_priority_fee_per_gas=1,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=auth_nonce,
                signer=auth_signer,
            ),
        ],
        sender=sender,
        error=TransactionException.SEND_RAW_TRANSACTION_ERROR,
    )

    payload_building_test(
        pre=pre,
        steps=[
            tx_from_set_code,
            set_code_tx,
            Payload(
                sorted_transactions=[tx_from_set_code],
            ),
        ],
    )


@pytest.mark.parametrize(
    "auth_tx_nonce",
    [
        0,
        1,
    ],
)
def test_new_txs_from_senders_with_pooled_delegations_should_not_be_accepted(
    payload_building_test: PayloadBuildingTestFiller,
    pre: Alloc,
    auth_tx_nonce: int,
):
    """Test that new transactions from senders with pooled delegations should not be accepted."""
    storage = Storage()

    auth_signer = pre.fund_eoa()
    sender = pre.fund_eoa()

    set_code = (
        Op.SSTORE(storage.store_next(sender), Op.ORIGIN)
        + Op.SSTORE(storage.store_next(sender), Op.CALLER)
        + Op.SSTORE(storage.store_next(1), Op.CALLVALUE)
        + Op.STOP
    )
    set_code_to_address = pre.deploy_contract(
        set_code,
    )

    set_code_tx = TransactionWithPost(
        gas_limit=500_000,
        to=auth_signer,
        value=1,
        max_priority_fee_per_gas=1,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=sender,
        post={
            set_code_to_address: Account(
                storage={k: 0 for k in storage},
            ),
            auth_signer: Account(
                nonce=1,
                code=Spec.delegation_designation(set_code_to_address),
                storage=storage,
            ),
        },
    )

    tx_from_set_code = TransactionWithPost(
        gas_limit=100_000,
        nonce=auth_tx_nonce,
        to=Address(1),
        value=2,
        max_priority_fee_per_gas=1,
        sender=auth_signer,
        error=TransactionException.SEND_RAW_TRANSACTION_ERROR,
    )

    payload_building_test(
        pre=pre,
        steps=[
            set_code_tx,
            tx_from_set_code,
            Payload(
                sorted_transactions=[set_code_tx],
            ),
        ],
    )
