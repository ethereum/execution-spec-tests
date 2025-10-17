"""Helper functions for block production testing."""

from ethereum_test_base_types import Hash
from ethereum_test_rpc import EthRPC


def wait_for_transaction_in_mempool(
    eth_rpc: EthRPC,
    tx_hash: Hash,
    timeout: int = 10,
    poll_interval: float = 0.1,
) -> bool:
    """
    Wait for a transaction to appear in the mempool.
    """
    import time

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
