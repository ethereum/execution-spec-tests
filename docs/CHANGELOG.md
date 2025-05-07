# Changelog

Test fixtures for use by clients are available for each release on the [Github releases page](https://github.com/ethereum/execution-spec-tests/releases).

**Key:** ✨ = New, 🐞 = Fixed, 🔀 = Changed. 💥 = Breaking

## 🔜 [Unreleased]

### 💥 Breaking Change

### 🛠️ Framework

#### `fill`

- 🔀 Refactor: Encapsulate `fill`'s fixture output options (`--output`, `--flat-output`, `--single-fixture-per-file`) into a `FixtureOutput` class ([#1471](https://github.com/ethereum/execution-spec-tests/pull/1471)).
- ✨ Don't warn about a "high Transaction gas_limit" for `zkevm` tests ([#1598](https://github.com/ethereum/execution-spec-tests/pull/1598)).

#### `consume`

### 📋 Misc

- ✨ Added the [EIP checklist template](https://eest.ethereum.org/main/writing_tests/checklist_templates/eip_testing_checklist_template/) that serves as a reference to achieve better coverage when implementing tests for new EIPs ([#1327](https://github.com/ethereum/execution-spec-tests/pull/1327)).
- ✨ Added [Post-Mortems of Missed Test Scenarios](https://eest.ethereum.org/main/writing_tests/post_mortems/) to the documentation that serves as a reference list of all cases that were missed during the test implementation phase of a new EIP, and includes the steps taken in order to prevent similar test cases to be missed in the future ([#1327](https://github.com/ethereum/execution-spec-tests/pull/1327)).
- 🔀 Move Prague to stable and Osaka to develop ([#1573](https://github.com/ethereum/execution-spec-tests/pull/1573)).

### 🧪 Test Cases

## [v4.5.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v4.5.0) - 2025-05-14

### 💥 Breaking Change

#### EOF removed from Osaka

Following ["Interop Testing Call 34"](https://github.com/ethereum/pm/issues/1499) and the procedural EIPs [PR](https://github.com/ethereum/EIPs/pull/9703) the decision to remove EOF from Osaka was made.

To accommodate EOF testing for the interim within EEST, its tests have migrated to a new `tests/unscheduled` folder. This folder will now contain tests for features that are not yet CFI'd in any fork. When EOF is CFI'd for a fork in the future, all tests will be moved from unscheduled to the respective future fork folder.

A new fork `EOFv1` has additionally been created to fill and consume EOF related fixtures. Client tests fillers such as `evmone` (and client consumers) will now need to use this fork name.

### 🛠️ Framework

- ✨ Add an empty account function for usage within fill and execute ([#1482](https://github.com/ethereum/execution-spec-tests/pull/1482)).
- ✨ Added `TransactionException.INTRINSIC_GAS_BELOW_FLOOR_GAS_COST` exception to specifically catch the case where the intrinsic gas cost is insufficient due to the data floor gas cost ([#1582](https://github.com/ethereum/execution-spec-tests/pull/1582)).

### 📋 Misc

- ✨ Engine API updates for Osaka, add `get_blobs` rpc method ([#1510](https://github.com/ethereum/execution-spec-tests/pull/1510)).
- ✨ The EIP Version checker has been moved from `fill` and `execute` to it's own command-line tool `check_eip_versions` that gets ran daily as a Github Action ([#1537](https://github.com/ethereum/execution-spec-tests/pull/1537)).
- 🔀 Add new `tests/unscheduled` folder, move EOF from Osaka to unscheduled, add `EOFv1` fork name for EOF tests ([#1507](https://github.com/ethereum/execution-spec-tests/pull/1507)).
- ✨ CI features now contain an optional field to skip them from EEST full releases, `zkevm` and EOF features are now feature only ([#1596](https://github.com/ethereum/execution-spec-tests/pull/1596)).
- 🐞 Don't attempt to install `solc` via `solc-select` on ARM (official Linux ARM builds of `solc` are not available at the time of writing, cf [ethereum/solidity#11351](https://github.com/ethereum/solidity/issues/11351)) and add a version sanity check ([#1556](https://github.com/ethereum/execution-spec-tests/pull/1556)).

### 🧪 Test Cases

- 🔀 Automatically apply the `zkevm` marker to all tests under `./tests/zkevm/` and `./tests/prague/eip2537_bls_12_381_precompiles/` via conftest configuration ([#1534](https://github.com/ethereum/execution-spec-tests/pull/1534)).
- ✨ Port [calldataload](https://github.com/ethereum/tests/blob/ae4791077e8fcf716136e70fe8392f1a1f1495fb/src/GeneralStateTestsFiller/VMTests/vmTests/calldatacopyFiller.yml) and [calldatasize](https://github.com/ethereum/tests/blob/81862e4848585a438d64f911a19b3825f0f4cd95/src/GeneralStateTestsFiller/VMTests/vmTests/calldatasizeFiller.yml) tests ([#1236](https://github.com/ethereum/execution-spec-tests/pull/1236)).

## [v4.4.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v4.4.0) - 2025-04-29

### 💥 Breaking Change

#### `fixtures_static`

A new fixture tarball has been included in this release: `fixtures_static.tar.gz`.

This tarball contains all tests inside of [`./tests/static`](https://github.com/ethereum/execution-spec-tests/tree/main/tests/static), which at this point only contains all tests copied from [`GeneralStateTests` in `ethereum/tests@7dc757ec132e372b6178a016b91f4c639f366c02`](https://github.com/ethereum/tests/tree/7dc757ec132e372b6178a016b91f4c639f366c02/src/GeneralStateTestsFiller).

The tests have been filled using the new static test filler introduced in [#1336](https://github.com/ethereum/execution-spec-tests/pull/1336), and enhanced in [#1362](https://github.com/ethereum/execution-spec-tests/pull/1362) and [#1439](https://github.com/ethereum/execution-spec-tests/pull/1439).

Users can expect that all tests currently living in [ethereum/tests](https://github.com/ethereum/tests/tree/develop/src) should eventually make its way into [`./tests/static`](https://github.com/ethereum/execution-spec-tests/tree/main/tests/static) and can rely that these tests, filled for new forks even, will be included in `fixtures_static.tar.gz`.

#### `fixtures_zkevm`

Another new fixture tarball has been included in this release: `fixtures_zkevm.tar.gz`.

Includes tests that are tailored specifically to test the execution layer proof generators.

### 🛠️ Framework

#### `fill`

- 🐞 Fix the reported fixture source URLs for the case of auto-generated tests ([#1488](https://github.com/ethereum/execution-spec-tests/pull/1488)).

#### `consume`

- 🐞 Fix the Hive commands used to reproduce test executions that are displayed in test descriptions in the Hive UI ([#1494](https://github.com/ethereum/execution-spec-tests/pull/1494)).
- 🐞 Fix consume direct fails for geth blockchain tests ([#1502](https://github.com/ethereum/execution-spec-tests/pull/1502)).

### 📋 Misc

### 🧪 Test Cases

- ✨ [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): Test that DELEGATECALL to a 7702 target works as intended ([#1485](https://github.com/ethereum/execution-spec-tests/pull/1485)).
- ✨ [EIP-2573](https://eips.ethereum.org/EIPS/eip-2537): Includes a BLS12 point generator, alongside additional coverage many of the precompiles ([#1350](https://github.com/ethereum/execution-spec-tests/pull/1350)), ([#1505](https://github.com/ethereum/execution-spec-tests/pull/1505)).
- ✨ Add all [`GeneralStateTests` from `ethereum/tests`](https://github.com/ethereum/tests/tree/7dc757ec132e372b6178a016b91f4c639f366c02/src/GeneralStateTestsFiller) to `execution-spec-tests` located now at [tests/static/state_tests](https://github.com/ethereum/execution-spec-tests/tree/main/tests/static/state_tests) ([#1442](https://github.com/ethereum/execution-spec-tests/pull/1442)).
- ✨ [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929): Test that precompile addresses are cold/warm depending on the fork they are activated ([#1495](https://github.com/ethereum/execution-spec-tests/pull/1495)).

## [v4.3.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v4.3.0) - 2025-04-18

### 💥 Breaking Change

#### Consume engine strict exception checking

`consume engine` now checks exceptions returned by the execution clients in their Engine API responses, specifically in the `validationError`field of the `engine_newPayloadVX` method.

While not strictly a breaking change since tests will continue to run normally, failures are expected if a client modifies their exception messages.

This feature can be disabled by using `--disable-strict-exception-matching` for specific clients or forks.

### 🛠️ Framework

#### `fill`

- ✨ The `static_filler` plug-in now has support for static state tests (from [GeneralStateTests](https://github.com/ethereum/tests/tree/develop/src/GeneralStateTestsFiller)) ([#1362](https://github.com/ethereum/execution-spec-tests/pull/1362)).
- ✨ Introduce `pytest.mark.exception_test` to mark tests that contain an invalid transaction or block ([#1436](https://github.com/ethereum/execution-spec-tests/pull/1436)).
- 🐞 Fix `DeprecationWarning: Pickle, copy, and deepcopy support will be removed from itertools in Python 3.14.` by avoiding use `itertools` object in the spec `BaseTest` pydantic model ([#1414](https://github.com/ethereum/execution-spec-tests/pull/1414)).
- ✨ An optional configuration flag to override the maximum gas limit in the environment for filling or executing tests is now available. The `--block-gas-limit` flag overrides the default block gas limit during filling. The `--transaction-gas-limit` flag overrides the maximum for transactions during execution. ([#1470](https://github.com/ethereum/execution-spec-tests/pull/1470)).

#### `consume`

- 🐞 Fix fixture tarball downloading with regular, non-Github release URLS and with numerical versions in regular release specs, e.g., `stable@v4.2.0` ([#1437](https://github.com/ethereum/execution-spec-tests/pull/1437)).
- ✨ `consume engine` now has strict exception mapping enabled by default ([#1416](https://github.com/ethereum/execution-spec-tests/pull/1416)).

#### Tools

- 🔀 `generate_system_contract_deploy_test` test generator has been updated to handle system contracts that are not allowed to be absent when the fork happens ([#1394](https://github.com/ethereum/execution-spec-tests/pull/1394)).
- ✨ Add `generate_system_contract_error_test` to generate tests on system contracts that invalidate a block in case of error ([#1394](https://github.com/ethereum/execution-spec-tests/pull/1394)).

#### Exceptions

- ✨ `BlockException.SYSTEM_CONTRACT_EMPTY`: Raised when a required system contract was not found in the state by the time it was due to execution with a system transaction call ([#1394](https://github.com/ethereum/execution-spec-tests/pull/1394)).
- ✨ `BlockException.SYSTEM_CONTRACT_CALL_FAILED`: Raised when a system contract call made by a system transaction fails ([#1394](https://github.com/ethereum/execution-spec-tests/pull/1394)).
- ✨ `BlockException.INVALID_BLOCK_HASH`: Raised when the calculated block hash does not match the expectation (Currently only during Engine API calls) ([#1416](https://github.com/ethereum/execution-spec-tests/pull/1416)).
- ✨ `BlockException.INVALID_VERSIONED_HASHES`: Raised when a discrepancy is found between versioned hashes in the payload and the ones found in the transactions ([#1416](https://github.com/ethereum/execution-spec-tests/pull/1416)).

### 🧪 Test Cases

- ✨ [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): Test precompile case in same transaction as delegation without extra gas in case of precompile code execution; parametrize all call opcodes in existing precompile test ([#1431](https://github.com/ethereum/execution-spec-tests/pull/1431)).
- ✨ [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): Add invalid nonce authorizations tests for the case of multiple signers when the sender's nonce gets increased ([#1441](https://github.com/ethereum/execution-spec-tests/pull/1441)).
- ✨ [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): Add a test that verifies that set code transactions are correctly rejected before Prague activation ([#1463](https://github.com/ethereum/execution-spec-tests/pull/1463)).
- ✨ [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623): Additionally parametrize transaction validity tests with the `to` set to an EOA account (previously only contracts) ([#1422](https://github.com/ethereum/execution-spec-tests/pull/1422)).
- ✨ [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251): Add EIP-7251 test cases for modified consolidations contract that allows more consolidations ([#1465](https://github.com/ethereum/execution-spec-tests/pull/1465)).
- ✨ [EIP-6110](https://eips.ethereum.org/EIPS/eip-6110): Add extra deposit request edge cases, sending eth to the deposit contract while sending a deposit request ([#1467](https://github.com/ethereum/execution-spec-tests/pull/1467)).
- ✨ [EIP-6110](https://eips.ethereum.org/EIPS/eip-6110): Add cases for deposit log layout and other topics (ERC-20) transfer ([#1371](https://github.com/ethereum/execution-spec-tests/pull/1371)).
- ✨ [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251): Remove pytest skips for consolidation request cases ([#1449](https://github.com/ethereum/execution-spec-tests/pull/1449)).
- ✨ [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002), [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251): Add cases to verify behavior of contracts missing at fork ([#1394](https://github.com/ethereum/execution-spec-tests/pull/1394)).
- ✨ [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002), [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251): Add cases to verify behavior of system contract errors invalidating a block ([#1394](https://github.com/ethereum/execution-spec-tests/pull/1394)).
- 🔀 Remove [EIP-7698](https://eips.ethereum.org/EIPS/eip-7698): EIP has been removed and the tests related to it have also been removed, while preserving a subset of the tests to verify that functionality is removed in clients ([#1451](https://github.com/ethereum/execution-spec-tests/pull/1451)).

### 📋 Misc

- 🐞 Configure `markdownlint` to expect an indent of 4 with unordered lists (otherwise HTML documentation is rendered incorrectly, [#1460](https://github.com/ethereum/execution-spec-tests/pull/1460)).
- 🔀 Update `eels_resolutions.json` to point to temporary commit `bb0eb750d643ced0ebf5dec732cdd23558d0b7f2`, which is based on `forks/prague` branch, commit `d9a7ee24db359aacecd636349b4f3ac95a4a6e71`, with PRs https://github.com/ethereum/execution-specs/pull/1182, https://github.com/ethereum/execution-specs/pull/1183 and https://github.com/ethereum/execution-specs/pull/1191 merged ([#1394](https://github.com/ethereum/execution-spec-tests/pull/1394)).

## [v4.2.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v4.2.0) - 2025-04-08

**Note**: Although not a breaking change, `consume` users should delete the cache directory (typically located at `~/.cache/ethereum-execution-spec-tests`) used to store downloaded fixture release tarballs. This release adds support for [ethereum/tests](https://github.com/ethereum/tests) and [ethereum/legacytests](https://github.com/ethereum/legacytests) fixture release downloads and the structure of the cache directory has been updated to accommodate this change.

To try this feature:

```shell
consume direct --input=https://github.com/ethereum/tests/releases/download/v17.0/fixtures_blockchain_tests.tgz
```

To determine the cache directory location, see the `--cache-folder` entry from the command:

```shell
consume cache --help
```

### 💥 Breaking Change

### 🛠️ Framework

#### `consume`

- ✨ Add support for [ethereum/tests](https://github.com/ethereum/tests) and [ethereum/legacytests](https://github.com/ethereum/legacytests) release tarball download via URL to the `--input` flag of `consume` commands ([#1306](https://github.com/ethereum/execution-spec-tests/pull/1306)).
- ✨ Add support for Nethermind's `nethtest` command to `consume direct` ([#1250](https://github.com/ethereum/execution-spec-tests/pull/1250)).
- ✨ Allow filtering of test cases by fork via pytest marks (e.g., `-m "Cancun or Prague"`) ([#1304](https://github.com/ethereum/execution-spec-tests/pull/1304), [#1318](https://github.com/ethereum/execution-spec-tests/pull/1318)).
- ✨ Allow filtering of test cases by fixture format via pytest marks (e.g., `-m blockchain_test`) ([#1314](https://github.com/ethereum/execution-spec-tests/pull/1314)).
- ✨ Add top-level entries `forks` and `fixture_formats` to the index file that list all the forks and fixture formats used in the indexed fixtures ([#1318](https://github.com/ethereum/execution-spec-tests/pull/1318)).
- ✨ Enable logging from `consume` commands ([#1361](https://github.com/ethereum/execution-spec-tests/pull/1361)).
- ✨ Propagate stdout and stderr (including logs) captured during test execution to the Hive test result ([#1361](https://github.com/ethereum/execution-spec-tests/pull/1361)).
- 🐞 Don't parametrize tests for unsupported fixture formats; improve `consume` test collection ([#1315](https://github.com/ethereum/execution-spec-tests/pull/1315)).
- 🐞 Fix the the hive command printed in test reports to reproduce tests in isolation by prefixing the `--sim.limit` flag value with `id:` ([#1333](https://github.com/ethereum/execution-spec-tests/pull/1333)).
- 🐞 Improve index generation of [ethereum/tests](https://github.com/ethereum/tests) fixtures: Allow generation at any directory level and include `generatedTestHash` in the index file for the `fixture_hash` ([#1303](https://github.com/ethereum/execution-spec-tests/pull/1303)).
- 🐞 Fix loading of [ethereum/tests](https://github.com/ethereum/tests) and [ethereum/legacytests](https://github.com/ethereum/legacytests) fixtures for the case of mixed `0x0` and `0x1` transaction types in multi-index (`data`, `gas`, `value`) state test fixtures ([#1330](https://github.com/ethereum/execution-spec-tests/pull/1330)).
- ✨ Add Osaka to the hive ruleset, includes a small ruleset refactor ([#1355](https://github.com/ethereum/execution-spec-tests/pull/1355)).

#### `fill`

- 🐞 Fix `--fork/from/until` for transition forks when using `fill` [#1311](https://github.com/ethereum/execution-spec-tests/pull/1311).
- 🐞 Fix the node id for state tests marked by transition forks ([#1313](https://github.com/ethereum/execution-spec-tests/pull/1313)).
- ✨ Add `static_filler` plug-in which allows to fill static YAML and JSON tests (from [ethereum/tests](https://github.com/ethereum/tests)) by adding flag `--fill-static-tests` to `uv run fill` ([#1336](https://github.com/ethereum/execution-spec-tests/pull/1336)).

#### `execute`

- 🔀 Test IDs have changed to include the name of the test spec where the test came from (e.g. `state_test`, `blockchain_test`, etc) ([#1367](https://github.com/ethereum/execution-spec-tests/pull/1367)).
- ✨ Markers can now be used to execute only tests from a specific test spec type (e.g. `-m state_test`, `-m blockchain_test`, etc) ([#1367](https://github.com/ethereum/execution-spec-tests/pull/1367)).

### 📋 Misc

- 🔀 Bump the version of `execution-specs` used by the framework to the package [`ethereum-execution==1.17.0rc6.dev1`](https://pypi.org/project/ethereum-execution/1.17.0rc6.dev1/); bump the version used for test fixture generation for forks < Prague to current `execution-specs` master, [fa847a0](https://github.com/ethereum/execution-specs/commit/fa847a0e48309debee8edc510ceddb2fd5db2f2e) ([#1310](https://github.com/ethereum/execution-spec-tests/pull/1310)).
- 🐞 Init `TransitionTool` in `GethTransitionTool` ([#1276](https://github.com/ethereum/execution-spec-tests/pull/1276)).
- 🔀 Refactored RLP encoding of test objects to allow automatic generation of tests ([#1359](https://github.com/ethereum/execution-spec-tests/pull/1359)).
- ✨ Document how to manage `execution-spec-tests` package dependencies ([#1388](https://github.com/ethereum/execution-spec-tests/pull/1388)).

#### Packaging

- 🐞 Fix `eest make test` when `ethereum-execution-spec-tests` is installed as a package ([#1342](https://github.com/ethereum/execution-spec-tests/pull/1342)).
- 🔀 Pin `setuptools` and `wheel` in `[build-system]`, bump `trie>=3.1` and remove `setuptools` from package dependencies ([#1345](https://github.com/ethereum/execution-spec-tests/pull/1345), [#1351](https://github.com/ethereum/execution-spec-tests/pull/1351)).

### 🧪 Test Cases

- ✨ Add additional test coverage for EIP-152 Blake2 precompiles ([#1244](https://github.com/ethereum/execution-spec-tests/pull/1244)). Refactor to add variables for spec constants and common fixture code. ([#1395](https://github.com/ethereum/execution-spec-tests/pull/1395)), ([#1405](https://github.com/ethereum/execution-spec-tests/pull/1405)).
- ✨ Add EIP-7702 incorrect-rlp-encoding tests ([#1347](https://github.com/ethereum/execution-spec-tests/pull/1347)).
- ✨ Add EIP-2935 tests for all call opcodes ([#1379](https://github.com/ethereum/execution-spec-tests/pull/1379)).
- ✨ Add more tests for EIP-7702: max-fee-per-gas verification, delegation-designation as initcode tests ([#1372](https://github.com/ethereum/execution-spec-tests/pull/1372)).

## [v4.1.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v4.1.0) - 2025-03-11

### 💥 Breaking Changes

The following changes may be potentially breaking (all clients were tested with these changes with the state test format, but not the blockchain test format):

- 💥 Add a `yParity` field (that duplicates `v`) to transaction authorization tuples in fixture formats to have fields that conform to EIP-7702 spec, resolves [erigontech/erigon#14073](https://github.com/erigontech/erigon/issues/14073) ([#1286](https://github.com/ethereum/execution-spec-tests/pull/1286)).
- 💥 Rename the recently introduced `_info` field `fixture_format` to `fixture-format` for consistency [#1295](https://github.com/ethereum/execution-spec-tests/pull/1295).

### 🛠️ Framework

- 🔀 Make `BaseFixture` able to parse any fixture format such as `BlockchainFixture` ([#1210](https://github.com/ethereum/execution-spec-tests/pull/1210)).
- ✨ Blockchain and Blockchain-Engine tests now have a marker to specify that they were generated from a state test, which can be used with `-m blockchain_test_from_state_test` and `-m blockchain_test_engine_from_state_test` respectively ([#1220](https://github.com/ethereum/execution-spec-tests/pull/1220)).
- ✨ Blockchain and Blockchain-Engine tests that were generated from a state test now have `blockchain_test_from_state_test` or `blockchain_test_engine_from_state_test` as part of their test IDs ([#1220](https://github.com/ethereum/execution-spec-tests/pull/1220)).
- 🔀 Refactor `ethereum_test_fixtures` and `ethereum_clis` to create `FixtureConsumer` and `FixtureConsumerTool` classes which abstract away the consumption process used by `consume direct` ([#935](https://github.com/ethereum/execution-spec-tests/pull/935)).
- ✨ Allow `consume direct --collect-only` without specifying a fixture consumer binary on the command-line ([#1237](https://github.com/ethereum/execution-spec-tests/pull/1237)).
- ✨ Allow `fill --collect-only` without the need for existence of the folder `./fixtures'
- ✨ Report the (resolved) fixture tarball URL and local fixture cache directory when `consume`'s `--input` flag is a release spec or URL ([#1239](https://github.com/ethereum/execution-spec-tests/pull/1239)).
- ✨ EOF Container validation tests (`eof_test`) now generate container deployment state tests, by wrapping the EOF container in an init-container and sending a deploy transaction ([#783](https://github.com/ethereum/execution-spec-tests/pull/783), [#1233](https://github.com/ethereum/execution-spec-tests/pull/1233)).
- ✨ Use regexes for Hive's `--sim.limit` argument and don't use xdist if `--sim.parallelism==1` in the `eest/consume-rlp` and `eest/consume-rlp` simulators ([#1220](https://github.com/ethereum/execution-spec-tests/pull/1220)).
- 🐞 Register generated test markers, e.g., `blockchain_test_from_state_test`, to prevent test session warnings ([#1238](https://github.com/ethereum/execution-spec-tests/pull/1238), [#1245](https://github.com/ethereum/execution-spec-tests/pull/1245)).
- 🐞 Zero-pad `Environment` fields passed to `t8n` tools as required by `evmone-t8n` ([#1268](https://github.com/ethereum/execution-spec-tests/pull/1268)).

### 📋 Misc

- ✨ Add a guide to the docs for porting tests from `ethereum/tests` to EEST ([#1165](https://github.com/ethereum/execution-spec-tests/pull/1165)).
- ✨ Improve the `uv run eest make test` interactive CLI to enable creation of new test modules within existing test sub-folders ([#1241](https://github.com/ethereum/execution-spec-tests/pull/1241)).
- ✨ Update `mypy` to latest release `>=1.15.0,<1.16` ([#1209](https://github.com/ethereum/execution-spec-tests/pull/1209)).
- 🐞 Bug fix for filling with EELS for certain Python versions due to an issue with CPython ([#1231](https://github.com/ethereum/execution-spec-tests/pull/1231)).
- 🐞 Fix HTML site deployment due to the site's index file exceeding Github's max file size limit ([#1292](https://github.com/ethereum/execution-spec-tests/pull/1292)).
- ✨ Update the build fixtures workflow to use multiple self-hosted runners, remove `pectra-devnet-6` feature build ([#1296](https://github.com/ethereum/execution-spec-tests/pull/1296)).

### 🧪 Test Cases

- ✨ Add gas cost of delegation access in CALL opcode ([#1208](https://github.com/ethereum/execution-spec-tests/pull/1208)).
- ✨ Add EIP-7698 failed nonce and short data tests ([#1211](https://github.com/ethereum/execution-spec-tests/pull/1211)).
- ✨ Add EIP-2537 additional pairing precompile tests cases, and then update all BLS12 test vectors ([#1275](https://github.com/ethereum/execution-spec-tests/pull/1275), [#1289](https://github.com/ethereum/execution-spec-tests/pull/1289)).
- ✨ Add EIP-7685 and EIP-7002 test cases for additional request type combinations and modified withdrawal contract that allows more withdrawals ([#1340](https://github.com/ethereum/execution-spec-tests/pull/1340)).

## [v4.0.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v4.0.0) - 2025-02-14 - 💕

### 📁 Fixture Releases

- 🔀 Initially we moved old fork configured tests within stable and develop fixture releases to a separate legacy release ([#788](https://github.com/ethereum/execution-spec-tests/pull/788)).
- 🔀 This was later reverted after some client teams preferred to keep them in all in the same releases ([#1053](https://github.com/ethereum/execution-spec-tests/pull/1053)).

### 💥 Breaking Change

- ✨ Use uv for package management replacing pip ([#777](https://github.com/ethereum/execution-spec-tests/pull/777)).
- ✨ Ruff now replaces Flake8, Isort and Black resulting in significant changes to the entire code base including its usage ([#922](https://github.com/ethereum/execution-spec-tests/pull/922)).
- 🔀 Fill test fixtures using EELS by default. EEST now uses the [`ethereum-specs-evm-resolver`](https://github.com/petertdavies/ethereum-spec-evm-resolver) with the EELS daemon ([#792](https://github.com/ethereum/execution-spec-tests/pull/792)).
- 🔀 The EOF fixture format contained in `eof_tests` may now contain multiple exceptions in the `"exception"` field in the form of a pipe (`|`) separated string ([#759](https://github.com/ethereum/execution-spec-tests/pull/759)).
- 🔀 `state_test`, `blockchain_test` and `blockchain_test_engine` fixtures now contain a `config` field, which contains an object that contains a `blobSchedule` field. On the `blockchain_test` and `blockchain_test_engine` fixtures, the object also contains a duplicate of the `network` root field. The root's `network` field will be eventually deprecated ([#1040](https://github.com/ethereum/execution-spec-tests/pull/1040)).
- 🔀 `latest-stable-release` and `latest-develop-release` keywords for the `--input` flag in consume commands have been replaced with `stable@latest` and `develop@latest` respectively ([#1044](https://github.com/ethereum/execution-spec-tests/pull/1044)).

### 🛠️ Framework

- ✨ Execute command added to run existing tests in live networks ([#](https://github.com/ethereum/execution-spec-tests/pull/1157)).
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
- ✨ Added [`extend_with_defaults` utility function](https://eest.ethereum.org/main/writing_tests/writing_a_new_test/#ethereum_test_tools.utility.pytest.extend_with_defaults), which helps extend test case parameter sets with default values. `@pytest.mark.parametrize` ([#739](https://github.com/ethereum/execution-spec-tests/pull/739)).
- ✨ Added `Container.Init` to `ethereum_test_types.EOF.V1` package, which allows generation of an EOF init container more easily ([#739](https://github.com/ethereum/execution-spec-tests/pull/739)).
- ✨ Introduce method valid_opcodes() to the fork class ([#748](https://github.com/ethereum/execution-spec-tests/pull/748)).
- 🐞 Fixed `consume` exit code return values, ensuring that pytest's return value is correctly propagated to the shell. This allows the shell to accurately reflect the test results (e.g., failures) based on the pytest exit code ([#765](https://github.com/ethereum/execution-spec-tests/pull/765)).
- ✨ Added a new flag `--solc-version` to the `fill` command, which allows the user to specify the version of the Solidity compiler to use when compiling Yul source code; this version will now be automatically downloaded by `fill` via [`solc-select`](https://github.com/crytic/solc-select) ([#772](https://github.com/ethereum/execution-spec-tests/pull/772)).
- 🐞 Fix usage of multiple `@pytest.mark.with_all*` markers which shared parameters, such as `with_all_call_opcodes` and `with_all_create_opcodes` which shared `evm_code_type`, and now only parametrize compatible values ([#762](https://github.com/ethereum/execution-spec-tests/pull/762)).
- ✨ Added `selector` and `marks` fields to all `@pytest.mark.with_all*` markers, which allows passing lambda functions to select or mark specific parametrized values (see [documentation](https://eest.ethereum.org/main/writing_tests/test_markers/#covariant-marker-keyword-arguments) for more information) ([#762](https://github.com/ethereum/execution-spec-tests/pull/762)).
- ✨ Improves consume input flags for develop and stable fixture releases, fixes `--help` flag for consume ([#745](https://github.com/ethereum/execution-spec-tests/pull/745)).
- 🔀 Return exit-code from `consume` commands ([#766](https://github.com/ethereum/execution-spec-tests/pull/766)).
- 🔀 Remove duplicate EOF container tests, automatically check for duplicates ([#800](https://github.com/ethereum/execution-spec-tests/pull/800)).
- 🔀 Fix DATALOAD `pushed_stack_items` calculation ([#784](https://github.com/ethereum/execution-spec-tests/pull/784)).
- ✨ Add `evm_bytes` rename and print asm ([#844](https://github.com/ethereum/execution-spec-tests/pull/844)).
- 🔀 Use the `session_temp_folder` introduced in #824 ([#845](https://github.com/ethereum/execution-spec-tests/pull/845)).
- 🐞 Don't treat eels resolutions as a fixture ([#878](https://github.com/ethereum/execution-spec-tests/pull/878)).
- ✨ Emphasize that no tests were executed during a fill pytest session ([#887](https://github.com/ethereum/execution-spec-tests/pull/887)).
- 🔀 Move generic code from TransitionTool to a new generic base class EthereumCLI ([#894](https://github.com/ethereum/execution-spec-tests/pull/894)).
- 🐞 Fix erroneous fork mes- 🔀 Fix max stack height calculation ([#810](https://github.com/ethereum/execution-spec-tests/pull/810)).
- ✨ Add storage key hint in Storage class ([#917](https://github.com/ethereum/execution-spec-tests/pull/917)).
- ✨ Add system to verify exception strings ([#795](https://github.com/ethereum/execution-spec-tests/pull/795)).
- 🔀 Fix `FixedBytes` assignment rules ([#1010](https://github.com/ethereum/execution-spec-tests/pull/1010)).
- 🔀 Fix `Address` padding options ([#1113](https://github.com/ethereum/execution-spec-tests/pull/1113)).
- 🔀 Add `Container.expected_bytecode` optional parameter ([#737](https://github.com/ethereum/execution-spec-tests/pull/737)).
- ✨ Add support for `initcode_prefix` on EOF `Container.Init` ([#819](https://github.com/ethereum/execution-spec-tests/pull/819)).sage in pytest session header with development forks ([#806](https://github.com/ethereum/execution-spec-tests/pull/806)).
- 🐞 Fix `Conditional` code generator in EOF mode ([#821](https://github.com/ethereum/execution-spec-tests/pull/821)).
- 🔀 Ensure that `Block` objects keep track of their `fork`, for example, when the block's `rlp_modifier` is not `None` ([#854](https://github.com/ethereum/execution-spec-tests/pull/854)).
- 🔀 `ethereum_test_rpc` library has been created with what was previously `ethereum_test_tools.rpc` ([#822](https://github.com/ethereum/execution-spec-tests/pull/822)).
- ✨ Add `Wei` type to `ethereum_test_base_types` which allows parsing wei amounts from strings like "1 ether", "1000 wei", "10**2 gwei", etc ([#825](https://github.com/ethereum/execution-spec-tests/pull/825)).
- ✨ Pin EELS versions in `eels_resolutions.json` and include this file in fixture releases ([#872](https://github.com/ethereum/execution-spec-tests/pull/872)).
- 🔀 Replace `ethereum.base_types` with `ethereum-types` ([#850](https://github.com/ethereum/execution-spec-tests/pull/850)).
- 💥 Rename the `PragueEIP7692` fork to `Osaka` ([#869](https://github.com/ethereum/execution-spec-tests/pull/869)).
- ✨ Improve `fill` terminal output to emphasize that filling tests is not actually testing a client ([#807](https://github.com/ethereum/execution-spec-tests/pull/887)).
- ✨ Add the `BlockchainTestEngine` test spec type that only generates a fixture in the `EngineFixture` (`blockchain_test_engine`) format ([#888](https://github.com/ethereum/execution-spec-tests/pull/888)).
- 🔀 Move the `evm_transition_tool` package to `ethereum_clis` and derive the transition tool CL interfaces from a shared `EthereumCLI` class that can be reused for other sub-commands ([#894](https://github.com/ethereum/execution-spec-tests/pull/894)).
- ✨ Pass `state_test` property to T8N tools that support it (Only EELS at the time of merge) ([#943](https://github.com/ethereum/execution-spec-tests/pull/943)).
- ✨ Add the `eofwrap` cli used to wrap tests from `ethereum/tests` in an EOF container ([#896](https://github.com/ethereum/execution-spec-tests/pull/896)).
- 🔀 Improve gentest architecture with `EthereumTestBaseModel` and `EthereumTestRootModel` ([#901](https://github.com/ethereum/execution-spec-tests/pull/901)).
- 🔀 Migrate transaction test to `state_test` for `gentest` ([#903](https://github.com/ethereum/execution-spec-tests/pull/903)).
- 🔀 `ethereum_test_forks` forks now contain gas-calculating functions, which return the appropriate function to calculate the gas used by a transaction or memory function for the given fork ([#779](https://github.com/ethereum/execution-spec-tests/pull/779)).
- 🐞 Fix `Bytecode` class `__eq__` method ([#939](https://github.com/ethereum/execution-spec-tests/pull/939)).
- 🔀 Update `pydantic` from 2.8.2 to 2.9.2 ([#960](https://github.com/ethereum/execution-spec-tests/pull/960)).
- ✨ Add the `eest make test` command, an interactive CLI that helps users create a new test module and function ([#950](https://github.com/ethereum/execution-spec-tests/pull/950)).
- ✨ Add the `eest clean` command that helps delete generated files and directories from the repository ([#980](https://github.com/ethereum/execution-spec-tests/pull/980)).
- ✨ Add framework changes for EIP-7742, required for Prague devnet-5 ([#931](https://github.com/ethereum/execution-spec-tests/pull/931)).
- ✨ Add the `eest make env` command that generates a default env file (`env.yaml`)([#996](https://github.com/ethereum/execution-spec-tests/pull/996)).
- ✨ Generate Transaction Test type ([#933](https://github.com/ethereum/execution-spec-tests/pull/933)).
- ✨ Add a default location for evm logs (`--evm-dump-dir`) when filling tests ([#999](https://github.com/ethereum/execution-spec-tests/pull/999)).
- ✨ Slow tests now have greater timeout when making a request to the T8N server ([#1037](https://github.com/ethereum/execution-spec-tests/pull/1037)).
- ✨ Introduce [`pytest.mark.parametrize_by_fork`](https://eest.ethereum.org/main/writing_tests/test_markers/#pytestmarkfork_parametrize) helper marker ([#1019](https://github.com/ethereum/execution-spec-tests/pull/1019), [#1057](https://github.com/ethereum/execution-spec-tests/pull/1057)).
- 🐞 fix(consume): allow absolute paths with `--evm-bin` ([#1052](https://github.com/ethereum/execution-spec-tests/pull/1052)).
- ✨ Disable EIP-7742 framework changes for Prague ([#1023](https://github.com/ethereum/execution-spec-tests/pull/1023)).
- ✨ Allow verification of the transaction receipt on executed test transactions ([#1068](https://github.com/ethereum/execution-spec-tests/pull/1068)).
- ✨ Modify `valid_at_transition_to` marker to add keyword arguments `subsequent_transitions` and `until` to fill a test using multiple transition forks ([#1081](https://github.com/ethereum/execution-spec-tests/pull/1081)).
- 🐞 fix(consume): use `"HIVE_CHECK_LIVE_PORT"` to signal hive to wait for port 8551 (Engine API port) instead of the 8545 port when running `consume engine` ([#1095](https://github.com/ethereum/execution-spec-tests/pull/1095)).
- ✨ `state_test`, `blockchain_test` and `blockchain_test_engine` fixtures now contain the `blobSchedule` from [EIP-7840](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-7840.md), only for tests filled for Cancun and Prague forks ([#1040](https://github.com/ethereum/execution-spec-tests/pull/1040)).
- 🔀 Change `--dist` flag to the default value, `load`, for better parallelism handling during test filling ([#1118](https://github.com/ethereum/execution-spec-tests/pull/1118)).
- 🔀 Refactor framework code to use the [`ethereum-rlp`](https://pypi.org/project/ethereum-rlp/) package instead of `ethereum.rlp`, previously available in ethereum/execution-specs ([#1180](https://github.com/ethereum/execution-spec-tests/pull/1180)).
- 🔀 Update EELS / execution-specs EEST dependency to [99238233](https://github.com/ethereum/execution-specs/commit/9923823367b5586228e590537d47aa9cc4c6a206) for EEST framework libraries and test case generation ([#1181](https://github.com/ethereum/execution-spec-tests/pull/1181)).
- ✨ Add the `consume cache` command to cache fixtures before running consume commands ([#1044](https://github.com/ethereum/execution-spec-tests/pull/1044)).
- ✨ The `--input` flag of the consume commands now supports parsing of tagged release names in the format `<RELEASE_NAME>@<RELEASE_VERSION>` ([#1044](https://github.com/ethereum/execution-spec-tests/pull/1044)).
- 🐞 Fix stdout output when using the `fill` command ([#1188](https://github.com/ethereum/execution-spec-tests/pull/1188)).
- ✨ Add tests for blockchain intermediate state verification ([#1075](https://github.com/ethereum/execution-spec-tests/pull/1075)).
- ✨ Add Interactive CLI input functionality ([#947](https://github.com/ethereum/execution-spec-tests/pull/947)).
- 🔀 Rename `EOFTest.data` to `EOFTest.container` with rebase of `EOFStateTest` ([#1145](https://github.com/ethereum/execution-spec-tests/pull/1145)).
- ✨ Turn on `--traces` for EELS + `ethereum-specs-evm-resolver` ([#1174](https://github.com/ethereum/execution-spec-tests/pull/1174)).

### 📋 Misc

- ✨ Feature releases can now include multiple types of fixture tarball files from different releases that start with the same prefix ([#736](https://github.com/ethereum/execution-spec-tests/pull/736)).
- ✨ Releases for feature eip7692 now include both Cancun and Prague based tests in the same release, in files `fixtures_eip7692.tar.gz` and `fixtures_eip7692-prague.tar.gz` respectively ([#743](https://github.com/ethereum/execution-spec-tests/pull/743)).
✨ Re-write the test case reference doc flow as a pytest plugin and add pages for test functions with a table providing an overview of their parametrized test cases ([#801](https://github.com/ethereum/execution-spec-tests/pull/801), [#842](https://github.com/ethereum/execution-spec-tests/pull/842)).
- 🔀 Simplify Python project configuration and consolidate it into `pyproject.toml` ([#764](https://github.com/ethereum/execution-spec-tests/pull/764)).
- ✨ Add dev docs to help using nectos/act ([#776](https://github.com/ethereum/execution-spec-tests/pull/776)).
- 🔀 Update `uv.lock` for updated solc deps ([#782](https://github.com/ethereum/execution-spec-tests/pull/782)).
- ✨ Enable coverage on any test change ([#790](https://github.com/ethereum/execution-spec-tests/pull/790)).
- 🔀 Created `pytest_plugins.concurrency` plugin to sync multiple `xdist` processes without using a command flag to specify the temporary working folder ([#824](https://github.com/ethereum/execution-spec-tests/pull/824))
- 🔀 Move pytest plugin `pytest_plugins.filler.solc` to `pytest_plugins.solc.solc` ([#823](https://github.com/ethereum/execution-spec-tests/pull/823)).
- 🔀 Remove `formats.py`, embed properties as class vars ([#826](https://github.com/ethereum/execution-spec-tests/pull/826)).
- ✨ Add `build-evm-base` to docs deploy workflows ([#829](https://github.com/ethereum/execution-spec-tests/pull/829)).
- 🔀 Add links to the online test case docs in the EOF tracker ([#838](https://github.com/ethereum/execution-spec-tests/pull/838)).
- 🔀 Fix miscellaneous improvements to troubleshooting, navigation, styling ([#840](https://github.com/ethereum/execution-spec-tests/pull/840)).
- ✨ Include all parameters in test parameter datatables ([#842](https://github.com/ethereum/execution-spec-tests/pull/842)).
- ✨ Add info about ripemd160 & update running actions locally ([#847](https://github.com/ethereum/execution-spec-tests/pull/847)).
- ✨ Add `SECURITY.md` describing how to report vulnerabilities ([#848](https://github.com/ethereum/execution-spec-tests/pull/848)).
- 🔀 Change image from ubuntu-24.04 to ubuntu-latest in CI ([#855](https://github.com/ethereum/execution-spec-tests/pull/855)).
- 🐞 Asserts that the deploy docs tags workflow is only triggered for full releases ([#857](https://github.com/ethereum/execution-spec-tests/pull/857)).
- 🐞 Fix deploy docs tags workflow trigger ([#858](https://github.com/ethereum/execution-spec-tests/pull/858)).
- ✨ A new application-wide configuration manager provides access to environment and application configurations. ([#892](https://github.com/ethereum/execution-spec-tests/pull/892)).
- 🔀 Update the developer docs navigation ([#898](https://github.com/ethereum/execution-spec-tests/pull/898)).
- 🔀 Use jinja2 templating in `gentest` ([#900](https://github.com/ethereum/execution-spec-tests/pull/900)).
- ✨ Fix/add test github actions locally page ([#909](https://github.com/ethereum/execution-spec-tests/pull/909)).
- 🐞 Fix print fill output in coverage workflow on errors ([#919](https://github.com/ethereum/execution-spec-tests/pull/919)).
- 🐞 Use a local version of ethereum/execution-specs (EELS) when running the framework tests in CI ([#997](https://github.com/ethereum/execution-spec-tests/pull/997)).
- ✨ Use self-hosted runners for fixture building in CI ([#1051](https://github.com/ethereum/execution-spec-tests/pull/1051)).
- ✨ Release tarballs now contain fixtures filled for all forks, not only the fork under active development and the fork currently deployed on mainnet ([#1053](https://github.com/ethereum/execution-spec-tests/pull/1053)).
- ✨ `StateTest` fixture format now contains `state` field in each network post result, containing the decoded post allocation that results from the transaction execution ([#1064](https://github.com/ethereum/execution-spec-tests/pull/1064)).
- ✨ Include EELS fork resolution information in filled json test fixtures ([#1123](https://github.com/ethereum/execution-spec-tests/pull/1123)).
- 🔀 Updates ruff from version 0.8.2 to 0.9.4 ([#1168](https://github.com/ethereum/execution-spec-tests/pull/1168)).
- 🔀 Update `uv.lock` to be compatible with `uv>=0.5.22` ([#1178](https://github.com/ethereum/execution-spec-tests/pull/1178)).
- 🔀 Update `mypy` from version `0.991` to `1.15` ([#1209](https://github.com/ethereum/execution-spec-tests/pull/1209)).

### 🧪 Test Cases

- ✨ Migrate validation tests `EIP3540/validInvalidFiller.yml` ([#598](https://github.com/ethereum/execution-spec-tests/pull/598)).
- ✨ EIP-4844 test `tests/cancun/eip4844_blobs/test_point_evaluation_precompile.py` includes an EOF test case ([#610](https://github.com/ethereum/execution-spec-tests/pull/610)).
- ✨ Example test `tests/frontier/opcodes/test_dup.py` now includes EOF parametrization ([#610](https://github.com/ethereum/execution-spec-tests/pull/610)).
- ✨ Add EOFv1 function test - Call simple contract test ([#695](https://github.com/ethereum/execution-spec-tests/pull/695)).
- ✨ Add section size validation tests ([#705](https://github.com/ethereum/execution-spec-tests/pull/705)).
- ✨ Add deep and wide EOF subcontainers tests ([#718](https://github.com/ethereum/execution-spec-tests/pull/718)).
- ✨ Update [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) tests for Devnet-3 ([#733](https://github.com/ethereum/execution-spec-tests/pull/733))
- ✨ Migrate "valid" EOFCREATE validation ([#738](https://github.com/ethereum/execution-spec-tests/pull/738)).
- ✨ Migrate tests for truncated sections ([#740](https://github.com/ethereum/execution-spec-tests/pull/740)).
- ✨ Add out of order container section test ([#741](https://github.com/ethereum/execution-spec-tests/pull/741)).
- ✨ Convert all opcodes validation test `tests/frontier/opcodes/test_all_opcodes.py` ([#748](https://github.com/ethereum/execution-spec-tests/pull/748)).
- 🔀 Add Test types with 128 inputs ([#749](https://github.com/ethereum/execution-spec-tests/pull/749)).
- 🔀 Use new marker to EOF-ize MCOPY test ([#754](https://github.com/ethereum/execution-spec-tests/pull/754)).
- ✨ Add EOF Tests from Fuzzing ([#756](https://github.com/ethereum/execution-spec-tests/pull/756)).
- ✨ Add embedded container tests ([#763](https://github.com/ethereum/execution-spec-tests/pull/763)).
- ✨ Validate EOF only opcodes are invalid in legacy ([#768](https://github.com/ethereum/execution-spec-tests/pull/768)).
- ✨ Update EOF tracker, add unimplemented tests ([#773](https://github.com/ethereum/execution-spec-tests/pull/773)).
- ✨ Add EIP-7620 EOFCREATE gas tests ([#785](https://github.com/ethereum/execution-spec-tests/pull/785)).
- ✨ Add more fuzzing discovered EOF tests ([#789](https://github.com/ethereum/execution-spec-tests/pull/789)).
- ✨ Add EOF tests for invalid non-returning sections ([#794](https://github.com/ethereum/execution-spec-tests/pull/794)).
- ✨ Test to ensure transient storage is cleared after transactions ([#798](https://github.com/ethereum/execution-spec-tests/pull/798)).
- ✨ Test that transient storage stays at correct address ([#799](https://github.com/ethereum/execution-spec-tests/pull/799)).
- ✨ Add EOFCREATE referencing the same subcontainer twice test ([#809](https://github.com/ethereum/execution-spec-tests/pull/809)).
- ✨ Add dangling data in subcontainer test ([#812](https://github.com/ethereum/execution-spec-tests/pull/812)).
- 🐞 Fix [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)+EOF tests due to incorrect test expectations and faulty `Conditional` test generator in EOF mode ([#821](https://github.com/ethereum/execution-spec-tests/pull/821))
- 🐞 Fix TSTORE EOF variant test ([#831](https://github.com/ethereum/execution-spec-tests/pull/831)).
- 🔀 Unify EOF return code constants ([#834](https://github.com/ethereum/execution-spec-tests/pull/834)).
- ✨ Add RJUMP* vs CALLF tests ([#833](https://github.com/ethereum/execution-spec-tests/pull/833)).
- ✨ Add tests to clarify "non-returning instruction" ([#837](https://github.com/ethereum/execution-spec-tests/pull/837)).
- ✨ Add double RJUMPI stack validation tests ([#851](https://github.com/ethereum/execution-spec-tests/pull/851)).
- ✨ Add unreachable code sections tests ([#856](https://github.com/ethereum/execution-spec-tests/pull/856)).
- 💥 `PragueEIP7692` fork in tests has been updated to `Osaka` ([#869](https://github.com/ethereum/execution-spec-tests/pull/869))
- ✨ Update [EIP-6110](https://eips.ethereum.org/EIPS/eip-6110), [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002), [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251), [EIP-7685](https://eips.ethereum.org/EIPS/eip-7685), and [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) tests for Devnet-4 ([#832](https://github.com/ethereum/execution-spec-tests/pull/832))
- ✨ Add EIP-7069 and EIP-7620 failures and context vars tests ([#836](https://github.com/ethereum/execution-spec-tests/pull/836)).
- ✨ Add EOF EIP-4750 Stack validation in CALLF test ([#889](https://github.com/ethereum/execution-spec-tests/pull/889)).
- ✨ Add stack overflow by rule check to JUMPF tests ([#902](https://github.com/ethereum/execution-spec-tests/pull/902)).
- 🐞 Fix erroneous test with`CALLF` rule bug ([#907](https://github.com/ethereum/execution-spec-tests/pull/907)).
- ✨ Add test for EXTDELEGATECALL value cost ([#911](https://github.com/ethereum/execution-spec-tests/pull/911)).
- ✨ Add basic EOF execution tests ([#912](https://github.com/ethereum/execution-spec-tests/pull/912)).
- ✨ Add parametrized CALLF execution tests ([#913](https://github.com/ethereum/execution-spec-tests/pull/913)).
- ✨ Add CALLF execution tests ([#914](https://github.com/ethereum/execution-spec-tests/pull/914)).
- ✨ Add fibonacci and factorial CALLF tests ([#915](https://github.com/ethereum/execution-spec-tests/pull/915)).
- ✨ Add RJUMP* execution tests ([#916](https://github.com/ethereum/execution-spec-tests/pull/916)).
- ✨ [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) many delegations test ([#923](https://github.com/ethereum/execution-spec-tests/pull/923))
- ✨ Add opcode validation tests ([#932](https://github.com/ethereum/execution-spec-tests/pull/932)).
- ✨ Add RJUMPI with JUMPF tests ([#928](https://github.com/ethereum/execution-spec-tests/pull/928)).
- ✨ [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) set code of non-empty-storage account test ([#948](https://github.com/ethereum/execution-spec-tests/pull/948))
- ✨ Add PUSH* opcode tests ([#975](https://github.com/ethereum/execution-spec-tests/pull/975)).
- ✨ [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) implement 7702 test ideas ([#981](https://github.com/ethereum/execution-spec-tests/pull/981))
- ✨ [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) Remove delegation behavior of EXTCODE* ([#984](https://github.com/ethereum/execution-spec-tests/pull/984))
- ✨ Add EIP-7620 RETURNCONTRACT behavior verification test ([#1109](https://github.com/ethereum/execution-spec-tests/pull/1109)).
- ✨ Add EIP-7069 p256verify EOF calls tests ([#1021](https://github.com/ethereum/execution-spec-tests/pull/1021)).
- ✨ Add EIP-7480 DATACOPY edge cases tests ([#1020](https://github.com/ethereum/execution-spec-tests/pull/1020)).
- ✨ Add EIP-7069 EXTCALL creation gas charge tests ([#1025](https://github.com/ethereum/execution-spec-tests/pull/1025)).
- ✨ Add generic precompile-absence test ([#1036](https://github.com/ethereum/execution-spec-tests/pull/1036))
- ✨ Add test for [EIP-2537](https://eips.ethereum.org/EIPS/eip-2537) which uses the full discount table of G2 MSM ([#1038](https://github.com/ethereum/execution-spec-tests/pull/1038))
- ✨ [EIP-7691](https://eips.ethereum.org/EIPS/eip-7691) Blob throughput increase tests by parametrization of existing EIP-4844 tests ([#1023](https://github.com/ethereum/execution-spec-tests/pull/1023), [#1082](https://github.com/ethereum/execution-spec-tests/pull/1082))
- ✨ Port [calldatacopy test](https://github.com/ethereum/tests/blob/ae4791077e8fcf716136e70fe8392f1a1f1495fb/src/GeneralStateTestsFiller/VMTests/vmTests/calldatacopyFiller.yml) ([#1056](https://github.com/ethereum/execution-spec-tests/pull/1056)).
- ✨ [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623) Increase calldata cost ([#1004](https://github.com/ethereum/execution-spec-tests/pull/1004), [#1071](https://github.com/ethereum/execution-spec-tests/pull/1071))
- ✨ Add CALLF invalid section index tests ([#1111](https://github.com/ethereum/execution-spec-tests/pull/1111)).
- ✨ Add JUMPF invalid section index tests ([#1112](https://github.com/ethereum/execution-spec-tests/pull/1112)).
- ✨ Add CALLF truncated immediate bytes tests ([#1114](https://github.com/ethereum/execution-spec-tests/pull/1114)).
- ✨ [EIP-152](https://eips.ethereum.org/EIPS/eip-152) Add tests for Blake2 compression function `F` precompile ([#1067](https://github.com/ethereum/execution-spec-tests/pull/1067))
- ✨ Add CALLF non-returning section tests ([#1126](https://github.com/ethereum/execution-spec-tests/pull/1126)).
- ✨ Add DATALOADN truncated immediate bytes tests ([#1127](https://github.com/ethereum/execution-spec-tests/pull/1127)).
- 🔀 Update EIP-7702 test expectations according to [spec updates](https://github.com/ethereum/EIPs/pull/9248) ([#1129](https://github.com/ethereum/execution-spec-tests/pull/1129))
- ✨ Add tests for CALLF and non-returning ([#1140](https://github.com/ethereum/execution-spec-tests/pull/1140)).
- 🔀 Update EIP-7251 according to spec updates [#9127](https://github.com/ethereum/EIPs/pull/9127), [#9289](https://github.com/ethereum/EIPs/pull/9289) ([#1024](https://github.com/ethereum/execution-spec-tests/pull/1024), [#1155](https://github.com/ethereum/execution-spec-tests/pull/1155)).
- 🔀 Update EIP-7002 according to spec updates [#9119](https://github.com/ethereum/EIPs/pull/9119), [#9288](https://github.com/ethereum/EIPs/pull/9288) ([#1024](https://github.com/ethereum/execution-spec-tests/pull/1024), [#1155](https://github.com/ethereum/execution-spec-tests/pull/1155)).
- 🔀 Update EIP-2935 according to spec updates [#9144](https://github.com/ethereum/EIPs/pull/9144), [#9287](https://github.com/ethereum/EIPs/pull/9287) ([#1046](https://github.com/ethereum/execution-spec-tests/pull/1046), [#1155](https://github.com/ethereum/execution-spec-tests/pull/1155))
- ✨ Add DATALOADN validation and execution tests ([#1162](https://github.com/ethereum/execution-spec-tests/pull/1162)).
- ✨ Add EOF prefix tests ([#1187](https://github.com/ethereum/execution-spec-tests/pull/1187)).
- ✨ Add tests for EOF code header missing ([#1193](https://github.com/ethereum/execution-spec-tests/pull/1193)).
- ✨ Add tests for empty EOF type section ([#1194](https://github.com/ethereum/execution-spec-tests/pull/1194)).
- ✨ Add tests for multiple EOF type sections ([#1195](https://github.com/ethereum/execution-spec-tests/pull/1195)).
- ✨ Add EIP-7698 legacy EOF creation prevention tests ([#1206](https://github.com/ethereum/execution-spec-tests/pull/1206)).

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
- ✨ Tests are now encouraged to declare a `pre: Alloc` parameter to get the pre-allocation object for the test, and use `pre.deploy_contract` and `pre.fund_eoa` to deploy contracts and fund accounts respectively, instead of declaring the `pre` as a dictionary or modifying its contents directly (see the [state test tutorial](https://eest.ethereum.org/v4.1.0/writing_tests/tutorials/state_transition/) for an updated example) ([#584](https://github.com/ethereum/execution-spec-tests/pull/584)).
- ✨ Enable loading of [ethereum/tests/BlockchainTests](https://github.com/ethereum/tests/tree/develop/BlockchainTests) ([#596](https://github.com/ethereum/execution-spec-tests/pull/596)).
- 🔀 Refactor `gentest` to use `ethereum_test_tools.rpc.rpc` by adding to `get_transaction_by_hash`, `debug_trace_call` to `EthRPC` ([#568](https://github.com/ethereum/execution-spec-tests/pull/568)).
- ✨ Write a properties file to the output directory and enable direct generation of a fixture tarball from `fill` via `--output=fixtures.tgz`([#627](https://github.com/ethereum/execution-spec-tests/pull/627)).
- 🔀 `ethereum_test_tools` library has been split into multiple libraries ([#645](https://github.com/ethereum/execution-spec-tests/pull/645)).
- ✨ Add the consume engine simulator and refactor the consume simulator suite ([#691](https://github.com/ethereum/execution-spec-tests/pull/691)).
- 🐞 Prevents forcing consume to use stdin as an input when running from hive ([#701](https://github.com/ethereum/execution-spec-tests/pull/701)).

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

- ✨ Docs: Add a ["Consuming Tests"](https://eest.ethereum.org/main/consuming_tests/) section to the docs, where each test fixture format is described, along with the steps to consume them, and the description of the structures used in each format ([#375](https://github.com/ethereum/execution-spec-tests/pull/375)).
- 🔀 Docs: Update `t8n` tool branch to fill tests for development features in the [readme](https://github.com/ethereum/execution-spec-tests) ([#338](https://github.com/ethereum/execution-spec-tests/pull/338)).
- 🔀 Filling tool: Updated the default filling tool (`t8n`) to go-ethereum@master ([#368](https://github.com/ethereum/execution-spec-tests/pull/368)).
- 🐞 Docs: Fix error banner in online docs due to mermaid syntax error ([#398](https://github.com/ethereum/execution-spec-tests/pull/398)).
- 🐞 Docs: Fix incorrectly formatted nested lists in online doc ([#403](https://github.com/ethereum/execution-spec-tests/pull/403)).
- 🔀 CLI: `evm_bytes_to_python` is renamed to `evm_bytes` and now accepts flag `--assembly` to output the code in assembly format ([#844](https://github.com/ethereum/execution-spec-tests/pull/844))

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
- ✨ Docs: Add [a section explaining execution-spec-tests release artifacts](https://eest.ethereum.org/v4.1.0/consuming_tests/) ([#334](https://github.com/ethereum/execution-spec-tests/pull/334)).
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
