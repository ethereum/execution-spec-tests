# Consume Command

## What is consume?

The `consume` command is a utility that helps clients run and validate test fixtures. It provides different methods for consuming test fixtures, making it flexible for various testing scenarios.

## When to Use

Use the consume command when you need to:

- Run specific test fixtures against your client implementation
- Debug client behavior with detailed logging
- Validate your client's conformance to Ethereum specifications

## Basic Usage

```bash
uv run consume [OPTIONS] COMMAND [ARGS]...
```

The command supports four consumption methods:

- `direct`: Via the `blocktest` interface
- `engine`: Via the Engine API
- `hive`: Via all available hive methods
- `rlp`: Via RLP-encoded blocks

## Common Options

All consumption methods support these basic options:

- `--input INPUT`: Specify the JSON test fixtures source
  - Local directory (default: './fixtures')
  - URL pointing to a fixtures.tar.gz archive
  - Special keywords: 'stdin', 'latest-stable', 'latest-develop'
- `--fork FORK`: Only consume tests for the specified fork
- `--no-html`: Don't generate an HTML test report

## Method-Specific Options

### Direct Method

```bash
uv run consume direct [OPTIONS]
```

Additional options:

- `--evm-bin EVM_BIN`: Path to an evm executable that provides `blocktest`
- `--traces`: Collect execution traces from the transition tool

### Engine Method

```bash
uv run consume engine [OPTIONS]
```

Additional options:

- `--timing-data`: Log timing data for each test case execution

### Hive Method

```bash
uv run consume hive [OPTIONS]
```

Additional options:

- `--timing-data`: Log timing data for each test case execution

When using Hive, additional configuration is available through Hive's own command-line interface:

```bash
./hive --sim ethereum/pyspec --client-file CONFIG_FILE --client CLIENT_NAME
```

Hive-specific options:

- `--dev`: Enable development mode (preserves containers and logs)
- `--client-file`: Specify client configuration file
- `--client`: Specify which client to test

### RLP Method

```bash
uv run consume rlp [OPTIONS]
```

Additional options:

- `--timing-data`: Log timing data for each test case execution

## Examples

1. Running direct tests with traces:

   ```bash
   uv run consume direct --input ./fixtures --traces
   ```

2. Running engine tests for a specific fork:

   ```bash
   uv run consume engine --fork shanghai --timing-data
   ```

3. Running Hive tests with development mode:

   ```bash
   # First, start Hive in dev mode
   ./hive --dev --client-file configs/prague.yaml --client geth

   # Then run the consume command
   uv run consume hive --input ./fixtures
   ```

4. Running RLP tests:

   ```bash
   uv run consume rlp --input latest-stable --timing-data
   ```
