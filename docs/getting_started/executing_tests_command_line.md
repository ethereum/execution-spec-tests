# Executing Tests at a Prompt

The execution-spec-tests repo uses [pytest](https://docs.pytest.org/en/latest/) as its test framework. The `fill` command is essentially an alias for `pytest`.

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

By default, all test cases are executed for all forks deployed to mainnet, but not for forks still under active development, i.e.,

```console
fill
```

will generate fixtures for test cases from Frontier to Shanghai (as of time of writing, Q2 2023).

To generate all the test fixtures defined in the `./tests/shanghai` sub-directory and write them to the `./fixtures-shanghai` directory, run `fill` in the top-level directory as:

```console
fill ./tests/shanghai --output="fixtures-shanghai"
```

!!! note "Test case verification"
    Note, that the (limited set of) test `post` conditions are tested against the output of the `evm t8n` command during test generation.

To generate all the test fixtures in the `tests/shanghai/eip3651_warm_coinbase/test_warm_coinbase.py` module, for example, run:

```console
fill tests/shanghai/eip3651_warm_coinbase/test_warm_coinbase.py
```

To generate specific test fixtures from a specific test function or even test function and parameter set, obtain the corresponding test ID using:

```console
fill --collect-only -q -k test_warm_coinbase
```

This filters the tests by `test_warm_coinbase`. Then find the relevant test ID in the console output and provide it to fill, for example, for a test function:

```console
fill tests/shanghai/eip3651_warm_coinbase/test_warm_coinbase.py::test_warm_coinbase_gas_usage
```

or, for a test function and specific parameter combination:

```console
fill tests/shanghai/eip3651_warm_coinbase/test_warm_coinbase.py::test_warm_coinbase_gas_usage[fork=Merge-DELEGATECALL]
```

## Execution for Development Forks

!!! note ""
    By default, test cases are not executed with upcoming Ethereum forks so that they can be readily executed against the `evm` tool from the latest `geth` release.

    In order to execute test cases for an upcoming fork, ensure that the `evm` tool used supports that fork and features under test and use the `--until` or `--fork` flag.
    
    For example, as of Q2 2023, the current fork under active development is `Cancun`:
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
