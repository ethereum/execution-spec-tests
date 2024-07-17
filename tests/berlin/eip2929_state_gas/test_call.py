"""
Test the CALL family of instructions after EIP-2929
"""

import pytest

from ethereum_test_tools import Account, Alloc, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Transaction

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-2929.md"
REFERENCE_SPEC_VERSION = "949de3748527504fba8ef5a47cc76413fff85159"


@pytest.mark.valid_from("Berlin")
def test_call_insufficient_balance(state_test: StateTestFiller, pre: Alloc):
    """
    Test a regular CALL to see if it warms the destination with insufficient
    balance.
    """
    env = Environment()

    destination = pre.fund_eoa(1)
    contract_address = pre.deploy_contract(
        Op.CALL(
            gas=Op.GAS,
            address=destination,
            value=1,
            args_offset=0,
            args_size=0,
            ret_offset=0,
            ret_size=0,
        )
        + Op.SSTORE(key=1, value=Op.BALANCE(address=destination))
        + Op.SSTORE(key=2, value=Op.GAS),
        balance=0,
    )
    sender = pre.fund_eoa(0x3000000000)

    tx = Transaction(
        chain_id=0x01,
        to=contract_address,
        value=0,
        gas_limit=323328,
        access_list=[],
        protected=True,
        sender=sender,
    )

    post = {
        destination: Account(
            balance=1,
        ),
    }
    state_test(env=env, pre=pre, post=post, tx=tx)
