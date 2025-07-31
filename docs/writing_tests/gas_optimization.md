# Gas Optimization

The `--optimize-gas` feature helps find the minimum gas limit required for transactions to execute correctly while maintaining the same execution trace and post-state. This is useful for creating more efficient test cases and understanding the exact gas requirements of specific operations.

## Basic Usage

Enable gas optimization for all tests:

```bash
uv run fill --optimize-gas
```

## Output Configuration

Specify a custom output file for gas optimization results:

```bash
uv run fill --optimize-gas --optimize-gas-output=my_gas_results.json path/to/some/test/to/optimize
```

## Post-Processing Mode

Enable post-processing to handle opcodes that put the current gas in the stack (like `GAS` opcode):

```bash
uv run fill --optimize-gas --optimize-gas-post-processing
```

## How It Works

The gas optimization algorithm uses a binary search approach:

1. **Initial Validation**: First tries reducing the gas limit by 1 to verify when even minimal changes affect the execution trace
2. **Binary Search**: Uses binary search between 0 and the original gas limit to find the minimum viable gas limit
3. **Verification**: For each candidate gas limit, it verifies:
   - Execution traces are equivalent (with optional post-processing)
   - Post-state allocation matches the expected result
   - Transaction validation passes
   - Account states remain consistent
4. **Result**: Outputs the minimum gas limit that still produces correct execution

## Output Format

The optimization results are saved to a JSON file (default: `optimize-gas-output.json`) containing:

- Test identifiers as keys of the JSON object
- Optimized gas limits in each value or `null` if the optimization failed.

## Use Cases

- **Test Efficiency**: Create tests with minimal gas requirements
- **Gas Analysis**: Understand exact gas costs for specific operations
- **Regression Testing**: Ensure gas optimizations don't break test correctness
- **Performance Testing**: Benchmark gas usage across different scenarios

## Limitations

- Only works with state tests (not blockchain tests)
- Requires trace collection to be enabled
- May significantly increase test execution time due to multiple trial runs
- Some tests may not be optimizable if they require the exact original gas limit

## Integration with Test Writing

When writing tests, you can use gas optimization to:

1. **Optimize Existing Tests**: Run `--optimize-gas` on your test suite to find more efficient gas limits
2. **Validate Gas Requirements**: Ensure your tests use the minimum necessary gas
3. **Create Efficient Test Cases**: Use the optimized gas limits in your test specifications
4. **Benchmark Changes**: Compare gas usage before and after modifications

## Example Workflow

```bash
# 1. Write your test
# 2. Run with gas optimization
uv run fill --optimize-gas --optimize-gas-output=optimization_results.json

# 3. Review the results
cat optimization_results.json

# 4. Update your test with optimized gas limits if desired
# 5. Re-run to verify correctness
uv run fill
```

## Best Practices

### Leave a Buffer for Future Forks

When using the optimized gas limits in your tests, it's recommended to add a small buffer (typically 5-10%) above the exact value outputted by the gas optimization. This accounts for potential gas cost changes in future Ethereum forks that might increase the gas requirements for the same operations.

For example, if the optimization outputs a gas limit of 100,000, consider using 105,000 or 110,000 in your test specification to ensure compatibility with future protocol changes.
