# Quick Start

!!! info "Testing features under active development"
    The EVM features under test must be implemented in the `evm` tool and `solc` executables that are used by the execution-spec-tests framework. The following guide installs the stable version of the geth `evm`; `solc` will be installed by the `fill` command.

    To test features under active development, start with this base configuration and then follow the steps in [executing tests for features under development](./executing_tests_dev_fork.md). 

The following requires a Python 3.10, 3.11 or 3.12 installation.

1. Ensure `go-ethereum`'s `evm` tool is in your path. Either build the required version, or alternatively:

    === "Ubuntu"

          ```console
          sudo add-apt-repository -y ppa:ethereum/ethereum
          sudo apt-get update
          sudo apt-get install ethereum
          ```
          More help:

          - [geth installation doc](https://geth.ethereum.org/docs/getting-started/installing-geth#ubuntu-via-ppas).

    === "macOS"

          ```console
          brew update
          brew upgrade
          brew tap ethereum/ethereum
          brew install ethereum solidity
          ```
          More help:

          - [geth installation doc](https://geth.ethereum.org/docs/getting-started/installing-geth#macos-via-homebrew).

    === "Windows"

          Binaries available here:

          - [geth](https://geth.ethereum.org/downloads) (binary or installer).
          - [solc](https://github.com/ethereum/solidity/releases).

          More help:

          - [geth installation doc](https://geth.ethereum.org/docs/getting-started/installing-geth#windows).

2. Clone the [execution-spec-tests](https://github.com/ethereum/execution-spec-tests) repo and install its dependencies (it's recommended to use a virtual environment for the installation):

    ```console
    git clone https://github.com/ethereum/execution-spec-tests
    cd execution-spec-tests
    pip install uv  # or curl -LsSf https://astral.sh/uv/install.sh | sh
    uv sync --all-extras
    uv run solc-select use 0.8.24 --always-install
    source .venv/bin/activate  # or run `uv run fill ...`
    ```

3. Verify installation:
    1. Explore test cases:

        ```console
        fill --collect-only
        ```

        Expected console output:
        <figure markdown>  <!-- markdownlint-disable MD033 (MD033=no-inline-html) -->
            ![Screenshot of pytest test collection console output](./img/pytest_collect_only.png){align=center}
        </figure>

    2. Execute the test cases (verbosely) in the `./tests/berlin/eip2930_access_list/test_acl.py` module:

        ```console
        fill -v tests/berlin/eip2930_access_list/test_acl.py
        ```

        Expected console output:
        <figure markdown>  <!-- markdownlint-disable MD033 (MD033=no-inline-html) -->
            ![Screenshot of pytest test collection console output](./img/pytest_run_example.png){align=center}
        </figure>
        Check:

        1. The versions of the `evm` tool is as expected (your versions may differ from those in the highlighted box).
        2. The generated HTML test report by clicking the link at the bottom of the console output.
        3. The corresponding fixture file has been generated:

            ```console
            head fixtures/blockchain_tests/berlin/eip2930_access_list/acl/access_list.json
            ```

## Installation Troubleshooting

If you encounter issues during installation, see the [Installation Troubleshooting](./installation_troubleshooting.md) guide.

## Next Steps

1. Learn [useful command-line flags](./executing_tests_command_line.md).
2. [Execute tests for features under development](./executing_tests_dev_fork.md) via the `--fork` flag.
3. _Optional:_ [Configure VS Code](./setup_vs_code.md) to auto-format Python code and [execute tests within VS Code](./executing_tests_vs_code.md#executing-and-debugging-test-cases).
4. Implement a new test case, see [Writing Tests](../writing_tests/index.md).
