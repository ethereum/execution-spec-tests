"""
Test Div by Zero:
    # Original test by Ori Pomerantz qbzzt1@gmail.com
    # Port from ethereum/tests:
    #   - GeneralStateTestsFiller/VMTests/vmTest/divByZeroFiller.yml
    #   - Original test by Ori Pomerantz qbzzt1@gmail.com
    #
    # A standard location for division by zero tests.
    #
    # Opcodes where this is relevant:
    #   DIV
    #
    # Any division or mod by zero returns zero.
"""

from ethereum_test_tools import Account, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    StateTest,
    TestAddress,
    Transaction,
    test_from,
    to_address,
)


@test_from("istanbul")
def test_div_by_zero(fork):
    """
    Test division by zero.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/divByZeroFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []

    div_values = [2, 1, 0]
    for i in range(0, len(div_values)):
        address = to_address(0x100 + i)
        a = div_values[i]

        code_div = (
            # Push 0
            # Push a
            # Div(a, 0)
            Op.PUSH1(0)
            + Op.PUSH1(a)
            + Op.DIV
            # Push 0
            # sstore(0, div(a,0))
            + Op.PUSH1(i)
            + Op.SSTORE(3, 1)
            + Op.STOP
        )

        pre[address] = Account(code=code_div)

        tx = Transaction(
            nonce=i,
            to=address,
            gas_limit=100000000,
            gas_price=10,
        )
        txs.append(tx)

        post = {address: Account(storage={i: 0x00})}

    yield StateTest(env=env, pre=pre, post=post, txs=txs)
