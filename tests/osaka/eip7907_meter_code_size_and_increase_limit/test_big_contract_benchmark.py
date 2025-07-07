"""
abstract: Tests [EIP-7939: Count leading zeros (CLZ) opcode](https://eips.ethereum.org/EIPS/eip-7939)
    Test cases for [EIP-7939: Count leading zeros (CLZ) opcode](https://eips.ethereum.org/EIPS/eip-7939).
"""

import math

import pytest

from ethereum_test_base_types.base_types import Hash
from ethereum_test_base_types.composite_types import Account
from ethereum_test_forks.helpers import Fork
from ethereum_test_specs.blockchain import Block
from ethereum_test_tools import (
    Alloc,
    BlockchainTestFiller,
)
from ethereum_test_tools.code.generators import While
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.block_types import Environment
from ethereum_test_types.helpers import compute_create2_address
from ethereum_test_types.transaction_types import Transaction
from ethereum_test_vm.bytecode import Bytecode

from .spec import Spec, ref_spec_7907

REFERENCE_SPEC_GIT_PATH = ref_spec_7907.git_path
REFERENCE_SPEC_VERSION = ref_spec_7907.version

XOR_TABLE_SIZE = 256
XOR_TABLE = [Hash(i).sha256() for i in range(XOR_TABLE_SIZE)]


#      '0xe82e4e9607738c31c00fef26cec6a7d46526ae57',
#      '0x6ce334bfafe0bc1ce1b2215986008d3d64f17eb4',
#      '0x8070b3a20ad702990e6924ebe92ed006f272ba11'


# Marks the opcode and the proxy_gas, which is the exact amount to send to the proxy contract
# This depends on the opcode due to the stack setup costs and possible extract dynamic costs
# (copy gas per byte for EXTCODECOPY for instance)
# NOTE: this is fork-dependent and is currently only correct for Osaka
@pytest.mark.parametrize(
    "opcode,proxy_gas",
    [
        # For proxy gas: all need to load the address from calldata (PUSH0 + CALLDATALOAD = 5 gas)
        # All also pay for warming the cold account (2600 gas)
        # Both the costs 2600 + 5 = 2605 is the minimal cost.
        # All other is PUSH1 overhead (EEST does not default to PUSH0 if PUSH1(0)).
        # PUSH1 costs 3 gas
        (Op.EXTCODESIZE, 2605),  # 0 overhead
        (Op.EXTCODECOPY, 2620),  # 2620 - 2605 = 15 = 3x PUSH1 (9) + bytecopy (3) + mem expand (3)
        (Op.CALL, 2622),  # 2622 - 2605 = 17 = 5x PUSH1 (15) 1x GAS (2)
        (Op.CALLCODE, 2622),  # 2622 - 2605 = 17 = 5x PUSH1 (15) 1x GAS (2)
        (Op.DELEGATECALL, 2619),  # 2619 - 2605 = 14 = 4x PUSH1 (12) 1x GAS (2)
        (Op.STATICCALL, 2619),  # 2619 - 2605 = 14 = 4x PUSH1 (12) 1x GAS (2)
    ],
)
@pytest.mark.slow()
@pytest.mark.valid_from("Osaka")
def test_big_contract_reads_bench(
    blockchain_test: BlockchainTestFiller, fork: Fork, pre: Alloc, opcode: Op, proxy_gas: int
):
    """
    Benchmarks a scenario where "big contracts" (> 24 KiB (i.e. EIP-170 limit)) are
    targeted by a code-reading opcode. The test loops over the deployed CREATE2 addresses and
    then calls into a proxy-contract given exactly enough gas to perform the operation for
    a "small" contract (<= 24 KiB) but not enough to pay any gas for the pricing mechanism
    introduced in EIP-7907. This ensures that the EVM has to lookup the code (to calculate the
    size), but when calculating the actual price and attempting to deduct it, it is concluded
    that the current context does not have enough gas to pay for loading this big code.
    From a trie point of view, the code thus has to be loaded (code size can only be determined
    from reading the complete code). To speedup this process, an implicit side-index is thus
    necessary in a client to ensure that the code size can be read without having to read all
    the code.
    """
    # NOTE: this test is edited from `test_worst_bytecode_single_opcode` from `benchmarks` test
    # folder
    # TODO: attack is currently setup with the 30M tx gas limit in mind. NOT the block gas limit
    # (should this be changed to block gas limit?)

    # The attack gas limit is the gas limit which the target tx will use
    # The test will scale the block gas limit to setup the contracts accordingly to be
    # able to pay for the contract deposit. This has to take into account the 200 gas per byte,
    # but also the quadratic memory expansion costs which have to be paid each time the
    # memory is being setup
    attack_gas_limit = 30_000_000  # Max queries per tx. TODO: read from EIP7825 or fork config
    target_contract_size = Spec.TARGET_CODE_SIZE

    gas_costs = fork.gas_costs()

    # Start of benchmark setup phase

    # Calculate the absolute minimum gas costs to deploy the contract
    # This does not take into account setting up the actual memory (using KECCAK256 and XOR)
    # so the actual costs of deploying the contract is higher
    memory_expansion_gas_calculator = fork.memory_expansion_gas_calculator()
    memory_gas_minimum = memory_expansion_gas_calculator(
        new_bytes=len(bytes(target_contract_size))
    )
    code_deposit_gas_minimum = (
        fork.gas_costs().G_CODE_DEPOSIT_BYTE * target_contract_size + memory_gas_minimum
    )
    # This determines how much contracts are deployed per tx
    # TODO: change 30M gas limit to read from fork config
    # NOTE: code_deposit_gas_limit is too low. In certain gas limits, this might
    # assume max deployments per tx too high. (This will fail the post-alloc check though
    # so the fixture will fail to fill). To fix: this needs to calculate the actual deposit gas.
    max_deployment_per_tx = 30_000_000 // code_deposit_gas_minimum

    intrinsic_gas_cost_calc = fork.transaction_intrinsic_cost_calculator()
    # Calculate the loop cost of the attacker to query one address
    # NOTE: this is too low, but this will thus give an upper bound of the contracts to target
    loop_cost = (
        gas_costs.G_KECCAK_256  # KECCAK static cost
        + math.ceil(85 / 32) * gas_costs.G_KECCAK_256_WORD  # KECCAK dynamic cost for CREATE2
        + gas_costs.G_VERY_LOW * 3  # ~MSTOREs+ADDs
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # Opcode cost
        + 30  # ~Gluing opcodes
    )
    # Calculate the number of contracts to be targeted
    num_contracts = (
        # Base available gas = GAS_LIMIT - intrinsic - (out of loop MSTOREs)
        attack_gas_limit - intrinsic_gas_cost_calc() - gas_costs.G_VERY_LOW * 4
    ) // loop_cost

    # Set the block gas limit to a relative high value to ensure the code deposit tx
    # fits in the block (there is enough gas available in the block to execute this)
    env = Environment(gas_limit=code_deposit_gas_minimum * 2 * num_contracts)

    # This simple initcode will deploy a contract of size `target_contract_size` to the chain
    # It will MSTORE the address (note: this still marks the first 12 bytes as 00s (STOP))
    # This MSTORE is used to generate unique codes and thus code hashes
    initcode = Op.MSTORE(0, Op.ADDRESS) + Op.RETURN(0, target_contract_size)
    initcode_address = pre.deploy_contract(code=initcode)

    # The factory contract will simply use the initcode that is already deployed,
    # and create a new contract and return its address if successful.
    factory_code = (
        Op.EXTCODECOPY(
            address=initcode_address,
            dest_offset=0,
            offset=0,
            size=Op.EXTCODESIZE(initcode_address),
        )
        + Op.MSTORE(
            0,
            Op.CREATE2(
                value=0,
                offset=0,
                size=Op.EXTCODESIZE(initcode_address),
                salt=Op.SLOAD(0),
            ),
        )
        + Op.SSTORE(0, Op.ADD(Op.SLOAD(0), 1))
        + Op.RETURN(0, 32)
    )
    factory_address = pre.deploy_contract(code=factory_code)

    # The factory caller will call the factory contract N times, creating N new contracts.
    # Calldata should contain the N value.
    factory_caller_code = Op.CALLDATALOAD(0) + While(
        body=Op.POP(Op.CALL(address=factory_address)),
        condition=Op.PUSH1(1) + Op.SWAP1 + Op.SUB + Op.DUP1 + Op.ISZERO + Op.ISZERO,
    )
    factory_caller_address = pre.deploy_contract(code=factory_caller_code)
    deploy_txs = []

    deployed_contracts = 0
    while deployed_contracts < num_contracts:
        tx = Transaction(
            to=factory_caller_address,
            gas_limit=30_000_000,  # TODO read max tx limit from fork config or EIP 7825
            # TODO: `Hash` is sometimes used in tests to either represent the EVM 32-byte
            # stack or for other purposes (here: align calldata correctly for CALLDATALOAD)
            # `Hash` should change to something like EVMByte or something more helpful
            # (it now reads like it hashes `max_deployment_per_tx` but does not do this)
            data=Hash(max_deployment_per_tx),
            sender=pre.fund_eoa(),
            nonce=len(deploy_txs),
        )
        deploy_txs.append(tx)
        deployed_contracts += max_deployment_per_tx
        break

    post = {}
    deployed_contract_addresses = []
    for i in range(num_contracts):
        deployed_contract_address = compute_create2_address(
            address=factory_address,
            salt=i,
            initcode=initcode,
        )
        post[deployed_contract_address] = Account(nonce=1)
        deployed_contract_addresses.append(deployed_contract_address)

    # Start of the actual benchmark setup

    # Read target address from calldata and push to stack
    read_address_code = Op.PUSH0 + Op.CALLDATALOAD
    proxy_code = Bytecode()
    if opcode == Op.EXTCODECOPY:
        # Size is set to 1 to force copying
        # NOTE: this is not clear from spec (and an edge case): if 0 size is read, should
        # "big code cost" still be priced in? (It is clear 0 bytes are copied so reading any code
        # is not strictly necessary)
        proxy_code = Op.EXTCODECOPY(address=read_address_code, size=1)
    else:
        # For the rest of the opcodes, we can use the same generic attack call
        # since all only minimally need the `address` of the target.
        proxy_code = opcode(address=read_address_code)

        # For the rest of the opcodes, we can use the same generic attack call
        # since all only minimally need the `address` of the target.

    proxy_contract = pre.deploy_contract(code=proxy_code)

    call_proxy = Op.MSTORE(96, Op.SHA3(32 - 20 - 1, 85)) + Op.POP(
        Op.STATICCALL(address=proxy_contract, gas=proxy_gas, args_offset=96, args_size=32)
    )

    attack_code = (
        # Setup memory for later CREATE2 address generation loop.
        # 0xFF+[Address(20bytes)]+[seed(32bytes)]+[initcode keccak(32bytes)]
        Op.MSTORE(0, factory_address)
        + Op.MSTORE8(32 - 20 - 1, 0xFF)
        + Op.MSTORE(32, 0)
        + Op.MSTORE(64, initcode.keccak256())
        # Main loop
        + While(
            body=call_proxy + Op.MSTORE(32, Op.ADD(Op.MLOAD(32), 1)),
        )
    )

    if len(attack_code) > target_contract_size:
        raise ValueError(
            f"Code size {len(attack_code)} exceeds maximum code size {target_contract_size}"
        )
    opcode_address = pre.deploy_contract(code=attack_code)
    opcode_tx = Transaction(
        to=opcode_address,
        gas_limit=attack_gas_limit,
        sender=pre.fund_eoa(),
    )

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=[
            Block(txs=deploy_txs),
            Block(txs=[opcode_tx]),
        ],
        exclude_full_post_state_in_output=True,
    )
