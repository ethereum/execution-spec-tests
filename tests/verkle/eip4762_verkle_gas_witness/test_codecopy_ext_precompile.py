"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_forks import Fork, Verkle
from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.verkle.helpers import chunkify_code

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x04")
system_contract_address = Address("0xfffffffffffffffffffffffffffffffffffffffe")


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "target",
    [
        precompile_address,
        system_contract_address,
    ],
)
def test_extcodecopy_precompile(blockchain_test: BlockchainTestFiller, fork: Fork, target):
    """
    Test EXTCODECOPY targeting a precompile or system contract.
    """
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(
            balance=1000000000000000000000, code=Op.EXTCODECOPY(target, 0, 0, 10)
        ),
    }

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=1_000_000,
        gas_price=10,
    )

    witness_check = WitnessCheck(fork=Verkle)
    for address in [env.fee_recipient, TestAddress, TestAddress2]:
        witness_check.add_account_full(address=address, account=pre.get(address))
    code_chunks = chunkify_code(pre[TestAddress2].code)
    for i, chunk in enumerate(code_chunks, start=0):
        witness_check.add_code_chunk(address=TestAddress2, chunk_number=i, value=chunk)

    if target == system_contract_address:
        sys_contract_account = Account(**fork.pre_allocation_blockchain()[system_contract_address])
        code_chunks = chunkify_code(sys_contract_account.code)
        witness_check.add_account_basic_data(system_contract_address, sys_contract_account)
        witness_check.add_code_chunk(
            address=system_contract_address, chunk_number=0, value=code_chunks[0]
        )

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
    )
