"""
Test Div opcode
"""

from ethereum_test_tools import (
    Account,
    Environment,
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    test_from,
    to_address,
    to_hash,
)


@test_from("shanghai")
def test_div_opcode(fork):
    """
    Test Div Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/divFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []
    post = {}

    code_div = Yul(
        """
        {
            let calladdr := calldataload(0)
            {
            switch calladdr
                case 0x100 {
                    sstore(0, div(
                        2,
                        0xfedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210
                        )
                    )
                }
                case 0x101 {
                    sstore(0, div(
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFBA,
                        0x1DAE6076B981DAE6076B981DAE6076B981DAE6076B981DAE6076B981DAE6077
                        )
                    )
                }
                case 0x102 {
                    sstore(0, div(5, 2))
                }
                case 0x103 {
                    sstore(0, div(23, 24))
                }
                case 0x104 {
                    sstore(0, div(0, 24))
                }
                case 0x105 {
                    sstore(0, div(1, 1))
                }
                case 0x106 {
                    sstore(0, div(2, 0))
                }
                case 0x107 {
                    sstore(0, add(div(13, 0), 7))
                }
            }
        }
        """
    )

    total_tests = 8
    solutions = {
        to_address(0x100): 0x00,  # div_2_big
        to_address(0x101): 0x89,  # div_boost_bug
        to_address(0x102): 0x02,
        to_address(0x103): 0x00,
        to_address(0x104): 0x00,
        to_address(0x105): 0x01,
        to_address(0x106): 0x00,
        to_address(0x107): 0x07,
    }

    for i in range(0, total_tests):
        account = to_address(0x100 + i)
        pre[account] = Account(code=code_div)

        tx = Transaction(
            nonce=i,
            data=to_hash(0x100 + i),
            to=account,
            gas_limit=500000,
            gas_price=10,
        )

        txs.append(tx)
        post[account] = Account(storage={0: solutions[account]})

    yield StateTest(env=env, pre=pre, post=post, txs=txs)
