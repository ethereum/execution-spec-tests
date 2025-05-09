"""Shared pytest definitions for EIP-7883 tests."""

from typing import Dict, Tuple

import pytest

from ethereum_test_tools import (
    EOA,
    Account,
    Address,
    Alloc,
    Bytecode,
    CodeGasMeasure,
    Environment,
    Storage,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import parse_modexp_input
from .spec import Spec


@pytest.fixture
def env() -> Environment:
    """Environment fixture."""
    return Environment()


@pytest.fixture
def parsed_input(input_data: bytes) -> Tuple[bytes, bytes, bytes, int]:
    """Parse the ModExp input data."""
    return parse_modexp_input(input_data)


@pytest.fixture
def base(parsed_input: Tuple[bytes, bytes, bytes, int]) -> bytes:
    """Get the base value from the parsed input."""
    return parsed_input[0]


@pytest.fixture
def exponent_bytes(parsed_input: Tuple[bytes, bytes, bytes, int]) -> bytes:
    """Get the exponent bytes from the parsed input."""
    return parsed_input[1]


@pytest.fixture
def modulus(parsed_input: Tuple[bytes, bytes, bytes, int]) -> bytes:
    """Get the modulus value from the parsed input."""
    return parsed_input[2]


@pytest.fixture
def exponent(parsed_input: Tuple[bytes, bytes, bytes, int]) -> int:
    """Get the exponent value from the parsed input."""
    return parsed_input[3]


@pytest.fixture
def sender(pre: Alloc) -> EOA:
    """Create and fund an EOA to be used as the transaction sender."""
    return pre.fund_eoa()


@pytest.fixture
def call_opcode() -> Op:
    """Return default call used to call the precompile."""
    return Op.CALL


@pytest.fixture
def modexp_call_code(call_opcode: Op, input_data: bytes) -> Bytecode:
    """Create bytecode to call the ModExp precompile."""
    call_code = call_opcode(
        address=Spec.MODEXP_ADDRESS,
        value=0,
        args_offset=0,
        args_size=Op.CALLDATASIZE,
        ret_offset=0,
        ret_size=0x80,
    )
    call_code += Op.SSTORE(0, Op.ISZERO(Op.ISZERO))
    return call_code


@pytest.fixture
def gas_measure_contract(pre: Alloc, modexp_call_code: Bytecode) -> Address:
    """Deploys a contract that measures ModExp gas consumption."""
    calldata_copy = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
    measured_code = CodeGasMeasure(
        code=calldata_copy + modexp_call_code,
        overhead_cost=12,  # TODO: Calculate overhead cost
        extra_stack_items=0,
        sstore_key=1,
        stop=True,
    )
    return pre.deploy_contract(measured_code)


@pytest.fixture
def precompile_gas_modifier() -> int:
    """Modify the gas passed to the precompile, for negative testing purposes."""
    return 0


@pytest.fixture
def precompile_gas(base: bytes, exponent_bytes: bytes, modulus: bytes, expected_gas: int) -> int:
    """Calculate gas cost for the ModExp precompile and verify it matches expected gas."""
    base_length = len(base)
    exponent_length = len(exponent_bytes)
    modulus_length = len(modulus)
    exponent_value = int.from_bytes(exponent_bytes, byteorder="big")
    calculated_gas = Spec.calculate_new_gas_cost(
        base_length, modulus_length, exponent_length, exponent_value
    )
    assert (
        calculated_gas == expected_gas
    ), f"Calculated gas {calculated_gas} != Vector gas {expected_gas}"
    return calculated_gas


@pytest.fixture
def modexp_input_data(input_data: bytes) -> bytes:
    """ModExp input data, directly use the input from the test vector."""
    return input_data


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
        gas_limit=1_000_000,
    )


@pytest.fixture
def post(
    gas_measure_contract: Address,
    precompile_gas: int,
) -> Dict[Address, Dict[str, Storage]]:
    """Return expected post state with gas consumption check."""
    return {
        gas_measure_contract: Account(
            storage={
                0: 1,  # Call should succeed
                1: precompile_gas,
            }
        )
    }
