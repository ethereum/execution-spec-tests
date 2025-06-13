# Blockchain Engine Reorg Tests  <!-- markdownlint-disable MD051 (MD051=link-fragments "Link fragments should be valid") -->

The Blockchain Engine Reorg Test fixture format tests are included in the fixtures subdirectory `blockchain_tests_engine_reorg`, and use Engine API directives with optimized shared pre-allocation for improved execution performance.

These are produced by the `StateTest` and `BlockchainTest` test specs when using the `--generate-shared-pre` and `--use-shared-pre` flags.

## Description

The Blockchain Engine Reorg Test fixture format is an optimized variant of the [Blockchain Engine Test](./blockchain_test_engine.md) format designed for large-scale test execution with performance optimizations.

It uses the Engine API to test block validation and consensus rules while leveraging **shared pre-allocation state** to significantly reduce test execution time and resource usage. Tests are grouped by their initial state (fork + environment + pre-allocation) and share common genesis states through blockchain reorganization.

The key optimization is that **clients need only be started once per group** instead of once per test (as in the original engine fixture format), dramatically improving execution performance for large test suites.

Instead of including large pre-allocation state in each test fixture, this format references a shared pre-allocation folder (`pre_alloc`) which includes all different pre-allocation combinations used for any test fixture group.

A single JSON fixture file is composed of a JSON object where each key-value pair is a different [`ReorgFixture`](#reorgfixture) test object, with the key string representing the test name.

The JSON file path plus the test name are used as the unique test identifier.

## Shared Pre-Allocation File

The `blockchain_tests_engine_reorg` directory contains a special directory `pre_alloc` that stores shared pre-allocation state file used by all tests in this format, one per pre-allocation group with the name of the pre-alloc hash. This folder is essential for test execution and must be present alongside the test fixtures.

### Pre-Allocation File Structure

Each file in the `pre_alloc` folder corresponds to a pre-allocation hash to shared state groups:

```json
{
   "test_count": 88,
   "pre_account_count": 174,
   "testIds": ["test1", "test2", ...],
   "network": "Prague",
   "environment": { ... },
   "pre": { ... }
}
```

#### SharedPreStateGroup Fields

- **`test_count`**: Number of tests sharing this pre-allocation group
- **`pre_account_count`**: Number of accounts in the shared pre-allocation state
- **`testIds`**: Array of test identifiers that use this shared state
- **`network`**: Fork name (e.g., "Prague", "Cancun")
- **`environment`**: Complete [`Environment`](./common_types.md#environment) object with execution context
- **`pre`**: Shared [`Alloc`](./common_types.md#alloc-mappingaddressaccount) object containing initial account states

## Consumption

For each [`ReorgFixture`](#reorgfixture) test object in the JSON fixture file, perform the following steps:

1. **Load Shared Pre-Allocation**:
   - Read the appropriate file from the `pre_alloc` folder in the same directory
   - Locate the shared state group using [`preHash`](#-prehash-string)
   - Extract the `pre` allocation and `environment` from the shared group

2. **Initialize Client**:
   - Use [`network`](#-network-fork) to configure the execution fork schedule
   - Use the shared `pre` allocation as the starting state
   - Use the shared `environment` as the execution context
   - Use [`genesisBlockHeader`](#-genesisblockheader-fixtureheader) as the genesis block header

3. **Execute Engine API Sequence**:
   - For each [`FixtureEngineNewPayload`](#fixtureenginenewpayload) in [`engineNewPayloads`](#-enginenewpayloads-listfixtureenginenewpayload):
     1. Deliver the payload using `engine_newPayloadVX`
     2. Validate the response according to the payload's expected status
   - If [`syncPayload`](#-syncpayload-optionalfixtureenginenewpayload) is present, execute it for chain synchronization

4. **Verify Final State**:
   - Compare the final chain head against [`lastblockhash`](#-lastblockhash-hash)
   - If [`postStateDiff`](#-poststatediff-optionalalloc) is present:
     - Apply the state differences to the shared pre-allocation
     - Verify the resulting state matches the client's final state
   - If `post` field were present (not typical), verify it directly

## Structures

### `ReorgFixture`

#### - `network`: [`Fork`](./common_types.md#fork)

##### TO BE DEPRECATED

Fork configuration for the test.

This field is going to be replaced by the value contained in `config.network`.

#### - `preHash`: `string`

Hash identifier referencing a shared pre-allocation group in the `pre_alloc` folder. This hash uniquely identifies the combination of fork, environment, and pre-allocation state shared by multiple tests.

#### - `genesisBlockHeader`: [`FixtureHeader`](./blockchain_test.md#fixtureheader)

Genesis block header. The state root in this header must match the state root calculated from the shared pre-allocation referenced by [`preHash`](#-prehash-string).

#### - `engineNewPayloads`: [`List`](./common_types.md#list)`[`[`FixtureEngineNewPayload`](#fixtureenginenewpayload)`]`

List of `engine_newPayloadVX` directives to be processed after the genesis block. These define the sequence of blocks to be executed via the Engine API.

#### - `syncPayload`: [`Optional`](./common_types.md#optional)`[`[`FixtureEngineNewPayload`](#fixtureenginenewpayload)`]`

Optional synchronization payload used for blockchain reorganization scenarios. When present, this payload is typically used to sync the chain to a specific state before or after the main payload sequence.

#### - `lastblockhash`: [`Hash`](./common_types.md#hash)

Hash of the last valid block after all payloads have been processed, or the genesis block hash if all payloads are invalid.

#### - `postStateDiff`: [`Optional`](./common_types.md#optional)`[`[`Alloc`](./common_types.md#alloc-mappingaddressaccount)`]`

State differences from the shared pre-allocation state after test execution. This optimization stores only the accounts that changed, were created, or were deleted during test execution, rather than the complete final state.

To reconstruct the final state:

1. Start with the shared pre-allocation from the `pre_alloc` folder
2. Apply the changes in `postStateDiff`:
   - **Modified accounts**: Replace existing accounts with new values
   - **New accounts**: Add accounts not present in pre-allocation  
   - **Deleted accounts**: Remove accounts (represented as `null` values)

#### - `config`: [`FixtureConfig`](#fixtureconfig)

Chain configuration object to be applied to the client running the blockchain engine reorg test.

### `FixtureConfig`

#### - `network`: [`Fork`](./common_types.md#fork)

Fork configuration for the test. It is guaranteed that this field contains the same value as the root field `network`.

#### - `blobSchedule`: [`BlobSchedule`](./common_types.md#blobschedule-mappingforkforkblobschedule)

Optional; present from Cancun on. Maps forks to their blob schedule configurations as defined by [EIP-7840](https://eips.ethereum.org/EIPS/eip-7840).

### `FixtureEngineNewPayload`

Engine API payload structure identical to the one defined in [Blockchain Engine Tests](./blockchain_test_engine.md#fixtureenginenewpayload). Includes execution payload, versioned hashes, parent beacon block root, validation errors, version, and error codes.

## Usage Notes

- This format is only generated when using `--generate-shared-pre` and `--use-shared-pre` flags
- The `pre_alloc` folder is essential and must be distributed with the test fixtures
- Tests are grouped by identical (fork + environment + pre-allocation) combinations
- The format is optimized for Engine API testing (post-Paris forks)
- Reorganization scenarios are supported through the `forkChoiceUpdate` mechanism
