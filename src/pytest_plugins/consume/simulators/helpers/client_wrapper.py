"""Client wrapper classes for managing client lifecycle in engine simulators."""

import io
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, cast

from hive.client import Client, ClientType

from ethereum_test_base_types import Number, to_json
from ethereum_test_fixtures import BlockchainFixtureCommon
from ethereum_test_fixtures.pre_alloc_groups import PreAllocGroup
from ethereum_test_forks import Fork
from pytest_plugins.consume.simulators.helpers.ruleset import ruleset

from .test_tracker import PreAllocGroupTestTracker

logger = logging.getLogger(__name__)


class ClientWrapper(ABC):
    """
    Abstract base class for managing client instances in engine simulators.

    This class encapsulates the common logic for generating genesis configurations,
    environment variables, and client files needed to start a client.
    """

    def __init__(self, client_type: ClientType):
        """
        Initialize the client wrapper.

        Args:
            client_type: The type of client to manage

        """
        self.client_type = client_type
        self.client: Optional[Client] = None
        self._is_started = False
        self.test_count = 0

    @abstractmethod
    def _get_fork(self) -> Fork:
        """Get the fork for this client."""
        pass

    @abstractmethod
    def _get_chain_id(self) -> int:
        """Get the chain ID for this client."""
        pass

    @abstractmethod
    def _get_pre_alloc(self) -> dict:
        """Get the pre-allocation for this client."""
        pass

    @abstractmethod
    def _get_genesis_header(self) -> dict:
        """Get the genesis header for this client."""
        pass

    def get_genesis_config(self) -> dict:
        """
        Get the genesis configuration for this client.

        Returns:
            Genesis configuration dict

        """
        # Convert genesis header to JSON format
        genesis = self._get_genesis_header()

        # Convert pre-allocation to JSON format
        alloc = self._get_pre_alloc()

        # NOTE: nethermind requires account keys without '0x' prefix
        genesis["alloc"] = {k.replace("0x", ""): v for k, v in alloc.items()}

        return genesis

    def get_environment(self) -> dict:
        """
        Get the environment variables for this client.

        Returns:
            Environment variables dict

        """
        fork = self._get_fork()
        chain_id = self._get_chain_id()

        assert fork in ruleset, f"fork '{fork}' missing in hive ruleset"

        # Set check live port for engine simulator
        check_live_port = 8551  # Engine API port

        return {
            "HIVE_CHAIN_ID": str(Number(chain_id)),
            "HIVE_FORK_DAO_VOTE": "1",
            "HIVE_NODETYPE": "full",
            "HIVE_CHECK_LIVE_PORT": str(check_live_port),
            **{k: f"{v:d}" for k, v in ruleset[fork].items()},
        }

    def get_client_files(self) -> dict:
        """
        Get the client files dict needed for start_client().

        Returns:
            Dict with genesis.json file

        """
        # Create buffered genesis file
        genesis_config = self.get_genesis_config()
        genesis_json = json.dumps(genesis_config)
        genesis_bytes = genesis_json.encode("utf-8")
        buffered_genesis = io.BufferedReader(cast(io.RawIOBase, io.BytesIO(genesis_bytes)))

        return {"/genesis.json": buffered_genesis}

    def set_client(self, client: Client) -> None:
        """
        Set the client instance after it has been started.

        Args:
            client: The started client instance

        """
        if self._is_started:
            raise RuntimeError(f"Client {self.client_type.name} is already set")

        self.client = client
        self._is_started = True
        logger.info(f"Client ({self.client_type.name}) registered")

    def increment_test_count(self) -> None:
        """Increment the count of tests that have used this client."""
        self.test_count += 1
        logger.debug(f"Test count for {self.client_type.name}: {self.test_count}")

    def stop(self) -> None:
        """Mark the client as stopped."""
        if self._is_started:
            logger.info(
                f"Marking client ({self.client_type.name}) as stopped after {self.test_count} "
                "tests."
            )
            self.client = None
            self._is_started = False

    @property
    def is_running(self) -> bool:
        """Check if the client is currently running."""
        return self._is_started and self.client is not None


class RestartClient(ClientWrapper):
    """
    Client wrapper for the restart simulator where clients restart for each test.

    This class manages clients that are started and stopped for each individual test,
    providing complete isolation between test executions.
    """

    def __init__(self, client_type: ClientType, fixture: BlockchainFixtureCommon):
        """
        Initialize a restart client wrapper.

        Args:
            client_type: The type of client to manage
            fixture: The blockchain fixture for this test

        """
        super().__init__(client_type)
        self.fixture = fixture

    def _get_fork(self) -> Fork:
        """Get the fork from the fixture."""
        return self.fixture.fork

    def _get_chain_id(self) -> int:
        """Get the chain ID from the fixture config."""
        return self.fixture.config.chain_id

    def _get_pre_alloc(self) -> dict:
        """Get the pre-allocation from the fixture."""
        return to_json(self.fixture.pre)

    def _get_genesis_header(self) -> dict:
        """Get the genesis header from the fixture."""
        return to_json(self.fixture.genesis)


class MultiTestClient(ClientWrapper):
    """
    Client wrapper for multi-test execution where clients are used across tests.

    This class manages clients that are reused across multiple tests in the same
    pre-allocation group.
    """

    def __init__(
        self,
        pre_hash: str,
        client_type: ClientType,
        pre_alloc_group: PreAllocGroup,
    ):
        """
        Initialize a multi-test client wrapper.

        Args:
            pre_hash: The hash identifying the pre-allocation group
            client_type: The type of client to manage
            pre_alloc_group: The pre-allocation group data for this group

        """
        super().__init__(client_type)
        self.pre_hash = pre_hash
        self.pre_alloc_group = pre_alloc_group

    def _get_fork(self) -> Fork:
        """Get the fork from the pre-allocation group."""
        return self.pre_alloc_group.fork

    def _get_chain_id(self) -> int:
        """Get the chain ID from the pre-allocation group environment."""
        # TODO: Environment doesn't have chain_id field - see work_in_progress.md
        return 1

    def _get_pre_alloc(self) -> dict:
        """Get the pre-allocation from the pre-allocation group."""
        return to_json(self.pre_alloc_group.pre)

    def _get_genesis_header(self) -> dict:
        """Get the genesis header from the pre-allocation group."""
        return self.pre_alloc_group.genesis.model_dump(by_alias=True)

    def set_client(self, client: Client) -> None:
        """Override to log with pre_hash information."""
        if self._is_started:
            raise RuntimeError(f"Client for pre-allocation group {self.pre_hash} is already set")

        self.client = client
        self._is_started = True
        logger.info(
            f"Multi-test client ({self.client_type.name}) registered for pre-allocation group "
            f"{self.pre_hash}"
        )

    def stop(self) -> None:
        """Override to log with pre_hash information and actually stop the client."""
        if self._is_started:
            logger.info(
                f"Stopping multi-test client ({self.client_type.name}) for pre-allocation group "
                f"{self.pre_hash} after {self.test_count} tests"
            )
            # Actually stop the Hive client
            if self.client is not None:
                try:
                    self.client.stop()
                    logger.debug(f"Hive client stopped for pre-allocation group {self.pre_hash}")
                except Exception as e:
                    logger.error(
                        f"Error stopping Hive client for pre-allocation group {self.pre_hash}: {e}"
                    )

            self.client = None
            self._is_started = False


class MultiTestClientManager:
    """
    Singleton manager for coordinating multi-test clients across test execution.

    This class tracks all multi-test clients by their preHash and ensures proper
    lifecycle management including cleanup at session end.
    """

    _instance: Optional["MultiTestClientManager"] = None
    _initialized: bool

    def __new__(cls) -> "MultiTestClientManager":
        """Ensure only one instance of MultiTestClientManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the manager if not already initialized."""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.multi_test_clients: Dict[str, MultiTestClient] = {}
        self.pre_alloc_path: Optional[Path] = None
        self.test_tracker: Optional["PreAllocGroupTestTracker"] = None
        self._initialized = True
        logger.info("MultiTestClientManager initialized")

    def set_pre_alloc_path(self, path: Path) -> None:
        """
        Set the path to the pre-allocation files directory.

        Args:
            path: Path to the directory containing pre-allocation JSON files

        """
        self.pre_alloc_path = path
        logger.debug(f"Pre-alloc path set to: {path}")

    def set_test_tracker(self, test_tracker: "PreAllocGroupTestTracker") -> None:
        """
        Set the test tracker for automatic client cleanup.

        Args:
            test_tracker: The test tracker instance

        """
        self.test_tracker = test_tracker
        logger.debug("Test tracker set for automatic client cleanup")

    def load_pre_alloc_group(self, pre_hash: str) -> PreAllocGroup:
        """
        Load the pre-allocation group for a given preHash.

        Args:
            pre_hash: The hash identifying the pre-allocation group

        Returns:
            The loaded PreAllocGroup

        Raises:
            RuntimeError: If pre-alloc path is not set
            FileNotFoundError: If pre-allocation file is not found

        """
        if self.pre_alloc_path is None:
            raise RuntimeError("Pre-alloc path not set in MultiTestClientManager")

        pre_alloc_file = self.pre_alloc_path / f"{pre_hash}.json"
        if not pre_alloc_file.exists():
            raise FileNotFoundError(f"Pre-allocation file not found: {pre_alloc_file}")

        return PreAllocGroup.model_validate_json(pre_alloc_file.read_text())

    def get_or_create_multi_test_client(
        self,
        pre_hash: str,
        client_type: ClientType,
    ) -> MultiTestClient:
        """
        Get an existing MultiTestClient or create a new one for the given preHash.

        This method doesn't start the actual client - that's done by HiveTestSuite.
        It just manages the MultiTestClient wrapper objects.

        Args:
            pre_hash: The hash identifying the pre-allocation group
            client_type: The type of client that will be started

        Returns:
            The MultiTestClient wrapper instance

        """
        # Check if we already have a MultiTestClient for this preHash
        if pre_hash in self.multi_test_clients:
            multi_test_client = self.multi_test_clients[pre_hash]
            if multi_test_client.is_running:
                logger.debug(f"Found existing MultiTestClient for pre-allocation group {pre_hash}")
                return multi_test_client
            else:
                # MultiTestClient exists but isn't running, remove it
                logger.warning(
                    f"Found stopped MultiTestClient for pre-allocation group {pre_hash}, removing"
                )
                del self.multi_test_clients[pre_hash]

        # Load the pre-allocation group for this group
        pre_alloc_group = self.load_pre_alloc_group(pre_hash)

        # Create new MultiTestClient wrapper
        multi_test_client = MultiTestClient(
            pre_hash=pre_hash,
            client_type=client_type,
            pre_alloc_group=pre_alloc_group,
        )

        # Track the MultiTestClient
        self.multi_test_clients[pre_hash] = multi_test_client

        logger.info(
            f"Created new MultiTestClient wrapper for pre-allocation group {pre_hash} "
            f"(total tracked clients: {len(self.multi_test_clients)})"
        )

        return multi_test_client

    def get_client_for_test(
        self, pre_hash: str, test_id: Optional[str] = None
    ) -> Optional[Client]:
        """
        Get the actual client instance for a test with the given preHash.

        Args:
            pre_hash: The hash identifying the pre-allocation group
            test_id: Optional test ID for completion tracking

        Returns:
            The client instance if available, None otherwise

        """
        if pre_hash in self.multi_test_clients:
            multi_test_client = self.multi_test_clients[pre_hash]
            if multi_test_client.is_running:
                multi_test_client.increment_test_count()
                return multi_test_client.client
        return None

    def mark_test_completed(self, pre_hash: str, test_id: str) -> None:
        """
        Mark a test as completed and trigger automatic client cleanup if appropriate.

        Args:
            pre_hash: The hash identifying the pre-allocation group
            test_id: The unique test identifier

        """
        if self.test_tracker is None:
            logger.debug("No test tracker available, skipping completion tracking")
            return

        # Mark test as completed in tracker
        is_group_complete = self.test_tracker.mark_test_completed(pre_hash, test_id)

        if is_group_complete:
            # All tests in this pre-allocation group are complete
            self._auto_stop_client_if_complete(pre_hash)

    def _auto_stop_client_if_complete(self, pre_hash: str) -> None:
        """
        Automatically stop the client for a pre-allocation group if all tests are complete.

        Args:
            pre_hash: The hash identifying the pre-allocation group

        """
        if pre_hash not in self.multi_test_clients:
            logger.debug(f"No client found for pre-allocation group {pre_hash}")
            return

        multi_test_client = self.multi_test_clients[pre_hash]
        if not multi_test_client.is_running:
            logger.debug(f"Client for pre-allocation group {pre_hash} is already stopped")
            return

        # Stop the client and remove from tracking
        logger.info(
            f"Auto-stopping client for pre-allocation group {pre_hash} - "
            f"all tests completed ({multi_test_client.test_count} tests executed)"
        )

        try:
            multi_test_client.stop()
        except Exception as e:
            logger.error(f"Error auto-stopping client for pre-allocation group {pre_hash}: {e}")
        finally:
            # Remove from tracking to free memory
            del self.multi_test_clients[pre_hash]
            logger.debug(f"Removed completed client from tracking: {pre_hash}")

    def stop_all_clients(self) -> None:
        """Mark all multi-test clients as stopped."""
        logger.info(f"Marking all {len(self.multi_test_clients)} multi-test clients as stopped")

        for pre_hash, multi_test_client in list(self.multi_test_clients.items()):
            try:
                multi_test_client.stop()
            except Exception as e:
                logger.error(
                    f"Error stopping MultiTestClient for pre-allocation group {pre_hash}: {e}"
                )
            finally:
                del self.multi_test_clients[pre_hash]

        logger.info("All MultiTestClient wrappers cleared")

    def get_client_count(self) -> int:
        """Get the number of tracked multi-test clients."""
        return len(self.multi_test_clients)

    def get_test_counts(self) -> Dict[str, int]:
        """Get test counts for each multi-test client."""
        return {
            pre_hash: client.test_count for pre_hash, client in self.multi_test_clients.items()
        }

    def reset(self) -> None:
        """Reset the manager, clearing all state."""
        self.stop_all_clients()
        self.multi_test_clients.clear()
        self.pre_alloc_path = None
        self.test_tracker = None
        logger.info("MultiTestClientManager reset")
