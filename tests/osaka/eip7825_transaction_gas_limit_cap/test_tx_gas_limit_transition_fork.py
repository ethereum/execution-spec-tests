"""
abstract: Tests [EIP-7825 Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825)
    Test cases for [EIP-7825 Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825)].
"""

import pytest

from ethereum_test_checklists import EIPChecklist
from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
    TransactionException,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .spec import ref_spec_7825

REFERENCE_SPEC_GIT_PATH = ref_spec_7825.git_path
REFERENCE_SPEC_VERSION = ref_spec_7825.version


@EIPChecklist.ModifiedTransactionValidityConstraint.Test.ForkTransition.AcceptedBeforeFork()
@EIPChecklist.ModifiedTransactionValidityConstraint.Test.ForkTransition.RejectedBeforeFork()
@EIPChecklist.ModifiedTransactionValidityConstraint.Test.ForkTransition.AcceptedAfterFork()
@EIPChecklist.ModifiedTransactionValidityConstraint.Test.ForkTransition.RejectedAfterFork()
@pytest.mark.valid_at_transition_to("Osaka", subsequent_forks=True)
@pytest.mark.exception_test
def test_transaction_gas_limit_cap_at_transition(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
):
    """
    Test transaction gas limit cap behavior at the Osaka transition.

    Before timestamp 15000: No gas limit cap (transactions with gas > 2^24 are valid)
    At/after timestamp 15000: Gas limit cap of 2^24 is enforced
    """
    contract_address = pre.deploy_contract(
        code=Op.SSTORE(Op.TIMESTAMP, Op.ADD(Op.SLOAD(0), 1)) + Op.STOP,
    )

    pre_cap = fork.transaction_gas_limit_cap(timestamp=14_999)
    post_cap = fork.transaction_gas_limit_cap(timestamp=15_000)
    assert post_cap is not None, "Post cap should not be None"

    pre_cap = pre_cap if pre_cap else post_cap + 1

    assert post_cap <= pre_cap, (
        "Post cap should be less than or equal to pre cap, test needs update"
    )

    # Before fork activation
    high_gas_tx_before_fork = Transaction(
        ty=0,  # Legacy transaction
        to=contract_address,
        gas_limit=pre_cap,
        sender=pre.fund_eoa(),
    )

    cap_tx_before_fork = Transaction(
        ty=0,  # Legacy transaction
        to=contract_address,
        gas_limit=post_cap,
        sender=pre.fund_eoa(),
    )

    post_cap_tx_error = TransactionException.GAS_LIMIT_EXCEEDS_MAXIMUM

    # After fork activation
    high_gas_tx_after_fork = Transaction(
        ty=0,  # Legacy transaction
        to=contract_address,
        gas_limit=pre_cap,
        sender=pre.fund_eoa(),
        error=post_cap_tx_error,
    )

    cap_tx_after_fork = Transaction(
        ty=0,  # Legacy transaction
        to=contract_address,
        gas_limit=post_cap,
        sender=pre.fund_eoa(),
    )

    blocks = []

    # Before transition (timestamp < 15000): high gas transaction should succeed
    blocks.append(
        Block(
            timestamp=14_999,
            txs=[high_gas_tx_before_fork, cap_tx_before_fork],
        )
    )

    # At transition (timestamp = 15000): high gas transaction should fail
    blocks.append(
        Block(
            timestamp=15_000,
            txs=[
                cap_tx_after_fork,
                high_gas_tx_after_fork,
            ],
            exception=post_cap_tx_error,
        )
    )

    # Post state: storage should be updated by successful transactions
    post = {
        contract_address: Account(
            storage={
                14_999: 1,  # Set by first transaction (before transition)
                15_000: 0,  # Set by second transaction (at transition)
            }
        )
    }

    blockchain_test(pre=pre, blocks=blocks, post=post)
