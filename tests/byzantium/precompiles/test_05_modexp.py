"""
abstract: Test MODEXP (0x0000..0005)

    Tests the MODEXP precompile, located at address 0x0000..0005

"""
from ethereum_test_forks import Frontier
from ethereum_test_tools import (
    Account,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
    to_address,
)


def test_modexp(state_test: StateTestFiller, fork: str):
    """
        Test the MODEXP precompile
    """
    env = Environment()
    pre = {"0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b": Account(balance=1000000000000000000000)}
    txs = []
    post = {}

    """
    We are setting up 16 accounts, ranging from 0x100 to 0x10f.
    They push values into the stack from 0-16, but each contract uses a
    different DUP opcode, and depending on the opcode used, the item copied
    into the storage changes.
    """

    account = to_address(0x100)
    dup_opcode = 0x80 + i

    pre[account] = Account(
        code=(
            # Store all CALLDATA into memory (offset 0)
            """0x366000600037"""
            +
            # Setup stack to CALL into ModExp with the CALLDATA and CALL into it
            """600060003660006000060055AF1"""
            +
            # Clear out the first 32 bytes of memory (these 32 bytes are saved into storage)
            """6000600052"""
            +
            # RETURNDATACOPY the returned data into memory (offset 0, overwrites original CALLDATA)
            """3D600060003E"""
            +
            # SSTORE the first 32 bytes into storage slot 0
            """600051600055"""
            +
            # RETURN the returned data from ModExp
            """3D6000F3"""
        )
    )

    """
    Also we are sending one transaction to each account.
    The storage of each will only change by one item: storage[0]
    The value depends on the DUP opcode used.
    """

    tx = Transaction(
        ty=0x0,
        nonce=0,
        to=account,
        data="""0x0000000000000000000000000000000000000000000000000000000000000000"""
        +    """0000000000000000000000000000000000000000000000000000000000000000"""
        +    """0000000000000000000000000000000000000000000000000000000000000001""",
        gas_limit=500000,
        gas_price=10,
        protected=True,
    )
    txs.append(tx)

    s: Storage.StorageDictType = dict([(0, 0x01000000000000000000000000000000000000000000000000000000000000)])

    post[account] = Account(storage=s)

    state_test(env=env, pre=pre, post=post, txs=txs)
