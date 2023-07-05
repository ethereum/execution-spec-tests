"""
Transition tool abstract class.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from ethereum_test_forks import Fork


class TransitionTool:
    """
    Transition tool abstract base class which should be inherited by all transition tool
    implementations.
    """

    traces: List[List[List[Dict]]] | None = None

    registered_tools: List[Type["TransitionTool"]] = []
    default_tool: Optional[Type["TransitionTool"]] = None

    # Abstract methods that each tool must implement

    @abstractmethod
    def __init__(
        self,
        *,
        binary: Optional[Path | str] = None,
        trace: bool = False,
    ):
        """
        Abstract initialization method that all subclasses must implement.
        """
        pass

    def __init_subclass__(cls):
        """
        Registers all subclasses of TransitionTool as possible tools.
        """
        TransitionTool.register_tool(cls)

    @classmethod
    def register_tool(cls, tool_subclass: Type["TransitionTool"]):
        """
        Registers a given subclass as tool option.
        """
        cls.registered_tools.append(tool_subclass)

    @classmethod
    def set_default_tool(cls, tool_subclass: Type["TransitionTool"]):
        """
        Registers the default tool subclass.
        """
        cls.default_tool = tool_subclass

    @classmethod
    def from_binary_path(cls, *, binary_path: Optional[str]) -> Type["TransitionTool"]:
        """
        Returns the appropriate TransitionTool subclass derived from the binary path.
        """
        assert cls.default_tool is not None, "default transition tool was never set"

        if binary_path is None:
            return cls.default_tool

        for subclass in cls.registered_tools:
            if subclass.matches_binary_path(binary_path):
                return subclass

        return cls.default_tool

    @staticmethod
    @abstractmethod
    def matches_binary_path(binary_path: str) -> bool:
        """
        Returns True if the binary path matches the tool
        """
        pass

    @abstractmethod
    def evaluate(
        self,
        alloc: Any,
        txs: Any,
        env: Any,
        fork: Fork,
        chain_id: int = 1,
        reward: int = 0,
        eips: Optional[List[int]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Simulate a state transition with specified parameters
        """
        pass

    @abstractmethod
    def version(self) -> str:
        """
        Return name and version of tool used to state transition
        """
        pass

    @abstractmethod
    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool
        """
        pass

    def reset_traces(self):
        """
        Resets the internal trace storage for a new test to begin
        """
        self.traces = None

    def append_traces(self, new_traces: List[List[Dict]]):
        """
        Appends a list of traces of a state transition to the current list
        """
        if self.traces is None:
            self.traces = []
        self.traces.append(new_traces)

    def get_traces(self) -> List[List[List[Dict]]] | None:
        """
        Returns the accumulated traces
        """
        return self.traces

    def calc_state_root(self, alloc: Any, fork: Fork) -> bytes:
        """
        Calculate the state root for the given `alloc`.
        """
        env: Dict[str, Any] = {
            "currentCoinbase": "0x0000000000000000000000000000000000000000",
            "currentDifficulty": "0x0",
            "currentGasLimit": "0x0",
            "currentNumber": "0",
            "currentTimestamp": "0",
        }

        if fork.header_base_fee_required(0, 0):
            env["currentBaseFee"] = "7"

        if fork.header_prev_randao_required(0, 0):
            env["currentRandom"] = "0"

        if fork.header_withdrawals_required(0, 0):
            env["withdrawals"] = []

        _, result = self.evaluate(alloc, [], env, fork)
        state_root = result.get("stateRoot")
        if state_root is None or not isinstance(state_root, str):
            raise Exception("Unable to calculate state root")
        return bytes.fromhex(state_root[2:])

    def calc_withdrawals_root(self, withdrawals: Any, fork: Fork) -> bytes:
        """
        Calculate the state root for the given `alloc`.
        """
        if type(withdrawals) is list and len(withdrawals) == 0:
            # Optimize returning the empty root immediately
            return bytes.fromhex(
                "56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"
            )

        env: Dict[str, Any] = {
            "currentCoinbase": "0x0000000000000000000000000000000000000000",
            "currentDifficulty": "0x0",
            "currentGasLimit": "0x0",
            "currentNumber": "0",
            "currentTimestamp": "0",
            "withdrawals": withdrawals,
        }

        if fork.header_base_fee_required(0, 0):
            env["currentBaseFee"] = "7"

        if fork.header_prev_randao_required(0, 0):
            env["currentRandom"] = "0"

        if fork.header_excess_data_gas_required(0, 0):
            env["currentExcessDataGas"] = "0"

        _, result = self.evaluate({}, [], env, fork)
        withdrawals_root = result.get("withdrawalsRoot")
        if withdrawals_root is None:
            raise Exception(
                "Unable to calculate withdrawals root: no value returned from transition tool"
            )
        if type(withdrawals_root) is not str:
            raise Exception(
                "Unable to calculate withdrawals root: "
                + "incorrect type returned from transition tool: "
                + f"{withdrawals_root}"
            )
        return bytes.fromhex(withdrawals_root[2:])
