"""
Test Add/Sub Opcodes
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

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
               {
                   /* -1 + -1 = -2 */
                   sstore(0x10, add(sub(0, 1), sub(0, 1)))
                   /* -1 + 4  =  3 */
                   sstore(0x11, add(sub(0, 1), 4))
                   /* -1 + 1  =  0 */
                   sstore(0x12, add(sub(0, 1), 1))
                   /* 0 + 0   =  0 */
                   sstore(0x13, add(0, 0))
                   /* 1 + -1  =  0 */
                   sstore(0x14, add(1, sub(0, 1)))
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
                0x10: to_hash(-2),
                0x11: 0x03,
                0x12: 0x00,
                0x13: 0x00,
                0x14: 0x00,
            }
        )
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])


@test_from("istanbul")
def test_sub_opcode(fork):
    """
    Test Sub Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/subFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    pre = {
        to_address(0x100): Account(
            balance=0x0BA1A9CE0BA1A9CE,
            code=Yul(
                """
               {
                   /* 23 - 1   = -22 */
                   sstore(0x10, sub(23, 1))
                   /* -2 - 3   =  -1 */
                   sstore(0x11, sub(2, 3))
                   /* 0 - 23   = -23 */
                   sstore(0x12, sub(0, 23))
                   /* 0 - (-1) =   1 */
                   sstore(0x13, sub(0, sub(0, 1)))
                   /* -1 - 0   =  -1 */
                   sstore(0x14, sub(sub(0, 1), 0))
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
                0x10: 0x16,
                0x11: to_hash(-1),
                0x12: to_hash(-23),
                0x13: 0x01,
                0x14: to_hash(-1),
            }
        )
    }

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])
