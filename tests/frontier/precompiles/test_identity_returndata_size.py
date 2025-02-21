"""abstract: Test identity precompile output size."""

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
REFERENCE_SPEC_VERSION = "5510973b40973b6aa774f04c9caba823c8ff8460"

IDENTITY_PRECOMPILE_ADDRESS = 0x04


@pytest.mark.valid_from("Byzantium")
@pytest.mark.parametrize(
    ["args_size", "output_size", "returndatasize"],
    [
        pytest.param(16, 32, 16, id="output_16"),
        pytest.param(32, 16, 32, id="output_32"),
    ],
)
def test_identity_precompile_returndata(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    args_size: int,
    output_size: int,
    returndatasize: int,
):
    """Test identity precompile RETURNDATA is sized correctly based on the input size."""
    env = Environment()

    account = pre.deploy_contract(
        Op.MSTORE(0, 0)
        + Op.GAS
        + Op.MSTORE(0, 0x112233445566778899AABBCCDDEEFF00112233445566778899AABBCCDDEEFF00)
        + Op.CALL(
            address=IDENTITY_PRECOMPILE_ADDRESS,
            args_offset=0,
            args_size=args_size,
            output_offset=0x10,
            output_size=output_size,
        )
        + Op.POP
        + Op.SSTORE(0, Op.RETURNDATASIZE)
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
    post = {account: Account(storage={0: returndatasize})}

    state_test(env=env, pre=pre, post=post, tx=tx)
