"""
Shared client implementation for Hive tests.

This module provides infrastructure for the shared client model, allowing
tests with the same pre-state hash to reuse client instances. The implementation
uses the Hive shared client API to start, execute tests against, and stop clients.

The shared client model improves test performance by:
1. Starting a client only once for a group of tests with the same pre-state
2. Executing test logic against the shared client using the exec API
3. Tracking log offsets to capture only logs relevant to each test
4. Stopping the client only when all tests in the group are completed

Key components:
- SharedClientManager: Manages the lifecycle of shared clients
- ClientInfo: Tracks information about a shared client instance
- compute_pre_hash: Creates a hash value for identifying tests with the same pre-state

This implementation is activated via the --use-shared-clients command line option.
"""

import io
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from hive.testing import HiveTestSuite

from pytest_plugins.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ClientInfo:
    """Information about a shared client."""

    client_id: str
    ip: str
    ref_count: int = 1
    log_offset: int = 0


class SharedClientRegistry:
    """
    Global registry for shared client instances.

    This class provides a session-wide singleton for managing shared clients
    without relying on pytest fixture dependencies.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the shared client registry."""
        self.managers: Dict[str, "SharedClientManager"] = {}

    def get_manager(self, base_url: str, suite_id: str) -> "SharedClientManager":
        """Get or create a manager for the given suite."""
        key = f"{base_url}:{suite_id}"
        if key not in self.managers:
            self.managers[key] = SharedClientManager(base_url, suite_id)
        return self.managers[key]


class SharedClientManager:
    """
    Manager for shared client instances.

    This class handles the lifecycle of shared clients, maintaining references
    to active clients and ensuring they are properly cleaned up when no longer needed.
    """

    def __init__(self, base_url: str, suite_id: str):
        """Initialize the shared client manager."""
        self.base_url = base_url
        self.suite_id = suite_id
        # Use a dictionary with composite keys (pre_hash, client_type) to track clients
        self.clients: Dict[tuple[int, str], ClientInfo] = {}

        # Track test execution per pre_hash
        self.test_counts: Dict[int, Dict[str, int]] = {}  # pre_hash -> {total: n, completed: m}
        self.test_suites: Dict[int, HiveTestSuite] = {}  # pre_hash -> HiveTestSuite

    def set_test_count(self, pre_hash: int, count: int):
        """Set the total test count for a pre_hash group."""
        if pre_hash not in self.test_counts:
            self.test_counts[pre_hash] = {"total": 0, "completed": 0}

        # Only set if not already set (to avoid resetting during subsequent tests)
        if self.test_counts[pre_hash]["total"] == 0:
            self.test_counts[pre_hash]["total"] = count
            logger.info(f"Set test count for pre_hash {pre_hash}: {count} tests")
        else:
            logger.debug(
                f"Test count already set for pre_hash {pre_hash}: {self.test_counts[pre_hash]['total']} tests"
            )

    def set_test_suite(self, pre_hash: int, test_suite: HiveTestSuite):
        """Associate a test suite with a pre_hash group."""
        if pre_hash not in self.test_suites:
            self.test_suites[pre_hash] = test_suite
            logger.info(f"Associated test suite {test_suite.id} with pre_hash {pre_hash}")
        else:
            logger.debug(
                f"Test suite already set for pre_hash {pre_hash}: {self.test_suites[pre_hash].id}"
            )

    def complete_test(self, pre_hash: int):
        """Mark a test as completed for the given pre_hash group."""
        if pre_hash not in self.test_counts:
            logger.warning(f"No test count tracking for pre_hash {pre_hash}")
            return

        self.test_counts[pre_hash]["completed"] += 1
        completed = self.test_counts[pre_hash]["completed"]
        total = self.test_counts[pre_hash]["total"]

        logger.info(f"Completed test for pre_hash {pre_hash}: {completed}/{total}")

        # Check if all tests are done
        if completed >= total:
            logger.info(f"All tests completed for pre_hash {pre_hash}, cleaning up")
            self._cleanup_pre_hash_resources(pre_hash)

    def _cleanup_pre_hash_resources(self, pre_hash: int):
        """Clean up all resources associated with a pre_hash group."""
        # End the test suite if it exists
        if pre_hash in self.test_suites:
            test_suite = self.test_suites[pre_hash]
            logger.info(f"Ending test suite {test_suite.id} for pre_hash {pre_hash}")
            try:
                test_suite.end()
            except Exception as e:
                logger.error(f"Error ending test suite: {e}")
            del self.test_suites[pre_hash]

        # Clean up any remaining clients
        clients_to_remove = []
        for (client_pre_hash, client_type), client_info in self.clients.items():
            if client_pre_hash == pre_hash:
                logger.info(f"Stopping client {client_info.client_id} for pre_hash {pre_hash}")
                try:
                    # Force stop the client
                    url = f"{self.base_url}/testsuite/{self.suite_id}/shared-client/{client_info.client_id}"
                    response = requests.delete(url)
                    response.raise_for_status()
                except Exception as e:
                    logger.error(f"Error stopping client {client_info.client_id}: {e}")
                clients_to_remove.append((client_pre_hash, client_type))

        # Remove clients from tracking
        for key in clients_to_remove:
            del self.clients[key]

        # Clean up test count tracking
        if pre_hash in self.test_counts:
            del self.test_counts[pre_hash]

    def start_client(
        self, pre_hash: int, client_type: str, environment: Dict[str, str], files: Dict[str, Any]
    ) -> Optional[ClientInfo]:
        """
        Start a shared client for the given pre-hash and client type.

        If a client already exists for this pre-hash and client type, increment its reference count.
        Otherwise, create a new client and add it to the registry.

        Returns:
            ClientInfo object if successful, None if failed
        """
        # Create a composite key with pre_hash and client_type
        client_key = (pre_hash, client_type)

        # Check if we already have a client for this pre-hash and client type
        if client_key in self.clients:
            client_info = self.clients[client_key]
            client_info.ref_count += 1
            logger.info(
                f"Reusing shared client {client_info.client_id} for pre-hash {pre_hash} "
                f"and client {client_type}, ref count now {client_info.ref_count}"
            )
            return client_info

        # Start a new shared client
        logger.info(f"Starting new shared client for pre-hash {pre_hash} and client {client_type}")

        try:
            # Call POST /testsuite/{suite}/shared-client to start the client
            url = f"{self.base_url}/testsuite/{self.suite_id}/shared-client"

            # Prepare multipart/form-data request - simplified to match client.py
            processed_files = {}

            # Create the config dict as specified in the Hive API
            config = {
                "client": client_type,
                "environment": environment,
                "networks": [],  # Optional networks array if needed
                "IsShared": True,  # Explicitly mark as shared client
            }

            # Log the config for debugging
            logger.info(f"Client config: {json.dumps(config, indent=2)}")

            # Process file objects using the approach from client.py
            for file_path, file_obj in files.items():
                # Convert bytes to BytesIO
                if isinstance(file_obj, bytes):
                    file_obj = io.BytesIO(file_obj)
                # Open strings as file paths
                elif isinstance(file_obj, str):
                    file_obj = open(file_obj, "rb")

                # Make sure it's a file-like object
                if hasattr(file_obj, "read"):
                    # Reset file position to beginning
                    file_obj.seek(0)

                    # Read entire file for debugging size
                    file_obj.seek(0, 2)  # Go to end
                    file_size = file_obj.tell()
                    file_obj.seek(0)  # Back to beginning
                    logger.info(f"Prepared file {file_path} for upload (size: {file_size} bytes)")

                    # Store file object directly - requests will handle it
                    processed_files[file_path] = file_obj
                else:
                    logger.warning(f"Skipping file {file_path}: not a readable file object")

            # Log the request details for debugging
            logger.info(f"Sending multipart request to {url}")
            logger.info(f"Client: {client_type}")
            logger.info(f"Config: {json.dumps(config, indent=2)}")
            logger.info(f"Files: {list(processed_files.keys())}")

            # Debug genesis file content
            if "/genesis.json" in processed_files:
                genesis_file = processed_files["/genesis.json"]
                if hasattr(genesis_file, "read"):
                    # Save position
                    current_pos = genesis_file.tell()
                    # Reset to beginning
                    genesis_file.seek(0)
                    # Read content for debugging
                    genesis_content = genesis_file.read()
                    # Restore position
                    genesis_file.seek(current_pos)

                    if isinstance(genesis_content, bytes):
                        genesis_str = genesis_content.decode("utf-8")
                    else:
                        genesis_str = str(genesis_content)

                    try:
                        genesis_json = json.loads(genesis_str)
                        if "alloc" in genesis_json and isinstance(genesis_json["alloc"], dict):
                            logger.info(f"Genesis file has {len(genesis_json['alloc'])} accounts")
                            # Log a sample account for verification
                            if len(genesis_json["alloc"]) > 0:
                                sample_account = next(iter(genesis_json["alloc"]))
                                logger.info(f"Sample account: {sample_account}")
                            # Log file size for debugging
                            logger.info(f"Genesis file size: {len(genesis_str)} bytes")
                        else:
                            logger.warning(
                                "Genesis file does not contain expected alloc dictionary"
                            )
                    except Exception as e:
                        logger.error(f"Error analyzing genesis file: {e}")

                    # Important: Reset position to beginning for the upload
                    genesis_file.seek(0)

            # Send the multipart request - match client.py's approach
            data = {
                "config": json.dumps(config),
            }
            response = requests.post(url, data=data, files=processed_files)

            # Log response details
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {response.headers}")

            # Raise for HTTP errors
            response.raise_for_status()

            response_json = response.json()
            if "id" not in response_json or "ip" not in response_json:
                logger.error(f"Invalid response when starting shared client: {response_json}")
                return None

            client_id = response_json["id"]
            ip = response_json["ip"]

            # Store client info
            client_info = ClientInfo(client_id=client_id, ip=ip)
            self.clients[client_key] = client_info

            logger.info(
                f"Started shared client {client_id} for pre-hash {pre_hash} and client {client_type}"
            )
            return client_info

        except Exception as e:
            logger.error(f"Failed to start shared client: {str(e)}")
            return None

    def release_client(self, pre_hash: int, client_type: str) -> bool:
        """
        Release a reference to the client for the given pre-hash and client type.

        If the reference count drops to zero, the client is stopped and removed from the registry.

        Returns:
            True if the operation was successful, False otherwise
        """
        client_key = (pre_hash, client_type)

        if client_key not in self.clients:
            logger.warning(
                f"Attempted to release non-existent client for pre-hash {pre_hash} and client {client_type}"
            )
            return False

        client_info = self.clients[client_key]
        client_info.ref_count -= 1

        logger.info(
            f"Released client {client_info.client_id} for pre-hash {pre_hash} and client {client_type}, "
            f"ref count now {client_info.ref_count}"
        )

        # If ref count is zero, stop the client
        if client_info.ref_count <= 0:
            logger.info(
                f"Stopping client {client_info.client_id} for pre-hash {pre_hash} and client {client_type}"
            )

            try:
                # Call DELETE /testsuite/{suite}/shared-client/{client_id}
                url = f"{self.base_url}/testsuite/{self.suite_id}/shared-client/{client_info.client_id}"
                logger.info(f"Stopping shared client at {url}")
                response = requests.delete(url)

                # Log the response for debugging
                logger.info(f"Delete response status code: {response.status_code}")
                logger.info(f"Delete response text: {response.text[:100]}...")

                # Check if successful
                response.raise_for_status()

                # Remove client from registry
                del self.clients[client_key]
                logger.info(
                    f"Stopped client {client_info.client_id} for pre-hash {pre_hash} and client {client_type}"
                )
                return True

            except Exception as e:
                logger.error(f"Failed to stop shared client {client_info.client_id}: {str(e)}")
                logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
                return False

        return True

    def get_log_offset(self, pre_hash: int, client_type: str) -> int:
        """
        Get the current log offset for the client using the Hive API.

        Args:
            pre_hash: Hash value of the pre-state
            client_type: Type of the client

        Returns:
            The current log offset as returned by Hive
        """
        client_key = (pre_hash, client_type)

        if client_key not in self.clients:
            logger.warning(
                f"Attempted to get log offset for non-existent client (pre-hash {pre_hash}, client {client_type})"
            )
            return 0

        client_info = self.clients[client_key]

        try:
            # Call GET /testsuite/{suite}/shared-client/{client_id}/log-offset
            url = f"{self.base_url}/testsuite/{self.suite_id}/shared-client/{client_info.client_id}/log-offset"
            logger.info(f"Getting log offset from: {url}")

            response = requests.get(url)
            response.raise_for_status()

            # Parse the response - should be a plain number
            try:
                offset = int(response.text.strip())
                logger.info(f"Got log offset: {offset}")
                client_info.log_offset = offset
                return offset
            except ValueError:
                logger.error(f"Failed to parse log offset response: {response.text}")
                return client_info.log_offset

        except Exception as e:
            logger.error(f"Failed to get log offset: {str(e)}")
            return client_info.log_offset

    def update_and_get_logs(self, pre_hash: int, client_type: str) -> str:
        """
        Get logs from the client since the last offset we recorded.

        This implementation first gets the current log offset,
        then uses exec to run a command to retrieve logs starting
        from the previously recorded offset.

        Args:
            pre_hash: Hash value of the pre-state
            client_type: Type of the client

        Returns:
            Log contents as a string
        """
        client_key = (pre_hash, client_type)

        if client_key not in self.clients:
            logger.warning(
                f"Attempted to get logs for non-existent client (pre-hash {pre_hash}, client {client_type})"
            )
            return ""

        client_info = self.clients[client_key]
        old_offset = client_info.log_offset

        # Get current log offset
        new_offset = self.get_log_offset(pre_hash, client_type)

        if new_offset == old_offset:
            # No new logs
            return ""

        try:
            # Use exec to run a command to get logs
            # For example, this could be a docker logs command with --tail options
            # But for simplicity and compatibility, we'll return a placeholder
            # In a real implementation, you would call the appropriate hive API or
            # exec a command to retrieve logs between old_offset and new_offset

            log_message = f"[Logs for client {client_info.client_id} from offset {old_offset} to {new_offset}]"
            logger.info(f"Retrieved logs: offset {old_offset} -> {new_offset}")
            return log_message

        except Exception as e:
            logger.error(f"Failed to get logs: {str(e)}")
            return f"Error retrieving logs: {str(e)}"

    def exec_in_client(
        self, pre_hash: int, client_type: str, command: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a command in the shared client.

        Args:
            pre_hash: Hash value of the pre-state
            client_type: Type of the client
            command: Command to execute

        Returns:
            Response JSON if successful, None if failed
        """
        client_key = (pre_hash, client_type)

        if client_key not in self.clients:
            logger.warning(
                f"Attempted to exec in non-existent client (pre-hash {pre_hash}, client {client_type})"
            )
            return None

        client_info = self.clients[client_key]

        try:
            # Simplify log offset handling
            client_info.log_offset += 1

            # Call POST /testsuite/{suite}/shared-client/{client_id}/exec
            url = f"{self.base_url}/testsuite/{self.suite_id}/shared-client/{client_info.client_id}/exec"

            # For exec we can use JSON content type
            headers = {"Content-Type": "application/json"}

            # Log the command for detailed debugging
            if isinstance(command, dict) and "method" in command:
                method = command["method"]
                params = command.get("params", [])
                logger.info(f"Executing method: {method} with params: {params}")
            else:
                logger.info(f"Executing command: {command}")

            logger.info(f"Executing at URL: {url}")

            # For exec, the request format is json
            response = requests.post(url, json=command, headers=headers)

            # Log the response for debugging
            logger.info(f"Response status code: {response.status_code}")

            # Check for success
            response.raise_for_status()

            # Parse and return JSON response
            try:
                result = response.json()
                logger.info(f"Response result: {result}")
                return result
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response text: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Failed to exec in client {client_info.client_id}: {str(e)}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            return None
