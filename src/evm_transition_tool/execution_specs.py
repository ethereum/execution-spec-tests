"""
Ethereum Specs EVM Transition tool interface.

https://github.com/ethereum/execution-specs
"""

import subprocess
import time
from pathlib import Path
from re import compile
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Tuple

from requests_unixsocket import Session  # type: ignore

from ethereum_test_forks import Constantinople, ConstantinopleFix, Fork

from .geth import GethTransitionTool
from .transition_tool import FixtureFormats

<<<<<<< HEAD
UNSUPPORTED_FORKS = (
    Constantinople,
    ConstantinopleFix,
)
=======
DAEMON_STARTUP_TIMEOUT_SECONDS = 5
>>>>>>> 9df200c2d (feat(transition_tool): Use execution-specs daemon)


class ExecutionSpecsTransitionTool(GethTransitionTool):
    """
    Ethereum Specs `ethereum-spec-evm` Transition tool interface wrapper class.

    The behavior of this tool is almost identical to go-ethereum's `evm t8n` command.

    note: Using the latest version of the `ethereum-spec-evm` tool:

        As the `ethereum` package provided by `execution-specs` is a requirement of
        `execution-spec-tests`, the `ethereum-spec-evm` is already installed in the
        virtual environment where `execution-spec-tests` is installed
        (via `pip install -e .`). Therefore, the `ethereum-spec-evm` transition tool
        can be used to fill tests via:

        ```console
            fill --evm-bin=ethereum-spec-evm
        ```

        To ensure you're using the latest version of `ethereum-spec-evm` you can run:

        ```
        pip install --force-reinstall -e .
        ```

        or

        ```
        pip install --force-reinstall -e .[docs,lint,tests]
        ```

        as appropriate.

    note: Using a specific version of the `ethereum-spec-evm` tool:

        1. Create a virtual environment and activate it:
            ```
            python -m venv venv-execution-specs
            source venv-execution-specs/bin/activate
            ```
        2. Clone the ethereum/execution-specs repository, change working directory to it and
            retrieve the desired version of the repository:
            ```
            git clone git@github.com:ethereum/execution-specs.git
            cd execution-specs
            git checkout <version>
            ```
        3. Install the packages provided by the repository:
            ```
            pip install -e .
            ```
            Check that the `ethereum-spec-evm` command is available:
            ```
            ethereum-spec-evm --help
            ```
        4. Clone the ethereum/execution-specs-tests repository and change working directory to it:
            ```
            cd ..
            git clone git@github.com:ethereum/execution-spec-tests.git
            cd execution-spec-tests
            ```
        5. Install the packages provided by the ethereum/execution-spec-tests repository:
            ```
            pip install -e .
            ```
        6. Run the tests, specifying the `ethereum-spec-evm` command as the transition tool:
            ```
            fill --evm-bin=path/to/venv-execution-specs/ethereum-spec-evm
            ```
    """

    default_binary = Path("ethereum-spec-evm")
    detect_binary_pattern = compile(r"^ethereum-spec-evm\b")
    statetest_subcommand: Optional[str] = None
    blocktest_subcommand: Optional[str] = None
    process: Optional[subprocess.Popen] = None
    server_url: str
    temp_dir: Optional[TemporaryDirectory] = None

    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool.
        Currently, ethereum-spec-evm provides no way to determine supported forks.
        """
        return fork not in UNSUPPORTED_FORKS

    def get_blocktest_help(self) -> str:
        """
        Return the help string for the blocktest subcommand.
        """
        raise NotImplementedError(
            "The `blocktest` command is not supported by the ethereum-spec-evm. "
            "Use geth's evm tool."
        )

    def verify_fixture(
        self,
        fixture_format: FixtureFormats,
        fixture_path: Path,
        fixture_name: Optional[str] = None,
        debug_output_path: Optional[Path] = None,
    ):
        """
        Executes `evm [state|block]test` to verify the fixture at `fixture_path`.

        Currently only implemented by geth's evm.
        """
        raise NotImplementedError(
            "The `verify_fixture()` function is not supported by the ethereum-spec-evm. "
            "Use geth's evm tool."
        )

    def start_server(self):
        """
        Starts the t8n-server process, extracts the port, and leaves it running for future re-use.
        """
        self.temp_dir = TemporaryDirectory()
        self.server_file_path = Path(self.temp_dir.name) / "t8n.sock"
        replaced_str = str(self.server_file_path).replace("/", "%2F")
        self.server_url = f"http+unix://{replaced_str}/"
        self.process = subprocess.Popen(
            args=[
                str(self.binary),
                "daemon",
                "--uds",
                self.server_file_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        start = time.time()
        while True:
            if self.server_file_path.exists():
                break
            if time.time() - start > DAEMON_STARTUP_TIMEOUT_SECONDS:
                raise Exception("Failed starting ethereum-spec-evm subprocess")
            time.sleep(0)  # yield to other processes

    def shutdown(self):
        """
        Stops the t8n-server process if it was started
        """
        if self.process:
            self.process.kill()
        if self.temp_dir:
            self.temp_dir.cleanup()
            self.temp_dir = None

    def evaluate(
        self,
        alloc: Any,
        txs: Any,
        env: Any,
        fork_name: str,
        chain_id: int = 1,
        reward: int = 0,
        eips: Optional[List[int]] = None,
        debug_output_path: str = "",
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Executes `evm t8n` with the specified arguments.
        """
        if not self.process:
            self.start_server()

        if eips is not None:
            fork_name = "+".join([fork_name] + [str(eip) for eip in eips])

        input_json = {
            "alloc": alloc,
            "txs": txs,
            "env": env,
        }
        state_json = {
            "fork": fork_name,
            "chainid": chain_id,
            "reward": reward,
        }

        post_data = {"state": state_json, "input": input_json}
        response = Session().post(self.server_url, json=post_data, timeout=5)
        response.raise_for_status()  # exception visible in pytest failure output
        output = response.json()

        if response.status_code != 200:
            raise Exception(
                f"t8n-server returned status code {response.status_code}, "
                f"response: {response.text}"
            )
        if not all([x in output for x in ["alloc", "result", "body"]]):
            raise Exception(
                "Malformed t8n output: missing 'alloc', 'result' or 'body', server response: "
                f"{response.text}"
            )

        return output["alloc"], output["result"]
