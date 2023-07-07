"""
abstract: Tests [EIP-6780: SELFDESTRUCT only in same transaction](https://eips.ethereum.org/EIPS/eip-6780)

    Tests for [EIP-6780: SELFDESTRUCT only in same transaction](https://eips.ethereum.org/EIPS/eip-6780).

"""  # noqa: E501

from itertools import count
from typing import Dict, List

import pytest
from ethereum.crypto.hash import keccak256

from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    Environment,
    Initcode,
    StateTestFiller,
    Storage,
    TestAddress,
    Transaction,
    compute_create2_address,
    compute_create_address,
    to_address,
    to_hash_bytes,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6780.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

SELFDESTRUCT_EIP_NUMBER = 6780


# TODO:

# - Destroy and re-create multiple times in the same tx
# - Create and destroy multiple contracts in the same tx
# - Create multiple contracts in a tx and destroy only one of them, but attempt to destroy the
#    other one in a subsequent tx
# - Create contract, attempt to destroy it in a subsequent tx in the same block
# - Create a contract and try to destroy using another calltype (e.g. Delegatecall then destroy)
# - Create a contract that creates another contract, then selfdestruct only the parent
#    (or vice versa)
# - Test selfdestructing using all types of create
# - Create a contract using CREATE2, then in a subsequent tx do CREATE2 to the same address, and
#    try to self-destruct
# - Create a contract using CREATE2 to an account that has some balance, and try to self-destruct
#    it in the same tx
# - Check balance after self-destruct using Op.BALANCE
# - Check that the Op.SENDALL recipient does not execute code


@pytest.fixture
def eips(eip_enabled: bool) -> List[int]:
    """Prepares the list of EIPs depending on the test that enables it or not."""
    return [SELFDESTRUCT_EIP_NUMBER] if eip_enabled else []


@pytest.fixture
def env() -> Environment:
    """Default environment for all tests."""
    return Environment(
        coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        gas_limit=10000000000,
    )


@pytest.fixture
def sendall_destination_address() -> int:
    """Account that receives the balance from the self-destructed account."""
    return 0x1234


@pytest.fixture
def selfdestruct_code(
    sendall_destination_address: int,
) -> bytes:
    """Bytecode that self-destructs."""
    return Op.SSTORE(
        0,
        Op.ADD(Op.SLOAD(0), 1),  # Add to the SSTORE'd value each time we enter the contract
    ) + Op.SELFDESTRUCT(sendall_destination_address)


@pytest.fixture
def selfdestructing_initcode() -> bool:
    """
    Whether the contract shall self-destruct during initialization.
    By default it does not.
    """
    return False


@pytest.fixture
def selfdestruct_contract_initcode(
    selfdestruct_code: bytes,
    selfdestructing_initcode: bool,
) -> bytes:
    """Prepares an initcode that creates a self-destructing account."""
    if selfdestructing_initcode:
        return selfdestruct_code
    return Initcode(deploy_code=selfdestruct_code).assemble()


@pytest.mark.parametrize("create_opcode", [Op.CREATE, Op.CREATE2])
@pytest.mark.parametrize("call_times", [1, 40])
@pytest.mark.parametrize("prefunded_selfdestruct_address", [False, True])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_create_selfdestruct_same_tx(
    state_test: StateTestFiller,
    env: Environment,
    selfdestruct_code: bytes,
    selfdestruct_contract_initcode: bytes,
    sendall_destination_address: int,
    create_opcode: Op,
    call_times: int,  # Number of times to call the self-destructing contract in the same tx
    prefunded_selfdestruct_address: bool,
):
    # Our entry point is an initcode that in turn creates a self-destructing contract
    entry_code_address = compute_create_address(TestAddress, 0)
    entry_code_storage: Storage.StorageDictType = {}
    storage_index = count()
    sendall_amount = 0

    # Address of a pre-existing contract we use to simply copy initcode from
    initcode_copy_from_address = to_address(0x200)

    # Calculate the address of the selfdestructing contract
    if create_opcode == Op.CREATE:
        selfdestruct_contract_address = compute_create_address(entry_code_address, 1)
    elif create_opcode == Op.CREATE2:
        selfdestruct_contract_address = compute_create2_address(
            entry_code_address, 0, selfdestruct_contract_initcode
        )
    else:
        raise Exception("Invalid opcode")

    # Bytecode used to create the contract, can be CREATE or CREATE2
    op_args = [
        0,  # Value
        0,  # Offset
        len(selfdestruct_contract_initcode),  # Length
    ]
    if create_opcode == Op.CREATE2:
        # CREATE2 requires a salt argument
        op_args.append(0)
    create_bytecode = create_opcode(*op_args)

    # Entry code that will be executed, creates the contract and then calls it in the same tx
    entry_code = (
        # Initcode is already deployed at `initcode_copy_from_address`, so just copy it
        Op.EXTCODECOPY(
            Op.PUSH20(initcode_copy_from_address),
            0,
            0,
            len(selfdestruct_contract_initcode),
        )
        # And we store the created address for verification purposes
        + Op.SSTORE(
            0,
            create_bytecode,
        )
    )
    # Store the created address
    entry_code_storage[next(storage_index)] = selfdestruct_contract_address

    # Store the extcode* properties of the created address
    current_index = next(storage_index)
    entry_code += Op.SSTORE(
        current_index,
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )
    entry_code_storage[current_index] = len(selfdestruct_code)

    current_index = next(storage_index)
    entry_code += Op.SSTORE(
        current_index,
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )
    entry_code_storage[current_index] = bytes(keccak256(selfdestruct_code))

    # Call the self-destructing contract multiple times as required, incrementing the wei sent each
    # time
    for i in range(call_times):
        current_index = next(storage_index)
        entry_code += Op.SSTORE(
            current_index,
            Op.CALL(
                Op.GASLIMIT,  # Gas
                Op.PUSH20(selfdestruct_contract_address),  # Address
                i,  # Value
                0,
                0,
                0,
                0,
            ),
        )
        entry_code_storage[current_index] = 1

        # TODO: Why is this correct ??
        sendall_amount += i

        current_index = next(storage_index)
        entry_code += Op.SSTORE(
            current_index,
            Op.BALANCE(Op.PUSH20(selfdestruct_contract_address)),
        )
        entry_code_storage[current_index] = 0

    # Check the extcode* properties of the selfdestructing contract again
    current_index = next(storage_index)
    entry_code += Op.SSTORE(
        current_index,
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )
    entry_code_storage[current_index] = 0 if call_times > 0 else len(selfdestruct_code)

    current_index = next(storage_index)
    entry_code += Op.SSTORE(
        current_index,
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )
    entry_code_storage[current_index] = bytes(
        keccak256(selfdestruct_code if call_times > 0 else b"")
    )

    # Lastly return "0x00" so the entry point contract is created and we can retain the stored
    # values for verification.
    entry_code += Op.RETURN(len(selfdestruct_contract_initcode), 1)

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        initcode_copy_from_address: Account(code=selfdestruct_contract_initcode),
    }

    if prefunded_selfdestruct_address:
        # Address where the contract is created already had some balance,
        # which must be included in the send-all operation
        pre[selfdestruct_contract_address] = Account(balance=1000000000000000000000)
        sendall_amount += 1000000000000000000000

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        selfdestruct_contract_address: Account.NONEXISTENT,  # type: ignore
        initcode_copy_from_address: Account(
            code=selfdestruct_contract_initcode,
        ),
    }
    if sendall_amount > 0:
        post[to_address(sendall_destination_address)] = Account(balance=sendall_amount)

    nonce = count()
    tx = Transaction(
        ty=0x0,
        value=100_000,
        data=entry_code,
        chain_id=0x0,
        nonce=next(nonce),
        to=None,
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.parametrize("create_opcode", [Op.CREATE, Op.CREATE2])
@pytest.mark.parametrize("call_times", [0, 1])
@pytest.mark.parametrize("prefunded_selfdestruct_address", [False, True])
@pytest.mark.parametrize("selfdestructing_initcode", [True], ids=[""])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_selfdestructing_initcode(
    state_test: StateTestFiller,
    env: Environment,
    selfdestruct_contract_initcode: bytes,
    sendall_destination_address: int,
    create_opcode: Op,
    call_times: int,  # Number of times to call the self-destructing contract in the same tx
    prefunded_selfdestruct_address: bool,
):
    # Our entry point is an initcode that in turn creates a self-destructing contract
    entry_code_address = compute_create_address(TestAddress, 0)
    entry_code_storage: Storage.StorageDictType = {}
    storage_index = count()
    sendall_amount = 0

    # Address of a pre-existing contract we use to simply copy initcode from
    initcode_copy_from_address = to_address(0x200)

    # Calculate the address of the selfdestructing contract
    if create_opcode == Op.CREATE:
        selfdestruct_contract_address = compute_create_address(entry_code_address, 1)
    elif create_opcode == Op.CREATE2:
        selfdestruct_contract_address = compute_create2_address(
            entry_code_address, 0, selfdestruct_contract_initcode
        )
    else:
        raise Exception("Invalid opcode")

    # Bytecode used to create the contract, can be CREATE or CREATE2
    op_args = [
        0,  # Value
        0,  # Offset
        len(selfdestruct_contract_initcode),  # Length
    ]
    if create_opcode == Op.CREATE2:
        # CREATE2 requires a salt argument
        op_args.append(0)
    create_bytecode = create_opcode(*op_args)

    # Entry code that will be executed, creates the contract and then calls it in the same tx
    entry_code = (
        # Initcode is already deployed at `initcode_copy_from_address`, so just copy it
        Op.EXTCODECOPY(
            Op.PUSH20(initcode_copy_from_address),
            0,
            0,
            len(selfdestruct_contract_initcode),
        )
        # And we store the created address for verification purposes
        + Op.SSTORE(
            0,
            create_bytecode,
        )
    )
    # Store the created address
    entry_code_storage[next(storage_index)] = selfdestruct_contract_address

    # Store the extcode* properties of the created address
    current_index = next(storage_index)
    entry_code += Op.SSTORE(
        current_index,
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )
    entry_code_storage[current_index] = 0

    current_index = next(storage_index)
    entry_code += Op.SSTORE(
        current_index,
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )
    entry_code_storage[current_index] = bytes(keccak256(bytes()))

    # Call the self-destructing contract multiple times as required, incrementing the wei sent each
    # time
    for i in range(call_times):
        current_index = next(storage_index)
        entry_code += Op.SSTORE(
            current_index,
            Op.CALL(
                Op.GASLIMIT,  # Gas
                Op.PUSH20(selfdestruct_contract_address),  # Address
                i,  # Value
                0,
                0,
                0,
                0,
            ),
        )
        entry_code_storage[current_index] = 1

        current_index = next(storage_index)
        entry_code += Op.SSTORE(
            current_index,
            Op.BALANCE(Op.PUSH20(selfdestruct_contract_address)),
        )
        entry_code_storage[current_index] = 0

    # Lastly return "0x00" so the entry point contract is created and we can retain the stored
    # values for verification.
    entry_code += Op.RETURN(len(selfdestruct_contract_initcode), 1)

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        initcode_copy_from_address: Account(code=selfdestruct_contract_initcode),
    }

    if prefunded_selfdestruct_address:
        # Address where the contract is created already had some balance,
        # which must be included in the send-all operation
        pre[selfdestruct_contract_address] = Account(balance=1000000000000000000000)
        sendall_amount += 1000000000000000000000

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        selfdestruct_contract_address: Account.NONEXISTENT,  # type: ignore
        initcode_copy_from_address: Account(
            code=selfdestruct_contract_initcode,
        ),
    }
    if sendall_amount > 0:
        post[to_address(sendall_destination_address)] = Account(balance=sendall_amount)

    nonce = count()
    tx = Transaction(
        ty=0x0,
        value=100_000,
        data=entry_code,
        chain_id=0x0,
        nonce=next(nonce),
        to=None,
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.parametrize("create_opcode", [Op.CREATE2])  # Can only recreate using CREATE2
@pytest.mark.parametrize("recreate_times", [1])
@pytest.mark.parametrize("call_times", [1])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_recreate_selfdestructed_contract(
    blockchain_test: BlockchainTestFiller,
    env: Environment,
    selfdestruct_contract_initcode: bytes,
    create_opcode: Op,
    recreate_times: int,  # Number of times to recreate the contract in different transactions
    call_times: int,  # Number of times to call the self-destructing contract in the same tx
):
    assert create_opcode == Op.CREATE2, "cannot recreate contract using CREATE opcode"

    entry_code_address = to_address(
        0x100
    )  # Needs to be constant to be able to recreate the contract
    initcode_copy_from_address = to_address(0x200)
    entry_code_storage: Storage.StorageDictType = {}
    storage_index = count()

    # Calculate the address of the selfdestructing contract
    if create_opcode == Op.CREATE:
        selfdestruct_contract_address = compute_create_address(entry_code_address, 1)
    elif create_opcode == Op.CREATE2:
        selfdestruct_contract_address = compute_create2_address(
            entry_code_address, 0, selfdestruct_contract_initcode
        )
    else:
        raise Exception("Invalid opcode")

    # Bytecode used to create the contract
    op_args = [0, 0, len(selfdestruct_contract_initcode)]
    if create_opcode == Op.CREATE2:
        op_args.append(0)

    create_bytecode = create_opcode(*op_args)

    # Entry code that will be executed, creates the contract and then calls it
    entry_code = (
        # Initcode is already deployed at initcode_copy_from_address, so just copy it
        Op.EXTCODECOPY(
            Op.PUSH20(initcode_copy_from_address),
            0,
            0,
            len(selfdestruct_contract_initcode),
        )
        + Op.SSTORE(
            Op.CALLDATALOAD(0),
            create_bytecode,
        )
    )

    for i in range(call_times):
        entry_code += Op.CALL(
            Op.GASLIMIT,
            Op.PUSH20(selfdestruct_contract_address),
            i,
            0,
            0,
            0,
            0,
        )
        # CHECK BALANCE HERE

    entry_code += Op.RETURN(len(selfdestruct_contract_initcode), 1)

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        entry_code_address: Account(code=entry_code),
        initcode_copy_from_address: Account(code=selfdestruct_contract_initcode),
    }

    txs: List[Transaction] = []
    nonce = count()
    for i in range(recreate_times + 1):
        txs.append(
            Transaction(
                ty=0x0,
                data=to_hash_bytes(i),
                chain_id=0x0,
                nonce=next(nonce),
                to=entry_code_address,
                gas_limit=100000000,
                gas_price=10,
                protected=False,
            )
        )
        entry_code_storage[i] = selfdestruct_contract_address

    entry_address_expected_code = entry_code

    post: Dict[str, Account] = {
        entry_code_address: Account(code=entry_address_expected_code, storage=entry_code_storage),
        selfdestruct_contract_address: Account.NONEXISTENT,  # type: ignore
        initcode_copy_from_address: Account(code=selfdestruct_contract_initcode),
    }

    blockchain_test(genesis_environment=env, pre=pre, post=post, blocks=[Block(txs=txs)])


@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 1])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_selfdestruct_prev_created(
    state_test: StateTestFiller,
    eip_enabled: bool,
    env: Environment,
    selfdestruct_contract_initial_balance: int,
):
    """
    Test that if a previously created account that contains a selfdestruct is
    called, its balance is sent to the zero address.
    """

    # original code: 0x60016000556000ff  # noqa: SC100
    balance_destination_address = 0x200
    code = Op.SSTORE(0, 1) + Op.SELFDESTRUCT(balance_destination_address)

    selfdestruct_contract_address = "0x1111111111111111111111111111111111111111"
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        selfdestruct_contract_address: Account(
            balance=selfdestruct_contract_initial_balance, code=code
        ),
        to_address(balance_destination_address): Account(balance=1),
    }
    # CHECK BALANCE SOMEWHERE

    post: Dict[str, Account] = {
        to_address(balance_destination_address): Account(
            balance=selfdestruct_contract_initial_balance + 1
        ),
    }

    if eip_enabled:
        post[selfdestruct_contract_address] = Account(balance=0, code=code, storage={0: 1})
    else:
        post[selfdestruct_contract_address] = Account.NONEXISTENT  # type: ignore

    tx = Transaction(
        ty=0x0,
        data="",
        chain_id=0x0,
        nonce=0,
        to=selfdestruct_contract_address,
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.parametrize(
    "selfdestruct_contract_initial_balance,prefunding_tx",
    [
        (0, False),
        (1, False),
        (1, True),
    ],
    ids=[
        "no-prefund",
        "prefunded-in-selfdestruct-tx",
        "prefunded-in-tx-before-create-tx",
    ],
)
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_selfdestruct_prev_created_same_block(
    blockchain_test: BlockchainTestFiller,
    eip_enabled: bool,
    env: Environment,
    selfdestruct_code: bytes,
    prefunding_tx: bool,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_initial_balance: int,
    sendall_destination_address: int,
):
    """
    Test that if an account created in the same block that contains a selfdestruct is
    called, its balance is sent to the zero address.
    """

    selfdestruct_contract_address = compute_create_address(TestAddress, 1 if prefunding_tx else 0)

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        to_address(sendall_destination_address): Account(balance=1),
    }

    post: Dict[str, Account] = {
        to_address(sendall_destination_address): Account(
            balance=selfdestruct_contract_initial_balance + 1
        ),
    }

    if eip_enabled:
        post[selfdestruct_contract_address] = Account(balance=0, code=selfdestruct_code)
    else:
        post[selfdestruct_contract_address] = Account.NONEXISTENT  # type: ignore

    txs: List[Transaction] = []
    nonce = count()
    if prefunding_tx:
        # Send some balance to the account to be created before it is created
        txs += [
            Transaction(
                ty=0x0,
                chain_id=0x0,
                value=selfdestruct_contract_initial_balance,
                nonce=next(nonce),
                to=selfdestruct_contract_address,
                gas_limit=100000000,
                gas_price=10,
                protected=False,
            )
        ]
    txs += [
        Transaction(
            ty=0x0,
            data=selfdestruct_contract_initcode,
            chain_id=0x0,
            value=0,
            nonce=next(nonce),
            to=None,
            gas_limit=100000000,
            gas_price=10,
            protected=False,
        ),
        Transaction(
            ty=0x0,
            chain_id=0x0,
            value=selfdestruct_contract_initial_balance if not prefunding_tx else 0,
            nonce=next(nonce),
            to=selfdestruct_contract_address,
            gas_limit=100000000,
            gas_price=10,
            protected=False,
        ),
    ]

    blockchain_test(genesis_environment=env, pre=pre, post=post, blocks=[Block(txs=txs)])
