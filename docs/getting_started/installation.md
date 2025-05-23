# Installation

## Prerequisites

The tools provided by [execution-spec-tests](https://github.com/ethereum/execution-spec-tests) use `uv` ([docs.astral.sh/uv](https://docs.astral.sh/uv/)) to manage their dependencies and virtual environment.

It's typically recommended to use the latest version of `uv`, currently `uv>=0.5.22` is required.

The latest version of `uv` can be installed via `curl` (recommended; can self-update via `uv self update`) or pip (requires Python, can't self-update):

=== "curl"

    ```console
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "pip"

    ```console
    pip install uv
    ```

If installed via `curl`, `uv` will download Python for your target platform if one of the required versions (Python 3.10, 3.11 or 3.12) is not available natively.

## Installation Commands

Clone [execution-spec-tests](https://github.com/ethereum/execution-spec-tests) and install its dependencies. We recommend using Python 3.12, the following uses `uv` to download and configures 3.12 to be the Python version used in execution-spec-tests:

=== "All x86-64 platforms and ARM64 macOS"

    ```console
    git clone https://github.com/ethereum/execution-spec-tests
    cd execution-spec-tests
    uv python install 3.12
    uv python pin 3.12
    uv sync --all-extras
    uv run solc-select use 0.8.24 --always-install
    ```

=== "ARM64 Linux"

    ```console
    git clone https://github.com/ethereum/execution-spec-tests
    uv python install 3.12
    uv python pin 3.12
    cd execution-spec-tests
    uv sync --all-extras
    ```
    Then follow [this guide](./installation_troubleshooting.md#problem-exception-failed-to-compile-yul-source) to build the `solc` binary from source and copy it to the expected location.

## Installation Troubleshooting

If you encounter issues during installation, see the [Installation Troubleshooting](./installation_troubleshooting.md) guide.
