# Hive Development Mode

## Overview

Hive's development mode (`--dev`) provides an interactive testing environment that allows developers to run EEST consume commands against live client containers without the overhead of rebuilding containers for each test run. This mode is particularly valuable for:

- **Rapid iteration**: Testing changes without container rebuilds
- **Interactive debugging**: Real-time log output and container inspection  
- **Flexible test selection**: Using pytest-style filtering syntax
- **Branch switching**: Testing different EEST versions against the same client

## How Development Mode Works

When Hive runs in dev mode:

1. Starts the Hive API server (default: `http://127.0.0.1:3000`)
2. Builds and maintains client containers  
3. Keeps containers running between test executions
4. Waits for external simulator connections via the API

This allows EEST's consume commands to connect to the running Hive instance and execute tests interactively.

## Basic Setup

### 1. Start Hive in Development Mode

```bash
./hive --dev --client <client-name> --client-file <config.yaml> [options]
```

**Example:**

```bash
./hive --dev --client go-ethereum --client-file clients.yaml --docker.output
```

### 2. Configure Environment in EEST

Set the `HIVE_SIMULATOR` environment variable to connect to Hive:

```bash
# Bash/Zsh
export HIVE_SIMULATOR=http://127.0.0.1:3000

# Fish
set -x HIVE_SIMULATOR http://127.0.0.1:3000

# Windows PowerShell
$env:HIVE_SIMULATOR="http://127.0.0.1:3000"
```

### 3. Run EEST Consume Commands

```bash
uv run consume engine --input ./fixtures -k "test_chainid"
uv run consume rlp --input latest-stable --fork shanghai
```

## Configuration Examples

### Single Client Testing

```bash
# Start dev mode with go-ethereum
./hive --dev \
  --client go-ethereum \
  --client-file clients.yaml \
  --docker.output \
  --sim.loglevel 5
```

### Multi-Client Testing

```bash
# Test against multiple clients
./hive --dev \
  --client go-ethereum,besu,nethermind \
  --client-file clients.yaml \
  --docker.output
```

### Custom API Endpoint

```bash
# Use different port for API
./hive --dev \
  --dev.addr 127.0.0.1:5000 \
  --client reth \
  --client-file clients.yaml
```

Then connect with:

```bash
export HIVE_SIMULATOR=http://127.0.0.1:5000
```

## Client Configuration Files

### Basic Client Configuration

**clients.yaml:**

```yaml
- client: go-ethereum
  nametag: master
  dockerfile: git
  build_args:
    github: ethereum/go-ethereum
    tag: master
```

### Development Branches

**clients_prague.yaml:**

```yaml
- client: go-ethereum
  nametag: prague-devnet-4
  dockerfile: git
  build_args:
    github: lightclient/go-ethereum
    tag: prague-devnet-4

- client: besu
  nametag: main-branch
  dockerfile: git
  build_args:
    github: hyperledger/besu
    tag: main
```

### Local Development Builds

```yaml
- client: go-ethereum
  nametag: local-dev
  dockerfile: local
  build_args:
    local_path: ./clients/go-ethereum/go-ethereum-local
```

### Inline Configuration

For quick testing without separate YAML files:

```bash
./hive --dev \
  --client-file <(echo '[{"client":"besu","dockerfile":"git","build_args":{"github":"hyperledger/besu","tag":"main"}}]') \
  --client besu \
  --docker.output
```

## EEST Command Integration

### Using pytest-style Filtering

Unlike Hive's regex-based `--sim.limit`, dev mode supports pytest's `-k` syntax:

```bash
# Run specific test patterns
uv run consume engine -k "test_chainid and fork_London"
uv run consume rlp -k "eip1559 or eip4844" --fork cancun

# Run single test by exact match
uv run consume engine -k "test_recreate[fork_Paris-blockchain_test_engine-recreate_on_separate_block_False]"
```

### Test Collection and Dry Runs

```bash
# See which tests would run without executing them
uv run consume engine --collect-only -q -k "fork_Prague"

# Verbose collection with test descriptions
uv run consume rlp --collect-only -k "blob_txs"
```

### Fixture Source Options

```bash
# Local fixtures
uv run consume engine --input ./fixtures

# Remote release
uv run consume rlp --input stable@latest

# Cached fixtures (after first download)
uv run consume engine --input cached_downloads/v4.1.0/fixtures_develop/fixtures

# Specific URL
uv run consume rlp --input https://github.com/ethereum/execution-spec-tests/releases/download/v4.1.0/fixtures_develop.tar.gz
```

## Debugging and Logging

### Container Output

Use `--docker.output` to see real-time client logs:

```bash
./hive --dev --client ethereumjs --docker.output --sim.loglevel 5
```

### Log Levels

Configure client log verbosity with `--sim.loglevel`:

- `0`: Emergency
- `1`: Alert  
- `2`: Critical
- `3`: Error (default)
- `4`: Warning
- `5`: Info

### Container Inspection

While in dev mode, containers remain running for inspection:

```bash
# List running containers
docker ps

# Inspect specific client container
docker logs <container-id>

# Execute commands in container
docker exec -it <container-id> /bin/sh
```

## Advanced Usage

### Multiple EEST Branches

Dev mode allows testing different EEST branches against the same client:

```bash
# Terminal 1: Start Hive dev mode
./hive --dev --client go-ethereum --client-file clients.yaml

# Terminal 2: Test main branch
git checkout main
export HIVE_SIMULATOR=http://127.0.0.1:3000
uv run consume engine -k "test_specific_feature"

# Terminal 2: Switch to feature branch  
git checkout feature-branch
uv run consume engine -k "test_specific_feature"
```

### Performance Testing

```bash
# Run with timing data
uv run consume engine --timing-data -k "performance_tests"

# Parallel execution (be careful with --docker.output)
uv run consume rlp -n 4 -k "fork_Shanghai"
```

### Custom Test Patterns

```bash
# Complex filtering
uv run consume engine -k "(eip4844 or eip1559) and not invalid"

# Fork-specific testing
uv run consume rlp -k "fork_Prague" --fork prague

# EIP-specific testing  
uv run consume engine -k "eip4844" --input latest-develop
```

## Common Workflows

### Client Development Workflow

```bash
# 1. Start Hive with your client
./hive --dev --client your-client --client-file config.yaml --docker.output

# 2. Run tests against your changes
export HIVE_SIMULATOR=http://127.0.0.1:3000
uv run consume engine -k "specific_feature_tests"

# 3. Make code changes to client
# 4. Rebuild client container
docker build -t hive/clients/your-client:latest ./clients/your-client

# 5. Restart Hive dev mode and retest
./hive --dev --client your-client --client-file config.yaml
```

### Fork Validation Workflow

```bash
# Test new fork implementation
./hive --dev --client go-ethereum,besu,nethermind --client-file fork-config.yaml

# Run comprehensive fork tests
export HIVE_SIMULATOR=http://127.0.0.1:3000
uv run consume engine -k "fork_NewFork" --input latest-develop

# Compare with previous fork
uv run consume engine -k "fork_PreviousFork" --input stable@latest
```

### CI Integration Workflow

```bash
# Start Hive in background for CI
./hive --dev --client ci-client --client-file ci-config.yaml > hive.log 2>&1 &
HIVE_PID=$!

# Wait for API to be ready
sleep 10

# Run tests
export HIVE_SIMULATOR=http://127.0.0.1:3000
uv run consume engine --input fixtures/ --junit-xml results.xml

# Cleanup
kill $HIVE_PID
```

## Troubleshooting

### Connection Issues

#### Error: "HIVE_SIMULATOR environment variable is not set"

```bash
# Ensure variable is exported
export HIVE_SIMULATOR=http://127.0.0.1:3000
echo $HIVE_SIMULATOR
```

#### Error: "Connection refused"

```bash
# Check if Hive is running
curl http://127.0.0.1:3000/

# Check custom port
./hive --dev --dev.addr 127.0.0.1:5000
export HIVE_SIMULATOR=http://127.0.0.1:5000
```

### Container Issues

**Client container fails to start:**

```bash
# Check client logs
./hive --dev --docker.output --sim.loglevel 5

# Rebuild client image
docker build --no-cache -t hive/clients/your-client:latest ./clients/your-client
```

**Timeout waiting for client:**

```bash
# Increase timeout
./hive --dev --client.checktimelimit=60s
```

### Performance Issues

**Slow test execution:**

```bash
# Reduce log output
./hive --dev --sim.loglevel 2

# Remove docker output for faster execution
./hive --dev --client your-client  # without --docker.output
```

## See Also

- [Hive Simulator Guide](./hive.md)
- [Client Configuration](./client_config.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Consume Command Overview](./index.md)
