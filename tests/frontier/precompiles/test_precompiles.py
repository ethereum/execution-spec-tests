"""Tests supported precompiled contracts."""

from typing import Iterator, Tuple

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.code.generators import Conditional
from ethereum_test_tools.vm.opcode import Opcodes as Op

UPPER_BOUND = 0xFF
NUM_UNSUPPORTED_PRECOMPILES = 1


def precompile_addresses(fork: Fork) -> Iterator[Tuple[str, bool]]:
    """
    Yield the addresses of precompiled contracts and their support status for a given fork.

    Args:
        fork (Fork): The fork instance containing precompiled contract information.

    Yields:
        Iterator[Tuple[str, bool]]: A tuple containing the address in hexadecimal format and a
            boolean indicating whether the address is a supported precompile.

    """
    supported_precompiles = fork.precompiles()

    num_unsupported = NUM_UNSUPPORTED_PRECOMPILES
    for address in range(1, UPPER_BOUND + 1):
        if address in supported_precompiles:
            yield (hex(address), True)
        elif num_unsupported > 0:
            # Check unsupported precompiles up to NUM_UNSUPPORTED_PRECOMPILES
            yield (hex(address), False)
            num_unsupported -= 1


@pytest.mark.valid_from("Berlin")
@pytest.mark.parametrize_by_fork("address,precompile_exists", precompile_addresses)
def test_precompiles(
    state_test: StateTestFiller, address: str, precompile_exists: bool, pre: Alloc
):
    """
    Tests the behavior of precompiled contracts in the Ethereum state test.

    Args:
        state_test (StateTestFiller): The state test filler object used to run the test.
        address (str): The address of the precompiled contract to test.
        precompile_exists (bool): A flag indicating whether the precompiled contract exists at the
            given address.
        pre (Alloc): The allocation object used to deploy the contract and set up the initial
            state.

    This test deploys a contract that performs two CALL operations to the specified address and a
    fixed address (0x10000), measuring the gas used for each call. It then stores the difference
    in gas usage in storage slot 0. The test verifies the expected storage value based on
    whether the precompiled contract exists at the given address.

    """
    env = Environment()

    slot_precompile_call_gas = 0x00
    slot_empty_address_call_gas = 0x20

    account = pre.deploy_contract(
        Op.MSTORE(slot_precompile_call_gas, Op.GAS)
        + Op.CALL(
            address=address,
            value=0,
            args_offset=0,
            args_size=32,
            output_offset=32,
            output_size=32,
        )
        + Op.MSTORE(slot_precompile_call_gas, Op.SUB(Op.MLOAD(slot_precompile_call_gas), Op.GAS))
        + Op.MSTORE(slot_empty_address_call_gas, Op.GAS)
        + Op.CALL(
            address=0x10000,
            value=0,
            args_offset=0,
            args_size=32,
            output_offset=32,
            output_size=32,
        )
        + Op.MSTORE(
            slot_empty_address_call_gas, Op.SUB(Op.MLOAD(slot_empty_address_call_gas), Op.GAS)
        )
        + Op.SSTORE(
            0,
            Op.LT(
                Conditional(
                    condition=Op.GT(
                        Op.MLOAD(slot_precompile_call_gas), Op.MLOAD(slot_empty_address_call_gas)
                    ),
                    if_true=Op.SUB(
                        Op.MLOAD(slot_precompile_call_gas), Op.MLOAD(slot_empty_address_call_gas)
                    ),
                    if_false=Op.SUB(
                        Op.MLOAD(slot_empty_address_call_gas), Op.MLOAD(slot_precompile_call_gas)
                    ),
                ),
                0x1A4,
            ),
        )
        + Op.STOP,
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
    post = {account: Account(storage={0: "0x00" if precompile_exists else "0x01"})}

    state_test(env=env, pre=pre, post=post, tx=tx)
