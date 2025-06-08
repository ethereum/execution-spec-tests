# Consume RLP Method

## Overview

The RLP consumption method tests execution clients by feeding them RLP-encoded blocks directly, similar to the block import process during historical synchronization. This method tests the client's core block processing logic without the overhead of network protocols or consensus mechanisms.

## How It Works

The `consume rlp` command:

1. **Reads blockchain test fixtures** from the specified input source
2. **Extracts RLP-encoded blocks** from the fixture files  
3. **Provides blocks to the client** via files in the `/blocks/` directory
4. **Starts the client** with the genesis state and block files
5. **Validates client behavior** by checking the final state matches expectations

This method simulates how clients import blocks during historical sync, testing the complete block validation and state transition pipeline.

## Command Syntax

```bash
uv run consume rlp [OPTIONS]
```

See [Common Options](../../hive/common_options.md) for options shared with all simulators.

## Usage Examples

### Basic Usage

**Run all RLP tests from local fixtures:**

```bash
uv run consume rlp --input ./fixtures
```

**Run tests for specific fork:**

```bash
uv run consume rlp --input ./fixtures --fork cancun
```

**Run with performance timing:**

```bash
uv run consume rlp --input ./fixtures --timing-data
```

### Using Remote Fixtures

**Latest stable release:**

```bash
uv run consume rlp --input stable@latest
```

**Specific release version:**

```bash
uv run consume rlp --input develop@v4.1.0
```

**Direct URL:**

```bash
uv run consume rlp --input https://github.com/ethereum/execution-spec-tests/releases/download/v4.1.0/fixtures_develop.tar.gz
```

### Test Filtering

**Filter by test pattern:**

```bash
# Using --sim.limit (exact regex)
uv run consume rlp --sim.limit ".*eip1559.*"

# In development mode, using pytest -k syntax
uv run consume rlp -k "eip1559 and fork_London"
```

**Run specific test by ID:**

```bash
uv run consume rlp --sim.limit "id:tests/london/eip1559_fee_market/test_base_fee.py::test_base_fee[fork_London-blockchain_test-exact_balance_plus_1]"
```

**Dry run to see matching tests:**

```bash
uv run consume rlp --collect-only -q -k "blob_txs"
```

## Via Hive Simulators

The RLP method can also be run through Hive for containerized testing:

### Direct Hive Execution

```bash
./hive --sim ethereum/eest/consume-rlp \
  --client go-ethereum \
  --sim.limit ".*fork_Cancun.*"
```

### Hive Development Mode

**Start Hive:**

```bash
./hive --dev --client go-ethereum --docker.output
```

**Run EEST consume:**

```bash
export HIVE_SIMULATOR=http://127.0.0.1:3000
uv run consume rlp --input stable@latest -k "eip4844"
```

## Client Integration Requirements

For clients to work with the RLP consumption method:

### File Structure Expected

The client container receives:

- **`/genesis.json`**: Genesis block and initial state
- **`/blocks/0001.rlp`**: First block encoded as RLP
- **`/blocks/0002.rlp`**: Second block encoded as RLP  
- **`/blocks/NNNN.rlp`**: Additional blocks in sequence

### Client Behavior Requirements

1. **Genesis Initialization:**
   - Load genesis state from `/genesis.json`
   - Initialize blockchain with genesis block

2. **Block Import:**
   - Import blocks from `/blocks/` directory in numerical order
   - Process each block through normal validation pipeline
   - Continue importing even if some blocks are invalid

3. **State Management:**
   - Maintain state transitions for valid blocks
   - Final state should match expected post-state in fixtures

4. **Error Handling:**
   - Handle invalid blocks gracefully without crashing
   - Continue processing subsequent blocks after invalid ones

### Integration Example

```python
# Pseudo-code for client RLP integration
def import_blocks():
    # Load genesis
    genesis = load_json("/genesis.json")
    blockchain.initialize(genesis)
    
    # Import blocks in order
    block_files = sorted(glob("/blocks/*.rlp"))
    for block_file in block_files:
        block_rlp = read_file(block_file)
        try:
            block = decode_rlp(block_rlp)
            result = blockchain.import_block(block)
            log_result(block_file, result)
        except Exception as e:
            log_error(block_file, e)
            continue  # Continue with next block
```

## Test Coverage and Scope

### What RLP Tests Cover

**Block Processing Pipeline:**

- Block header validation
- Transaction validation and execution
- State root verification
- Receipt root verification
- Gas limit and gas used validation

**State Transitions:**

- Account balance changes
- Contract storage updates
- Contract code deployment
- Account creation and deletion

**EIP Implementations:**

- Fork-specific feature validation
- Gas cost calculations
- New transaction types
- Precompile behavior

### Code Paths Tested

The RLP method exercises client code paths similar to:

- **Historical sync**: Importing pre-validated blocks
- **Block import**: Processing blocks received from peers
- **State transitions**: Executing transactions and updating state
- **Validation logic**: Verifying block and transaction validity

### Complementary Testing

RLP testing complements other testing methods:

- **vs Direct method**: Tests full client instead of just EVM
- **vs Engine method**: Tests historical sync paths vs. consensus integration
- **vs State tests**: Tests complete blocks vs. individual transactions

## Debugging Failed Tests

### Understanding Test Failures

**Common failure types:**

1. **State mismatch**: Client final state differs from expected
2. **Invalid block acceptance**: Client accepts block that should be invalid  
3. **Valid block rejection**: Client rejects block that should be valid
4. **Exception errors**: Wrong exception type or message

### Debugging Workflow

**1. Identify failing test:**

```bash
# Run with verbose output
uv run consume rlp -v --input ./fixtures -k "failing_test"
```

**2. Examine test fixture:**

```bash
# Look at the specific test file
find ./fixtures -name "*failing_test*" -type f | head -1 | xargs cat | jq .
```

**3. Check client logs:**

```bash
# In Hive mode with client output
./hive --sim ethereum/eest/consume-rlp \
  --client your-client \
  --sim.limit "id:failing_test_id" \
  --docker.output
```

**4. Compare expected vs actual:**

```bash
# Enable timing data to see performance metrics
uv run consume rlp --timing-data -k "failing_test"
```

### Exception Debugging

**Exception matching errors:**

```text
expected exception: "TransactionException.INSUFFICIENT_ACCOUNT_FUNDS"
returned exception: "insufficient balance"
```

**Solutions:**

1. **Update exception mapper:**

   ```python
   # In src/ethereum_clis/clis/<client>.py
   def map_exception(error_message):
       if "insufficient balance" in error_message:
           return "TransactionException.INSUFFICIENT_ACCOUNT_FUNDS"
   ```

2. **Disable strict matching temporarily:**

   ```bash
   uv run consume rlp --disable-strict-exception-matching=your-client
   ```

## Performance Considerations

### Execution Speed

**Factors affecting performance:**

- **Fixture size**: Number of tests and blocks per test
- **Client startup time**: Time to initialize client container
- **Block processing speed**: Client's block import performance
- **I/O overhead**: Reading RLP files and writing logs

**Optimization strategies:**

```bash
# Reduce logging for faster execution
uv run consume rlp --input ./fixtures --fork shanghai

# Use parallel execution (where supported)
uv run consume rlp -n auto --input ./fixtures

# Use local fixtures to avoid download time
uv run consume rlp --input ./cached_fixtures/
```

### Resource Usage

**Memory requirements:**

- Client memory for state processing
- EEST memory for fixture loading
- Docker overhead for containerized execution

**Disk usage:**

- Fixture files (can be several GB)
- Client database/state storage
- Log files and timing data

## Comparison with Other Methods

### RLP vs Engine API

| Aspect | RLP Method | Engine Method |
|--------|------------|---------------|
| **Code path** | Historical sync / block import | Engine API / consensus integration |
| **Network simulation** | No P2P, direct block import | Simulates consensus client interaction |
| **Fork coverage** | All forks | Post-merge forks (Paris+) |
| **Debugging** | Direct block-by-block analysis | More complex consensus interactions |
| **Speed** | Generally faster | Slower due to API overhead |

### RLP vs Direct Method

| Aspect | RLP Method | Direct Method |
|--------|------------|---------------|
| **Client scope** | Full client integration | EVM transition tool only |
| **Container overhead** | Yes (via Hive) | No (direct CLI) |
| **Debugging complexity** | Higher (full client) | Lower (isolated EVM) |
| **Real-world similarity** | High (full block processing) | Medium (transaction-level) |

## Best Practices

### Test Selection

1. **Start with stable forks:**

   ```bash
   uv run consume rlp --fork cancun --input stable@latest
   ```

2. **Use targeted testing:**

   ```bash
   uv run consume rlp -k "eip1559" --input ./fixtures
   ```

3. **Progressive testing:**

   ```bash
   # Test individual EIPs before comprehensive runs
   uv run consume rlp -k "eip4844" --fork cancun
   uv run consume rlp -k "eip1559" --fork london
   ```

### Development Workflow

1. **Use development mode for iteration:**

   ```bash
   ./hive --dev --client your-client
   export HIVE_SIMULATOR=http://127.0.0.1:3000
   uv run consume rlp -k "your_test_pattern"
   ```

2. **Enable timing for performance analysis:**

   ```bash
   uv run consume rlp --timing-data -k "performance_tests"
   ```

3. **Use collect-only for test validation:**

   ```bash
   uv run consume rlp --collect-only -q -k "new_tests"
   ```

### Client Development

1. **Test incremental changes:**

   ```bash
   # Test specific functionality
   uv run consume rlp -k "new_feature" --input ./test_fixtures/
   ```

2. **Validate exception handling:**

   ```bash
   # Test with strict exception matching
   uv run consume rlp -k "invalid_blocks"
   ```

3. **Performance regression testing:**

   ```bash
   # Compare timing data between versions  
   uv run consume rlp --timing-data --input ./fixtures > timing_before.log
   # ... make changes ...
   uv run consume rlp --timing-data --input ./fixtures > timing_after.log
   ```
