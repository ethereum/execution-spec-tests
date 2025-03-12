"""Tests supported precompiled contracts."""

from typing import Any, Iterator

import pytest

from ethereum_test_forks.base_fork import Fork
from ethereum_test_forks.forks.forks import Cancun, Prague
from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.types import EOA
from ethereum_test_vm.bytecode import Bytecode

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-2929.md"
REFERENCE_SPEC_VERSION = "0e11417265a623adb680c527b15d0cb6701b870b"

UPPER_BOUND = 0xFF
NUM_UNSUPPORTED_PRECOMPILES = 8


def contract_bytecode(**call_kwargs) -> Bytecode:
    """Generate bytecode for the contract to be tested."""
    return (
        Op.GAS
        + Op.CALL(**call_kwargs)
        + Op.POP
        + Op.SUB(Op.SWAP1, Op.GAS)
        + Op.GAS
        + Op.CALL(**call_kwargs)
        + Op.POP
        + Op.SUB(Op.SWAP1, Op.GAS)
        + Op.SWAP1
        + Op.SSTORE(0, Op.SUB)
        + Op.STOP
    )


def initial_setup_bytecode(address: EOA) -> Bytecode:
    """Generate bytecode for the initial setup to be tested."""
    return (
        Op.MSTORE(0, 0) + Op.MSTORE(0x100, 0xDEADBEEF) + Op.CALL(address=address, value=1) + Op.POP
    )


def call_addresses_and_expected_output(fork: Fork) -> Iterator[Any]:
    """
    Yield the addresses of precompiled contracts and their support status for a given fork.

    Args:
        fork (Fork): The fork instance containing precompiled contract information.

    Yields:
        Iterator[Any]: A pytest ParameterSet containing the address in hexadecimal format and a
            boolean indicating whether the address is a supported precompile.

    """
    supported_precompiles = fork.precompiles()

    num_unsupported = NUM_UNSUPPORTED_PRECOMPILES
    for address in range(1, UPPER_BOUND + 1):
        if address in supported_precompiles:
            _address = hex(address)
            precompile_exists = True
            yield pytest.param(
                _address,
                precompile_exists,
                id=f"address_{_address}_precompile_{precompile_exists}",
            )
        elif num_unsupported > 0:
            # Check unsupported precompiles up to NUM_UNSUPPORTED_PRECOMPILES
            _address = hex(address)
            precompile_exists = False
            yield pytest.param(
                _address,
                precompile_exists,
                id=f"address_{_address}_precompile_{precompile_exists}",
            )
            num_unsupported -= 1


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize_by_fork("address,precompile_exists", call_addresses_and_expected_output)
def test_call_params_value_0(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    address: str,
    precompile_exists: int,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode(address=address),
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    expected_gas_cost_change = hex(0x0)
    if not precompile_exists:
        expected_gas_cost_change = hex(0x09C4)
    elif fork == Cancun and address in ["0x9", "0xa"]:
        expected_gas_cost_change = hex(0xDEADBEEF)
    elif fork == Prague and address in [
        "0x9",
        "0xa",
        "0xb",
        "0xc",
        "0xd",
        "0xe",
        "0xf",
        "0x10",
        "0x11",
    ]:
        expected_gas_cost_change = hex(0xDEADBEEF)

    post = {account: Account(storage={0: expected_gas_cost_change})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize_by_fork("address,precompile_exists", call_addresses_and_expected_output)
def test_call_params_value_1(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    address: str,
    precompile_exists: int,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0))
        + contract_bytecode(address=address, value=1),
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    expected_gas_cost_change = hex(0x0)
    if not precompile_exists:
        expected_gas_cost_change = hex(0x6B6C)
    elif fork >= Cancun and address in ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7", "0x8"]:
        expected_gas_cost_change = hex(0x61A8)
    elif fork == Prague and address in ["0x9", "0xa"]:
        expected_gas_cost_change = hex(0xDEADBEEF)

    post = {account: Account(storage={0: expected_gas_cost_change})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize_by_fork("address,precompile_exists", call_addresses_and_expected_output)
def test_call_params_value_0_args_size_1(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    address: str,
    precompile_exists: int,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0))
        + contract_bytecode(address=address, args_size=1),
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    expected_gas_cost_change = hex(0x0)
    if not precompile_exists:
        expected_gas_cost_change = hex(0x09C4)
    elif fork >= Cancun and address in ["0x8", "0x9", "0xa"]:
        expected_gas_cost_change = hex(0xDEADBEEF)
    elif fork == Prague and address in [
        "0xb",
        "0xc",
        "0xd",
        "0xe",
        "0xf",
        "0x10",
        "0x11",
    ]:
        expected_gas_cost_change = hex(0xDEADBEEF)

    post = {account: Account(storage={0: expected_gas_cost_change})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize_by_fork("address,precompile_exists", call_addresses_and_expected_output)
def test_call_params_value_1_args_size_1(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    address: str,
    precompile_exists: int,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0))
        + contract_bytecode(address=address, value=1, args_size=1),
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    expected_gas_cost_change = hex(0x0)
    if not precompile_exists:
        expected_gas_cost_change = hex(0x6B6C)
    elif fork >= Cancun and address in ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7"]:
        expected_gas_cost_change = hex(0x61A8)
    elif fork == Cancun and address in ["0x8", "0x9", "0xa"]:
        expected_gas_cost_change = hex(0xDEADBEEF)

    post = {account: Account(storage={0: expected_gas_cost_change})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize_by_fork("address,precompile_exists", call_addresses_and_expected_output)
def test_call_params_value_0_output_size_1(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    address: str,
    precompile_exists: int,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0))
        + contract_bytecode(address=address, output_size=1),
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    expected_gas_cost_change = hex(0x0)
    if not precompile_exists:
        expected_gas_cost_change = hex(0x9C4)
    elif fork == Cancun and address in ["0x8", "0x9", "0xa"]:
        expected_gas_cost_change = hex(0xDEADBEEF)
    elif fork == Prague and address in [
        "0x9",
        "0xa",
        "0xb",
        "0xc",
        "0xd",
        "0xe",
        "0xf",
        "0x10",
        "0x11",
    ]:
        expected_gas_cost_change = hex(0xDEADBEEF)

    post = {account: Account(storage={0: expected_gas_cost_change})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize_by_fork("address,precompile_exists", call_addresses_and_expected_output)
def test_call_params_value_1_output_size_1(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    address: str,
    precompile_exists: int,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0))
        + contract_bytecode(address=address, value=1, output_size=1),
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    expected_gas_cost_change = hex(0x0)
    if not precompile_exists:
        expected_gas_cost_change = hex(0x6B6C)
    elif fork >= Cancun and address in ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7", "0x8"]:
        expected_gas_cost_change = hex(0x61A8)
    elif fork == Cancun and address in ["0x9", "0xa"]:
        expected_gas_cost_change = hex(0xDEADBEEF)
    elif fork == Prague and address in [
        "0xb",
        "0xc",
        "0xd",
        "0xe",
        "0xf",
        "0x10",
        "0x11",
    ]:
        expected_gas_cost_change = hex(0xDEADBEEF)

    post = {account: Account(storage={0: expected_gas_cost_change})}

    state_test(env=env, pre=pre, post=post, tx=tx)
