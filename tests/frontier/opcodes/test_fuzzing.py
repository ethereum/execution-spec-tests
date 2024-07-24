"""
Test fuzzer example.
"""

import random
from typing import Annotated

import pytest

from ethereum_test_forks import Fork, Frontier, Homestead
from ethereum_test_tools import Account, Alloc, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Transaction


@pytest.mark.parametrize(
    "key,value",
    [(1, 1)],
)
@pytest.mark.fuzzable("key", "value")
def test_sstore(
    state_test: StateTestFiller,
    fork: Fork,
    pre: Alloc,
    key: Annotated[int, lambda: random.randint(0, 2**64)],
    value: int,
):
    """
    Simple SSTORE test that can be fuzzed to generate any number of tests.
    """
    env = Environment()
    sender = pre.fund_eoa()
    post = {}

    account_code = Op.SSTORE(key, value) + Op.STOP

    account = pre.deploy_contract(account_code)

    tx = Transaction(
        to=account,
        gas_limit=500000,
        data="",
        sender=sender,
        protected=False if fork in [Frontier, Homestead] else True,
    )

    post = {
        account: Account(
            storage={
                key: value,
            }
        )
    }

    state_test(env=env, pre=pre, post=post, tx=tx)
