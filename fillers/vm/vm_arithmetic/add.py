"""
Test Add opcode
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


@test_from("istanbul")
def test_add_opcode(fork):
    """
    Test Add Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/addFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []
    post = {}

    code_sums = Yul(
        """
        {
            let calladdr := calldataload(0)
            let x := 0
            let y := 0
            {
            switch calladdr
                // -1 + -1 = -2
                case 0x100 {
                    x := sub(0, 1)
                    y := sub(0, 1)
                }
                // -1 + 4 = 3
                case 0x101 {
                    x := sub(0, 1)
                    y := 4
                }
                // -1 + 1 = 0
                case 0x102 {
                    x := sub(0, 1)
                    y := 1
                }
                // 0 + 0 = 0
                case 0x103 {
                    x := 0
                    y := 0
                }
                // 1 + -1 = 0
                case 0x104 {
                    x := 1
                    y := sub(0, 1)
                }
            }
            sstore(0, add(x, y))
        }
        """
    )

    total_tests = 5
    solutions = {
        to_address(0x100): to_hash(-2),
        to_address(0x101): 0x03,
        to_address(0x102): 0x00,
        to_address(0x103): 0x00,
        to_address(0x104): 0x00,
    }

    for i in range(0, total_tests):
        account = to_address(0x100 + i)
        pre[account] = Account(code=code_sums)

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
