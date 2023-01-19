"""
Test Mul opcode
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
def test_mul_opcode(fork):
    """
    Test Mul Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/mulFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []
    post = {}

    code_mul = Yul(
        """
        {
            let calladdr := calldataload(0)
            {
            switch calladdr
                case 0x100 {
                    sstore(0, mul(2, 3))
                }
                case 0x101 {
                    sstore(0, mul(sub(0, 1), sub(0, 1)))
                }
                case 0x102 {
                    sstore(0, mul(0, 23))
                }
                case 0x103 {
                    sstore(0, mul(23, 1))
                }
                case 0x104 {
                    // 2^255 * -1 (the expected answer is 2^255,
                    // because -2^255 = 2^256-2^255 in evm arithmetic)
                    sstore(0, mul(exp(2, 255), sub(0, 1)))
                }
                case 0x105 {
                    //2^255 * 2^255
                    //the expected answer is 0, because 2^510 % 2^256 = 0
                    sstore(0, mul(exp(2, 255), exp(2, 255)))
                }
                case 0x106 {
                    // (2^255-1) * (2^255-1)
                    // = 2^510 - 2*2^255 + 1 = 2^510 - 2^256 + 1 = 1
                    sstore(0, mul(sub(exp(2, 255), 1), sub(exp(2, 255), 1)))
                }
                case 0x107 {
                    // just x^3
                    let x := 0x1234567890ABCDEF0FEDCBA0987654321
                    sstore(0, mul(mul(x, x), x))
                }
            }
        }
        """
    )

    code_underflow = (  # address 108
        # Do a mul underflow, see that the transaction is reverted
        # so the test will fail if there is no revert
        # 00 PUSH1 01
        # 02 PUSH1 00
        # 04 SSTORE
        # Do a stack underflow
        # 05 PUSH1 01
        # 07 MUL
        # 08 STOP
        "0x600160005560010200"
    )

    total_tests = 9
    solutions = {
        to_address(0x100): 0x06,
        to_address(0x101): 0x01,
        to_address(0x102): 0x00,
        to_address(0x103): 0x17,
        to_address(
            0x104
        ): 0x8000000000000000000000000000000000000000000000000000000000000000,
        to_address(0x105): 0x00,
        to_address(0x106): 0x01,
        to_address(
            0x107
        ): 0x47D0817E4167B1EB4F9FC722B133EF9D7D9A6FB4C2C1C442D000107A5E419561,
        to_address(0x108): 0x00,  # Its 1 unless the tx is reverted.
    }

    for i in range(0, total_tests):
        account = to_address(0x100 + i)
        # Use code_mul until last address then use code_underflow for address 108
        pre[account] = (
            Account(code=code_mul) if (i < 8) else Account(code=code_underflow)
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
