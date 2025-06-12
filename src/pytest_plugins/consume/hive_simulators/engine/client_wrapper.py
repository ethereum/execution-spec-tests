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
from ethereum_test_fixtures.shared_alloc import SharedPreStateGroup
from ethereum_test_forks import Fork
from pytest_plugins.consume.hive_simulators.ruleset import ruleset

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


class ReorgClient(ClientWrapper):
    """
    Client wrapper for the reorg simulator where clients are shared across tests.

    This class manages clients that are reused across multiple tests in the same
    pre-allocation group, using blockchain reorganization to reset state between tests.
    """

    def __init__(
        self,
        pre_hash: str,
        client_type: ClientType,
        shared_pre_state: SharedPreStateGroup,
    ):
        """
        Initialize a reorg client wrapper.

        Args:
            pre_hash: The hash identifying the pre-allocation group
            client_type: The type of client to manage
            shared_pre_state: The shared pre-state data for this group

        """
        super().__init__(client_type)
        self.pre_hash = pre_hash
        self.shared_pre_state = shared_pre_state

    def _get_fork(self) -> Fork:
        """Get the fork from the shared pre-state."""
        return self.shared_pre_state.fork

    def _get_chain_id(self) -> int:
        """Get the chain ID from the shared pre-state environment."""
        # TODO: Environment doesn't have chain_id field - see work_in_progress.md
        return 1

    def _get_pre_alloc(self) -> dict:
        """Get the pre-allocation from the shared pre-state."""
        return to_json(self.shared_pre_state.pre)

    def _get_genesis_header(self) -> dict:
        """Get the genesis header from the shared pre-state."""
        return self.shared_pre_state.genesis().model_dump(by_alias=True)

    def set_client(self, client: Client) -> None:
        """Override to log with pre_hash information."""
        if self._is_started:
            raise RuntimeError(f"Client for preHash {self.pre_hash} is already set")

        self.client = client
        self._is_started = True
        logger.info(
            f"Reorg client ({self.client_type.name}) registered for preHash {self.pre_hash}"
        )

    def stop(self) -> None:
        """Override to log with pre_hash information."""
        if self._is_started:
            logger.info(
                f"Marking reorg client ({self.client_type.name}) for preHash {self.pre_hash} "
                f"as stopped after {self.test_count} tests"
            )
            self.client = None
            self._is_started = False


class ReorgClientManager:
    """
    Singleton manager for coordinating reorg clients across test execution.

    This class tracks all reorg clients by their preHash and ensures proper
    lifecycle management including cleanup at session end.
    """

    _instance: Optional["ReorgClientManager"] = None
    _initialized: bool

    def __new__(cls) -> "ReorgClientManager":
        """Ensure only one instance of ReorgClientManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the manager if not already initialized."""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.reorg_clients: Dict[str, ReorgClient] = {}
        self.pre_alloc_path: Optional[Path] = None
        self._initialized = True
        logger.info("ReorgClientManager initialized")

    def set_pre_alloc_path(self, path: Path) -> None:
        """
        Set the path to the pre-allocation files directory.

        Args:
            path: Path to the directory containing pre-allocation JSON files

        """
        self.pre_alloc_path = path
        logger.debug(f"Pre-alloc path set to: {path}")

    def load_shared_pre_state(self, pre_hash: str) -> SharedPreStateGroup:
        """
        Load the shared pre-state for a given preHash.

        Args:
            pre_hash: The hash identifying the pre-allocation group

        Returns:
            The loaded SharedPreStateGroup

        Raises:
            RuntimeError: If pre-alloc path is not set
            FileNotFoundError: If pre-allocation file is not found

        """
        if self.pre_alloc_path is None:
            raise RuntimeError("Pre-alloc path not set in ReorgClientManager")

        pre_alloc_file = self.pre_alloc_path / f"{pre_hash}.json"
        if not pre_alloc_file.exists():
            raise FileNotFoundError(f"Pre-allocation file not found: {pre_alloc_file}")

        return SharedPreStateGroup.model_validate_json(pre_alloc_file.read_text())

    def get_or_create_reorg_client(
        self,
        pre_hash: str,
        client_type: ClientType,
    ) -> ReorgClient:
        """
        Get an existing ReorgClient or create a new one for the given preHash.

        This method doesn't start the actual client - that's done by HiveTestSuite.
        It just manages the ReorgClient wrapper objects.

        Args:
            pre_hash: The hash identifying the pre-allocation group
            client_type: The type of client that will be started

        Returns:
            The ReorgClient wrapper instance

        """
        # Check if we already have a ReorgClient for this preHash
        if pre_hash in self.reorg_clients:
            reorg_client = self.reorg_clients[pre_hash]
            if reorg_client.is_running:
                logger.debug(f"Found existing ReorgClient for preHash {pre_hash}")
                return reorg_client
            else:
                # ReorgClient exists but isn't running, remove it
                logger.warning(f"Found stopped ReorgClient for preHash {pre_hash}, removing")
                del self.reorg_clients[pre_hash]

        # Load the shared pre-state for this group
        shared_pre_state = self.load_shared_pre_state(pre_hash)

        # Create new ReorgClient wrapper
        reorg_client = ReorgClient(
            pre_hash=pre_hash,
            client_type=client_type,
            shared_pre_state=shared_pre_state,
        )

        # Track the ReorgClient
        self.reorg_clients[pre_hash] = reorg_client

        logger.info(
            f"Created new ReorgClient wrapper for preHash {pre_hash} "
            f"(total tracked clients: {len(self.reorg_clients)})"
        )

        return reorg_client

    def get_client_for_test(self, pre_hash: str) -> Optional[Client]:
        """
        Get the actual client instance for a test with the given preHash.

        Args:
            pre_hash: The hash identifying the pre-allocation group

        Returns:
            The client instance if available, None otherwise

        """
        if pre_hash in self.reorg_clients:
            reorg_client = self.reorg_clients[pre_hash]
            if reorg_client.is_running:
                reorg_client.increment_test_count()
                return reorg_client.client
        return None

    def stop_all_clients(self) -> None:
        """Mark all reorg clients as stopped."""
        logger.info(f"Marking all {len(self.reorg_clients)} reorg clients as stopped")

        for pre_hash, reorg_client in list(self.reorg_clients.items()):
            try:
                reorg_client.stop()
            except Exception as e:
                logger.error(f"Error stopping ReorgClient for preHash {pre_hash}: {e}")
            finally:
                del self.reorg_clients[pre_hash]

        logger.info("All ReorgClient wrappers cleared")

    def get_client_count(self) -> int:
        """Get the number of tracked reorg clients."""
        return len(self.reorg_clients)

    def get_test_counts(self) -> Dict[str, int]:
        """Get test counts for each reorg client."""
        return {pre_hash: client.test_count for pre_hash, client in self.reorg_clients.items()}

    def reset(self) -> None:
        """Reset the manager, clearing all state."""
        self.stop_all_clients()
        self.reorg_clients.clear()
        self.pre_alloc_path = None
        logger.info("ReorgClientManager reset")
