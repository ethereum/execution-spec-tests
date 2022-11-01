"""
State test filler.
"""
import json
import os
import tempfile
from dataclasses import dataclass
from typing import Callable, Generator, List, Mapping, Tuple

from evm_block_builder import BlockBuilder
from evm_transition_tool import TransitionTool

from .base_test import (
    BaseTest,
    remove_transactions_from_rlp,
    verify_post_alloc,
    verify_transactions,
)
from .common import EmptyTrieRoot
from .fork import is_london
from .types import (
    Account,
    Environment,
    FixtureBlock,
    FixtureHeader,
    JSONEncoder,
    Transaction,
)


@dataclass
class StateTest(BaseTest):
    """
    Filler type that tests transactions over the period of a single block.
    """

    env: Environment
    pre: Mapping[str, Account]
    post: Mapping[str, Account]
    txs: List[Transaction]

    def make_genesis(
        self,
        b11r: BlockBuilder,
        t8n: TransitionTool,
        fork: str,
    ) -> FixtureHeader:
        """
        Create a genesis block from the state test definition.
        """
        genesis = FixtureHeader(
            parent_hash="0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
            ommers_hash="0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",  # noqa: E501
            coinbase="0x0000000000000000000000000000000000000000",
            state_root=t8n.calc_state_root(
                self.env,
                json.loads(json.dumps(self.pre, cls=JSONEncoder)),
                fork,
            ),
            transactions_root=EmptyTrieRoot,
            receipt_root=EmptyTrieRoot,
            bloom="0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
            difficulty=0x20000,
            number=self.env.number - 1,
            gas_limit=self.env.gas_limit,
            gas_used=0,
            timestamp=0,
            extra_data="0x00",
            mix_digest="0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
            nonce="0x0000000000000000",
            base_fee=self.env.base_fee,
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
        Create a block from the state test definition.
        Performs checks against the expected behavior of the test.
        Raises exception on invalid test behavior.
        """
        env = self.env.apply_new_parent(genesis)
        if env.base_fee is None and is_london(fork):
            env.base_fee = 7
        pre = json.loads(json.dumps(self.pre, cls=JSONEncoder))
        txs = json.loads(json.dumps(self.txs, cls=JSONEncoder))
        env = json.loads(json.dumps(env, cls=JSONEncoder))

        with tempfile.TemporaryDirectory() as directory:
            txsRlp = os.path.join(directory, "txs.rlp")
            (alloc, result) = t8n.evaluate(
                pre,
                txs,
                env,
                fork,
                txsPath=txsRlp,
                chain_id=chain_id,
                reward=reward,
            )
            with open(txsRlp, "r") as file:
                txs = file.read().strip('"')

        rejected_txs = verify_transactions(self.txs, result)
        if len(rejected_txs) > 0:
            txs = remove_transactions_from_rlp(txs, rejected_txs)

        verify_post_alloc(self.post, alloc)

        header = result | {
            "parentHash": genesis.hash,
            "miner": self.env.coinbase,
            "transactionsRoot": result.get("txRoot"),
            "difficulty": hex(self.env.difficulty)
            if self.env.difficulty is not None
            else result.get("currentDifficulty"),
            "number": str(self.env.number),
            "gasLimit": str(self.env.gas_limit),
            "timestamp": str(self.env.timestamp),
            "extraData": "0x00",
            "uncleHash": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",  # noqa: E501
            "mixDigest": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
            "nonce": "0x0000000000000000",
        }
        if self.env.base_fee is not None:
            header["baseFeePerGas"] = str(self.env.base_fee)
        block, head = b11r.build(header, txs, [], None)
        header["hash"] = head
        return (
            [
                FixtureBlock(
                    rlp=block,
                    block_header=FixtureHeader.from_dict(header),
                )
            ],
            head,
        )


StateTestSpec = Callable[[str], Generator[StateTest, None, None]]
