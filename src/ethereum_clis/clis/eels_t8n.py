"""
EELS T8N transition tool.

https://github.com/ethereum/execution-specs
"""

from abc import ABC, abstractmethod
from typing import List

from ethereum_clis import TransitionTool, TransitionToolOutput
from ethereum_test_base_types import BlobSchedule
from ethereum_test_forks import Fork
from ethereum_test_types import Alloc, Environment, Transaction


class EELST8NWrapper(TransitionTool, ABC):
    """
    Abstract base class for EELS T8N wrapper implementations.

    This class provides an interface for calling the EELS T8N entrypoint directly
    without going through a binary. It implements a registration mechanism for
    concrete implementations to be set as the default wrapper.

    Attributes:
        _default (class): The registered default subclass to use for instantiation.
                           Should be set via `set_default()`.

    Usage:
        1. Create a concrete subclass implementing all abstract methods
        2. Register it using `EELST8NWrapper.set_default(YourSubclass)`
        3. Instantiate via `EELST8NWrapper.default()`

    """

    _default = None

    @classmethod
    def set_default(cls, default_cls):
        """
        Register a default subclass for instantiation.

        Args:
            default_cls: The subclass to register as default

        Raises:
            TypeError: If `default_cls` is not a subclass of EELST8NWrapper

        """
        if not issubclass(default_cls, cls):
            raise TypeError(f"{default_cls.__name__} is not a subclass of {cls.__name__}")
        cls._default = default_cls

    @classmethod
    def default(cls, *args, **kwargs):
        """
        Instantiate the registered default implementation.

        Returns:
            Instance of the registered default subclass

        Raises:
            RuntimeError: If no default implementation has been registered

        """
        if cls._default is None:
            raise RuntimeError("Default subclass not set!")
        return cls._default(*args, **kwargs)

    @abstractmethod
    def version(self):
        """Return the version string of the transition tool implementation."""
        pass

    @abstractmethod
    def is_fork_supported(self, fork) -> bool:
        """Check if a specific fork is supported by the tool."""
        pass

    @abstractmethod
    def _evaluate_eels_t8n(
        self,
        *,
        t8n_data: TransitionTool.TransitionToolData,
        debug_output_path: str = "",
    ) -> TransitionToolOutput:
        """
        Execute the transition tool implementation (core functionality).

        This must be implemented by concrete subclasses to provide the actual
        transition tool evaluation logic.

        Args:
            t8n_data: Input data for the state transition
            debug_output_path: Optional path for writing debug output

        Returns:
            TransitionToolOutput: Result of the state transition

        """
        pass

    def evaluate(
        self,
        *,
        alloc: Alloc,
        txs: List[Transaction],
        env: Environment,
        fork: Fork,
        chain_id: int,
        reward: int,
        blob_schedule: BlobSchedule | None,
        debug_output_path: str = "",
        state_test: bool = False,
        slow_request: bool = False,
    ) -> TransitionToolOutput:
        """
        Execute the relevant evaluate method as required by the `t8n` tool.

        If a client's `t8n` tool varies from the default behavior, this method
        can be overridden.
        """
        fork_name = fork.transition_tool_name(
            block_number=env.number,
            timestamp=env.timestamp,
        )
        if env.number == 0:
            reward = -1
        t8n_data = self.TransitionToolData(
            alloc=alloc,
            txs=txs,
            env=env,
            fork_name=fork_name,
            chain_id=chain_id,
            reward=reward,
            blob_schedule=blob_schedule,
            state_test=state_test,
        )

        return self._evaluate_eels_t8n(t8n_data=t8n_data, debug_output_path=debug_output_path)
