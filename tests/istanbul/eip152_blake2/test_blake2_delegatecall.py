"""abstract: Test delegatecall to Blake2B Precompile before and after it was added."""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-152.md"
REFERENCE_SPEC_VERSION = "2762bfcff3e549ef263342e5239ef03ac2b07400"

BLAKE2_PRECOMPILE_ADDRESS = 0x09


@pytest.mark.valid_from("Cancun")
def test_blake2_precompile_delegatecall(state_test: StateTestFiller, pre: Alloc, fork: Fork):
    """Test delegatecall consumes specified gas for the Blake2B precompile when it exists."""
    env = Environment()

    account = pre.deploy_contract(
        Op.MSTORE(0, 0)  # Pre-expand the memory so the gas costs are exactly the same
        + Op.GAS
        + Op.DELEGATECALL(
            gas=1,
            address=BLAKE2_PRECOMPILE_ADDRESS,
        )
        + Op.POP
        + Op.GAS
        + Op.SUB
        + Op.SSTORE(0, Op.ISZERO)
        + Op.STOP,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    # Delegatecall to the precompile will fail and consume the specified gas amount
    # Otherwise delegatecall will succeed and no gas will be consumed
    post = {account: Account(storage={0: "0x01" if fork == "Istanbul" else "0x00"})}

    state_test(env=env, pre=pre, post=post, tx=tx)
