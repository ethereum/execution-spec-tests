"""
abstract: Tests [EIP-5656: MCOPY - Memory copying instruction](https://eips.ethereum.org/EIPS/eip-5656)

    Test copy operations of [EIP-5656: MCOPY - Memory copying instruction](https://eips.ethereum.org/EIPS/eip-5656)

"""  # noqa: E501
from typing import Mapping, Tuple

import pytest

from .common import REFERENCE_SPEC_GIT_PATH, REFERENCE_SPEC_VERSION
from ethereum_test_tools import Account, StateTestFiller, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    Storage,
    TestAddress,
    Transaction,
    cost_memory_bytes,
    to_address,
)

caller_address = 0x100
"""
Code address used to call the test bytecode on every test case.
"""

memory_expansion_address = 0x200
"""
Code address used to perform the memory expansion.
"""

REFERENCE_SPEC_GIT_PATH = REFERENCE_SPEC_GIT_PATH
REFERENCE_SPEC_VERSION = REFERENCE_SPEC_VERSION


@pytest.fixture
def callee_bytecode(dest: int, src: int, length: int) -> bytes:
    """
    Callee performs a single mcopy operation and then returns.
    """
    bytecode = b""

    # Copy the initial memory
    bytecode += Op.CALLDATACOPY(0x00, 0x00, Op.CALLDATASIZE())

    # Pushes for the return operation
    bytecode += Op.PUSH1(0x00) + Op.PUSH1(0x00)

    # Perform the mcopy operation
    bytecode += Op.MCOPY(dest, src, length)

    bytecode += Op.RETURN

    return bytecode


@pytest.fixture
def subcall_exact_cost(
    initial_memory: bytes,
    dest: int,
    length: int,
) -> int:
    mcopy_cost = 3
    mcopy_cost += 3 * ((length + 31) // 32)
    if length > 0 and dest + length > len(initial_memory):
        mcopy_cost += cost_memory_bytes(dest + length, len(initial_memory))

    calldatacopy_cost = 3
    calldatacopy_cost += 3 * ((len(initial_memory) + 31) // 32)
    calldatacopy_cost += cost_memory_bytes(len(initial_memory), 0)

    pushes_cost = 3 * 7
    calldatasize_cost = 2
    return mcopy_cost + calldatacopy_cost + pushes_cost + calldatasize_cost


@pytest.fixture
def bytecode_storage(
    subcall_exact_cost: int,
    successful: bool,
) -> Tuple[bytes, Storage.StorageDictType]:
    """
    Prepares the bytecode and storage for the test, based on the expected result of the subcall
    (whether it succeeds or fails depending on the length of the memory expansion).
    """
    bytecode = b""
    storage = {}

    # Pass on the calldata
    bytecode += Op.CALLDATACOPY(0x00, 0x00, Op.CALLDATASIZE())

    subcall_gas = subcall_exact_cost if successful else subcall_exact_cost - 1

    # Perform the subcall and store a one in the result location
    bytecode += Op.SSTORE(
        Op.CALL(subcall_gas, memory_expansion_address, 0, 0, Op.CALLDATASIZE(), 0, 0), 1
    )

    if successful:
        storage[1] = 1
    else:
        storage[0] = 1

    return (bytecode, storage)


@pytest.fixture
def pre(
    bytecode_storage: Tuple[bytes, Storage.StorageDictType],
    callee_bytecode: bytes,
) -> Mapping[str, Account]:  # noqa: D103
    return {
        TestAddress: Account(balance=10**40),
        to_address(caller_address): Account(code=bytecode_storage[0]),
        to_address(memory_expansion_address): Account(code=callee_bytecode),
    }


@pytest.fixture
def tx(
    subcall_exact_cost: int,
    initial_memory: bytes,
) -> Transaction:  # noqa: D103
    return Transaction(
        to=to_address(caller_address),
        data=initial_memory,
        gas_limit=max(500_000, subcall_exact_cost * 2),
    )


@pytest.fixture
def post(
    bytecode_storage: Tuple[bytes, Storage.StorageDictType]
) -> Mapping[str, Account]:  # noqa: D103
    return {
        to_address(caller_address): Account(storage=bytecode_storage[1]),
    }


@pytest.mark.parametrize(
    "dest,src,length",
    [
        (0x00, 0x00, 0x01),
        (0x100, 0x00, 0x01),
        (0x1F, 0x00, 0x01),
        (0x20, 0x00, 0x01),
        (0x1000, 0x00, 0x01),
        (0x1000, 0x00, 0x40),
        (0x00, 0x00, 0x00),
        (2**256 - 1, 0x00, 0x00),
        (0x00, 2**256 - 1, 0x00),
        (0x00, 2**256 - 1, 0x01),
        (2**256 - 1, 2**256 - 1, 0x00),
    ],
    ids=[
        "single_byte_expansion",
        "single_byte_expansion_2",
        "single_byte_expansion_word_boundary",
        "single_byte_expansion_word_boundary_2",
        "multi_word_expansion",
        "multi_word_expansion_2",
        "zero_length_expansion",
        "huge_dest_zero_length",
        "huge_src_zero_length",
        "huge_src_one_byte_length",
        "huge_dest_huge_src_zero_length",
    ],
)
@pytest.mark.parametrize("successful", [True, False])
@pytest.mark.parametrize(
    "initial_memory",
    [
        bytes(range(0x00, 0x100)),
        bytes(),
    ],
    ids=[
        "from_existent_memory",
        "from_empty_memory",
    ],
)
@pytest.mark.valid_from("Cancun")
def test_mcopy_memory_expansion(
    state_test: StateTestFiller,
    pre: Mapping[str, Account],
    post: Mapping[str, Account],
    tx: Transaction,
):
    """
    Perform MCOPY operations that expand the memory, and verify the gas it costs to do so.
    """

    state_test(
        env=Environment(),
        pre=pre,
        post=post,
        txs=[tx],
    )
