"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    Environment,
    Initcode,
    TestAddress,
    Transaction,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "instruction",
    [
        Op.CODECOPY,
        Op.EXTCODECOPY,
    ],
)
def test_generic_codecopy_initcode(blockchain_test: BlockchainTestFiller, fork: str, instruction):
    """
    Test *CODECOPY executed in initcode works as expected.
    """
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    sender_balance = 1000000000000000000000
    pre = {
        TestAddress: Account(balance=sender_balance),
    }

    data = Initcode(deploy_code=Op.CODECOPY(0, 0, 100) + Op.ORIGIN * 100).bytecode
    if instruction == Op.EXTCODECOPY:
        contract_address = compute_create_address(TestAddress, 0)
        deploy_code = Op.EXTCODECOPY(contract_address, 0, 0, 100) + Op.ORIGIN * 100
        data = Initcode(deploy_code=deploy_code).bytecode

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=None,
        gas_limit=1_000_000,
        gas_price=10,
        data=data,
    )
    blocks = [Block(txs=[tx])]

    # TODO(verkle): define witness assertion
    witness_keys = ""

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness_keys=witness_keys,
    )
