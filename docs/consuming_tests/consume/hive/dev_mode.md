# Hive Development Mode

Running EEST simulators against Hive in dev mode avoids running the simulator in a dockerized environment. This has several advantages:

1. A local directory path containing fixtures can be easily specified.
2. Allows dropping into a Python debugger (via `--pdb`) upon a fail to inspect the response or ssh to the client container.
3. Access to all the simulator's command-line options;
4. It's slightly faster, the client container continues to run in between `consume` executions.

## Quick Start

### Prerequisites

- EEST is installed, see [Installation](./../../../getting_started/installation.md)
- Hive is built, see [Hive](./index.md).

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
    uv run consume rlp --input latest-stable --fork shanghai
    ```

## How Development Mode Works

When Hive runs in dev mode:

1. Starts the Hive API server (default: `http://127.0.0.1:3000`)
2. Builds and maintains client containers  
3. Keeps containers running between test executions
4. Waits for external simulator connections via the API

This allows EEST's consume commands to connect to the running Hive instance and execute tests interactively.

## Other Useful Options

### Using pytest-style Filtering

In addition to Hive's regex-based `--sim.limit` option, running in dev mode supports pytest's `-k` syntax:

```bash
uv run consume engine -k "test_chainid and fork_London"
uv run consume rlp -k "eip1559 or eip4844" -m cancun
```

Use `--collect-only` to see which tests would run without executing them:

```bash
uv run consume engine --collect-only -q -k "fork_Prague"
```

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
