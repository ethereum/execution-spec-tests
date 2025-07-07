"""
Test dynamically created address is still callable and perform storage operations
after being called for self destruct in a call.
"""

from enum import Enum

import pytest

from ethereum_test_forks import Byzantium, Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Case,
    Environment,
    Initcode,
    StateTestFiller,
    Storage,
    Switch,
    Transaction,
    compute_create_address,
)
from ethereum_test_tools import Opcodes as Op


class Operation(Enum):
    """Enum for created contract actions."""

    SUICIDE = 1
    ADD_STORAGE = 2
    GET_STORAGE = 3

    def __int__(self):
        """Convert to int."""
        return int(self.value)


@pytest.mark.ported_from(
    [
        "https://github.com/ethereum/tests/blob/v13.3/src/GeneralStateTestsFiller/stCreateTest/CREATE_AcreateB_BSuicide_BStoreFiller.json",
    ],
    pr=["https://github.com/ethereum/execution-spec-tests/pull/1867"],
    # coverage_missed_reason="Converting solidity code result in following opcode not being used:"
    # "PUSH29, DUP4, DUP8, SWAP2, ISZERO, AND, MUL, DIV, CALLVALUE, EXTCODESIZE",
)
@pytest.mark.valid_from("Frontier")
@pytest.mark.with_all_create_opcodes
def test_create_suicide_store(
    state_test: StateTestFiller,
    fork: Fork,
    pre: Alloc,
    create_opcode: Op,
):
    """
    Create dynamic contract that suicides, then called to push some storage
    and then called to return that storage value.
    """
    tload_support = fork.valid_opcodes().count(Op.TLOAD)
    subcall_storage = 0x12
    suicide_initcode: Initcode = Initcode(
        deploy_code=Switch(
            cases=[
                Case(
                    condition=Op.EQ(Op.CALLDATALOAD(0), int(Operation.SUICIDE)),
                    action=Op.SELFDESTRUCT(0x11),
                ),
                Case(
                    condition=Op.EQ(Op.CALLDATALOAD(0), int(Operation.ADD_STORAGE)),
                    action=Op.SSTORE(1, Op.ADD(Op.SLOAD(1), subcall_storage))
                    + (
                        Op.TSTORE(1, Op.ADD(Op.TLOAD(1), subcall_storage))
                        if tload_support
                        else Op.STOP
                    ),
                ),
                Case(
                    condition=Op.EQ(Op.CALLDATALOAD(0), int(Operation.GET_STORAGE)),
                    action=(
                        Op.MSTORE(0, Op.ADD(Op.SLOAD(1), Op.TLOAD(1)))
                        if tload_support
                        else Op.MSTORE(0, Op.SLOAD(1))
                    )
                    + Op.RETURN(0, 32),
                ),
            ],
            default_action=None,
        )
    )

    sender = pre.fund_eoa()
    expect_post = Storage()

    slot_create_result = 0
    slot_after_suicide_sstore_return = 1
    slot_program_success = 2
    create_contract = pre.deploy_contract(
        code=Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
        + Op.SSTORE(slot_create_result, create_opcode(size=Op.CALLDATASIZE()))
        # Put some storage before suicide
        + Op.MSTORE(64, int(Operation.ADD_STORAGE))
        + Op.CALL(
            gas=Op.SUB(Op.GAS, 300_000),
            address=Op.SLOAD(slot_create_result),
            args_offset=64,
            args_size=32,
        )
        + Op.MSTORE(64, int(Operation.SUICIDE))
        + Op.CALL(
            gas=Op.SUB(Op.GAS, 300_000),
            address=Op.SLOAD(slot_create_result),
            args_offset=64,
            args_size=32,
        )
        # Put some storage after suicide
        + Op.MSTORE(64, int(Operation.ADD_STORAGE))
        + Op.CALL(
            gas=Op.SUB(Op.GAS, 300_000),
            address=Op.SLOAD(slot_create_result),
            args_offset=64,
            args_size=32,
        )
        + Op.MSTORE(64, int(Operation.GET_STORAGE))
        + Op.CALL(
            gas=Op.SUB(Op.GAS, 300_000),
            address=Op.SLOAD(0),
            args_offset=64,
            args_size=32,
            ret_offset=100,
            ret_size=32,
        )
        + Op.SSTORE(slot_after_suicide_sstore_return, Op.MLOAD(100))
        + Op.SSTORE(slot_program_success, 1)
    )

    expected_create_address = compute_create_address(
        address=create_contract, nonce=1, initcode=suicide_initcode, opcode=create_opcode
    )
    expect_post[slot_create_result] = expected_create_address
    expect_post[slot_after_suicide_sstore_return] = (
        subcall_storage * 2  # added value before and after suicide
        + (subcall_storage * 2 if tload_support else 0)  # tload value added
    )
    expect_post[slot_program_success] = 1

    tx = Transaction(
        gas_limit=1_000_000,
        to=create_contract,
        data=suicide_initcode,
        nonce=0,
        sender=sender,
        protected=fork >= Byzantium,
    )

    post = {
        create_contract: Account(storage=expect_post),
        expected_create_address: Account.NONEXISTENT,
    }
    state_test(env=Environment(), pre=pre, post=post, tx=tx)
