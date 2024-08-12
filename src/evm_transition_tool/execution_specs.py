"""
Ethereum Specs EVM Transition tool interface.

https://github.com/ethereum/execution-specs
"""

import subprocess
import time
from pathlib import Path
from re import compile
from tempfile import TemporaryDirectory
from typing import Optional

from ethereum_test_forks import Fork

from .transition_tool import TransitionTool

DAEMON_STARTUP_TIMEOUT_SECONDS = 5


class ExecutionSpecsTransitionTool(TransitionTool):
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
    t8n_use_server: bool = True
    server_dir: Optional[TemporaryDirectory] = None

    def __init__(
        self,
        *,
        binary: Optional[Path] = None,
        trace: bool = False,
    ):
        super().__init__(binary=binary, trace=trace)
        args = [str(self.binary), "--help"]
        try:
            result = subprocess.run(args, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception(
                "ethereum-spec-evm process unexpectedly returned a non-zero status code: " f"{e}."
            )
        except Exception as e:
            raise Exception(f"Unexpected exception calling ethereum-spec-evm: {e}.")
        self.help_string = result.stdout

    def start_server(self):
        """
        Starts the t8n-server process, extracts the port, and leaves it running for future re-use.
        """
        self.server_dir = TemporaryDirectory()
        self.server_file_path = Path(self.server_dir.name) / "t8n.sock"
        replaced_str = str(self.server_file_path).replace("/", "%2F")
        self.server_url = f"http+unix://{replaced_str}/"
        self.process = subprocess.Popen(
            args=[
                str(self.binary),
                "daemon",
                "--uds",
                self.server_file_path,
            ],
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
        Stops the t8n-server process if it was started.
        """
        if self.process:
            self.process.kill()
        if self.server_dir:
            self.server_dir.cleanup()
            self.server_dir = None

    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool.

        If the fork is a transition fork, we want to check the fork it transitions to.

        `ethereum-spec-evm` appends newlines to forks in the help string.
        """
        return (fork.transition_tool_name() + "\n") in self.help_string
