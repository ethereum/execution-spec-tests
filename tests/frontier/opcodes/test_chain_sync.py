"""
abstract: Test the chain synchronization feature.
    Ensure that the chain synchronization feature accurately validates the transaction chain
"""

import pytest

from ethereum_test_forks import Frontier, Homestead
from ethereum_test_tools import Account, Alloc, Block, BlockchainTestFiller, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import Transaction


@pytest.mark.parametrize(
    "offset,expected",
    [
        (254, 0x59E4655F093809C72B7655D2C4E17A29E1AFC868D50D074AE33FAE4FF7F45B57),
        (255, 0x3B37DF5B367774496FEB057125414B8B02C6A16BE37C5CFEE48F6EA310476895),
        (256, 0xCA4B3DF81146433C8B710608B2AE7D59CB949F721D87DDBA579339E9452188F1),
        (257, 0x0),
    ],
)
@pytest.mark.with_all_evm_code_types
@pytest.mark.valid_from("Frontier")
@pytest.mark.valid_until(
    "Frontier"
)  # Can only do one right now because of how hashes change between forks
def test_blockhash(
    offset: int, expected: int, blockchain_test: BlockchainTestFiller, fork: str, pre: Alloc
):
    """
    Tests the BLOCKHASH opcode when the blocks are in extreme positions near the limit of the chain

    Note: Hardcoded blockhashes to get us started. Will look for a better
    way of doing this in future
    """
    env = Environment()
    sender = pre.fund_eoa()
    blockhash_code = Op.SSTORE(
        0,
        Op.BLOCKHASH(Op.SUB(Op.NUMBER, offset)),
    )
    generated_blocks = [Block() for _ in range(offset - 1)]

    # Deploy the contract to the chain (to be called later)
    account = pre.deploy_contract(blockhash_code)
    post = {
        account: Account(
            storage={"0x0": expected},
        ),
    }

    tx = Transaction(
        ty=0x0,
        nonce=0,
        to=account,
        gas_limit=500000,
        gas_price=10,
        protected=fork not in [Frontier, Homestead],
        sender=sender,
    )

    blockhash_block = Block(txs=[blockhash_transaction])

    blockchain_test(
        env=env,
        pre=pre,
        post=post,
        blocks=generated_blocks + [blockhash_block],
    )
