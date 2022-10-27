"""
Blockchain test filler.
"""

import json
import os
import tempfile
from dataclasses import dataclass
from typing import Callable, Generator, List, Mapping, Tuple

from ethereum_test.fork import is_london
from evm_block_builder import BlockBuilder
from evm_transition_tool import TransitionTool

from .base_test import (
    BaseTest,
    remove_transactions_from_rlp,
    verify_post_alloc,
    verify_transactions,
)
from .common import EmptyTrieRoot
from .types import (
    Account,
    Block,
    Environment,
    FixtureBlock,
    FixtureHeader,
    JSONEncoder,
)


@dataclass(kw_only=True)
class BlockchainTest(BaseTest):
    """
    Filler type that tests multiple blocks (valid or invalid) in a chain.
    """

    pre: Mapping[str, Account]
    post: Mapping[str, Account]
    blocks: List[Block]
    genesis_environment: Environment = Environment()

    def make_genesis(
        self,
        b11r: BlockBuilder,
        t8n: TransitionTool,
        fork: str,
    ) -> FixtureHeader:
        """
        Create a genesis block from the state test definition.
        """
        if is_london(fork) and self.genesis_environment.base_fee is None:
            self.genesis_environment.base_fee = 7
        genesis = FixtureHeader(
            parent_hash="0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
            ommers_hash="0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",  # noqa: E501
            coinbase="0x0000000000000000000000000000000000000000",
            state_root=t8n.calc_state_root(
                self.genesis_environment,
                json.loads(json.dumps(self.pre, cls=JSONEncoder)),
                fork,
            ),
            transactions_root=EmptyTrieRoot,
            receipt_root=EmptyTrieRoot,
            bloom="0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
            difficulty=0x20000,
            number=0,
            gas_limit=self.genesis_environment.gas_limit,
            gas_used=0,
            timestamp=0,
            extra_data="0x00",
            mix_digest="0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
            nonce="0x0000000000000000",
            base_fee=self.genesis_environment.base_fee,
        )

        (_, h) = b11r.build(genesis.to_geth_dict(), "", [])
        genesis.hash = h

        return genesis

    def make_blocks(
        self,
        b11r: BlockBuilder,
        t8n: TransitionTool,
        genesis: FixtureHeader,
        fork: str,
        chain_id=1,
        reward=0,
    ) -> Tuple[List[FixtureBlock], str]:
        """
        Create a block list from the blockchain test definition.
        Performs checks against the expected behavior of the test.
        Raises exception on invalid test behavior.
        """
        prev_alloc = json.loads(json.dumps(self.pre, cls=JSONEncoder))
        env = Environment(
            parent_difficulty=genesis.difficulty,
            parent_timestamp=genesis.timestamp,
            parent_base_fee=genesis.base_fee,
            parent_gas_used=genesis.gas_used,
            parent_gas_limit=genesis.gas_limit,
            parent_uncle_hash=genesis.ommers_hash,
            block_hashes={
                genesis.number: genesis.hash
                if genesis.hash is not None
                else "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
            },
        )
        blocks: List[FixtureBlock] = []
        # head_number = self.env.number
        head = genesis.hash if genesis.hash is not None else ""
        for block in self.blocks:
            current_alloc = None
            rlp = None
            if block.rlp and block.exception is not None:
                raise Exception(
                    "test correctness: post-state cannot be verified if the "
                    + "block's rlp is supplied and the block is not supposed "
                    + "to produce an exception"
                )

            if block.rlp is None:
                """
                This is the most common case, the RLP needs to be constructed
                based on the transactions to be included in the block.
                """
                txs = json.loads(
                    json.dumps(
                        block.txs if block.txs is not None else [],
                        cls=JSONEncoder,
                    )
                )
                """
                Set the environment according to the block to execute.
                """
                env = block.set_environment(env)

                with tempfile.TemporaryDirectory() as directory:
                    txsRlp = os.path.join(directory, "txs.rlp")
                    (current_alloc, result) = t8n.evaluate(
                        prev_alloc,
                        txs,
                        json.loads(json.dumps(env, cls=JSONEncoder)),
                        fork,
                        txsPath=txsRlp,
                        chain_id=chain_id,
                        reward=reward,
                    )
                    with open(txsRlp, "r") as file:
                        txs = file.read().strip('"')

                rejected_txs = verify_transactions(block.txs, result)
                if len(rejected_txs) > 0:
                    txs = remove_transactions_from_rlp(txs, rejected_txs)

                header = FixtureHeader.from_dict(
                    result
                    | {
                        "parentHash": env.parent_hash(),
                        "miner": env.coinbase,
                        "transactionsRoot": result.get("txRoot"),
                        "difficulty": result.get("currentDifficulty"),
                        "number": str(env.number),
                        "gasLimit": str(env.gas_limit),
                        "timestamp": str(env.timestamp),
                        "extraData": block.extra_data
                        if block.extra_data is not None
                        and len(block.extra_data) != 0
                        else "0x",
                        "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",  # noqa: E501
                        "mixDigest": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                        "nonce": "0x0000000000000000",
                        "baseFeePerGas": result.get("currentBaseFee"),
                    }
                )

                if block.rlp_modifier is not None:
                    header |= json.loads(
                        json.dumps(block.rlp_modifier, cls=JSONEncoder)
                    )

                rlp, header.hash = b11r.build(
                    header.to_geth_dict(), txs, [], None
                )

                if block.exception is None:
                    head = header.hash

                    """
                    Update environment for the following block
                    """
                    env.parent_base_fee = header.base_fee
                    env.parent_difficulty = header.difficulty
                    env.parent_timestamp = header.timestamp
                    env.parent_gas_used = header.gas_used
                    env.parent_gas_limit = header.gas_limit
                    env.parent_uncle_hash = header.ommers_hash

                    # Add hash to the list of previous hashes
                    env.block_hashes[header.number] = header.hash

                    # Update the allocation to the latest
                    prev_alloc = current_alloc
                    blocks.append(
                        FixtureBlock(
                            rlp=rlp,
                            block_header=header,
                            expected_exception=block.exception,
                        )
                    )
            else:
                rlp = block.rlp

                blocks.append(
                    FixtureBlock(
                        rlp=rlp,
                        expected_exception=block.exception,
                    )
                )

        verify_post_alloc(self.post, prev_alloc)

        return (blocks, head)


BlockchainTestSpec = Callable[[str], Generator[BlockchainTest, None, None]]
