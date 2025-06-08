# Common Simulator Options

All EEST Hive simulators (`eest/consume-engine` and `eest/consume-rlp`) share common command-line options and patterns.

## Basic Usage

```bash
# Via Hive directly
./hive --sim ethereum/eest/consume-engine --client go-ethereum

# Via consume command in development mode
uv run consume engine --input ./fixtures
```

## Common Options

### Specifying the Fixture Input

See [`consume cache` and Fixture Inputs](../consume/cache.md#consume-command-inputs). Here's some brief examples:

```bash
# Local directory
--input ./fixtures

# Release versions
--input stable@latest
--input develop@v4.1.0

# Direct URL
--input https://github.com/ethereum/execution-spec-tests/releases/download/v4.1.0/fixtures_develop.tar.gz
```

### Test Selection

**Pattern matching with `--sim.limit`:**

```bash
# Regex pattern
./hive --sim ethereum/eest/consume-engine --sim.limit ".*eip4844.*"

# Exact test ID
./hive --sim ethereum/eest/consume-rlp --sim.limit "id:tests/cancun/eip4844_blobs/test_blob_txs.py::test_sufficient_balance_blob_tx"
```

**Development mode with `-k` (pytest-style):**

```bash
# Keyword matching
uv run consume engine -k "eip4844"

# Complex conditions
uv run consume rlp -k "eip4844 and fork_Cancun and not invalid"
```

### Fork Filtering

```bash
# Run only specific fork tests
--fork cancun
--fork shanghai
```

### Performance Options

**Parallelism:**

```bash
# Simulator parallelism
./hive --sim ethereum/eest/consume-rlp --sim.parallelism 4

# Multi-client parallel execution
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum,besu,nethermind,reth \
  --sim.parallelism 2
```

**Timing data:**

```bash
# Enable detailed timing logs
--timing-data
```

### Output Options

```bash
# Disable HTML report generation
--no-html

# Verbose logging (development mode)
-v

# Hive simulator logging
./hive --sim ethereum/eest/consume-engine --sim.loglevel 5
```

## Client Configuration

See [Client Configuration Guide](./client_config.md) for details on:

- Client YAML file format
- Building from different sources (binary, git, local)
- Multiple client configurations

Basic example:

```bash
./hive --sim ethereum/eest/consume-engine \
  --client-file clients.yaml \
  --client go-ethereum
```

### Multiple Clients

```bash
./hive --sim ethereum/eest/consume-engine \
  --client-file multi-client.yaml \
  --client go-ethereum,besu,nethermind,reth
```

### Parallel testing

```bash
./hive --sim.parallelism 4 --sim ethereum/eest/consume-engine
```

### Container Issues

Increase client timeout:

```bash
./hive --client.checktimelimit=60s --sim ethereum/eest/consume-engine
```
