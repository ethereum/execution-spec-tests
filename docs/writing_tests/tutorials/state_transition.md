# State Transition Tests

This tutorial teaches you to create a state transition execution specification test. These tests verify that a starting pre-state will reach a specified post-state after executing a single transaction.

## Pre-requisites

Before proceeding with this tutorial, it is assumed that you have prior knowledge and experience with the following:

- Repository set-up, see [installation](../../getting_started/installation.md).and run an execution specification test as outlined in the .
- Able to run `fill`, see [Getting Started: Filling Tests](../../filling_tests/getting_started.md).
- Understand how to read a [static state transition test](https://ethereum-tests.readthedocs.io/en/latest/state-transition-tutorial.html#the-source-code).
- Know the basics of [Yul](https://docs.soliditylang.org/en/latest/yul.html), which is an EVM assembly language.
- Familiarity with [Python](https://docs.python.org/3/tutorial/).

## Example Tests

The most effective method of learning how to write tests is to study a couple of straightforward examples. In this tutorial we will go over the [Yul](https://github.com/ethereum/execution-spec-tests/blob/main/tests/homestead/yul/test_yul_example.py#L19) state test.

### Yul Test

You can find the source code for the Yul test in [tests/homestead/yul/test_yul_example.py](../../tests/homestead/yul/test_yul_example/index.md).
It is the spec test equivalent of this [static test](https://github.com/ethereum/tests/blob/develop/src/GeneralStateTestsFiller/stExample/yulExampleFiller.yml).

Lets examine each section.

```python
"""
Test Yul Source Code Examples
"""
```

In Python, multi-line strings are denoted using `"""`. As a convention, a file's purpose is often described in the opening string of the file.

```python
from ethereum_test_forks import Fork, Frontier, Homestead
from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
    YulCompiler,
)
```

In this snippet the required constants, types and helper functions are imported from `ethereum_test_tools` and `ethereum_test_forks`. We will go over these as we come across them.

```python
@pytest.mark.valid_from("Homestead")
```

In Python this kind of definition is called a [*decorator*](https://docs.python.org/3/search.html?q=decorator).
It modifies the action of the function after it.
In this case, the decorator is a custom [pytest fixture](https://docs.pytest.org/en/latest/explanation/fixtures.html) defined by the execution-specs-test framework that specifies that the test is valid for the [Homestead fork](https://ethereum.org/en/history/#homestead) and all forks after it. The framework will then fill this test case for all forks in the fork range specified by the command-line arguments.

!!! info "Filling the test"
    To fill this test for all the specified forks, we can specify pytest's `-k` flag that [filters test cases by keyword expression](https://docs.pytest.org/en/latest/how-to/usage.html#specifying-tests-selecting-tests):

    ```console
    fill -k test_yul
    ```

    and to fill it for a specific fork range, we can provide the `--from` and `--until` command-line arguments:

    ```console
    fill -k test_yul --from London --until Paris
    ```

```python
def test_yul(state_test: StateTestFiller, pre: Alloc, yul: YulCompiler, fork: Fork):
    """
    Test YUL compiled bytecode.
    """
```

This is the format of a [Python function](https://docs.python.org/3/tutorial/controlflow.html#defining-functions).
It starts with `def <function name>(<parameters>):`, and then has indented code for the function.
The function definition ends when there is a line that is no longer indented. As with files, by convention functions start with a string that explains what the function does.

!!! note "The `state_test` function argument"
    This test defines a state test and, as such, *must* include the `state_test` in its function arguments. This is a callable object (actually a wrapper class to the `StateTest`); we will see how it is called later.

!!! note "The `pre` function argument"
    For all types of tests, it is highly encouraged that we define the `pre` allocation as a function argument, which will be populated with the pre-state requirements during the execution of the test function (see below).

```python
    env = Environment()
```

This line specifies that `env` is an [`Environment`](https://github.com/ethereum/execution-spec-tests/blob/8b4504aaf6ae0b69c3e847a6c051e64fcefa4db0/src/ethereum_test_tools/common/types.py#L711) object, and that we just use the default parameters.
If necessary we can modify the environment to have different block gas limits, block numbers, etc.
In most tests the defaults are good enough.

For more information, [see the static test documentation](../../consuming_tests/state_test.md).

#### Pre State

For every test we need to define the pre-state requirements, so we are certain of what is on the "blockchain" before the transaction is executed.
It can be used as a [dictionary](https://docs.python.org/3/tutorial/datastructures.html#dictionaries), which is the Python term for an associative array, but the appropriate way to populate it is by using the methods `fund_eoa`, `deploy_contract` or `fund_address` from the `Alloc` object.

In this example we are using the `deploy_contract` method to deploy a contract to some address available in the pre-state.

```python
    contract_address = pre.deploy_contract(
        code=yul(
            """
            {
                function f(a, b) -> c {
                    c := add(a, b)
                }

                sstore(0, f(1, 2))
                return(0, 32)
            }
            """
        ),
        balance=0x0BA1A9CE0BA1A9CE,
    )
```

Specifically we deploy a contract with yul code that adds two numbers and stores the result in storage.

```python
            balance=0x0BA1A9CE0BA1A9CE,
```

This field is the balance: the amount of Wei that the account has. It usually doesn't matter what its value is in the case of state test contracts.

```python
    contract_address = pre.deploy_contract(
```

As return value of the `deploy_contract` method we get the address where the contract was deployed and put it in the `contract_address` variable, which will later be used in the transaction.

```python
        storage={
            0x00: 0x00,
        },
```

We could also specify a starting storage for the contract, which is done by adding a `storage` parameter to the `deploy_contract` method.

```python
            code=yul(
```

Here we define the [Yul](https://docs.soliditylang.org/en/v0.8.17/yul.html) code for the contract. It is defined as a multi-line string and starts and ends with curly braces (`{ <yul> }`).

When running the test filler `fill`, the solidity compiler `solc` will automatically translate the Yul to EVM opcode at runtime.

!!! note
    Currently Yul and direct EVM opcode are supported in execution spec tests.

```python
                """
                {
                    function f(a, b) -> c {
                        c := add(a, b)
                    }
                    sstore(0, f(1, 2))
                    return(0, 32)
                }
                """
```

Within this example test Yul code we have a function definition, and inside it we are using the Yul `add` instruction. When compiled with `solc` it translates the instruction directly to the `ADD` opcode. For further Yul instructions [see here](https://docs.soliditylang.org/en/latest/yul.html#evm-dialect). Notice that function is utilized with the Yul `sstore` instruction, which stores the result of `add(1, 2)` to the storage address `0x00`.

Generally for execution spec tests the `sstore` instruction acts as a high-level assertion method to check pre to post-state changes. The test filler achieves this by verifying that the correct value is held within post-state storage, hence we can validate that the Yul code has run successfully.

```python
    sender = pre.fund_eoa(amount=0x0BA1A9CE0BA1A9CE)
```

In this line we specify that we require a single externally owned account (EOA) with a balance of `0x0BA1A9CE0BA1A9CE` Wei.

The returned object, which includes a private key, an address, and a nonce, is stored in the `sender` variable and will later be used as the sender of the transaction.

#### Transactions

```python
    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        sender=sender,
        to=contract_address,
        gas_limit=500000,
        gas_price=10,
        protected=False if fork in [Frontier, Homestead] else True,
    )
```

With the pre-state built, we can add a description for the [`Transaction`](https://github.com/ethereum/execution-spec-tests/blob/8b4504aaf6ae0b69c3e847a6c051e64fcefa4db0/src/ethereum_test_tools/common/types.py#L887).

```python
            sender=sender,
```

We use the sender variable from the pre-state to specify the sender of the transaction, which already has the necessary information to sign the transaction, and also contains the correct `nonce` for the transaction.

The `nonce` is a protection mechanism to prevent replay attacks, and the current rules of Ethereum require that the nonce of a transaction is equal to the number of transactions sent from the sender's address, starting from zero. This means that the first transaction sent from an address must have a nonce of zero, the second transaction must have a nonce of one, and so on.

The `nonce` field of the `sender` variable is automatically incremented for us by the `Transaction` object when the transaction is signed, so if we were to create another transaction with the same sender, the nonce would be incremented by one yet another time.

```python
            to=contract_address,
```

The `to` field specifies the address of the contract we want to call and, in this case, it is the address of the contract we deployed earlier.

For more information, [see the static test documentation](../../consuming_tests/state_test.md)

#### Post State

```python
    post = {
        contract_address: Account(
            storage={
                0x00: 0x03,
            },
        ),
    }
```

This is the post-state which is equivalent to [`expect`](https://ethereum-tests.readthedocs.io/en/latest/test_filler/state_filler.html#expect) in static tests, but without the indexes. It is similar to the pre-state, except that we do not need to specify everything, only those accounts and fields we wish to test.

In this case, we look at the storage of the contract we called and add to it what we expect to see. In this example storage cell `0x00` should be `0x03` as in the pre-state we essentially stored the result of the Yul instruction `add(1, 2)`.

#### State Test

```python
    state_test(env=env, pre=pre, post=post, tx=tx)
```

This line calls the wrapper to the `StateTest` object that provides all the objects required (for example, the fork parameter) in order to fill the test, generate the test fixtures and write them to file (by default, `./fixtures/<blockchain,state>_tests/example/yul_example/test_yul.json`).

## Conclusion

At this point you should be able to state transition tests within a single block.
