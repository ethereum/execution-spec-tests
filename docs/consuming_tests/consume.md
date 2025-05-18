# Consume Command

The `consume` command provides a unified way to run test fixtures against execution clients directly within the execution-spec-tests framework. It offers several subcommands for different consumption methods and use cases.

## What is Consume?

The `consume` command is a tool designed to help client developers and testers run Ethereum test fixtures against execution clients in various ways. It acts as a bridge between the test fixtures and the client implementation, allowing you to verify that your client correctly processes the fixtures according to the Ethereum specification.

## When Should It Be Used?

You should use the `consume` command when:

1. Testing a client implementation against official Ethereum test fixtures
2. Verifying consensus rules in your client
3. Debugging client behavior with specific test cases
4. Running integration tests with Hive

## How to Use It

The `consume` command has several subcommands, each designed for a different method of consumption:

```bash
uv run consume [SUBCOMMAND] [OPTIONS]
```

### Subcommands

#### `direct`

```bash
uv run consume direct --bin=/path/to/client [OPTIONS]
```

Clients consume directly via the `blocktest` or `statetest` interface. This is the most straightforward method of testing, where the client uses its built-in interface to process test fixtures.

**Examples:**

```bash
# Run with a specific client implementation
uv run consume direct --bin=./client/evm --input=./fixtures/state_tests

# Run with multiple clients for comparison
uv run consume direct --bin=./client1/evm --bin=./client2/evm --input=./fixtures/state_tests
```

#### `engine`

```bash
uv run consume engine [OPTIONS]
```

Client consumes via the Engine API. This method is used for testing post-Merge forks by sending payloads through the Engine API.

**Examples:**

```bash
# Run Engine API tests with a specific client
uv run consume engine --client=geth --input=./fixtures/blockchain_tests_engine
```

#### `rlp`

```bash
uv run consume rlp [OPTIONS]
```

Client consumes RLP-encoded blocks on startup. This is useful for testing block processing by providing pre-encoded blocks.

**Examples:**

```bash
# Run RLP tests with specific clients
uv run consume rlp --client=geth --input=./fixtures/blockchain_tests
```

#### `hive`

```bash
uv run consume hive [OPTIONS]
```

Client consumes via all available Hive methods (both `rlp` and `engine`). This is useful for comprehensive testing with Hive.

**Examples:**

```bash
# Run all Hive tests
uv run consume hive --client=geth --input=./fixtures/blockchain_tests
```

#### `cache`

```bash
uv run consume cache [OPTIONS]
```

This subcommand is used to download and cache test fixtures for later use. It's particularly useful for Hive testing where Docker can download fixtures as a cached step.

**Examples:**

```bash
# Cache the latest stable release
uv run consume cache --input=stable@latest

# Cache a specific version
uv run consume cache --input=stable@v4.2.0
```

### Common Options

Here are the common options that can be used with all `consume` subcommands:

- `--input=PATH`: Specify the path to test fixtures or a release spec (e.g., `stable@latest` or `develop@latest`)
- `--client=NAME`: Specify the client implementation to test (for `engine`, `rlp`, and `hive`)
- `--client-config=FILE`: Specify a client configuration file (for Hive methods)
- `--dev`: Enable development mode which skips some validation steps
- `--disable-strict-exception-matching`: Disable strict checking of exception messages (for Engine API)
- `-k "EXPRESSION"`: Only run tests that match the given expression

## Hive Considerations

When running with Hive, there are additional options and behaviors to consider:

### Development Mode

The `--dev` flag enables development mode, which is particularly useful for Hive testing as it:

- Relaxes certain validation requirements
- Allows faster iteration during development
- Skips checks that might be too strict for work-in-progress code

```bash
uv run consume hive --dev --client=geth
```

### Client Configuration

The `--client-config` flag allows you to specify a configuration file for the client:

```bash
uv run consume hive --client=geth --client-config=./client_config.json
```

This is useful for:
- Setting specific client options
- Enabling or disabling features
- Configuring network parameters

### Environment Variables

When running in Hive, the following environment variables are automatically handled:

- `HIVE_TEST_PATTERN`: Converted to `--sim.limit` for test filtering
- `HIVE_PARALLELISM`: Converted to `-n` for parallelism control

## Using Release Fixtures

The `consume` command can download and run fixtures directly from GitHub releases:

```bash
# Run latest stable fixtures
uv run consume direct --bin=./client/evm --input=stable@latest

# Run specific version
uv run consume direct --bin=./client/evm --input=stable@v4.2.0

# Run latest development fixtures
uv run consume direct --bin=./client/evm --input=develop@latest
```

This eliminates the need to manually download and extract the fixture archives.

## Debugging and Troubleshooting

For detailed debugging output, add the `-v` or `--verbose` flag:

```bash
uv run consume direct --bin=./client/evm --input=./fixtures/state_tests -v
```

To enable trace collection for deeper analysis:

```bash
uv run consume direct --bin=./client/evm --input=./fixtures/state_tests --traces
```

For saving debug dumps to a directory:

```bash
uv run consume direct --bin=./client/evm --input=./fixtures/state_tests --dump-dir=./debug_output
``` 
