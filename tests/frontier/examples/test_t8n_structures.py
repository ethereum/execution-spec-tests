"""Test T8N compatibility."""

import pytest

from ethereum_test_forks import Berlin, Byzantium, Cancun, Fork, London, Paris, Prague
from ethereum_test_tools import (
    AccessList,
    Account,
    Alloc,
    AuthorizationTuple,
    Block,
    BlockchainTestFiller,
    Environment,
    Storage,
    Transaction,
    Withdrawal,
    add_kzg_version,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ...cancun.eip4844_blobs.spec import Spec as BlobSpec


@pytest.mark.valid_from("Frontier")
def test_t8n_structures(blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork):
    """Feed t8n with all kinds of possible input."""
    env = Environment()
    sender = pre.fund_eoa()
    storage_1 = Storage()
    storage_2 = Storage()

    code_account_1 = pre.deploy_contract(
        code=Op.SSTORE(storage_1.store_next(1, "blockhash_0_is_set"), Op.GT(Op.BLOCKHASH(0), 0))
        + Op.SSTORE(storage_1.store_next(0, "blockhash_1"), Op.BLOCKHASH(1))
        + Op.SSTORE(
            storage_1.store_next(1 if fork < Paris else 0, "difficulty_1_is_near_20000"),
            Op.AND(Op.GT(Op.PREVRANDAO(), 0x19990), Op.LT(Op.PREVRANDAO(), 0x20100)),
        )
    )
    code_account_2 = pre.deploy_contract(
        code=Op.SSTORE(storage_2.store_next(1, "blockhash_1_is_set"), Op.GT(Op.BLOCKHASH(1), 0))
        + Op.SSTORE(
            storage_2.store_next(1 if fork < Paris else 0, "difficulty_2_is_near_20000"),
            Op.AND(Op.GT(Op.PREVRANDAO(), 0x19990), Op.LT(Op.PREVRANDAO(), 0x20100)),
        )
    )

    tx_1 = Transaction(
        gas_limit=100_000, to=code_account_1, data=b"", sender=sender, protected=fork >= Byzantium
    )
    if fork < Berlin:
        # Feed legacy transaction
        tx_2 = Transaction(
            gas_limit=100_000,
            to=code_account_2,
            data=b"",
            sender=sender,
            protected=fork >= Byzantium,
        )
    elif fork < London:
        # Feed access list transaction
        tx_2 = Transaction(
            gas_limit=100_000,
            to=code_account_2,
            data=b"",
            sender=sender,
            protected=fork >= Byzantium,
            access_list=[
                AccessList(
                    address=0x1234,
                    storage_keys=[0, 1],
                )
            ],
        )
    elif fork < Cancun:
        # Feed base fee transaction
        tx_2 = Transaction(
            to=code_account_2,
            data=b"",
            sender=sender,
            protected=fork >= Byzantium,
            gas_limit=100_000,
            max_priority_fee_per_gas=5,
            max_fee_per_gas=10,
            access_list=[
                AccessList(
                    address=0x1234,
                    storage_keys=[0, 1],
                )
            ],
        )
    elif fork < Prague:
        # Feed blob transaction
        tx_2 = Transaction(
            to=code_account_2,
            data=b"",
            sender=sender,
            protected=fork >= Byzantium,
            gas_limit=100_000,
            max_priority_fee_per_gas=5,
            max_fee_per_gas=10,
            max_fee_per_blob_gas=30,
            blob_versioned_hashes=add_kzg_version([1], BlobSpec.BLOB_COMMITMENT_VERSION_KZG),
            access_list=[
                AccessList(
                    address=0x1234,
                    storage_keys=[0, 1],
                )
            ],
        )
    else:
        # Feed set code transaction
        tx_2 = Transaction(
            to=sender,
            data=b"",
            sender=sender,
            protected=fork >= Byzantium,
            gas_limit=100_000,
            max_priority_fee_per_gas=5,
            max_fee_per_gas=10,
            nonce=1,
            access_list=[
                AccessList(
                    address=0x1234,
                    storage_keys=[0, 1],
                )
            ],
            authorization_list=[
                AuthorizationTuple(
                    address=code_account_2,
                    nonce=2,
                    signer=sender,
                ),
            ],
        )

    block_1 = Block(
        txs=[tx_1],
        expected_post_state={
            code_account_1: Account(
                storage=storage_1,
            ),
        },
    )

    block_2 = Block(
        txs=[tx_2],
        expected_post_state={
            code_account_2: Account(
                balance=1_000_000_000 if fork >= Cancun else 0,
                storage=storage_2,
            ),
        }
        if fork < Prague
        else {
            code_account_2: Account(
                balance=1_000_000_000 if fork >= Cancun else 0,
            ),
            sender: Account(
                storage=storage_2,
            ),
        },
    )

    if fork >= Cancun:
        block_2.withdrawals = [
            Withdrawal(
                address=code_account_2,
                amount=1,
                index=1,
                validator_index=0,
            ),
        ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=block_1.expected_post_state,
        blocks=[block_1, block_2],
    )
