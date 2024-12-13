"""
A state test for [EIP-7702 SetCodeTX](https://eips.ethereum.org/EIPS/eip-7702).
"""

from enum import Enum

import pytest

from ethereum_test_forks import Fork, GasCosts
from ethereum_test_tools import (
    AccessList,
    Account,
    Address,
    Alloc,
    AuthorizationTuple,
    Block,
    BlockchainTestFiller,
    Conditional,
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
    IN_NORMAL_TX_ONLY = 2
    IN_POINTER_TX_ONLY = 3
    IN_BOTH_TX = 4


class PointerDefinition(Enum):
    """Define pointer in transactions"""

    SEPARATE = 1
    IN_NORMAL_TX_ONLY = 2
    IN_POINTER_TX_ONLY = 3
    IN_BOTH_TX = 4


class AccessListTo(Enum):
    """Define access list to"""

    POINTER_ADDRESS = 1
    CONTRACT_ADDRESS = 2


@pytest.mark.parametrize(
    "access_list_rule",
    [
        AccessListCall.NONE,
        AccessListCall.IN_BOTH_TX,
        AccessListCall.IN_NORMAL_TX_ONLY,
        AccessListCall.IN_POINTER_TX_ONLY,
    ],
)
@pytest.mark.parametrize(
    "pointer_definition",
    [
        PointerDefinition.SEPARATE,
        PointerDefinition.IN_BOTH_TX,
        PointerDefinition.IN_NORMAL_TX_ONLY,
        PointerDefinition.IN_POINTER_TX_ONLY,
    ],
)
@pytest.mark.parametrize(
    "access_list_to",
    [AccessListTo.POINTER_ADDRESS, AccessListTo.CONTRACT_ADDRESS],
)
@pytest.mark.valid_from("Prague")
def test_gas_diff_pointer_vs_direct_call(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    access_list_rule: AccessListCall,
    pointer_definition: PointerDefinition,
    access_list_to: AccessListTo,
):
    """
    Check the gas difference when calling the contract directly vs as a pointer
    Combine with AccessList and AuthTuple gas reductions scenarios
    """
    env = Environment()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()
    call_worked = 1
    gas_costs: GasCosts = fork.gas_costs()

    opcodes_price = 42
    G_CALL_OPCODE: int = 100
    direct_call_gas: int = (
        # 20_000 + 2_600 + 2_100 + 100 + 42 = 24842
        gas_costs.G_STORAGE_SET
        + (
            # access account price
            # If storage and account is declared in access list then discount
            gas_costs.G_WARM_ACCOUNT_ACCESS + gas_costs.G_WARM_SLOAD
            if access_list_rule in [AccessListCall.IN_NORMAL_TX_ONLY, AccessListCall.IN_BOTH_TX]
            else gas_costs.G_COLD_ACCOUNT_ACCESS + gas_costs.G_COLD_SLOAD
        )
        + G_CALL_OPCODE
        + opcodes_price
    )

    pointer_call_gas: int = (
        # sstore + addr + addr + sload + call + op
        # no access list, no pointer, all accesses are hot
        # 20_000 + 2_600 * 2 + 2_100 + 100 + 42 = 27_442
        #
        # access list for pointer, pointer is set
        # additional 2_600 charged for access of contract
        # 20_000 + 100 + 2_600 + 100 + 100 + 42 = 22_942
        #
        # no access list, pointer is set
        # pointer access is hot, sload and contract are hot
        # 20_000 + 100 + 2_600 + 2_100 + 100 + 42 = 24_942
        #
        # access list for contract, pointer is set
        # contract call is hot, pointer call is call because pointer is set
        # only sload is hot because access list is for contract
        # 20_000 + 100 + 100 + 2100 + 100  + 42 = 22_442
        gas_costs.G_STORAGE_SET
        # pointer address access
        + (
            gas_costs.G_WARM_ACCOUNT_ACCESS
            if (
                pointer_definition
                in [PointerDefinition.IN_BOTH_TX, PointerDefinition.IN_POINTER_TX_ONLY]
                or access_list_rule
                in [AccessListCall.IN_BOTH_TX, AccessListCall.IN_POINTER_TX_ONLY]
                and access_list_to == AccessListTo.POINTER_ADDRESS
            )
            else gas_costs.G_COLD_ACCOUNT_ACCESS
        )
        # storage access
        + (
            gas_costs.G_WARM_SLOAD
            if (
                access_list_rule in [AccessListCall.IN_BOTH_TX, AccessListCall.IN_POINTER_TX_ONLY]
                and access_list_to == AccessListTo.POINTER_ADDRESS
            )
            else gas_costs.G_COLD_SLOAD
        )
        # contract address access
        + (
            gas_costs.G_WARM_ACCOUNT_ACCESS
            if (
                access_list_rule in [AccessListCall.IN_BOTH_TX, AccessListCall.IN_POINTER_TX_ONLY]
                and access_list_to == AccessListTo.CONTRACT_ADDRESS
            )
            else gas_costs.G_COLD_ACCOUNT_ACCESS
        )
        + G_CALL_OPCODE
        + opcodes_price
    )

    contract = pre.deploy_contract(code=Op.SSTORE(call_worked, Op.ADD(Op.SLOAD(call_worked), 1)))

    # Op.CALLDATASIZE() does not work with kwargs
    storage_normal: Storage = Storage()
    contract_test_normal = pre.deploy_contract(
        code=Op.MSTORE(1000, Op.GAS())
        + Op.CALL(gas=100_000, address=contract)
        + Op.SSTORE(
            storage_normal.store_next(direct_call_gas, "normal_call_price"),
            Op.SUB(Op.MLOAD(1000), Op.GAS()),
        )
    )

    storage_pointer: Storage = Storage()
    contract_test_pointer = pre.deploy_contract(
        code=Op.MSTORE(1000, Op.GAS())
        + Op.CALL(gas=100_000, address=pointer_a)
        + Op.SSTORE(
            storage_pointer.store_next(pointer_call_gas, "pointer_call_price"),
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
            or pointer_definition == PointerDefinition.IN_NORMAL_TX_ONLY
            else None
        ),
        access_list=(
            [
                AccessList(
                    address=contract,
                    storage_keys=[call_worked],
                )
            ]
            if access_list_rule == AccessListCall.IN_BOTH_TX
            or access_list_rule == AccessListCall.IN_NORMAL_TX_ONLY
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
            or pointer_definition == PointerDefinition.IN_POINTER_TX_ONLY
            else None
        ),
        access_list=(
            [
                AccessList(
                    address=(
                        pointer_a if access_list_to == AccessListTo.POINTER_ADDRESS else contract
                    ),
                    storage_keys=[call_worked],
                )
            ]
            if access_list_rule == AccessListCall.IN_BOTH_TX
            or access_list_rule == AccessListCall.IN_POINTER_TX_ONLY
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
def test_pointer_call_followed_by_direct_call(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
):
    """
    If we first call by pointer then direct call, will the call/sload be hot
    The direct call will warm because pointer access marks it warm
    But the sload is still cold because storage marked hot from pointer's account in a pointer call
    """
    env = Environment()

    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()
    gas_costs: GasCosts = fork.gas_costs()
    call_worked = 1
    G_CALL_OPCODE: int = 100
    opcodes_price: int = 42
    pointer_call_gas = (
        gas_costs.G_STORAGE_SET
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # pointer is warm
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # contract is cold
        + gas_costs.G_COLD_SLOAD  # storage access under pointer call is cold
        + G_CALL_OPCODE
        + opcodes_price
    )
    direct_call_gas = (
        gas_costs.G_STORAGE_SET
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # since previous pointer call, contract is now warm
        + gas_costs.G_COLD_SLOAD  # but storage is cold, because it's contract's direct
        + G_CALL_OPCODE
        + opcodes_price
        - 2  # because direct call is cheaper?
    )

    contract = pre.deploy_contract(code=Op.SSTORE(call_worked, Op.ADD(Op.SLOAD(call_worked), 1)))

    storage_test_gas: Storage = Storage()
    contract_test_gas = pre.deploy_contract(
        code=Op.MSTORE(1000, Op.GAS())
        + Op.CALL(gas=100_000, address=pointer_a)
        + Op.SSTORE(
            storage_test_gas.store_next(pointer_call_gas, "pointer_call_price"),
            Op.SUB(Op.MLOAD(1000), Op.GAS()),
        )
        + Op.MSTORE(2000, Op.GAS())
        + Op.CALL(gas=100_000, address=contract)
        + Op.SSTORE(
            storage_test_gas.store_next(direct_call_gas, "direct_call_price"),
            Op.SUB(Op.MLOAD(2000), Op.GAS()),
        )
    )

    tx = Transaction(
        to=contract_test_gas,
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
        ),
    )

    post = {
        contract: Account(storage={call_worked: 1}),
        pointer_a: Account(storage={call_worked: 1}),
        contract_test_gas: Account(storage=storage_test_gas),
    }
    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
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


@pytest.mark.valid_from("Prague")
def test_pointer_to_static_reentry(state_test: StateTestFiller, pre: Alloc):
    """
    Tx call -> pointer A -> static -> code -> pointer A -> static violation
    Verify that static context is active when called under pointer
    """
    env = Environment()
    storage: Storage = Storage()
    sender = pre.fund_eoa()
    pointer_a = pre.fund_eoa()

    contract_b = pre.deploy_contract(
        code=Op.MSTORE(0, Op.ADD(1, Op.CALLDATALOAD(0)))
        + Conditional(
            condition=Op.EQ(Op.MLOAD(0), 2), if_true=Op.SSTORE(5, 5), if_false=Op.JUMPDEST()
        )
        + Op.CALL(gas=100_000, address=pointer_a, args_offset=0, args_size=Op.CALLDATASIZE())
    )
    contract_a = pre.deploy_contract(
        code=Op.MSTORE(0, Op.CALLDATALOAD(0))
        + Conditional(
            condition=Op.EQ(Op.MLOAD(0), 0),
            if_true=Op.SSTORE(
                storage.store_next(1, "static_call"),
                Op.STATICCALL(1_000_000, contract_b, 0, Op.CALLDATASIZE(), 1000, 32),
            )
            + Op.SSTORE(storage.store_next(1, "call_worked"), 1),
            if_false=Op.CALL(1_000_000, contract_b, 0, 0, Op.CALLDATASIZE(), 1000, 32),
        )
    )

    tx = Transaction(
        to=pointer_a,
        gas_limit=3_000_000,
        data=[0x00] * 32,
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
@pytest.mark.parametrize(
    "call_type",
    [Op.CALL, Op.DELEGATECALL, Op.CALLCODE],
)
def test_contract_storage_to_pointer_with_storage(
    state_test: StateTestFiller, pre: Alloc, call_type: Op
):
    """
    Tx call -> contract with storage -> pointer A with storage -> storage/tstorage modify
    Check storage/tstorage modifications when interacting with pointers
    """
    env = Environment()

    sender = pre.fund_eoa()

    # Pointer B
    storage_pointer_b: Storage = Storage()
    storage_pointer_b.store_next(
        0 if call_type in [Op.DELEGATECALL, Op.CALLCODE] else 1, "first_slot"
    )
    storage_pointer_b.store_next(0, "second_slot")
    storage_pointer_b.store_next(0, "third_slot")
    pointer_b = pre.fund_eoa()

    # Contract B
    storage_b: Storage = Storage()
    first_slot = storage_b.store_next(10, "first_slot")
    second_slot = storage_b.store_next(20, "second_slot")
    third_slot = storage_b.store_next(30, "third_slot")
    fourth_slot = storage_b.store_next(0, "fourth_slot")
    contract_b = pre.deploy_contract(
        code=Op.MSTORE(0, Op.CALLDATALOAD(0))
        + Conditional(
            condition=Op.EQ(Op.MLOAD(0), 1),
            if_true=Op.SSTORE(fourth_slot, Op.TLOAD(third_slot)),
            if_false=Op.SSTORE(first_slot, Op.ADD(Op.SLOAD(first_slot), 1))
            + Op.TSTORE(third_slot, Op.ADD(Op.TLOAD(third_slot), 1)),
        ),
        storage={
            # Original contract storage is untouched
            first_slot: 10,
            second_slot: 20,
            third_slot: 30,
        },
    )

    # Contract A
    storage_a: Storage = Storage()
    contract_a = pre.deploy_contract(
        code=Op.TSTORE(third_slot, 1)
        + call_type(address=pointer_b, gas=500_000)
        + Op.SSTORE(third_slot, Op.TLOAD(third_slot))
        # Verify tstorage in contract after interacting with pointer, it must be 0
        + Op.MSTORE(0, 1) + Op.CALL(address=contract_b, gas=500_000, args_offset=0, args_size=32),
        storage={
            storage_a.store_next(
                # caller storage is modified when calling pointer with delegate or callcode
                6 if call_type in [Op.DELEGATECALL, Op.CALLCODE] else 5,
                "first_slot",
            ): 5,
            storage_a.store_next(2, "second_slot"): 2,
            storage_a.store_next(
                # TSTORE is modified when calling pointer with delegate or callcode
                2 if call_type in [Op.DELEGATECALL, Op.CALLCODE] else 1,
                "third_slot",
            ): 3,
        },
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
                signer=pointer_b,
            )
        ],
    )

    post = {
        contract_a: Account(storage=storage_a),
        contract_b: Account(storage=storage_b),
        pointer_b: Account(storage=storage_pointer_b),
    }
    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )
