"""
Python wrapper for the `evm t8n` tool.
"""

import json
import os
import subprocess
import tempfile
from abc import abstractmethod
from pathlib import Path
from shutil import which
from typing import Any, Dict, List, Optional, Tuple, Type

from ethereum_test_forks import Fork


class TransitionTool:
    """
    Transition tool frontend.
    """

    traces: List[List[List[Dict]]] | None = None

    # Static methods

    @staticmethod
    def from_binary_path(*, binary_path: Optional[str]) -> Type["TransitionTool"]:
        """
        Returns the appropriate TransitionTool subclass derived from the binary path.
        """
        if binary_path and "evmone-t8n" in binary_path:
            return EvmOneTransitionTool

        return EvmTransitionTool

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

    def write_json_file(self, data: Dict[str, Any], file_path: str) -> None:
        """
        Write a JSON file to the given path.
        """
        with open(file_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


class EvmTransitionTool(TransitionTool):
    """
    Go-ethereum `evm` Transition tool frontend.
    """

    binary: Path
    cached_version: Optional[str] = None
    trace: bool

    def __init__(
        self,
        *,
        binary: Optional[Path | str] = None,
        trace: bool = False,
    ):
        if binary is None or type(binary) is str:
            if binary is None:
                binary = "evm"
            which_path = which(binary)
            if which_path is not None:
                binary = Path(which_path)
        if binary is None or not Path(binary).exists():
            raise Exception(
                """`evm` binary executable is not accessible, please refer to
                https://github.com/ethereum/go-ethereum on how to compile and
                install the full suite of utilities including the `evm` tool"""
            )
        self.binary = Path(binary)
        self.trace = trace
        args = [str(self.binary), "t8n", "--help"]
        try:
            result = subprocess.run(args, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception("evm process unexpectedly returned a non-zero status code: " f"{e}.")
        except Exception as e:
            raise Exception(f"Unexpected exception calling evm tool: {e}.")
        self.help_string = result.stdout

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
        Executes `evm t8n` with the specified arguments.
        """
        fork_name = fork.name()
        if eips is not None:
            fork_name = "+".join([fork_name] + [str(eip) for eip in eips])

        temp_dir = tempfile.TemporaryDirectory()

        if int(env["currentNumber"], 0) == 0:
            reward = -1
        args = [
            str(self.binary),
            "t8n",
            "--input.alloc=stdin",
            "--input.txs=stdin",
            "--input.env=stdin",
            "--output.result=stdout",
            "--output.alloc=stdout",
            "--output.body=txs.rlp",
            f"--output.basedir={temp_dir.name}",
            f"--state.fork={fork_name}",
            f"--state.chainid={chain_id}",
            f"--state.reward={reward}",
        ]

        if self.trace:
            args.append("--trace")

        stdin = {
            "alloc": alloc,
            "txs": txs,
            "env": env,
        }

        encoded_input = str.encode(json.dumps(stdin))
        result = subprocess.run(
            args,
            input=encoded_input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise Exception("failed to evaluate: " + result.stderr.decode())

        output = json.loads(result.stdout)

        if "alloc" not in output or "result" not in output:
            raise Exception("malformed result")

        if self.trace:
            receipts: List[Any] = output["result"]["receipts"]
            traces: List[List[Dict]] = []
            for i, r in enumerate(receipts):
                h = r["transactionHash"]
                trace_file_name = f"trace-{i}-{h}.jsonl"
                with open(os.path.join(temp_dir.name, trace_file_name), "r") as trace_file:
                    tx_traces: List[Dict] = []
                    for trace_line in trace_file.readlines():
                        tx_traces.append(json.loads(trace_line))
                    traces.append(tx_traces)
            self.append_traces(traces)

        temp_dir.cleanup()

        return output["alloc"], output["result"]

    def version(self) -> str:
        """
        Gets `evm` binary version.
        """
        if self.cached_version is None:
            result = subprocess.run(
                [str(self.binary), "-v"],
                stdout=subprocess.PIPE,
            )

            if result.returncode != 0:
                raise Exception("failed to evaluate: " + result.stderr.decode())

            self.cached_version = result.stdout.decode().strip()

        return self.cached_version

    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool
        """
        return fork().name() in self.help_string


class EvmOneTransitionTool(TransitionTool):
    """
    Evmone `evmone-t8n` Transition tool frontend.
    """

    binary: Path
    cached_version: Optional[str] = None
    trace: bool

    def __init__(
        self,
        *,
        binary: Optional[Path | str] = None,
        trace: bool = False,
    ):
        if binary is None or type(binary) is str:
            if binary is None:
                binary = "evmone-t8n"
            which_path = which(binary)
            if which_path is not None:
                binary = Path(which_path)
        if binary is None or not Path(binary).exists():
            raise Exception("""`evmone-t8n` binary executable is not accessible""")
        self.binary = Path(binary)
        self.trace = trace

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
        Executes `evmone-t8n` with the specified arguments.
        """
        fork_name = fork.name()
        if eips is not None:
            fork_name = "+".join([fork_name] + [str(eip) for eip in eips])

        temp_dir = tempfile.TemporaryDirectory()

        input_contents = {
            "alloc": alloc,
            "env": env,
            "txs": txs,
        }
        input_paths = {
            k: os.path.join(temp_dir.name, f"input_{k}.json") for k in input_contents.keys()
        }
        for key, val in input_contents.items():
            file_path = os.path.join(temp_dir.name, f"input_{key}.json")
            self.write_json_file(val, file_path)

        # Construct args for evmone-t8n binary
        args = [
            str(self.binary),
            "--state.fork",
            fork_name,
            "--input.alloc",
            input_paths["alloc"],
            "--input.env",
            input_paths["env"],
            "--input.txs",
            input_paths["txs"],
            "--output.basedir",
            temp_dir.name,
            "--output.result",
            "output_result.json",
            "--output.alloc",
            "output_alloc.json",
            "--output.body",
            "txs.rlp",
            "--state.reward",
            str(reward),
            "--state.chainid",
            str(chain_id),
        ]
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise Exception("failed to evaluate: " + result.stderr.decode())

        output_paths = {
            "alloc": os.path.join(temp_dir.name, "output_alloc.json"),
            "result": os.path.join(temp_dir.name, "output_result.json"),
        }

        output_contents = {}
        for key, file_path in output_paths.items():
            with open(file_path, "r+") as file:
                contents = json.load(file)
                file.seek(0)
                json.dump(contents, file, ensure_ascii=False, indent=4)
                file.truncate()
                output_contents[key] = contents

        temp_dir.cleanup()

        return output_contents["alloc"], output_contents["result"]

    def version(self) -> str:
        """
        Gets `evmone-t8n` binary version.
        """
        if self.cached_version is None:
            result = subprocess.run(
                [str(self.binary), "-v"],
                stdout=subprocess.PIPE,
            )

            if result.returncode != 0:
                raise Exception("failed to evaluate: " + result.stderr.decode())

            self.cached_version = result.stdout.decode().strip()

        return self.cached_version

    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool.
        Currently, evmone-t8n provides no way to determine supported forks.
        """
        return True
