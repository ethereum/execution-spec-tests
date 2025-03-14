"""Tests supported precompiled contracts."""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_vm.bytecode import Bytecode

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-2929.md"
REFERENCE_SPEC_VERSION = "0e11417265a623adb680c527b15d0cb6701b870b"

UPPER_BOUND = 0xFF
NUM_UNSUPPORTED_PRECOMPILES = 8


@pytest.fixture
def contract_bytecode(request) -> Bytecode:
    """Generate bytecode for the contract to be tested."""
    return (
        Op.GAS
        + Op.CALL(
            address=request.param["address"],
            value=request.param["value"],
            args_offset=request.param["args_offset"],
            args_size=request.param["args_size"],
            output_offset=request.param["output_offset"],
            output_size=request.param["output_size"],
        )
        + Op.POP
        + Op.SUB(Op.SWAP1, Op.GAS)
        + Op.GAS
        + Op.CALL(
            address=request.param["address"],
            value=request.param["value"],
            args_offset=request.param["args_offset"],
            args_size=request.param["args_size"],
            output_offset=request.param["output_offset"],
            output_size=request.param["output_size"],
        )
        + Op.POP
        + Op.SUB(Op.SWAP1, Op.GAS)
        + Op.SWAP1
        + Op.SSTORE(0, Op.SUB)
        + Op.STOP
    )


def initial_setup_bytecode(sender: Account) -> Bytecode:
    """Generate bytecode for the initial setup to be tested."""
    return (
        Op.MSTORE(0, 0)
        + Op.MSTORE(0x100, 0xDEADBEEF)
        + Op.CALL(
            address=sender,
            value=1,
            args_offset=0,
            args_size=0,
            output_offset=0,
            output_size=0,
        )
        + Op.POP
    )


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x0B,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_11_params_0",
        ),
        pytest.param(
            {
                "address": 0x0C,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_12_params_0",
        ),
        pytest.param(
            {
                "address": 0x0D,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_13_params_0",
        ),
        pytest.param(
            {
                "address": 0x0E,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_14_params_0",
        ),
        pytest.param(
            {
                "address": 0x0F,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_15_params_0",
        ),
        pytest.param(
            {
                "address": 0x10,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_16_params_0",
        ),
        pytest.param(
            {
                "address": 0x11,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_17_params_0",
        ),
    ],
    indirect=True,
)
def test_prague_call_consumes_equal_gas_amount(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation against Prague for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x00})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x01,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_1_params_0",
        ),
        pytest.param(
            {
                "address": 0x02,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_2_params_0",
        ),
        pytest.param(
            {
                "address": 0x03,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_3_params_0",
        ),
        pytest.param(
            {
                "address": 0x04,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_4_params_0",
        ),
        pytest.param(
            {
                "address": 0x05,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_5_params_0",
        ),
        pytest.param(
            {
                "address": 0x06,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_6_params_0",
        ),
        pytest.param(
            {
                "address": 0x07,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_7_params_0",
        ),
        pytest.param(
            {
                "address": 0x08,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_8_params_0",
        ),
    ],
    indirect=True,
)
def test_cancun_call_consumes_equal_gas_amount(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x00})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x01,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_1_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x02,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_2_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x03,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_3_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x04,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_4_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x05,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_5_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x06,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_6_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x07,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_7_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x08,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_8_params_value_1",
        ),
    ],
    indirect=True,
)
def test_cancun_call_extra_gas_for_trie(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x61A8})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x09,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_9_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x0A,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_10_params_value_1",
        ),
    ],
    indirect=True,
)
def test_cancun_call_no_gas_for_call_rejected(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x00})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x0B,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_11_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x0C,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_12_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x0D,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_13_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x0E,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_14_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x0F,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_15_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x10,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_16_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x11,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_17_params_value_1",
        ),
        pytest.param(
            {
                "address": 0x12,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_18_params_value_1",
        ),
    ],
    indirect=True,
)
def test_cancun_call_additional_gas_for_new_trie(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x6B6C})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x01,
                "value": 0,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_1_params_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x02,
                "value": 0,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_2_params_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x03,
                "value": 0,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_3_params_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x04,
                "value": 0,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_4_params_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x05,
                "value": 0,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_5_params_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x06,
                "value": 0,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_6_params_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x07,
                "value": 0,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_7_params_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x08,
                "value": 0,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_8_params_args_size_1",
        ),
    ],
    indirect=True,
)
def test_cancun_call_with_data_consumes_equal_gas_amount(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x00})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x01,
                "value": 1,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_1_params_value_1_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x02,
                "value": 1,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_2_params_value_1_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x03,
                "value": 1,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_3_params_value_1_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x04,
                "value": 1,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_4_params_value_1_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x05,
                "value": 1,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_5_params_value_1_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x06,
                "value": 1,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_6_params_value_1_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x07,
                "value": 1,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_7_params_value_1_args_size_1",
        ),
        pytest.param(
            {
                "address": 0x08,
                "value": 1,
                "args_offset": 0,
                "args_size": 1,
                "output_offset": 0,
                "output_size": 0,
            },
            id="call_address_8_params_value_1_args_size_1",
        ),
    ],
    indirect=True,
)
def test_cancun_call_with_wei_and_data_additional_gas_for_new_trie(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x61A8})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x01,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_1_params_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x02,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_2_params_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x03,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_3_params_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x04,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_4_params_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x05,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_5_params_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x06,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_6_params_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x07,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_7_params_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x08,
                "value": 0,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_8_params_output_size_1",
        ),
    ],
    indirect=True,
)
def test_cancun_call_receive_data_consumes_equal_gas_amount(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x00})}

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "contract_bytecode",
    [
        pytest.param(
            {
                "address": 0x01,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_1_params_value_1_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x02,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_2_params_value_1_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x03,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_3_params_value_1_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x04,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_4_params_value_1_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x05,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_5_params_value_1_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x06,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_6_params_value_1_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x07,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_7_params_value_1_output_size_1",
        ),
        pytest.param(
            {
                "address": 0x08,
                "value": 1,
                "args_offset": 0,
                "args_size": 0,
                "output_offset": 0,
                "output_size": 1,
            },
            id="call_address_8_params_value_1_output_size_1",
        ),
    ],
    indirect=True,
)
def test_cancun_call_with_wei_and_receive_data_additional_gas_for_new_trie(
    state_test: StateTestFiller,
    pre: Alloc,
    contract_bytecode: Bytecode,
):
    """Tests equal gas consumption of CALL operation for the given addresses and parameters."""
    env = Environment()

    account = pre.deploy_contract(
        initial_setup_bytecode(pre.fund_eoa(amount=0)) + contract_bytecode,
        storage={0: 0xDEADBEEF},
    )

    tx = Transaction(
        to=account,
        sender=pre.fund_eoa(),
        gas_limit=1_000_000,
        protected=True,
    )

    post = {account: Account(storage={0: 0x61A8})}

    state_test(env=env, pre=pre, post=post, tx=tx)
