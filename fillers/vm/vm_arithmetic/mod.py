"""
Test Mod/SMod/AddMod/MulMod
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
def test_mod_opcode(fork):
    """
    Test Mod Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/modFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    sstore(0x10, mod(2, 3))
                    sstore(0x11, mod(sub(0, 1), 2))
                    sstore(0x12, mod(0, sub(0, 1)))
                    sstore(0x13, mod(3, 0))

                    /* The expected result is 2, which is counter
                    intuitive. The reason is that MOD uses unsigned
                    arithmetic. -2 % 3 is indeed 1, but 2^256 % 3 = 1
                    and therefore (2^256-2) % 3 = 2 */
                    sstore(0x14, mod(sub(0, 2), 3))

                    /* The original test was (3%0)-1, but since we're
                    already checking 3%0, I decided it would be better
                    to check a different number */
                    sstore(0x15, sub(mod(16, 0), 1))
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
                0x10: 0x02,
                0x11: 0x01,
                0x12: 0x00,
                0x13: 0x00,
                0x14: 0x02,
                0x15: to_hash(-1),
            }
        )
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])


@test_from("istanbul")
def test_addmod_opcode(fork):
    """
    Test Addmod Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/addmodFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    /* (1 + 2) % 2 */
                    sstore(0x10, addmod(1, 2, 2))

                    /* (-1 + -2) % 2 */
                    sstore(0x11, addmod(sub(0, 1), sub(0, 2), 2))

                    /* (-6 + 1) % 3 */
                    sstore(0x12, addmod(sub(0, 6), 1, 3))

                    /* (-5 % 3) == ((-6 + 1) % 3) */
                    sstore(0x13, eq(smod(sub(0, 5), 3), addmod(sub(0, 6), 1, 3)))

                    /* (-5 % 3) == ((-6 + 1) % 3) */
                    sstore(0x14, eq(mod(sub(0,5), 3), addmod(sub(0, 6), 1, 3)))

                    /* (4 + 1) % -3 */
                    sstore(0x15, addmod(4, 1, sub(0, 3)))

                    /* ((4 + 1) % -3) == 2 */
                    sstore(0x16, eq(addmod(4, 1, sub(0, 3)), 2))

                    /* (-1 + 0) % 5 */
                    sstore(0x17, addmod(sub(0, 1), 0, 5))

                    /* (-1 + 1) % 5 */
                    sstore(0x18, addmod(sub(0, 1), 1, 5))

                    /* (-1 + 2) % 5 */
                    sstore(0x19, addmod(sub(0, 1), 2, 5))

                    /* (-1 + -2) % 5 */
                    sstore(0x1A, addmod(sub(0, 1), sub(0, 2), 5))

                    /* (4 + 1) % 0 */
                    sstore(0x1B, addmod(4, 1, 0))

                    /* (0 + 1) % 0 */
                    sstore(0x1C, addmod(0, 1, 0))

                    /* (1 + 0) % 0 */
                    sstore(0x1D, addmod(1, 0, 0))

                    /* ((0 + 0) % 0)) - 1 */
                    sstore(0x1E, sub(addmod(0, 0, 0), 1))
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
                0x10: 0x01,
                0x11: 0x01,
                0x12: 0x02,
                0x13: 0x00,
                0x14: 0x01,
                0x15: 0x05,
                0x16: 0x00,
                0x17: 0x00,
                0x18: 0x01,
                0x19: 0x02,
                0x1A: 0x04,
                0x1B: 0x00,
                0x1C: 0x00,
                0x1D: 0x00,
                0x1E: to_hash(-1),
            }
        )
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])


@test_from("istanbul")
def test_mulmod_opcode(fork):
    """
    Test mulmod Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/mulmodFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
                {
                    /* (1 * 2) % 2 */
                    sstore(0x10, mulmod(1, 2, 2))

                    /* (-1 * -2) % 3 */
                    sstore(0x11, mulmod(sub(0, 1), sub(0, 2), 3))

                    /* (-5 * 1) % 3 */
                    sstore(0x12, mulmod(sub(0, 5), 1, 3))

                    /* (5 * 1) % -3 */
                    sstore(0x13, mulmod(5, 1, sub(0, 3)))

                    /* (27 * 37) % 100 */
                    sstore(0x14, mulmod(27, 37, 100))

                    /* (5^255 * 2) % 5 */
                    sstore(0x15, mulmod(exp(2, 255), 2, 5))

                    /* (-1 * 2) % 5 */
                    sstore(0x16, mulmod(sub(0, 1), 2, 5))

                    /* ((2^255)-1 * 2) % 5 */
                    sstore(0x17, mulmod(sub(exp(2, 255), 1), 2, 5))

                    /* ((2^255)+1 * 2) % 5 */
                    sstore(0x18, mulmod(add(exp(2, 255), 1), 2, 5))

                    /* (-5 % 3) == (-5 * 1) % 3 */
                    sstore(0x19, eq(smod(sub(0, 5), 3), mulmod(sub(0, 5), 1, 3)))

                    /* (-5 % 3) == (-5 * 1) % 3 */
                    sstore(0x1A, eq(mod(sub(0, 5), 3), mulmod(sub(0, 5), 1, 3)))

                    /* (5 * 1) % -3 == 2 */
                    sstore(0x1B, eq(mulmod(5, 1, sub(0, 3)), 2))

                    /* (0 * 1) % 0 */
                    sstore(0x1C, mulmod(0, 1, 0))

                    /* (1 * 0) % 0 */
                    sstore(0x1D, mulmod(1, 0, 0))

                    /* 1 - ((1 * 0) % 0) */
                    sstore(0x1E, sub(1, mulmod(1, 0, 0)))

                    /* (5 * 1) % 0 */
                    sstore(0x1F, mulmod(5, 1, 0))
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
                0x11: 0x00,
                0x12: 0x02,
                0x13: 0x05,
                0x14: 0x63,
                0x15: 0x01,
                0x16: 0x00,
                0x17: 0x04,
                0x18: 0x03,
                0x19: 0x00,
                0x1A: 0x01,
                0x1B: 0x00,
                0x1C: 0x00,
                0x1D: 0x00,
                0x1E: 0x01,
                0x1F: 0x00,
            }
        )
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])
