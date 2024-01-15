# Exception Tests

Exception tests are a special type of test that verify that an invalid transaction or an invalid block are correctly rejected with the expected error.

## Creating an Exception Test

To test for an exception, the test can use either the following types from `ethereum_test_tools` library:

- [`TransactionException`](../../library/ethereum_test_tools/#ethereum_test_tools.TransactionException): To be added to the `error` field of the [`Transaction`](../../library/ethereum_test_tools/#ethereum_test_tools.Transaction) object, and to the `exception` field of the [`Block`](../../library/ethereum_test_tools/#ethereum_test_tools.Block) object that includes the transaction; this exception type is used when a transaction is expected to fail, and therefore when included in a block, the block is expected to be invalid too. This is different from transactions that can be included in blocks but where an exception during EVM execution is expected (e.g. a revert, or out-of-gas, which can be included in valid blocks).
- [`BlockException`](../../library/ethereum_test_tools/#ethereum_test_tools.BlockException): To be added to the `exception` field of the [`Block`](../../library/ethereum_test_tools/#ethereum_test_tools.Block) object; this exception type is used when a block is expected to be invalid, but the exception is related to a block property, e.g. an invalid value of the block header.

Exceptions can be combined with the `|` operator, to indicate that a test vector can throw either exception.

Ideally, the tester should aim to use only one exception per test vector, and only use multiple exceptions on the rare instance when it is not possible to know which exception will be thrown because it depends on client implementation.

## Adding a new exception

If a test requires a new exception, because none of the existing ones is suitable for the test, a new exception can be added to either [`TransactionException`](../../library/ethereum_test_tools/#ethereum_test_tools.TransactionException) or [`BlockException`](../../library/ethereum_test_tools/#ethereum_test_tools.BlockException) classes.

The new exception should be added as a new enum value, and the docstring of the attribute should be a string that describes the exception.

The name of the exception should be unique, and should not be used by any other exception.

## Test runner behavior on exception tests

When an exception is added to a test vector, the test runner must check that the transaction or block is rejected with the expected exception.

The test runner must map the exception key to the corresponding error string that is expected to be returned by the client.

Exception mapping are particularly important in blockchain tests because the block can be invalid for multiple reasons, and the client returning a different error can mean that a verification in the client is faulty.