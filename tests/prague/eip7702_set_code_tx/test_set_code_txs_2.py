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
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .spec import ref_spec_7702

pytestmark = pytest.mark.valid_from("Prague")

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version


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
