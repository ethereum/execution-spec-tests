"""Fixtures for EIP-7907 meter contract code size tests."""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Address,
    Alloc,
    Bytecode,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types import Environment

from .helpers import create_large_contract


@pytest.fixture
def env() -> Environment:
    """Environment fixture with sufficient gas limit for large contract tests."""
    return Environment(gas_limit=30_000_000)


@pytest.fixture
def large_contract_code() -> Bytecode:
    """Return the default large contract code."""
    return Op.STOP


@pytest.fixture
def large_contract_size(fork: Fork) -> int:
    """Return the minimum contract size that triggers the large contract access gas."""
    large_contract_size = fork.large_contract_size()
    if large_contract_size is None:
        return fork.max_code_size()
    else:
        return large_contract_size + 1


@pytest.fixture
def large_contract_bytecode(
    large_contract_size: int,
    large_contract_code: Bytecode | None,
) -> bytes:
    """Return the default large contract code."""
    return create_large_contract(size=large_contract_size, prefix=large_contract_code)


@pytest.fixture
def large_contract_address(
    pre: Alloc,
    large_contract_bytecode: bytes,
) -> Address:
    """Create a large contract address."""
    return pre.deploy_contract(large_contract_bytecode)
