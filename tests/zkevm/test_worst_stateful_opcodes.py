"""
abstract: Tests zkEVMs worst-case stateful opcodes.
    Tests zkEVMs worst-case stateful opcodes.

Tests running worst-case stateful opcodes for zkEVMs.
"""

import math

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (Account, Address, Alloc, Block,
                                 BlockchainTestFiller, Environment,
                                 Transaction, While)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "attack_gas_limit",
    [
        36_000_000,
    ],
)
@pytest.mark.parametrize(
    "opcode",
    [
        Op.BALANCE,
    ],
)
def test_worst_address_state_cold(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    attack_gas_limit: int,
    opcode: Op,
):
    """
    Test running a block with as many stateful opcodes execution accessing
    an account state as possible.
    """
    env = Environment(gas_limit=100_000_000_000)


    # Setup
    gas_costs = fork.gas_costs()
    intrinsic_gas_cost_calc = fork.transaction_intrinsic_cost_calculator()
    num_target_accounts = (
        attack_gas_limit - intrinsic_gas_cost_calc()
    ) // gas_costs.G_COLD_ACCOUNT_ACCESS

    # Create num_target_accounts accounts by sending 10 wei to each. The addresses are 
    # consecutive numbers starting from addr_offset so we avoid collisions.
    addr_offset = 100_000
    factory_code = Op.PUSH4(num_target_accounts) + While(
        body=Op.POP(Op.CALL(address=Op.ADD(addr_offset, Op.DUP6), value=10)),
        condition=Op.PUSH1(1) + Op.SWAP1 + Op.SUB + Op.DUP1 + Op.ISZERO + Op.ISZERO,
    )
    factory_address = pre.deploy_contract(code=factory_code, balance=10**18)

    setup_tx = Transaction(
        to=factory_address,
        gas_limit=env.gas_limit,
        gas_price=10,
        sender=pre.fund_eoa(),
    )

    # Execution
    op_code = Op.PUSH4(num_target_accounts) + While(
        body=Op.POP(opcode(Op.ADD(addr_offset, Op.DUP1))),
        condition=Op.PUSH1(1) + Op.SWAP1 + Op.SUB + Op.DUP1 + Op.ISZERO + Op.ISZERO,
    )
    op_address = pre.deploy_contract(code=op_code)
    op_tx = Transaction(
        to=op_address,
        gas_limit=attack_gas_limit,
        gas_price=10,
        sender=pre.fund_eoa(),
    )

    post = {}
    for i in range(num_target_accounts):
        addr = Address(i+addr_offset+1)
        post[addr] = Account(balance=10)

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=[
            Block(txs=[setup_tx]),
            Block(txs=[op_tx]),
        ],
        # TODO: add skip_post_check=True
    )
