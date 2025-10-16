# BloatNet Single-Opcode Benchmarks

This directory contains benchmarks for testing single EVM opcodes (SLOAD, SSTORE) under state-heavy conditions using pre-deployed contracts.

## Test Setup

### Prerequisites

1. Pre-deployed ERC20 contracts on the target network
2. A JSON file containing contract addresses (stubs)

### Address Stubs Format

Create a JSON file (`stubs.json`) mapping test-specific stub names to deployed contract addresses:

```json
{
  "test_sload_empty_erc20_balanceof_USDT": "0x1234567890123456789012345678901234567890",
  "test_sload_empty_erc20_balanceof_USDC": "0x2345678901234567890123456789012345678901",
  "test_sload_empty_erc20_balanceof_DAI": "0x3456789012345678901234567890123456789012",
  "test_sload_empty_erc20_balanceof_WETH": "0x4567890123456789012345678901234567890123",
  "test_sload_empty_erc20_balanceof_WBTC": "0x5678901234567890123456789012345678901234",

  "test_sstore_erc20_approve_USDT": "0x1234567890123456789012345678901234567890",
  "test_sstore_erc20_approve_USDC": "0x2345678901234567890123456789012345678901",
  "test_sstore_erc20_approve_DAI": "0x3456789012345678901234567890123456789012",
  "test_sstore_erc20_approve_WETH": "0x4567890123456789012345678901234567890123",
  "test_sstore_erc20_approve_WBTC": "0x5678901234567890123456789012345678901234""
}
```

**Naming Convention:**
- Stub names MUST start with the test function name
- Format: `{test_function_name}_{identifier}`
- Example: `test_sload_empty_erc20_balanceof_USDT`


### Running the Tests

#### Execute Mode (Against Live Network)

```bash
# Run with specific number of contracts (e.g., only the 5-contract variant)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run execute \
  --address-stubs /path/to/stubs.json \
  --fork=Prague \
  tests/benchmark/stateful/bloatnet/test_single_opcode.py::test_sload_empty_erc20_balanceof \
  -k "[5]" \
  -v

# Run all parametrized variants (1, 5, 10, 20 contracts)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run execute \
  --address-stubs /path/to/stubs.json \
  --fork=Prague \
  tests/benchmark/stateful/bloatnet/test_single_opcode.py \
  -v
```


## Test Parametrization

Both tests are parametrized with `num_contracts = [1, 5, 10, 20, 100]`, generating 5 test variants each:

- **1 contract**: Baseline single-contract performance
- **5 contracts**: Small-scale multi-contract scenario
- **10 contracts**: Medium-scale multi-contract scenario
- **20 contracts**: Large-scale multi-contract scenario
- **100 contracts**: Very large-scale multi-contract stress test

### How Stub Filtering Works

1. Test extracts its function name (e.g., `test_sload_empty_erc20_balanceof`)
2. Filters stubs starting with that name from `stubs.json`
3. Selects the **first N** matching stubs based on `num_contracts` parameter
4. Errors if insufficient matching stubs found

