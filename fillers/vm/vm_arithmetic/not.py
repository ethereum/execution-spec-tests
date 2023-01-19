"""
Test not opcode
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
def test_not_opcode(fork):
    """
    Test not Opcode.
    Port from ethereum/tests:
      - GeneralStateTestsFiller/VMTests/vmTest/notFiller.yml
      - Original test by Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    pre = {TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE)}
    post = {}

    code_not = Yul(
        """
        {
            sstore(0, not(0X123456789ABCDEF))
        }
        """
    )

    account = to_address(0x100)
    pre[account] = Account(code=code_not)

    tx = Transaction(
        nonce=0,
        data=to_hash(0x100),
        to=account,
        gas_limit=500000,
        gas_price=10,
    )

    not_solution = (
        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEDCBA9876543210
    )

    post[account] = Account(storage={0: not_solution})

    yield StateTest(env=env, pre=pre, post=post, txs=[tx])
