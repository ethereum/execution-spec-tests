"""
Client proxy for shared clients.

This module provides a proxy that maintains the same interface as the standard hive.client.Client
but uses the shared client API behind the scenes. This allows existing test code to continue
working without modification while benefiting from the new shared client model.

The proxy transparently handles executing commands through the Hive shared client API
and captures logs for each test case, only returning logs that were generated during
the current test execution.

Key features:
- Maintains compatibility with existing tests
- Supports executing RPC commands via the shared client
- Captures only logs relevant to the current test
- Handles client lifecycle through the SharedClientManager
"""

from typing import Any, Dict, Optional

from pytest_plugins.logging import get_logger

from .shared_client import SharedClientManager

logger = get_logger(__name__)


class SharedClientProxy:
    """
    A proxy for the standard hive.client.Client class that works with the shared client API.

    This class provides compatibility with code that expects the standard Client interface
    but uses the shared client API underneath. This allows existing test code to continue
    working without modification.
    """

    def __init__(self, manager: SharedClientManager, pre_hash: int, client_type: str, client_id: str, ip: str):
        """Initialize the client proxy."""
        self._manager = manager
        self._pre_hash = pre_hash
        self._client_type = client_type
        self._client_id = client_id
        self.ip = ip

    def exec(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command in the shared client.

        Args:
            command: Command to execute (method and params)

        Returns:
            Response from the client

        Raises:
            Exception if execution fails
        """
        result = self._manager.exec_in_client(self._pre_hash, self._client_type, command)
        if result is None:
            raise Exception(f"Failed to execute command in shared client {self._client_id}")
        return result

    def get_logs(self) -> str:
        """
        Get the latest logs from the client.

        Returns:
            Latest logs as a string
        """
        return self._manager.update_and_get_logs(self._pre_hash, self._client_type)

    def stop(self) -> None:
        """
        Release a reference to the client.

        This does not actually stop the client unless this was the last reference.
        """
        # This is called automatically by the client fixture teardown
        # We just log it and let the reference counting handle actual stopping
        logger.info(f"Client.stop() called on shared client proxy for pre_hash {self._pre_hash} and client {self._client_type}")

    @property
    def client_id(self) -> str:
        """Get the client ID."""
        return self._client_id

    @property
    def pre_hash(self) -> int:
        """Get the pre-state hash."""
        return self._pre_hash
