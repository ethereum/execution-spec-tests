"""
Test 2^(2^(n)), 2^(2^(n-1)), 2^(2^(n+1))
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
)


@test_from("shanghai")
def test_exp_power_2(fork):
    """
    Test Exp Opcode for 2^(2^(n)), 2^(2^(n-1)), 2^(2^(n+1)).
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/expPower2Filler.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    let n := 1
                    for { } lt(n, 9) { }
                    {
                        sstore(mul(0x10, n), exp(2, exp(2, n)))
                        sstore(add(mul(0x10, n), 1), exp(2, sub(exp(2, n), 1)))
                        sstore(add(mul(0x10, n), 2), exp(2, add(exp(2, n), 1)))
                        n := add(n, 1)
                    }
                }
                """
            ),
        ),
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
    }

    tx = Transaction(
        nonce=0,
        to=to_address(0x100),
        gas_limit=5000000,
        gas_price=10,
    )

    post = {
        to_address(0x100): Account(
            storage={
                # 0x10*n:   2^(2^(n))
                # 0x10*n+1: 2^(2^(n-1))
                # 0x10*n+2: 2^(2^(n+1))
                # 2^2
                0x10: 0x04,
                0x11: 0x02,
                0x12: 0x08,
                0x20: 0x10,
                0x21: 0x08,
                0x22: 0x20,
                0x30: 0x0100,
                0x31: 0x0080,
                0x32: 0x0200,
                0x40: 0x010000,
                0x41: 0x008000,
                0x42: 0x020000,
                0x50: 0x0100000000,
                0x51: 0x0080000000,
                0x52: 0x0200000000,
                0x60: 0x010000000000000000,
                0x61: 0x008000000000000000,
                0x62: 0x020000000000000000,
                0x70: 0x0100000000000000000000000000000000,
                0x71: 0x0080000000000000000000000000000000,
                0x72: 0x0200000000000000000000000000000000,
                # 2^256 = 0 in evm math
                0x81: 0x8000000000000000000000000000000000000000000000000000000000000000,
            }
        )
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])
