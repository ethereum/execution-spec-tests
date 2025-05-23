# Moving `./tests/` to `execution-specs`

## Requirements

1. Test implementers can continue working on tests from Day 1.
   i. Familiar CI checks enabled in Github Actions.
   ii. TBD: Test implementers can continue using familiar tooling: `uv`, `ruff`, `tox`.
2. The execution-spec-tests git history of `./tests` is maintained in ethereum-specs.
3. Consistent pytest versions across repos.
4. Consistent minimum Python versions across repos.
5. The "[Test Case Reference](https://eest.ethereum.org/main/tests/)" documentation is published on ethereum-specs.

## Main Steps

### Phase I

For the initial move.

1. EEST: Make EEST an installable package, tracking issue: [ethereum/execution-spec-tests#1565](https://github.com/ethereum/execution-spec-tests/issues/1565).
2. EEST: Remove last dependencies on execution-specs to remove any circular dependencies:
    - Use of `FrontierAccount` and `FrontierAddress` for state root calculation in [ethereum_test_types](https://github.com/ethereum/execution-spec-tests/blob/d9f5eabebb35b4f6a44e10f9163aa27e31125c52/src/ethereum_test_types/types.py#L222-L245).
3. TBD, EELS: Update execution-specs to same Python tooling experience (`uv`, `ruff`, ...) as EEST?
4. New repo: Add shared Github Actions for building clients (e.g., evmone-t8n required for coverage flow).
5. EELS & EEST: Enable execution-spec-tests CI flows in execution-specs.
6. EELS: Add Github Pages at eels.ethereum.org.
7. EELS: Add mkdocs doc flow to publish a basic doc structure and the Test Case Reference.

### Phase II

Can be left as follow-up work.

1. TBD: EEST: Move some `src/ethereum_test*` libraries to EELS or a shared repo?
2. TBD: EEST: Publish pytest plugins individually in separate repos?

## Other Questions (than the TBDs above)

1. Do we need a new top-level `steel` Github organization? This could host components that don't belong in either repo, e.g.,
   - [marioevz/hive.py](https://github.com/marioevz/hive.py)
   - [petertdavies/ethereum-spec-evm-resolver](https://github.com/petertdavies/ethereum-spec-evm-resolver)
   - Other components, such as pytest plugins.
2. TBD: Should execution-specs adopt conventional commits similar to execution-spec-tests?
3. Low priority: EIP versioning: Should the implementation also define MD5 hash digests of the ethereum/EIPs markdown?

## `ethereum/execution-spec-tests` Component Analysis

### 1. GitHub Workflows and Actions

| Component Name          | Description                                                                         | Repository Path                           | Future Location                   |
| ----------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------- | --------------------------------- |
| check_eip_versions.yaml | Checks if EIP version references in test code are outdated, creates issues if found | .github/workflows/check_eip_versions.yaml | execution-specs                   |
| check_links.yml         | Validates links in documentation and source code using lychee                       | .github/workflows/check_links.yml         | EEST                              |
| coverage.yaml           | Generates evmone coverage reports for test changes in PRs                           | .github/workflows/coverage.yaml           | execution-specs                   |
| docs_deploy.yaml        | Deploys documentation to GitHub Pages using mkdocs                                  | .github/workflows/docs_deploy.yaml        | execution-specs                   |
| fixtures_feature.yaml   | Builds fixtures for specific features based on tags                                 | .github/workflows/fixtures_feature.yaml   | execution-specs                   |
| fixtures.yaml           | Builds fixtures for standard forks on version tags                                  | .github/workflows/fixtures.yaml           | execution-specs                   |
| tox_verify.yaml         | Main CI workflow for code quality checks (lint, type check, tests)                  | .github/workflows/tox_verify.yaml         | Split/Both; see `tox` table below |
| build-evm-base          | Base action for building EVM clients from configuration                             | .github/actions/build-evm-base/           | new repo                          |
| build-fixtures          | Builds and packages test fixtures for release                                       | .github/actions/build-fixtures/           | execution-specs                   |
| build-evm-client/evmone | Builds evmone EVM implementation                                                    | .github/actions/build-evm-client/evmone/  | new repo                          |
| build-evm-client/geth   | Builds Go-Ethereum EVM implementation                                               | .github/actions/build-evm-client/geth/    | new repo                          |
| build-evm-client/besu   | Builds Hyperledger Besu EVM implementation                                          | .github/actions/build-evm-client/besu/    | new repo                          |
| build-evm-client/ethjs  | Builds EthereumJS EVM implementation                                                | .github/actions/build-evm-client/ethjs/   | new repo                          |

### 2. Tox Environments

| Component Name       | Description                                                       | Repository Path | Future Location |
| -------------------- | ----------------------------------------------------------------- | --------------- | --------------- |
| lint                 | Runs ruff for code formatting and linting checks                  | tox.ini         | Both            |
| typecheck            | Runs mypy for type checking Python code                           | tox.ini         | Both            |
| markdownlint         | Lints markdown files for formatting issues                        | tox.ini         | Both            |
| spellcheck           | Checks spelling in documentation using pyspelling                 | tox.ini         | Both            |
| pytest               | Runs framework unit tests and library tests                       | tox.ini         | EEST            |
| tests-deployed       | Fills test cases for deployed mainnet forks (excludes slow/zkevm) | tox.ini         | execution-specs |
| tests-deployed-zkevm | Fills zkEVM test cases using evmone-t8n                           | tox.ini         | execution-specs |
| mkdocs               | Builds documentation in strict mode using mkdocs                  | tox.ini         | execution-specs |
| tests-develop        | Fills test cases for development forks                            | tox.ini         | execution-specs |

### 3. Command-Line Interfaces (CLIs)

| Component Name     | Description                                   | Repository Path                               | Future Location               |
| ------------------ | --------------------------------------------- | --------------------------------------------- | ----------------------------- |
| fill               | Fills test cases using pytest wrapper         | src/cli/pytest_commands/fill.py               | EEST                          |
| execute            | Executes test cases against clients           | src/cli/pytest_commands/execute.py            | EEST                          |
| consume            | Validates test fixtures against clients       | src/cli/pytest_commands/consume.py            | EEST                          |
| checkfixtures      | Checks test fixtures for validity             | src/cli/check_fixtures.py                     | delete                        |
| check_eip_versions | Verifies EIP references are up-to-date        | src/cli/pytest_commands/check_eip_versions.py | EEST                          |
| genindex           | Generates index for test fixtures             | src/cli/gen_index.py                          | EEST; used in execution-specs |
| gentest            | Generates test templates from specifications  | src/cli/gentest/                              | EEST; used in execution-specs |
| eofwrap            | Wraps bytecode in EOF format                  | src/cli/eofwrap.py                            | ?                             |
| order_fixtures     | Orders fixture files appropriately            | src/cli/order_fixtures.py                     | ?                             |
| evm_bytes          | Handles EVM bytecode operations               | src/cli/evm_bytes.py                          | EEST                          |
| hasher             | Creates hashes for test fixtures verification | src/cli/hasher.py                             | EEST                          |
| eest info          | Print repo info and tool versions             | src/cli/eest/                                 | both; add `eels` command?     |
| eest clean         | Remove temporary files/artifacts              | src/cli/eest/                                 | both                          |
| eest make          | Create a new test template                    | src/cli/eest/                                 | Move `make` to `es` command?  |
| fillerconvert      | Converts legacy test fillers to new format    | src/cli/fillerconvert/                        | ?                             |

### 4. Top-level Library Functions

| Component Name           | Description                                               | Repository Path               | Future Location |
| ------------------------ | --------------------------------------------------------- | ----------------------------- | --------------- |
| ethereum_test_base_types | Base types for Ethereum testing (addresses, hashes, etc.) | src/ethereum_test_base_types/ |                 |
| ethereum_test_exceptions | Exception mapping and handling for test scenarios         | src/ethereum_test_exceptions/ | ?               |
| ethereum_test_execution  | Execution context and transaction handling                | src/ethereum_test_execution/  |                 |
| ethereum_test_fixtures   | Test fixture formats and consumers                        | src/ethereum_test_fixtures/   |                 |
| ethereum_test_forks      | Fork definitions and capabilities                         | src/ethereum_test_forks/      |                 |
| ethereum_test_rpc        | RPC client interfaces for testing                         | src/ethereum_test_rpc/        |                 |
| ethereum_test_specs      | Test specification classes (state, blockchain)            | src/ethereum_test_specs/      |                 |
| ethereum_test_tools      | Utility functions for test creation                       | src/ethereum_test_tools/      |                 |
| ethereum_test_types      | Common types used across test scenarios                   | src/ethereum_test_types/      |                 |
| ethereum_test_vm         | Virtual machine operations and opcodes                    | src/ethereum_test_vm/         |                 |
| ethereum_clis            | Client interfaces for various Ethereum implementations    | src/ethereum_clis/            | EEST            |

### 5. Pytest Plugins

| Component Name       | Description                                             | Repository Path                          | Future Location |
| -------------------- | ------------------------------------------------------- | ---------------------------------------- | --------------- |
| consume              | Consumes and validates generated test fixtures          | src/pytest_plugins/consume/              | EEST            |
| execute              | Executes test cases against Ethereum clients            | src/pytest_plugins/execute/              | EEST            |
| filler               | Fills test templates to generate fixtures               | src/pytest_plugins/filler/               | EEST            |
| gen_test_docs        | Generates reference test case documentation             | src/pytest_plugins/filler/               | EEST            |
| forks                | Handles fork-specific test parametrization              | src/pytest_plugins/forks/                | EEST            |
| help                 | Provides help command integration for pytest            | src/pytest_plugins/help/                 | EEST            |
| logging              | Enhanced logging with custom levels and features        | src/pytest_plugins/logging/              | EEST            |
| spec_version_checker | Verifies EIP specification versions                     | src/pytest_plugins/spec_version_checker/ | EEST            |
| solc                 | Manages Solidity compiler integration                   | src/pytest_plugins/solc/                 | EEST            |
| pytest_hive          | Integration with Hive testing framework                 | src/pytest_plugins/pytest_hive/          | EEST            |
| concurrency          | Manages concurrent test execution                       | src/pytest_plugins/concurrency.py        | EEST            |
| eels_resolver        | Resolves EELS (Ethereum Execution Layer Specifications) | src/pytest_plugins/eels_resolver.py      | EEST            |
