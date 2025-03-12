"""Tests supported precompiled contracts."""

from typing import Callable, Dict

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-2929.md"
REFERENCE_SPEC_VERSION = "0e11417265a623adb680c527b15d0cb6701b870b"

UPPER_BOUND = 0xFF
NUM_UNSUPPORTED_PRECOMPILES = 8


def contract_call_bytecode(address, call_params):
    """Return the bytecode for a contract that measures the gas cost of a CALL operation."""
    return (
        Op.MSTORE(0, 0)  # Pre-expand the memory so the gas costs are exactly the same
        + Op.MSTORE(0x100, 0xDEADBEEF)  # Initialize memory for gas measurement
        + Op.CALL(
            address=0x101157,
            value=1,
            args_offset=0,
            args_size=0,
            output_offset=0,
            output_size=0,
        )  # Call to a fixed address with wei to warm up
        + Op.POP
        + Op.GAS
        + Op.CALL(
            address=address,
            value=call_params["value"],
            args_offset=call_params["args_offset"],
            args_size=call_params["args_size"],
            output_offset=call_params["output_offset"],
            output_size=call_params["output_size"],
        )
        + Op.POP
        + Op.SUB(Op.SWAP1, Op.GAS)
        + Op.GAS
        + Op.CALL(
            address=address,
            value=call_params["value"],
            args_offset=call_params["args_offset"],
            args_size=call_params["args_size"],
            output_offset=call_params["output_offset"],
            output_size=call_params["output_size"],
        )
        + Op.POP
        + Op.SUB(Op.SWAP1, Op.GAS)
        + Op.SWAP1
        + Op.SSTORE(0, Op.SUB)
        + Op.STOP
    )


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "address,expected",
    [
        pytest.param(0x01, 0x00, id="ecrecover_no_gas_cost_difference"),
        pytest.param(0x02, 0x00, id="sha256_no_gas_cost_difference"),
        pytest.param(0x03, 0x00, id="ripemd160_no_gas_cost_difference"),
        pytest.param(0x04, 0x00, id="identity_no_gas_cost_difference"),
        pytest.param(0x05, 0x00, id="modexp_no_gas_cost_difference"),
        pytest.param(0x06, 0x00, id="ecadd_no_gas_cost_difference"),
        pytest.param(0x07, 0x00, id="ecscalar_no_gas_cost_difference"),
        pytest.param(0x08, 0x00, id="ecpairing_no_gas_cost_difference"),
        pytest.param(0x09, 0x00, id="blake2f_no_gas_cost_difference"),
        pytest.param(0x0A, 0x00, id="kzg_point_evaluation_no_gas_cost_difference"),
        pytest.param(0x0B, 0x00, id="bls12_381_g1_add_no_gas_cost_difference"),
        pytest.param(0x0C, 0x00, id="bls12_381_g1_mul_no_gas_cost_difference"),
        pytest.param(0x0D, 0x00, id="bls12_381_g2_add_no_gas_cost_difference"),
        pytest.param(0x0E, 0x00, id="bls12_381_g2_mul_no_gas_cost_difference"),
        pytest.param(0x0F, 0x00, id="bls12_381_pairing_no_gas_cost_difference"),
        pytest.param(0x10, 0x00, id="bls12_381_map_fp_to_g1_no_gas_cost_difference"),
        pytest.param(0x11, 0x00, id="bls12_381_map_fp2_to_g2_no_gas_cost_difference"),
        pytest.param(0x12, 0x09C4, id="no_precompile_gas_cost_decrease"),
    ],
)
@pytest.mark.parametrize(
    "params",
    (
        {"value": 0, "args_offset": 0, "args_size": 0, "output_offset": 0, "output_size": 0},
        {"value": 1, "args_offset": 0, "args_size": 0, "output_offset": 0, "output_size": 0},
        {"value": 0, "args_offset": 0, "args_size": 1, "output_offset": 0, "output_size": 0},
        {"value": 1, "args_offset": 0, "args_size": 1, "output_offset": 0, "output_size": 0},
        {"value": 0, "args_offset": 0, "args_size": 0, "output_offset": 0, "output_size": 1},
        {"value": 1, "args_offset": 0, "args_size": 0, "output_offset": 0, "output_size": 1},
    ),
)
def test_gas_cost_call(
    state_test: StateTestFiller,
    address: int,
    params: Dict[str, int],
    expected: int,
    pre: Alloc,
):
    """Tests gas consumption of a CALL operation to various precompiled contracts."""
    env = Environment()

    account = pre.deploy_contract(
        contract_call_bytecode(address, params),
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    # A high gas cost will result from calling a precompile
    # Expect 0x00 when a precompile exists at the address, 0x01 otherwise
    post = {account: Account(storage={0: expected})}

    state_test(env=env, pre=pre, post=post, tx=tx)


# def test_gas_cost_callcode():
#     pass


# def test_gas_cost_delegatecall():
#     pass


# def test_gas_cost_staticcall():
#     pass
