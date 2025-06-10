# Hive Development Mode

This section explains how to run EEST simulators using their EEST commands, e.g., `uv run consume engine`, against a Hive "development" server as apposed to using the standalone `./hive` command.

This avoids running the simulator in a dockerized environment and has several advantages:

1. A local directory containing fixtures can be specified (`--input=./fixtures/`).
2. Allows dropping into a Python debugger (via `--pdb`) upon test failure to inspect the response or ssh to the client container.
3. Provides access to a larger set of the simulator's command-line options,
4. Runs are faster; there are no docker image rebuilds in between runs. In particular, modifications to the simulator do not require a an image rebuild.

## Quick Start

### Prerequisites

- EEST is installed, see [Installation](../../getting_started/installation.md)
- Hive is built, see [Hive](../hive/index.md#quick-start).

## Hive Dev Setup

1. Start Hive in development mode, e.g.:

    ```bash
    ./hive --dev --client go-ethereum --client-file clients.yaml --docker.output
    ```

2. In a separate shell, configure environment for EEST:

    === "bash/zsh"

        ```bash
        export HIVE_SIMULATOR=http://127.0.0.1:3000
        ```

    === "fish"

        ```console
        set -x HIVE_SIMULATOR http://127.0.0.1:3000
        ```

3. Run EEST consume commands

    ```bash
    uv run consume engine --input ./fixtures -k "test_chainid"
    uv run consume rlp --input stable@latest
    ```

## How Development Mode Works

When Hive runs in dev mode:

1. Starts the Hive API server (default: `http://127.0.0.1:3000`).
2. Builds and maintains client containers.
3. Keeps the Hive Proxy container running between test executions.
4. Waits for external simulator connections via the API.

This allows EEST's consume commands to connect to the running Hive instance and execute tests interactively.

## More Options Available

There are many useful native pytest options available in dev mode, see [Useful Options](../useful_pytest_options.md).

### Custom API Endpoint

Specify a custom address and port via `--dev.addr`:

```bash
./hive --dev \
  --dev.addr 127.0.0.1:5000 \
  --client reth \
  --client-file clients.yaml
```

Then connect with:

```bash
export HIVE_SIMULATOR=http://127.0.0.1:5000
```
