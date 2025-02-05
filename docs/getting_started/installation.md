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

## Installation

Clone [execution-spec-tests](https://github.com/ethereum/execution-spec-tests) and install its dependencies:

```console
git clone https://github.com/ethereum/execution-spec-tests
cd execution-spec-tests
uv sync --all-extras
uv run solc-select use 0.8.24 --always-install
```

## Installation Troubleshooting

If you encounter issues during installation, see the [Installation Troubleshooting](./installation_troubleshooting.md) guide.
