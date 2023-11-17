# Changelog

Test fixtures for use by clients are available for each release on the [Github releases page](https://github.com/ethereum/execution-spec-tests/releases).

**Key:** ✨ = New, 🐞 = Fixed, 🔀 = Changed, 💥 = Breaking change.

## 🔜 [Unreleased - v1.0.7](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.7) - 2023-XX-XX: 🐍

### 🧪 Test Cases

### 🛠️ Framework

- ✨ Add a `--single-fixture-per-file` flag to generate one fixture JSON file per test case ([#331](https://github.com/ethereum/execution-spec-tests/pull/331)).
- 🔀 Rename test fixtures names to match the corresponding pytest node ID as generated using `fill` ([#342](https://github.com/ethereum/execution-spec-tests/pull/342)).
- 💥 Replace "=" with "_" in pytest node ids and test fixture names ([#342](https://github.com/ethereum/execution-spec-tests/pull/342)).

### 🔧 EVM Tools

### 📋 Misc

- 🔀 Docs: Update `t8n` tool branch to fill tests for development features in the [readme](https://github.com/ethereum/execution-spec-test) ([#338](https://github.com/ethereum/execution-spec-tests/pull/338)).

## Breaking Changes

1. In this release the pytest node ID is now used for fixture names (previously only the test parameters were used), this should not be breaking. However, "=" in both node IDs and therefore fixture names, have been replaced with "_", which may break tooling that depends on the "=" character.

   Pytest node ID example:

   - Previous node ID: `tests/frontier/opcodes/test_dup.py::test_dup[fork=Frontier]`
   - New node ID: `tests/frontier/opcodes/test_dup.py::test_dup[fork_Frontier]`

   Fixture name example:
   - Previous fixture name: `fork=Frontier`
   - New fixture name: `fork_Frontier`

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
