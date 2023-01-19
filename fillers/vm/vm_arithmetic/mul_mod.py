"""
Test mulmod opcode
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
def test_mulmod_opcode(fork):
    """
    Test mulmod Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/mulmodFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []
    post = {}

    code_mulmod = Yul(
        """
        {
            let calladdr := calldataload(0)
            {
            switch calladdr
                case 0x100 {
                    // (1*2) % 2 is zero
                    sstore(0, mulmod(1, 2, 2))
                }
                case 0x101 {
                    // -a is actually 2^256-a
                    //  2^256 % 3 = 1
                    //  (2^256-1) % 3 = (1-1)%3 = 0
                    sstore(0, mulmod(sub(0, 1), sub(0, 2), 3))
                }
                case 0x102 {
                    // -5 % 3 = (2^256 - 5) % 3 = (1-2)%3 = (-1) % 3 = 2
                    sstore(0, mulmod(sub(0, 5), 1, 3))
                }
                case 0x103 {
                    // -3 is actually 2^256-3, which is much more than five
                    sstore(0, mulmod(5, 1, sub(0, 3)))
                }
                case 0x104 {
                    sstore(0, mulmod(27, 37, 100))
                }
                case 0x105 {
                    sstore(0, mulmod(exp(2, 255), 2, 5))
                }
                case 0x106 {
                    // (256^2-1) % 5 = 0
                    sstore(0, mulmod(sub(0, 1), 2, 5))
                }
                case 0x107 {
                    // 2^255%5 = 3
                    //     2%5 = 2
                    // (3-1) * 2 = 4
                    sstore(0, mulmod(sub(exp(2, 255), 1), 2, 5))
                }
                case 0x108 {
                    // 2^255%5 = 3
                    //     2%5 = 2
                    // ((3+1) * 2) % 5 = 3
                    sstore(0, mulmod(add(exp(2, 255), 1), 2, 5))
                }
                case 0x109 {
                    // smod   is signed mod, -5%3 = -1
                    // mulmod is unsigned mod, -5%3 = 2
                    // -1 != 2
                    sstore(0, eq(smod(sub(0, 5), 3), mulmod(sub(0, 5),  1, 3)))
                }
                case 0x10a {
                    // mod and mulmod are both unsigned mod
                    // equal
                    sstore(0, eq(mod(sub(0, 5), 3), mulmod(sub(0, 5),  1, 3)))
                }
                case 0x10b {
                    // (mulmod a b -c) is usually a*b, because -c is
                    // actually 2^256-c, which is huge
                    // not equal
                    sstore(0, eq(mulmod(5, 1, sub(0, 3)), 2))
                }
                case 0x10c {
                    // (mulmod x y 0) is zero  0
                    sstore(0, mulmod(0, 1, 0))
                }
                case 0x10d {
                    // (mulmod x y 0) is zero  0
                    sstore(0, mulmod(1, 0, 0))
                }
                case 0x10e {
                    // (mulmod x y 0) is zero  0
                    sstore(0, sub(1, mulmod(1, 0, 0)))
                }
                case 0x10f {
                    // (mulmod x y 0) is zero  0
                    sstore(0, mulmod(5, 1, 0))
                }
            }
        }
        """
    )

    total_tests = 16
    solutions = {
        to_address(0x100): 0x00,
        to_address(0x101): 0x00,
        to_address(0x102): 0x02,
        to_address(0x103): 0x05,
        to_address(0x104): 0x63,
        to_address(0x105): 0x01,
        to_address(0x106): 0x00,
        to_address(0x107): 0x04,
        to_address(0x108): 0x03,
        to_address(0x109): 0x00,
        to_address(0x10A): 0x01,
        to_address(0x10B): 0x00,
        to_address(0x10C): 0x00,
        to_address(0x10D): 0x00,
        to_address(0x10E): 0x01,
        to_address(0x10F): 0x00,
    }

    for i in range(0, total_tests):
        account = to_address(0x100 + i)
        pre[account] = Account(code=code_mulmod)

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
