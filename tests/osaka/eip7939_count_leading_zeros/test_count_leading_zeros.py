"""
abstract: Tests [EIP-7939: Count leading zeros (CLZ) opcode](https://eips.ethereum.org/EIPS/eip-7939)
    Test cases for [EIP-7939: Count leading zeros (CLZ) opcode](https://eips.ethereum.org/EIPS/eip-7939).
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import Account, Alloc, CodeGasMeasure, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7939.md"
REFERENCE_SPEC_VERSION = "1a4aed0bca3a74bc2caa37c16514098e3d072a8c"

CLZ_GAS_COST = 3


@pytest.mark.valid_from("Osaka")
@pytest.mark.parametrize("bits", range(257))
def test_clz_filled_format_0b0111(state_test: StateTestFiller, bits: int, pre: Alloc, fork: Fork):
    """
    Test CLZ opcode. Value is of format 0b0011..11.
    The CLZ(0) case is also included in this test.
    """
    value = 2**256 - 1 >> bits
    contract_address = pre.deploy_contract(
        Op.SSTORE(0, Op.CLZ(value)),
        storage={"0x00": "0xdeadbeef"},
    )
    sender = pre.fund_eoa()

    tx = Transaction(to=contract_address, sender=sender, gas_limit=200_000)

    post = {
        # gas cost calculation adds the cost of PUSH (3), POP (2) and GAS (2) to the costs of CLZ
        # TODO: read gas costs of these opcode from fork
        contract_address: Account(storage={"0x00": bits}),
    }

    state_test(pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Osaka")
@pytest.mark.parametrize("bits", range(0, 256))
def test_clz_filled_format_0b0100(state_test: StateTestFiller, bits: int, pre: Alloc, fork: Fork):
    """Test CLZ opcode. Value is of format 0b0010..00."""
    value = 1 << bits
    contract_address = pre.deploy_contract(
        Op.SSTORE(0, Op.CLZ(value)),
        storage={"0x00": "0xdeadbeef"},
    )
    sender = pre.fund_eoa()

    tx = Transaction(to=contract_address, sender=sender, gas_limit=200_000)

    post = {
        # gas cost calculation adds the cost of PUSH (3), POP (2) and GAS (2) to the costs of CLZ
        # TODO: read gas costs of these opcode from fork
        contract_address: Account(storage={"0x00": 255 - bits}),
    }

    state_test(pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Osaka")
def test_clz_gas(state_test: StateTestFiller, pre: Alloc, fork: Fork):
    """Tests the gas cost of the CLZ opcode."""
    gas_cost = fork.gas_costs()
    contract_address = pre.deploy_contract(
        Op.SSTORE(
            0,
            CodeGasMeasure(code=Op.CLZ(Op.PUSH1(1)), extra_stack_items=1, overhead_cost=0),
        ),
        storage={"0x00": "0xdeadbeef"},
    )
    sender = pre.fund_eoa()

    tx = Transaction(to=contract_address, sender=sender, gas_limit=200_000)

    post = {
        # Cost measured is CLZ + PUSH1
        contract_address: Account(storage={"0x00": CLZ_GAS_COST + gas_cost.G_VERY_LOW}),
    }

    state_test(pre=pre, post=post, tx=tx)
