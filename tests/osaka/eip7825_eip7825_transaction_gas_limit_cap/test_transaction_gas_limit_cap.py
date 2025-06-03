"""
abstract: Tests [EIP-7825 Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825)
    Test cases for [EIP-7825 Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825)].
"""

import pytest

from ethereum_test_tools import Account, Alloc, Environment, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7825.md"
REFERENCE_SPEC_VERSION = "47cbfed315988c0bd4d10002c110ae402504cd94"


@pytest.mark.valid_from("Osaka")
def test_transaction_gas_limit_cap(state_test: StateTestFiller, pre: Alloc):
    """
    TODO: Enter a one-line test summary here.

    TODO: (Optional) Enter a more detailed test function description here.
    """
    env = Environment()

    # TODO: Delete this explanation.
    # In this demo test, the pre-state contains one EOA and one very simple
    # smart contract. The EOA, `sender`, executes the smart contract, which
    # simply sets the value of the contract's storage slot.
    # The (non-exhaustive) post-state verifies that the storage slot was set
    # correctly - this is checked when filling the test.
    #
    # One gotcha is ensuring that the transaction `gas_limit` is set high
    # enough to cover the gas cost of the contract execution.

    storage_slot: int = 1

    # TODO: Modify pre-state allocations here.
    sender = pre.fund_eoa()
    contract_address = pre.deploy_contract(
        code=Op.SSTORE(storage_slot, 0x2) + Op.STOP,
        storage={storage_slot: 0x1},
    )

    tx = Transaction(
        to=contract_address,
        gas_limit=100000000,
        data=b"",
        value=0,
        sender=sender,
    )

    # TODO: Modify post-state allocations here.
    post = {contract_address: Account(storage={storage_slot: 0x2})}

    state_test(env=env, pre=pre, post=post, tx=tx)
