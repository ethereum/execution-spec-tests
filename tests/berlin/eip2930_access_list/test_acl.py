"""Test ACL Transaction Source Code Examples."""

import time
import pytest

from ethereum_test_tools import (
    AccessList,
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-2930.md"
REFERENCE_SPEC_VERSION = "c9db53a936c5c9cbe2db32ba0d1b86c4c6e73534"


@pytest.mark.valid_from("Berlin")
def test_access_list(state_test: StateTestFiller, pre: Alloc):
    """Test type 1 transaction."""
    env = Environment()

    contract_address = pre.deploy_contract(
        Op.PC + Op.SLOAD + Op.POP + Op.PC + Op.SLOAD,
        balance=0x03,
    )

    sender = pre.fund_eoa(10000000000000001)

    tx = Transaction(
        ty=1,
        to=contract_address,
        value=1,
        gas_limit=1_000_000,
        access_list=[
            AccessList(
                address="0x0000000000000000000000000000000000000000",
                storage_keys=[
                    "0x0000000000000000000000000000000000000000000000000000000000000000",
                ],
            )
        ],
        protected=True,
        sender=sender,
    )

    post = {
        contract_address: Account(
            code="0x5854505854",
            balance=4,
            nonce=1,
        ),
        sender: Account(
            balance=9970494000000000,
            nonce=1,
        ),
    }
    state_test(env=env, pre=pre, post=post, tx=tx)
