"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    Initcode,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..temp_verkle_helpers import Witness

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x09")
system_contract_address = Address("0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "target",
    [
        precompile_address,
        system_contract_address,
    ],
)
def test_extcodecopy_precompile(blockchain_test: BlockchainTestFiller, fork: str, target):
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
    }

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=None,
        gas_limit=1_000_000,
        gas_price=10,
        data=Initcode(deploy_code=Op.EXTCODECOPY(target, 0, 0, 100)).bytecode,
    )
    blocks = [Block(txs=[tx])]

    witness = Witness()
    witness.add_account_full(env.fee_recipient, None)
    witness.add_account_full(TestAddress, pre[TestAddress])
    # No basic data for target.
    # No code chunks.

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness=witness,
    )
