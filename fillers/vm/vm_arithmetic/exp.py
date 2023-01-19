"""
Test Exponentiation opcode
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
def test_exp_opcode(fork):
    """
    Test Exp Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/expFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []
    post = {}

    code_exp = Yul(
        """
        {
            let calladdr := calldataload(0)
            {
            switch calladdr
                case 0x100 {
                    sstore(0, exp(2, 2))
                }
                case 0x101 { // -1**-2
                    sstore(0, exp(sub(0, 1), sub(0, 2)))
                }
                case 0x102 { // just a big number to the power of itself
                    sstore(0, exp(2147483647, 2147483647))
                }
                case 0x103 { // 0 to the power of a big number
                    sstore(0, exp(0, 2147483647))
                }
                case 0x104 { // big number to the power of 0
                    sstore(0, exp(2147483647, 0))
                }
                case 0x105 { // 257**1
                    sstore(0, exp(257, 1))
                }
                case 0x106 { // 1**257
                    sstore(0, exp(1, 257))
                }
                case 0x107 { // 2**257 (zero mod 2**256)
                    sstore(0, exp(2, 257))
                }
                case 0x108 { // 0**0 (1 in evm)
                    sstore(0, exp(0, 0))
                }
                case 0x109 { // 2**big = 0
                    sstore(0, exp(2, 0x0100000000000f))
                }
                case 0x10a { // 2**15 = 0x8000
                    sstore(0, exp(2, 15))
                }
            }
        }
        """
    )

    total_tests = 11
    solutions = {
        to_address(0x100): 0x04,
        to_address(0x101): 0x01,
        to_address(
            0x102
        ): 0xBC8CCCCCCCC888888880000000AAAAAAB00000000FFFFFFFFFFFFFFF7FFFFFFF,
        to_address(0x103): 0x00,
        to_address(0x104): 0x01,
        to_address(0x105): 0x0101,
        to_address(0x106): 0x01,
        to_address(0x107): 0x00,
        to_address(0x108): 0x01,
        to_address(0x109): 0x00,
        to_address(0x10A): 0x8000,
    }

    for i in range(0, total_tests):
        account = to_address(0x100 + i)
        pre[account] = Account(code=code_exp)

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
