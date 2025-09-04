"""
A request manager Ethereum  RPC calls.

The RequestManager handles transactions and block data retrieval from a remote Ethereum node,
utilizing Pydantic models to define the structure of transactions and blocks.

Classes:
- RequestManager: The main class for managing RPC requests and responses.
- RemoteTransaction: A Pydantic model representing a transaction retrieved from the node.
- RemoteBlock: A Pydantic model representing a block retrieved from the node.
"""

from typing import Dict

from config import EnvConfig
from ethereum_test_base_types import Hash
from ethereum_test_rpc import BlockNumberType, DebugRPC, EthRPC
from ethereum_test_rpc.types import TransactionByHashResponse
from ethereum_test_types import Environment


class RPCRequest:
    """Interface for the RPC interaction with remote node."""

    node_url: str
    headers: dict[str, str]

    def __init__(self):
        """Initialize the RequestManager with specific client config."""
        print("[DEBUG] Initializing RPCRequest...")
        node_config = EnvConfig().remote_nodes[0]
        self.node_url = node_config.node_url
        headers = node_config.rpc_headers

        print("[DEBUG] Config loaded:")
        print(f"  - Node URL: {self.node_url}")
        print(f"  - Headers: {headers}")

        self.rpc = EthRPC(node_config.node_url, extra_headers=headers)
        self.debug_rpc = DebugRPC(node_config.node_url, extra_headers=headers)
        print("[DEBUG] RPC clients initialized successfully")

    def eth_get_transaction_by_hash(self, transaction_hash: Hash) -> TransactionByHashResponse:
        """Get transaction data."""
        print(f"[DEBUG] Getting transaction by hash: {transaction_hash}")
        print(f"[DEBUG] Making eth_getTransactionByHash request to: {self.node_url}")

        try:
            res = self.rpc.get_transaction_by_hash(transaction_hash)
            assert res is not None, "Transaction not found"
            block_number = res.block_number
            assert block_number is not None, (
                "Transaction does not seem to be included in any block"
            )

            print(f"[DEBUG] Transaction found successfully in block: {block_number}")
            return res
        except Exception as e:
            print(f"[DEBUG] eth_getTransactionByHash failed: {e}")
            raise

    def eth_get_block_by_number(self, block_number: BlockNumberType) -> Environment:
        """Get block by number."""
        print(f"[DEBUG] Getting block by number: {block_number}")
        print(f"[DEBUG] Making eth_getBlockByNumber request to: {self.node_url}")

        try:
            res = self.rpc.get_block_by_number(block_number)

            env = Environment(
                fee_recipient=res["miner"],
                number=res["number"],
                difficulty=res["difficulty"],
                gas_limit=res["gasLimit"],
                timestamp=res["timestamp"],
            )
            print("[DEBUG] Block retrieved successfully")
            return env
        except Exception as e:
            print(f"[DEBUG] eth_getBlockByNumber failed: {e}")
            raise

    def debug_trace_call(self, transaction: TransactionByHashResponse) -> Dict[str, dict]:
        """Get pre-state required for transaction."""
        print("[DEBUG] Starting debug_trace_call...")
        assert transaction.sender is not None
        assert transaction.to is not None

        call_params = {
            "from": transaction.sender.hex(),
            "to": transaction.to.hex(),
            "data": transaction.data.hex(),
        }

        print("[DEBUG] debug_traceCall parameters:")
        print(f"  - URL: {self.node_url}")
        print(f"  - from: {call_params['from']}")
        print(f"  - to: {call_params['to']}")
        print(f"  - data: {call_params['data']}")
        print(f"  - block_number: {transaction.block_number}")
        print("  - tracer: prestateTracer")

        try:
            result = self.debug_rpc.trace_call(
                call_params,
                f"{transaction.block_number}",
            )
            print("[DEBUG] debug_trace_call completed successfully")
            return result
        except Exception as e:
            print(f"[DEBUG] debug_trace_call failed: {e}")
            raise
