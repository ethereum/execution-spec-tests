# Exceptions

Exception types are represented as a JSON string in the test fixtures.

The exception converted into a string is composed of the exception type name,
followed by a period, followed by the specific exception name.

For example, the exception `INSUFFICIENT_ACCOUNT_FUNDS` of type
`TransactionException` is represented as
`"TransactionException.INSUFFICIENT_ACCOUNT_FUNDS"`.

The JSON string can contain multiple exception types, separated by the `|`
character, denoting that the transaction or block can throw either one of
the exceptions.

## `TransactionException`

::: ethereum_test_exceptions.TransactionException

## `BlockException`

::: ethereum_test_exceptions.BlockException

## `EOFException`

::: ethereum_test_exceptions.EOFException
