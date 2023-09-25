"""
Test EIP-6968: Contract Secured Revenue
EIP: https://eips.ethereum.org/EIPS/eip-6968
"""

import pytest

from ethereum_test_forks import Fork

from ethereum_test_tools import (
    AddrAA,
    Account,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
    to_address,
)

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6968.md"
REFERENCE_SPEC_VERSION = "7500ac4fc1bbdfaf684e7ef851f798f6b667b2fe"


@pytest.mark.valid_from("London")
def test_simple_tx(state_test: StateTestFiller, fork: Fork):
    """
    Test that EOA to EOA transfer behavior does not change.
    """
    env = Environment()
    balance = 1000000000000000000000

    pre = {
        TestAddress: Account(balance=balance),
        AddrAA: Account(balance=100),
    }
    tx = Transaction(
        to=to_address("0xaa"),
        gas_price=10,
    )
    post = {
        TestAddress: Account(balance=balance - 10 * 21000),
        AddrAA: Account(balance=100),
    }

    state_test(env=env, pre=pre, post=post, txs=[tx])
