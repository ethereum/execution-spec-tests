# Quick Start

## Prerequisites

The tools provided by [execution-spec-tests](https://github.com/ethereum/execution-spec-tests) use `uv` ([docs.astral.sh/uv](https://docs.astral.sh/uv/)) to manage their dependencies and virtual environment.

`uv` can be installed via curl (recommended; can self-update) or pip (requires Python, can't self-update):

=== "curl"

    ```console
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "pip"

    ```console
    pip install uv
    ```

If installed via `curl`, `uv` will download Python for your target platform if one of the required versions (Python 3.10, 3.11 or 3.12) is not available natively.

## Installation

Clone [execution-spec-tests](https://github.com/ethereum/execution-spec-tests) and install its dependencies:

```console
git clone https://github.com/ethereum/execution-spec-tests
cd execution-spec-tests
uv sync --all-extras
uv run solc-select use 0.8.24 --always-install
```

See [Installation Troubleshooting](./installation_troubleshooting.md) if you encounter issues.

## Exploring and Filling Test Cases

By default, JSON test fixtures are generated from this repository's Python test cases using the [Ethereum Execution Layer Specification](https://github.com/ethereum/execution-specs) (EELS) reference implementation. The resulting JSON fixtures can be executed against execution clients to verify consensus. The process of generating fixtures is often referred to as "filling".

1. Explore test cases via `--collect-only` and search for test cases that combine `PUSH0` and `DELEGATECALL` in the EVM functionality introduced in the Shanghai hard fork:

    ```console
    uv run fill --collect-only -k "push0 and delegatecall" tests/shanghai/
    ```

    The `fill` command is based on [`pytest`](https://docs.pytest.org/en/stable/). The above command uses the [optional pytest arguments](https://docs.pytest.org/en/stable/how-to/usage.html):

    - `--collect-only` only collect test cases; don't execute them.
    - `-k <expression>` filter test cases by their test case ID based on the given expression.
    - `tests/shanghai` the directory containing the test cases (tells `fill` to only discover test cases in this directory; default: `tests/`).

    Expected console output:
    <figure markdown>  <!-- markdownlint-disable MD033 (MD033=no-inline-html) -->
        ![Screenshot of pytest test collection console output](./img/pytest_collect_only.png){align=center}
    </figure>

2. Fill `state_test` fixtures for these test cases:

    ```console
    uv run fill -k "push0 and delegatecall" tests/shanghai/ -m state_test -v
    ```

    where:

    - `-m state_test` only fills test cases marked as a `state_test` (see all available markers via `uv run fill --markers`).
    - `-v` enables verbose output.

    Expected console output:
    <figure markdown>  <!-- markdownlint-disable MD033 (MD033=no-inline-html) -->
        ![Screenshot of fill test collection console output](./img/pytest_run_example.png){align=center}
    </figure>

3. Verify the generated fixtures:

    a. Check the corresponding fixture file has been generated:

    ```console
    head fixtures/state_tests/shanghai/eip3855_push0/push0/push0_contract_during_call_contexts.json
    ```

    b. Open the generated HTML test using the link provided at the bottom of the console output. This is written to the output directory at:

    ```console
    ./fixtures/.meta/report_fill.html
    ```

## Installation Troubleshooting

If you encounter issues during installation, see the [Installation Troubleshooting](./installation_troubleshooting.md) guide.

## Next Steps

1. Learn [useful command-line flags](./executing_tests_command_line.md).
2. [Execute tests for features under development](./executing_tests_dev_fork.md) via the `--fork` flag.
3. _Optional:_ [Configure VS Code](./setup_vs_code.md) to auto-format Python code and [execute tests within VS Code](./executing_tests_vs_code.md#executing-and-debugging-test-cases).
4. Implement a new test case, see [Writing Tests](../writing_tests/index.md).
