
"""
Test Mod opcode
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
def test_mod_opcode(fork):
    """
    Test Mod Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/modFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    txs = []
    post = {}

    code_mod = Yul(
        """
        {
            let calladdr := calldataload(0)
            {
            switch calladdr
                case 0x100 {
                    sstore(0, mod(2, 3))
                }
                case 0x101 {
                    sstore(0, mod(sub(0, 1), 2))
                }
                case 0x102 {
                    sstore(0, mod(0, sub(0, 1)))
                }
                case 0x103 {
                    sstore(0, mod(3, 0))
                }
                case 0x104 {
                    // The expected result is 2, which is counter
                    // intuitive. The reason is that MOD uses unsigned
                    // arithmetic. -2 % 3 is indeed 1, but 2^256 % 3 = 1
                    // and therefore (2^256-2) % 3 = 2
                    sstore(0, mod(sub(0, 2), 3))
                }
                case 0x105 {
                    // The original test was (3%0)-1, but since we're 
                    // already checking 3%0 (contract 0...0103), I decided
                    // it would be better to check a different number
                    sstore(0, sub(mod(16, 0), 1))
                }
            }
        }
        """
    )

    total_tests = 6
    solutions = {
        to_address(0x100): 0x02,
        to_address(0x101): 0x01,
        to_address(0x102): 0x00,
        to_address(0x103): 0x00,
        to_address(0x104): 0x02,
        to_address(0x105): to_hash(-1),
    }

    for i in range(0, total_tests):
        account = to_address(0x100 + i)
        pre[account] = Account(code=code_mod)

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
