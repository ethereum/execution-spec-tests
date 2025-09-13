"""
abstract: Tests practical scenarios on Mainnet with the XEN (which has a big state) contract

Tests practical scenarios on Mainnet with the XEN (which has a big state) contract.
This currently has one situation, but will be expanded with other scenarios.
The goal is to bloat as much of the big state of XEN as possible. XEN has a big state trie.
We therefore want to do as much state situations (either read or write: likely write is
the most expensive situation).
NOTE: this is thus NOT the worst-case scenario, since we can remove the overhead execution
computations for XEN and only do state operations on an account with a big state attached to it.
This therefore only tests the practical, "real life" and most likely scenario.
However, with enough funds (to bloat a contract state), this is thus not the worst scenario.
"""

import math

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    Hash,
    Transaction,
    While,
    compute_create2_address,
)
from ethereum_test_tools import Macros as Om
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO
# The current test does only claimRank(1) and then waits `SECONDS_IN_DAY = 3_600 * 24;` plus 1
# (see https://etherscan.io/token/0x06450dEe7FD2Fb8E39061434BAbCFC05599a6Fb8#code) and then
# claimMintReward() from CREATE2-create proxy accounts (to save gas).
# This might not be the worst scenario, for instance `claimMintRewardAndShare(address,uint256)`
# might yield even worse scenarios (or scenarios regarding "staking")
# These scenarios will be added.


# TODO: set correct fork, XEN might reject on historical forks due to e.g. non-existent opcodes
# NOTE: deploy both XEN (0x06450dEe7FD2Fb8E39061434BAbCFC05599a6Fb8)
# and Math (0x4bBA9B6B49f3dFA6615f079E9d66B0AA68B04A4d) in prestate for the Mainnet scenario!
@pytest.mark.valid_from("Frontier")
def test_xen_claimrank_and_mint(
    blockchain_test: BlockchainTestFiller,
    fork: Fork,
    pre: Alloc,
    env: Environment,
    gas_benchmark_value: int,
):
    """Simple XEN scenario to claimRank(1) and claimMintReward()."""
    attack_gas_limit = gas_benchmark_value
    fee_recipient = pre.fund_eoa(amount=1)

    # timestamp to use for the initial block. Timestamp of later blocks are manually added/changed.
    timestamp = 12

    # TODO: adjust this to the right amount of the actual performance test block
    num_xen = 10

    # NOTE: these contracts MUST be specified for this test to work
    # TODO: check how/if EEST enforces this
    xen_contract = pre.deploy_contract("", label="XEN_CONTRACT")
    # NOTE: from the test perspective this contract should not be specified
    # However, the XEN contract needs the Math contract. If this is not provided, the transaction
    # will likely revert ("fail"). This is not what we want. We want state bloat!
    pre.deploy_contract("", label="MATH_CONTRACT")

    # This is after (!!) deployment (so step 2, not 1): claimMintReward()
    calldata_claim_mint_reward = bytes.fromhex("52c7f8dc")
    after_initcode_callata = Om.MSTORE(bytes.fromhex("52c7f8dc")) + Op.CALL(
        address=xen_contract, args_size=len(calldata_claim_mint_reward)
    )

    # Calldata for claimRank(1)
    calldata_claim_rank = bytes.fromhex(
        "9ff054df0000000000000000000000000000000000000000000000000000000000000001"
    )

    # claimRank(1) and deposits the code to claimMintReward() if this contract is called
    initcode = (
        Om.MSTORE(calldata_claim_rank)
        + Op.CALL(address=xen_contract, args_size=len(calldata_claim_rank))
        + Om.MSTORE(after_initcode_callata)
        + Op.RETURN(0, len(after_initcode_callata))
    )

    # Template code that will be used to deploy a large number of contracts.
    initcode_address = pre.deploy_contract(code=initcode)

    # Calculate the number of contracts that can be deployed with the available gas.
    gas_costs = fork.gas_costs()
    intrinsic_gas_cost_calc = fork.transaction_intrinsic_cost_calculator()
    loop_cost = (
        gas_costs.G_KECCAK_256  # KECCAK static cost
        + math.ceil(85 / 32) * gas_costs.G_KECCAK_256_WORD  # KECCAK dynamic cost for CREATE2
        + gas_costs.G_VERY_LOW * 3  # ~MSTOREs+ADDs
        + gas_costs.G_COLD_ACCOUNT_ACCESS  # CALL to self-destructing contract
        + gas_costs.G_SELF_DESTRUCT
        + 63  # ~Gluing opcodes
    )
    final_storage_gas = (
        gas_costs.G_STORAGE_RESET + gas_costs.G_COLD_SLOAD + (gas_costs.G_VERY_LOW * 2)
    )
    memory_expansion_cost = fork().memory_expansion_gas_calculator()(new_bytes=96)
    base_costs = (
        intrinsic_gas_cost_calc()
        + (gas_costs.G_VERY_LOW * 12)  # 8 PUSHs + 4 MSTOREs
        + final_storage_gas
        + memory_expansion_cost
    )
    num_contracts = num_xen  # TODO: edit this to construct as much contracts as possible to
    # `claimMintReward()` as the performance test.
    expected_benchmark_gas_used = num_contracts * loop_cost + base_costs

    # Create a factory that deployes a new SELFDESTRUCT contract instance pre-funded depending on
    # the value_bearing parameter. We use CREATE2 so the caller contract can easily reproduce
    # the addresses in a loop for CALLs.
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
                offset=0,
                size=Op.EXTCODESIZE(initcode_address),
                salt=Op.SLOAD(0),
            ),
        )
        + Op.SSTORE(0, Op.ADD(Op.SLOAD(0), 1))
        + Op.RETURN(0, 32)
    )

    factory_address = pre.deploy_contract(code=factory_code)

    factory_caller_code = Op.CALLDATALOAD(0) + While(
        body=Op.POP(Op.CALL(address=factory_address)),
        condition=Op.PUSH1(1) + Op.SWAP1 + Op.SUB + Op.DUP1 + Op.ISZERO + Op.ISZERO,
    )
    factory_caller_address = pre.deploy_contract(code=factory_caller_code)

    contracts_deployment_tx = Transaction(
        to=factory_caller_address,
        gas_limit=env.gas_limit,
        data=Hash(num_contracts),
        sender=pre.fund_eoa(),
    )

    code = (
        # Setup memory for later CREATE2 address generation loop.
        # 0xFF+[Address(20bytes)]+[seed(32bytes)]+[initcode keccak(32bytes)]
        Op.MSTORE(0, factory_address)
        + Op.MSTORE8(32 - 20 - 1, 0xFF)
        + Op.MSTORE(32, 0)  # NOTE: this memory location is used as start index of the contracts.
        + Op.MSTORE(64, initcode.keccak256())
        + Op.CALLDATALOAD(0)
        # Main loop
        + While(
            body=Op.POP(Op.CALL(address=Op.SHA3(32 - 20 - 1, 85)))
            + Op.MSTORE(32, Op.ADD(Op.MLOAD(32), 1)),
            # Loop over `CALLDATALOAD` contracts
            condition=Op.PUSH1(1) + Op.SWAP1 + Op.SUB + Op.DUP1 + Op.ISZERO + Op.ISZERO,
        )
        + Op.SSTORE(0, 42)  # Done for successful tx execution assertion below.
    )
    assert len(code) <= fork.max_code_size()

    # The 0 storage slot is initialize to avoid creation costs in SSTORE above.
    code_addr = pre.deploy_contract(code=code, storage={0: 1})
    opcode_tx = Transaction(
        to=code_addr,
        data=Hash(num_contracts),
        gas_limit=attack_gas_limit,
        sender=pre.fund_eoa(),
    )

    post = {
        factory_address: Account(storage={0: num_contracts}),
        code_addr: Account(storage={0: 42}),  # Check for successful execution.
    }
    deployed_contract_addresses = []
    for i in range(num_contracts):
        deployed_contract_address = compute_create2_address(
            address=factory_address,
            salt=i,
            initcode=initcode,
        )
        post[deployed_contract_address] = Account(nonce=1)
        deployed_contract_addresses.append(deployed_contract_address)

    setup_block = Block(txs=[contracts_deployment_tx], timestamp=timestamp)
    blockchain_test(
        pre=pre,
        post=post,
        blocks=[
            setup_block,
            Block(
                txs=[opcode_tx],
                fee_recipient=fee_recipient,
                # Set timestamp such that XEN bond matures
                # See `MIN_TERM` constant in XEN source
                timestamp=timestamp + 3_600 * 24,
            ),
        ],
        exclude_full_post_state_in_output=True,
        expected_benchmark_gas_used=expected_benchmark_gas_used,
    )
