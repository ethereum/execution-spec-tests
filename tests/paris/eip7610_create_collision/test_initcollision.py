"""
Test collision in CREATE/CREATE2 account creation, where the existing account only has a non-zero
storage slot set.
"""

import pytest

from ethereum_test_tools import Account, Alloc, Environment, Initcode
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    StateTestFiller,
    Transaction,
    compute_create2_address,
    compute_create_address,
)

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7610.md"
REFERENCE_SPEC_VERSION = "80ef48d0bbb5a4939ade51caaaac57b5df6acd4e"


@pytest.mark.parametrize("nonce", [0, 1])
@pytest.mark.pre_alloc_modifier  # We need to modify the pre-alloc to include the collision
@pytest.mark.with_all_contract_creating_tx_types
@pytest.mark.valid_from("Paris")
def test_init_collision_create_tx(
    state_test: StateTestFiller,
    pre: Alloc,
    nonce: int,
    tx_type: int,
):
    """
    Test that a contract creation transaction exceptionally aborts when the target address has a
    non-empty storage.
    """
    env = Environment()

    sender = pre.fund_eoa()

    initcode = Initcode(
        deploy_code=Op.STOP,
        initcode_prefix=Op.SSTORE(0, 1) + Op.SSTORE(1, 0),
    )

    tx = Transaction(
        sender=sender,
        type=tx_type,
        to=None,
        data=initcode,
        gas_limit=200_000,
    )

    created_contract_address = tx.created_contract

    pre[created_contract_address] = Account(
        storage={0x01: 0x01},
        nonce=nonce,
    )

    state_test(
        env=env,
        pre=pre,
        post={
            created_contract_address: Account(
                storage={0x01: 0x01},
            ),
        },
        tx=tx,
    )


@pytest.mark.parametrize("opcode", [Op.CREATE, Op.CREATE2])
@pytest.mark.parametrize("nonce", [0, 1])
@pytest.mark.pre_alloc_modifier  # We need to modify the pre-alloc to include the collision
@pytest.mark.valid_from("Paris")
def test_init_collision_create_opcode(
    state_test: StateTestFiller,
    pre: Alloc,
    nonce: int,
    opcode: Op,
):
    """
    Test that a contract creation opcode exceptionally aborts when the target address has a
    non-empty storage.
    """
    env = Environment()

    sender = pre.fund_eoa()

    initcode = Initcode(
        deploy_code=Op.STOP,
        initcode_prefix=Op.SSTORE(0, 1) + Op.SSTORE(1, 0),
    )

    salt = 0x0
    salt_param = [salt] if opcode == Op.CREATE2 else []
    assert len(initcode) <= 32
    contract_creator_code = (
        Op.MSTORE(0, Op.PUSH32(bytes(initcode).ljust(32, b"\0")))
        + Op.SSTORE(0x01, opcode(0, 0, len(initcode), *salt_param))
        + Op.STOP
    )
    contract_creator_address = pre.deploy_contract(
        contract_creator_code,
        storage={0x01: 0x01},
    )
    if opcode == Op.CREATE2:
        created_contract_address = compute_create2_address(
            contract_creator_address, salt, initcode
        )
    elif opcode == Op.CREATE:
        created_contract_address = compute_create_address(contract_creator_address, 1)
    else:
        raise ValueError(f"Unknown opcode: {opcode}")

    tx = Transaction(
        sender=sender,
        to=contract_creator_address,
        data=initcode,
        gas_price=10,
        gas_limit=2_000_000,
    )

    pre[created_contract_address] = Account(
        storage={0x01: 0x01},
        nonce=nonce,
    )

    state_test(
        env=env,
        pre=pre,
        post={
            created_contract_address: Account(
                storage={0x01: 0x01},
            ),
            contract_creator_address: Account(storage={0x01: 0x00}),
        },
        tx=tx,
    )
