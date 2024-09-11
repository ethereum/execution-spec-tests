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
    if create_instruction is None:
        contract_address = compute_create_address(address=TestAddress, nonce=0)
    elif create_instruction == Op.CREATE:
        contract_address = compute_create_address(address=TestAddress2, nonce=0)
    else:
        contract_address = compute_create2_address(
            TestAddress2, 0xDEADBEEF, Initcode(deploy_code=contract_code)
        )

    num_code_chunks = (len(contract_code) + 30) // 31

    witness_check_extra = WitnessCheck(fork=Verkle)
    witness_check_extra.add_account_full(contract_address, None)
    for i in range(num_code_chunks):
        witness_check_extra.add_code_chunk(contract_address, i, None)

    _create(
        blockchain_test,
        create_instruction,
        witness_check_extra,
        contract_code,
        value=0,
    )


@pytest.mark.valid_from("Verkle")
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
        WitnessCheck(fork=Verkle),
        contract_code,
        value=100,
        creator_balance=0,
    )


@pytest.mark.valid_from("Verkle")
@pytest.mark.skip("Pending TBD gas limits")
@pytest.mark.parametrize(
    "create_instruction",
    [
        None,
        Op.CREATE,
        Op.CREATE2,
    ],
)
@pytest.mark.parametrize(
    "gas_limit, witness_basic_data, witness_codehash, witness_chunk_count",
    [
        ("TBD", False, False, 0),
        ("TBD", False, False, 0),
        ("TBD", True, False, 0),
        ("TBD", True, False, 3),
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
    create_instruction,
    gas_limit,
    witness_basic_data: bool,
    witness_codehash: bool,
    witness_chunk_count: int,
):
    """
    Test *CREATE  with insufficient gas at different points of execution.
    """
    contract_code = Op.PUSH0 * (129 * 31 + 42)
    if create_instruction is None or create_instruction == Op.CREATE:
        contract_address = compute_create_address(address=TestAddress, nonce=0)
    else:
        contract_address = compute_create2_address(
            TestAddress, 0xDEADBEEF, Initcode(deploy_code=contract_code)
        )

    code_chunks = chunkify_code(bytes(contract_code))

    witness_check_extra = WitnessCheck(fork=Verkle)
    if witness_basic_data and witness_codehash:
        witness_check_extra.add_account_full(contract_address, None)
        for i in range(witness_chunk_count):
            witness_check_extra.add_code_chunk(contract_address, i, code_chunks[i])  # type: ignore
    elif witness_basic_data and not witness_codehash:
        witness_check_extra.add_account_basic_data(contract_address, None)
        # No code chunks since we failed earlier.

    _create(
        blockchain_test,
        create_instruction,
        witness_check_extra,
        contract_code,
        value=0,
        gas_limit=gas_limit,
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
        WitnessCheck(
            fork=Verkle
        ),  # Static cost fail means the created contract shouldn't be in the witness
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
def test_create_collision(
    blockchain_test: BlockchainTestFiller,
    create_instruction,
):
    """
    Test tx contract creation and *CREATE with address collision.
    """
    _create(
        blockchain_test,
        create_instruction,
        WitnessCheck(
            fork=Verkle
        ),  # Collision means the created contract shouldn't be in the witness
        Op.PUSH0 * (129 * 31 + 42),
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
def test_big_calldata(
    blockchain_test: BlockchainTestFiller,
    create_instruction,
):
    """
    Test *CREATE checking that code-chunk touching in the witness is not calculated from calldata
    size but actual returned code from initcode execution.
    """
    contract_code = bytes(Op.PUSH0 * (1000 * 31 + 42))
    if create_instruction is None:
        contract_address = compute_create_address(address=TestAddress, nonce=0)
    elif create_instruction == Op.CREATE:
        contract_address = compute_create_address(address=TestAddress2, nonce=0)
    else:
        contract_address = compute_create2_address(
            TestAddress2, 0xDEADBEEF, Initcode(initcode_prefix=Op.STOP, deploy_code=contract_code)
        )

    witness_check_extra = WitnessCheck(fork=Verkle)
    witness_check_extra.add_account_full(contract_address, None)
    # No code chunks since we do an immediate STOP in the Initcode.

    _create(
        blockchain_test,
        create_instruction,
        witness_check_extra,
        contract_code,
        value=0,
        initcode_stop_prefix=True,
    )


def _create(
    blockchain_test: BlockchainTestFiller,
    create_instruction: Opcode | None,
    witness_check_extra: WitnessCheck,
    contract_code,
    value: int = 0,
    gas_limit=10000000000,
    generate_collision: bool = False,
    initcode_stop_prefix: bool = False,
    creator_balance: int = 0,
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
        if generate_collision:
            contract_address = compute_create_address(address=TestAddress2, nonce=0)
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
        if generate_collision:
            contract_address = compute_create2_address(TestAddress2, 0xDEADBEEF, deploy_code)
            pre[contract_address] = Account(nonce=1)
    else:
        tx_target = None
        tx_value = value
        tx_data = deploy_code
        if generate_collision:
            contract_address = compute_create_address(address=TestAddress, nonce=0)
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

    witness_check = witness_check_extra
    witness_check.add_account_full(env.fee_recipient, None)
    witness_check.add_account_full(TestAddress, pre[TestAddress])
    if tx_target is not None:
        witness_check.add_account_full(tx_target, pre[tx_target])

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
