# Specifying Consume Input Sources

## Overview

The EEST consume framework provides a flexible `--input` system for specifying test fixture sources. This system handles local directories, remote releases, direct URLs, and automatic caching to provide a seamless experience for accessing test fixtures.

## Input Source Types

### Local Directories

**Default behavior:**

```bash
# Uses ./fixtures directory by default
uv run consume engine

# Explicitly specify local directory
uv run consume rlp --input ./my-fixtures
uv run consume engine --input /path/to/fixtures
```

**Requirements for local directories:**

- Directory must exist
- Must contain JSON fixture files
- Supports nested directory structures

### Release Specifications

**Format:** `NAME@VERSION`

**Supported release names:**

- `stable`: Latest stable fork release
- `develop`: Latest development fork release
- Custom release names: e.g., `pectra-devnet-4`, `eip7692`

**Supported version formats:**

- `latest`: Most recent release for the specified name
- `v1.2.3`: Specific semantic version

**Examples:**

```bash
# Latest stable release
uv run consume engine --input stable@latest

# Latest development release  
uv run consume rlp --input develop@latest

# Specific version
uv run consume engine --input stable@v4.1.0
uv run consume rlp --input develop@v4.2.1

# Custom release names
uv run consume cache --input pectra-devnet-6@v1.0.0
uv run consume direct --input eip7692@latest --bin ../go-ethereum/build/bin/evm
```

### Direct URLs

**Supported formats:**

- GitHub release URLs
- Direct links to `.tar.gz` archives
- Any HTTP/HTTPS URL serving fixture archives

**Examples:**

```bash
# GitHub release URL
uv run consume engine --input https://github.com/ethereum/execution-spec-tests/releases/download/v4.1.0/fixtures_develop.tar.gz

# Direct archive URL
uv run consume rlp --input https://example.com/custom-fixtures.tar.gz
```

### Standard Input (stdin)

**Use case:** Streaming fixtures from another process

```bash
# Pipe fixtures from another source
cat fixtures.json | uv run consume engine --input stdin

# From file
uv run consume rlp --input stdin < fixtures.json
```

## Caching System

### Automatic Caching

All remote fixture sources are automatically cached to avoid repeated downloads:

**Default cache location:**

```text
~/.cache/ethereum-execution-spec-tests/cached_downloads/
```

**Cache structure:**

```text
cached_downloads/
├── ethereum/
│   └── execution-spec-tests/
│       ├── v4.1.0/
│       │   └── fixtures_develop/
│       └── v4.2.0/
│           └── fixtures_stable/
└── other/
    └── custom-archives/
```

### Using Cached Fixtures

**Reuse automatically cached fixtures:**

```bash
# First run downloads and caches
uv run consume engine --input stable@latest

# Subsequent runs use cached version
uv run consume rlp --input stable@latest  # Uses cache

# Manually specify cached path
uv run consume engine --input ~/.cache/ethereum-execution-spec-tests/cached_downloads/ethereum/execution-spec-tests/v4.1.0/fixtures_develop
```

### Cache Management

**Download without running tests:**

```bash
# Download and cache fixtures only
uv run consume cache --input stable@latest
uv run consume cache --input develop@v4.1.0
uv run consume cache --input https://example.com/fixtures.tar.gz
```

**Custom cache location:**

```bash
# Specify custom cache directory
uv run consume engine --input stable@latest --cache-folder /custom/cache/path
```

**Check cache status:**

```bash
# Shows if fixtures were cached or downloaded
uv run consume cache --input stable@latest
```

**Example output:**

```text
Fixtures already cached.
Path: /home/user/.cache/ethereum-execution-spec-tests/cached_downloads/ethereum/execution-spec-tests/v4.1.0/fixtures_stable
Input: https://github.com/ethereum/execution-spec-tests/releases/download/v4.1.0/fixtures_stable.tar.gz
Release page: https://github.com/ethereum/execution-spec-tests/releases/tag/v4.1.0
```

## Practical Examples

### Development Workflow

**1. Quick testing with latest stable:**

```bash
uv run consume engine --input stable@latest -k "eip4844"
```

**2. Testing development features:**

```bash
uv run consume rlp --input develop@latest --fork prague
```

**3. Comparing versions:**

```bash
# Test against stable
uv run consume engine --input stable@latest -k "eip1559" 

# Test against development
uv run consume engine --input develop@latest -k "eip1559"
```

**4. Development mode examples (with Hive dev mode running):**

```bash
# Basic engine testing with specific test
uv run consume engine --input develop@latest \
  --sim.limit "id:tests/istanbul/eip1344_chainid/test_chainid.py::test_chainid[fork_Prague-blockchain_test_engine_from_state_test]"

# Testing with fork filtering and pytest markers
uv run consume engine --input develop@latest -k "test_chainid" -m "Prague"

# Parallel execution for faster testing
uv run consume rlp --input develop@latest --sim.limit ".*chainid.*" -n 4

# Custom release testing
uv run consume direct --input pectra-devnet-6@v1.0.0 -k chainid --bin ../go-ethereum/build/bin/evm

# Debug mode with detailed output  
uv run consume rlp --input develop@latest --sim.limit ".*chainid.*" -m "Cancun" --eest-log-level DEBUG -s
```

### CI/CD Integration

**Cache fixtures for faster CI runs:**

```bash
# In CI setup phase
uv run consume cache --input stable@latest
uv run consume cache --input develop@latest

# In test phase (uses cached fixtures)
uv run consume engine --input stable@latest
uv run consume rlp --input develop@latest
```

### Local Development

**Using local fixture builds:**

```bash
# After running fill command
uv run fill --fork cancun tests/cancun/eip4844_blobs/

# Test against local fixtures
uv run consume engine --input ./fixtures --fork cancun
```

**Mixed testing approach:**

```bash
# Test latest features against development fixtures
uv run consume engine --input develop@latest -k "new_feature"

# Regression test against stable
uv run consume engine --input stable@latest -k "regression_tests"

# Performance test with local optimized fixtures
uv run consume rlp --input ./optimized-fixtures --timing-data
```

## Via Hive Simulators

When using Hive simulators, fixtures are specified via build arguments.

### Critical Best Practice: Matching EEST Branch with Fixture Version

**Always specify the EEST branch that matches your fixture version** to avoid incompatibilities between fixture JSON format and internal data structures:

```bash
# RECOMMENDED: Match branch with fixture version
./hive --sim ethereum/eest/consume-engine \
  --sim.buildarg fixtures=https://github.com/ethereum/execution-spec-tests/releases/download/v4.3.0/fixtures_develop.tar.gz \
  --sim.buildarg branch=v4.3.0 \
  --client go-ethereum

# Using release specification with matching branch
./hive --sim ethereum/eest/consume-engine \
  --sim.buildarg fixtures=stable@latest \
  --sim.buildarg branch=v4.3.0 \
  --client go-ethereum
```

### Comprehensive Hive Examples

**Basic usage:**

```bash
# Single client with specific version
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum \
  --sim.buildarg fixtures=https://github.com/ethereum/execution-spec-tests/releases/download/v4.3.0/fixtures_develop.tar.gz \
  --sim.buildarg branch=v4.3.0

# Multiple clients with configuration file  
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum,nethermind \
  --client-file clients_pectra.yaml \
  --sim.buildarg fixtures=stable@latest \
  --sim.buildarg branch=v4.3.0
```

**Production-ready configuration:**

```bash
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum,nethermind \
  --client-file clients_pectra.yaml \
  --client.checktimelimit 180s \
  --sim.parallelism 4 \
  --docker.buildoutput \
  --sim.buildarg fixtures=https://github.com/ethereum/execution-spec-tests/releases/download/v4.3.0/fixtures_develop.tar.gz \
  --sim.buildarg branch=v4.3.0 \
  --sim.loglevel 3 \
  --results-root results
```

**Test filtering with Hive:**

```bash
# Regex pattern filtering
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum \
  --sim.buildarg fixtures=develop@latest \
  --sim.buildarg branch=v4.3.0 \
  --sim.limit ".*chainid.*"

# Exact test ID
./hive --sim ethereum/eest/consume-engine \
  --client besu \
  --sim.buildarg fixtures=stable@latest \
  --sim.buildarg branch=v4.3.0 \
  --sim.limit "id:tests/istanbul/eip1344_chainid/test_chainid.py::test_chainid[fork_Cancun-blockchain_test_engine_from_state_test]"
```

**RLP simulator examples:**

```bash
# Using ethereum/tests repository
./hive --sim ethereum/eest/consume-rlp \
  --client reth \
  --client-file clients_pectra.yaml \
  --sim.buildarg fixtures=https://github.com/ethereum/tests/releases/download/v17.0/fixtures_blockchain_tests.tgz \
  --sim.buildarg branch=v4.3.0 \
  --sim.limit ".*Prague.*"

# Development testing
./hive --sim ethereum/eest/consume-rlp \
  --client go-ethereum \
  --client-file clients_pectra.yaml \
  --docker.buildoutput \
  --sim.buildarg fixtures=develop@latest \
  --sim.buildarg branch=main \
  --sim.parallelism 8
```

**Debug and development options:**

```bash
# Force rebuild and show output
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum \
  --docker.buildoutput \
  --docker.nocache consume \
  --sim.buildarg fixtures=develop@latest \
  --sim.buildarg branch=fix/consume-reproduce-command \
  --sim.limit ".*chainid.*"

# Single test with detailed logging
./hive --sim ethereum/eest/consume-engine \
  --client besu \
  --client.checktimelimit 180s \
  --docker.buildoutput \
  --sim.buildarg fixtures=stable@latest \
  --sim.buildarg branch=v4.3.0 \
  --sim.loglevel 5 \
  --sim.limit "id:tests/istanbul/eip1344_chainid/test_chainid.py::test_chainid[fork_Paris-blockchain_test_engine_from_state_test]"
```

## Troubleshooting

### Common Issues

**"Fixture directory does not exist":**

```bash
# Check path exists
ls -la ./fixtures

# Use absolute path
uv run consume engine --input /absolute/path/to/fixtures
```

**"No JSON files found":**

```bash
# Check for JSON files
find ./fixtures -name "*.json" | head -5

# Verify fixture structure
ls -la ./fixtures/blockchain_tests_engine/
```

**"Download failed":**

```bash
# Check network connectivity
curl -I https://github.com/ethereum/execution-spec-tests/releases/latest

# Try specific version
uv run consume engine --input stable@v4.1.0
```

**"Cache corruption":**

```bash
# Clear cache and re-download
rm -rf ~/.cache/ethereum-execution-spec-tests/cached_downloads
uv run consume cache --input stable@latest
```

### Verification

**Check what fixtures are available:**

```bash
# List test cases without running
uv run consume engine --input stable@latest --collect-only -q

# Check specific format availability
ls ~/.cache/ethereum-execution-spec-tests/cached_downloads/ethereum/execution-spec-tests/v4.1.0/fixtures_stable/blockchain_tests_engine/
```

**Validate fixture integrity:**

```bash
# Test small subset first
uv run consume engine --input stable@latest -k "simple_test" --fork cancun

# Check fixture format
jq . ~/.cache/ethereum-execution-spec-tests/cached_downloads/ethereum/execution-spec-tests/v4.1.0/fixtures_stable/blockchain_tests_engine/cancun/test.json | head -20
```

## Best Practices

### Performance Optimization

1. **Pre-cache frequently used fixtures:**

   ```bash
   uv run consume cache --input stable@latest
   uv run consume cache --input develop@latest
   ```

2. **Use specific versions for reproducible results:**

   ```bash
   uv run consume engine --input stable@v4.1.0  # Instead of stable@latest
   ```

3. **Leverage local fixtures for development:**

   ```bash
   uv run consume rlp --input ./fixtures  # Fastest option
   ```

### Release Management

1. **Pin versions in CI:**

   ```yaml
   # In CI configuration
   - run: uv run consume engine --input stable@v4.1.0
   ```

2. **Test across multiple releases:**

   ```bash
   for version in v4.0.0 v4.1.0 v4.2.0; do
     uv run consume engine --input stable@$version -k "critical_tests"
   done
   ```

3. **Monitor release updates:**

   ```bash
   # Check latest available releases
   curl -s https://api.github.com/repos/ethereum/execution-spec-tests/releases/latest | jq -r .tag_name
   ```

## See Also

- [Consume Command Overview](./index.md)
- [RLP Method](./rlp.md)
- [Engine Method](./engine.md)
- [Hive Simulators](./hive.md)
- [Troubleshooting](./troubleshooting.md)
