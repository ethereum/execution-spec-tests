"""
Test Arith (basic)
"""

from ethereum_test_tools import (
    Account,
    Environment,
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

    code_arith = (  # noqa
        # noqa: 00 PUSH1 1      6001                      1
        # noqa: 02 PUSH1 1      6001                      1,1
        # noqa: 04 SWAP1        90
        # noqa: 05 ADD          01                        2
        # noqa: 06 PUSH1 7      6007                      7,2
        # noqa: 08 MUL          02                        14
        # noqa: 09 PUSH1 5      6005                      5,14
        # noqa: 0B ADD          01                        19
        # noqa: 0C PUSH1 2      6002                      2,19
        # noqa: 0E SWAP1        90                        19,2
        # noqa: 0F DIV          04                        9
        # noqa: 10 PUSH1 4      6004                      4,9
        # noqa: 12 SWAP1        90                        9,4
        # noqa: 13 PUSH1 0x21   6021                      33,9,4
        # noqa: 15 SWAP1        90                        9,33,4
        # noqa: 16 SDIV         05                        0,4
        # noqa: 17 PUSH1 0x17   6017                      21,0,4
        # noqa: 19 ADD          01                        21,4
        # noqa: 1A PUSH1 3      6003                      3,21,4
        # noqa: 1C MUL          02                        63,4
        # noqa: 1D PUSH1 5      6005                      5,63,4
        # noqa: 1F SWAP1        90                        63,5,4
        # noqa: 20 SMOD         07                        3,4
        # noqa: 21 PUSH1 3      6003                      3,3,4
        # noqa: 23 SUB          03                        0,4
        # noqa: 24 PUSH1 9      6009                      9,0,4
        # noqa: 26 PUSH1 0x11   6011                      17,9,0,4
        # noqa: 28 EXP          0A                        17^9,0,4
        # noqa: 29 PUSH1 0      6000                      0,17^9,0,4
        # noqa: 2B SSTORE       55 The original was MSTORE, but that's not testable
        # noqa: 2C PUSH1 8      6008                      8,0,4
        # noqa: 2E PUSH1 0      6000                      0,8,0,4
        # noqa: 30 RETURN       F3
        "0x60016001900160070260050160029004600490602190056017016\
            0030260059007600303600960110A60005560086000F3"
    )

    solution = {
        to_address(0x100): 0x1B9C636491,
    }

    account = to_address(0x100)
    pre[account] = Account(code=code_arith)  # noqa

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
