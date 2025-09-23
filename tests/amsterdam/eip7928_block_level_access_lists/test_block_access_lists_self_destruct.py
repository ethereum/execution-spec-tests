"""Tests for effects of `SELFDESTRUCT` on EIP-7928 ."""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
    compute_create_address,
)
from ethereum_test_types.block_access_list import (
    BalAccountExpectation,
    BalBalanceChange,
    BalCodeChange,
    BalNonceChange,
    BlockAccessListExpectation,
)
from ethereum_test_vm import Opcodes as Op

from .spec import ref_spec_7928

REFERENCE_SPEC_GIT_PATH = ref_spec_7928.git_path
REFERENCE_SPEC_VERSION = ref_spec_7928.version


pytestmark = pytest.mark.valid_from("Amsterdam")


@pytest.mark.parametrize(
    "self_destruct_in_same_tx",
    [True, False],
    ids=["self_destruct_in_same_tx", "self_destruct_in_a_new_tx"],
)
def test_bal_self_destruct(
    pre: Alloc,
    blockchain_test: BlockchainTestFiller,
    self_destruct_in_same_tx: bool,
):
    """Ensure BAL captures balance changes caused by `SELFDESTRUCT`."""
    alice = pre.fund_eoa()
    bob = pre.fund_eoa(amount=0)

    selfdestruct_code = Op.SELFDESTRUCT(bob)
    # A pre existing self-destruct contract
    kaboom = pre.deploy_contract(code=selfdestruct_code)

    if self_destruct_in_same_tx:
        # The goal is to create a self-destructing contract in the same
        # transaction to trigger deletion of code as per EIP-6780.
        # The factory contract below creates a new self-destructing
        # contract and calls it in this transaction.

        bytecode_size = len(selfdestruct_code)
        factory_bytecode = (
            # Clone template memory
            Op.EXTCODECOPY(kaboom, 0, 0, bytecode_size)
            # Fund 100 wei and deploy the clone
            + Op.CREATE(100, 0, bytecode_size)
            # Call the clone, which self-destructs
            + Op.CALL(50_000, Op.DUP6, 0, 0, 0, 0, 0)
            + Op.STOP
        )

        factory = pre.deploy_contract(code=factory_bytecode)
        kaboom_same_tx = compute_create_address(address=factory, nonce=1)

    tx = Transaction(
        sender=alice,
        to=factory if self_destruct_in_same_tx else kaboom,
        value=100,
        gas_limit=1_000_000,
    )

    # Determine which account was destructed
    self_destructed_account = kaboom_same_tx if self_destruct_in_same_tx else kaboom

    block = Block(
        txs=[tx],
        expected_block_access_list=BlockAccessListExpectation(
            account_expectations={
                alice: BalAccountExpectation(
                    nonce_changes=[BalNonceChange(tx_index=1, post_nonce=1)],
                ),
                bob: BalAccountExpectation(
                    balance_changes=[BalBalanceChange(tx_index=1, post_balance=100)]
                ),
                self_destructed_account: BalAccountExpectation(
                    balance_changes=[BalBalanceChange(tx_index=1, post_balance=0)],
                    # Expect code to be cleared if self-destructed in same transaction.
                    code_changes=[BalCodeChange(tx_index=1, new_code="")]
                    if self_destruct_in_same_tx
                    else [],
                ),
            }
        ),
    )

    post = {
        alice: Account(nonce=1),
        bob: Account(balance=100),
        kaboom: Account(balance=0, code=selfdestruct_code),
    }

    # If the account was NOT self-destructed in the same contract,
    # we expect the account code to be present and its balance to be 0.
    if not self_destruct_in_same_tx:
        post[kaboom] = Account(balance=0, code=pre[kaboom].code)  # type: ignore

    blockchain_test(
        pre=pre,
        blocks=[block],
        post=post,
    )
