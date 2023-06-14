# Executing Tests at a Prompt

## Collection - Test Exploration

The test cases implemented in the `./tests` sub-directory can be listed in the console using:
```console
fill --collect-only
```
and can be filtered (by test path, function and parameter substring):
```console
fill --collect-only -k warm_coinbase
```
Docstrings are additionally displayed when ran verbosely:
```console
fill --collect-only -k warm_coinbase -vv
```

## Execution

To generate all the test fixtures defined in the `./tests` sub-directory and write them to the `./fixtures` directory, run `fill` in the top-level directory as:
```console
fill --output="fixtures"
```

!!! note "Test case verification"
    Note, that the test `post` conditions are tested against the output of the `evm t8n` command for transition tests, respectively `evm b11r` command for blockchain tests, during test generation.

To generate all the test fixtures in the `./tests/eips/` sub-directory (category), for example, run:
```console
fill tests/eips
```

To generate all the test fixtures in the `./tests/eips/test_eip3651.py` module, for example, run:
```console
fill ./tests/eips/test_eip3651.py
```

To generate specific test fixtures, such as those from the test function `test_warm_coinbase_call_out_of_gas()`, for example, run:
```console
fill -k "test_warm_coinbase_call_out_of_gas"
```
or, additionally, only for the for Shanghai fork:
```console
fill -k "test_warm_coinbase_call_out_of_gas and shanghai"
```

## Execution for Development Forks

!!! note ""
    By default, test cases are not executed with upcoming Ethereum forks so that they can be readily executed against the `evm` tool from the latest `geth` release.

    In order to execute test cases for an upcoming fork, ensure that the `evm` tool used supports that fork and features under test and use the `--until` or `--fork` flag.
    
    For example, as of May 2023, the current fork under active development is `Cancun`:
    ```console
    fill --until Cancun
    ```

    See: [Executing Tests for Features under Development](./executing_tests_dev_fork.md).

## Useful pytest/fill Command-Line Options

Custom `fill` command-line options:
```console
fill --traces       # Collect traces of the execution information from the transition tool
fill --evm=EVM_BIN  # Specify the evm executable to generate fixtures with
```

Pytest command-line options:
```console
fill -vv            # More verbose output
fill -x             # Exit instantly on first error or failed test case
fill --pdb          # drop into the debugger upon error in a test case
```

