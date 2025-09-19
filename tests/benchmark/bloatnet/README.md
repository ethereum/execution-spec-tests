# BloatNet Benchmark Tests setup guide

## Overview

This README pretends to be a guide for any user that wants to run the bloatnet test/benchmark suite in any network.
BloatNet bench cases can be seen in: https://hackmd.io/9icZeLN7R0Sk5mIjKlZAHQ.
The idea of all these tests is to stress client implementations to find out where the limits of processing are focusing specifically on state-related operations.

In this document you will find a guide that will help you deploy all the setup contracts required by the benchmarks in `/benchmarks/bloatnet`.

## Gas Cost Constants

### BALANCE + EXTCODESIZE Pattern
**Gas per contract: ~2,772**
- `SHA3` (CREATE2 address generation): 30 gas (static) + 18 gas (dynamic for 85 bytes)
- `BALANCE` (cold access): 2,600 gas
- `POP`: 2 gas
- `EXTCODESIZE` (warm): 100 gas
- `POP`: 2 gas
- Memory operations and loop overhead: ~20 gas

### BALANCE + EXTCODECOPY(single-byte) Pattern
**Gas per contract: ~2,775**
- `SHA3` (CREATE2 address generation): 30 gas (static) + 18 gas (dynamic for 85 bytes)
- `BALANCE` (cold access): 2,600 gas
- `POP`: 2 gas
- `EXTCODECOPY` (warm, 1 byte): 100 gas (base) + 3 gas (copy 1 byte)
- Memory operations: 4 gas
- Loop overhead: ~20 gas

Note: Reading just 1 byte (specifically the last byte at offset 24575) forces the client
to load the entire 24KB contract from disk while minimizing gas cost. This allows
targeting nearly as many contracts as the EXTCODESIZE pattern while forcing maximum I/O.

## Required Contracts Calculation Example:

### For BALANCE + EXTCODESIZE:
| Gas Limit | Contracts Needed | Calculation         |
| --------- | ---------------- | ------------------- |
| 1M        | 352              | 1,000,000 ÷ 2,772   |
| 5M        | 1,769            | 5,000,000 ÷ 2,772   |
| 50M       | 17,690           | 50,000,000 ÷ 2,772  |
| 150M      | 53,071           | 150,000,000 ÷ 2,772 |

### For BALANCE + EXTCODECOPY:
| Gas Limit | Contracts Needed | Calculation         |
| --------- | ---------------- | ------------------- |
| 1M        | 352              | 1,000,000 ÷ 2,775   |
| 5M        | 1,768            | 5,000,000 ÷ 2,775   |
| 50M       | 17,684           | 50,000,000 ÷ 2,775  |
| 150M      | 53,053           | 150,000,000 ÷ 2,775 |

The CREATE2 address generation adds ~48 gas per contract but eliminates memory limitations in test framework.

## Quick Start: 150M Gas Attack

### 1. Deploy CREATE2 Factory with Initcode Template

```bash
# Deploy the factory and initcode template (one-time setup)
python3 tests/benchmark/bloatnet/deploy_create2_factory_refactored.py

# Output will show:
# Factory deployed at: 0x...  <-- Save this address
# Init code hash: 0x...  <-- Save this hash
```

### 2. Deploy Contracts

Deploy contracts using the factory. Each contract will be unique due to ADDRESS-based randomness in the initcode.

#### Calculate Contracts Needed

Before running the deployment, calculate the number of contracts needed:
- For 150M gas BALANCE+EXTCODESIZE: 53,071 contracts
- For 150M gas BALANCE+EXTCODECOPY: 53,053 contracts

_Deploy enough contracts to cover the max gas you plan to use in your tests/benchmarks._

#### Running the Deployment

```bash
# Deploy contracts for 150M gas attack
python3 tests/benchmark/bloatnet/deploy_create2_factory_refactored.py \
    --deploy-contracts 53100

# For smaller tests (e.g., 1M gas)
python3 tests/benchmark/bloatnet/deploy_create2_factory_refactored.py \
    --deploy-contracts 370
```

#### Deployment Output

After successful deployment, the script will display:

```
✅ Successfully deployed 53100 contracts
NUM_DEPLOYED_CONTRACTS = 53100
```

### 3. Update Test Configuration

Edit `tests/benchmark/bloatnet/test_bloatnet.py` and update with values from deployment:

```python
FACTORY_ADDRESS = Address("0x...")  # From step 1 output
INIT_CODE_HASH = bytes.fromhex("...")  # From step 1 output
NUM_DEPLOYED_CONTRACTS = 53100  # From step 2 output
```

### 4. Run Benchmark Tests

#### Generate Test Fixtures
```bash
# Run with specific gas values (in millions)
uv run fill --fork=Prague --gas-benchmark-values=150 \
    tests/benchmark/bloatnet/test_bloatnet.py --clean

# Multiple gas values
uv run fill --fork=Prague --gas-benchmark-values=1,5,50,150 \
    tests/benchmark/bloatnet/test_bloatnet.py
```

#### Execute Against Live Client
```bash
# Start a test node (e.g., Geth)
geth --dev --http --http.api eth,web3,net,debug

# Run tests
uv run execute remote --rpc-endpoint http://127.0.0.1:8545 \
    --rpc-chain-id 1337 --rpc-seed-key 0x0000000000000000000000000000000000000000000000000000000000000001 \
    tests/benchmark/bloatnet/test_bloatnet.py \
    --fork=Prague --gas-benchmark-values=150 -v
```

#### With EVM Traces for Analysis
```bash
uv run fill --fork=Prague --gas-benchmark-values=150 \
    --evm-dump-dir=traces/ --traces \
    tests/benchmark/bloatnet/test_bloatnet.py

# Analyze opcodes executed
jq -r '.opName' traces/**/*.jsonl | sort | uniq -c
```
