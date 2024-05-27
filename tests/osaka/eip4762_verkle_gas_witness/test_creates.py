"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    Environment,
    Initcode,
    TestAddress,
    TestAddress2,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "create_instruction",
    [
        None,
        Op.CREATE,
        Op.CREATE2,
    ],
)
@pytest.mark.parametrize(
    "code_size",
    [
        0,
        127 * 32,
        130 * 32,
    ],
    ids=[
        "empty",
        "all_chunks_in_account_header",
        "chunks_outside_account_header",
    ],
)
def test_create_without_value(
    blockchain_test: BlockchainTestFiller, fork: str, create_instruction, code_size
):
    """
    Test *CREATE witness.
    """
    _create(blockchain_test, fork, create_instruction, code_size, 0)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "create_instruction",
    [
        None,
        Op.CREATE,
        Op.CREATE2,
    ],
)
def test_create_with_value(blockchain_test: BlockchainTestFiller, fork: str, create_instruction):
    """
    Test *CREATE witness.
    """
    _create(blockchain_test, fork, create_instruction, 130 * 31, 1)


def _create(
    blockchain_test: BlockchainTestFiller, fork: str, create_instruction, code_size, value
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    sender_balance = 1000000000000000000000
    pre = {
        TestAddress: Account(balance=sender_balance),
    }

    contract_code = Initcode(deploy_code=Op.PUSH0 * code_size)

    if create_instruction == Op.CREATE:
        pre[TestAddress2] = Account(
            code=Op.CALLDATACOPY(0, 0, len(contract_code))
            + Op.CREATE(value, 0, len(contract_code))
        )
        tx_target = TestAddress2
        tx_value = 0
        tx_data = contract_code.bytecode
    elif create_instruction == Op.CREATE2:
        pre[TestAddress2] = Account(
            code=Op.CALLDATACOPY(0, 0, len(contract_code))
            + Op.CREATE2(value, 0, len(contract_code), 0xDEADBEEF)
        )
        tx_target = TestAddress2
        tx_value = 0
        tx_data = contract_code.bytecode
    else:
        tx_target = None
        tx_value = value
        tx_data = contract_code.bytecode

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=tx_target,
        gas_limit=100000000,
        gas_price=10,
        value=tx_value,
        data=tx_data,
    )
    blocks = [Block(txs=[tx])]

    # TODO(verkle): define witness assertion
    witness_keys = ""

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness_keys=witness_keys,
    )
