"""Test payload building when type-4 transactions are sent to the client."""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    AuthorizationTuple,
    Payload,
    PayloadBuildingTestFiller,
    Storage,
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
            Payload(),
        ],
    )


@pytest.mark.parametrize(
    "order",
    [
        "normal_tx_first",
        "set_code_tx_first",
    ],
)
def test_type_4_transaction_invalidate_single_tx(
    payload_building_test: PayloadBuildingTestFiller,
    pre: Alloc,
    order: str,
):
    """
    Test payload building with a single type-4 transaction invalidating a different
    transaction.
    """
    auth_signer = pre.fund_eoa()
    sender = pre.fund_eoa()

    normal_tx_recipient = pre.fund_eoa(amount=0)
    normal_tx = TransactionWithPost(
        gas_limit=500_000,
        to=normal_tx_recipient,
        value=1,
        max_priority_fee_per_gas=1,
        sender=auth_signer,
        nonce=0,
        post={
            normal_tx_recipient: Account(
                balance=1,
            ),
        },
    )

    set_code = Op.STOP
    set_code_to_address = pre.deploy_contract(set_code)

    set_code_tx_recipient = pre.fund_eoa(amount=0)
    set_code_tx = TransactionWithPost(
        gas_limit=500_000,
        to=set_code_tx_recipient,
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
            set_code_tx_recipient: Account(
                balance=1,
            ),
        },
        invalidates=[normal_tx],
    )

    if order == "normal_tx_first":
        txs = [normal_tx, set_code_tx]
    else:
        txs = [set_code_tx, normal_tx]

    payload_building_test(
        pre=pre,
        steps=[
            *txs,
            Payload(),  # Should include either transaction
            Payload(),  # Empty payload
        ],
    )


@pytest.mark.parametrize(
    "order",
    [
        "normal_txs_first",
        "set_code_tx_first",
    ],
)
def test_type_4_transaction_invalidate_multiple_txs(
    payload_building_test: PayloadBuildingTestFiller,
    pre: Alloc,
    order: str,
):
    """
    Test payload building with a single type-4 transaction invalidating multiple different
    transactions from different EOAs each.
    """
    auth_signer_count = 100
    auth_signers = [pre.fund_eoa() for _ in range(auth_signer_count)]
    sender = pre.fund_eoa()

    normal_txs = []
    for auth_signer in auth_signers:
        normal_tx_recipient = pre.fund_eoa(amount=0)
        normal_txs.append(
            TransactionWithPost(
                gas_limit=500_000,
                to=normal_tx_recipient,
                value=1,
                max_priority_fee_per_gas=1,
                sender=auth_signer,
                nonce=0,
                post={
                    normal_tx_recipient: Account(
                        balance=1,
                    ),
                },
            )
        )

    set_code = Op.STOP
    set_code_to_address = pre.deploy_contract(set_code)

    set_code_tx_recipient = pre.fund_eoa(amount=0)
    set_code_tx = TransactionWithPost(
        gas_limit=500_000,
        to=set_code_tx_recipient,
        value=1,
        max_priority_fee_per_gas=1,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            )
            for auth_signer in auth_signers
        ],
        sender=sender,
        post={
            set_code_tx_recipient: Account(
                balance=1,
            ),
        },
        invalidates=normal_txs,
    )

    if order == "normal_txs_first":
        txs = [*normal_txs, set_code_tx]
    else:
        txs = [set_code_tx, *normal_txs]

    payload_building_test(
        pre=pre,
        steps=[
            *txs,
            Payload(),  # Should include some of the transactions
            Payload(),  # Empty payload
        ],
    )
