"""
abstract: Tests [EIP-6800: Ethereum state using a unified verkle tree]
(https://eips.ethereum.org/EIPS/eip-6800)
    Tests for [EIP-6800: Ethereum state using a unified verkle tree]
    (https://eips.ethereum.org/EIPS/eip-6800).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Block,
    Bytecode,
    BlockchainTestFiller,
    Environment,
    Initcode,
    TestAddress,
    Transaction,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6800.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "bytecode",
    [
        Bytecode(),
        Op.PUSH0 * 31,
        Op.PUSH0 * (31 + 1),
        Op.PUSH0 * (31 + 32),
        Op.PUSH0 * 24576,
        Op.PUSH0 * 10 + Op.PUSH10(0x42),  # |...pushnXXXXX...|
        Op.PUSH0 * (32 - 1 - 5) + Op.PUSH10(0x42),  # |...pushnXXX|XXX...|
        Op.PUSH0 * (32 - 1) + Op.PUSH10(0x42),  # |...pushn|XXXX...|
        Op.PUSH0 * (32 - 1) + Op.PUSH32(0x42),  # |...push32|XXXXX|X....|
    ],
    ids=[
        "empty",
        "0mod31",
        "1mod31",
        "32mod31",
        "max_size",
        "PUSHX_within_boundaries",
        "PUSHX_data_split",
        "PUSHX_perfect_split",
        "PUSH32_spanning_three_chunks",
    ],
)
def test_code_chunking(blockchain_test: BlockchainTestFiller, fork: str, bytecode: Bytecode):
    """
    Test that code chunking works correctly.
    """
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=None,
        gas_limit=100000000,
        gas_price=10,
        data=Initcode(deploy_code=bytecode).deploy_code,
    )
    blocks = [Block(txs=[tx])]

    contract_address = compute_create_address(TestAddress, tx.nonce)

    post = {
        contract_address: Account(
            code=bytecode,
        ),
    }

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
    )
