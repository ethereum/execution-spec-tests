"""Helper functions for block production testing."""

import time
from typing import Any

from ethereum_test_base_types import Bytes, Hash
from ethereum_test_rpc import EthRPC


def wait_for_transaction_in_mempool(
    eth_rpc: EthRPC,
    tx_hash: Hash,
    timeout: int = 10,
    poll_interval: float = 0.1,
) -> bool:
    """
    Wait for a transaction to appear in the mempool.

    Returns True if transaction found, False if timeout reached.
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            tx = eth_rpc.get_transaction_by_hash(tx_hash)
            if tx is not None:
                return True
        except Exception:
            pass
        time.sleep(poll_interval)

    return False


def wait_for_payload_ready(
    engine_rpc: Any,
    payload_id: Bytes,
    get_payload_version: int,
    timeout: float = 5.0,
    poll_interval: float = 0.1,
) -> Any:
    """
    Poll until payload is ready to be retrieved.

    Returns the built payload response when ready.
    Raises TimeoutError if not ready within timeout.
    """
    start = time.time()
    last_exception = None

    while time.time() - start < timeout:
        try:
            built_payload_response = engine_rpc.get_payload(
                payload_id=payload_id,
                version=get_payload_version,
            )
            return built_payload_response
        except Exception as e:
            last_exception = e
            time.sleep(poll_interval)

    elapsed = time.time() - start
    raise TimeoutError(f"Payload not ready after {elapsed:.2f}s. Last error: {last_exception}")
