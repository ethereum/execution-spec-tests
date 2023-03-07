"""
Test Mul/Div/SDiv Opcodes
"""

from ethereum_test_tools import Account, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    test_from,
    to_address,
    to_hash,
)


@test_from("istanbul")
def test_mul_opcode(fork):
    """
    Test Mul Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/mulFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    # Do a mul underflow, see that the transaction is reverted
    # so the test will fail if there is no revert
    code_underflow = (
        Op.PUSH1(1)
        + Op.PUSH1(0)
        + Op.SSTORE
        +
        # Do a stack underflow
        # PUSH1 01
        # MUL
        # STOP
        Op.PUSH1(1)
        + Op.MUL
        + Op.STOP
    )

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    sstore(0x10, mul(2, 3))
                    sstore(0x11, mul(sub(0, 1), sub(0, 1)))
                    sstore(0x12, mul(0, 23))
                    sstore(0x13, mul(23, 1))

                    /* 2^255 * -1 (the expected answer is 2^255,
                    because -2^255 = 2^256-2^255 in evm arithmetic) */
                    sstore(0x14, mul(exp(2, 255), sub(0, 1)))

                    /* 2^255 * 2^255 the expected answer is 0,
                    because 2^510 % 2^256 = 0 */
                    sstore(0x15, mul(exp(2, 255), exp(2, 255)))

                    /* (2^255-1) * (2^255-1) = 2^510 - 2*2^255 + 1
                        = 2^510 - 2^256 + 1 = 1 */
                    sstore(0x16, mul(sub(exp(2, 255), 1), sub(exp(2, 255), 1)))

                    /* Just x^3 */
                    let x := 0x1234567890ABCDEF0FEDCBA0987654321
                    sstore(0x17, mul(mul(x, x), x))
                }
                """
            ),
        ),
        to_address(0x200): Account(
            balance=0x0BA1A9CE0BA1A9CE, code=code_underflow
        ),
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
    }

    tx_1 = Transaction(
        nonce=0,
        to=to_address(0x100),
        gas_limit=500000,
        gas_price=10,
    )

    tx_2 = Transaction(
        nonce=1,
        to=to_address(0x200),
        gas_limit=50000,
        gas_price=10,
    )

    post = {
        to_address(0x100): Account(
            storage={
                0x10: 0x06,
                0x11: 0x01,
                0x12: 0x00,
                0x13: 0x17,
                0x14: 0x8000000000000000000000000000000000000000000000000000000000000000,
                0x15: 0x00,
                0x16: 0x01,
                0x17: 0x47D0817E4167B1EB4F9FC722B133EF9D7D9A6FB4C2C1C442D000107A5E419561,
            }
        ),
        to_address(0x200): Account(
            storage={
                0x18: 0x00,  # Its 1 unless the tx is reverted.
            }
        ),
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx_1, tx_2])


@test_from("istanbul")
def test_div_opcode(fork):
    """
    Test Div Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/divFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    /* 2 divided by a big number */
                    sstore(0x10, div(
                        2,
                        0xfedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210
                        )
                    )
                    /* Verify to fix to the divBoostBug */
                    sstore(0x11, div(
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFBA,
                        0x1DAE6076B981DAE6076B981DAE6076B981DAE6076B981DAE6076B981DAE6077
                        )
                    )
                    sstore(0x12, div(5, 2))
                    sstore(0x13, div(23, 24))
                    sstore(0x14, div(0, 24))
                    sstore(0x15, div(1, 1))
                    sstore(0x16, div(2, 0))
                    sstore(0x17, add(div(13, 0), 7))
                }
                """
            ),
        ),
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
    }

    tx = Transaction(
        nonce=0,
        to=to_address(0x100),
        gas_limit=500000,
        gas_price=10,
    )

    post = {
        to_address(0x100): Account(
            storage={
                0x10: 0x00,
                0x11: 0x89,
                0x12: 0x02,
                0x13: 0x00,
                0x14: 0x00,
                0x15: 0x01,
                0x16: 0x00,
                0x17: 0x07,
            }
        )
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])


@test_from("istanbul")
def test_sdiv_opcode(fork):
    """
    Test sdiv Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/sdivFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    code_sdiv = (
        # PUSH1 05
        # PUSH1 09
        # PUSH1 00
        # SUB  (stack becomes -9, 5)
        Op.PUSH1(5)
        + Op.PUSH1(9)
        + Op.PUSH1(0)
        + Op.SUB
        # SDIV (-9/5 = -1, no fractions)
        # PUSH1 00
        # SSTORE
        # STOP
        + Op.SDIV
        + Op.PUSH1(0x20)
        + Op.SSTORE
        + Op.STOP
    )

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    /* (0 - (-1)) / (-1) = 1/(-1) = -1
                    -1 = 2^256-1 */
                    sstore(0x10, sdiv(sub(0, sub(0, 1)), sub(0, 1)))

                    /* (-1) / (0 - (-1)) = (-1)/1 = -1
                    -1 = 2^256-1 */
                    sstore(0x11, sdiv(sub(0, 1), sub(0, sub(0, 1))))

                    /* (-2) / (-4) = 0 evm doesn't do fractions */
                    sstore(0x12, sdiv(sub(0, 2), sub(0, 4)))

                    /* 4 / (-2) = -2 */
                    sstore(0x13, sdiv(4, sub(0, 2)))

                    /* 5 / (-4) = -1 evm doesn't do fractions */
                    sstore(0x14, sdiv(5, sub(0, 4)))

                    /* (-2^255) / (-1) = 2^255
                    Because 2^255 = -2^255 in evm arithmetic */
                    sstore(0x15, sdiv(exp(sub(0, 2), 255), sub(0, 1)))

                    /* (-2^255) / 0 = 0, anything / 0 = 0 in evm */
                    sstore(0x16, sdiv(sub(0, exp(2, 255)), 0))

                    /* (-1)/25 = 0 (no fractions in evm) */
                    sstore(0x17, sdiv(sub(0, 1), 25))

                    /* (-1)/(-1) = 1 */
                    sstore(0x18, sdiv(sub(0, 1), sub(0, 1)))

                    /* (-1)/1 = -1 */
                    sstore(0x19, sdiv(sub(0, 1), 1))

                    /* (-3)/0 = 0, x/0 = 0 in evm */
                    sstore(0x1A, sdiv(sub(0, 3), 0))

                    /* (0-(-1))/0 = 0, -1 = 2^256-1 */
                    sstore(0x1B, sdiv(sub(0, sub(0, 1)), 0))

                    /* (0-(-1))/0 + 1 = 1, -1 = 2^256-1 */
                    sstore(0x1C, add(sdiv(sub(0, sub(0, 1)), 0), 1))

                    /* A negative number sdiv -1 is the
                    absolute value of that number */
                    let pow2_255 := exp(2, 255)
                    let pow2_255_min1 := sub(pow2_255, 1)
                    sstore(0x1D, sdiv(sub(0, pow2_255_min1), sub(0, 1)))

                    /* A negative number sdiv -1 is the
                    absolute value of that number */
                    sstore(0x1E, sdiv(sub(0, pow2_255), sub(0, 1)))

                    /* (- 0 maxint) is 0x80.....01, so -1 / -maxint is zero */
                    let maxint := 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                    sstore(0x1F, sdiv(sub(0, 1), sub(0, maxint)))
                }
                """
            ),
        ),
        to_address(0x200): Account(balance=0x0BA1A9CE0BA1A9CE, code=code_sdiv),
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
    }

    tx_1 = Transaction(
        nonce=0,
        to=to_address(0x100),
        gas_limit=5000000,
        gas_price=10,
    )

    tx_2 = Transaction(
        nonce=1,
        to=to_address(0x200),
        gas_limit=50000,
        gas_price=10,
    )

    post = {
        to_address(0x100): Account(
            storage={
                0x10: to_hash(-1),
                0x11: to_hash(-1),
                0x12: 0x00,
                0x13: to_hash(-2),
                0x14: to_hash(-1),
                0x15: 0x8000000000000000000000000000000000000000000000000000000000000000,
                0x16: 0x00,
                0x17: 0x00,
                0x18: 0x01,
                0x19: to_hash(-1),
                0x1A: 0x00,
                0x1B: 0x00,
                0x1C: 0x01,
                0x1D: 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                0x1E: 0x8000000000000000000000000000000000000000000000000000000000000000,
                0x1F: 0x00,
            }
        ),
        to_address(0x200): Account(
            storage={
                0x20: to_hash(-1),
            }
        ),
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx_1, tx_2])
