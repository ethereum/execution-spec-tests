"""Build valid blocktests from fuzzer-generated transactions and pre-state."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import ethereum_test_forks
from ethereum_clis import GethTransitionTool, TransitionTool
from ethereum_test_fixtures import BlockchainFixture
from ethereum_test_specs import BlockchainTest

from .models import FuzzerOutput


class BlocktestBuilder:
    """Build valid blocktests from fuzzer-generated transactions."""

    def __init__(self, transition_tool: Optional[TransitionTool] = None):
        """Initialize the builder with optional transition tool."""
        self.t8n = transition_tool or GethTransitionTool()

    def build_blocktest(
        self,
        fuzzer_output: Dict[str, Any],
        num_blocks: int = 1,
        block_strategy: str = "distribute",
        block_time: int = 12,
    ) -> Dict[str, Any]:
        """Build a valid blocktest from fuzzer output."""
        # Parse and validate using Pydantic model
        fuzzer_data = FuzzerOutput(**fuzzer_output)

        # Get fork
        fork_name = fuzzer_data.fork
        fork = getattr(ethereum_test_forks, fork_name)

        # Create BlockchainTest
        if num_blocks == 1:
            # Single-block mode (backward compatible)
            test = BlockchainTest.from_fuzzer(fuzzer_output, fork)
        else:
            # Multi-block mode
            test = self._create_multiblock_test(
                fuzzer_data, fork, num_blocks, block_strategy, block_time
            )

        # Generate fixture
        fixture = test.generate(
            t8n=self.t8n,
            fork=fork,
            fixture_format=BlockchainFixture,
        )

        return fixture.model_dump(exclude_none=True, by_alias=True, mode="json")

    def build_and_save(self, fuzzer_output: Dict[str, Any], output_path: Path) -> Path:
        """Build blocktest and save to file."""
        blocktest = self.build_blocktest(fuzzer_output)
        fixtures = {"fuzzer_generated_test": blocktest}

        with open(output_path, "w") as f:
            json.dump(fixtures, f, indent=2)

        return output_path

    def _distribute_transactions(
        self, transactions: list, num_blocks: int, strategy: str
    ) -> list[list]:
        """Distribute transactions across multiple blocks."""
        if strategy == "first-block":
            # All transactions in first block, rest empty
            return [transactions] + [[] for _ in range(num_blocks - 1)]
        elif strategy == "distribute":
            # Sequential distribution to preserve nonce ordering
            # Splits transactions into consecutive chunks
            if not transactions:
                return [[] for _ in range(num_blocks)]

            result = []
            chunk_size = len(transactions) // num_blocks
            remainder = len(transactions) % num_blocks

            start = 0
            for i in range(num_blocks):
                # Distribute remainder across first blocks
                current_chunk_size = chunk_size + (1 if i < remainder else 0)
                end = start + current_chunk_size
                result.append(transactions[start:end])
                start = end

            return result
        else:
            raise ValueError(f"Unknown block strategy: {strategy}")

    def _create_multiblock_test(
        self,
        fuzzer_data: FuzzerOutput,
        fork,
        num_blocks: int,
        block_strategy: str,
        block_time: int,
    ) -> BlockchainTest:
        """Create a multi-block BlockchainTest from fuzzer output."""
        from ethereum_test_base_types import Address, Hash, HexNumber
        from ethereum_test_tools import Account, AuthorizationTuple, Block, Transaction
        from ethereum_test_types import Alloc, Environment

        # Build pre-state
        pre_dict: Dict[Address, Any] = {}
        for addr, account in fuzzer_data.accounts.items():
            pre_dict[addr] = Account(
                balance=account.balance,
                nonce=account.nonce,
                code=account.code,
                storage=account.storage,
            )
        pre = Alloc(pre_dict)

        # Build transactions
        transactions = []
        for tx in fuzzer_data.transactions:
            # Get private key for sender
            sender_account = fuzzer_data.accounts.get(tx.from_)
            if not sender_account or not sender_account.privateKey:
                raise ValueError(f"No private key for sender {tx.from_}")

            tx_params = {
                "sender": tx.from_,
                "secret_key": str(sender_account.privateKey),
                "to": tx.to,
                "value": tx.value,
                "gas_limit": tx.gas,
                "nonce": tx.nonce,
                "data": tx.data,
                "access_list": tx.accessList,
                "blob_versioned_hashes": tx.blobVersionedHashes,
            }

            # Handle gas pricing
            if tx.gasPrice:
                tx_params["gas_price"] = tx.gasPrice
            if tx.maxFeePerGas:
                tx_params["max_fee_per_gas"] = tx.maxFeePerGas
            if tx.maxPriorityFeePerGas:
                tx_params["max_priority_fee_per_gas"] = tx.maxPriorityFeePerGas

            # Handle authorization list (EIP-7702)
            if tx.authorizationList:
                tx_params["authorization_list"] = [
                    AuthorizationTuple(
                        chain_id=auth.chainId,
                        address=auth.address,
                        nonce=auth.nonce,
                        v=auth.v,
                        r=auth.r,
                        s=auth.s,
                    )
                    for auth in tx.authorizationList
                ]

            transactions.append(Transaction(**tx_params))

        # Distribute transactions across blocks
        tx_groups = self._distribute_transactions(transactions, num_blocks, block_strategy)

        # Build genesis environment
        env = fuzzer_data.env
        genesis_env = Environment(
            fee_recipient=env.currentCoinbase,
            difficulty=0,  # Post-merge
            gas_limit=int(env.currentGasLimit),
            number=0,
            timestamp=HexNumber(int(env.currentTimestamp) - 12),
            prev_randao=env.currentRandom or Hash(0),
            base_fee_per_gas=env.currentBaseFee if env.currentBaseFee else None,
            excess_blob_gas=env.currentExcessBlobGas if env.currentExcessBlobGas else None,
            blob_gas_used=env.currentBlobGasUsed if env.currentBlobGasUsed else None,
        )

        # Create blocks with incrementing timestamps
        base_timestamp = int(env.currentTimestamp)
        blocks = []
        for i, tx_group in enumerate(tx_groups):
            blocks.append(
                Block(
                    txs=tx_group,
                    timestamp=base_timestamp + (i * block_time),
                    fee_recipient=env.currentCoinbase,
                    parent_beacon_block_root=fuzzer_data.parentBeaconBlockRoot if i == 0 else None,
                )
            )

        # Return BlockchainTest instance
        return BlockchainTest(
            pre=pre,
            blocks=blocks,
            post={},  # Will be calculated during generation
            genesis_environment=genesis_env,
            chain_id=fuzzer_data.chainId,
        )


def build_blocktest_from_fuzzer(
    fuzzer_data: Dict[str, Any], t8n: Optional[TransitionTool] = None
) -> Dict[str, Any]:
    """Build blocktest from fuzzer output."""
    builder = BlocktestBuilder(t8n)
    return builder.build_blocktest(fuzzer_data)
