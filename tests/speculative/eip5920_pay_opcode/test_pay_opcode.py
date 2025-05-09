"""
abstract: Tests [EIP-5920: PAY opcode](https://eips.ethereum.org/EIPS/eip-5920)
    Test cases for [EIP-5920: PAY opcode](https://eips.ethereum.org/EIPS/eip-5920).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from . import PAY_OPCODE_FORK_NAME
from .spec import ref_spec_5920

REFERENCE_SPEC_GIT_PATH = ref_spec_5920.git_path
REFERENCE_SPEC_VERSION = ref_spec_5920.version

pytestmark = pytest.mark.valid_from(PAY_OPCODE_FORK_NAME)


@pytest.mark.parametrize("initial_contract_balance, initial_recipient_balance", [(10000, 100)])
@pytest.mark.parametrize(
    "transfer_value,success",
    [
        (0, True),
        (1000, True),
        (1000000, False),
    ],
    ids=[
        "zero_value",
        "non_zero_value",
        "insufficient_balance",
    ],
)
def test_basic_transfer(
    state_test: StateTestFiller,
    pre: Alloc,
    initial_contract_balance: int,
    initial_recipient_balance: int,
    transfer_value: int,
    success: bool,
):
    """
    Tests basic transfer functionality of the PAY opcode under various conditions.

    The pytest cases primarily verify the following:
    1. PAY opcode can transfer value to an existing address.
    2. PAY opcode can transfer value to a new address.
    3. PAY opcode fails if the sender's balance is insufficient.
    """
    sender_address = pre.fund_eoa()
    recipient = pre.fund_eoa(initial_recipient_balance)
    contract_address = pre.deploy_contract(
        code=(
            Op.SSTORE(0, Op.SELFBALANCE)  # Contract balance (slot 0)
            + Op.SSTORE(1, Op.BALANCE(recipient))  # Recipient balance (slot 1)
            + Op.SSTORE(
                2,
                # Perform the transfer
                Op.PAY(recipient, transfer_value),
            )  # Success marker (slot 2)
            + Op.SSTORE(3, Op.SELFBALANCE)  # New contract balance (slot 3)
            + Op.SSTORE(4, Op.BALANCE(recipient))  # New recipient balance (slot 4)
        ),
        balance=initial_contract_balance,
    )

    if success:
        expected_storage = {
            0: initial_contract_balance,
            1: initial_recipient_balance,
            2: 1,  # PAY succeeded
            3: initial_contract_balance - transfer_value,
            4: initial_recipient_balance + transfer_value,
        }
        post = {
            contract_address: Account(
                balance=initial_contract_balance - transfer_value, storage=expected_storage
            ),
        }
        # Add recipient to post-state only if a non-zero transfer is made
        if transfer_value > 0:
            post[recipient] = Account(balance=initial_recipient_balance + transfer_value)
    else:
        # Contract execution should abort. Only slot 0 and 1 are written.
        expected_storage = {
            0: initial_contract_balance,
            1: initial_recipient_balance,
            2: 0,  # PAY failed (0)
        }
        # Check balance remains unchanged for both contract and recipient
        post = {
            contract_address: Account(
                balance=initial_contract_balance,
                storage=expected_storage,
            ),
        }

    tx = Transaction(sender=sender_address, to=contract_address, gas_limit=1000000)
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize("initial_contract_balance", [10000])
@pytest.mark.parametrize(
    "transfer_amount,success",
    [
        (0, True),
        (1000, True),
        (20000, False),
    ],
    ids=[
        "zero_value_to_self",
        "non_zero_value_to_self",
        "insufficient_balance_to_self",
    ],
)
def test_transfer_to_self(
    state_test: StateTestFiller,
    pre: Alloc,
    initial_contract_balance: int,
    transfer_amount: int,
    success: bool,
):
    """
    Tests PAY opcode functionality when a contract transfers to itself.

    The pytest cases verify the following:
    1. PAY opcode can transfer zero value to itself.
    2. PAY opcode can transfer non-zero value to itself.
    3. PAY opcode fails if attempted transfer exceeds balance.
    """
    sender_address = pre.fund_eoa()
    contract_address = pre.deploy_contract(
        code=(Op.SSTORE(0, Op.PAY(Op.ADDRESS, transfer_amount))),
        balance=initial_contract_balance,
    )
    post = {
        contract_address: Account(
            balance=initial_contract_balance,
            storage={
                0: 1 if success else 0,
            },
        )
    }
    tx = Transaction(sender=sender_address, to=contract_address, gas_limit=1000000)
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize("initial_contract_balance, transfer_amount", [(10000, 1000)])
@pytest.mark.with_all_precompiles
def test_pay_to_precompile(
    state_test: StateTestFiller,
    pre: Alloc,
    initial_contract_balance: int,
    transfer_amount: int,
    precompile: int,
):
    """
    Tests PAY opcode functionality when a contract transfers to a precompile.

    The pytest cases verify the latter across all precompiles available to the fork the test
    filled for.

    Precompile addresses will always receive the transferred value.
    """
    sender_address = pre.fund_eoa()
    contract_address = pre.deploy_contract(
        code=(
            Op.SSTORE(0, Op.SELFBALANCE)  # Contract balance (slot 0)
            + Op.SSTORE(1, Op.BALANCE(precompile))  # Precompile balance (slot 1)
            + Op.SSTORE(2, Op.PAY(precompile, transfer_amount))  # Success marker (slot 2)
            + Op.SSTORE(3, Op.SELFBALANCE)  # New contract balance (slot 3)
            + Op.SSTORE(4, Op.BALANCE(precompile))  # New precompile balance (slot 4)
        ),
        balance=initial_contract_balance,
    )
    expected_storage = {
        0: initial_contract_balance,
        1: 0,  # Original precompile balance
        2: 1,  # PAY succeeded
        3: initial_contract_balance - transfer_amount,
        4: transfer_amount,  # New precompile balance
    }
    post = {
        contract_address: Account(
            balance=initial_contract_balance - transfer_amount, storage=expected_storage
        ),
        precompile: Account(balance=transfer_amount),
    }

    tx = Transaction(sender=sender_address, to=contract_address, gas_limit=1000000)
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize("initial_contract_balance, transfer_amount", [(10000, 1000)])
def test_pay_invalid_address(
    state_test: StateTestFiller,
    pre: Alloc,
    initial_contract_balance: int,
    transfer_amount: int,
):
    """
    Tests PAY opcode functionality with an invalid address (high 12 bytes non-zero).

    The test verifies that the PAY opcode fails when attempting to pay to an address
    with non-zero high bytes, where the PAY opcode is expected to fail.
    """
    sender_address = pre.fund_eoa()
    invalid_recipient = 0xFFFFFFFFFFFFFFFFFFFFFFFF1234567890123456789012
    contract_address = pre.deploy_contract(
        code=(
            Op.SSTORE(0, Op.PAY(invalid_recipient, transfer_amount))  # Success marker (slot 0)
        ),
        balance=initial_contract_balance,
    )
    post = {
        contract_address: Account(
            balance=initial_contract_balance,
            storage={
                0: 0,  # PAY failed (0)
            },
        )
    }

    tx = Transaction(sender=sender_address, to=contract_address, gas_limit=1000000)
    state_test(env=Environment(), pre=pre, post=post, tx=tx)
