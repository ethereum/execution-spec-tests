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
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6780.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

SELFDESTRUCT_EIP_NUMBER = 6780

PRE_EXISTING_SELFDESTRUCT_ADDRESS = "0x1111111111111111111111111111111111111111"

# TODO:

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
# - Delegate call to a contract that contains self-destruct and was created in the current tx
#    from a contract that was created in a previous tx
# - SENDALL to multiple different contracts in a single tx, from a single or multiple contracts,
#   all of which would not self destruct (or perhaps some of them would and some others won't)
# Recursive contract creation and self-destruction


@pytest.fixture
def eips(eip_enabled: bool) -> List[int]:
    """Prepares the list of EIPs depending on the test that enables it or not."""
    return [SELFDESTRUCT_EIP_NUMBER] if eip_enabled else []


@pytest.fixture
def env() -> Environment:
    """Default environment for all tests."""
    return Environment(
        coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        gas_limit=10_000_000_000,
    )


@pytest.fixture
def sendall_recipient_address() -> int:
    """Account that receives the balance from the self-destructed account."""
    return 0x1234


def selfdestruct_code_preset(
    sendall_recipient_address: int,
) -> bytes:
    """Return a bytecode that self-destructs."""
    return (
        Op.SSTORE(
            0,
            Op.ADD(Op.SLOAD(0), 1),  # Add to the SSTORE'd value each time we enter the contract
        )
        + Op.SELFDESTRUCT(sendall_recipient_address)
        # This should never be reached, even when the contract is not self-destructed
        + Op.SSTORE(0, 0)
    )


@pytest.fixture
def selfdestruct_code(
    sendall_recipient_address: int,
) -> bytes:
    """
    Creates the default self-destructing bytecode,
    which can be modified by each test if necessary.
    """
    return selfdestruct_code_preset(sendall_recipient_address)


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


@pytest.fixture
def initcode_copy_from_address() -> str:
    """Address of a pre-existing contract we use to simply copy initcode from."""
    return to_address(0xABCD)


@pytest.fixture
def entry_code_address() -> str:
    """Address where the entry code will run."""
    return compute_create_address(TestAddress, 0)


@pytest.fixture
def selfdestruct_contract_address(
    create_opcode: Op,
    entry_code_address: str,
    selfdestruct_contract_initcode: bytes,
) -> str:
    """Returns the address of the self-destructing contract."""
    if create_opcode == Op.CREATE:
        return compute_create_address(entry_code_address, 1)

    if create_opcode == Op.CREATE2:
        return compute_create2_address(entry_code_address, 0, selfdestruct_contract_initcode)

    raise Exception("Invalid opcode")


@pytest.fixture
def pre(
    initcode_copy_from_address: str,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_address: str,
    selfdestruct_contract_initial_balance: int,
    sendall_recipient_address: int,
) -> Dict[str, Account]:
    """Pre-state of all tests"""
    pre = {
        TestAddress: Account(balance=100_000_000_000_000_000_000),
        initcode_copy_from_address: Account(code=selfdestruct_contract_initcode),
    }

    if (
        selfdestruct_contract_initial_balance > 0
        and selfdestruct_contract_address != PRE_EXISTING_SELFDESTRUCT_ADDRESS
    ):
        pre[selfdestruct_contract_address] = Account(balance=selfdestruct_contract_initial_balance)

    # Also put a pre-existing copy of the self-destruct contract in a known place
    pre[PRE_EXISTING_SELFDESTRUCT_ADDRESS] = Account(
        code=selfdestruct_code_preset(sendall_recipient_address),
        balance=selfdestruct_contract_initial_balance,
    )

    # Send-all recipient account contains code that unconditionally resets an storage key upon
    # entry, so we can check that it was not executed
    pre[to_address(sendall_recipient_address)] = Account(
        code=Op.SSTORE(0, 0),
        storage={0: 1},
    )

    return pre


@pytest.mark.parametrize("create_opcode", [Op.CREATE, Op.CREATE2])
@pytest.mark.parametrize("call_times", [1, 40])
@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 100_000])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_create_selfdestruct_same_tx(
    state_test: StateTestFiller,
    env: Environment,
    pre: Dict[str, Account],
    entry_code_address: str,
    selfdestruct_code: bytes,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_address: str,
    sendall_recipient_address: int,
    initcode_copy_from_address: str,
    create_opcode: Op,
    call_times: int,
    selfdestruct_contract_initial_balance: int,
):
    # Our entry point is an initcode that in turn creates a self-destructing contract
    entry_code_storage = Storage()
    sendall_amount = 0

    # Bytecode used to create the contract, can be CREATE or CREATE2
    create_args = [
        0,  # Value
        0,  # Offset
        len(selfdestruct_contract_initcode),  # Length
    ]
    if create_opcode == Op.CREATE2:
        # CREATE2 requires a salt argument
        create_args.append(0)
    create_bytecode = create_opcode(*create_args)

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
            entry_code_storage.store_next(selfdestruct_contract_address),
            create_bytecode,
        )
    )

    # Store the extcode* properties of the created address
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(len(selfdestruct_code)),
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )

    entry_code += Op.SSTORE(
        entry_code_storage.store_next(keccak256(selfdestruct_code)),
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )

    # Call the self-destructing contract multiple times as required, incrementing the wei sent each
    # time
    for i in range(call_times):
        entry_code += Op.SSTORE(
            entry_code_storage.store_next(1),
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

        # TODO: Why is this correct ??
        sendall_amount += i

        entry_code += Op.SSTORE(
            entry_code_storage.store_next(0),
            Op.BALANCE(Op.PUSH20(selfdestruct_contract_address)),
        )

    # Check the extcode* properties of the selfdestructing contract again
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(len(selfdestruct_code)),
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )

    entry_code += Op.SSTORE(
        entry_code_storage.store_next(keccak256(selfdestruct_code)),
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )

    # Lastly return "0x00" so the entry point contract is created and we can retain the stored
    # values for verification.
    entry_code += Op.RETURN(len(selfdestruct_contract_initcode), 1)

    if selfdestruct_contract_initial_balance > 0:
        # Address where the contract is created already had some balance,
        # which must be included in the send-all operation
        sendall_amount += selfdestruct_contract_initial_balance

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        selfdestruct_contract_address: Account.NONEXISTENT,  # type: ignore
        initcode_copy_from_address: Account(
            code=selfdestruct_contract_initcode,
        ),
        to_address(sendall_recipient_address): Account(balance=sendall_amount, storage={0: 1}),
    }

    nonce = count()
    tx = Transaction(
        ty=0x0,
        value=100_000,
        data=entry_code,
        chain_id=0x0,
        nonce=next(nonce),
        to=None,
        gas_limit=100_000_000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.parametrize("create_opcode", [Op.CREATE, Op.CREATE2])
@pytest.mark.parametrize("call_times", [0, 1])
@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 100_000])
@pytest.mark.parametrize("selfdestructing_initcode", [True], ids=[""])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_selfdestructing_initcode(
    state_test: StateTestFiller,
    env: Environment,
    pre: Dict[str, Account],
    entry_code_address: str,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_address: str,
    sendall_recipient_address: int,
    initcode_copy_from_address: str,
    create_opcode: Op,
    call_times: int,  # Number of times to call the self-destructing contract in the same tx
    selfdestruct_contract_initial_balance: int,
):
    # Our entry point is an initcode that in turn creates a self-destructing contract
    entry_code_storage = Storage()
    sendall_amount = 0

    # Bytecode used to create the contract, can be CREATE or CREATE2
    create_args = [
        0,  # Value
        0,  # Offset
        len(selfdestruct_contract_initcode),  # Length
    ]
    if create_opcode == Op.CREATE2:
        # CREATE2 requires a salt argument
        create_args.append(0)
    create_bytecode = create_opcode(*create_args)

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
            entry_code_storage.store_next(selfdestruct_contract_address),
            create_bytecode,
        )
    )

    # Store the extcode* properties of the created address
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(0),
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )

    entry_code += Op.SSTORE(
        entry_code_storage.store_next(keccak256(bytes())),
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )

    # Call the self-destructing contract multiple times as required, incrementing the wei sent each
    # time
    for i in range(call_times):
        entry_code += Op.SSTORE(
            entry_code_storage.store_next(1),
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

        entry_code += Op.SSTORE(
            entry_code_storage.store_next(0),
            Op.BALANCE(Op.PUSH20(selfdestruct_contract_address)),
        )

    # Lastly return "0x00" so the entry point contract is created and we can retain the stored
    # values for verification.
    entry_code += Op.RETURN(len(selfdestruct_contract_initcode), 1)

    if selfdestruct_contract_initial_balance > 0:
        # Address where the contract is created already had some balance,
        # which must be included in the send-all operation
        sendall_amount += selfdestruct_contract_initial_balance

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        selfdestruct_contract_address: Account.NONEXISTENT,  # type: ignore
        initcode_copy_from_address: Account(
            code=selfdestruct_contract_initcode,
        ),
        to_address(sendall_recipient_address): Account(balance=sendall_amount, storage={0: 1}),
    }

    nonce = count()
    tx = Transaction(
        ty=0x0,
        value=100_000,
        data=entry_code,
        chain_id=0x0,
        nonce=next(nonce),
        to=None,
        gas_limit=100_000_000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.parametrize("tx_value", [0, 100_000])
@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 100_000])
@pytest.mark.parametrize("selfdestructing_initcode", [True], ids=[""])
@pytest.mark.parametrize("selfdestruct_contract_address", [compute_create_address(TestAddress, 0)])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_selfdestructing_initcode_create_tx(
    state_test: StateTestFiller,
    env: Environment,
    pre: Dict[str, Account],
    tx_value: int,
    entry_code_address: str,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_address: str,
    sendall_recipient_address: int,
    initcode_copy_from_address: str,
    selfdestruct_contract_initial_balance: int,
):
    assert entry_code_address == selfdestruct_contract_address

    # Our entry point is an initcode that in turn creates a self-destructing contract
    sendall_amount = selfdestruct_contract_initial_balance + tx_value

    post: Dict[str, Account] = {
        selfdestruct_contract_address: Account.NONEXISTENT,  # type: ignore
        initcode_copy_from_address: Account(
            code=selfdestruct_contract_initcode,
        ),
        to_address(sendall_recipient_address): Account(balance=sendall_amount, storage={0: 1}),
    }

    nonce = count()
    tx = Transaction(
        ty=0x0,
        value=tx_value,
        data=selfdestruct_contract_initcode,
        chain_id=0x0,
        nonce=next(nonce),
        to=None,
        gas_limit=100_000_000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.parametrize("create_opcode", [Op.CREATE2])  # Can only recreate using CREATE2
@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 100_000])
@pytest.mark.parametrize("recreate_times", [1])
@pytest.mark.parametrize("call_times", [1])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_recreate_selfdestructed_contract_different_txs(
    blockchain_test: BlockchainTestFiller,
    env: Environment,
    pre: Dict[str, Account],
    entry_code_address: str,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_address: str,
    selfdestruct_contract_initial_balance: int,
    sendall_recipient_address: int,
    initcode_copy_from_address: str,
    create_opcode: Op,
    recreate_times: int,  # Number of times to recreate the contract in different transactions
    call_times: int,  # Number of times to call the self-destructing contract in the same tx
):
    """
    Test that a contract can be recreated after it has self-destructed.
    """
    entry_code_storage = Storage()
    sendall_amount = selfdestruct_contract_initial_balance

    # Bytecode used to create the contract
    assert create_opcode == Op.CREATE2, "cannot recreate contract using CREATE opcode"
    create_bytecode = Op.CREATE2(0, 0, len(selfdestruct_contract_initcode), 0)

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
            Op.ADD(Op.SLOAD(0), 1),
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
        sendall_amount += i

    entry_code += Op.RETURN(len(selfdestruct_contract_initcode), 1)

    txs: List[Transaction] = []
    nonce = count()
    for i in range(recreate_times + 1):
        txs.append(
            Transaction(
                ty=0x0,
                data=entry_code,
                chain_id=0x0,
                nonce=next(nonce),
                to=entry_code_address if i > 0 else None,  # First call creates the contract
                gas_limit=100_000_000,
                gas_price=10,
                protected=False,
            )
        )

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        selfdestruct_contract_address: Account.NONEXISTENT,  # type: ignore
        initcode_copy_from_address: Account(
            code=selfdestruct_contract_initcode,
        ),
        to_address(sendall_recipient_address): Account(balance=sendall_amount, storage={0: 1}),
    }

    blockchain_test(genesis_environment=env, pre=pre, post=post, blocks=[Block(txs=txs)])


@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 1])
@pytest.mark.parametrize("call_times", [1, 10])
@pytest.mark.parametrize("selfdestruct_contract_address", [PRE_EXISTING_SELFDESTRUCT_ADDRESS])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_selfdestruct_pre_existing(
    state_test: StateTestFiller,
    eip_enabled: bool,
    env: Environment,
    pre: Dict[str, Account],
    entry_code_address: str,
    selfdestruct_contract_address: str,
    selfdestruct_code: bytes,
    selfdestruct_contract_initial_balance: int,
    sendall_recipient_address: int,
    call_times: int,
):
    """
    Test that if a previously created account that contains a selfdestruct is
    called, its balance is sent to the destination address.
    """
    entry_code_storage = Storage()
    sendall_amount = selfdestruct_contract_initial_balance
    entry_code = b""

    # Entry code in this case will simply call the pre-existing selfdestructing contract,
    # as many times as required

    # Call the self-destructing contract multiple times as required, incrementing the wei sent each
    # time
    for i in range(call_times):
        entry_code += Op.SSTORE(
            entry_code_storage.store_next(1),
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

        sendall_amount += i

        entry_code += Op.SSTORE(
            entry_code_storage.store_next(0),
            Op.BALANCE(Op.PUSH20(selfdestruct_contract_address)),
        )

    # Check the extcode* properties of the selfdestructing contract
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(len(selfdestruct_code)),
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )

    entry_code += Op.SSTORE(
        # entry_code_storage.store_next(keccak256(selfdestruct_code if eip_enabled else b""))
        # TODO: Don't really understand why this works. It should be empty if EIP is disabled,
        #       but it works if it's not
        entry_code_storage.store_next(keccak256(selfdestruct_code)),
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )

    # Lastly return "0x00" so the entry point contract is created and we can retain the stored
    # values for verification.
    entry_code += Op.RETURN(0, 1)

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        to_address(sendall_recipient_address): Account(balance=sendall_amount, storage={0: 1}),
    }

    if eip_enabled:
        post[selfdestruct_contract_address] = Account(
            balance=0, code=selfdestruct_code, storage={0: call_times}
        )
    else:
        post[selfdestruct_contract_address] = Account.NONEXISTENT  # type: ignore

    nonce = count()
    tx = Transaction(
        ty=0x0,
        value=100_000,
        data=entry_code,
        chain_id=0x0,
        nonce=next(nonce),
        to=None,
        gas_limit=100_000_000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 1])
@pytest.mark.parametrize("call_times", [1, 10])
@pytest.mark.parametrize(
    "selfdestruct_contract_address,entry_code_address",
    [(compute_create_address(TestAddress, 0), compute_create_address(TestAddress, 1))],
)
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_selfdestruct_created_same_block_different_tx(
    blockchain_test: BlockchainTestFiller,
    eip_enabled: bool,
    env: Environment,
    pre: Dict[str, Account],
    entry_code_address: str,
    selfdestruct_contract_address: str,
    selfdestruct_code: bytes,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_initial_balance: int,
    sendall_recipient_address: int,
    call_times: int,
):
    """
    Test that if an account created in the same block that contains a selfdestruct is
    called, its balance is sent to the zero address.
    """
    entry_code_storage = Storage()
    sendall_amount = selfdestruct_contract_initial_balance
    entry_code = b""

    # Entry code in this case will simply call the pre-existing selfdestructing contract,
    # as many times as required

    # Call the self-destructing contract multiple times as required, incrementing the wei sent each
    # time
    for i in range(call_times):
        entry_code += Op.SSTORE(
            entry_code_storage.store_next(1),
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

        sendall_amount += i

        entry_code += Op.SSTORE(
            entry_code_storage.store_next(0),
            Op.BALANCE(Op.PUSH20(selfdestruct_contract_address)),
        )

    # Check the extcode* properties of the selfdestructing contract
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(len(selfdestruct_code)),
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )

    entry_code += Op.SSTORE(
        # entry_code_storage.store_next(keccak256(selfdestruct_code if eip_enabled else b""))
        # TODO: Don't really understand why this works. It should be empty if EIP is disabled,
        #       but it works if it's not
        entry_code_storage.store_next(keccak256(selfdestruct_code)),
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )

    # Lastly return "0x00" so the entry point contract is created and we can retain the stored
    # values for verification.
    entry_code += Op.RETURN(0, 1)

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        to_address(sendall_recipient_address): Account(balance=sendall_amount, storage={0: 1}),
    }

    if eip_enabled:
        post[selfdestruct_contract_address] = Account(
            balance=0, code=selfdestruct_code, storage={0: call_times}
        )
    else:
        post[selfdestruct_contract_address] = Account.NONEXISTENT  # type: ignore

    nonce = count()
    txs = [
        Transaction(
            ty=0x0,
            value=0,
            data=selfdestruct_contract_initcode,
            chain_id=0x0,
            nonce=next(nonce),
            to=None,
            gas_limit=100_000_000,
            gas_price=10,
            protected=False,
        ),
        Transaction(
            ty=0x0,
            value=100_000,
            data=entry_code,
            chain_id=0x0,
            nonce=next(nonce),
            to=None,
            gas_limit=100_000_000,
            gas_price=10,
            protected=False,
        ),
    ]

    blockchain_test(genesis_environment=env, pre=pre, post=post, blocks=[Block(txs=txs)])


@pytest.mark.parametrize(
    "selfdestruct_code",
    [
        Op.DELEGATECALL(
            Op.GAS,
            Op.PUSH20(PRE_EXISTING_SELFDESTRUCT_ADDRESS),
            0,
            0,
            0,
            0,
        ),
        Op.CALLCODE(
            Op.GAS,
            Op.PUSH20(PRE_EXISTING_SELFDESTRUCT_ADDRESS),
            0,
            0,
            0,
            0,
            0,
        ),
    ],
    ids=["delegatecall", "callcode"],
)  # The self-destruct code is delegatecall
@pytest.mark.parametrize("call_times", [1])
@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 1])
@pytest.mark.parametrize("create_opcode", [Op.CREATE])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_delegatecall_from_new_contract_to_pre_existing_contract(
    state_test: StateTestFiller,
    env: Environment,
    pre: Dict[str, Account],
    entry_code_address: str,
    selfdestruct_code: bytes,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_address: str,
    sendall_recipient_address: int,
    initcode_copy_from_address: str,
    create_opcode: Op,
    call_times: int,
    selfdestruct_contract_initial_balance: int,
):
    # Our entry point is an initcode that in turn creates a self-destructing contract
    entry_code_storage = Storage()
    sendall_amount = 0

    # Bytecode used to create the contract, can be CREATE or CREATE2
    create_args = [
        0,  # Value
        0,  # Offset
        len(selfdestruct_contract_initcode),  # Length
    ]
    if create_opcode == Op.CREATE2:
        # CREATE2 requires a salt argument
        create_args.append(0)
    create_bytecode = create_opcode(*create_args)

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
            entry_code_storage.store_next(selfdestruct_contract_address),
            create_bytecode,
        )
    )

    # Store the extcode* properties of the created address
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(len(selfdestruct_code)),
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )

    entry_code += Op.SSTORE(
        entry_code_storage.store_next(keccak256(selfdestruct_code)),
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )

    # Call the self-destructing contract multiple times as required, incrementing the wei sent each
    # time
    for i in range(call_times):
        entry_code += Op.SSTORE(
            entry_code_storage.store_next(1),
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

        # TODO: Why is this correct ??
        sendall_amount += i

        entry_code += Op.SSTORE(
            entry_code_storage.store_next(0),
            Op.BALANCE(Op.PUSH20(selfdestruct_contract_address)),
        )

    # Check the extcode* properties of the selfdestructing contract again
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(len(selfdestruct_code)),
        Op.EXTCODESIZE(Op.PUSH20(selfdestruct_contract_address)),
    )

    entry_code += Op.SSTORE(
        entry_code_storage.store_next(keccak256(selfdestruct_code)),
        Op.EXTCODEHASH(Op.PUSH20(selfdestruct_contract_address)),
    )

    # Lastly return "0x00" so the entry point contract is created and we can retain the stored
    # values for verification.
    entry_code += Op.RETURN(len(selfdestruct_contract_initcode), 1)

    if selfdestruct_contract_initial_balance > 0:
        # Address where the contract is created already had some balance,
        # which must be included in the send-all operation
        sendall_amount += selfdestruct_contract_initial_balance

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        selfdestruct_contract_address: Account.NONEXISTENT,  # type: ignore
        initcode_copy_from_address: Account(
            code=selfdestruct_contract_initcode,
        ),
        to_address(sendall_recipient_address): Account(balance=sendall_amount, storage={0: 1}),
    }

    nonce = count()
    tx = Transaction(
        ty=0x0,
        value=100_000,
        data=entry_code,
        chain_id=0x0,
        nonce=next(nonce),
        to=None,
        gas_limit=100_000_000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])


@pytest.mark.parametrize("create_opcode", [Op.CREATE, Op.CREATE2])
@pytest.mark.parametrize("call_opcode", [Op.DELEGATECALL, Op.CALLCODE])
@pytest.mark.parametrize("call_times", [1])
@pytest.mark.parametrize("selfdestruct_contract_initial_balance", [0, 1])
@pytest.mark.parametrize("eip_enabled", [True, False])
@pytest.mark.valid_from("Shanghai")
def test_delegatecall_from_pre_existing_contract_to_new_contract(
    state_test: StateTestFiller,
    eip_enabled: bool,
    env: Environment,
    pre: Dict[str, Account],
    entry_code_address: str,
    selfdestruct_code: bytes,
    selfdestruct_contract_initcode: bytes,
    selfdestruct_contract_address: str,
    sendall_recipient_address: int,
    initcode_copy_from_address: str,
    call_opcode: Op,
    create_opcode: Op,
    call_times: int,
    selfdestruct_contract_initial_balance: int,
):
    # Add the contract that delegate calls to the newly created contract
    delegate_caller_address = "0x2222222222222222222222222222222222222222"
    call_args: List[int | bytes] = [
        Op.GAS(),
        Op.PUSH20(selfdestruct_contract_address),
        0,
        0,
        0,
        0,
    ]
    if call_opcode == Op.CALLCODE:
        # CALLCODE requires `value`
        call_args.append(0)
    delegate_caller_code = call_opcode(*call_args)
    pre[delegate_caller_address] = Account(code=delegate_caller_code)

    # Our entry point is an initcode that in turn creates a self-destructing contract
    entry_code_storage = Storage()
    sendall_amount = 0

    # Bytecode used to create the contract, can be CREATE or CREATE2
    create_args = [
        0,  # Value
        0,  # Offset
        len(selfdestruct_contract_initcode),  # Length
    ]
    if create_opcode == Op.CREATE2:
        # CREATE2 requires a salt argument
        create_args.append(0)
    create_bytecode = create_opcode(*create_args)

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
            entry_code_storage.store_next(selfdestruct_contract_address),
            create_bytecode,
        )
    )

    # Store the extcode* properties of the pre-existing address
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(len(delegate_caller_code)),
        Op.EXTCODESIZE(Op.PUSH20(delegate_caller_address)),
    )

    entry_code += Op.SSTORE(
        entry_code_storage.store_next(keccak256(delegate_caller_code)),
        Op.EXTCODEHASH(Op.PUSH20(delegate_caller_address)),
    )

    # Now instead of calling the newly created contract directly, we delegate call to it
    # from a pre-existing contract, and the contract must not self-destruct
    for i in range(call_times):
        entry_code += Op.SSTORE(
            entry_code_storage.store_next(1),
            Op.CALL(
                Op.GASLIMIT,  # Gas
                Op.PUSH20(delegate_caller_address),  # Address
                i,  # Value
                0,
                0,
                0,
                0,
            ),
        )

        # TODO: Why is this correct ??
        sendall_amount += i

        entry_code += Op.SSTORE(
            entry_code_storage.store_next(0),
            Op.BALANCE(Op.PUSH20(delegate_caller_address)),
        )

    # Check the extcode* properties of the pre-existing address again
    entry_code += Op.SSTORE(
        entry_code_storage.store_next(len(selfdestruct_code)),
        Op.EXTCODESIZE(Op.PUSH20(delegate_caller_address)),
    )

    entry_code += Op.SSTORE(
        entry_code_storage.store_next(keccak256(selfdestruct_code)),
        Op.EXTCODEHASH(Op.PUSH20(delegate_caller_address)),
    )

    # Lastly return "0x00" so the entry point contract is created and we can retain the stored
    # values for verification.
    entry_code += Op.RETURN(len(selfdestruct_contract_initcode), 1)

    post: Dict[str, Account] = {
        entry_code_address: Account(
            code="0x00",
            storage=entry_code_storage,
        ),
        selfdestruct_contract_address: Account(
            code=selfdestruct_code, balance=selfdestruct_contract_initial_balance
        ),
        initcode_copy_from_address: Account(
            code=selfdestruct_contract_initcode,
        ),
        to_address(sendall_recipient_address): Account(balance=sendall_amount, storage={0: 1}),
    }

    if eip_enabled:
        post[delegate_caller_address] = Account(code=delegate_caller_code, balance=0)
    else:
        post[delegate_caller_address] = Account.NONEXISTENT  # type: ignore

    nonce = count()
    tx = Transaction(
        ty=0x0,
        value=100_000,
        data=entry_code,
        chain_id=0x0,
        nonce=next(nonce),
        to=None,
        gas_limit=100_000_000,
        gas_price=10,
        protected=False,
    )

    state_test(env=env, pre=pre, post=post, txs=[tx])
