"""
abstract: Tests [EIP-7825 Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825)
    Test cases for [EIP-7825 Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825)].
"""

from typing import List, Tuple

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    AuthorizationTuple,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
    TransactionException,
    add_kzg_version,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7825.md"
REFERENCE_SPEC_VERSION = "47cbfed315988c0bd4d10002c110ae402504cd94"

TX_GAS_LIMIT = 30_000_000
BLOB_COMMITMENT_VERSION_KZG = 1


def tx_gas_limit_cap_tests(fork: Fork) -> List[Tuple[int, TransactionException | None]]:
    """
    Return a list of tests for transaction gas limit cap parametrized for each different
    fork.
    """
    fork_tx_gas_limit_cap = fork.transaction_gas_limit_cap()
    if fork_tx_gas_limit_cap is None:
        # Use a default value for forks that don't have a transaction gas limit cap
        return [
            pytest.param(TX_GAS_LIMIT + 1, None, id="tx_gas_limit_cap_none"),
        ]

    return [
        pytest.param(
            fork_tx_gas_limit_cap + 1,
            TransactionException.GAS_LIMIT_EXCEEDS_MAXIMUM,
            id="tx_gas_limit_cap_exceeds_maximum",
            marks=pytest.mark.exception_test,
        ),
        pytest.param(fork_tx_gas_limit_cap, None, id="tx_gas_limit_cap_none"),
    ]


@pytest.mark.parametrize_by_fork("tx_gas_limit,error", tx_gas_limit_cap_tests)
@pytest.mark.with_all_tx_types
@pytest.mark.valid_from("Prague")
def test_transaction_gas_limit_cap(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
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

    # Add extra required fields based on transaction type
    if tx_type >= 1:
        # Type 1: EIP-2930 Access List Transaction
        tx_kwargs["access_list"] = [
            {
                "address": contract_address,
                "storage_keys": [0],
            }
        ]
    if tx_type == 3:
        # Type 3: EIP-4844 Blob Transaction
        tx_kwargs["max_fee_per_blob_gas"] = fork.min_base_fee_per_blob_gas()
        tx_kwargs["blob_versioned_hashes"] = add_kzg_version([0], BLOB_COMMITMENT_VERSION_KZG)
    elif tx_type == 4:
        # Type 4: EIP-7702 Set Code Transaction
        signer = pre.fund_eoa(amount=0)
        tx_kwargs["authorization_list"] = [
            AuthorizationTuple(
                signer=signer,
                address=Address(0),
                nonce=0,
            )
        ]

    tx = Transaction(**tx_kwargs)
    post = {contract_address: Account(storage=storage if error is None else {})}

    state_test(env=env, pre=pre, post=post, tx=tx)
