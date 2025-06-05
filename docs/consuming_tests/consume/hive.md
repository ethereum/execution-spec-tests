# Running Tests via Hive Simulators

## Overview

Hive simulators provide the most comprehensive way to test Ethereum execution clients against EEST fixtures. The EEST project provides two simulators in the Hive ecosystem:

- **`ethereum/eest/consume-rlp`**: Tests block import via RLP-encoded blocks (similar to historical sync)
- **`ethereum/eest/consume-engine`**: Tests via the Engine API (post-merge consensus integration)

These simulators run the same test logic as other consume methods but provide system-level integration testing with full client containers.

## Installation and Setup

### Prerequisites

1. **Docker**: Hive requires Docker for containerization
2. **Go**: Version 1.17+ required to build Hive
3. **Git**: To clone the Hive repository

### Installing Hive

```bash
git clone https://github.com/ethereum/hive
cd hive
go build .
```

## Running Simulators

### Basic Simulator Execution

The general syntax for running EEST simulators via Hive:

```bash
./hive --sim <simulator-name> --client <client-list> [options]
```

#### Examples

Run Engine API tests against go-ethereum:

```bash
./hive --sim ethereum/eest/consume-engine --client go-ethereum
```

Run RLP tests against multiple clients:

```bash
./hive --sim ethereum/eest/consume-rlp --client go-ethereum,besu,nethermind
```

### Command-Line Options

#### Essential Options

- `--client <list>`: Comma-separated list of clients to test
- `--client-file <file>`: YAML file with client configurations  
- `--sim.limit <pattern>`: Filter which tests to run (see [Test Filtering](#test-filtering))
- `--docker.output`: Show client container output during execution
- `--sim.parallelism <number>`: Number of parallel test executions (default: 1)

#### Client Configuration Options

- `--client.checktimelimit <timeout>`: Time to wait for client startup (default: 3m)
- `--sim.loglevel <level>`: Client log verbosity (0-5, default: 3)

#### Development Options

- `--dev`: Start in development mode (see [Development Mode](#development-mode))
- `--results-root <dir>`: Directory for results and logs (default: `workspace/logs`)

### Test Filtering

#### Using `--sim.limit` for Test Selection

EEST simulators support powerful test filtering via the `--sim.limit` option:

**Run a specific test by exact ID:**

```bash
./hive --sim ethereum/eest/consume-engine \
  --client besu \
  --sim.limit "id:tests/constantinople/eip1014_create2/test_recreate.py::test_recreate[fork_Paris-blockchain_test_engine-recreate_on_separate_block_False]"
```

**Use regex patterns:**

```bash
./hive --sim ethereum/eest/consume-rlp \
  --client go-ethereum \
  --sim.limit ".*fork_Prague.*"
```

**Dry-run to see which tests match:**

```bash
./hive --sim ethereum/eest/consume-engine \
  --client nethermind \
  --sim.limit "collectonly:.*fork_Paris.*" \
  --docker.output
```

#### Syntax Rules

- `id:` prefix: Exact test ID match (auto-escapes special regex characters)
- `collectonly:` prefix: Dry-run mode showing matched tests without execution
- No prefix: Standard regex pattern matching

## Client Configuration

### Using Client Files

Create a YAML file to specify client builds and configurations:

**clients.yaml:**

```yaml
- client: go-ethereum
  nametag: main
  dockerfile: git
  build_args:
    github: ethereum/go-ethereum
    tag: master

- client: besu
  nametag: develop
  build_args:
    baseimage: hyperledger/besu
    tag: develop
```

**Run with client file:**

```bash
./hive --sim ethereum/eest/consume-engine \
  --client-file clients.yaml \
  --client go-ethereum,besu
```

### Build Arguments

Common build arguments for client configuration:

- `tag`: Git commit/tag/branch or Docker tag
- `github`: GitHub repository (e.g., `ethereum/go-ethereum`)
- `baseimage`: Docker Hub organization/image name
- `dockerfile`: Alternative Dockerfile to use (e.g., `git`, `local`)

### Local Development Builds

For testing local client code:

```yaml
- client: go-ethereum
  nametag: local-dev
  dockerfile: local
  build_args:
    local_path: ./clients/go-ethereum/go-ethereum-local
```

## Development Mode

### Interactive Testing Workflow

Hive's development mode allows interactive testing without rebuilding containers:

**1. Start Hive in dev mode:**

```bash
./hive --dev --client go-ethereum --client-file clients.yaml --docker.output
```

**2. In another terminal, run EEST consume commands:**

```bash
# Set environment variable
export HIVE_SIMULATOR=http://127.0.0.1:3000

# Run tests interactively
uv run consume engine --input ./fixtures -k "test_chainid"
uv run consume rlp --input latest-stable --fork shanghai
```

### Advantages of Development Mode

- **Faster iteration**: No container rebuilding between test runs
- **Interactive debugging**: Real-time log output with `--docker.output`
- **Flexible test selection**: Use pytest `-k` syntax for filtering
- **Branch switching**: Easy EEST branch changes without client rebuilds

## Fixture Sources

### Using Different Fixture Sources

EEST simulators support multiple fixture input sources:

**Local fixtures:**

```bash
./hive --sim ethereum/eest/consume-engine \
  --sim.buildarg fixtures=/path/to/fixtures \
  --client go-ethereum
```

**Remote release archives:**

```bash
./hive --sim ethereum/eest/consume-rlp \
  --sim.buildarg fixtures=https://github.com/ethereum/execution-spec-tests/releases/download/v4.1.0/fixtures_develop.tar.gz \
  --client besu
```

**Release shortcuts:**

```bash
# Use latest stable release
./hive --sim ethereum/eest/consume-engine \
  --sim.buildarg fixtures=stable@latest \
  --client nethermind
```

## Viewing Results

### Using hiveview

Build and run the result viewer:

```bash
go build ./cmd/hiveview
./hiveview --serve --logdir ./workspace/logs
```

Access the web interface at: http://127.0.0.1:8080

### Result Files

Hive stores results in the `workspace/logs` directory:

- **JSON files**: Test results and metadata
- **Log files**: Client and simulator output
- **Timing data**: Performance metrics (when enabled)

### Test Report Features

- **Per-client results**: Success/failure breakdown by client
- **Test details**: Individual test case information
- **Reproduce commands**: Copy-paste commands to rerun specific tests
- **Log viewing**: Client output for debugging failures

## Integration with CI/CD

### Automated Testing

The Ethereum Foundation maintains continuous testing at:

- **Production results**: [hive.ethpandaops.io](https://hive.ethpandaops.io)
- **Development results**: [hive2.ethpandaops.io](https://hive2.ethpandaops.io)

### GitHub Actions Integration

Use the official Hive GitHub Action for CI integration:

```yaml
- name: Run Hive Simulator
  uses: ethpandaops/hive-github-action@v1
  with:
    simulator: ethereum/eest/consume-engine
    client: go-ethereum,besu
    client-file: .github/clients.yaml
```

Repository: [ethpandaops/hive-github-action](https://github.com/ethpandaops/hive-github-action)

## Complete Examples

### Testing Prague Fork Features

```bash
# Clone and build Hive
git clone https://github.com/ethereum/hive
cd hive && go build .

# Create client configuration
cat > clients_prague.yaml << EOF
- client: go-ethereum
  nametag: prague-devnet-4
  dockerfile: git
  build_args:
    github: lightclient/go-ethereum
    tag: prague-devnet-4
EOF

# Run Prague tests
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum \
  --client-file clients_prague.yaml \
  --sim.limit ".*fork_Prague.*" \
  --sim.parallelism 4 \
  --sim.loglevel 4
```

### Multi-Client Comparison

```bash
# Test all major clients
./hive --sim ethereum/eest/consume-rlp \
  --client go-ethereum,besu,nethermind,reth \
  --client-file configs/mainnet.yaml \
  --sim.limit ".*fork_Cancun.*" \
  --sim.parallelism 2
```

## See Also

- [Development Mode Documentation](./dev_mode.md)
- [Client Configuration Guide](./client_config.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Consume Command Overview](./index.md)
