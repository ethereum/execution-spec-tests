"""
Go-ethereum Transition tool frontend.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from shutil import which
from typing import Any, Dict, List, Optional, Tuple

from ethereum_test_forks import Fork

from .transition_tool import TransitionTool


class GethTransitionTool(TransitionTool):
    """
    Go-ethereum `evm` Transition tool frontend wrapper class.
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

    @staticmethod
    def matches_binary_path(binary_path: str) -> bool:
        """
        Returns True if the binary path matches the tool
        """
        return os.path.basename(binary_path) == "evm"

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
