"""
A state test for [EIP-7702 SetCodeTX](https://eips.ethereum.org/EIPS/eip-7702).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    AuthorizationTuple,
    Block,
    BlockchainTestFiller,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .spec import Spec, ref_spec_7702

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version


@pytest.mark.valid_from("Prague")
def test_7702_pointer_contract_pointer_loop(state_test: StateTestFiller, pre: Alloc):
    """
    tx -> call -> pointer A -> contract A -> pointer B -> contract loop C

    Call pointer that goes more level of depth to call a contract loop
    Loop is created only if pointers are set with auth tuples
    """
    env = Environment()

    storage: Storage = Storage()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()
    pointer_b = pre.fund_eoa()
    contract_a = pre.deploy_contract(
        code=Op.SSTORE(storage.store_next(1, "contract_a_worked"), 0x1)
        + Op.CALL(1_000_000, pointer_b, 0, 0, 0, 0, 0)
        + Op.STOP,
    )

    storage_loop = storage.store_next(0, "contract_loop_worked")
    contract_loop = pre.deploy_contract(
        code=Op.SSTORE(storage_loop, Op.ADD(1, Op.SLOAD(0)))
        + Op.CALL(1_000_000, pointer_a, 0, 0, 0, 0, 0)
        + Op.STOP,
    )
    tx = Transaction(
        to=pointer_a,
        gas_limit=100_000_000,
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

    # TODO: Modify post-state allocations here.
    post = {pointer_a: Account(storage=storage)}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
def test_7702_pointer_to_pointer(state_test: StateTestFiller, pre: Alloc):
    """
    tx -> call -> pointer A -> pointer B

    Direct call from pointer to pointer is OOG
    """
    env = Environment()

    storage: Storage = Storage()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()
    pointer_b = pre.fund_eoa()

    contract_a = pre.deploy_contract(
        code=Op.SSTORE(storage.store_next(0, "contract_a_worked"), 0x1)
        + Op.CALL(1_000_000, pointer_b, 0, 0, 0, 0, 0)
        + Op.STOP,
    )

    tx = Transaction(
        to=pointer_a,
        gas_limit=100_000_000,
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
@pytest.mark.parametrize("create_opcode", [Op.CREATE, Op.CREATE2])
def test_7702_create_pointer_style_contract(
    state_test: StateTestFiller, pre: Alloc, create_opcode: Op
):
    """
    tx -> create -> pointer bytecode

    Attempt to deploy contract with magic bytes result in no contract being created
    """
    env = Environment()

    storage: Storage = Storage()

    sender = pre.fund_eoa()

    # An attempt to deploy code starting with ef01 result in no
    # contract being created as it is prohibited
    create_init = Op.MSTORE(0, "0xef01" + sender.hex()[2:]) + Op.RETURN(10, 22)
    contract_a = pre.deploy_contract(
        balance=100,
        code=Op.MSTORE(0, Op.CALLDATALOAD(0))
        + Op.SSTORE(
            storage.store_next(0, "contract_a_create_result"),
            create_opcode(value=1, offset=0, size=Op.CALLDATASIZE(), salt=0),
        )
        + Op.STOP,
    )

    tx = Transaction(
        to=contract_a,
        gas_limit=100_000_000,
        data=create_init,
        value=0,
        sender=sender,
    )

    create_address = compute_create_address(
        address=contract_a, nonce=1, initcode=create_init, salt=0, opcode=create_opcode
    )
    post = {contract_a: Account(balance=100, storage=storage), create_address: Account.NONEXISTENT}
    state_test(env=env, pre=pre, post=post, tx=tx)


def test_7702_create_pointer_style_contract_tx_deploy(state_test: StateTestFiller, pre: Alloc):
    """
    tx -> deploy pointer bytecode

    Attempt to deploy contract with magic bytes result in no contract being created
    """
    env = Environment()
    sender = pre.fund_eoa()

    create_init = Op.MSTORE(0, "0xef01" + sender.hex()[2:]) + Op.RETURN(10, 22)

    tx = Transaction(
        to=b"",
        gas_limit=100_000_000,
        data=create_init,
        value=0,
        sender=sender,
    )

    create_address = compute_create_address(
        address=sender, nonce=0, initcode=create_init, salt=0, opcode=Op.CREATE
    )
    post = {sender: Account(nonce=1), create_address: Account.NONEXISTENT}
    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
def test_7702_pointer_normal(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    tx -> call -> pointer A -> contract
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
        gas_limit=100_000_000,
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
        gas_limit=100_000_000,
        data=b"",
        value=0,
        sender=sender,
    )

    # Event from another block
    tx_3 = Transaction(
        to=pointer_a,
        gas_limit=100_000_000,
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
def test_7702_pointer_measurements(blockchain_test: BlockchainTestFiller, pre: Alloc):
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
            storage_pointer_code.store_next(pointer.hex(), "address"),
            Op.ADDRESS(),
        )
        + Op.SSTORE(
            storage_pointer_code.store_next(3, "callvalue"),
            Op.CALLVALUE(),
        )
        + Op.CALL(1000, 0, 3, 0, 0, 0, 0)
        + Op.SSTORE(
            storage_pointer_code.store_next(100, "selfbalance"),
            Op.SELFBALANCE(),
        )
        + Op.SSTORE(
            storage_pointer_code.store_next(sender.hex(), "origin"),
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
        gas_limit=100_000_000,
        data=b"",
        value=0,
        sender=sender,
    )

    tx_pointer = Transaction(
        to=contract_measurements_pointer,
        gas_limit=100_000_000,
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
        gas_limit=100_000_000,
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
