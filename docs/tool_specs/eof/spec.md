# Ethereum EVM Object Format code verification tool

Each client is encouraged to implement the `evm eof` tool, which is used to validate EOF code tests by verifying EOF container validity.

## Inputs

### Test Vector Fixture

The test vector fixture is a JSON object that contains the test vector information. It is used to validate the EOF code and indicate the expected (if any) exception.

#### JSON Schema

See [types/Fixture](./types.md#fixture).

## Parameters

### Fork

The fork is a string that specifies the fork rules and all EIPs included in it for the state transition.

#### JSON Schema

See [types/Forks](./types.md#forks).

## Outputs

### Test Pass

The test pass is a JSON object that contains the test pass information. It is used to indicate the test pass status after execution of the test vector.

If the `evm eof` tool matches the expected result and expected exception (if any), the test pass status is `true`, otherwise, the test pass status is `false`.

The exception is either way set to `null` or the exception encountered by the `evm eof` tool.

#### JSON Schema

See [types/TestPass](./types.md#testpass).
