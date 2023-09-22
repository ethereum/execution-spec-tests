# Changelog

Test fixtures for use by clients are available for each release on the [Github releases page](https://github.com/ethereum/execution-spec-tests/releases).

**Key:** ✨ = New, 🐞 = Fixed, 🔀 = Changed, 💥 = Breaking change.

## 🔜 [Unreleased]

### 🧪 Test Cases

### 🛠️ Framework

### 🔧 EVM Tools

### 📋 Misc

- ✨ Docs: Changelog added ([#TBA](https://github.com/ethereum/execution-spec-tests/pull/TBA)).
- ✨ CI/CD: Run development fork tests in Github Actions ([#302](https://github.com/ethereum/execution-spec-tests/pull/302)).
- ✨ CI/CD: Generate test JSON fixtures on push ([#301](https://github.com/ethereum/execution-spec-tests/pull/303)).

## [v1.0.4](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.4) - 2023-09-21: 🐍 Cancun Devnet 9 Release 2

This release adds additional coverage to the current set of Cancun tests, up to the [Devnet-9 Cancun specification](https://notes.ethereum.org/@ethpandaops/dencun-devnet-9).

**Note:** Additional EIP-4788 updates from [ethereum/EIPs/pull/7672](https://github.com/ethereum/EIPs/pull/7672) will be included in the next release.

### 🧪 Test Cases

- ✨ [EIP-7516: BLOBBASEFEE opcode](https://eips.ethereum.org/EIPS/eip-7516): First tests. @marioevz in [#294](https://github.com/ethereum/execution-spec-tests/pull/294).
- ✨ [EIP-4788: Beacon block root in the EVM](https://eips.ethereum.org/EIPS/eip-4788): Increase coverage. @spencer-tb in [#297](https://github.com/ethereum/execution-spec-tests/pull/297).
- 🐞 [EIP-1153: Transient storage opcodes](https://eips.ethereum.org/EIPS/eip-1153): Remove conftest '+1153' in network field. @spencer-tb in [#299](https://github.com/ethereum/execution-spec-tests/pull/299).

### 🛠️ Framework

- 🔀 [EIP-4788](https://eips.ethereum.org/EIPS/eip-4788): Beacon root contract is pre-deployed at `0xbEAC020008aFF7331c0A389CB2AAb67597567d7a` @spencer-tb in [#297](https://github.com/ethereum/execution-spec-tests/pull/297).
- ✨ Deprecate empty accounts within framework. @spencer-tb in [#300](https://github.com/ethereum/execution-spec-tests/pull/300).
- ✨ Fixture generation split based on hive specificity. @spencer-tb in [#301](https://github.com/ethereum/execution-spec-tests/pull/301).
- 💥 `fill`: `--disable-hive` flag removed; replaced by `--enable-hive`. @spencer-tb in [#301](https://github.com/ethereum/execution-spec-tests/pull/301).
- ✨ Add engine API forkchoice updated information in fixtures. @spencer-tb in [#256](https://github.com/ethereum/execution-spec-tests/pull/256).

## [v1.0.3](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.3) - 2023-09-14: 🐍 Cancun Devnet 9 Release

See [v1.0.3](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.3).

## [v1.0.2](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.2) - 2023-08-11: 🐍 Cancun Devnet 8 + 4788 v2 Pre-Release

See [v1.0.2](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.2).

## [v1.0.1](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.1) - 2023-08-03: 🐍 Cancun Devnet-8 Pre-Release

See [v1.0.1](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.1).

## [v1.0.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.0) - 2023-06-27: 🧪 Welcome to the Pytest Era

See [v1.0.0](https://github.com/ethereum/execution-spec-tests/releases/tag/v1.0.0).

Older releases can be found on [the releases page](https://github.com/ethereum/execution-spec-tests/releases).
