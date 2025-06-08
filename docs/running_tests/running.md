# Methods to Run Tests

EEST has two commands `consume` and `execute` to help run test cases against EL clients:

1. `consume` runs a JSON test fixtures against a client - the client is said to "consume" the test case fixture. JSON test fixtures are generated using [`fill`](../filling_tests/index.md) and EELS.
2. `execute` runs a test case from its Python source against a client - the test case is "executed" against the client.

Both of `consume` and `execute` provide sub-commands which correspond to different testing methods:

| Command                                      | Description                                                            | Components tested                                            | Environment   | Scope                        |
| -------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------ | ------------- | ---------------------------- |
| [`consume direct`](./consume/direct.md)      | Client consume tests via a `statetest` interface                       | EVM                                                          | Staging       | Module test                  |
| [`consume direct`](./consume/direct.md)      | Client consume tests via a `blocktest` interface                       | EVM, block processing                                        | Staging       | Module test/</br>Integration test |
| [`consume engine`](./consume/hive/engine.md) | Client imports blocks via Engine API `EngineNewPayload` in Hive        | EVM, block processing, Engine API                            | Staging, Hive | System test                  |
| [`consume rlp`](./consume/hive/rlp.md)       | Client imports RLP-encoded blocks upon start-up in Hive                | EVM, block processing, RLP import (sync\*)                   | Staging, Hive | System test                  |
| [`execute hive`](./execute/index.md)          | Tests executed against a client via JSON RPC `eth_sendRawTransaction` in Hive           | EVM, JSON RPC, mempool                                       | Staging, Hive | System test |
| [`execute remote`](./execute/index.md)      | Tests executed against a client via JSON RPC `eth_sendRawTransaction` on a live network | EVM, JSON RPC, mempool, EL-EL/EL-CL interaction (indirectly) | Production    | System Test |

\*sync: Depending on code paths used in client, see the RLP vs Engine Simulator section below.

## RLP vs Engine Simulator

The RLP Simulator (`eest/consume-rlp`) and the Engine Simulator (`eest/consume-engine`) should be seen as complimentary to one another. Although they execute the same underlying EVM test cases, the block validation logic is executed via different client code paths (using different [fixture formats](./test_formats/index.md)). Therefore, ideally, **both simulators should be executed for full coverage**.

### Code Path Choices

Clients consume fixtures in the `eest/consume-engine` simulator via the Engine API's `EngineNewPayloadv*` endpoint; a natural way to validate, respectively invalidate, block payloads. In this case, there is no flexibility in the choice of code path - it directly harnesses mainnet client functionality. The `eest/consume-rlp` Simulator, however, allows clients more freedom, as the rlp-encoded blocks are imported upon client startup. Clients are recommended to try and hook the block import into the code path used for historical syncing.

### Differences

| Aspect                  | RLP Simulator: `eest/consume-rlp`                         | Engine Simulator: `eest/consume-engine`                                |
| ----------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Fixture Format Used** | [`BlockchainTest`](./test_formats/blockchain_test.md) | [`BlockchainTestEngine`](./test_formats/blockchain_test_engine.md) |
| **Fork support**        | All forks (including pre-merge)                           | Post-merge forks only (Paris+)                                         |
| **Client code path**    | Historical sync / block import pipeline                   | Engine API / consensus integration                                     |
| **Real-world analogy**  | Blocks received during sync                               | Blocks received from consensus client                                  |
| **Interface**           | Block import upon start-up via RLP files                  | Engine API calls (`newPayload`, `forkchoiceUpdated`)                   |
| **Exception testing**   | Basic exception handling                                  | Advanced exception verification with client-specific mappers           |

### The Engine Simulator is essential for

- Testing production post-merge behavior.
- Validating Engine API implementations.
- Testing consensus-execution layer interaction.
- Ensuring correct payload handling.
- **Performing exception tests with correct client exception verification**.
- Production readiness validation.

### The RLP Simulator is ideal for

- Testing historical sync code paths.
- Validating block import and validation logic.
- Testing all forks including pre-merge.
- Debugging block processing issues.
- Performance testing of block import.

!!! hint "Running both simulators adds some redundancy that can assist test debugging"

    If Engine tests fail but RLP tests pass, the issue is likely in your Engine API implementation rather than core EVM logic.

!!! tip "Rapid EVM development"

    The [`direct` method](./consume/direct.md) with the [`StateTest` format](./test_formats/state_test.md) should be used for the fastest EVM development feedback loop. Additionally, EVM traces can be readily produced and compared to other implementations.
