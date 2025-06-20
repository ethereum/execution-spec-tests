"""
abstract: Tests [EIP-7907 Meter Contract Code Size And Increase Limit](https://eips.ethereum.org/EIPS/eip-7907)
    Test cases for [EIP-7907 Meter Contract Code Size And Increase Limit](https://eips.ethereum.org/EIPS/eip-7907)].
"""

import pytest

from ethereum_test_tools import Address, Alloc, Bytecode, StateTestFiller
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7907.md"
REFERENCE_SPEC_VERSION = "DUMMY_VERSION"

pytestmark = pytest.mark.valid_from("Prague")


def create_large_contract(
    *,
    size: int,
    padding_byte: bytes = b"\0",
    prefix: Bytecode | None = None,
) -> bytes:
    """Create a large contract with the given size and prefix."""
    if prefix is None:
        prefix = Bytecode()
    return bytes(prefix + padding_byte * (size - len(prefix)))


@pytest.fixture
def large_contract_code() -> Bytecode:
    """Return the default large contract code."""
    return Op.STOP


@pytest.fixture
def large_contract_address(
    pre: Alloc,
    large_contract_size: int,
    large_contract_code: Bytecode | None,
) -> Address:
    """Create a large contract address."""
    return pre.deploy_contract(
        create_large_contract(size=large_contract_size, prefix=large_contract_code)
    )


def test_contract_reentry(
    state_test: StateTestFiller,
    large_contract_address: Address,
):
    """
    Test a large contract being the transaction entry point, calls a different contract,
    and then re-enters the large contract back to the entry point.
    """
    pass


def test_different_large_contracts_same_code_hash():
    """
    Test calling two different large contracts with the same code hash in the
    same transaction.
    """
    pass


def test_calling_large_contract_twice_same_tx():
    """Test calling a large contract twice in the same transaction."""
    pass


def test_calling_large_contract_twice_different_tx():
    """Test calling a large contract twice in different transactions."""
    pass


def test_calling_large_contract_after_creation():
    """Test calling a large contract after it has been created (in the same transaction)."""
    pass


def test_calling_large_contract_in_authorization_list():
    """Test calling a large contract in the authorization list of the transaction."""
    pass


def test_calling_large_contract_in_access_list():
    """Test calling a large contract in the access list of the transaction."""
    pass


def test_opcode_then_call_large_contract():
    """
    Test calling a large contract after an opcode that accesses the account or code.

    - EXTCODESIZE
    - EXTCODEHASH
    - CODESIZE
    - CODECOPY
    - EXTCODECOPY
    - SELFDESTRUCT
    - BALANCE

    """
    pass


def test_call_large_contract_then_opcode():
    """Test using an opcode that accesses the account or code after calling a large contract."""
    pass


def test_call_large_contract_as_coinbase():
    """Test calling a large contract as the coinbase."""
    pass


def test_call_delegated_account_to_large_contract():
    """Test calling a large contract from a delegated account."""
    pass


def test_call_large_contract_after_oog_call_to_same_contract():
    """Test calling a large contract after an OOG call to the same contract."""
    pass
