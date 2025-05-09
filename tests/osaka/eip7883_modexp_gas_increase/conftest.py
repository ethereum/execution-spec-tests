"""Shared pytest definitions local to EIP-7883 tests."""

from typing import Dict

import pytest

from ethereum_test_tools import (
    EOA,
    Account,
    Address,
    Alloc,
    Environment,
    Storage,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .spec import Spec


@pytest.fixture
def env() -> Environment:
    """Environment fixture."""
    return Environment()


@pytest.fixture
def sender(pre: Alloc):
    """Create and fund an EOA to be used as the transaction sender."""
    return pre.fund_eoa()


@pytest.fixture
def gas_measure_contract(pre: Alloc):
    """Deploys a simple contract to call ModExp and store its success."""
    # TODO: fix the gas accounting
    measured_code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        0,
        Op.CALL(
            address=Spec.MODEXP_ADDRESS,
            value=0,
            args_offset=0,
            args_size=Op.CALLDATASIZE,
            ret_offset=0,
            ret_size=0x80,
        ),
    )
    return pre.deploy_contract(measured_code)


@pytest.fixture
def base(base_length, request):
    """Generate base bytes with the specified length."""
    return b"\xff" * base_length  # arbitrary bytes


@pytest.fixture
def modulus(modulus_length, request):
    """Generate modulus bytes with the specified length."""
    return b"\xff" * modulus_length  # arbitrary bytes


@pytest.fixture
def exponent_bytes(exponent_length, exponent, request):
    """Convert the integer exponent to bytes with the specified length."""
    # Truncate to the lowest exponent length bytes to avoid overflow
    mask = (1 << (8 * exponent_length)) - 1
    truncated = exponent & mask
    return truncated.to_bytes(exponent_length, byteorder="big")


@pytest.fixture
def expected_gas(
    base: bytes,
    exponent_bytes: bytes,
    modulus: bytes,
) -> int:
    """Return expected gas consumption of the ModExp precompile."""
    base_length = len(base)
    exponent_length = len(exponent_bytes)
    modulus_length = len(modulus)
    exponent_value = int.from_bytes(exponent_bytes, byteorder="big")
    # return Spec.calculate_new_gas_cost(
    # base_length, modulus_length, exponent_length, exponent_value
    # )
    # Temporarily use the old (EIP-2565) gas schedule
    return Spec.calculate_old_gas_cost(
        base_length, modulus_length, exponent_length, exponent_value
    )


@pytest.fixture
def modexp_input_data(base: bytes, exponent_bytes: bytes, modulus: bytes) -> bytes:
    """ModExp input data."""
    return Spec.create_modexp_input(base, exponent_bytes, modulus)


@pytest.fixture
def tx(
    sender: EOA,
    gas_measure_contract: Address,
    modexp_input_data: bytes,
) -> Transaction:
    """Transaction to measure gas consumption of the ModExp precompile."""
    return Transaction(
        sender=sender,
        to=gas_measure_contract,
        data=modexp_input_data,
        gas_limit=100_000,
    )


@pytest.fixture
def post(
    gas_measure_contract: Address,
    expected_gas: int,
) -> Dict[Address, Dict[str, Storage]]:
    """Return expected post state."""
    return {
        gas_measure_contract: Account(
            storage={
                0: 1,
            }
        )
    }
