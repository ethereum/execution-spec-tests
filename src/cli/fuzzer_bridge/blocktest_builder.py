"""Build valid blocktests from fuzzer-generated transactions and pre-state."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import ethereum_test_forks
from ethereum_clis import GethTransitionTool, TransitionTool
from ethereum_test_base_types import Address, Hash, HexNumber
from ethereum_test_fixtures import BlockchainFixture
from ethereum_test_specs import BlockchainTest
from ethereum_test_tools import Account, Alloc, Block, Environment, Transaction
from ethereum_test_types import Withdrawal


class BlocktestBuilder:
    """Build valid blocktests from fuzzer-generated transactions."""

    def __init__(self, transition_tool: Optional[TransitionTool] = None):
        """Initialize the builder with optional transition tool."""
        self.t8n = transition_tool or GethTransitionTool()

    def _parse_pre_state(self, accounts: Dict[str, Any]) -> tuple[Alloc, Dict[Address, str]]:
        """Parse pre-state accounts and private keys."""
        pre_dict: Dict[Address, Account | None] = {}
        private_keys: Dict[Address, str] = {}

        for addr_str, account_data in accounts.items():
            addr = Address(addr_str)
            pre_dict[addr] = Account(
                balance=HexNumber(account_data.get("balance", "0x0")),
                nonce=HexNumber(account_data.get("nonce", "0x0")),
                code=account_data.get("code", ""),
                storage=account_data.get("storage", {}),
            )
            if "privateKey" in account_data:
                private_keys[addr] = account_data["privateKey"]

        return Alloc(pre_dict), private_keys

    def _parse_transactions(
        self, tx_list: List[Dict[str, Any]], private_keys: Dict[Address, str]
    ) -> List[Transaction]:
        """Parse transactions from fuzzer output."""
        transactions = []
        for tx_data in tx_list:
            sender = Address(tx_data.get("from", tx_data.get("sender")))
            transactions.append(
                Transaction(
                    sender=sender,
                    secret_key=private_keys.get(sender),
                    to=Address(tx_data["to"]) if tx_data.get("to") else None,
                    value=HexNumber(tx_data.get("value", "0x0")),
                    gas_limit=HexNumber(tx_data.get("gas", tx_data.get("gasLimit", "0x5208"))),
                    gas_price=HexNumber(tx_data.get("gasPrice", "0x1")),
                    nonce=HexNumber(tx_data.get("nonce", "0x0")),
                    data=tx_data.get("data", tx_data.get("input", "")),
                    max_fee_per_gas=HexNumber(tx_data["maxFeePerGas"])
                    if "maxFeePerGas" in tx_data
                    else None,
                    max_priority_fee_per_gas=HexNumber(tx_data["maxPriorityFeePerGas"])
                    if "maxPriorityFeePerGas" in tx_data
                    else None,
                    access_list=tx_data.get("accessList"),
                    blob_versioned_hashes=tx_data.get("blobVersionedHashes"),
                )
            )
        return transactions

    def _parse_environment(self, env_data: Dict[str, Any]) -> Environment:
        """Parse environment from fuzzer output."""
        return Environment(
            fee_recipient=Address(env_data.get("currentCoinbase")),
            difficulty=0,  # Post-merge
            gas_limit=int(env_data.get("currentGasLimit", "0x1000000"), 16),
            number=0,
            timestamp=HexNumber(int(env_data.get("currentTimestamp", "0x1000"), 16) - 12),
            prev_randao=Hash(
                env_data.get(
                    "currentRandom",
                    env_data.get(
                        "prevRandao",
                        "0x0000000000000000000000000000000000000000000000000000000000000000",
                    ),
                )
            ),
            base_fee_per_gas=HexNumber(env_data.get("currentBaseFee", "0x7"))
            if "currentBaseFee" in env_data
            else None,
            excess_blob_gas=HexNumber(env_data.get("currentExcessBlobGas", "0x0"))
            if "currentExcessBlobGas" in env_data
            else None,
            withdrawals=self._parse_withdrawals(env_data.get("withdrawals")),
        )

    def parse_fuzzer_output(self, fuzzer_data: Dict[str, Any]) -> tuple:
        """Parse fuzzer output format into test components."""
        # Parse accounts and private keys
        accounts = fuzzer_data.get("accounts", fuzzer_data.get("pre", {}))
        pre, private_keys = self._parse_pre_state(accounts)

        # Parse transactions
        transactions = self._parse_transactions(fuzzer_data.get("transactions", []), private_keys)

        # Parse environment
        env = self._parse_environment(fuzzer_data.get("env", {}))

        # Parse fork
        fork_name = fuzzer_data.get("fork", "Prague")
        fork = getattr(ethereum_test_forks, fork_name)

        # Parse chain ID
        chain_id_raw = fuzzer_data.get("chainId", fuzzer_data.get("chainid", "1"))
        chain_id = int(chain_id_raw, 16) if isinstance(chain_id_raw, str) else chain_id_raw

        return pre, transactions, env, fork, chain_id

    def _parse_withdrawals(self, withdrawals_data: Optional[List]) -> Optional[List[Withdrawal]]:
        """Parse withdrawals from fuzzer data."""
        if not withdrawals_data:
            return None

        withdrawals = []
        for w in withdrawals_data:
            withdrawals.append(
                Withdrawal(
                    index=HexNumber(w["index"]),
                    validator_index=HexNumber(w["validatorIndex"]),
                    address=Address(w["address"]),
                    amount=HexNumber(w["amount"]),
                )
            )
        return withdrawals

    def build_blocktest(self, fuzzer_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build a valid blocktest from fuzzer output."""
        pre, transactions, env, fork, chain_id = self.parse_fuzzer_output(fuzzer_output)

        # Create block with transactions (block 1)
        env_data = fuzzer_output.get("env", {})
        block = Block(
            txs=transactions,
            timestamp=int(env_data.get("currentTimestamp", "0x1000"), 16),
            fee_recipient=Address(env_data.get("currentCoinbase")),
        )

        # Create blockchain test
        test = BlockchainTest(
            pre=pre,
            blocks=[block],
            post={},  # Calculated during generation
            genesis_environment=env,
            chain_id=chain_id,
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


def build_blocktest_from_fuzzer(
    fuzzer_data: Dict[str, Any], t8n: Optional[TransitionTool] = None
) -> Dict[str, Any]:
    """Build blocktest from fuzzer output."""
    builder = BlocktestBuilder(t8n)
    return builder.build_blocktest(fuzzer_data)
