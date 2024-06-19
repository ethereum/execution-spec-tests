"""
Test collision in CREATE/CREATE2 account creation, where the existing account only has a non-zero
storage slot set.
"""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Initcode,
    StateTestFiller,
    Transaction,
    compute_create_address,
)
from ethereum_test_tools import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7610.md"
REFERENCE_SPEC_VERSION = "80ef48d0bbb5a4939ade51caaaac57b5df6acd4e"


@pytest.mark.ported_from(
    [
        "https://github.com/ethereum/tests/blob/v13.3/src/GeneralStateTestsFiller/stSStoreTest/InitCollisionFiller.json",
        "https://github.com/ethereum/tests/blob/v13.3/src/GeneralStateTestsFiller/stSStoreTest/InitCollisionNonZeroNonceFiller.json",
        "https://github.com/ethereum/tests/blob/v13.3/src/GeneralStateTestsFiller/stSStoreTest/InitCollisionParisFiller.json",
    ],
    pr=["https://github.com/ethereum/execution-spec-tests/pull/1535"],
)
@pytest.mark.pre_alloc_modify  # We need to modify the pre-alloc to include the collision
@pytest.mark.with_all_contract_creating_tx_types
@pytest.mark.valid_from("Paris")
def test_init_collision_create_tx(
    state_test: StateTestFiller,
    pre: Alloc,
    tx_type: int,
):
    """
    Test that a contract creation transaction exceptionally aborts when the target address has a
    non-empty storage.
    """
    initcode = Initcode(
        deploy_code=Op.STOP,
        initcode_prefix=Op.SSTORE(0, 1) + Op.SSTORE(1, 0),
    )

    tx = Transaction(
        sender=pre.fund_eoa(),
        type=tx_type,
        to=None,
        data=initcode,
        gas_limit=200_000,
    )

    created_contract_address = tx.created_contract

    # This is the collision
    pre[created_contract_address] = Account(
        storage={0x01: 0x01},
        nonce=1,
    )

    state_test(
        pre=pre,
        post={
            created_contract_address: Account(
                storage={0x01: 0x01},
            ),
        },
        tx=tx,
    )


@pytest.mark.parametrize("opcode", [Op.CREATE, Op.CREATE2])
@pytest.mark.pre_alloc_modify  # We need to modify the pre-alloc to include the collision
@pytest.mark.valid_from("Paris")
def test_init_collision_create_opcode(
    state_test: StateTestFiller,
    pre: Alloc,
    opcode: Op,
):
    """
    Test that a contract creation opcode exceptionally aborts when the target address has a
    non-empty storage.
    """
    initcode = Initcode(
        deploy_code=Op.STOP,
        initcode_prefix=Op.SSTORE(0, 1) + Op.SSTORE(1, 0),
    )

    assert len(initcode) <= 32
    contract_creator_code = (
        Op.MSTORE(0, Op.PUSH32(bytes(initcode).ljust(32, b"\0")))
        + Op.SSTORE(0x01, opcode(value=0, offset=0, size=len(initcode)))
        + Op.STOP
    )
    contract_creator_address = pre.deploy_contract(
        contract_creator_code,
        storage={0x01: 0x01},
    )
    created_contract_address = compute_create_address(
        address=contract_creator_address,
        nonce=1,
        salt=0,
        initcode=initcode,
        opcode=opcode,
    )

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=contract_creator_address,
        data=initcode,
        gas_limit=2_000_000,
    )

    pre[created_contract_address] = Account(
        storage={0x01: 0x01},
        nonce=1,
    )

    state_test(
        pre=pre,
        post={
            created_contract_address: Account(
                storage={0x01: 0x01},
            ),
            contract_creator_address: Account(storage={0x01: 0x00}),
        },
        tx=tx,
    )
