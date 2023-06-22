"""
abstract: Tests [EIP-5656: MCOPY - Memory copying instruction](https://eips.ethereum.org/EIPS/eip-5656)

    Test memory copy under different call contexts [EIP-5656: MCOPY - Memory copying instruction](https://eips.ethereum.org/EIPS/eip-5656)

"""  # noqa: E501
from typing import List, Mapping, Tuple

import pytest
from .common import REFERENCE_SPEC_GIT_PATH, REFERENCE_SPEC_VERSION

from ethereum_test_tools import Account, StateTestFiller, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    OpcodeCallArg,
    Storage,
    TestAddress,
    Transaction,
    to_address,
)

code_address = 0x100
"""
Code address used to call the test bytecode on every test case.
"""

callee_address = 0x200
"""
Code address of the callee contract
"""


REFERENCE_SPEC_GIT_PATH = REFERENCE_SPEC_GIT_PATH
REFERENCE_SPEC_VERSION = REFERENCE_SPEC_VERSION


@pytest.fixture
def initial_memory() -> bytes:  # noqa: D103
    return bytes(range(0x00, 0x100))


@pytest.fixture
def callee_bytecode(initial_memory: bytes) -> bytes:
    """
    Callee simply performs mcopy operations that should not have any effect on the
    caller context.
    """
    bytecode = b""

    # Perform some copy operations
    bytecode += Op.MCOPY(0x00, 0x01, 0x01)
    bytecode += Op.MCOPY(0x01, 0x00, 0x01)
    bytecode += Op.MCOPY(0x01, 0x00, 0x20)
    # And a potential memory cleanup
    bytecode += Op.MCOPY(0x00, len(initial_memory), len(initial_memory))

    # In case of initcode, return empty code
    bytecode += Op.RETURN(0x00, 0x00)

    return bytecode


@pytest.fixture
def caller_bytecode(
    initial_memory: bytes,
    opcode: Op,
) -> bytes:
    """
    Bytecode to be used by the top level call to make a successful call to the callee,
    or execute initcode.
    """
    args: List[OpcodeCallArg] = []
    bytecode = bytes()
    if opcode in [Op.CALL, Op.CALLCODE]:
        args = [Op.GAS(), callee_address, 0, 0, 0, 0, 0]
    elif opcode in [Op.DELEGATECALL, Op.STATICCALL]:
        args = [Op.GAS(), callee_address, 0, 0, 0, 0]
    elif opcode in [Op.CREATE, Op.CREATE2]:
        # First copy the initcode that uses mcopy
        bytecode += Op.EXTCODECOPY(
            callee_address, len(initial_memory), 0, Op.EXTCODESIZE(callee_address)
        )
        if opcode == Op.CREATE:
            args = [0, len(initial_memory), Op.EXTCODESIZE(callee_address)]
        else:
            args = [0, len(initial_memory), Op.EXTCODESIZE(callee_address), 0]

    return bytecode + opcode(*args)


@pytest.fixture
def bytecode_storage(
    initial_memory: bytes,
    caller_bytecode: bytes,
) -> Tuple[bytes, Storage.StorageDictType]:
    """
    Prepares the bytecode and storage for the test, based on the starting memory and the final
    memory that resulted from the copy.
    """
    bytecode = b""
    storage = {}

    # Fill memory with initial values
    for i in range(0, len(initial_memory), 0x20):
        bytecode += Op.MSTORE(i, initial_memory[i : i + 0x20])

    # Perform the call to the contract that is going to perform mcopy
    bytecode += caller_bytecode

    # Store all memory in the initial range to verify the MCOPY in the subcall did not affect
    # this level's memory
    for w in range(0, len(initial_memory) // 0x20):
        bytecode += Op.SSTORE(w, Op.MLOAD(w * 0x20))
        storage[w] = initial_memory[w * 0x20 : w * 0x20 + 0x20]

    return (bytecode, storage)


@pytest.fixture
def pre(
    bytecode_storage: Tuple[bytes, Storage.StorageDictType],
    callee_bytecode: bytes,
) -> Mapping[str, Account]:  # noqa: D103
    return {
        TestAddress: Account(balance=10**40),
        to_address(code_address): Account(code=bytecode_storage[0]),
        to_address(callee_address): Account(code=callee_bytecode),
    }


@pytest.fixture
def tx() -> Transaction:  # noqa: D103
    return Transaction(
        to=to_address(code_address),
        gas_limit=1_000_000,
    )


@pytest.fixture
def post(
    bytecode_storage: Tuple[bytes, Storage.StorageDictType]
) -> Mapping[str, Account]:  # noqa: D103
    return {
        to_address(code_address): Account(storage=bytecode_storage[1]),
    }


@pytest.mark.parametrize(
    "opcode",
    [
        Op.CALL,
        Op.DELEGATECALL,
        Op.STATICCALL,
        Op.CALLCODE,
        Op.CREATE,
        Op.CREATE2,
    ],
)
@pytest.mark.valid_from("Cancun")
def test_no_memory_corruption_on_upper_call_stack_levels(
    state_test: StateTestFiller,
    pre: Mapping[str, Account],
    post: Mapping[str, Account],
    tx: Transaction,
):
    """
    Perform a subcall with any of the following opcodes, which uses MCOPY during its execution,
    and verify that the caller's memory is unaffected:
    - CALL
    - CALLCODE
    - DELEGATECALL
    - STATICCALL
    - CREATE
    - CREATE2
    """

    state_test(
        env=Environment(),
        pre=pre,
        post=post,
        txs=[tx],
    )
