"""
Test Exponentiation opcode
"""

from string import Template

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


def exp(a: int, b: int) -> int:
    """
    Helper Exponential Function
    """
    return pow(a, b, 2**256)


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

    base_exp_result = [
        ("2, 2", 0x04),
        ("sub(0, 1), sub(0, 2)", 0x01),
        (
            "2147483647, 2147483647",
            0xBC8CCCCCCCC888888880000000AAAAAAB00000000FFFFFFFFFFFFFFF7FFFFFFF,
        ),
        ("0, 2147483647", 0x00),
        ("2147483647, 0", 0x01),
        ("257, 1", 0x0101),
        ("1, 257", 0x01),
        ("2, 257", 0x00),
        ("0, 0", 0x01),
        ("2, 0x0100000000000f", 0x00),
        ("2, 15", 0x8000),
    ]

    for i, (b_e, result) in enumerate(base_exp_result):
        address = to_address(0x100 + i)
        yul_code = Template(
            """
            {
                sstore(${address}, exp(${b_e}))
            }
            """
        ).substitute(b_e=b_e, address=address)
        pre[address] = Account(code=Yul(yul_code))

        tx = Transaction(
            nonce=i,
            to=address,
            gas_limit=500000,
            gas_price=10,
        )
        txs.append(tx)
        post[address] = Account(storage={address: result})

    yield StateTest(env=env, pre=pre, post=post, txs=txs)


@test_from("istanbul")
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

    storage = {
        (0x10 * n) + i: exp(2, exp(2, n) + j)
        for n in range(1, 9)
        for i, j in [(0, 0), (1, -1), (2, 1)]
    }

    post = {to_address(0x100): Account(storage=storage)}

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])


@test_from("istanbul")
def test_exp_power_256_of_256(fork):
    """
    Test Exp Opcode for (255 to 257)**((255 to 257)**n).
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/expPower256of256Filler.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    let n := 0
                    for { } lt(n, 34) { }
                    {
                        sstore(mul(0x10, n), exp(256, exp(256, n)))
                        sstore(add(mul(0x10, n), 1), exp(256, exp(255, n)))
                        sstore(add(mul(0x10, n), 2), exp(256, exp(257, n)))

                        sstore(add(mul(0x10, n), 3), exp(255, exp(256, n)))
                        sstore(add(mul(0x10, n), 4), exp(255, exp(255, n)))
                        sstore(add(mul(0x10, n), 5), exp(255, exp(257, n)))

                        sstore(add(mul(0x10, n), 6), exp(257, exp(256, n)))
                        sstore(add(mul(0x10, n), 7), exp(257, exp(255, n)))
                        sstore(add(mul(0x10, n), 8), exp(257, exp(257, n)))

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
        gas_limit=5000000000,
        gas_price=10,
    )

    base_values = []
    for x in [256, 255, 257]:
        for y in [256, 255, 257]:
            base_values.append((x, y))

    storage = {
        (0x10 * n) + i: exp(b, exp(e, n))
        for n in range(34)
        for i, (b, e) in enumerate(base_values, start=0)
    }

    post = {to_address(0x100): Account(storage=storage)}

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])


@test_from("istanbul")
def test_exp_power_256(fork):
    """
    Test Exp Opcode for 255-257**n.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/expPower256Filler.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    let n := 0
                    for { } lt(n, 34) { }
                    {
                        sstore(mul(0x10, n), exp(256, n))
                        sstore(add(mul(0x10, n), 1), exp(255, n))
                        sstore(add(mul(0x10, n), 2), exp(257, n))
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

    storage = {
        (0x10 * n) + i: exp(b, n)
        for n in range(34)
        for i, b in enumerate([256, 255, 257], start=0)
    }

    post = {to_address(0x100): Account(storage=storage)}

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])
