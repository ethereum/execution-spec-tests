# Filling Tests at a Prompt

The execution-spec-tests test framework uses the [pytest framework](https://docs.pytest.org/en/latest/) for test case collection and execution. The `fill` command is essentially an alias for `pytest`, which uses several [custom pytest plugins](../library/pytest_plugins/index.md) to run transition tools against test cases and generate JSON fixtures.

!!! note "Options specific to execution-spec-tests"
    The command-line options specific to filling tests can be listed via:

    ```console
    fill --help
    ```

    See [Custom `fill` Command-Line Options](#custom-fill-command-line-options) for all options.

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

By default, test cases are filled for all forks already deployed to mainnet, but not for forks still under active development, i.e., as of time of writing, Q2 2023:

```console
fill
```

will generate fixtures for test cases from Frontier to Shanghai.

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
fill tests/shanghai/eip3651_warm_coinbase/test_warm_coinbase.py::test_warm_coinbase_gas_usage[fork_Paris-DELEGATECALL]
```

## Execution for Development Forks

!!! note ""
    By default, test cases are not filled for upcoming Ethereum forks so that they can be readily filled using the `evm` tool from the latest `geth` release.

    In order to fill test cases for an upcoming fork, ensure that the `evm` tool used supports that fork and features under test and use the `--until` or `--fork` flag.
    
    For example, as of Q2 2023, the current fork under active development is `Cancun`:
    ```console
    fill --until Cancun
    ```

    See: [Filling Tests for Features under Development](./filling_tests_dev_fork.md).

## Debugging the `t8n` Command

The `--evm-dump-dir` flag can be used to dump the inputs and outputs of every call made to the `t8n` command for debugging purposes, see [Debugging Transition Tools](./debugging_t8n_tools.md).

## Other Useful Pytest Command-Line Options

```console
fill -vv            # More verbose output
fill -x             # Exit instantly on first error or failed test case
fill --pdb -nauto   # Drop into the debugger upon error in a test case
fill -s             # Print stdout from tests to the console during execution
```

## Custom `fill` Command-Line Options

To see all the options available to fill, including pytest and pytest plugin options, use `--pytest-help`.

To list the options that only specific to fill, use:

```console
fill --help
```

Output:

```text
usage: fill [-h] [--strict-alloc] [--ca-start CA_START] [--ca-incr CA_INCR]
            [--evm-code-type EVM_CODE_TYPE] [--solc-bin SOLC_BIN]
            [--solc-version SOLC_VERSION] [--evm-bin EVM_BIN] [--traces]
            [--verify-fixtures] [--verify-fixtures-bin VERIFY_FIXTURES_BIN]
            [--filler-path FILLER_PATH] [--output OUTPUT] [--flat-output]
            [--single-fixture-per-file] [--no-html] [--strict-alloc]
            [--ca-start CA_START] [--ca-incr CA_INCR] [--build-name BUILD_NAME]
            [--evm-dump-dir EVM_DUMP_DIR] [--forks] [--fork FORK] [--from FROM]
            [--until UNTIL]

options:
  -h, --help            show this help message and exit

Arguments defining pre-allocation behavior.:
  --strict-alloc        [DEBUG ONLY] Disallows deploying a contract in a
                        predefined address.
  --ca-start CA_START, --contract-address-start CA_START
                        The starting address from which tests will deploy
                        contracts.
  --ca-incr CA_INCR, --contract-address-increment CA_INCR
                        The address increment value to each deployed contract by
                        a test.
  --evm-code-type EVM_CODE_TYPE
                        Type of EVM code to deploy in each test by default.

Arguments defining the solc executable:
  --solc-bin SOLC_BIN   Path to a solc executable (for Yul source compilation).
                        No default; if unspecified `--solc-version` is used.
  --solc-version SOLC_VERSION
                        Version of the solc compiler to use. Default: 0.8.24.

Arguments defining evm executable behavior:
  --evm-bin EVM_BIN     Path to an evm executable that provides `t8n`. Default:
                        First 'evm' entry in PATH.
  --traces              Collect traces of the execution information from the
                        transition tool.
  --verify-fixtures     Verify generated fixture JSON files using geth's evm
                        blocktest command. By default, the same evm binary as for
                        the t8n tool is used. A different (geth) evm binary may
                        be specified via --verify-fixtures-bin, this must be
                        specified if filling with a non-geth t8n tool that does
                        not support blocktest.
  --verify-fixtures-bin VERIFY_FIXTURES_BIN
                        Path to an evm executable that provides the `blocktest`
                        command. Default: The first (geth) 'evm' entry in PATH.

Arguments defining filler location and output:
  --filler-path FILLER_PATH
                        Path to filler directives
  --output OUTPUT       Directory path to store the generated test fixtures. If
                        the specified path ends in '.tar.gz', then the specified
                        tarball is additionally created (the fixtures are still
                        written to the specified path without the '.tar.gz'
                        suffix). Can be deleted. Default: './fixtures'.
  --flat-output         Output each test case in the directory without the folder
                        structure.
  --single-fixture-per-file
                        Don't group fixtures in JSON files by test function;
                        write each fixture to its own file. This can be used to
                        increase the granularity of --verify-fixtures.
  --no-html             Don't generate an HTML test report (in the output
                        directory). The --html flag can be used to specify a
                        different path.
  --build-name BUILD_NAME
                        Specify a build name for the fixtures.ini file, e.g.,
                        'stable'.
  --index               Generate an index file for all produced fixtures.

Arguments defining debug behavior:
  --evm-dump-dir EVM_DUMP_DIR, --t8n-dump-dir EVM_DUMP_DIR
                        Path to dump the transition tool debug output.  (Default: <repo>/logs/evm)

Specify the fork range to generate fixtures for:
  --forks               Display forks supported by the test framework and exit.
  --fork FORK           Only fill tests for the specified fork.
  --from FROM           Fill tests from and including the specified fork.
  --until UNTIL         Fill tests until and including the specified fork.

Exit: After displaying help.
```
