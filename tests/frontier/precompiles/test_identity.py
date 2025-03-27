"""abstract: Test identity precompile output size."""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Bytecode,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-152.md"
REFERENCE_SPEC_VERSION = "5510973b40973b6aa774f04c9caba823c8ff8460"

IDENTITY_PRECOMPILE_ADDRESS = 0x04


class CallInputs:
    """Defines inputs to CALL for the Identity precompile."""

    def __init__(
        self,
        gas=0x1F4,
        value=0x0,
        args_offset=0x0,
        args_size=0x20,
        ret_offset=0x0,
        ret_size=0x20,
    ):
        """Create a new instance with the provided values."""
        self.gas = gas
        self.value = value
        self.args_offset = args_offset
        self.args_size = args_size
        self.ret_offset = ret_offset
        self.ret_size = ret_size


@pytest.mark.valid_from("Byzantium")
@pytest.mark.parametrize(
    [
        "inputs",
        "store_values_code",
        "stored_value_offset",
        "expected_stored_value",
        "expected_call_result",
    ],
    [
        pytest.param(CallInputs(gas=0xFF), Op.MSTORE(0, 0x1), 0x0, 0x1, 0x1, id="identity_0"),
        pytest.param(
            CallInputs(args_size=0x0),
            Op.MSTORE(0, 0x0),
            0x0,
            0x0,
            0x1,
            id="identity_1",
        ),
        pytest.param(
            CallInputs(gas=0x30D40, value=0x13, args_size=0x0),
            Bytecode(),
            0x0,
            0x0,
            0x1,
            id="identity_1_nonzero",
        ),
        pytest.param(
            CallInputs(args_size=0x25),
            Op.MSTORE(0, 0xF34578907F),
            0x0,
            0xF34578907F,
            0x1,
            id="identity_2",
        ),
        pytest.param(
            CallInputs(args_size=0x25),
            Op.MSTORE(0, 0xF34578907F),
            0x0,
            0xF34578907F,
            0x1,
            id="identity_3",
        ),
        pytest.param(
            CallInputs(gas=0x64),
            Op.MSTORE(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF),
            0x0,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            0x1,
            id="identity_4",
        ),
        pytest.param(
            CallInputs(gas=0x11),
            Op.MSTORE(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF),
            0x0,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            0x0,
            id="identity_4_gas17",
        ),
        pytest.param(
            CallInputs(gas=0x12),
            Op.MSTORE(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF),
            0x0,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            0x1,
            id="identity_4_gas18",
        ),
        pytest.param(
            CallInputs(gas=0x258, args_size=0xF4240),
            Op.MSTORE(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF),
            0x0,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            0xDEADBEEF,
            id="identity_5",
        ),
        pytest.param(
            CallInputs(gas=0x258, ret_size=0x40),
            Op.MSTORE(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
            + Op.MSTORE(0x20, 0x1234),
            0x20,
            0x1234,
            0x1,
            id="identity_6",
        ),
    ],
)
def test_call_identity_precompile(
    state_test: StateTestFiller,
    pre: Alloc,
    inputs: CallInputs,
    store_values_code: Bytecode,
    stored_value_offset: int,
    expected_stored_value: int,
    expected_call_result: int,
):
    """Test identity precompile RETURNDATA is sized correctly based on the input size."""
    env = Environment()

    account = pre.deploy_contract(
        store_values_code
        + Op.SSTORE(
            2,
            Op.CALL(
                gas=inputs.gas,
                address=IDENTITY_PRECOMPILE_ADDRESS,
                value=inputs.value,
                args_offset=inputs.args_offset,
                args_size=inputs.args_size,
                ret_offset=inputs.ret_offset,
                ret_size=inputs.ret_size,
            ),
        )
        + Op.SSTORE(0, Op.MLOAD(stored_value_offset))
        + Op.STOP,
        storage={0: 0xDEADBEEF, 2: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: expected_stored_value, 2: expected_call_result})}

    state_test(env=env, pre=pre, post=post, tx=tx)
