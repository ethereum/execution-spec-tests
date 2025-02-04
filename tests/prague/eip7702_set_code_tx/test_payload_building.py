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
) -> None:
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
