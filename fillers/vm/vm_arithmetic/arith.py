"""
Test Arith (basic)
"""

from ethereum_test_tools import Account, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    StateTest,
    TestAddress,
    Transaction,
    test_from,
    to_address,
    to_hash,
)


@test_from("istanbul")
def test_arith(fork):  # noqa
    """
    Basic Arithmetic Test
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/arithFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []
    post = {}

    code_arith = (
        Op.PUSH1(1)
        + Op.PUSH1(1)
        + Op.SWAP1()
        + Op.ADD()
        + Op.PUSH1(7)
        + Op.MUL()
        + Op.PUSH1(5)
        + Op.ADD()
        + Op.PUSH1(2)
        + Op.SWAP1()
        + Op.DIV()
        + Op.PUSH1(4)
        + Op.SWAP1()
        + Op.PUSH1(0x21)
        + Op.SWAP1()
        + Op.SDIV()
        + Op.PUSH1(0x17)
        + Op.ADD()
        + Op.PUSH1(3)
        + Op.MUL()
        + Op.PUSH1(5)
        + Op.SWAP1()
        + Op.SMOD()
        + Op.PUSH1(3)
        + Op.SUB()
        + Op.PUSH1(9)
        + Op.PUSH1(0x11)
        + Op.EXP()
        + Op.PUSH1(0)
        + Op.SSTORE()
        + Op.PUSH1(8)
        + Op.PUSH1(0)
        + Op.RETURN()
    )

    solution = {
        to_address(0x100): 0x1B9C636491,
    }

    account = to_address(0x100)
    pre[account] = Account(code=code_arith)

    tx = Transaction(
        nonce=0,
        data=to_hash(0x100),
        to=account,
        gas_limit=500000,
        gas_price=10,
    )

    txs.append(tx)
    post[account] = Account(storage={0: solution[account]})

    yield StateTest(env=env, pre=pre, post=post, txs=txs)
