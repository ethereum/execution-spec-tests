"""
Blockchain Test
"""

from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTest,
    Environment,
    TestAddress,
    Transaction,
    Yul,
    test_from,
)


@test_from(fork="london")
def test_block_number(fork):
    """
    Test the NUMBER opcode in different blocks
    Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()
    contract_addr = "0x" + "0" * (40 - 4) + "60A7"
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        contract_addr: Account(
            balance=1000000000000000000000,
            code=Yul(
                """
                {
                    let next_slot := sload(0)
                    sstore(next_slot, number())
                    sstore(0, add(next_slot, 1))
                }
                """
            ),
            storage={
                0x00: 0x01,
            },
        ),
    }

    def tx_generator():
        nonce = 0  # Initial value
        while True:
            tx = Transaction(
                ty=0x0,
                chain_id=0x0,
                nonce=nonce,
                to=contract_addr,
                gas_limit=500000,
                gas_price=10,
            )
            nonce = nonce + 1
            yield tx

    tx_generator = tx_generator()

    tx_per_block = [2, 0, 4, 8, 0, 0, 20, 1, 50]

    blocks = map(
        lambda len: Block(txs=list(map(lambda x: next(tx_generator), range(len)))),
        tx_per_block,
    )

    storage = {0: sum(tx_per_block) + 1}
    next_slot = 1
    for blocknum in range(len(tx_per_block)):
        for _ in range(tx_per_block[blocknum]):
            storage[next_slot] = blocknum + 1
            next_slot = next_slot + 1

    post = {contract_addr: Account(storage=storage)}

    yield BlockchainTest(
        genesis_environment=env,
        pre=pre,
        blocks=blocks,
        post=post,
    )
