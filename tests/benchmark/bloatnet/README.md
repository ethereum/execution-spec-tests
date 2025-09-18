# BloatNet Benchmark Tests setup guide

## Overview

The Bloatnet benchmarks work on the following fashion:
1. They usually require a previously-deployed state (usually quite large) which the benchmarks
will interact with.
2. The deployment script helpers help deploying the required bytecode for the specific tests.
3. The outputs of the deployment scripts get hardcoded into the codebase such that the benchmarks can interact with them.

## Gas Cost Constants

### BALANCE + EXTCODESIZE Pattern
**Gas per contract: 2,707**
- `PUSH20` (address): 3 gas
- `BALANCE` (cold access): 2,600 gas
- `POP`: 2 gas
- `EXTCODESIZE` (warm): 100 gas
- `POP`: 2 gas

### BALANCE + EXTCODECOPY(single-byte) Pattern 
**Gas per contract: ~2,710**
- `PUSH20` (address): 3 gas
- `BALANCE` (cold access): 2,600 gas
- `POP`: 2 gas
- `EXTCODECOPY` (warm, 1 byte): 100 gas (base) + 3 gas (copy 1 byte)
- `POP`: 2 gas

Note: Reading just 1 byte (specifically the last byte at offset 24575) forces the client
to load the entire 24KB contract from disk while minimizing gas cost. This allows
targeting nearly as many contracts as the EXTCODESIZE pattern while forcing maximum I/O.

## Required Contracts Calculation Example:

### For BALANCE + EXTCODESIZE:
| Gas Limit | Contracts Needed | Calculation         |
| --------- | ---------------- | ------------------- |
| 5M        | 1,838            | 5,000,000 ÷ 2,707   |
| 50M       | 18,380           | 50,000,000 ÷ 2,707  |
| 150M      | 55,403           | 150,000,000 ÷ 2,707 |

### For BALANCE + EXTCODECOPY (Optimized):
| Gas Limit | Contracts Needed | Calculation         |
| --------- | ---------------- | ------------------- |
| 5M        | 1,845            | 5,000,000 ÷ 2,710   |
| 50M       | 18,450           | 50,000,000 ÷ 2,710  |
| 150M      | 55,350           | 150,000,000 ÷ 2,710 |

You can see the associated attack constants inside of the tests in `bloatnet/test_bloatnet.py`

## Quick Start: 150M Gas Attack

### 1. Deploy CREATE2 Factory (you can use an already deployed one if preferred and therefore, skip this step)

```bash
# One-time setup - deploy the CREATE2 factory
python3 tests/benchmark/bloatnet/deploy_create2_factory.py

# Output will show:
# Factory deployed at: 0x...  <-- Save this address
```

### 2. Deploy Contracts

The deployment script is interactive and will guide you through selecting the appropriate contract type for your benchmark.

#### Contract Types Available

1. **max_size_24kb**: 24KB contracts filled with unique bytecode (EXTCODE_ type of tests)
2. **sload_heavy**: Contracts optimized for SLOAD benchmarking
3. **storage_heavy**: Contracts with pre-initialized storage
4. **custom**: Custom bytecode (for future extensions)

#### Calculate Contracts Needed

Before running the deployment, calculate the number of contracts needed:
- For 150M gas BALANCE+EXTCODESIZE: 55,403 contracts
- For 150M gas BALANCE+EXTCODECOPY: 29,958 contracts

_Deploy enough contracts to cover the max gas you plan to use in your tests/benchmarks._

#### Running the Deployment

```bash
# Run the interactive deployment script
python3 tests/benchmark/bloatnet/deploy_bloatnet_simple.py \
    --num-contracts 55403 \
    --factory-address 0x... \  # Use factory address from step 1
    --max-code-size 24576      # Optional: specify max contract size (default: 24576)
```

#### Deployment Output

After successful deployment, the script will:

1. Display the configuration needed for tests:
```python
=== Configuration for max_size_24kb tests ===
CONTRACT_TYPE = "max_size_24kb"
FACTORY_ADDRESS = Address("0x...")
INIT_CODE_HASH = bytes.fromhex("...")
NUM_DEPLOYED_CONTRACTS = 55403
```

2. Save the configuration to a file:
```
Configuration saved to: bloatnet_config_max_size_24kb.txt
```

This file contains all the values needed to update your test configuration.

### 3. Update Test Configuration

Edit `tests/benchmark/bloatnet/test_bloatnet.py` and update:

```python
FACTORY_ADDRESS = Address("0x...")  # From deployment output
INIT_CODE_HASH = bytes.fromhex("...")  # From deployment output
NUM_DEPLOYED_CONTRACTS = 55403  # Actual deployed count
```

### 5. Run Benchmark Tests

```bash
# Run with specific gas values (in millions)
uv run fill --fork=Prague --gas-benchmark-values=150 \
    tests/benchmark/bloatnet/test_bloatnet.py --clean

# With EVM traces for analysis
uv run fill --fork=Prague --gas-benchmark-values=150 \
    --evm-dump-dir=traces/ --traces \
    tests/benchmark/bloatnet/test_bloatnet.py

# Multiple gas values
uv run fill --fork=Prague --gas-benchmark-values=5,50,150 \
    tests/benchmark/bloatnet/test_bloatnet.py
```
