# Hive Simulators

## Overview

Hive provides containerized testing infrastructure for Ethereum clients. EEST offers two Hive simulators:

- **`ethereum/eest/consume-rlp`**: Tests block import via RLP-encoded blocks (all forks)
- **`ethereum/eest/consume-engine`**: Tests via Engine API (post-merge forks only)

See [Simulator Comparison](./comparison.md) for detailed differences.

## Quick Start

### Installation

```bash
git clone https://github.com/ethereum/hive
cd hive
go build .
```

Requirements: Docker, Go 1.22+

### Basic Usage

```bash
# Engine API tests
./hive --sim ethereum/eest/consume-engine --client go-ethereum

# RLP tests with multiple clients
./hive --sim ethereum/eest/consume-rlp --client go-ethereum,besu,nethermind

# With client configuration file
./hive --sim ethereum/eest/consume-engine --client-file clients.yaml --client go-ethereum
```

## Key Features

### Test Selection

Filter tests using `--sim.limit`:

```bash
# Regex pattern
./hive --sim ethereum/eest/consume-engine --sim.limit ".*eip4844.*"

# Exact test ID
./hive --sim ethereum/eest/consume-rlp --sim.limit "id:tests/cancun/eip4844_blobs/test_blob_txs.py::test_sufficient_balance_blob_tx"
```

### Development Mode

Run simulators interactively without container rebuilds:

```bash
# Start Hive server
./hive --dev --client go-ethereum --docker.output

# In another terminal
export HIVE_SIMULATOR=http://127.0.0.1:3000
uv run consume engine -k "test_chainid"
```

See [Development Mode Guide](./dev_mode.md) for details.

### Viewing Results

```bash
# Build result viewer
go build ./cmd/hiveview

# View results
./hiveview --serve --logdir ./workspace/logs
```

Access at http://127.0.0.1:8080

## Documentation

- [Common Options](./common_options.md) - Options shared by all simulators
- [Client Configuration](./client_config.md) - Setting up client builds
- [Development Mode](./dev_mode.md) - Interactive testing workflow
- [Exception Tests](./exceptions.md) - Understanding exception validation
- [Troubleshooting](../troubleshooting.md) - Common issues and solutions
