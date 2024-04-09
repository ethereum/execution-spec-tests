"""
Return data management around create2
Port call_outsize_then_create2_successful_then_returndatasizeFiller.json test
Port call_then_create2_successful_then_returndatasizeFiller.json test
"""

from typing import Dict, Union

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    Initcode,
    StateTestFiller,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.valid_from("Istanbul")
@pytest.mark.parametrize("call_return_size", [0x20, 0])
@pytest.mark.parametrize("create_type", [Op.CREATE, Op.CREATE2])
def test_create2_return_data(
    call_return_size: int,
    create_type: Op,
    state_test: StateTestFiller,
):
    """
    Validate that create2 return data does not interfere with previously existing memory
    """
    # Storage vars
    slot_returndatasize_before_create = 0
    slot_returndatasize_after_create = 1
    slot_code_worked = 2

    # Pre-Existing Addresses
    address_to = Address(0x0600)
    address_call = Address(0x0601)

    # CREATE2 Initcode
    create2_salt = 1
    initcode = Initcode(
        deploy_code=b"",
        initcode_prefix=Op.MSTORE(0, 0x112233) + Op.RETURN(0, 32) + Op.STOP(),
    )

    def make_create() -> bytes:
        if create_type == Op.CREATE2:
            return Op.CREATE2(0, 0x100, Op.CALLDATASIZE(), create2_salt)
        elif create_type == Op.CREATE:
            return Op.CREATE(0, 0x100, Op.CALLDATASIZE())
        return Op.STOP

    pre = {
        address_to: Account(
            balance=100000000,
            nonce=0,
            code=Op.JUMPDEST()
            + Op.MSTORE(0x100, Op.CALLDATALOAD(0))
            + Op.CALL(0x0900000000, address_call, 0, 0, 0, 0, call_return_size)
            + Op.SSTORE(slot_returndatasize_before_create, Op.RETURNDATASIZE())
            + make_create()
            + Op.SSTORE(slot_returndatasize_after_create, Op.RETURNDATASIZE())
            + Op.SSTORE(slot_code_worked, 1)
            + Op.STOP(),
            storage={
                slot_returndatasize_before_create: 0xFF,
                slot_returndatasize_after_create: 0xFF,
            },
        ),
        address_call: Account(
            balance=0,
            nonce=0,
            code=Op.JUMPDEST()
            + Op.MSTORE(0, 0x0000111122223333444455556666777788889999AAAABBBBCCCCDDDDEEEEFFFF)
            + Op.RETURN(0, 32),
            storage={},
        ),
        TestAddress: Account(
            balance=7000000000000000000,
            nonce=0,
            code="0x",
            storage={},
        ),
    }

    post: Dict[Address, Union[Account, object]] = {}

    post[address_to] = Account(
        storage={
            slot_code_worked: 1,
            slot_returndatasize_before_create: 32,
            slot_returndatasize_after_create: 0,
        }
    )

    tx = Transaction(
        ty=0x0,
        chain_id=0x0,
        nonce=0,
        to=address_to,
        gas_price=10,
        protected=False,
        data=initcode.bytecode,
        gas_limit=0x0A00000000,
        value=0,
    )

    state_test(env=Environment(), pre=pre, post=post, tx=tx)
