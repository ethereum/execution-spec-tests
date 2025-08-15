# Test Fixtures for filter_fixtures CLI

This directory contains a minimal test fixture set for sanity checking the `filter_fixtures` CLI command.

## Purpose

These fixtures provide thorough coverage for edge cases while maintaining fast test execution. They are used by:

- Unit tests: `src/cli/tests/test_filter_fixtures.py`
- Integration tests: `src/cli/tests/test_filter_fixtures_consume.py`

## Coverage

### Fixture Formats (All 4)

- ✅ `state_test` - 10 test cases
- ✅ `blockchain_test` - 14 test cases  
- ✅ `blockchain_test_engine` - 9 test cases
- ✅ `blockchain_test_engine_x` - 9 test cases (includes pre_alloc files)

### Forks (Byzantium to Osaka)

- ✅ **Regular forks**: Byzantium, ConstantinopleFix, Istanbul, Berlin, London, Paris, Shanghai, Cancun, Prague, Osaka
- ✅ **Transition forks**: ParisToShanghaiAtTime15k, ShanghaiToCancunAtTime15k, CancunToPragueAtTime15k, PragueToOsakaAtTime15k

## Statistics

- **42 total test cases** - Minimal but thorough coverage
- **14 forks covered** - All essential forks plus all transition forks
- **Pre_alloc files included** - Required for engine_x format testing

## Regeneration Command

To regenerate these fixtures in the future:

```bash
uv run fill tests/frontier/identity_precompile/test_identity_returndatasize.py \
         tests/berlin/eip2929_gas_cost_increases/test_precompile_warming.py \
         -k "(0x0000000000000000000000000000000000000001-precompile_in_successor_True-precompile_in_predecessor_True) or (test_identity_precompile_returndata and output_size_greater_than_input)" \
         --output=fixtures-test --clean -n auto --until Osaka
```
