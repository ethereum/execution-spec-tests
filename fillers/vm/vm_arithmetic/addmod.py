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


@test_from("shanghai")
def test_addmod_opcode(fork):
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
            {
            switch calladdr
                case 0x100 {
                    sstore(0, addmod(1, 2, 2))
                }
                case 0x101 {
                    sstore(0, addmod(sub(0, 1), sub(0, 2), 2))
                }
                case 0x102 {
                    sstore(0, addmod(sub(0, 6), 1, 3))
                }
                case 0x103 {
                    sstore(0, eq(smod(sub(0, 5), 3), addmod(sub(0, 6), 1, 3)))
                }
                case 0x104 {
                    sstore(0, eq(mod(sub(0,5), 3), addmod(sub(0, 6), 1, 3)))
                }
                case 0x105 {
                    sstore(0, addmod(4, 1, sub(0, 3)))
                }
                case 0x106 {
                    sstore(0, eq(addmod(4, 1, sub(0, 3)), 2))
                }
                case 0x107 {
                    sstore(0, addmod(sub(0, 1), 0, 5))
                }
                case 0x108 {
                    sstore(0, addmod(sub(0, 1), 1, 5))
                }
                case 0x109 {
                    sstore(0, addmod(sub(0, 1),  2, 5))
                }
                case 0x10a {
                    sstore(0, addmod(sub(0, 1), sub(0, 2), 5))
                }
                case 0x10b {
                    sstore(0, addmod(sub(0, 1), 1, 5))
                }
                case 0x10c {
                    sstore(0, addmod(4, 1, 0))
                }
                case 0x10d {
                    sstore(0, addmod(0, 1, 0))
                }
                case 0x10e {
                    sstore(0, addmod(1, 0, 0))
                }
                case 0x10f {
                    sstore(0, sub(addmod(0, 0, 0), 1))
                }
            }
        }
        """
    )

    total_tests = 16
    solutions = {
        to_address(0x100): 0x01,
        to_address(0x101): 0x01,
        to_address(0x102): 0x02,
        to_address(0x103): 0x00,
        to_address(0x104): 0x01,
        to_address(0x105): 0x05,
        to_address(0x106): 0x00,
        to_address(0x107): 0x00,
        to_address(0x108): 0x01,
        to_address(0x109): 0x02,
        to_address(0x10A): 0x04,
        to_address(0x10B): 0x01,
        to_address(0x10C): 0x00,
        to_address(0x10D): 0x00,
        to_address(0x10E): 0x00,
        to_address(0x10F): to_hash(-1),
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
