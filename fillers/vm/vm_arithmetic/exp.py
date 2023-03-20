"""
Test Exponentiation opcode
"""

from typing import Callable, Dict, List, Tuple

from ethereum_test_tools import Account, Environment, Opcode
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    test_from,
    to_address,
)


def test_case_generator(
    test_cases: List[Tuple[int, int]],
    opcode: Opcode,
    c: Callable[[int, int], int],
) -> Tuple[bytes, Dict[str | int, str | int]]:
    """
    Generates a code that automatically checks all test cases requested for the
    given opcode.
    Takes a list of tuples of two values, where the values represent `a` and
    `b` in expression `opcode(a, b)`.
    Returns code and the dictionary of storage values expected for this code.
    """
    test_code = bytes()
    results: Dict[str | int, str | int] = {}
    for i, (a, b) in enumerate(test_cases):
        # Push the values into the stack
        test_code += Op.PUSH32(b)
        test_code += Op.PUSH32(a)
        # Execute opcode for test
        test_code += opcode
        # store the result
        test_code += Op.PUSH32(i)
        test_code += Op.SSTORE
        # use `exp` to calculate the expected result, and save it to the dict
        results[i] = c(a, b)
    return test_code, results


def exp(a: int, b: int) -> int:
    """
    Helper Exponential Function
    """
    if a < 0:
        a = 2**256 + a
    if b < 0:
        b = 2**256 + b
    return pow(a, b, 2**256)


@test_from("istanbul")
def test_exp_opcode(_: str):
    """
    Test Exp Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/expFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    test_cases = [
        (2, 2),
        (-1, -2),
        (2147483647, 2147483647),
        (0, 2147483647),
        (2147483647, 0),
        (257, 1),
        (1, 257),
        (2, 257),
        (0, 0),
        (2, 0x0100000000000F),
        (2, 15),
    ]

    # Fill all test cases
    test_code, results = test_case_generator(test_cases, Op.EXP, exp)

    test_code_address = to_address(0x100)
    pre = {
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
        test_code_address: Account(code=test_code),
    }
    post = {test_code_address: Account(storage=results)}

    tx = Transaction(
        nonce=0,
        to=test_code_address,
        gas_limit=5000000,
        gas_price=10,
    )

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])


@test_from("istanbul")
def test_exp_power_2(_: str):
    """
    Test Exp Opcode for 2^(2^(n)), 2^(2^(n-1)), 2^(2^(n+1)).
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/expPower2Filler.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    test_cases = [
        (2, (exp(2, n) + j) % (2**256))
        for n in range(1, 9)
        for j in [0, -1, 1]
    ]

    # Fill all test cases
    test_code, results = test_case_generator(test_cases, Op.EXP, exp)

    test_code_address = to_address(0x100)
    pre = {
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
        test_code_address: Account(code=test_code),
    }
    post = {test_code_address: Account(storage=results)}

    tx = Transaction(
        nonce=0,
        to=test_code_address,
        gas_limit=5000000,
        gas_price=10,
    )

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
