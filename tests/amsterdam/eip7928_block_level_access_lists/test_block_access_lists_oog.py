"""
Tests for EIP-7928 Block Access Lists with out-of-gas scenarios.

Block access lists (BAL) are generated via a client's state tracing journal. Residual journal
entries may persist when opcodes run out of gas, resulting in a bloated BAL payload.

Issues identified in:
https://github.com/paradigmxyz/reth/issues/17765
https://github.com/bluealloy/revm/pull/2903

These tests ensure out-of-gas operations are not recorded in BAL, preventing consensus issues.
"""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
    TransactionException,
)
from ethereum_test_types.block_access_list import (
    BlockAccessListExpectation,
)

from .spec import ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version


@pytest.mark.valid_from("Amsterdam")
@pytest.mark.exception_test
def test_bal_oog_intrinsic(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    fork,
):
    """Ensure BAL correctly handles intrinsic out-of-gas failure."""
    alice = pre.fund_eoa(amount=1_000_000)
    bob = pre.fund_eoa(amount=100)

    # Calculate exact intrinsic gas cost
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    intrinsic_gas_cost = intrinsic_gas_calculator(
        calldata=b"",
        contract_creation=False,
        access_list=[],
    )

    # Set gas limit below intrinsic cost to force immediate failure
    insufficient_gas = intrinsic_gas_cost - 1

    tx = Transaction(
        sender=alice,
        to=bob,
        value=100,
        gas_limit=insufficient_gas,
        error=TransactionException.INTRINSIC_GAS_TOO_LOW,
    )

    # Transaction should fail
    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={alice: None, bob: None}
            # Empty - intrinsic gas failures don't create BAL entries
        ),
        exception=TransactionException.INTRINSIC_GAS_TOO_LOW,
    )

    blockchain_test(
        pre=pre,
        blocks=[block],
        post={
            # Alice's nonce should not increment on intrinsic gas failure
            alice: Account(nonce=0, balance=1_000_000),
            # Consequently, bob's balance must not change
            bob: Account(balance=100),
        },
    )
