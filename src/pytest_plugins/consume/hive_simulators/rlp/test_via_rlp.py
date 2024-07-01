"""
Test a fully instantiated client using RLP-encoded blocks from blockchain tests.

The input test fixtures have the blockchain test format. The setup sends
the genesis file and RLP-encoded blocks to the client container using hive.
The client consumes these files upon start-up.

Given a genesis state and a list of RLP-encoded blocks, the test verifies that:
1. The client's genesis block hash matches that defined in the fixture.
2. The client's last block hash matches that defined in the fixture.
"""

import time

from ethereum_test_fixtures import BlockchainFixture
from ethereum_test_fixtures.blockchain import FixtureHeader
from ethereum_test_tools.rpc import EthRPC
from pytest_plugins.consume.hive_simulators.exceptions import GenesisBlockMismatchException


def test_via_rlp(
    timing_data,
    eth_rpc: EthRPC,
    blockchain_fixture: BlockchainFixture,
):
    """
    Verify that the client's state as calculated from the specified genesis state
    and blocks matches those defined in the test fixture.

    Test:

    1. The client's genesis block hash matches `blockchain_fixture.genesis.block_hash`.
    2. The client's last block's hash matches `blockchain_fixture.last_block_hash`.
    """
    t_start = time.perf_counter()
    genesis_block = eth_rpc.get_block_by_number(0)
    timing_data.get_genesis = time.perf_counter() - t_start
    if genesis_block["hash"] != str(blockchain_fixture.genesis.block_hash):
        raise GenesisBlockMismatchException(
            expected_header=blockchain_fixture.genesis, got_header=FixtureHeader(**genesis_block)
        )
    block = eth_rpc.get_block_by_number("latest")
    timing_data.get_last_block = time.perf_counter() - timing_data.get_genesis - t_start
    assert block["hash"] == str(blockchain_fixture.last_block_hash), "hash mismatch in last block"
