"""
abstract: Tests zkEVMs worst-case block scenarios.
    Tests zkEVMs worst-case block scenarios.

Tests running worst-case block scenarios for zkEVMs.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    Transaction,
)


@pytest.fixture
def iteration_count(fork: Fork):
    """Calculate the number of iterations based on the gas limit and intrinsic cost."""
    intrinsic_cost = fork.transaction_intrinsic_cost_calculator()
    return Environment().gas_limit // intrinsic_cost()


@pytest.fixture
def transfer_amount():
    """Ether to transfer in each transaction."""
    return 1


@pytest.fixture
def eth_transfer_cost(fork: Fork):
    """Transaction gas limit."""
    intrinsic_cost = fork.transaction_intrinsic_cost_calculator()
    return intrinsic_cost()


@pytest.fixture
def ether_transfer_case(
    request,
    pre: Alloc,
    iteration_count: int,
    transfer_amount: int,
    eth_transfer_cost: int,
):
    """Generate the test parameters based on the case ID."""
    case_id = request.param

    senders = [pre.fund_eoa() for _ in range(iteration_count)]
    receivers = [pre.fund_eoa(0) for _ in range(iteration_count)]

    single_sender = pre.fund_eoa()
    single_receiver = pre.fund_eoa(0)

    if case_id == "a_to_a":
        """Sending to self."""
        total_balance = pre._eoa_fund_amount_default - eth_transfer_cost * iteration_count * 0x0A
        sender_list = [single_sender for _ in range(iteration_count)]
        receiver_list = [single_sender for _ in range(iteration_count)]
        post = {single_sender: Account(balance=total_balance)}

    elif case_id == "a_to_b":
        """One sender → one receiver."""
        sender_list = [single_sender for _ in range(iteration_count)]
        receiver_list = [single_receiver for _ in range(iteration_count)]
        post = {single_receiver: Account(balance=transfer_amount * iteration_count)}

    elif case_id == "diff_acc_to_b":
        """Multiple senders → one receiver."""
        sender_list = senders.copy()
        receiver_list = [single_receiver for _ in range(iteration_count)]
        post = {single_receiver: Account(balance=transfer_amount * iteration_count)}

    elif case_id == "a_to_diff_acc":
        """One sender → multiple receivers."""
        sender_list = [single_sender for _ in range(iteration_count)]
        receiver_list = receivers.copy()
        post = {receiver: Account(balance=transfer_amount) for receiver in receivers}

    elif case_id == "diff_acc_to_diff_acc":
        """Multiple senders → multiple receivers."""
        sender_list = senders.copy()
        receiver_list = receivers.copy()
        post = {receiver: Account(balance=transfer_amount) for receiver in receivers}

    else:
        raise ValueError(f"Unknown case: {case_id}")

    return sender_list, receiver_list, post


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "ether_transfer_case",
    ["a_to_a", "a_to_b", "diff_acc_to_b", "a_to_diff_acc", "diff_acc_to_diff_acc"],
    indirect=True,
)
def test_block_full_of_ether_transfers(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    ether_transfer_case,
    iteration_count: int,
    transfer_amount: int,
    eth_transfer_cost: int,
):
    """
    Single test for ether transfer scenarios.

    Scenarios:
    - a_to_a: one sender → one sender
    - a_to_b: one sender → one receiver
    - diff_acc_to_b: multiple senders → one receiver
    - a_to_diff_acc: one sender → multiple receivers
    - diff_acc_to_diff_acc: multiple senders → multiple receivers
    """
    sender_list, receiver_list, post = ether_transfer_case

    blocks = []
    for i in range(iteration_count):
        tx = Transaction(
            to=receiver_list[i],
            value=transfer_amount,
            gas_limit=eth_transfer_cost,
            sender=sender_list[i],
        )
        blocks.append(Block(txs=[tx]))

    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        post=post,
        blocks=blocks,
        exclude_full_post_state_in_output=True,
    )
