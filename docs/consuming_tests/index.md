# Consuming Tests

This section provides specifications for @ethereum/execution-spec-tests test fixtures formats and an overview of the different methods and tools available to execution layer clients to help verify their implementations.

The information is organized as follows:

1. **[EEST Fixture Releases](./releases.md):** The available release types releases; release versioning.

2. **[Test Fixture Specifications](./test_formats/index.md):** Detailed fixture format specifications and help for implementing [`StateTest`](./test_formats/state_test.md#consumption) and [`BlockchainTest`](./test_formats/blockchain_test.md#consumption) consumer interfaces.

3. **[The Consume Command](./consume/index.md):** A family of commands that help clients "consume" test fixtures.

    i. **[Consume Cache & Fixture Inputs](./consume/cache.md):** How `consume` obtains fixtures.

    ii. **[Consume Direct](./consume/direct.md):** A command that assists executing tests against client direct interfaces.

    iii. **[Consume and Execute](./consume/hive/index.md):** The Hive Simulators available to verify EL client consensus:

    - [`eest/consume-engine`](./consume/hive/engine.md).
    - [`eest/consume-rlp`](./consume/hive/rlp.md).
    - [`eest/execute-blobs`](./consume/hive/execute.md).
