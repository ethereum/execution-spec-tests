"""
A state test for [EIP-7702 SetCodeTX](https://eips.ethereum.org/EIPS/eip-7702).
"""

from enum import Enum

import pytest

from ethereum_test_tools import (
    AccessList,
    Account,
    Address,
    Alloc,
    AuthorizationTuple,
    Block,
    BlockchainTestFiller,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
)
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .spec import ref_spec_7702

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version


@pytest.mark.valid_from("Prague")
def test_pointer_contract_pointer_loop(state_test: StateTestFiller, pre: Alloc):
    """
    Tx -> call -> pointer A -> contract A -> pointer B -> contract loop C

    Call pointer that goes more level of depth to call a contract loop
    Loop is created only if pointers are set with auth tuples
    """
    env = Environment()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()
    pointer_b = pre.fund_eoa()

    storage: Storage = Storage()
    contract_a = pre.deploy_contract(
        code=Op.SSTORE(storage.store_next(1, "contract_a_worked"), 0x1)
        + Op.CALL(gas=1_000_000, address=pointer_b)
        + Op.STOP,
    )

    storage_loop: Storage = Storage()
    contract_worked = storage_loop.store_next(112, "contract_loop_worked")
    contract_loop = pre.deploy_contract(
        code=Op.SSTORE(contract_worked, Op.ADD(1, Op.SLOAD(0)))
        + Op.CALL(gas=1_000_000, address=pointer_a)
        + Op.STOP,
    )
    tx = Transaction(
        to=pointer_a,
        gas_limit=1_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=contract_a,
                nonce=0,
                signer=pointer_a,
            ),
            AuthorizationTuple(
                address=contract_loop,
                nonce=0,
                signer=pointer_b,
            ),
        ],
    )

    post = {
        pointer_a: Account(storage=storage),
        pointer_b: Account(storage=storage_loop),
    }
    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
def test_pointer_to_pointer(state_test: StateTestFiller, pre: Alloc):
    """
    Tx -> call -> pointer A -> pointer B

    Direct call from pointer to pointer is OOG
    """
    env = Environment()

    storage: Storage = Storage()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()
    pointer_b = pre.fund_eoa()

    contract_a = pre.deploy_contract(
        code=Op.SSTORE(storage.store_next(0, "contract_a_worked"), 0x1)
        + Op.CALL(gas=1_000_000, address=pointer_b)
        + Op.STOP,
    )

    tx = Transaction(
        to=pointer_a,
        gas_limit=1_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=pointer_b,
                nonce=0,
                signer=pointer_a,
            ),
            AuthorizationTuple(
                address=contract_a,
                nonce=0,
                signer=pointer_b,
            ),
        ],
    )
    post = {pointer_a: Account(storage=storage)}
    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
def test_pointer_normal(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    Tx -> call -> pointer A -> contract
    Other normal tx can interact with previously assigned pointers
    """
    env = Environment()

    storage: Storage = Storage()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()

    slot_worked = storage.store_next(3, "contract_a_worked")
    contract_a = pre.deploy_contract(
        code=Op.SSTORE(slot_worked, Op.ADD(1, Op.SLOAD(slot_worked))) + Op.STOP,
    )

    tx = Transaction(
        to=pointer_a,
        gas_limit=1_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=contract_a,
                nonce=0,
                signer=pointer_a,
            )
        ],
    )

    # Other normal tx can interact with previously assigned pointers
    tx_2 = Transaction(
        to=pointer_a,
        gas_limit=1_000_000,
        data=b"",
        value=0,
        sender=sender,
    )

    # Event from another block
    tx_3 = Transaction(
        to=pointer_a,
        gas_limit=1_000_000,
        data=b"",
        value=0,
        sender=sender,
    )

    post = {pointer_a: Account(storage=storage)}
    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=[Block(txs=[tx, tx_2]), Block(txs=[tx_3])],
    )


@pytest.mark.valid_from("Prague")
def test_pointer_measurements(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    Check extcode* operations on pointer before and after pointer is set
    Check context opcode results when called under pointer call
    Opcodes have context of an original pointer account (balance, storage)
    """
    env = Environment()

    sender = pre.fund_eoa()
    pointer = pre.fund_eoa(amount=100)

    storage_normal: Storage = Storage()
    storage_pointer: Storage = Storage()
    storage_pointer_code: Storage = Storage()  # this storage will be applied to pointer address
    pointer_code = pre.deploy_contract(
        balance=200,
        code=Op.SSTORE(
            storage_pointer_code.store_next(pointer, "address"),
            Op.ADDRESS(),
        )
        + Op.SSTORE(
            storage_pointer_code.store_next(3, "callvalue"),
            Op.CALLVALUE(),
        )
        + Op.CALL(gas=1000, address=0, value=3)
        + Op.SSTORE(
            storage_pointer_code.store_next(100, "selfbalance"),
            Op.SELFBALANCE(),
        )
        + Op.SSTORE(
            storage_pointer_code.store_next(sender, "origin"),
            Op.ORIGIN(),
        )
        + Op.SSTORE(
            storage_pointer_code.store_next(
                "0x1122334400000000000000000000000000000000000000000000000000000000",
                "calldataload",
            ),
            Op.CALLDATALOAD(0),
        )
        + Op.SSTORE(
            storage_pointer_code.store_next(
                4,
                "calldatasize",
            ),
            Op.CALLDATASIZE(),
        )
        + Op.CALLDATACOPY(0, 0, 32)
        + Op.SSTORE(
            storage_pointer_code.store_next(
                "0x1122334400000000000000000000000000000000000000000000000000000000",
                "calldatacopy",
            ),
            Op.MLOAD(0),
        )
        + Op.MSTORE(0, 0)
        + Op.SSTORE(
            storage_pointer_code.store_next(83, "codesize"),
            Op.CODESIZE(),
        )
        + Op.CODECOPY(0, 0, 32)
        + Op.SSTORE(
            storage_pointer_code.store_next(
                "0x30600055346001556000600060006000600360006103e8f14760025532600355", "codecopy"
            ),
            Op.MLOAD(0),
        )
        + Op.SSTORE(
            storage_pointer_code.store_next(0, "sload"),
            Op.SLOAD(15),
        ),
        storage={15: 25},
    )

    contract_measurements = pre.deploy_contract(
        code=Op.EXTCODECOPY(pointer, 0, 0, 32)
        + Op.SSTORE(
            storage_normal.store_next(
                0xC5D2460186F7233C927E7DB2DCC703C0E500B653CA82273B7BFAD8045D85A470, "extcodehash"
            ),
            Op.EXTCODEHASH(pointer),
        )
        + Op.SSTORE(storage_normal.store_next(0, "extcodesize"), Op.EXTCODESIZE(pointer))
        + Op.SSTORE(storage_normal.store_next(0, "extcodecopy"), Op.MLOAD(0))
        + Op.SSTORE(storage_normal.store_next(100, "balance"), Op.BALANCE(pointer))
        + Op.STOP,
    )

    contract_measurements_pointer = pre.deploy_contract(
        code=Op.EXTCODECOPY(pointer, 0, 0, 32)
        + Op.SSTORE(
            storage_pointer.store_next(
                0x92526A3983053385B72FE45972C2BD833B82F66DB3B46AA71707AB5739EB57BA, "extcodehash"
            ),
            Op.EXTCODEHASH(pointer),
        )
        + Op.SSTORE(storage_pointer.store_next(83, "extcodesize"), Op.EXTCODESIZE(pointer))
        + Op.SSTORE(
            storage_pointer.store_next(
                0x30600055346001556000600060006000600360006103E8F14760025532600355, "extcodecopy"
            ),
            Op.MLOAD(0),
        )
        + Op.SSTORE(storage_pointer.store_next(100, "balance"), Op.BALANCE(pointer))
        + Op.STOP,
    )

    tx = Transaction(
        to=contract_measurements,
        gas_limit=1_000_000,
        data=b"",
        value=0,
        sender=sender,
    )

    tx_pointer = Transaction(
        to=contract_measurements_pointer,
        gas_limit=1_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=pointer_code,
                nonce=0,
                signer=pointer,
            )
        ],
    )

    tx_pointer_call = Transaction(
        to=pointer,
        gas_limit=1_000_000,
        data=bytes.fromhex("11223344"),
        value=3,
        sender=sender,
    )

    post = {
        contract_measurements: Account(storage=storage_normal),
        contract_measurements_pointer: Account(storage=storage_pointer),
        pointer: Account(storage=storage_pointer_code),
    }
    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=[Block(txs=[tx]), Block(txs=[tx_pointer, tx_pointer_call])],
    )


@pytest.mark.with_all_precompiles
@pytest.mark.valid_from("Prague")
def test_call_to_precompile_in_pointer_context(
    state_test: StateTestFiller, pre: Alloc, precompile: int
):
    """
    Tx -> call -> pointer A -> precompile contract
    Make sure that gas consumed when calling precompiles in normal call are the same
    As from inside the pointer context call
    """
    env = Environment()

    storage: Storage = Storage()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()

    # Op.CALLDATASIZE() does not work with kwargs
    contract_test = pre.deploy_contract(
        code=Op.MSTORE(1000, Op.GAS())
        + Op.CALL(100_000, precompile, 0, 0, Op.CALLDATASIZE(), 0, 0)
        + Op.MSTORE(0, Op.SUB(Op.MLOAD(1000), Op.GAS()))
        + Op.RETURN(0, 32)
    )
    normal_call_gas = 2000
    pointer_call_gas = 3000
    contract_a = pre.deploy_contract(
        code=Op.CALL(1_000_000, contract_test, 0, 0, Op.CALLDATASIZE(), 1000, 32)
        + Op.MSTORE(normal_call_gas, Op.MLOAD(1000))
        + Op.CALL(1_000_000, pointer_a, 0, 0, Op.CALLDATASIZE(), 1000, 32)
        + Op.MSTORE(pointer_call_gas, Op.MLOAD(1000))
        + Op.SSTORE(
            storage.store_next(0, "call_gas_diff"),
            Op.SUB(Op.MLOAD(normal_call_gas), Op.MLOAD(pointer_call_gas)),
        )
    )

    tx = Transaction(
        to=contract_a,
        gas_limit=3_000_000,
        data=[0x11] * 256,
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=contract_test,
                nonce=0,
                signer=pointer_a,
            )
        ],
    )

    post = {contract_a: Account(storage=storage)}
    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


@pytest.mark.with_all_precompiles
@pytest.mark.valid_from("Prague")
def test_pointer_to_precompile(state_test: StateTestFiller, pre: Alloc, precompile: int):
    """
    Tx -> call -> pointer A -> precompile contract

    In case a delegation designator points to a precompile address, retrieved code is considered
    empty and CALL, CALLCODE, STATICCALL, DELEGATECALL instructions targeting this account will
    execute empty code, i.e. succeed with no execution given enough gas.

    So call to a pointer that points to a precompile is like call to an empty account
    """
    env = Environment()

    storage: Storage = Storage()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()

    # Op.CALLDATASIZE() does not work with kwargs
    contract_test_normal = pre.deploy_contract(
        code=Op.MSTORE(1000, Op.GAS())
        + Op.CALL(100_000, precompile, 0, 0, Op.CALLDATASIZE(), 0, 0)
        + Op.MSTORE(0, Op.SUB(Op.MLOAD(1000), Op.GAS()))
        + Op.RETURN(0, 32)
    )

    contract_test_pointer = pre.deploy_contract(
        code=Op.MSTORE(1000, Op.GAS())
        + Op.CALL(100_000, pointer_a, 0, 0, Op.CALLDATASIZE(), 0, 0)
        + Op.MSTORE(0, Op.SUB(Op.MLOAD(1000), Op.GAS()))
        + Op.RETURN(0, 32)
    )

    # Precompile call gas diff map. if it matches we know for sure
    # that pointer call didn't work as a call to precompile contract
    # due to unique call gas difference
    # Existing test check only return call value, but we can either see the gas consumed on
    # precompile or provide a valid data and verify that the precompile really didn't work
    precompile_gas_diff: dict[int, int] = {
        1: 2900,
        2: 56,
        3: 1460,
        4: -61,
        5: 99900,
        6: 50,
        7: 5900,
        8: 99900,
        9: 99900,
        10: 99900,
        11: 400,
        12: 99900,
        13: 99900,
        14: 99900,
        15: 99900,
        16: 99900,
        17: 99900,
        18: 99900,
        19: 99900,
    }

    normal_call_gas = 2000
    pointer_call_gas = 3000
    contract_a = pre.deploy_contract(
        code=Op.CALL(1_000_000, contract_test_normal, 0, 0, Op.CALLDATASIZE(), 1000, 32)
        + Op.MSTORE(normal_call_gas, Op.MLOAD(1000))
        + Op.CALL(1_000_000, contract_test_pointer, 0, 0, Op.CALLDATASIZE(), 1000, 32)
        + Op.MSTORE(pointer_call_gas, Op.MLOAD(1000))
        + Op.SSTORE(
            storage.store_next(
                precompile_gas_diff.get(int(Address(precompile).hex(), 16), 0), "call_gas_diff"
            ),
            Op.SUB(Op.MLOAD(normal_call_gas), Op.MLOAD(pointer_call_gas)),
        )
    )

    tx = Transaction(
        to=contract_a,
        gas_limit=3_000_000,
        data=[0x11] * 256,
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=precompile,
                nonce=0,
                signer=pointer_a,
            )
        ],
    )

    post = {contract_a: Account(storage=storage)}
    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


class AccessListCall(Enum):
    """Add addresses to access list"""

    NONE = 1
    NORMAL_ONLY = 2
    POINTER_ONLY = 3
    BOTH = 4


class PointerDefinition(Enum):
    """Define pointer in transactions"""

    SEPARATE = 1
    IN_TX1_ONLY = 2
    IN_TX2_ONLY = 3
    IN_BOTH_TX = 4


@pytest.mark.parametrize(
    "access_list_rule",
    [
        AccessListCall.NONE,
        AccessListCall.BOTH,
        AccessListCall.NORMAL_ONLY,
        AccessListCall.POINTER_ONLY,
    ],
)
@pytest.mark.parametrize(
    "pointer_definition",
    [
        PointerDefinition.SEPARATE,
        PointerDefinition.IN_BOTH_TX,
        PointerDefinition.IN_TX1_ONLY,
        PointerDefinition.IN_TX2_ONLY,
    ],
)
@pytest.mark.valid_from("Prague")
def test_gas_diff_pointer_vs_direct_call(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    access_list_rule: AccessListCall,
    pointer_definition: PointerDefinition,
):
    """
    Check the gas difference when calling the contract directly vs as a pointer
    Combine with AccessList and AuthTuple gas reductions scenarios

    TODO: the test uses direct gas values, which can be replaced with opcode gas price(fork)
    in the future. direct gas values are not good to use in tests, but sometimes we need it
    """
    env = Environment()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()
    call_worked = 1
    contract = pre.deploy_contract(code=Op.SSTORE(call_worked, Op.ADD(Op.SLOAD(call_worked), 1)))

    # Op.CALLDATASIZE() does not work with kwargs
    storage_normal: Storage = Storage()
    contract_test_normal = pre.deploy_contract(
        code=Op.MSTORE(1000, Op.GAS())
        + Op.CALL(100_000, contract, 0, 0, Op.CALLDATASIZE(), 0, 0)
        + Op.SSTORE(
            storage_normal.store_next(
                (
                    20341
                    if access_list_rule == AccessListCall.BOTH
                    or access_list_rule == AccessListCall.NORMAL_ONLY
                    else 24841
                ),
                "normal_call_price",
            ),
            Op.SUB(Op.MLOAD(1000), Op.GAS()),
        )
    )

    storage_pointer: Storage = Storage()
    contract_test_pointer = pre.deploy_contract(
        code=Op.MSTORE(1000, Op.GAS())
        + Op.CALL(100_000, pointer_a, 0, 0, Op.CALLDATASIZE(), 0, 0)
        + Op.SSTORE(
            storage_pointer.store_next(
                (
                    22941
                    if access_list_rule == AccessListCall.BOTH
                    or access_list_rule == AccessListCall.POINTER_ONLY
                    else (
                        24941  # setting pointer once again in each transaction reduces the price
                        if pointer_definition == PointerDefinition.IN_TX2_ONLY
                        or pointer_definition == PointerDefinition.IN_BOTH_TX
                        else 27441
                    )
                ),
                "pointer_call_price",
            ),
            Op.SUB(Op.MLOAD(1000), Op.GAS()),
        )
    )

    tx_0 = Transaction(
        to=1,
        gas_limit=3_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=(
            [
                AuthorizationTuple(
                    address=contract,
                    nonce=0,
                    signer=pointer_a,
                )
            ]
            if pointer_definition == PointerDefinition.SEPARATE
            else None
        ),
    )

    tx = Transaction(
        to=contract_test_normal,
        gas_limit=3_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=(
            [
                AuthorizationTuple(
                    address=contract,
                    nonce=0,
                    signer=pointer_a,
                )
            ]
            if pointer_definition == PointerDefinition.IN_BOTH_TX
            or pointer_definition == PointerDefinition.IN_TX1_ONLY
            else None
        ),
        access_list=(
            [
                AccessList(
                    address=contract,
                    storage_keys=[call_worked],
                )
            ]
            if access_list_rule == AccessListCall.BOTH
            or access_list_rule == AccessListCall.NORMAL_ONLY
            else None
        ),
    )
    tx2 = Transaction(
        to=contract_test_pointer,
        gas_limit=3_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=(
            [
                AuthorizationTuple(
                    address=contract,
                    nonce=0,
                    signer=pointer_a,
                )
            ]
            if pointer_definition == PointerDefinition.IN_BOTH_TX
            or pointer_definition == PointerDefinition.IN_TX2_ONLY
            else None
        ),
        access_list=(
            [
                AccessList(
                    address=pointer_a,
                    storage_keys=[call_worked],
                )
            ]
            if access_list_rule == AccessListCall.BOTH
            or access_list_rule == AccessListCall.POINTER_ONLY
            else None
        ),
    )

    post = {
        contract: Account(storage={call_worked: 1}),
        pointer_a: Account(storage={call_worked: 1}),
        contract_test_normal: Account(storage=storage_normal),
        contract_test_pointer: Account(storage=storage_pointer),
    }
    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=[Block(txs=[tx_0]), Block(txs=[tx]), Block(txs=[tx2])],
    )


@pytest.mark.valid_from("Prague")
def test_pointer_to_static(state_test: StateTestFiller, pre: Alloc):
    """
    Tx -> call -> pointer A -> static -> static violation
    Verify that static context is active when called under pointer
    """
    env = Environment()
    storage: Storage = Storage()
    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()

    contract_b = pre.deploy_contract(code=Op.SSTORE(0, 5))
    contract_a = pre.deploy_contract(
        code=Op.SSTORE(
            storage.store_next(0, "static_call"),
            Op.STATICCALL(1_000_000, contract_b, 0, 32, 1000, 32),
        )
        + Op.SSTORE(storage.store_next(1, "call_worked"), 1)
    )

    tx = Transaction(
        to=pointer_a,
        gas_limit=3_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=contract_a,
                nonce=0,
                signer=pointer_a,
            )
        ],
    )

    post = {pointer_a: Account(storage=storage)}
    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


@pytest.mark.valid_from("Prague")
def test_static_to_pointer(state_test: StateTestFiller, pre: Alloc):
    """
    Tx -> staticcall -> pointer A -> static violation
    Verify that static context is active when make sub call to pointer
    """
    env = Environment()
    storage: Storage = Storage()
    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()

    contract_b = pre.deploy_contract(code=Op.SSTORE(0, 5))
    contract_a = pre.deploy_contract(
        code=Op.SSTORE(
            storage.store_next(0, "static_call"),
            Op.STATICCALL(1_000_000, pointer_a, 0, 32, 1000, 32),
        )
        + Op.SSTORE(storage.store_next(1, "call_worked"), 1)
    )

    tx = Transaction(
        to=contract_a,
        gas_limit=3_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=contract_b,
                nonce=0,
                signer=pointer_a,
            )
        ],
    )

    post = {contract_a: Account(storage=storage)}
    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


@pytest.mark.valid_from("Osaka")
def test_pointer_to_eof(state_test: StateTestFiller, pre: Alloc):
    """
    Tx -> call -> pointer A -> EOF
    Pointer to eof contract works
    """
    env = Environment()
    storage: Storage = Storage()
    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()

    contract_a = pre.deploy_contract(
        code=Container(
            sections=[
                Section.Code(
                    code=Op.SSTORE(storage.store_next(5, "eof_call_result"), 5) + Op.STOP,
                )
            ]
        )
    )

    tx = Transaction(
        to=pointer_a,
        gas_limit=3_000_000,
        data=b"",
        value=0,
        sender=sender,
        authorization_list=[
            AuthorizationTuple(
                address=contract_a,
                nonce=0,
                signer=pointer_a,
            )
        ],
    )

    post = {pointer_a: Account(storage=storage)}
    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )
