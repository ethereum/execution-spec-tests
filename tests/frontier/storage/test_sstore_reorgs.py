"""Test sstore reorgs."""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Hash,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.valid_from("Frontier")
def test_sstore_reorgs(blockchain_test: BlockchainTestFiller, fork: Fork, pre: Alloc):
    """Test sstore reorgs."""
    sender = pre.fund_eoa()
    key = 0x4193F419339D8D52872C2A4D6EE5A6EB14C99332DAF66AD89D1882BF092892BE
    value = 0x0000000000000000000000000000000000000000000005FD4B1D5B1331457BB9
    contract_address = pre.deploy_contract(
        code=Op.SSTORE(
            key,
            Op.CALLDATALOAD(0),
        )
        + Op.STOP,
        storage={
            "0x0000000000000000000000000000000000000000000000000000000000000000": "0x0000000000000000000000000000000000000000000005fd4b1d5b1331457fa1",
            "0x0000000000000000000000000000000000000000000000000000000000000003": "0xfaff0740ae3023cde7a09ed3d170caac5e529fe85266d08d0b7a95f756b60329",
            "0x0000000000000000000000000000000000000000000000000000000000000005": "0x0000000000000000000000005c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
            "0x0000000000000000000000000000000000000000000000000000000000000006": "0x00000000000000000000000007f349d2013046ca78a08937170f8052e7c8cece",
            "0x0000000000000000000000000000000000000000000000000000000000000007": "0x000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "0x0000000000000000000000000000000000000000000000000000000000000008": "0x6884c7b300000000000017ac2851653e7c3f00000184d326e3372026f9f4bece",
            "0x0000000000000000000000000000000000000000000000000000000000000009": "0x000000000000000000000000000000000000000023b71f84b176af4604d4171c",
            "0x000000000000000000000000000000000000000000000000000000000000000a": "0x0000000000000000000000006a606449754140c3f84cc6d48389eebeb8a290",
            "0x000000000000000000000000000000000000000000000000000000000000000c": "0x0000000000000000000000000000000000000000000000000000000000000001",
            "0xa6eef7e35abe7026729641147f7915573c7e97b47efa546f5f6e3230263bcb49": "0x00000000000000000000000000000000000000000000000000000000000003e8",
            "0xb69b97f39af8d1773ae42072a8e0a97e63431cff1226a7bf7003fdc7ca0399f4": "0x0000000000000000000000000000000000000000000005fd4b1d5b1331457bb9",
        },
        address=Address(0x77D34361F991FA724FF1DB9B1D760063A16770DB),
    )
    trigger_contract_address = pre.deploy_contract(
        code=Op.SSTORE(0, 1) + Op.STOP,
        address=Address(0x77D34361F991FA724FF1DB9B1D760063A167D0E3),
    )

    orphan_block = Block(
        txs=[
            Transaction(
                to=0,
                gas_limit=100_000,
                sender=sender,
            ),
        ],
        parent_block="GENESIS",
    )
    # Reset the nonce
    sender.nonce = 0
    canonical_block_1 = Block(
        txs=[
            Transaction(
                to=contract_address,
                gas_limit=100_000,
                data=Hash(value),
                sender=sender,
            ),
        ],
        parent_block="GENESIS",
    )
    canonical_block_2 = Block(
        txs=[
            Transaction(
                to=contract_address,
                gas_limit=100_000,
                data=Hash(0),
                sender=sender,
            ),
        ],
        parent_block=canonical_block_1,
    )
    canonical_block_3 = Block(
        txs=[
            Transaction(
                to=trigger_contract_address,
                gas_limit=100_000,
                data=Hash(0),
                sender=sender,
            ),
        ],
        parent_block=canonical_block_2,
    )

    blockchain_test(
        pre=pre,
        post={},
        blocks=[
            orphan_block,
            canonical_block_1,
            canonical_block_2,
            canonical_block_3,
        ],
        re_org_test=True,
    )
