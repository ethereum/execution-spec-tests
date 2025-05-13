"""
abstract: Tests zkEVMs worst-case stateful opcodes.
    Tests zkEVMs worst-case stateful opcodes.

Tests running worst-case stateful opcodes for zkEVMs.
"""

import math

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (Account, Address, Alloc, Block,
                                 BlockchainTestFiller, Bytecode, Environment,
                                 Transaction, While)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"

MAX_CODE_SIZE = 24 * 1024


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "attack_gas_limit",
    [
        Environment().gas_limit,
    ],
)
@pytest.mark.parametrize(
    "opcode",
    [
        Op.BALANCE,
    ],
)
@pytest.mark.parametrize(
    "absent_target",
    [
        True,
        False,
    ],
)
def test_worst_address_state_cold(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    attack_gas_limit: int,
    opcode: Op,
    absent_target: bool,
):
    """
    Test running a block with as many stateful opcodes accessing cold accounts.
    """
    env = Environment(gas_limit=100_000_000_000)

    gas_costs = fork.gas_costs()
    intrinsic_gas_cost_calc = fork.transaction_intrinsic_cost_calculator()
    num_target_accounts = (
        attack_gas_limit - intrinsic_gas_cost_calc()
    ) // gas_costs.G_COLD_ACCOUNT_ACCESS

    blocks = []
    post = {}

    # Setup
    # The target addresses are going to be constructed (in the case of absent=False) and called
    # as addr_offset + i, where i is the index of the account. This is to avoid
    # collisions with the addresses indirectly created by the testing framework.
    addr_offset = 100_000

    if not absent_target:
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
        blocks.append(Block(txs=[setup_tx]))

        for i in range(num_target_accounts):
            addr = Address(i + addr_offset + 1)
            post[addr] = Account(balance=10)

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
    blocks.append(Block(txs=[op_tx]))

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
        # TODO: add skip_post_check=True
    )


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "attack_gas_limit",
    [
        Environment().gas_limit,
    ],
)
@pytest.mark.parametrize(
    "opcode",
    [
        Op.BALANCE,
        Op.EXTCODESIZE,
        Op.EXTCODEHASH,
    ],
)
@pytest.mark.parametrize(
    "absent_target",
    [
        True,
        False,
    ],
)
def test_worst_address_state_warm(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    attack_gas_limit: int,
    opcode: Op,
    absent_target: bool,
):
    """
    Test running a block with as many stateful opcodes doing warm access for an account.
    """
    env = Environment(gas_limit=100_000_000_000)

    # Setup
    target_addr = Address(100_000)
    post = {target_addr: None}
    if not absent_target:
        target_addr = pre.deploy_contract(balance=100, code=Op.JUMPDEST * 100)
        post[target_addr] = Account(balance=100, code=Op.JUMPDEST * 100)

    # Execution
    prep = Op.PUSH20(target_addr)
    jumpdest = Op.JUMPDEST
    jump_back = Op.JUMP(len(prep))
    iter_block = Op.POP(opcode(Op.DUP1))
    max_iters_loop = (MAX_CODE_SIZE - len(prep) - len(jumpdest) - len(jump_back)) // len(
        iter_block
    )
    op_code = prep + jumpdest + sum([iter_block] * max_iters_loop) + jump_back
    if len(op_code) > MAX_CODE_SIZE:
        # Must never happen, but keep it as a sanity check.
        raise ValueError(f"Code size {len(op_code)} exceeds maximum code size {MAX_CODE_SIZE}")
    op_address = pre.deploy_contract(code=op_code)
    op_tx = Transaction(
        to=op_address,
        gas_limit=attack_gas_limit,
        gas_price=10,
        sender=pre.fund_eoa(),
    )

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=[Block(txs=[op_tx])],
    )
    # TODO: add skip_post_check=True
