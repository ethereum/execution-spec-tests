"""
abstract: Tests [EIP-7825 Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825)
    Test cases for [EIP-7825 Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825)].
"""

from typing import List, Tuple

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
    TransactionException,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7825.md"
REFERENCE_SPEC_VERSION = "47cbfed315988c0bd4d10002c110ae402504cd94"

TX_GAS_LIMIT = 30_000_000


def tx_gas_limit_cap_tests(fork: Fork) -> List[Tuple[int, TransactionException | None]]:
    """
    Return a list of tests for transaction gas limit cap parametrized for each different
    fork.
    """
    fork_tx_gas_limit_cap = fork.transaction_gas_limit_cap()
    if fork_tx_gas_limit_cap is None:
        # Use a default value for forks that don't have a transaction gas limit cap
        return [
            (TX_GAS_LIMIT + 1, None),
        ]

    return [
        (fork_tx_gas_limit_cap + 1, TransactionException.GASLIMIT_EXCEEDS_MAXIMUM),
        (fork_tx_gas_limit_cap, None),
    ]


@pytest.mark.parametrize_by_fork("tx_gas_limit,error", tx_gas_limit_cap_tests)
@pytest.mark.with_all_tx_types
@pytest.mark.valid_from("Prague")
def test_transaction_gas_limit_cap(
    state_test: StateTestFiller,
    pre: Alloc,
    tx_gas_limit: int,
    error: TransactionException | None,
    tx_type: int,
):
    """
    TODO: Enter a one-line test summary here.

    TODO: (Optional) Enter a more detailed test function description here.
    """
    env = Environment()

    # TODO: Modify pre-state allocations here.
    sender = pre.fund_eoa()
    storage = Storage()
    contract_address = pre.deploy_contract(
        code=Op.SSTORE(storage.store_next(1), 1) + Op.STOP,
    )

    tx_kwargs = {
        "ty": tx_type,
        "to": contract_address,
        "gas_limit": tx_gas_limit,
        "data": b"",
        "value": 0,
        "sender": sender,
        "error": error,
    }

    tx = Transaction(**tx_kwargs)
    post = {contract_address: Account(storage=storage if error is None else {})}

    state_test(env=env, pre=pre, post=post, tx=tx)
