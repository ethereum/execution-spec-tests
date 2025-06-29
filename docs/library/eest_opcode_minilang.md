# EEST Opcode Minilang

This page helps test contributors get started with the EEST opcode minilang for writing smart contracts in execution-spec-tests.

## Writing Smart Contracts Using the Opcodes Minilang

The EEST project provides a Python-based minilang for constructing EVM bytecode using symbolic opcodes. This is implemented in [`Opcodes`](../../src/ethereum_test_vm/opcode.py), which contains all known EVM opcodes as Python enum members. Each opcode can be used as a callable to generate bytecode for tests.

### Example: Simple Addition Contract

```python
from ethereum_test_vm.opcode import Opcodes

# This contract adds two numbers and stores the result in storage slot 0
code = (
    Opcodes.PUSH1(0x02)  # Push 2
    + Opcodes.PUSH1(0x03)  # Push 3
    + Opcodes.ADD()        # Add
    + Opcodes.PUSH1(0x00)  # Storage slot 0
    + Opcodes.SSTORE()     # Store result
    + Opcodes.STOP()
)
```

You can assign this `code` to the `code` field of an account in your test's `pre` or `post` state.

For a full list of available opcodes and their usage, see [`src/ethereum_test_vm/opcode.py`](../../src/ethereum_test_vm/opcode.py).

## Higher-Level Constructs

To help with more complex control flow, EEST provides higher-level constructs in [`Switch`](../../src/ethereum_test_tools/code/generators.py) and related helpers.

### Example: Switch-Case

```python
from ethereum_test_tools.code.generators import Switch, Case
from ethereum_test_vm.opcode import Opcodes as Op

# Example: Switch on calldata value
code = Switch(
    cases=[
        Case(condition=Op.EQ(Op.CALLDATALOAD(0), 1), action=Op.PUSH1(0x01) + Op.STOP()),
        Case(condition=Op.EQ(Op.CALLDATALOAD(0), 2), action=Op.PUSH1(0x02) + Op.STOP()),
    ],
    default_action=Op.PUSH1(0x00) + Op.STOP(),
)
```

See [`src/ethereum_test_tools/code/generators.py`](../../src/ethereum_test_tools/code/generators.py) for more details and additional constructs like `While` and `Conditional`.

## Converting Bytecode to Minilang

If you have EVM bytecode (as hex or binary), you can use the [`evm_bytes` CLI tool](./cli/evm_bytes.md) to convert it to the EEST Python opcode minilang automatically:

- [evm_bytes CLI documentation](./cli/evm_bytes.md)
- [Online reference](https://eest.ethereum.org/main/library/cli/evm_bytes/)

## Restrictions: No Yul in Python Test Cases

**Note:** As of [PR #1779](https://github.com/ethereum/execution-spec-tests/pull/1779), the use of Yul source in Python test cases is forbidden. All new tests must use the Python opcode minilang as shown above.

For more on writing code for accounts in tests, see [Writing a New Test: Writing code for the accounts in the test](../writing_tests/writing_a_new_test.md#writing-code-for-the-accounts-in-the-test).

## See Also
- [Opcodes enum source](../../src/ethereum_test_vm/opcode.py)
- [Switch and higher-level constructs](../../src/ethereum_test_tools/code/generators.py)
- [evm_bytes CLI](./cli/evm_bytes.md)
- [Writing code for the accounts in the test](../writing_tests/writing_a_new_test.md#writing-code-for-the-accounts-in-the-test)
- [No Yul in Python tests (PR #1779)](https://github.com/ethereum/execution-spec-tests/pull/1779) 
