"""Test ACL Transaction Source Code Examples."""

from typing import List

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    AccessList,
    Account,
    Address,
    Alloc,
    Environment,
    Hash,
    StateTestFiller,
    Transaction,
    TransactionException,
)
from ethereum_test_tools import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-2930.md"
REFERENCE_SPEC_VERSION = "c9db53a936c5c9cbe2db32ba0d1b86c4c6e73534"


@pytest.mark.parametrize(
    "access_lists",
    [
        pytest.param(
            [],
            id="empty_access_list",
        ),
        pytest.param(
            [AccessList(address=Address(0), storage_keys=[])],
            id="single_address_multiple_no_storage_keys",
        ),
        pytest.param(
            [AccessList(address=Address(0), storage_keys=[Hash(0)])],
            id="single_address_single_storage_key",
        ),
        pytest.param(
            [AccessList(address=Address(0), storage_keys=[Hash(0), Hash(1)])],
            id="single_address_multiple_storage_keys",
        ),
        pytest.param(
            [
                AccessList(address=Address(0), storage_keys=[Hash(0), Hash(1)]),
                AccessList(address=Address(1), storage_keys=[]),
            ],
            id="multiple_addresses_second_address_no_storage_keys",
        ),
        pytest.param(
            [
                AccessList(address=Address(0), storage_keys=[Hash(0), Hash(1)]),
                AccessList(address=Address(1), storage_keys=[Hash(0)]),
            ],
            id="multiple_addresses_second_address_single_storage_key",
        ),
        pytest.param(
            [
                AccessList(address=Address(0), storage_keys=[Hash(0), Hash(1)]),
                AccessList(address=Address(1), storage_keys=[Hash(0), Hash(1)]),
            ],
            id="multiple_addresses_second_address_multiple_storage_keys",
        ),
        pytest.param(
            [
                AccessList(address=Address(0), storage_keys=[]),
                AccessList(address=Address(1), storage_keys=[Hash(0), Hash(1)]),
            ],
            id="multiple_addresses_first_address_no_storage_keys",
        ),
        pytest.param(
            [
                AccessList(address=Address(0), storage_keys=[Hash(0)]),
                AccessList(address=Address(1), storage_keys=[Hash(0), Hash(1)]),
            ],
            id="multiple_addresses_first_address_single_storage_key",
        ),
        pytest.param(
            [
                AccessList(address=Address(0), storage_keys=[]),
                AccessList(address=Address(1), storage_keys=[]),
            ],
            id="repeated_address_no_storage_keys",
        ),
        pytest.param(
            [
                AccessList(address=Address(0), storage_keys=[Hash(0)]),
                AccessList(address=Address(0), storage_keys=[Hash(1)]),
            ],
            id="repeated_address_single_storage_key",
        ),
        pytest.param(
            [
                AccessList(address=Address(0), storage_keys=[Hash(0), Hash(1)]),
                AccessList(address=Address(0), storage_keys=[Hash(0), Hash(1)]),
            ],
            id="repeated_address_multiple_storage_keys",
        ),
    ],
)
@pytest.mark.parametrize(
    "enough_gas",
    [
        pytest.param(True, id="enough_gas"),
        pytest.param(False, id="not_enough_gas", marks=pytest.mark.exception_test),
    ],
)
@pytest.mark.valid_from("Berlin")
def test_access_list(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    access_lists: List[AccessList],
    enough_gas: bool,
):
    """Test type 1 transaction."""
    env = Environment()

    contract_start_balance = 3
    contract_address = pre.deploy_contract(
        Op.STOP,
        balance=contract_start_balance,
    )
    sender = pre.fund_eoa()
    tx_value = 1
    pre.fund_address(sender, tx_value)

    contract_creation = False
    tx_data = b""

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()

    tx_exception = None
    tx_gas_limit = intrinsic_gas_calculator(
        calldata=tx_data,
        contract_creation=contract_creation,
        access_list=access_lists,
    )
    if not enough_gas:
        tx_gas_limit -= 1
        tx_exception = TransactionException.INTRINSIC_GAS_TOO_LOW

    tx = Transaction(
        ty=1,
        chain_id=0x01,
        data=tx_data,
        to=contract_address,
        value=tx_value,
        gas_limit=tx_gas_limit,
        access_list=access_lists,
        protected=True,
        sender=sender,
        error=tx_exception,
    )

    post = {
        contract_address: Account(
            balance=contract_start_balance + 1 if enough_gas else contract_start_balance,
            nonce=1,
        ),
        sender: Account(
            nonce=1 if enough_gas else 0,
        ),
    }
    state_test(env=env, pre=pre, post=post, tx=tx)
