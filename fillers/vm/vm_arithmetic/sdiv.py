"""
Test sdiv opcode Todo
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
def test_sdiv_opcode(fork):
    """
    Test sdiv Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/sdivFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []
    post = {}

    code_sdiv = Yul(
        """
        {
            let calladdr := calldataload(0)
            {
            switch calladdr
                case 0x100 {
                    // (0 - (-1)) / (-1) = 1/(-1) = -1
                    // -1 = 2^256-1
                    sstore(0, sdiv(sub(0, sub(0, 1)), sub(0, 1)))
                }
                case 0x101 {
                    // (-1) / (0 - (-1)) = (-1)/1 = -1
                    // -1 = 2^256-1
                    sstore(0, sdiv(sub(0, 1), sub(0, sub(0, 1))))
                }
                case 0x102 {
                    // (-2) / (-4) = 0
                    // evm doesn't do fractions
                    sstore(0, sdiv(sub(0, 2), sub(0, 4)))
                }
                case 0x103 {
                    // 4 / (-2) = -2
                    sstore(0, sdiv(4, sub(0, 2)))
                }
                case 0x104 {
                    // 5 / (-4) = -1
                    // evm doesn't do fractions
                    sstore(0, sdiv(5, sub(0, 4)))
                }
                case 0x105 {
                    // (-2^255) / (-1) = 2^255
                    // Because 2^255 = -2^255 in evm arithmetic
                    sstore(0, sdiv(exp(sub(0, 2), 255), sub(0, 1)))
                }
                case 0x106 {
                    // (-2^255) / 0 = 0
                    // anything / 0 = 0 in evm
                    sstore(0, sdiv(sub(0, exp(2, 255)), 0))
                }
                case 0x107 {
                    // (-1)/25 = 0 (no fractions in evm)
                    sstore(0, sdiv(sub(0, 1), 25))
                }
                case 0x108 {
                    // (-1)/(-1) = 1
                    sstore(0, sdiv(sub(0, 1), sub(0, 1)))
                }
                case 0x109 {
                    // (-1)/1 = -1
                    sstore(0, sdiv(sub(0, 1), 1))
                }
                case 0x10a {
                    // (-3)/0 = 0
                    // x/0 = 0 in evm
                    sstore(0, sdiv(sub(0, 3), 0))
                }
                case 0x10b {
                    // (0-(-1))/0 = 0
                    // -1 = 2^256-1
                    sstore(0, sdiv(sub(0, sub(0, 1)), 0))
                }
                case 0x10c {
                    // (0-(-1))/0 + 1 = 1
                    // -1 = 2^256-1
                    sstore(0, add(sdiv(sub(0, sub(0, 1)), 0), 1))
                }
                case 0x10e {
                    // A negative number sdiv -1 is the
                    // absolute value of that number
                    sstore(0, sdiv(sub(0, sub(exp(2, 255), 1)), sub(0, 1)))
                }
                case 0x10f {
                    // A negative number sdiv -1 is the
                    // absolute value of that number
                    sstore(0, sdiv(sub(0, exp(2, 255)), sub(0, 1)))
                }
                case 0x110 {
                    // (- 0 maxint) is 0x80.....01, so -1 / -maxint is zero
                    let x := 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                    sstore(0, sdiv(sub(0, 1), sub(0, x)))
                }
            }
        }
        """
    )

    code_op = (
        # PUSH1 05
        # PUSH1 09
        # PUSH1 00
        # SUB  (stack becomes -9, 5)
        # SDIV (-9/5 = -1, no fractions)
        # PUSH1 00
        # SSTORE
        # STOP
        "0x600560096000030560005500"
    )

    total_tests = 17
    solutions = {
        to_address(0x100): to_hash(-1),
        to_address(0x101): to_hash(-1),
        to_address(0x102): to_hash(-1),  # minus 1 should be 0
        to_address(0x103): to_hash(-1),  # should be -2
        to_address(0x104): to_hash(-1),
        to_address(
            0x105
        ): 0x8000000000000000000000000000000000000000000000000000000000000000,
        to_address(0x106): 0x00,
        to_address(0x107): 0x00,
        to_address(0x108): 0x01,
        to_address(0x109): to_hash(-1),
        to_address(0x10A): 0x00,
        to_address(0x10B): 0x00,
        to_address(0x10C): 0x01,
        to_address(0x10D): to_hash(-1),
        to_address(
            0x10E
        ): 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
        to_address(
            0x10F
        ): 0x8000000000000000000000000000000000000000000000000000000000000000,
        to_address(0x110): 0x00,
    }

    for i in range(0, total_tests):
        account = to_address(0x100 + i)
        # noqa: Use code_sdiv unless for op_code test case: to_address(0x10B)
        pre[account] = (
            Account(code=code_sdiv) if (i == 13) else Account(code=code_op)
        )

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
