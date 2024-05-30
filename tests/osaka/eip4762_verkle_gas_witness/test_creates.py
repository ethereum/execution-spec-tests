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
    compute_create2_address,
    compute_create_address,
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
    Test *CREATE without sending value.
    """
    new_contract_witness = None  # TODO(verkle)
    _create(
        blockchain_test,
        fork,
        create_instruction,
        new_contract_witness,
        code_size,
        value=0,
    )


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
    Test *CREATE sending value.
    """
    new_contract_witness = None  # TODO(verkle)
    _create(
        blockchain_test,
        fork,
        create_instruction,
        new_contract_witness,
    )


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
    "gas_limit, exp_new_contract_witness",
    [
        ["TBD1", "TBD1"],
        ["TBD2", "TBD2"],
        ["TBD3", "TBD3"],
    ],
    ids=[
        "insufficient_63/64_reservation",
        "insufficient_for_contract_init",
        "insufficient_for_all_contract_completion",
        "insufficient_for_all_code_chunks",
    ],
)
def test_create_insufficient_gas(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    create_instruction,
    gas_limit,
    exp_new_contract_witness,
):
    """
    Test *CREATE  with insufficient gas at different points of execution.
    """
    _create(
        blockchain_test, fork, create_instruction, exp_new_contract_witness, gas_limit=gas_limit
    )


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
def test_create_collision(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    create_instruction,
):
    """
    Test *CREATE  with address collision.
    """
    new_contract_witness = None
    _create(
        blockchain_test,
        fork,
        create_instruction,
        new_contract_witness,
        generate_collision=True,
    )


def _create(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    create_instruction,
    new_contract_witness,
    code_size=130 * 31,
    value=1,
    gas_limit=10000000000,
    generate_collision: bool = False,
):
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

    contract_code = Initcode(deploy_code=Op.PUSH0 * code_size)

    if create_instruction == Op.CREATE:
        pre[TestAddress2] = Account(
            code=Op.CALLDATACOPY(0, 0, len(contract_code))
            + Op.CREATE(value, 0, len(contract_code))
        )
        tx_target = TestAddress2
        tx_value = 0
        tx_data = contract_code.bytecode
        if generate_collision:
            contract_address = compute_create_address(TestAddress, 0)
            pre[contract_address] = Account(nonce=1)
    elif create_instruction == Op.CREATE2:
        pre[TestAddress2] = Account(
            code=Op.CALLDATACOPY(0, 0, len(contract_code))
            + Op.CREATE2(value, 0, len(contract_code), 0xDEADBEEF)
        )
        tx_target = TestAddress2
        tx_value = 0
        tx_data = contract_code.bytecode
        if generate_collision:
            contract_address = compute_create2_address(TestAddress, 0xDEADBEEF, contract_code)
            pre[contract_address] = Account(nonce=1)
    else:
        tx_target = None
        tx_value = value
        tx_data = contract_code.bytecode
        if generate_collision:
            contract_address = compute_create_address(TestAddress, 0)
            pre[contract_address] = Account(nonce=1)

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=tx_target,
        gas_limit=gas_limit,
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
