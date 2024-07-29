"""
abstract: Tests [EIP-5656: MCOPY - Memory copying instruction](https://eips.ethereum.org/EIPS/eip-5656)
    Test copy operations of [EIP-5656: MCOPY - Memory copying instruction](https://eips.ethereum.org/EIPS/eip-5656)
    that produce a memory expansion, and potentially an out-of-gas error.

"""  # noqa: E501
import pytest

from ethereum_test_tools import Bytecode, GasTestType
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import bytecode_gas_test, cost_memory_bytes

from .common import REFERENCE_SPEC_GIT_PATH, REFERENCE_SPEC_VERSION

REFERENCE_SPEC_GIT_PATH = REFERENCE_SPEC_GIT_PATH
REFERENCE_SPEC_VERSION = REFERENCE_SPEC_VERSION


@pytest.fixture
def bytecode(dest: int, src: int, length: int) -> Bytecode:
    """
    Bytecode that performs a single mcopy operation with given parameters.
    """
    # Copy the initial memory
    bytecode = Op.CALLDATACOPY(0x00, 0x00, Op.CALLDATASIZE())

    # Perform the mcopy operation
    bytecode += Op.MCOPY(dest, src, length)

    return bytecode


@pytest.fixture
def exact_gas_cost(
    initial_memory: bytes,
    dest: int,
    length: int,
) -> int:
    """
    Returns the exact cost of the bytecode execution, based on the initial memory and the length
    of the copy.
    """
    mcopy_cost = 3
    mcopy_cost += 3 * ((length + 31) // 32)
    if length > 0 and dest + length > len(initial_memory):
        mcopy_cost += cost_memory_bytes(dest + length, len(initial_memory))

    calldatacopy_cost = 3
    calldatacopy_cost += 3 * ((len(initial_memory) + 31) // 32)
    calldatacopy_cost += cost_memory_bytes(len(initial_memory), 0)

    pushes_cost = 3 * 5
    calldatasize_cost = 2
    return mcopy_cost + calldatacopy_cost + pushes_cost + calldatasize_cost


@pytest.fixture
def data(initial_memory: bytes) -> bytes:
    """
    Fixture rename for test case generator.
    """
    return initial_memory


@pytest.mark.parametrize(
    "dest,src,length",
    [
        pytest.param(0x00, 0x00, 0x01, id="single_byte_expansion"),
        pytest.param(0x100, 0x00, 0x01, id="single_byte_expansion_2"),
        pytest.param(0x1F, 0x00, 0x01, id="single_byte_expansion_word_boundary"),
        pytest.param(0x20, 0x00, 0x01, id="single_byte_expansion_word_boundary_2"),
        pytest.param(0x1000, 0x00, 0x01, id="multi_word_expansion"),
        pytest.param(0x1000, 0x00, 0x40, id="multi_word_expansion_2"),
        pytest.param(0x00, 0x00, 0x00, id="zero_length_expansion"),
        pytest.param(2**256 - 1, 0x00, 0x00, id="huge_dest_zero_length"),
        pytest.param(0x00, 2**256 - 1, 0x00, id="huge_src_zero_length"),
        pytest.param(2**256 - 1, 2**256 - 1, 0x00, id="huge_dest_huge_src_zero_length"),
    ],
)
@pytest.mark.parametrize(
    "initial_memory",
    [
        pytest.param(bytes(range(0x00, 0x100)), id="from_existent_memory"),
        pytest.param(bytes(), id="from_empty_memory"),
    ],
)
@pytest.mark.valid_from("Cancun")
@bytecode_gas_test(with_data=True)
def test_mcopy_memory_expansion_gas():
    """
    Perform MCOPY operations that expand the memory, and verify the gas it costs to do so.
    """
    pass


@pytest.mark.parametrize(
    "dest,src,length",
    [
        pytest.param(2**256 - 1, 0x00, 0x01, id="max_dest_single_byte_expansion"),
        pytest.param(2**256 - 2, 0x00, 0x01, id="max_dest_minus_one_single_byte_expansion"),
        pytest.param(2**255 - 1, 0x00, 0x01, id="half_max_dest_single_byte_expansion"),
        pytest.param(0x00, 2**256 - 1, 0x01, id="max_src_single_byte_expansion"),
        pytest.param(0x00, 2**256 - 2, 0x01, id="max_src_minus_one_single_byte_expansion"),
        pytest.param(0x00, 2**255 - 1, 0x01, id="half_max_src_single_byte_expansion"),
        pytest.param(0x00, 0x00, 2**256 - 1, id="max_length_expansion"),
        pytest.param(0x00, 0x00, 2**256 - 2, id="max_length_minus_one_expansion"),
        pytest.param(0x00, 0x00, 2**255 - 1, id="half_max_length_expansion"),
    ],
)
@pytest.mark.parametrize(
    "exact_gas_cost", [pytest.param(30_000_000, id="")]
)  # Hard-code gas, otherwise it would be impossibly large
@pytest.mark.parametrize(
    "initial_memory",
    [
        pytest.param(bytes(range(0x00, 0x100)), id="from_existent_memory"),
        pytest.param(bytes(), id="from_empty_memory"),
    ],
)
@pytest.mark.valid_from("Cancun")
@bytecode_gas_test(gas_test_types=GasTestType.OOG, with_data=True)
def test_mcopy_huge_memory_expansion():
    """
    Perform MCOPY operations that expand the memory by huge amounts, and verify that it correctly
    runs out of gas.
    """
    pass
