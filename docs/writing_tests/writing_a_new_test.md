# Writing a New Test

## Test Functions

Every test case is defined as a python function that defines a single `StateTest` or `BlockchainTest` by using one of the `state_test` or `blockchain_test` objects made available by the framework. Test cases, respectively test modules, must fulfill the following requirements:

| Requirement                                                            | When                                        |
| -----------------------------------------------------------------------|---------------------------------------------|
| Be [decorated with validity markers](#specifying-which-forks-tests-are-valid-for) | If the test case is not valid for all forks |
| Use one of `state_test` or `blockchain_test` [in its function arguments](#the-state_test-and-blockchain_test-test-function-arguments) | Always |
| Call the `state_test` or `blockchain_test` in its test body                                                                           | Always |
| Add a [reference version of the EIP spec](./reference_specification.md) under test | Test path contains `eip`  |

### Specifying which Forks Tests are Valid For

Test cases can (and it most cases should) be decorated with one or more "validity markers" that define which the forks the test is valid for. This is achieved by applying:

- `pytest.mark.valid_from(FORK)` and/or `pytest.mark.valid_until(FORK)`

or

- `pytest.mark.valid_at_transition_to(FORK)`

markers on either the test function, test class or test module level:

=== "Function"

    ```python
    import pytest

    @pytest.mark.valid_from("Berlin")
    @pytest.mark.valid_until("London")
    def test_access_list(state_test: StateTestFiller, fork: Fork):
    ```

=== "Class"

    ```python
    import pytest


    @pytest.mark.valid_from("Shanghai")
    class TestMultipleWithdrawalsSameAddress:
    ```

=== "Module"

    ```python
    import pytest

    pytestmark = pytest.mark.valid_from("Shanghai")
    ```

The [`ethereum_test_forks`](../library/ethereum_test_forks.md) package defines the available forks and provides the following helpers that return all forks within the specified range:

- [forks_from](../library/ethereum_test_forks.md#ethereum_test_forks.forks_from)
- [forks_from_until](../library/ethereum_test_forks.md#ethereum_test_forks.forks_from_until)

### The `state_test` and `blockchain_test` Test Function Arguments

The test function's signature _must_ contain exactly one of either a `state_test` or `blockchain_test` argument.

For example, for state tests:

```python
def test_access_list(state_test: StateTestFiller):
```

and for blockchain tests:

```python
def test_contract_creating_tx(
    blockchain_test: BlockchainTestFiller, fork: Fork, initcode: Initcode
):
```

The `state_test` and `blockchain_test` objects are actually wrapper classes to the `StateTest`, respectively `BlockchainTest` objects, that once called actually instantiate a new instance of these objects and fill the test case using the `evm` tool according to the pre and post states and the transactions defined within the test.

## `StateTest` Object

The `StateTest` object represents a single test vector, and contains the
following attributes:

- `env`: Environment object which describes the global state of the blockchain
    before the test starts.
- `pre`: Pre-State containing the information of all Ethereum accounts that exist
    before any transaction is executed.
- `post`: Post-State containing the information of all Ethereum accounts that are
    created or modified after all transactions are executed.
- `txs`: All transactions to be executed during test execution.

## `BlockchainTest` Object

The `BlockchainTest` object represents a single test vector that evaluates the
Ethereum VM by attempting to append multiple blocks to the chain:

- `pre`: Pre-State containing the information of all Ethereum accounts that exist
    before any block is executed.
- `post`: Post-State containing the information of all Ethereum accounts that are
    created or modified after all blocks are executed.
- `blocks`: All blocks to be appended to the blockchain during the test.

## Pre/Post State of the Test

The `pre` and `post` states are elemental to setup and then verify the outcome
of the state test.

Both `pre` and `post` are mappings of account addresses to `account` structures (see [more info](#the-account-object)).

A single test vector can contain as many accounts in the `pre` and `post` states
as required, and they can be also filled dynamically.

`storage` of an account is a key/value dictionary, and its values are
integers within range of `[0, 2**256 - 1]`.

`txs` are the steps which transform the pre-state into the post-state and
must perform specific actions within the accounts (smart contracts) that result
in verifiable changes to the balance, nonce, and/or storage in each of them.

`post` is compared against the outcome of the client after the execution
of each transaction, and any differences are considered a failure

When designing a test, all the changes must be ideally saved into the contract's
storage to be able to verify them in the post-state.

## Test Transactions

Transactions can be crafted by sending them with specific `data` or to a
specific account, which contains the code to be executed

Transactions can also create more accounts, by setting the `to` field to an
empty string.

Transactions can be designed to fail, and a verification must be made that the
transaction fails with the specific error that matches what is expected by the
test.

## Writing code for the accounts in the test

Account bytecode can be embedded in the test accounts by adding it to the `code`
field of the `account` object, or the `data` field of the `tx` object if the
bytecode is meant to be treated as init code or call data.

The code can be in either of the following formats:

- `bytes` object, representing the raw opcodes in binary format.
- `str`, representing an hexadecimal format of the opcodes.
- `Code` compilable object.

Currently supported built-in compilable objects are:

- `Yul` object containing [Yul source code](https://docs.soliditylang.org/en/latest/yul.html).

`Code` objects can be concatenated together by using the `+` operator.

## Verifying the Accounts' Post States

The state of the accounts after all blocks/transactions have been executed is
the way of verifying that the execution client actually behaves like the test
expects.

During their filling process, all tests automatically verify that the accounts
specified in their `post` property actually match what was returned by the
transition tool.

Within the `post` dictionary object, an account address can be:

- `None`: The account will not be checked for absence or existence in the
  result returned by the transition tool.
- `Account` object: The test expects that this account exists and also has
  properties equal to the properties specified by the `Account` object.
- `Account.NONEXISTENT`: The test expects that this account does not exist in
  the result returned by the transition tool, and if the account exists,
  it results in error.
  E.g. when the transaction creating a contract is expected to fail and the
  test wants to verify that the address where the contract was supposed to be
  created is indeed empty.

## The `Account` object

The `Account` object is used to specify the properties of an account to be
verified in the post state.

The python representation can be found in [src/ethereum_test_types/types.py](https://github.com/ethereum/execution-spec-tests/blob/main/src/ethereum_test_types/types.py).

It can verify the following properties of an account:

- `nonce`: the scalar value equal to a) the number of transactions sent by
  an Externally Owned Account, b) the amount of contracts created by a contract.
  
- `balance`: the amount of Wei (10<sup>-18</sup> Eth) the account has.  <!-- markdownlint-disable MD033 (MD033=no-inline-html) -->

- `code`: Bytecode contained by the account. To verify that an account contains
  no code, this property needs to be set to "0x" or "".
  
  It is not recommended to verify Yul compiled code in the output account,
  because the bytecode can change from version to version.

- `storage`: Storage within the account represented as a `dict` object.
  All storage keys that are expected to be set must be specified, and if a
  key is skipped, it is implied that its expected value is zero.
  Setting this property to `{}` (empty `dict`), means that all the keys in the
  account must be unset (equal to zero).

All account's properties are optional, and they can be skipped or set to `None`,
which means that no check will be performed on that specific account property.

## Verifying correctness of the new test

A well written test performs a single verification output at a time.

A verification output can be a single storage slot, the balance of an account,
or a newly created contract.

It is not recommended to use balance changes to verify test correctness, as it
can be easily affected by gas cost changes in future EIPs.

The best way to verify a transaction/block execution outcome is to check its
storage.

A test can be written as a negative verification. E.g. a contract is not
created, or a transaction fails to execute or runs out of gas.

This kind of verification must be carefully crafted because it is possible to end up
having a false positive result, which means that the test passed but the
intended verification was never made.

To avoid these scenarios, it is important to have a separate verification to
check that test is effective. E.g. when a transaction is supposed to fail, it
is necessary to check that the failure error is actually the one expected by
the test.

## Failing or invalid transactions

Transactions included in a StateTest are expected to be intrinsically valid,
i.e. the account sending the transaction must have enough funds to cover the
gas costs, the max fee of the transaction must be equal or higher than the
base fee of the block, etc.

An intrinsically valid transaction can still revert during its execution.

Blocks in a BlockchainTest can contain intrinsically invalid transactions but
in this case the block is expected to be completely rejected, along with all
transactions in it, including other valid transactions.

## Parametrizing tests

Tests can be parametrized by using the `@pytest.mark.parametrize` decorator.

Example:

```python
import pytest

@pytest.mark.parametrize(
    "tx_value,expected_balance",
    [
        pytest.param(0, 0, id="zero-value"),
        pytest.param(100, 100, id="non-zero-value"),
    ],
)
def test_contract_creating_tx(
    blockchain_test: BlockchainTestFiller, fork: Fork, tx_value: int, expected_balance: int
):
```

This will run the test twice, once with `tx_value` set to `0` and `expected_balance`
set to `0`, and once with `tx_value` set to `100` and `expected_balance` set to `100`.

The `fork` fixture is automatically provided by the framework and contains the
current fork under test, and does not need to be parametrized.

Tests can also be automatically parametrized with appropriate fork covariant
values using the `with_all_*` markers listed in the
[Test Markers](./test_markers.md#fork-covariant-markers) page.

### `named_pytest_param` helper function

This helper function receives keyword arguments with a default value specified for each, and returns a replacement to the pytest.param where not all parameters have to be specified and the missing parameters will be automatically parametrized with the default value.

Example:

```python
gas_test_argument_names, gas_test_param = named_pytest_param(
        signer_type=SignerType.SINGLE_SIGNER,
        authorization_invalidity_type=AuthorizationInvalidityType.NONE,
        authorizations_count=1,
        chain_id_type=ChainIDType.GENERIC,
        authorize_to_address=AddressType.EMPTY_ACCOUNT,
        access_list_case=AccessListType.EMPTY,
        self_sponsored=False,
        authority_type=AddressType.EMPTY_ACCOUNT,
        data=b"",
    )

@pytest.mark.parametrize(
  gas_test_argument_names,
  [
    gas_test_param(authorizations_count=2),
    ...
  ],
)
def test_gas(
    blockchain_test: BlockchainTestFiller,
    signer_type: SignerType,
    authorization_invalidity_type: AuthorizationInvalidityType,
    authorizations_count: int,
    chain_id_type: ChainIDType,
    authorize_to_address: AddressType,
    access_list_case: AccessListType,
    self_sponsored: bool,
    authority_type: AddressType,
    data: bytes,
):
    ... 
```

This will run the test with the default values for all parameters except for `authorizations_count` which will be set to `2`.
