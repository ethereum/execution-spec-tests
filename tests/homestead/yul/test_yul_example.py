"""
Test Yul Source Code Examples
"""

import pytest

from ethereum_test_forks import Fork, Frontier, Homestead
from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
    YulCompiler,
)


@pytest.fixture
def env():  # noqa: D103
    return Environment()


@pytest.fixture
def pre(yul: YulCompiler):  # noqa: D103
    return {
        "0x1000000000000000000000000000000000000000": Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=yul(
                """
            {
                function f(a, b) -> c {
                    c := add(a, b)
                }

                sstore(0, f(1, 2))
                return(0, 32)
            }
            """
            ),
        ),
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
    }


@pytest.fixture
def tx(fork):  # noqa: D103
    return Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to="0x1000000000000000000000000000000000000000",
        gas_limit=500000,
        gas_price=10,
        protected=False if fork in [Frontier, Homestead] else True,
    )


@pytest.fixture
def post():  # noqa: D103
    return {
        "0x1000000000000000000000000000000000000000": Account(
            storage={
                0x00: 0x03,
            },
        ),
    }


@pytest.mark.valid_from("Homestead")
def test_yul(state_test: StateTestFiller, env, pre, tx, post):
    """
    Test YUL compiled bytecode.
    """
    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.valid_from("Homestead")
def test_yul_blockchain(blockchain_test: BlockchainTestFiller, pre, tx, post):
    """
    Test YUL compiled bytecode.
    """
    blocks = [Block(txs=[tx])]
    blockchain_test(pre=pre, post=post, blocks=blocks)
