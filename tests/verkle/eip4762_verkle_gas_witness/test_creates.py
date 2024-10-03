"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_forks import Verkle
from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    Bytecode,
    Environment,
    Initcode,
    Opcode,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
    compute_create2_address,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.verkle.helpers import chunkify_code

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


@pytest.mark.valid_from("Verkle")
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
        127 * 31,
        130 * 31,
        130 * 31 + 1,
    ],
    ids=[
        "empty",
        "all_chunks_in_account_header",
        "chunks_outside_account_header",
        "with_partial_code_chunk",
    ],
)
def test_create(blockchain_test: BlockchainTestFiller, create_instruction: Opcode, code_size):
    """
    Test tx contract creation and *CREATE witness.
    """
    contract_code = bytes(Op.PUSH0 * code_size)
    _create(
        blockchain_test,
        create_instruction,
        contract_code,
        value=0,
    )


@pytest.mark.valid_from("Verkle")
@pytest.mark.skip("TBD when exhaustive check PR gets merged")
@pytest.mark.parametrize(
    "create_instruction",
    [
        Op.CREATE,
        Op.CREATE2,
    ],
)
def test_create_with_value_insufficient_balance(
    blockchain_test: BlockchainTestFiller,
    create_instruction: Opcode,
):
    """
    Test tx contract creation and *CREATE value-bearing without sufficient balance.
    """
    contract_code = bytes(Op.PUSH0 * 10)

    _create(
        blockchain_test,
        create_instruction,
        contract_code,
        value=100,  # TODO(verkle): generalize with value>0 and enough balance?
        creator_balance=0,
    )


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "extra_gas_limit, witness_basic_data, witness_codehash, witness_codechunk_count",
    [
        (2099, False, False, 0),
        (2100 + 199, True, False, 0),
        (2100 + 200, True, True, 0),
        (2100 + 200 + 3499, True, True, 0),
        (2100 + 200 + 3500 + 499, True, True, 0),
        (2100 + 200 + 3500 + 500 + 811, True, True, 0),
        (2100 + 200 + 3500 + 500 + 811 + 5 * (500 + 200), True, True, 5),
    ],
    ids=[
        "insufficient_for_basic_data",
        "insufficient_for_basic_data_and_codehash",
        "enough_only_for_basic_data_and_codehash",
        "insufficient_for_contract_init_basic_data",
        "insufficient_for_contract_init_code_hash",
        "insufficient_for_any_code_chunk_range",
        "insufficient_for_all_code_chunk_range",
    ],
)
def test_insufficient_gas_tx_create(
    blockchain_test: BlockchainTestFiller,
    extra_gas_limit: int,
    witness_basic_data: bool,
    witness_codehash: bool,
    witness_codechunk_count: int,
):
    """
    Test tx creation with insufficient gas at different points of execution.
    """
    base_gas = 118_074
    contract_code = Op.PUSH0 * (129 * 31 + 42)
    _create(
        blockchain_test,
        None,
        contract_code,
        value=0,
        gas_limit=base_gas + extra_gas_limit,
        witness_basic_data=witness_basic_data,
        witness_codehash=witness_codehash,
        witness_codechunk_count=witness_codechunk_count,
    )


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "create_instruction",
    [
        Op.CREATE,
        Op.CREATE2,
    ],
)
@pytest.mark.parametrize(
    "extra_gas_limit, witness_basic_data, witness_codehash, witness_codechunk_count",
    [
        (2099, False, False, 0),
        (2100 + 199, True, False, 0),
        (2100 + 200, True, True, 0),
        (2100 + 200 + 3499, True, True, 0),
        (2100 + 200 + 3500 + 499, True, True, 0),
        (2100 + 200 + 3500 + 500 + 811, True, True, 0),
        (2100 + 200 + 3500 + 500 + 811 + 5 * (500 + 200), True, True, 5),
    ],
    ids=[
        "insufficient_for_basic_data",
        "insufficient_for_basic_data_and_codehash",
        "enough_only_for_basic_data_and_codehash",
        "insufficient_for_contract_init_basic_data",
        "insufficient_for_contract_init_code_hash",
        "insufficient_for_any_code_chunk_range",
        "insufficient_for_all_code_chunk_range",
    ],
)
def test_insufficient_gas_creates(
    blockchain_test: BlockchainTestFiller,
    create_instruction,
    extra_gas_limit: int,
    witness_basic_data: bool,
    witness_codehash: bool,
    witness_codechunk_count: int,
):
    """
    Test CREATE* with insufficient gas at different points of execution.
    """
    if create_instruction is not None and create_instruction.int() == Op.CREATE.int():
        base_gas = 88_088
    elif create_instruction is not None and create_instruction.int() == Op.CREATE2.int():
        base_gas = 88_853

    contract_code = Op.PUSH0 * (129 * 31 + 42)

    _create(
        blockchain_test,
        create_instruction,
        contract_code,
        value=0,
        gas_limit=base_gas + (extra_gas_limit * 64) // 63,
        witness_basic_data=witness_basic_data,
        witness_codehash=witness_codehash,
        witness_codechunk_count=witness_codechunk_count,
    )


@pytest.mark.valid_from("Verkle")
@pytest.mark.skip("Pending TBD gas limits")
@pytest.mark.parametrize(
    "create_instruction, gas_limit",
    [
        (Op.CREATE, "TBD"),
        (Op.CREATE2, "TBD"),
    ],
)
def test_create_static_cost(
    blockchain_test: BlockchainTestFiller,
    create_instruction,
    gas_limit,
):
    """
    Test *CREATE  with insufficient gas to pay for static cost.
    """
    _create(
        blockchain_test,
        create_instruction,
        Op.PUSH0 * (129 * 31 + 42),
        value=0,
        gas_limit=gas_limit,
    )


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "create_instruction",
    [
        None,
        Op.CREATE,
        Op.CREATE2,
    ],
)
def test_create_collision(blockchain_test: BlockchainTestFiller, create_instruction):
    """
    Test tx contract creation and *CREATE with address collision.
    """
    _create(
        blockchain_test,
        create_instruction,
        Op.PUSH0 * (3 * 31 + 42),
        value=0,
        generate_collision=True,
    )


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "create_instruction",
    [
        None,
        Op.CREATE,
        Op.CREATE2,
    ],
)
def test_create_big_calldata(
    blockchain_test: BlockchainTestFiller,
    create_instruction,
):
    """
    Test *CREATE checking that code-chunk touching in the witness is not calculated from calldata
    size but actual returned code from initcode execution.
    """
    contract_code = bytes(Op.PUSH0 * (10 * 31 + 42))
    _create(
        blockchain_test,
        create_instruction,
        contract_code,
        value=0,
        initcode_stop_prefix=True,
    )


def _create(
    blockchain_test: BlockchainTestFiller,
    create_instruction: Opcode | None,
    contract_code,
    value: int = 0,
    gas_limit=10000000000,
    generate_collision: bool = False,
    initcode_stop_prefix: bool = False,
    creator_balance: int = 0,
    witness_basic_data: bool = True,
    witness_codehash: bool = True,
    witness_codechunk_count: int | None = None,
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    pre = {
        TestAddress: Account(balance=1_000_000_000_000),
    }

    deploy_code = Initcode(
        initcode_prefix=Op.STOP if initcode_stop_prefix else Bytecode(), deploy_code=contract_code
    )
    if create_instruction is not None and create_instruction.int() == Op.CREATE.int():
        pre[TestAddress2] = Account(
            code=Op.CALLDATACOPY(0, 0, len(deploy_code)) + Op.CREATE(value, 0, len(deploy_code)),
            balance=creator_balance,
        )
        tx_target = TestAddress2
        tx_value = 0
        tx_data = deploy_code
        contract_address = compute_create_address(address=TestAddress2, nonce=0)
        if generate_collision:
            pre[contract_address] = Account(nonce=1)
    elif create_instruction is not None and create_instruction.int() == Op.CREATE2.int():
        pre[TestAddress2] = Account(
            code=Op.CALLDATACOPY(0, 0, len(deploy_code))
            + Op.CREATE2(value, 0, len(deploy_code), 0xDEADBEEF),
            balance=creator_balance,
        )
        tx_target = TestAddress2
        tx_value = 0
        tx_data = deploy_code
        contract_address = compute_create2_address(TestAddress2, 0xDEADBEEF, deploy_code)
        if generate_collision:
            pre[contract_address] = Account(nonce=1)
    else:
        tx_target = None
        tx_value = value
        tx_data = deploy_code
        contract_address = compute_create_address(address=TestAddress, nonce=0)
        if generate_collision:
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

    witness_check = WitnessCheck(fork=Verkle)
    witness_check.add_account_full(env.fee_recipient, None)
    witness_check.add_account_full(TestAddress, pre[TestAddress])
    if tx_target is not None:
        witness_check.add_account_full(tx_target, pre[tx_target])
        # Include code that executes the CREATE*
        code_chunks = chunkify_code(pre[tx_target].code)
        for i, chunk in enumerate(code_chunks, start=0):
            witness_check.add_code_chunk(address=tx_target, chunk_number=i, value=chunk)

    # The contract address will always appear in the witness:
    # - If there's a collision, it should contain the existing contract for the collision check.
    # - Otherwise, it should prove there's no collision.
    # Under normal circumstances we'd add both basic_data & codehash in the witness. This is
    # separated in two ifs to support testing the gas cost of each witness part separately.
    if witness_basic_data:
        witness_check.add_account_basic_data(contract_address, pre.get(contract_address))
    if witness_codehash:
        witness_check.add_account_codehash(contract_address, pre.get(contract_address))

    # Assert the code-chunks where the contract is deployed are provided
    # DO NOT include the code-chunks if there was a collision, or we're testing that
    # code-chunk inclusion isn't based on calldata size (see big_calldata test).
    if not generate_collision and not initcode_stop_prefix:
        code_chunks = chunkify_code(bytes(deploy_code.deploy_code))
        for i, chunk in enumerate(code_chunks, start=0):
            if witness_codechunk_count is None or i < witness_codechunk_count:
                witness_check.add_code_chunk(address=contract_address, chunk_number=i, value=None)

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
    )
