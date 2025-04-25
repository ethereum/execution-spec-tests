"""Tests supported precompiled contracts."""

from typing import Iterator, Tuple

import pytest

from ethereum_test_forks import (
    Fork,
    get_transition_fork_predecessor,
    get_transition_fork_successor,
)
from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    StateTestFiller,
    Transaction,
)
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

    account = pre.deploy_contract(
        Op.MSTORE(0, 0)  # Pre-expand the memory so the gas costs are exactly the same
        + Op.GAS
        + Op.CALL(
            address=address,
            value=0,
            args_offset=0,
            args_size=32,
            output_offset=32,
            output_size=32,
        )
        + Op.POP
        + Op.SUB(Op.SWAP1, Op.GAS)
        + Op.GAS
        + Op.CALL(
            address=pre.fund_eoa(amount=0),
            value=0,
            args_offset=0,
            args_size=32,
            output_offset=32,
            output_size=32,
        )
        + Op.POP
        + Op.SUB(Op.SWAP1, Op.GAS)
        + Op.SWAP1
        + Op.SUB
        + Op.SSTORE(0, Op.ISZERO)
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


def precompile_addresses_in_successor(fork: Fork) -> Iterator[Tuple[str, bool]]:
    """
    Yield the addresses of precompiled contracts and whether they existed in the parent fork.

    Args:
        fork (Fork): The transition fork instance containing precompiled contract information.

    Yields:
        Iterator[Tuple[str, bool]]: A tuple containing the address in hexadecimal format and a
            boolean indicating whether the address has existed in the predecessor.

    """
    predecessor_precompiles = [
        hex(int.from_bytes(address, byteorder="big"))
        for address in get_transition_fork_predecessor(fork).precompiles()
    ]
    successor_precompiles = [
        hex(int.from_bytes(address, byteorder="big"))
        for address in get_transition_fork_successor(fork).precompiles()
    ]
    for address in successor_precompiles:
        if address in predecessor_precompiles:
            yield address, True
        else:
            yield address, False


@pytest.mark.valid_at_transition_to("Paris", subsequent_forks=True)
@pytest.mark.parametrize_by_fork(
    "address,exists_in_predecessor", precompile_addresses_in_successor
)
def test_precompile_warming(
    blockchain_test: BlockchainTestFiller, address: str, exists_in_predecessor: bool, pre: Alloc
):
    """
    Call BALANCE of a precompile addresses before and after a fork.

    According to EIP-2929, when a transaction begins, accessed_addresses is initialized to include:
    - tx.sender, tx.to
    - and the set of all precompiles

    This test verifies that:
    1. Precompiles that exist in the predecessor fork are always "warm" (lower gas cost)
    2. New precompiles added in a fork are "cold" before the fork and become "warm" after

    """
    sender = pre.fund_eoa()
    call_cost_slot = 0

    code = (
        Op.GAS
        + Op.BALANCE(address)
        + Op.POP
        + Op.SSTORE(call_cost_slot, Op.SUB(Op.SWAP1, Op.GAS))
        + Op.STOP
    )
    before = pre.deploy_contract(code, storage={0: 0xDEADBEEF})
    after = pre.deploy_contract(code, storage={0: 0xDEADBEEF})

    # Block before fork
    blocks = [
        Block(
            timestamp=10000,
            txs=[
                Transaction(
                    sender=sender,
                    to=before,
                    gas_limit=1_000_000,
                )
            ],
        )
    ]

    # Block after fork
    blocks += [
        Block(
            timestamp=20000,
            txs=[
                Transaction(
                    sender=sender,
                    to=after,
                    gas_limit=1_000_000,
                )
            ],
        )
    ]

    if not exists_in_predecessor:
        expected_gas_before = 2607
    else:
        expected_gas_before = 107

    post = {
        before: Account(storage={call_cost_slot: expected_gas_before}),
        after: Account(storage={call_cost_slot: 107}),
    }

    blockchain_test(
        pre=pre,
        post=post,
        blocks=blocks,
    )
