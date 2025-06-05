# Client Configuration Guide

## Overview

Client configuration in Hive allows precise control over how execution clients are built and configured for testing. This guide covers YAML configuration files, build arguments, Docker options, and environment variables used by EEST simulators.

## Configuration File Format

### Basic YAML Structure

Client configurations are defined in YAML files with the following structure:

```yaml
- client: <client-name>
  nametag: <unique-identifier>
  dockerfile: <dockerfile-variant>
  build_args:
    <key>: <value>
    ...
```

### Required Fields

- **`client`**: Must match a directory name in `clients/` within the Hive repository
- **`nametag`**: Unique identifier for this client configuration

### Optional Fields

- **`dockerfile`**: Alternative Dockerfile to use (default: `Dockerfile`)
- **`build_args`**: Docker build arguments passed to the Dockerfile

## Client Examples

### Go-Ethereum (Geth)

**Latest release:**

```yaml
- client: go-ethereum
  nametag: latest
  build_args:
    baseimage: ethereum/client-go
    tag: latest
```

**Specific version:**

```yaml
- client: go-ethereum
  nametag: v1.13.8
  build_args:
    baseimage: ethereum/client-go
    tag: v1.13.8
```

**Build from source:**

```yaml
- client: go-ethereum
  nametag: master
  dockerfile: git
  build_args:
    github: ethereum/go-ethereum
    tag: master
```

**Custom fork:**

```yaml
- client: go-ethereum
  nametag: prague-devnet-4
  dockerfile: git
  build_args:
    github: lightclient/go-ethereum
    tag: prague-devnet-4
```

### Besu

**Docker Hub release:**

```yaml
- client: besu
  nametag: develop
  build_args:
    baseimage: hyperledger/besu
    tag: develop
```

**Build from source:**

```yaml
- client: besu
  nametag: main
  dockerfile: git
  build_args:
    github: hyperledger/besu
    tag: main
```

### Nethermind

**Release version:**

```yaml
- client: nethermind
  nametag: v1.25.4
  build_args:
    baseimage: nethermind/nethermind
    tag: 1.25.4
```

**Preview builds:**

```yaml
- client: nethermind
  nametag: master
  build_args:
    baseimage: nethermindeth/nethermind
    tag: master
```

### Reth

**Stable release:**

```yaml
- client: reth
  nametag: v0.2.0-beta.5
  build_args:
    baseimage: ghcr.io/paradigmxyz/reth
    tag: v0.2.0-beta.5
```

**Development build:**

```yaml
- client: reth
  nametag: main
  dockerfile: git
  build_args:
    github: paradigmxyz/reth
    tag: main
```

### EthereumJS

**Docker Hub:**

```yaml
- client: ethereumjs
  nametag: master
  build_args:
    baseimage: ethereumjs/ethereumjs-monorepo
    tag: master
```

### Erigon

**Release:**

```yaml
- client: erigon
  nametag: v2.58.1
  build_args:
    baseimage: thorax/erigon
    tag: v2.58.1
```

**Development:**

```yaml
- client: erigon
  nametag: devel
  dockerfile: git
  build_args:
    github: ledgerwatch/erigon
    tag: devel
```

## Build Arguments

### Common Build Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `tag` | Git commit/tag/branch or Docker tag | `master`, `v1.13.8`, `latest` |
| `github` | GitHub repository for source builds | `ethereum/go-ethereum` |
| `baseimage` | Docker Hub image for binary builds | `ethereum/client-go` |

### Client-Specific Arguments

Different clients may support additional build arguments:

**Go-Ethereum specific:**

```yaml
build_args:
  github: ethereum/go-ethereum
  tag: master
  build_flags: "-tags=urfave_cli_no_docs"
```

**Besu specific:**

```yaml
build_args:
  github: hyperledger/besu
  tag: main
  gradle_options: "-x test"
```

## Dockerfile Variants

### Available Dockerfile Types

| Dockerfile | Purpose | Example Usage |
|------------|---------|---------------|
| `Dockerfile` | Default production build | `dockerfile: ""` (default) |
| `Dockerfile.git` | Build from Git source | `dockerfile: git` |
| `Dockerfile.local` | Build from local source | `dockerfile: local` |

### Using Git Dockerfiles

Git Dockerfiles clone and build from source:

```yaml
- client: go-ethereum
  nametag: experimental
  dockerfile: git
  build_args:
    github: your-username/go-ethereum
    tag: experimental-branch
```

### Using Local Dockerfiles

For testing local modifications:

```yaml
- client: go-ethereum
  nametag: local-dev
  dockerfile: local
  build_args:
    local_path: ./clients/go-ethereum/go-ethereum-local
```

**Setup for local builds:**

```bash
# Copy your local client code to Hive directory
cp -r /path/to/your/go-ethereum ./clients/go-ethereum/go-ethereum-local

# Update the dockerfile field to "local"
```

## Multi-Client Configurations

### Testing Multiple Clients

**Complete configuration example:**

```yaml
# Stable releases for compatibility testing
- client: go-ethereum
  nametag: stable
  build_args:
    baseimage: ethereum/client-go
    tag: stable

- client: besu
  nametag: stable
  build_args:
    baseimage: hyperledger/besu
    tag: latest

- client: nethermind
  nametag: stable
  build_args:
    baseimage: nethermind/nethermind
    tag: latest

- client: reth
  nametag: stable
  build_args:
    baseimage: ghcr.io/paradigmxyz/reth
    tag: latest

# Development versions for new features
- client: go-ethereum
  nametag: master
  dockerfile: git
  build_args:
    github: ethereum/go-ethereum
    tag: master

- client: besu
  nametag: main
  dockerfile: git
  build_args:
    github: hyperledger/besu
    tag: main
```

### Fork-Specific Testing

**Prague fork configuration:**

```yaml
- client: go-ethereum
  nametag: prague-devnet-4
  dockerfile: git
  build_args:
    github: lightclient/go-ethereum
    tag: prague-devnet-4

- client: besu
  nametag: prague-support
  dockerfile: git
  build_args:
    github: hyperledger/besu
    tag: prague-support-branch

- client: reth
  nametag: prague-features
  dockerfile: git
  build_args:
    github: paradigmxyz/reth
    tag: prague-features
```

## Environment Variables

### Client Environment Configuration

Hive sets environment variables for client configuration:

| Variable | Purpose | Example |
|----------|---------|---------|
| `HIVE_CHAIN_ID` | EIP-155 chain ID | `1` |
| `HIVE_NETWORK_ID` | P2P network ID | `1` |
| `HIVE_LOGLEVEL` | Client log level | `3` |
| `HIVE_NODETYPE` | Sync algorithm | `full`, `archive` |
| `HIVE_CHECK_LIVE_PORT` | Port for liveness check | `8545`, `8551` |

### Fork Activation Variables

```bash
HIVE_FORK_HOMESTEAD=1150000
HIVE_FORK_DAO_BLOCK=1920000  
HIVE_FORK_TANGERINE=2463000
HIVE_FORK_SPURIOUS=2675000
HIVE_FORK_BYZANTIUM=4370000
HIVE_FORK_CONSTANTINOPLE=7280000
HIVE_FORK_PETERSBURG=7280000
HIVE_FORK_ISTANBUL=9069000
HIVE_FORK_MUIR_GLACIER=9200000
HIVE_FORK_BERLIN=12244000
HIVE_FORK_LONDON=12965000
HIVE_FORK_ARROW_GLACIER=13773000
HIVE_FORK_GRAY_GLACIER=15050000
```

### EEST-Specific Variables

```bash
HIVE_SIMULATOR=http://127.0.0.1:3000
HIVE_PARALLELISM=1
HIVE_TEST_PATTERN=".*"
HIVE_RANDOM_SEED=0
```

## Command-Line Usage

### Basic Configuration

```bash
./hive --sim ethereum/eest/consume-engine \
  --client-file clients.yaml \
  --client go-ethereum
```

### Inline Configuration

For quick testing without separate files:

```bash
./hive --sim ethereum/eest/consume-rlp \
  --client-file <(echo '[{"client":"besu","dockerfile":"git","build_args":{"github":"hyperledger/besu","tag":"main"}}]') \
  --client besu
```

### Multiple Clients

```bash
./hive --sim ethereum/eest/consume-engine \
  --client-file multi-client.yaml \
  --client go-ethereum,besu,nethermind,reth
```

### Development Mode

```bash
./hive --dev \
  --client-file clients.yaml \
  --client go-ethereum \
  --docker.output
```

## Troubleshooting

### Build Issues

**Docker build failures:**

```bash
# Force rebuild base images
./hive --docker.pull --sim ethereum/eest/consume-engine

# Force rebuild specific client
./hive --docker.nocache "clients/go-ethereum" --sim ethereum/eest/consume-engine

# Show build output
./hive --docker.buildoutput --sim ethereum/eest/consume-engine
```

**Missing build arguments:**

```yaml
# Ensure required arguments are specified
- client: go-ethereum
  dockerfile: git
  build_args:
    github: ethereum/go-ethereum  # Required for git builds
    tag: master                   # Required for git builds
```

### Container Issues

**Client startup timeout:**

```bash
# Increase client startup timeout
./hive --client.checktimelimit=60s --sim ethereum/eest/consume-engine
```

**Port conflicts:**

```yaml
# Ensure port configuration matches simulator expectations
environment:
  HIVE_CHECK_LIVE_PORT: "8545"  # For RLP simulator
  HIVE_CHECK_LIVE_PORT: "8551"  # For Engine simulator
```

### Configuration Validation

**Test configuration without running tests:**

```bash
# Dry run to validate configuration
./hive --sim ethereum/eest/consume-engine \
  --client-file test-config.yaml \
  --client test-client \
  --sim.limit "collectonly:.*" \
  --docker.output
```

**Check available clients:**

```bash
# List configured clients
./hive --sim ethereum/eest/consume-engine \
  --client-file clients.yaml \
  --docker.output | grep "Available clients"
```

## Best Practices

### Configuration Organization

1. **Separate files by purpose:**
   - `clients-stable.yaml`: Stable releases for CI
   - `clients-develop.yaml`: Development versions
   - `clients-fork.yaml`: Fork-specific configurations

2. **Use descriptive nametags:**

   ```yaml
   nametag: geth-v1.13.8-stable      # Good
   nametag: test                     # Bad
   ```

3. **Document custom configurations:**

   ```yaml
   # Prague devnet testing configuration
   - client: go-ethereum
     nametag: prague-devnet-4
     dockerfile: git
     build_args:
       github: lightclient/go-ethereum
       tag: prague-devnet-4
   ```

### Performance Optimization

1. **Use Docker image caching:**

   ```bash
   # Avoid --docker.pull unless needed
   ./hive --sim ethereum/eest/consume-engine  # Uses cached images
   ```

2. **Parallel testing:**

   ```bash
   ./hive --sim.parallelism 4 --sim ethereum/eest/consume-engine
   ```

3. **Efficient client selection:**

   ```bash
   # Test specific clients rather than all
   --client go-ethereum,besu  # Instead of all clients
   ```

## See Also

- [Hive Simulator Guide](./hive.md)
- [Development Mode Guide](./dev_mode.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Consume Command Overview](./index.md)
