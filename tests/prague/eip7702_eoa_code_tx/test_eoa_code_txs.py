"""
abstract: Tests use of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702)
    Tests use of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702).
"""  # noqa: E501

from enum import Enum
from itertools import count

import pytest
from ethereum.crypto.hash import keccak256

from ethereum_test_tools import (
    Account,
    Alloc,
    AuthorizationTuple,
    Block,
    BlockchainTestFiller,
    Bytecode,
    Conditional,
    Environment,
    Initcode,
)
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    StateTestFiller,
    Storage,
    Transaction,
    compute_create2_address,
    compute_create_address,
)

from .spec import ref_spec_7702

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version

pytestmark = pytest.mark.valid_from("Prague")

# FIXME: Temporary workaround, should be zero
auth_account_start_balance = 1


class InvalidityReason(Enum):
    """
    Reasons for invalidity.
    """

    NONCE = "nonce"
    MULTIPLE_NONCE = "multiple_nonce"
    CHAIN_ID = "chain_id"
    ZERO_LENGTH_AUTHORIZATION_LIST = "zero_length_authorization_list"  # TODO: Implement test


@pytest.mark.parametrize(
    "tx_value",
    [0, 1],
)
@pytest.mark.parametrize(
    "suffix,succeeds",
    [
        pytest.param(Op.STOP, True, id="stop"),
        pytest.param(Op.RETURN(0, 0), True, id="return"),
        pytest.param(Op.REVERT, False, id="revert"),
        pytest.param(Op.INVALID, False, id="invalid"),
    ],
)
def test_self_sponsored_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
    suffix: Bytecode,
    succeeds: bool,
    tx_value: int,
):
    """
    Test the executing a self-sponsored set-code transaction.

    The transaction is sent to the sender, and the sender is the signer of the only authorization
    tuple in the authorization list.

    The authorization tuple has a nonce of 1 because the self-sponsored transaction increases the
    nonce of the sender from zero to one first.

    The expected nonce at the end of the transaction is 2.
    """
    storage = Storage()
    sender = pre.fund_eoa()

    set_code = (
        Op.SSTORE(storage.store_next(sender), Op.ORIGIN)
        + Op.SSTORE(storage.store_next(sender), Op.CALLER)
        + Op.SSTORE(storage.store_next(tx_value), Op.CALLVALUE)
        + suffix
    )
    set_code_to_address = pre.deploy_contract(
        set_code,
    )

    tx = Transaction(
        gas_limit=10_000_000,
        to=sender,
        value=tx_value,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=1,
                signer=sender,
            ),
        ],
        sender=sender,
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address: Account(storage={k: 0 for k in storage}),
            sender: Account(nonce=2, code=b"", storage=storage if succeeds else {}),
        },
    )


@pytest.mark.parametrize(
    "eoa_balance",
    [
        pytest.param(0, marks=pytest.mark.xfail(reason="evm fails on zero balance")),
        pytest.param(1),
    ],
)
@pytest.mark.parametrize(
    "tx_value",
    [0, 1],
)
@pytest.mark.parametrize(
    "suffix,succeeds",
    [
        pytest.param(Op.STOP, True, id="stop"),
        pytest.param(Op.RETURN(0, 0), True, id="return"),
        pytest.param(Op.REVERT, False, id="revert"),
        pytest.param(Op.INVALID, False, id="invalid"),
    ],
)
def test_set_code_to_sstore(
    state_test: StateTestFiller,
    pre: Alloc,
    suffix: Bytecode,
    succeeds: bool,
    tx_value: int,
    eoa_balance: int,
):
    """
    Test the executing a simple SSTORE in a set-code transaction.
    """
    storage = Storage()
    auth_signer = pre.fund_eoa(eoa_balance)
    sender = pre.fund_eoa()

    set_code = (
        Op.SSTORE(storage.store_next(sender), Op.ORIGIN)
        + Op.SSTORE(storage.store_next(sender), Op.CALLER)
        + Op.SSTORE(storage.store_next(tx_value), Op.CALLVALUE)
        + suffix
    )
    set_code_to_address = pre.deploy_contract(
        set_code,
    )

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=tx_value,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=sender,
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address: Account(storage={k: 0 for k in storage}),
            auth_signer: Account(nonce=1, code=b"", storage=storage if succeeds else {}),
        },
    )


def test_set_code_to_sstore_then_sload(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
):
    """
    Test the executing a simple SSTORE then SLOAD in two separate set-code transactions.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)
    sender = pre.fund_eoa()

    storage_key_1 = 0x1
    storage_key_2 = 0x2
    storage_value = 0x1234

    set_code_1 = Op.SSTORE(storage_key_1, storage_value) + Op.STOP
    set_code_1_address = pre.deploy_contract(set_code_1)

    set_code_2 = Op.SSTORE(storage_key_2, Op.ADD(Op.SLOAD(storage_key_1), 1)) + Op.STOP
    set_code_2_address = pre.deploy_contract(set_code_2)

    tx_1 = Transaction(
        gas_limit=50_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_1_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=sender,
    )

    tx_2 = Transaction(
        gas_limit=50_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_2_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=sender,
    )

    block = Block(
        txs=[tx_1, tx_2],
    )

    blockchain_test(
        pre=pre,
        post={
            auth_signer: Account(
                nonce=1,
                code=b"",
                storage={
                    storage_key_1: storage_value,
                    storage_key_2: storage_value + 1,
                },
            ),
        },
        blocks=[block],
    )


@pytest.mark.parametrize(
    "call_opcode",
    [
        Op.CALL,
        Op.DELEGATECALL,
        Op.STATICCALL,
        Op.CALLCODE,
    ],
)
@pytest.mark.parametrize(
    "return_opcode",
    [
        Op.RETURN,
        Op.REVERT,
    ],
)
def test_set_code_to_tstore_reentry(
    state_test: StateTestFiller,
    pre: Alloc,
    call_opcode: Op,
    return_opcode: Op,
):
    """
    Test the executing a simple TSTORE in a set-code transaction, which also performs a
    re-entry to TLOAD the value.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    tload_value = 0x1234
    set_code = Conditional(
        condition=Op.ISZERO(Op.TLOAD(1)),
        if_true=Op.TSTORE(1, tload_value)
        + call_opcode(address=Op.ADDRESS)
        + Op.RETURNDATACOPY(0, 0, 32)
        + Op.SSTORE(2, Op.MLOAD(0)),
        if_false=Op.MSTORE(0, Op.TLOAD(1)) + return_opcode(size=32),
    )
    set_code_to_address = pre.deploy_contract(set_code)

    tx = Transaction(
        gas_limit=100_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(nonce=1, code=b"", storage={2: tload_value}),
        },
    )


def test_set_code_to_self_destruct(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test the executing self-destruct opcode in a set-code transaction.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    set_code_to_address = pre.deploy_contract(Op.SSTORE(1, 1) + Op.SELFDESTRUCT(Op.ADDRESS))

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(nonce=1, code=b"", storage={1: 1}),
        },
    )


@pytest.mark.parametrize(
    "op",
    [
        Op.CREATE,
        Op.CREATE2,
    ],
)
def test_set_code_to_contract_creator(
    state_test: StateTestFiller,
    pre: Alloc,
    op: Op,
):
    """
    Test the executing a contract-creating opcode in a set-code transaction.
    """
    storage = Storage()
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    deployed_code = Op.STOP
    initcode = Initcode(deploy_code=deployed_code)

    deployed_contract_address = compute_create_address(
        address=auth_signer, salt=0, initcode=initcode, opcode=op
    )

    set_code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        storage.store_next(deployed_contract_address),
        op(value=0, offset=0, size=Op.CALLDATASIZE),
    )
    set_code_to_address = pre.deploy_contract(set_code)

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=0,
        data=initcode,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address: Account(storage={}),
            auth_signer: Account(nonce=2, code=b"", storage=storage),
            deployed_contract_address: Account(
                code=deployed_code,
                storage={},
            ),
        },
    )


@pytest.mark.parametrize(
    "op",
    [
        Op.CALL,
        Op.DELEGATECALL,
        Op.STATICCALL,
        Op.CALLCODE,
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        0,
        10**18,
    ],
)
def test_set_code_to_self_caller(
    state_test: StateTestFiller,
    pre: Alloc,
    op: Op,
    value: int,
):
    """
    Test the executing a self-call in a set-code transaction.
    """
    storage = Storage()
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    first_entry_slot = storage.store_next(True)
    re_entry_success_slot = storage.store_next(op != Op.STATICCALL)
    re_entry_call_return_code_slot = storage.store_next(op != Op.STATICCALL)
    set_code = Conditional(
        condition=Op.ISZERO(Op.SLOAD(first_entry_slot)),
        if_true=Op.SSTORE(first_entry_slot, 1)
        + Op.SSTORE(re_entry_call_return_code_slot, op(address=auth_signer, value=value))
        + Op.STOP,
        if_false=Op.SSTORE(re_entry_success_slot, 1) + Op.STOP,
    )
    set_code_to_address = pre.deploy_contract(set_code)

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=value,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(10**21),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address: Account(storage={}),
            auth_signer: Account(
                nonce=1,
                code=b"",
                storage=storage,
                balance=auth_account_start_balance + value,
            ),
        },
    )


@pytest.mark.parametrize(
    "op",
    [
        Op.CALL,
        Op.DELEGATECALL,
        Op.STATICCALL,
        Op.CALLCODE,
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        0,
        10**18,
    ],
)
def test_set_code_call_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
    op: Op,
    value: int,
):
    """
    Test the calling a set-code account from another set-code account.
    """
    auth_signer_1 = pre.fund_eoa(auth_account_start_balance)
    storage_1 = Storage()

    set_code_1_call_result_slot = storage_1.store_next(op != Op.STATICCALL)
    set_code_1_success = storage_1.store_next(True)

    auth_signer_2 = pre.fund_eoa(auth_account_start_balance)
    storage_2 = Storage().set_next_slot(storage_1.peek_slot())
    set_code_2_success = storage_2.store_next(op != Op.STATICCALL)

    set_code_1 = (
        Op.SSTORE(set_code_1_call_result_slot, op(address=auth_signer_2, value=value))
        + Op.SSTORE(set_code_1_success, 1)
        + Op.STOP
    )
    set_code_to_address_1 = pre.deploy_contract(set_code_1)

    set_code_2 = Op.SSTORE(set_code_2_success, 1) + Op.STOP
    set_code_to_address_2 = pre.deploy_contract(set_code_2)

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer_1,
        value=value,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address_1,
                nonce=0,
                signer=auth_signer_1,
            ),
            AuthorizationTuple(
                address=set_code_to_address_2,
                nonce=0,
                signer=auth_signer_2,
            ),
        ],
        sender=pre.fund_eoa(10**21),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address_1: Account(storage={k: 0 for k in storage_1}),
            set_code_to_address_2: Account(storage={k: 0 for k in storage_2}),
            auth_signer_1: Account(
                nonce=1,
                storage=storage_1 if op in [Op.CALL, Op.STATICCALL] else storage_1 + storage_2,
                balance=(0 if op == Op.CALL else value) + auth_account_start_balance,
            ),
            auth_signer_2: Account(
                nonce=1,
                storage=storage_2 if op == Op.CALL else {},
                balance=(value if op == Op.CALL else 0) + auth_account_start_balance,
            ),
        },
    )


def test_address_from_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test the address opcode in a set-code transaction.
    """
    storage = Storage()
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    set_code = Op.SSTORE(storage.store_next(auth_signer), Op.ADDRESS) + Op.STOP
    set_code_to_address = pre.deploy_contract(set_code)

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address: Account(storage={}),
            auth_signer: Account(nonce=1, code=b"", storage=storage),
        },
    )


def test_tx_into_self_delegating_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test a transaction that has entry-point into a set-code address that delegates to itself.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=auth_signer,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(nonce=1, code=b""),
        },
    )


def test_tx_into_chain_delegating_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test a transaction that has entry-point into a set-code address that delegates to itself.
    """
    auth_signer_1 = pre.fund_eoa(auth_account_start_balance)
    auth_signer_2 = pre.fund_eoa(auth_account_start_balance)

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer_1,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=auth_signer_2,
                nonce=0,
                signer=auth_signer_1,
            ),
            AuthorizationTuple(
                address=auth_signer_1,
                nonce=0,
                signer=auth_signer_2,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer_1: Account(nonce=1, code=b""),
            auth_signer_2: Account(nonce=1, code=b""),
        },
    )


@pytest.mark.parametrize(
    "call_opcode",
    [
        Op.CALL,
        Op.DELEGATECALL,
        Op.STATICCALL,
        Op.CALLCODE,
    ],
)
def test_call_into_self_delegating_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
    call_opcode: Op,
):
    """
    Test a transaction that has entry-point into a set-code address that delegates to itself.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    storage = Storage()
    entry_code = Op.SSTORE(storage.store_next(False), call_opcode(address=auth_signer)) + Op.STOP
    entry_address = pre.deploy_contract(entry_code)

    tx = Transaction(
        gas_limit=10_000_000,
        to=entry_address,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=auth_signer,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            entry_address: Account(storage=storage),
            auth_signer: Account(nonce=1, code=b""),
        },
    )


@pytest.mark.parametrize(
    "call_opcode",
    [
        Op.CALL,
        Op.DELEGATECALL,
        Op.STATICCALL,
        Op.CALLCODE,
    ],
)
def test_call_into_chain_delegating_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
    call_opcode: Op,
):
    """
    Test a transaction that has entry-point into a set-code address that delegates to itself.
    """
    auth_signer_1 = pre.fund_eoa(auth_account_start_balance)
    auth_signer_2 = pre.fund_eoa(auth_account_start_balance)

    storage = Storage()
    entry_code = Op.SSTORE(storage.store_next(False), call_opcode(address=auth_signer_1)) + Op.STOP
    entry_address = pre.deploy_contract(entry_code)

    tx = Transaction(
        gas_limit=10_000_000,
        to=entry_address,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=auth_signer_2,
                nonce=0,
                signer=auth_signer_1,
            ),
            AuthorizationTuple(
                address=auth_signer_1,
                nonce=0,
                signer=auth_signer_2,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            entry_address: Account(storage=storage),
            auth_signer_1: Account(nonce=1, code=b""),
            auth_signer_2: Account(nonce=1, code=b""),
        },
    )


@pytest.mark.parametrize(
    "balance",
    [
        pytest.param(0, marks=pytest.mark.xfail(reason="evm fails on zero balance")),
        pytest.param(10**18),
    ],
)
def test_ext_code_on_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
    balance: int,
):
    """
    Test different ext*code operations on a set-code address.
    """
    auth_signer = pre.fund_eoa(balance)

    slot = count(1)
    slot_call_success = next(slot)
    slot_caller = next(slot)
    slot_ext_code_size_result = next(slot)
    slot_ext_code_hash_result = next(slot)
    slot_ext_code_copy_result = next(slot)
    slot_ext_balance_result = next(slot)

    callee_code = (
        Op.SSTORE(slot_caller, Op.CALLER)
        + Op.SSTORE(slot_ext_code_size_result, Op.EXTCODESIZE(Op.CALLER))
        + Op.SSTORE(slot_ext_code_hash_result, Op.EXTCODEHASH(Op.CALLER))
        + Op.EXTCODECOPY(Op.CALLER, 0, 0, Op.EXTCODESIZE(Op.CALLER))
        + Op.SSTORE(slot_ext_code_copy_result, Op.MLOAD(0))
        + Op.SSTORE(slot_ext_balance_result, Op.BALANCE(Op.CALLER))
        + Op.STOP
    )
    callee_address = pre.deploy_contract(callee_code)
    callee_storage = Storage()

    auth_signer_storage = Storage()
    set_code = Op.SSTORE(slot_call_success, Op.CALL(address=callee_address)) + Op.STOP
    auth_signer_storage[slot_call_success] = True
    set_code_to_address = pre.deploy_contract(set_code)

    callee_storage[slot_caller] = auth_signer
    callee_storage[slot_ext_code_size_result] = len(set_code)
    callee_storage[slot_ext_code_hash_result] = set_code.keccak256()
    callee_storage[slot_ext_code_copy_result] = bytes(set_code).ljust(32, b"\x00")[:32]
    callee_storage[slot_ext_balance_result] = balance

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address: Account(storage={}),
            auth_signer: Account(nonce=1, code=b"", storage=auth_signer_storage, balance=balance),
            callee_address: Account(storage=callee_storage),
        },
    )


@pytest.mark.parametrize(
    "balance",
    [
        pytest.param(0, marks=pytest.mark.xfail(reason="evm fails on zero balance")),
        pytest.param(10**18),
    ],
)
def test_ext_code_on_self_delegating_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
    balance: int,
):
    """
    Test different ext*code operations on a set-code address that delegates to itself.
    """
    auth_signer = pre.fund_eoa(balance)

    slot = count(1)
    slot_ext_code_size_result = next(slot)
    slot_ext_code_hash_result = next(slot)
    slot_ext_code_copy_result = next(slot)
    slot_ext_balance_result = next(slot)

    callee_code = (
        Op.SSTORE(slot_ext_code_size_result, Op.EXTCODESIZE(auth_signer))
        + Op.SSTORE(slot_ext_code_hash_result, Op.EXTCODEHASH(auth_signer))
        + Op.EXTCODECOPY(auth_signer, 0, 0, Op.EXTCODESIZE(auth_signer))
        + Op.SSTORE(slot_ext_code_copy_result, Op.MLOAD(0))
        + Op.SSTORE(slot_ext_balance_result, Op.BALANCE(auth_signer))
        + Op.STOP
    )
    callee_address = pre.deploy_contract(callee_code)
    callee_storage = Storage()

    set_code = b"\xef\x01\x00" + bytes(auth_signer)
    callee_storage[slot_ext_code_size_result] = len(set_code)
    callee_storage[slot_ext_code_hash_result] = keccak256(set_code)
    callee_storage[slot_ext_code_copy_result] = bytes(set_code).ljust(32, b"\x00")[:32]
    callee_storage[slot_ext_balance_result] = balance

    tx = Transaction(
        gas_limit=10_000_000,
        to=callee_address,
        authorization_list=[
            AuthorizationTuple(
                address=auth_signer,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),  # TODO: Test with sender as auth_signer
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(nonce=1, code=b"", balance=balance),
            callee_address: Account(storage=callee_storage),
        },
    )


@pytest.mark.parametrize(
    "balance",
    [
        pytest.param(0, marks=pytest.mark.xfail(reason="evm fails on zero balance")),
        pytest.param(10**18),
    ],
)
def test_ext_code_on_chain_delegating_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
    balance: int,
):
    """
    Test different ext*code operations on a set-code address that references another delegated
    address.
    """
    auth_signer_1 = pre.fund_eoa(balance)
    auth_signer_2 = pre.fund_eoa(balance)

    slot = count(1)
    slot_ext_code_size_result = next(slot)
    slot_ext_code_hash_result = next(slot)
    slot_ext_code_copy_result = next(slot)
    slot_ext_balance_result = next(slot)

    callee_code = (
        Op.SSTORE(slot_ext_code_size_result, Op.EXTCODESIZE(auth_signer_1))
        + Op.SSTORE(slot_ext_code_hash_result, Op.EXTCODEHASH(auth_signer_1))
        + Op.EXTCODECOPY(auth_signer_1, 0, 0, Op.EXTCODESIZE(auth_signer_1))
        + Op.SSTORE(slot_ext_code_copy_result, Op.MLOAD(0))
        + Op.SSTORE(slot_ext_balance_result, Op.BALANCE(auth_signer_1))
        + Op.STOP
    )
    callee_address = pre.deploy_contract(callee_code)
    callee_storage = Storage()

    set_code = b"\xef\x01\x00" + bytes(auth_signer_2)
    callee_storage[slot_ext_code_size_result] = len(set_code)
    callee_storage[slot_ext_code_hash_result] = keccak256(set_code)
    callee_storage[slot_ext_code_copy_result] = bytes(set_code).ljust(32, b"\x00")[:32]
    callee_storage[slot_ext_balance_result] = balance

    tx = Transaction(
        gas_limit=10_000_000,
        to=callee_address,
        authorization_list=[
            AuthorizationTuple(
                address=auth_signer_2,
                nonce=0,
                signer=auth_signer_1,
            ),
            AuthorizationTuple(
                address=auth_signer_1,
                nonce=0,
                signer=auth_signer_2,
            ),
        ],
        sender=pre.fund_eoa(),  # TODO: Test with sender as auth_signer
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer_1: Account(nonce=1, code=b"", balance=balance),
            auth_signer_2: Account(nonce=1, code=b"", balance=balance),
            callee_address: Account(storage=callee_storage),
        },
    )


@pytest.mark.parametrize(
    "balance",
    [
        pytest.param(0, marks=pytest.mark.xfail(reason="evm fails on zero balance")),
        pytest.param(10**18),
    ],
)
def test_self_code_on_set_code(
    state_test: StateTestFiller,
    pre: Alloc,
    balance: int,
):
    """
    Test codesize and codecopy operations on a set-code address.
    """
    auth_signer = pre.fund_eoa(balance)

    slot = count(1)
    slot_code_size_result = next(slot)
    slot_code_copy_result = next(slot)
    slot_self_balance_result = next(slot)

    set_code = (
        Op.SSTORE(slot_code_size_result, Op.CODESIZE)
        + Op.CODECOPY(0, 0, Op.CODESIZE)
        + Op.SSTORE(slot_code_copy_result, Op.MLOAD(0))
        + Op.SSTORE(slot_self_balance_result, Op.SELFBALANCE)
        + Op.STOP
    )
    set_code_to_address = pre.deploy_contract(set_code)

    storage = Storage()
    storage[slot_code_size_result] = len(set_code)
    storage[slot_code_copy_result] = bytes(set_code).ljust(32, b"\x00")[:32]
    storage[slot_self_balance_result] = balance

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address: Account(storage={}),
            auth_signer: Account(nonce=1, code=b"", storage=storage, balance=balance),
        },
    )


@pytest.mark.parametrize(
    "create_op",
    [
        Op.CREATE,
        Op.CREATE2,
    ],
)
def test_set_code_to_account_deployed_in_same_tx(
    state_test: StateTestFiller,
    pre: Alloc,
    create_op: Op,
):
    """
    Test setting the code of an account to an address that is deployed in the same transaction,
    and test calling the set-code address and the deployed contract.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    success_slot = 1

    deployed_code = Op.SSTORE(success_slot, 1) + Op.STOP
    initcode = Initcode(deploy_code=deployed_code)

    deployed_contract_address_slot = 1
    signer_call_return_code_slot = 2
    deployed_contract_call_return_code_slot = 3

    contract_creator_code = (
        Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
        + Op.SSTORE(deployed_contract_address_slot, create_op(offset=0, size=Op.CALLDATASIZE))
        + Op.SSTORE(signer_call_return_code_slot, Op.CALL(address=auth_signer))
        + Op.SSTORE(
            deployed_contract_call_return_code_slot,
            Op.CALL(address=Op.SLOAD(deployed_contract_address_slot)),
        )
        + Op.STOP()
    )
    contract_creator_address = pre.deploy_contract(contract_creator_code)

    if create_op == Op.CREATE:
        deployed_contract_address = compute_create_address(
            address=contract_creator_address,
            nonce=1,
        )
    else:
        deployed_contract_address = compute_create2_address(
            address=contract_creator_address,
            salt=0,
            initcode=initcode,
        )

    tx = Transaction(
        gas_limit=10_000_000,
        to=contract_creator_address,
        value=0,
        data=initcode,
        authorization_list=[
            AuthorizationTuple(
                address=deployed_contract_address,
                nonce=0,
                signer=auth_signer,
            ),
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            deployed_contract_address: Account(
                storage={success_slot: 1},
            ),
            auth_signer: Account(
                nonce=1,
                code=b"",
                storage={},
            ),
            contract_creator_address: Account(
                storage={
                    deployed_contract_address_slot: deployed_contract_address,
                    signer_call_return_code_slot: 1,
                    deployed_contract_call_return_code_slot: 1,
                }
            ),
        },
    )


def test_set_code_multiple_valid_authorization_tuples_same_signer(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test setting the code of an account with multiple authorization tuples from the same signer.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    tuple_count = 10

    success_slot = 0

    addresses = [pre.deploy_contract(Op.SSTORE(i, 1) + Op.STOP) for i in range(tuple_count)]

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=address,
                nonce=0,
                signer=auth_signer,
            )
            for address in addresses
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(
                nonce=1,
                code=b"",
                storage={
                    success_slot: 1,
                },
            ),
        },
    )


def test_set_code_multiple_valid_authorization_tuples_same_signer_increasing_nonce(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test setting the code of an account with multiple authorization tuples from the same signer
    and each authorization tuple has an increasing nonce, therefore the last tuple is executed.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    tuple_count = 10

    success_slot = tuple_count - 1

    addresses = [pre.deploy_contract(Op.SSTORE(i, 1) + Op.STOP) for i in range(tuple_count)]

    tx = Transaction(
        gas_limit=10_000_000,  # TODO: Reduce gas limit of all tests
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=address,
                nonce=i,
                signer=auth_signer,
            )
            for i, address in enumerate(addresses)
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(
                nonce=10,
                code=b"",
                storage={
                    success_slot: 1,
                },
            ),
        },
    )


def test_set_code_multiple_valid_authorization_tuples_same_signer_increasing_nonce_self_sponsored(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test setting the code of an account with multiple authorization tuples from the same signer
    and each authorization tuple has an increasing nonce, therefore the last tuple is executed,
    and the transaction is self-sponsored.
    """
    auth_signer = pre.fund_eoa()

    tuple_count = 10

    success_slot = tuple_count - 1

    addresses = [pre.deploy_contract(Op.SSTORE(i, 1) + Op.STOP) for i in range(tuple_count)]

    tx = Transaction(
        gas_limit=10_000_000,  # TODO: Reduce gas limit of all tests
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=address,
                nonce=i + 1,
                signer=auth_signer,
            )
            for i, address in enumerate(addresses)
        ],
        sender=auth_signer,
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(
                nonce=11,
                code=b"",
                storage={
                    success_slot: 1,
                },
            ),
        },
    )


def test_set_code_multiple_valid_authorization_tuples_first_invalid_same_signer(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test setting the code of an account with multiple authorization tuples from the same signer
    but the first tuple is invalid.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    success_slot = 1

    tuple_count = 10

    addresses = [pre.deploy_contract(Op.SSTORE(i, 1) + Op.STOP) for i in range(tuple_count)]

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=address,
                nonce=1 if i == 0 else 0,
                signer=auth_signer,
            )
            for i, address in enumerate(addresses)
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(
                nonce=1,
                code=b"",
                storage={
                    success_slot: 1,
                },
            ),
        },
    )


def test_set_code_all_invalid_authorization_tuples(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test setting the code of an account with multiple authorization tuples from the same signer
    but the first tuple is invalid.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    tuple_count = 10

    addresses = [pre.deploy_contract(Op.SSTORE(i, 1) + Op.STOP) for i in range(tuple_count)]

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=address,
                nonce=1,
                signer=auth_signer,
            )
            for _, address in enumerate(addresses)
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(
                nonce=0,
                code=b"",
                storage={},
            ),
        },
    )


@pytest.mark.parametrize(
    "invalidity_reason",
    [
        InvalidityReason.NONCE,
        pytest.param(
            InvalidityReason.MULTIPLE_NONCE, marks=pytest.mark.xfail(reason="test issue")
        ),
        pytest.param(InvalidityReason.CHAIN_ID, marks=pytest.mark.xfail(reason="evm issue")),
    ],
)
def test_set_code_invalid_authorization_tuple(
    state_test: StateTestFiller,
    pre: Alloc,
    invalidity_reason: InvalidityReason,
):
    """
    Test attempting to set the code of an account with invalid authorization tuple.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    success_slot = 1

    set_code = Op.SSTORE(success_slot, 1) + Op.STOP
    set_code_to_address = pre.deploy_contract(set_code)

    tx = Transaction(
        gas_limit=10_000_000,
        to=auth_signer,
        value=0,
        authorization_list=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=1
                if invalidity_reason == InvalidityReason.NONCE
                else [0, 1]
                if invalidity_reason == InvalidityReason.MULTIPLE_NONCE
                else 0,
                chain_id=2 if invalidity_reason == InvalidityReason.CHAIN_ID else 0,
                signer=auth_signer,
            )
        ],
        sender=pre.fund_eoa(),
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(
                nonce=1,
                code=b"",
                storage={
                    success_slot: 0,
                },
            ),
        },
    )
