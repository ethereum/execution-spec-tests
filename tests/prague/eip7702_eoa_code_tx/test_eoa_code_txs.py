"""
abstract: Tests use of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702)
    Tests use of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702).
"""  # noqa: E501

import pytest

from ethereum_test_tools import Alloc, AuthorizationTuple, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Transaction

from .spec import ref_spec_7702

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version

pytestmark = [
    pytest.mark.valid_from("Prague"),
]


def test_set_code_to_self_destruct(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test the executing self-destruct opcode in a set-code transaction.
    """
    set_code_to_address = pre.deploy_contract(Op.SELFDESTRUCT(Op.ADDRESS))

    signer = pre.fund_eoa(0)

    sender = pre.fund_eoa(10**18)

    tx = Transaction(
        gas_limit=1_000_000,
        to=sender,
        value=0,
        authorization_tuples=[
            AuthorizationTuple(
                chain_id=1,
                address=set_code_to_address,
                nonce=0,
                signer=signer,
            ),
        ],
        sender=sender,
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={},
    )
