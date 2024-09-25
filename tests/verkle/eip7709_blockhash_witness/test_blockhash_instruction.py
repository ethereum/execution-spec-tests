"""
abstract: Tests [EIP-7709: Read BLOCKHASH from storage and update cost]
(https://eips.ethereum.org/EIPS/eip-7709)
    Tests for [EIP-7709: Read BLOCKHASH from storage and update cost]
    (https://eips.ethereum.org/EIPS/eip-7709).
"""

import pytest

from ethereum_test_forks import Verkle
from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_types.verkle.helpers import Hash, chunkify_code
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7709.md"
REFERENCE_SPEC_VERSION = "TODO"

system_contract_address = Address("0xfffffffffffffffffffffffffffffffffffffffe")
HISTORY_SERVE_WINDOW = 8192
BLOCKHASH_SERVE_WINDOW = 256
block_number = BLOCKHASH_SERVE_WINDOW + 5


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "blocknum_target",
    [
        block_number + 1,
        block_number,
        block_number - 1,
        block_number - 2,
        block_number - BLOCKHASH_SERVE_WINDOW,
        block_number - BLOCKHASH_SERVE_WINDOW - 1,
    ],
    ids=[
        "future_block",
        "current_block",
        "previous_block",  # Note this block is also written by EIP-2935
        "previous_previous_block",
        "last_supported_block",
        "too_old_block",
    ],
)
def test_blockhash(blockchain_test: BlockchainTestFiller, blocknum_target: int):
    """
    Test BLOCKHASH witness.
    """
    _blockhash(blockchain_test, blocknum_target)


@pytest.mark.valid_from("Verkle")
def test_blockhash_warm(blockchain_test: BlockchainTestFiller):
    """
    Test BLOCKHASH witness with warm cost.
    """
    _blockhash(blockchain_test, block_number - 2, warm=True)


@pytest.mark.valid_from("Verkle")
def test_blockhash_insufficient_gas(blockchain_test: BlockchainTestFiller):
    """
    Test BLOCKHASH with insufficient gas for witness addition.
    """
    # 21_223 = 21_000 + (one code-chunk) 200 + (PUSH2) 3 + (BLOCKHASH constant cost) 20
    _blockhash(blockchain_test, block_number - 2, gas_limit=21_223, fail=True)


def _blockhash(
    blockchain_test: BlockchainTestFiller,
    blocknum_target: int,
    gas_limit: int = 1_000_000,
    warm: bool = False,
    fail: bool = False,
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=0,
        timestamp=1000,
    )

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(code=Op.BLOCKHASH(blocknum_target) * (2 if warm else 1)),
    }

    # Create block_number-1 empty blocks to fill the ring buffer.
    blocks: list[Block] = []
    for b in range(block_number - 1):
        blocks.append(Block())

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=gas_limit,
        gas_price=10,
    )

    witness_check = WitnessCheck(fork=Verkle)
    for address in [env.fee_recipient, TestAddress, TestAddress2]:
        witness_check.add_account_full(address=address, account=pre.get(address))
    code_chunks = chunkify_code(pre[TestAddress2].code)
    for i, chunk in enumerate(code_chunks, start=0):
        witness_check.add_code_chunk(address=TestAddress2, chunk_number=i, value=chunk)

    # TODO(verkle): when system contract exhaustive checks are supported in the testing library,
    # add here the 2935 actions on the witness too.

    # TODO(verkle): Today the only way to create these assertions is by hardcoding the values.
    # If in the future the testing library can calculate these upfront, we should
    # calculate them instead of hardcoding them.
    hardcoded_blockhash = {
        block_number - 2: Hash(0x127986F98B6BAB3B2AF5AC250912018D9982696E7B9B364D28190FA68C0AB49D),
        block_number
        - BLOCKHASH_SERVE_WINDOW: Hash(
            0xBBB791529CE751AC1FDC021C21B0A7F13A22905BD5BB396EC3F57EBF97C0A14D
        ),
    }

    # If the execution isn't expected to fail due to insufficient gas, and we satisfy the
    # block number target condition defined in the spec, we should assert the appropriate slot
    # is in the witness.
    if not fail and not (
        blocknum_target >= block_number or blocknum_target + BLOCKHASH_SERVE_WINDOW < block_number
    ):
        witness_check.add_storage_slot(
            system_contract_address,
            blocknum_target % HISTORY_SERVE_WINDOW,
            hardcoded_blockhash.get(blocknum_target),
        )

    # The last block contains a single transaction with the BLOCKHASH instruction(s).
    blocks.append(
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    )

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
    )
