# BloatNet Benchmark Tests setup guide

## Overview

The Bloatnet benchmarks work on the following fashion:
1. They usually require a previously-deployed state (usually quite large) which the benchmarks
will interact with.
2. The deployment script helpers help deploying the required bytecode for the specific tests.
3. The outpus of the deployment scripts get hardcoded into the codebase such that the benchmarks can interact with them.

## Gas Cost Constants

### BALANCE + EXTCODESIZE Pattern
**Gas per contract: 2,707**
- `PUSH20` (address): 3 gas
- `BALANCE` (cold access): 2,600 gas
- `POP`: 2 gas
- `EXTCODESIZE` (warm): 100 gas
- `POP`: 2 gas

### BALANCE + EXTCODECOPY Pattern
**Gas per contract: ~5,007**
- `PUSH20` (address): 3 gas
- `BALANCE` (cold access): 2,600 gas
- `POP`: 2 gas
- `EXTCODECOPY` setup: ~100 gas
- `EXTCODECOPY` (24KB): ~2,300 gas
- `POP`: 2 gas

## Required Contracts Calculation Example:

### For BALANCE + EXTCODESIZE:
| Gas Limit | Contracts Needed | Calculation         |
| --------- | ---------------- | ------------------- |
| 5M        | 1,838            | 5,000,000 ÷ 2,707   |
| 50M       | 18,380           | 50,000,000 ÷ 2,707  |
| 150M      | 55,403           | 150,000,000 ÷ 2,707 |

### For BALANCE + EXTCODECOPY:
| Gas Limit | Contracts Needed | Calculation         |
| --------- | ---------------- | ------------------- |
| 5M        | 998              | 5,000,000 ÷ 5,007   |
| 50M       | 9,986            | 50,000,000 ÷ 5,007  |
| 150M      | 29,958           | 150,000,000 ÷ 5,007 |

You can see the associated attack constants inside of the tests in `bloatnet/test_bloatnet.py`

## Quick Start: 150M Gas Attack

### 1. Deploy CREATE2 Factory (you can use an already deployed one if preferred)

```bash
# One-time setup - deploy the CREATE2 factory
python3 tests/benchmark/bloatnet/deploy_create2_factory.py

# Output will show:
# Factory deployed at: 0x...  <-- Save this address
```

### 2. Deploy Contracts

Calculate the number of contracts needed for your test:
- For 150M gas BALANCE+EXTCODESIZE: 55,403 contracts
- For 150M gas BALANCE+EXTCODECOPY: 29,958 contracts

_The suggestion is to deploy enough contracts to cover for the max_gas you plan to use in your tests/benchmarks_

```bash
# Deploy contracts for 150M gas EXTCODESIZE test
python3 tests/benchmark/bloatnet/deploy_bloatnet_simple.py \
    --num-contracts 55403 \
    --factory-address 0x... # Use factory address from step 2

# Note the output:
# FACTORY_ADDRESS = Address("0x...")
# INIT_CODE_HASH = bytes.fromhex("...")
# NUM_CONTRACTS = 55403
```

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
