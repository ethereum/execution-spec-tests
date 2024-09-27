# Changelog

Test fixtures for use by clients are available for each release on the [Github releases page](https://github.com/ethereum/execution-spec-tests/releases).

**Key:** ✨ = New, 🐞 = Fixed, 🔀 = Changed, 💥 = Breaking change.

## 🔜 [Unreleased](https://github.com/ethereum/execution-spec-tests/releases/tag/UNRELEASED) - 2024-XX-XX

### 🧪 Test Cases

- ✨ EIP-4844 test `tests/cancun/eip4844_blobs/test_point_evaluation_precompile.py` includes an EOF test case ([#610](https://github.com/ethereum/execution-spec-tests/pull/610)).
- ✨ Example test `tests/frontier/opcodes/test_dup.py` now includes EOF parametrization ([#610](https://github.com/ethereum/execution-spec-tests/pull/610)).
- ✨ Convert all opcodes validation test `tests/frontier/opcodes/test_all_opcodes.py` ([#748](https://github.com/ethereum/execution-spec-tests/pull/748)).
- ✨ Update [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) tests for Devnet-3 ([#733](https://github.com/ethereum/execution-spec-tests/pull/733))
- 🐞 Fix [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)+EOF tests due to incorrect test expectations and faulty `Conditional` test generator in EOF mode ([#821](https://github.com/ethereum/execution-spec-tests/pull/821))

### 🛠️ Framework

- 🐞 Fixed consume hive commands from spawning different hive test suites during the same test execution when using xdist ([#712](https://github.com/ethereum/execution-spec-tests/pull/712)).
- ✨ `consume hive` command is now available to run all types of hive tests ([#712](https://github.com/ethereum/execution-spec-tests/pull/712)).
- ✨ Generated fixtures now contain the test index `index.json` by default ([#716](https://github.com/ethereum/execution-spec-tests/pull/716)).
- ✨ A metadata folder `.meta/` now stores all fixture metadata files by default ([#721](https://github.com/ethereum/execution-spec-tests/pull/721)).
- 🐞 Fixed `fill` command index generation issue due to concurrency ([#725](https://github.com/ethereum/execution-spec-tests/pull/725)).
- ✨ Added `with_all_evm_code_types`, `with_all_call_opcodes` and `with_all_create_opcodes` markers, which allow automatic parametrization of tests to EOF ([#610](https://github.com/ethereum/execution-spec-tests/pull/610), [#739](https://github.com/ethereum/execution-spec-tests/pull/739)).
- ✨ Added `with_all_system_contracts` marker, which helps parametrize tests with all contracts that affect the chain on a system level ([#739](https://github.com/ethereum/execution-spec-tests/pull/739)).
- ✨ Code generators `Conditional` and `Switch` now support EOF by adding parameter `evm_code_type` ([#610](https://github.com/ethereum/execution-spec-tests/pull/610)).
- ✨ `fill` command now supports parameter `--evm-code-type` that can be (currently) set to `legacy` or `eof_v1` to force all test smart contracts to deployed in normal or in EOF containers ([#610](https://github.com/ethereum/execution-spec-tests/pull/610)).
- 🐞 Fixed fixture index generation on EOF tests ([#728](https://github.com/ethereum/execution-spec-tests/pull/728)).
- 🐞 Fixes consume genesis mismatch exception for hive based simulators ([#734](https://github.com/ethereum/execution-spec-tests/pull/734)).
- ✨ Adds reproducible consume commands to hiveview ([#717](https://github.com/ethereum/execution-spec-tests/pull/717)).
- 💥 Added multiple exceptions to the EOF fixture format ([#759](https://github.com/ethereum/execution-spec-tests/pull/759)).
- ✨ Added optional parameter to all `with_all_*` markers to specify a lambda function that filters the parametrized values ([#739](https://github.com/ethereum/execution-spec-tests/pull/739)).
- ✨ Added [`extend_with_defaults` utility function](https://ethereum.github.io/execution-spec-tests/main/writing_tests/writing_a_new_test/#ethereum_test_tools.utility.pytest.extend_with_defaults), which helps extend test case parameter sets with default values. `@pytest.mark.parametrize` ([#739](https://github.com/ethereum/execution-spec-tests/pull/739)).
- ✨ Added `Container.Init` to `ethereum_test_types.EOF.V1` package, which allows generation of an EOF init container more easily ([#739](https://github.com/ethereum/execution-spec-tests/pull/739)).
- ✨ Introduce method valid_opcodes() to the fork class ([#748](https://github.com/ethereum/execution-spec-tests/pull/748)).
- 🐞 Fixed `consume` exit code return values, ensuring that pytest's return value is correctly propagated to the shell. This allows the shell to accurately reflect the test results (e.g., failures) based on the pytest exit code ([#765](https://github.com/ethereum/execution-spec-tests/pull/765)).
- ✨ Added a new flag `--solc-version` to the `fill` command, which allows the user to specify the version of the Solidity compiler to use when compiling Yul source code; this version will now be automatically downloaded by `fill` via [`solc-select`](https://github.com/crytic/solc-select) ([#772](https://github.com/ethereum/execution-spec-tests/pull/772)).
- 🐞 Fix usage of multiple `@pytest.mark.with_all*` markers which shared parameters, such as `with_all_call_opcodes` and `with_all_create_opcodes` which shared `evm_code_type`, and now only parametrize compatible values ([#762](https://github.com/ethereum/execution-spec-tests/pull/762)).
- ✨ Added `selector` and `marks` fields to all `@pytest.mark.with_all*` markers, which allows passing lambda functions to select or mark specific parametrized values (see [documentation](https://ethereum.github.io/execution-spec-tests/main/writing_tests/test_markers/#covariant-marker-keyword-arguments) for more information) ([#762](https://github.com/ethereum/execution-spec-tests/pull/762)).
- ✨ Improves consume input flags for develop and stable fixture releases, fixes `--help` flag for consume ([#745](https://github.com/ethereum/execution-spec-tests/pull/745)).
- 🐞 Fix erroneous fork message in pytest session header with development forks ([#806](https://github.com/ethereum/execution-spec-tests/pull/806)).
- 🐞 Fix `Conditional` code generator in EOF mode ([#821](https://github.com/ethereum/execution-spec-tests/pull/821))
- 🔀 `ethereum_test_rpc` library has been created with what was previously `ethereum_test_tools.rpc` ([#822](https://github.com/ethereum/execution-spec-tests/pull/822))
- ✨ Add `Wei` type to `ethereum_test_base_types` which allows parsing wei amounts from strings like "1 ether", "1000 wei", "10**2 gwei", etc ([#825](https://github.com/ethereum/execution-spec-tests/pull/825))

### 🔧 EVM Tools

- ✨ Fill test fixtures using EELS by default. EEST now uses the [`ethereum-specs-evm-resolver`](https://github.com/petertdavies/ethereum-spec-evm-resolver) with the EELS daemon ([#792](https://github.com/ethereum/execution-spec-tests/pull/792)).

### 📋 Misc

- ✨ Feature releases can now include multiple types of fixture tarball files from different releases that start with the same prefix ([#736](https://github.com/ethereum/execution-spec-tests/pull/736)).
- ✨ Releases for feature eip7692 now include both Cancun and Prague based tests in the same release, in files `fixtures_eip7692.tar.gz` and `fixtures_eip7692-prague.tar.gz` respectively ([#743](https://github.com/ethereum/execution-spec-tests/pull/743)).
✨ Re-write the test case reference doc flow as a pytest plugin and add pages for test functions with a table providing an overview of their parametrized test cases ([#801](https://github.com/ethereum/execution-spec-tests/pull/801)).
- 🔀 Simplify Python project configuration and consolidate it into `pyproject.toml` ([#764](https://github.com/ethereum/execution-spec-tests/pull/764)).
- 🔀 Created `pytest_plugins.concurrency` plugin to sync multiple `xdist` processes without using a command flag to specify the temporary working folder ([#824](https://github.com/ethereum/execution-spec-tests/pull/824))
- 🔀 Move pytest plugin `pytest_plugins.filler.solc` to `pytest_plugins.solc.solc` ([#823](https://github.com/ethereum/execution-spec-tests/pull/823)).

### 💥 Breaking Change

- The EOF fixture format contained in `eof_tests` may now contain multiple exceptions in the `"exception"` field in the form of a pipe (`|`) separated string ([#759](https://github.com/ethereum/execution-spec-tests/pull/759)).
- Remove redundant tests within stable and develop fixture releases, moving them to a separate legacy release ([#788](https://github.com/ethereum/execution-spec-tests/pull/788)).

## [v3.0.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0) - 2024-07-22

### 🧪 Test Cases

- ✨ Port create2 return data test ([#497](https://github.com/ethereum/execution-spec-tests/pull/497)).
- ✨ Add tests for eof container's section bytes position smart fuzzing ([#592](https://github.com/ethereum/execution-spec-tests/pull/592)).
- ✨ Add `test_create_selfdestruct_same_tx_increased_nonce` which tests self-destructing a contract with a nonce > 1 ([#478](https://github.com/ethereum/execution-spec-tests/pull/478)).
- ✨ Add `test_double_kill` and `test_recreate` which test resurrection of accounts killed with `SELFDESTRUCT` ([#488](https://github.com/ethereum/execution-spec-tests/pull/488)).
- ✨ Add eof example valid invalid tests from ori, fetch EOF Container implementation ([#535](https://github.com/ethereum/execution-spec-tests/pull/535)).
- ✨ Add tests for [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537) ([#499](https://github.com/ethereum/execution-spec-tests/pull/499)).
- ✨ [EIP-663](https://eips.ethereum.org/EIPS/eip-663): Add `test_dupn.py` and `test_swapn.py` ([#502](https://github.com/ethereum/execution-spec-tests/pull/502)).
- ✨ Add tests for [EIP-6110: Supply validator deposits on chain](https://eips.ethereum.org/EIPS/eip-6110) ([#530](https://github.com/ethereum/execution-spec-tests/pull/530)).
- ✨ Add tests for [EIP-7002: Execution layer triggerable withdrawals](https://eips.ethereum.org/EIPS/eip-7002) ([#530](https://github.com/ethereum/execution-spec-tests/pull/530)).
- ✨ Add tests for [EIP-7685: General purpose execution layer requests](https://eips.ethereum.org/EIPS/eip-7685) ([#530](https://github.com/ethereum/execution-spec-tests/pull/530)).
- ✨ Add tests for [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935) ([#564](https://github.com/ethereum/execution-spec-tests/pull/564), [#585](https://github.com/ethereum/execution-spec-tests/pull/585)).
- ✨ Add tests for [EIP-4200: EOF - Static relative jumps](https://eips.ethereum.org/EIPS/eip-4200) ([#581](https://github.com/ethereum/execution-spec-tests/pull/581), [#666](https://github.com/ethereum/execution-spec-tests/pull/666)).
- ✨ Add tests for [EIP-7069: EOF - Revamped CALL instructions](https://eips.ethereum.org/EIPS/eip-7069) ([#595](https://github.com/ethereum/execution-spec-tests/pull/595)).
- 🐞 Fix typos in self-destruct collision test from erroneous pytest parametrization ([#608](https://github.com/ethereum/execution-spec-tests/pull/608)).
- ✨ Add tests for [EIP-3540: EOF - EVM Object Format v1](https://eips.ethereum.org/EIPS/eip-3540) ([#634](https://github.com/ethereum/execution-spec-tests/pull/634), [#668](https://github.com/ethereum/execution-spec-tests/pull/668)).
- 🔀 Update EIP-7002 tests to match spec changes in [ethereum/execution-apis#549](https://github.com/ethereum/execution-apis/pull/549) ([#600](https://github.com/ethereum/execution-spec-tests/pull/600))
- ✨ Convert a few eip1153 tests from ethereum/tests repo into .py ([#440](https://github.com/ethereum/execution-spec-tests/pull/440)).
- ✨ Add tests for [EIP-7480: EOF - Data section access instructions](https://eips.ethereum.org/EIPS/eip-7480) ([#518](https://github.com/ethereum/execution-spec-tests/pull/518), [#664](https://github.com/ethereum/execution-spec-tests/pull/664)).
- ✨ Add tests for subcontainer kind validation from [EIP-7620: EOF Contract Creation](https://eips.ethereum.org/EIPS/eip-7620) for the cases with deeply nested containers and non-first code sections ([#676](https://github.com/ethereum/execution-spec-tests/pull/676)).
- ✨ Add tests for runtime stack overflow at CALLF instruction from [EIP-4750: EOF - Functions](https://eips.ethereum.org/EIPS/eip-4750) ([#678](https://github.com/ethereum/execution-spec-tests/pull/678)).
- ✨ Add tests for runtime stack overflow at JUMPF instruction from [EIP-6206: EOF - JUMPF and non-returning functions](https://eips.ethereum.org/EIPS/eip-6206) ([#690](https://github.com/ethereum/execution-spec-tests/pull/690)).
- ✨ Add tests for Devnet-1 version of [EIP-7702: Set EOA account code](https://eips.ethereum.org/EIPS/eip-7702) ([#621](https://github.com/ethereum/execution-spec-tests/pull/621))

### 🛠️ Framework

- 🐞 Fix incorrect `!=` operator for `FixedSizeBytes` ([#477](https://github.com/ethereum/execution-spec-tests/pull/477)).
- ✨ Add Macro enum that represents byte sequence of Op instructions ([#457](https://github.com/ethereum/execution-spec-tests/pull/457))
- ✨ Number of parameters used to call opcodes (to generate bytecode) is now checked ([#492](https://github.com/ethereum/execution-spec-tests/pull/492)).
- ✨ Libraries have been refactored to use `pydantic` for type checking in most test types ([#486](https://github.com/ethereum/execution-spec-tests/pull/486), [#501](https://github.com/ethereum/execution-spec-tests/pull/501), [#508](https://github.com/ethereum/execution-spec-tests/pull/508)).
- ✨ Opcodes are now subscriptable and it's used to define the data portion of the opcode: `Op.PUSH1(1) == Op.PUSH1[1]  == b"\x60\x01"` ([#513](https://github.com/ethereum/execution-spec-tests/pull/513))
- ✨ Added EOF fixture format ([#512](https://github.com/ethereum/execution-spec-tests/pull/512)).
- ✨ Verify filled EOF fixtures using `evmone-eofparse` during `fill` execution ([#519](https://github.com/ethereum/execution-spec-tests/pull/519)).
- ✨ Added `--traces` support when running with Hyperledger Besu ([#511](https://github.com/ethereum/execution-spec-tests/pull/511)).
- ✨ Use pytest's "short" traceback style (`--tb=short`) for failure summaries in the test report for more compact terminal output ([#542](https://github.com/ethereum/execution-spec-tests/pull/542)).
- ✨ The `fill` command now generates HTML test reports with links to the JSON fixtures and debug information ([#537](https://github.com/ethereum/execution-spec-tests/pull/537)).
- ✨ Add an Ethereum RPC client class for use with consume commands ([#556](https://github.com/ethereum/execution-spec-tests/pull/556)).
- ✨ Add a "slow" pytest marker, in order to be able to limit the filled tests until release ([#562](https://github.com/ethereum/execution-spec-tests/pull/562)).
- ✨ Add a CLI tool that generates blockchain tests as Python from a transaction hash ([#470](https://github.com/ethereum/execution-spec-tests/pull/470), [#576](https://github.com/ethereum/execution-spec-tests/pull/576)).
- ✨ Add more Transaction and Block exceptions from existing ethereum/tests repo ([#572](https://github.com/ethereum/execution-spec-tests/pull/572)).
- ✨ Add "description" and "url" fields containing test case documentation and a source code permalink to fixtures during `fill` and use them in `consume`-generated Hive test reports ([#579](https://github.com/ethereum/execution-spec-tests/pull/579)).
- ✨ Add git workflow evmone coverage script for any new lines mentioned in converted_ethereum_tests.txt ([#503](https://github.com/ethereum/execution-spec-tests/pull/503)).
- ✨ Add a new covariant marker `with_all_contract_creating_tx_types` that allows automatic parametrization of a test with all contract-creating transaction types at the current executing fork ([#602](https://github.com/ethereum/execution-spec-tests/pull/602)).
- ✨ Tests are now encouraged to declare a `pre: Alloc` parameter to get the pre-allocation object for the test, and use `pre.deploy_contract` and `pre.fund_eoa` to deploy contracts and fund accounts respectively, instead of declaring the `pre` as a dictionary or modifying its contents directly (see the [state test tutorial](https://ethereum.github.io/execution-spec-tests/main/tutorials/state_transition/) for an updated example) ([#584](https://github.com/ethereum/execution-spec-tests/pull/584)).
- ✨ Enable loading of [ethereum/tests/BlockchainTests](https://github.com/ethereum/tests/tree/develop/BlockchainTests) ([#596](https://github.com/ethereum/execution-spec-tests/pull/596)).
- 🔀 Refactor `gentest` to use `ethereum_test_tools.rpc.rpc` by adding to `get_transaction_by_hash`, `debug_trace_call` to `EthRPC` ([#568](https://github.com/ethereum/execution-spec-tests/pull/568)).
- ✨ Write a properties file to the output directory and enable direct generation of a fixture tarball from `fill` via `--output=fixtures.tgz`([#627](https://github.com/ethereum/execution-spec-tests/pull/627)).
- 🔀 `ethereum_test_tools` library has been split into multiple libraries ([#645](https://github.com/ethereum/execution-spec-tests/pull/645)).
- ✨ Add the consume engine simulator and refactor the consume simulator suite. ([#691](https://github.com/ethereum/execution-spec-tests/pull/691)).
- 🐞 Prevents forcing consume to use stdin as an input when running from hive. ([#701](https://github.com/ethereum/execution-spec-tests/pull/701)).

### 📋 Misc

- 🐞 Fix CI by using Golang 1.21 in Github Actions to build geth ([#484](https://github.com/ethereum/execution-spec-tests/pull/484)).
- 💥 "Merge" has been renamed to "Paris" in the "network" field of the Blockchain tests, and in the "post" field of the State tests ([#480](https://github.com/ethereum/execution-spec-tests/pull/480)).
- ✨ Port entry point scripts to use [click](https://click.palletsprojects.com) and add tests ([#483](https://github.com/ethereum/execution-spec-tests/pull/483)).
- 💥 As part of the pydantic conversion, the fixtures have the following (possibly breaking) changes ([#486](https://github.com/ethereum/execution-spec-tests/pull/486)):
  - State test field `transaction` now uses the proper zero-padded hex number format for fields `maxPriorityFeePerGas`, `maxFeePerGas`, and `maxFeePerBlobGas`
  - Fixtures' hashes (in the `_info` field) are now calculated by removing the "_info" field entirely instead of it being set to an empty dict.
- 🐞 Relax minor and patch dependency requirements to avoid conflicting package dependencies ([#510](https://github.com/ethereum/execution-spec-tests/pull/510)).
- 🔀 Update all CI actions to use their respective Node.js 20 versions, ahead of their Node.js 16 version deprecations ([#527](https://github.com/ethereum/execution-spec-tests/pull/527)).
- ✨ Releases now contain a `fixtures_eip7692.tar.gz` which contains all EOF fixtures ([#573](https://github.com/ethereum/execution-spec-tests/pull/573)).
- ✨ Use `solc-select` for tox when running locally and within CI ([#604](https://github.com/ethereum/execution-spec-tests/pull/604)).

### 💥 Breaking Change

- Cancun is now the latest deployed fork, and the development fork is now Prague ([#489](https://github.com/ethereum/execution-spec-tests/pull/489)).
- Stable fixtures artifact `fixtures.tar.gz` has been renamed to `fixtures_stable.tar.gz` ([#573](https://github.com/ethereum/execution-spec-tests/pull/573))
- The "Blockchain Test Hive" fixture format has been renamed to "Blockchain Test Engine" and updated to more closely resemble the `engine_newPayload` format in the `execution-apis` specification (https://github.com/ethereum/execution-apis/blob/main/src/engine/prague.md#request) and now contains a single `"params"` field instead of multiple fields for each parameter ([#687](https://github.com/ethereum/execution-spec-tests/pull/687)).
- Output folder for fixtures has been renamed from "blockchain_tests_hive" to "blockchain_tests_engine" ([#687](https://github.com/ethereum/execution-spec-tests/pull/687)).

## [v2.1.1](https://github.com/ethereum/execution-spec-tests/releases/tag/v2.1.1) - 2024-03-09

### 🧪 Test Cases

- 🐞 Dynamic create2 collision from different transactions same block ([#430](https://github.com/ethereum/execution-spec-tests/pull/430)).
- 🐞 Fix beacon root contract deployment tests so the account in the pre-alloc is not empty ([#425](https://github.com/ethereum/execution-spec-tests/pull/425)).
- 🔀 All beacon root contract tests are now contained in tests/cancun/eip4788_beacon_root/test_beacon_root_contract.py, and all state tests have been converted back to blockchain tests format ([#449](https://github.com/ethereum/execution-spec-tests/pull/449))

### 🛠️ Framework

- ✨ Adds two `consume` commands [#339](https://github.com/ethereum/execution-spec-tests/pull/339):

   1. `consume direct` - Execute a test fixture directly against a client using a `blocktest`-like command (currently only geth supported).
   2. `consume rlp` - Execute a test fixture in a hive simulator against a client that imports the test's genesis config and blocks as RLP upon startup. This is a re-write of the [ethereum/consensus](https://github.com/ethereum/hive/tree/master/simulators/ethereum/consensus) Golang simulator.

- ✨ Add Prague to forks ([#419](https://github.com/ethereum/execution-spec-tests/pull/419)).
- ✨ Improve handling of the argument passed to `solc --evm-version` when compiling Yul code ([#418](https://github.com/ethereum/execution-spec-tests/pull/418)).
- 🐞 Fix `fill -m yul_test` which failed to filter tests that are (dynamically) marked as a yul test ([#418](https://github.com/ethereum/execution-spec-tests/pull/418)).
- 🔀 Helper methods `to_address`, `to_hash` and `to_hash_bytes` have been deprecated in favor of `Address` and `Hash`, which are automatically detected as opcode parameters and pushed to the stack in the resulting bytecode ([#422](https://github.com/ethereum/execution-spec-tests/pull/422)).
- ✨ `Opcodes` enum now contains docstrings with each opcode description, including parameters and return values, which show up in many development environments ([#424](https://github.com/ethereum/execution-spec-tests/pull/424)) @ThreeHrSleep.
- 🔀 Locally calculate state root for the genesis blocks in the blockchain tests instead of calling t8n ([#450](https://github.com/ethereum/execution-spec-tests/pull/450)).
- 🐞 Fix bug that causes an exception during test collection because the fork parameter contains `None` ([#452](https://github.com/ethereum/execution-spec-tests/pull/452)).
- ✨ The `_info` field in the test fixtures now contains a `hash` field, which is the hash of the test fixture, and a `hasher` script has been added which prints and performs calculations on top of the hashes of all fixtures (see `hasher -h`) ([#454](https://github.com/ethereum/execution-spec-tests/pull/454)).
- ✨ Adds an optional `verify_sync` field to hive blockchain tests (EngineAPI). When set to true a second client attempts to sync to the first client that executed the tests ([#431](https://github.com/ethereum/execution-spec-tests/pull/431)).
- 🐞 Fix manually setting the gas limit in the genesis test env for post genesis blocks in blockchain tests ([#472](https://github.com/ethereum/execution-spec-tests/pull/472)).

### 📋 Misc

- 🐞 Fix deprecation warnings due to outdated config in recommended VS Code project settings ([#420](https://github.com/ethereum/execution-spec-tests/pull/420)).
- 🐞 Fix typo in the selfdestruct revert tests module ([#421](https://github.com/ethereum/execution-spec-tests/pull/421)).

## [v2.1.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v2.1.0) - 2024-01-29: 🐍🏖️ Cancun

Release [v2.1.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v2.1.0) primarily fixes a small bug introduced within the previous release where transition forks are used within the new `StateTest` format. This was highlighted by @chfast within #405 (https://github.com/ethereum/execution-spec-tests/issues/405), where the fork name `ShanghaiToCancunAtTime15k` was found within state tests.

### 🧪 Test Cases

- ✨ [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Adds `test_blob_gas_subtraction_tx()` verifying the blob gas fee is subtracted from the sender before executing the blob tx ([#407](https://github.com/ethereum/execution-spec-tests/pull/407)).

### 🛠️ Framework

- 🐞 State tests generated with transition forks no longer use the transition fork name in the fixture output, instead they use the actual enabled fork according to the state test's block number and timestamp ([#406](https://github.com/ethereum/execution-spec-tests/pull/406)).

### 📋 Misc

- ✨ Use `run-parallel` and shared wheel packages for `tox` ([#408](https://github.com/ethereum/execution-spec-tests/pull/408)).

## [v2.0.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v2.0.0) - 2024-01-25: 🐍🏖️ Cancun

Release [v2.0.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v2.0.0) contains many important framework changes, including introduction of the `StateTest` format, and some additional Cancun and other test coverage.

Due to changes in the framework, there is a breaking change in the directory structure in the release tarball, please see the dedicated "💥 Breaking Changes" section below for more information.

### 🧪 Test Cases

- ✨ [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Add `test_sufficient_balance_blob_tx()` and `test_sufficient_balance_blob_tx_pre_fund_tx()` ([#379](https://github.com/ethereum/execution-spec-tests/pull/379)).
- ✨ [EIP-6780](https://eips.ethereum.org/EIPS/eip-6780): Add a reentrancy suicide revert test ([#372](https://github.com/ethereum/execution-spec-tests/pull/372)).
- ✨ [EIP-1153](https://eips.ethereum.org/EIPS/eip-1153): Add `test_run_until_out_of_gas()` for transient storage opcodes ([#401](https://github.com/ethereum/execution-spec-tests/pull/401)).
- ✨ [EIP-198](https://eips.ethereum.org/EIPS/eip-198): Add tests for the MODEXP precompile ([#364](https://github.com/ethereum/execution-spec-tests/pull/364)).
- ✨ Tests for nested `CALL` and `CALLCODE` gas consumption with a positive value transfer (previously lacking coverage) ([#371](https://github.com/ethereum/execution-spec-tests/pull/371)).
- 🐞 [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Fixed `test_invalid_tx_max_fee_per_blob_gas()` to account for extra gas required in the case where the account is incorrectly deduced the balance as if it had the correct block blob gas fee ([#370](https://github.com/ethereum/execution-spec-tests/pull/370)).
- 🐞 [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Fixed `test_insufficient_balance_blob_tx()` to correctly calculate the minimum balance required for the accounts ([#379](https://github.com/ethereum/execution-spec-tests/pull/379)).
- 🐞 [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Fix and enable `test_invalid_blob_tx_contract_creation` ([#379](https://github.com/ethereum/execution-spec-tests/pull/379)).
- 🔀 Convert all eligible `BlockchainTest`s to `StateTest`s (and additionally generate corresponding `BlockchainTest`s) ([#368](https://github.com/ethereum/execution-spec-tests/pull/368), [#370](https://github.com/ethereum/execution-spec-tests/pull/370)).

### 🛠️ Framework

- ✨ Add `StateTest` fixture format generation; `StateTests` now generate a `StateTest` and a corresponding `BlockchainTest` test fixture, previously only `BlockchainTest` fixtures were generated ([#368](https://github.com/ethereum/execution-spec-tests/pull/368)).
- ✨ Add `StateTestOnly` fixture format is now available and its only difference with `StateTest` is that it does not produce a `BlockchainTest` ([#368](https://github.com/ethereum/execution-spec-tests/pull/368)).
- ✨ Add `evm_bytes_to_python` command-line utility which converts EVM bytecode to Python Opcodes ([#357](https://github.com/ethereum/execution-spec-tests/pull/357)).
- ✨ Fork objects used to write tests can now be compared using the `>`, `>=`, `<`, `<=` operators, to check for a fork being newer than, newer than or equal, older than, older than or equal, respectively when compared against other fork ([#367](https://github.com/ethereum/execution-spec-tests/pull/367)).
- ✨ Add [solc 0.8.23](https://github.com/ethereum/solidity/releases/tag/v0.8.23) support ([#373](https://github.com/ethereum/execution-spec-tests/pull/373)).
- ✨ Add framework unit tests for post state exception verification ([#350](https://github.com/ethereum/execution-spec-tests/pull/350)).
- ✨ Add a helper class `ethereum_test_tools.TestParameterGroup` to define test parameters as dataclasses and auto-generate test IDs ([#364](https://github.com/ethereum/execution-spec-tests/pull/364)).
- ✨ Add a `--single-fixture-per-file` flag to generate one fixture JSON file per test case ([#331](https://github.com/ethereum/execution-spec-tests/pull/331)).
- 🐞 Storage type iterator is now fixed ([#369](https://github.com/ethereum/execution-spec-tests/pull/369)).
- 🐞 Fix type coercion in `FixtureHeader.join()` ([#398](https://github.com/ethereum/execution-spec-tests/pull/398)).
- 🔀 Locally calculate the transactions list's root instead of using the one returned by t8n when producing BlockchainTests ([#353](https://github.com/ethereum/execution-spec-tests/pull/353)).
- 🔀 Change custom exception classes to dataclasses to improve testability ([#386](https://github.com/ethereum/execution-spec-tests/pull/386)).
- 🔀 Update fork name from "Merge" to "Paris" used within the framework and tests ([#363](https://github.com/ethereum/execution-spec-tests/pull/363)).
- 💥 Replace `=` with `_` in pytest node ids and test fixture names ([#342](https://github.com/ethereum/execution-spec-tests/pull/342)).
- 💥 The `StateTest`, spec format used to write tests, is now limited to a single transaction per test ([#361](https://github.com/ethereum/execution-spec-tests/pull/361)).
- 💥 Tests must now use `BlockException` and `TransactionException` to define the expected exception of a given test, which can be used to test whether the client is hitting the proper exception when processing the block or transaction ([#384](https://github.com/ethereum/execution-spec-tests/pull/384)).
- 💥 `fill`: Remove the `--enable-hive` flag; now all test types are generated by default ([#358](https://github.com/ethereum/execution-spec-tests/pull/358)).
- 💥 Rename test fixtures names to match the corresponding pytest node ID as generated using `fill` ([#342](https://github.com/ethereum/execution-spec-tests/pull/342)).

### 📋 Misc

- ✨ Docs: Add a ["Consuming Tests"](https://ethereum.github.io/execution-spec-tests/main/consuming_tests/) section to the docs, where each test fixture format is described, along with the steps to consume them, and the description of the structures used in each format ([#375](https://github.com/ethereum/execution-spec-tests/pull/375)).
- 🔀 Docs: Update `t8n` tool branch to fill tests for development features in the [readme](https://github.com/ethereum/execution-spec-test) ([#338](https://github.com/ethereum/execution-spec-tests/pull/338)).
- 🔀 Filling tool: Updated the default filling tool (`t8n`) to go-ethereum@master ([#368](https://github.com/ethereum/execution-spec-tests/pull/368)).
- 🐞 Docs: Fix error banner in online docs due to mermaid syntax error ([#398](https://github.com/ethereum/execution-spec-tests/pull/398)).
- 🐞 Docs: Fix incorrectly formatted nested lists in online doc ([#403](https://github.com/ethereum/execution-spec-tests/pull/403)).

### 💥 Breaking Changes

A concrete example of the test name renaming and change in directory structure is provided below.

1. Fixture output, including release tarballs, now contain subdirectories for different test types:

   1. `blockchain_tests`: Contains `BlockchainTest` formatted tests
   2. `blockchain_tests_hive`: Contains `BlockchainTest` with Engine API call directives for use in hive
   3. `state_tests`: Contains `StateTest` formatted tests

2. `StateTest`, spec format used to write tests, is now limited to a single transaction per test.
3. In this release the pytest node ID is now used for fixture names (previously only the test parameters were used), this should not be breaking. However, `=` in both node IDs (and therefore fixture names) have been replaced with `_`, which may break tooling that depends on the `=` character.
4. Produced `blockchain_tests` fixtures and their corresponding `blockchain_tests_hive` fixtures now contain the named exceptions `BlockException` and `TransactionException` as strings in the `expectException` and `validationError` fields, respectively. These exceptions can be used to test whether the client is hitting the proper exception when processing an invalid block.

   Blockchain test:

   ```json
   "blocks": [
         {
            ...
            "expectException": "TransactionException.INSUFFICIENT_ACCOUNT_FUNDS",
            ...
         }
         ...
   ]
   ```

   Blockchain hive test:

   ```json
   "engineNewPayloads": [
         {
            ...
            "validationError": "TransactionException.INSUFFICIENT_ACCOUNT_FUNDS",
            ...
         }
         ...
   ]
   ```

#### Renaming and Release Tarball Directory Structure Change Example

The fixture renaming provides a more consistent naming scheme between the pytest node ID and fixture name and allows the fixture name to be provided directly to pytest 5on the command line to execute individual tests in isolation, e.g. `pytest tests/frontier/opcodes/test_dup.py::test_dup[fork_Frontier]`.

1. Pytest node ID example:

   1. Previous node ID: `tests/frontier/opcodes/test_dup.py::test_dup[fork=Frontier]`.
   2. New node ID: `tests/frontier/opcodes/test_dup.py::test_dup[fork_Frontier]`.

2. Fixture name example:

   1. Previous fixture name: `000-fork=Frontier`
   2. New fixture name: `tests/frontier/opcodes/test_dup.py::test_dup[fork_Frontier]` (now the same as the pytest node ID).

3. Fixture JSON file name example (within the release tarball):

   1. Previous fixture file name: `fixtures/frontier/opcodes/dup/dup.json` (`BlockChainTest` format).
   2. New fixture file names (all present within the release tarball):

     - `fixtures/state_tests/frontier/opcodes/dup/dup.json` (`StateTest` format).
     - `fixtures/blockchain_tests/frontier/opcodes/dup/dup.json` (`BlockChainTest` format).
     - `fixtures/blockchain_tests_hive/frontier/opcodes/dup/dup.json` (a blockchain test in `HiveFixture` format).

## [v1.0.6](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.6) - 2023-10-19: 🐍🏖️ Cancun Devnet 10

### 🧪 Test Cases

- 🔀 [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Update KZG point evaluation test vectors to use data from the official KZG setup and Mainnet Trusted Setup ([#336](https://github.com/ethereum/execution-spec-tests/pull/336)).

### 🛠️ Framework

- 🔀 Fixtures: Add a non-RLP format field (`rlp_decoded`) to invalid blocks ([#322](https://github.com/ethereum/execution-spec-tests/pull/322)).
- 🔀 Spec: Refactor state and blockchain spec ([#307](https://github.com/ethereum/execution-spec-tests/pull/307)).

### 🔧 EVM Tools

- ✨ Run geth's `evm blocktest` command to verify JSON fixtures after test case execution (`--verify-fixtures`) ([#325](https://github.com/ethereum/execution-spec-tests/pull/325)).
- ✨ Enable tracing support for `ethereum-spec-evm` ([#289](https://github.com/ethereum/execution-spec-tests/pull/289)).

### 📋 Misc

- ✨ Tooling: Add Python 3.12 support ([#309](https://github.com/ethereum/execution-spec-tests/pull/309)).
- ✨ Process: Added a Github pull request template ([#308](https://github.com/ethereum/execution-spec-tests/pull/308)).
- ✨ Docs: Changelog updated post release ([#321](https://github.com/ethereum/execution-spec-tests/pull/321)).
- ✨ Docs: Add [a section explaining execution-spec-tests release artifacts](https://ethereum.github.io/execution-spec-tests/main/getting_started/using_fixtures/) ([#334](https://github.com/ethereum/execution-spec-tests/pull/334)).
- 🔀 T8N Tool: Branch used to generate the tests for Cancun is now [lightclient/go-ethereum@devnet-10](https://github.com/lightclient/go-ethereum/tree/devnet-10) ([#336](https://github.com/ethereum/execution-spec-tests/pull/336))

### 💥 Breaking Change

- Fixtures now use the Mainnet Trusted Setup merged on [consensus-specs#3521](https://github.com/ethereum/consensus-specs/pull/3521) ([#336](https://github.com/ethereum/execution-spec-tests/pull/336))

## [v1.0.5](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.5) - 2023-09-26: 🐍🏖️ Cancun Devnet 9 Release 3

This release mainly serves to update the EIP-4788 beacon roots address to `0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02`, as updated in [ethereum/EIPs/pull/7672](https://github.com/ethereum/EIPs/pull/7672).

### 🧪 Test Cases

- 🐞 [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Fix invalid blob txs pre-Cancun engine response ([#306](https://github.com/ethereum/execution-spec-tests/pull/306)).
- ✨ [EIP-4788](https://eips.ethereum.org/EIPS/eip-4788): Final update to the beacon root address ([#312](https://github.com/ethereum/execution-spec-tests/pull/312)).

### 📋 Misc

- ✨ Docs: Changelog added ([#305](https://github.com/ethereum/execution-spec-tests/pull/305)).
- ✨ CI/CD: Run development fork tests in Github Actions ([#302](https://github.com/ethereum/execution-spec-tests/pull/302)).
- ✨ CI/CD: Generate test JSON fixtures on push ([#303](https://github.com/ethereum/execution-spec-tests/pull/303)).

### 💥 Breaking Change

Please use development fixtures from now on when testing Cancun. These refer to changes that are currently under development within clients:

- fixtures: All tests until the last stable fork (Shanghai)
- fixtures_develop: All tests until the last development fork (Cancun)
- fixtures_hive: All tests until the last stable fork (Shanghai) in hive format (Engine API directives instead of the usual BlockchainTest format)
- fixtures_develop_hive: All tests until the last development fork (Cancun) in hive format

## [v1.0.4](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.4) - 2023-09-21: 🐍 Cancun Devnet 9 Release 2

This release adds additional coverage to the current set of Cancun tests, up to the [Devnet-9 Cancun specification](https://notes.ethereum.org/@ethpandaops/dencun-devnet-9).

**Note:** Additional EIP-4788 updates from [ethereum/EIPs/pull/7672](https://github.com/ethereum/EIPs/pull/7672) will be included in the next release.

### 🧪 Test Cases

- ✨ [EIP-7516: BLOBBASEFEE opcode](https://eips.ethereum.org/EIPS/eip-7516): Add first and comprehensive tests (@marioevz in [#294](https://github.com/ethereum/execution-spec-tests/pull/294)).
- ✨ [EIP-4788: Beacon block root in the EVM](https://eips.ethereum.org/EIPS/eip-4788): Increase coverage (@spencer-tb in [#297](https://github.com/ethereum/execution-spec-tests/pull/297)).
- 🐞 [EIP-1153: Transient storage opcodes](https://eips.ethereum.org/EIPS/eip-1153): Remove conftest '+1153' in network field (@spencer-tb in [#299](https://github.com/ethereum/execution-spec-tests/pull/299)).

### 🛠️ Framework

- 🔀 [EIP-4788](https://eips.ethereum.org/EIPS/eip-4788): Beacon root contract is pre-deployed at `0xbEAC020008aFF7331c0A389CB2AAb67597567d7a` (@spencer-tb in [#297](https://github.com/ethereum/execution-spec-tests/pull/297)).
- ✨ Deprecate empty accounts within framework (@spencer-tb in [#300](https://github.com/ethereum/execution-spec-tests/pull/300)).
- ✨ Fixture generation split based on hive specificity (@spencer-tb in [#301](https://github.com/ethereum/execution-spec-tests/pull/301)).
- 💥 `fill`: `--disable-hive` flag removed; replaced by `--enable-hive` (@spencer-tb in [#301](https://github.com/ethereum/execution-spec-tests/pull/301)).
- ✨ Add engine API forkchoice updated information in fixtures (@spencer-tb in [#256](https://github.com/ethereum/execution-spec-tests/pull/256)).

## [v1.0.3](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.3) - 2023-09-14: 🐍 Cancun Devnet 9 Release

See [v1.0.3](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.3).

## [v1.0.2](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.2) - 2023-08-11: 🐍 Cancun Devnet 8 + 4788 v2 Pre-Release

See [v1.0.2](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.2).

## [v1.0.1](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.1) - 2023-08-03: 🐍 Cancun Devnet-8 Pre-Release

See [v1.0.1](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.1).

## [v1.0.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.0) - 2023-06-27: 🧪 Welcome to the Pytest Era

See [v1.0.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.0).

Older releases can be found on [the releases page](https://github.com/ethereum/execution-spec-tests/releases).
