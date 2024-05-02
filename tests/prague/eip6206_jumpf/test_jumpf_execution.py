"""
Execution of CALLF, RETF opcodes within EOF V1 containers tests
"""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.eof.v1 import Container

from .contracts import VALID, container_name
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6206.md"
REFERENCE_SPEC_VERSION = "a1775816657df4093787fb9fe83c2f7cc17ecf47"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "container",
    VALID,
    ids=container_name,
)
def test_jumpf_execution(
    state_test: StateTestFiller,
    container: Container,
):
    """
    Test JUMPF valid contracts.  All should end with the same canary
    """
    assert (
        container.validity_error is None
    ), f"Valid container with validity error: {container.validity_error}"

    env = Environment()

    pre = {
        TestAddress: Account(
            balance=1000000000000000000000,
            nonce=1,
        ),
        Address(0x100): Account(
            code=container,
            nonce=1,
        ),
    }

    tx = Transaction(
        nonce=1,
        to=Address(0x100),
        gas_limit=44_000,
        gas_price=10,
        protected=False,
        data="1",
    )

    post = {Address(0x100): Account(storage={0: 1})}

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )
