# Consume Engine Method

## Overview

The Engine consumption method tests execution clients via the Engine API, simulating the interaction between consensus and execution layers in post-merge Ethereum. This method provides the most realistic testing environment for production Ethereum client behavior, covering consensus integration, payload validation, and state synchronization.

## How It Works

The `consume engine` command:

1. **Initializes the execution client** with genesis state
2. **Connects via Engine API** (port 8551) simulating a consensus client
3. **Sends forkchoice updates** to establish the chain head
4. **Submits payloads** using `engine_newPayload` calls
5. **Validates responses** and final state against expected results
6. **Tests error conditions** and exception handling

This method replicates the real-world interaction between consensus clients (like Prysm, Lighthouse) and execution clients during block production and validation.

## Command Syntax

```bash
uv run consume engine [OPTIONS]
```

See [Common Options](./common_options.md) for options shared with all simulators.

## Usage Examples

### Basic Usage

**Run Engine API tests from local fixtures:**

```bash
uv run consume engine --input ./fixtures
```

**Run tests for specific fork:**

```bash
uv run consume engine --input ./fixtures --fork cancun
```

**Run with detailed timing and logging:**

```bash
uv run consume engine --input ./fixtures --timing-data -v
```

### Using Remote Fixtures

**Latest development release:**

```bash
uv run consume engine --input develop@latest
```

**Specific release for Prague testing:**

```bash
uv run consume engine --input https://github.com/ethereum/execution-spec-tests/releases/download/pectra-devnet-4%40v1.0.1/fixtures_pectra-devnet-4.tar.gz
```

**Cached fixtures (after first download):**

```bash
uv run consume engine --input cached_downloads/v4.1.0/fixtures_develop/fixtures
```

### Test Filtering

**Filter by EIP implementation:**

```bash
# EIP-4844 (blob transactions)
uv run consume engine -k "eip4844" --fork cancun

# EIP-1559 (fee market)  
uv run consume engine -k "eip1559" --fork london

# Multiple EIPs
uv run consume engine -k "eip4844 or eip1559"
```

**Run specific test by exact ID:**

```bash
uv run consume engine --sim.limit "id:tests/cancun/eip4844_blobs/test_blob_txs.py::test_sufficient_balance_blob_tx[fork_Cancun-blockchain_test_engine-single_one_calldata]"
```

**Fork-specific testing:**

```bash
# All Cancun tests
uv run consume engine -k "fork_Cancun"

# Cross-fork comparison
uv run consume engine -k "fork_London or fork_Shanghai or fork_Cancun"
```

**Dry run to see matching tests:**

```bash
uv run consume engine --collect-only -q -k "blob"
```

## Via Hive Simulators

The Engine method runs through the `ethereum/eest/consume-engine` Hive simulator:

### Direct Hive Execution

```bash
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum \
  --client-file clients.yaml \
  --sim.limit ".*fork_Cancun.*"
```

### Multi-Client Testing

```bash
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum,besu,nethermind,reth \
  --client-file clients.yaml \
  --sim.parallelism 2
```

### Hive Development Mode

**Start Hive in dev mode:**

```bash
./hive --dev \
  --client go-ethereum \
  --client-file clients.yaml \
  --docker.output \
  --sim.loglevel 5
```

**Run EEST consume commands:**

```bash
export HIVE_SIMULATOR=http://127.0.0.1:3000
uv run consume engine --input develop@latest -k "eip4844"
```

## Engine API Integration

### Required Engine API Endpoints

Clients must implement these Engine API methods:

| Method | Purpose | Usage in Tests |
|--------|---------|----------------|
| `engine_newPayloadV1` | Submit payload for validation | Pre-merge payloads |
| `engine_newPayloadV2` | Submit payload with withdrawals | Post-Shanghai payloads |
| `engine_newPayloadV3` | Submit payload with blob data | Post-Cancun payloads |
| `engine_forkchoiceUpdatedV1` | Update chain head | Chain progression |
| `engine_forkchoiceUpdatedV2` | Update with withdrawals | Post-Shanghai chain updates |
| `engine_forkchoiceUpdatedV3` | Update with blob data | Post-Cancun chain updates |
| `engine_getPayloadV1` | Retrieve built payload | Pre-merge block building |
| `engine_getPayloadV2` | Retrieve with withdrawals | Post-Shanghai block building |
| `engine_getPayloadV3` | Retrieve with blob data | Post-Cancun block building |

### Client Configuration Requirements

**Port Configuration:**

- Engine API must listen on port 8551
- HTTP or WebSocket supported (HTTP used by default)
- JWT authentication not required for testing

**State Management:**

- Maintain consistent state across API calls
- Handle forkchoice updates correctly
- Validate payloads according to fork rules

**Error Handling:**

- Return appropriate error codes for invalid payloads
- Handle malformed requests gracefully
- Maintain API availability during testing

### Engine API Call Flow

**Typical test sequence:**

1. **Initialize:** Submit genesis forkchoice update
2. **Validate:** Call `engine_newPayload` with test payload
3. **Update:** Send `engine_forkchoiceUpdated` to make payload canonical
4. **Verify:** Check client state matches expected results

**Example flow:**

```python
# Pseudo-code for Engine API test flow
def test_engine_api():
    # 1. Initialize chain
    genesis_hash = client.get_genesis_hash()
    forkchoice_response = client.engine_forkchoice_updated(
        head=genesis_hash,
        safe=genesis_hash, 
        finalized=genesis_hash
    )
    assert forkchoice_response.status == "VALID"
    
    # 2. Submit payload
    payload_response = client.engine_new_payload(test_payload)
    assert payload_response.status == "VALID"
    
    # 3. Update forkchoice
    forkchoice_response = client.engine_forkchoice_updated(
        head=test_payload.block_hash,
        safe=genesis_hash,
        finalized=genesis_hash
    )
    assert forkchoice_response.status == "VALID"
    
    # 4. Verify final state
    final_state = client.get_state()
    assert final_state == expected_state
```

## Test Coverage and Scope

### Engine API Specific Features

**Payload Validation:**

- Block header validation via Engine API
- Transaction execution and state updates
- Gas limit and gas used validation
- Withdrawal processing (post-Shanghai)
- Blob transaction handling (post-Cancun)

**Consensus Integration:**

- Forkchoice updates and chain reorganizations
- Safe and finalized block tracking
- Payload building and retrieval
- Invalid payload handling

**Fork-Specific Testing:**

- Paris: Basic Engine API functionality
- Shanghai: Withdrawal support
- Cancun: Blob transaction support
- Future forks: New consensus features

### Error Conditions Tested

**Invalid Payloads:**

- Malformed block headers
- Invalid transaction data
- Incorrect state roots
- Gas limit violations
- Fork-specific validation failures

**API Error Handling:**

- Invalid method calls
- Malformed JSON-RPC requests
- Out-of-order payload submissions
- Invalid forkchoice states

**Network Conditions:**

- Connection timeouts
- API unavailability
- Slow response times
- Partial data transmission

## Debugging Failed Tests

### Understanding Engine API Failures

**Common failure patterns:**

1. **Payload rejection:** `engine_newPayload` returns `INVALID`
2. **State mismatch:** Final state differs from expected
3. **API errors:** Client returns error codes or exceptions
4. **Timeout issues:** Client doesn't respond within expected time

### Debugging Workflow

**1. Enable verbose logging:**

```bash
uv run consume engine -v --input ./fixtures -k "failing_test"
```

**2. Check Engine API responses:**

```bash
# With Hive, enable client output
./hive --sim ethereum/eest/consume-engine \
  --client your-client \
  --sim.limit "id:failing_test_id" \
  --docker.output \
  --sim.loglevel 5
```

**3. Analyze timing data:**

```bash
uv run consume engine --timing-data -k "failing_test"
```

**4. Compare with working clients:**

```bash
# Test same case with reference client
./hive --sim ethereum/eest/consume-engine \
  --client go-ethereum \
  --sim.limit "id:failing_test_id"
```

### Common Issues and Solutions

**Issue: `engine_newPayload` returns `INVALID` unexpectedly**

**Debug steps:**

1. Check payload structure in test fixture
2. Verify client logs for specific validation errors
3. Compare with Engine API specification
4. Test with simpler payload first

#### Issue: Forkchoice update failures

**Debug steps:**

1. Verify chain state before forkchoice update
2. Check block hash consistency
3. Ensure proper genesis initialization
4. Validate fork configuration

#### Issue: State root mismatches

**Debug steps:**

1. Enable state debugging in client
2. Compare transaction execution results
3. Check gas usage and receipt validation
4. Verify precompile behavior

## Performance Analysis

### Timing Data Interpretation

When using `--timing-data`, key metrics include:

**Client Startup Time:**

- Time to initialize and become ready
- Engine API endpoint availability
- Genesis state loading

**API Response Times:**

- `engine_newPayload` processing time
- `engine_forkchoiceUpdated` response time
- State synchronization delays

**Overall Test Execution:**

- End-to-end test completion time
- Payload processing throughput
- Memory and CPU usage patterns

### Optimization Strategies

**For Client Development:**

```bash
# Profile specific operations
uv run consume engine --timing-data -k "heavy_computation_tests"

# Test incremental changes
uv run consume engine -k "specific_feature" --timing-data
```

**For Test Execution:**

```bash
# Reduce logging overhead
uv run consume engine --input ./fixtures --fork cancun

# Use targeted testing
uv run consume engine -k "eip4844" --fork cancun
```

## Comparison with Other Methods

### Engine vs RLP Method

| Aspect | Engine Method | RLP Method |
|--------|---------------|------------|
| **API Layer** | Engine API (realistic) | Direct block import |
| **Consensus simulation** | Yes (forkchoice updates) | No |
| **Fork support** | Post-merge (Paris+) | All forks |
| **Debugging complexity** | Higher (API interactions) | Lower (direct block processing) |
| **Production similarity** | Very high | Medium |
| **Performance overhead** | Higher (API calls) | Lower (direct import) |

### Engine vs Direct Method

| Aspect | Engine Method | Direct Method |
|--------|---------------|---------------|
| **Client integration** | Full client via API | EVM transition tool only |
| **State management** | Client handles state | EEST manages state |
| **Network simulation** | Engine API calls | Direct CLI execution |
| **Fork testing** | Post-merge consensus | All forks via t8n tools |

## Best Practices

### Test Development

1. **Start with basic cases:**

   ```bash
   uv run consume engine -k "basic_engine_tests" --fork cancun
   ```

2. **Test fork-specific features:**

   ```bash
   # Shanghai withdrawals
   uv run consume engine -k "withdrawal" --fork shanghai
   
   # Cancun blobs
   uv run consume engine -k "blob" --fork cancun
   ```

3. **Validate error conditions:**

   ```bash
   uv run consume engine -k "invalid" --timing-data
   ```

### Client Development

1. **Incremental Engine API implementation:**

   ```bash
   # Test individual API methods
   uv run consume engine -k "newPayload" --fork paris
   uv run consume engine -k "forkchoice" --fork paris
   ```

2. **Fork migration testing:**

   ```bash
   # Test across fork boundaries
   uv run consume engine -k "fork_Paris or fork_Shanghai"
   ```

3. **Performance regression testing:**

   ```bash
   # Compare timing between versions
   uv run consume engine --timing-data --input ./fixtures > baseline.log
   # ... implement changes ...
   uv run consume engine --timing-data --input ./fixtures > updated.log
   ```

### Production Readiness

1. **Comprehensive testing:**

   ```bash
   # Test all supported forks
   uv run consume engine --input develop@latest
   ```

2. **Multi-client validation:**

   ```bash
   # Compare behavior across clients
   ./hive --sim ethereum/eest/consume-engine \
     --client go-ethereum,besu,nethermind,reth
   ```

3. **Stress testing:**

   ```bash
   # High-load scenarios
   uv run consume engine -k "large_state" --timing-data
   ```

## Future Developments

### Upcoming Fork Support

The Engine method will continue to evolve with new Ethereum forks:

- **Prague/Electra**: EIP-7002, EIP-7251, EIP-7594 support
- **Future forks**: New consensus features and Engine API extensions
- **Layer 2 integration**: Optimistic rollup and validium support

### Enhanced Testing

- **Real-time consensus simulation**: More realistic timing constraints
- **Network condition simulation**: Latency and bandwidth testing  
- **Multi-client consensus**: Testing client interoperability
- **Performance benchmarking**: Standardized performance metrics

## See Also

- [RLP Method Documentation](./rlp.md)
- [Hive Simulator Guide](./index.md)
- [Development Mode Guide](./dev_mode.md)
- [Client Configuration Guide](./client_config.md)
- [Troubleshooting Guide](../troubleshooting.md)
- [Consume Command Overview](../index.md)
- [Engine API Specification](https://github.com/ethereum/execution-apis/tree/main/src/engine)
