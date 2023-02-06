# Blockchain Tests

This tutorial teaches you to create a blockchain execution specification test. These tests verify that a blockchain, starting from a defined pre-state, will process given blocks and arrive at a defined post-state.

## Pre-requisites

Before proceeding with this tutorial, it is assumed that you have prior knowledge and experience with the following:

- Set up and run an execution specification test as outlined in the [quick start guide](../getting_started/01_quick_start.md).
- Understand how to read a [blockchain test](https://ethereum-tests.readthedocs.io/en/latest/test_filler/blockchain_filler.html).
- Know the basics of [Yul](https://docs.soliditylang.org/en/latest/yul.html), which is an EVM assembly language.
- Familiarity with [Python](https://docs.python.org/3/tutorial/).
- Understand how to write an execution spec [state transition test](./01_state_transition.md).

## Example Tests

The most effective method to learn how to write tests is to study a couple of straightforward examples. In this tutorial we will go over the [test_block_number](../../fillers/example/block_example.py#L19).

I assume you've already gone through the state transition test tutorial, so I will only explain the parts that are new.

### Smart Contract

This is the smart contract that is called by the transactions. It stores a pointer to storage in `storage[0]`. When it is called, that storage cell gets [the current block number](https://www.evm.codes/#43?fork=merge), and the pointer is incremented to the next value.


```python
contractAddr: Account(
    balance=1000000000000000000000,
    code=Yul(
        """
        {
            let nextCell := sload(0)
            sstore(nextCell, number())
            sstore(0, add(nextCell, 1))
        }
        """
    ),
    storage={
        0x00: 0x01,
    },
),
```




### Transaction generator

The transactions used in this test are nearly identical, the only different is the `nonce` value (which needs to be incremented). 

```python
def tx_generator():
    nonce = 0  # Initial value
    while True:
```

This looks like an endless loop, but it isn't because this is a [generator](https://wiki.python.org/moin/Generators) function. When generator encounters the `yield` keyword it returns the value and stops execution, keeping a copy of all the local variables.

```python
        tx = Transaction(
            ty=0x0,
            chain_id=0x0,
            nonce=nonce,
            to=contractAddr,
            gas_limit=500000,
            gas_price=10,
        )
        nonce = nonce + 1
```

Create the `Transaction` object and increment `nonce`.

```python
        yield tx

tx_generator = tx_generator()
```

Every time the function `tx_generator()` is called, it returns a new generator with a `nonce` of zero. To increment the `nonce` we need to use the *same* generator. We assign this generator to `tx_generator`.



### Blocks

```python
tx_per_block = [2, 0, 4, 8, 0, 0, 20, 1, 50]
```

Each integer in the `tx_per_block` array is the number of transactions in a block. The genesis is block zero, so we have two transactions in block one, no transactions in block two, four transactions at block three, etc.

```python
blocks = map(
    lambda len: Block(
        txs=list(map(lambda x: next(tx_generator), range(len)))
    ),
    tx_per_block,
)
```

The code that creates the blocks is a bit complex, so we'll go over it from the inside out.

```python
lambda x: next(tx_generator)
```

We use [`lambda` notation](https://www.w3schools.com/python/python_lambda.asp) to specify short functions. In this case, the function doesn't actually care about its input, it just returns the next transaction from the generator.

```python
range(len)
```

Python uses [`range(n)`](https://www.w3schools.com/python/ref_func_range.asp) to create a list of numbers, by default from 0 to `n-1`. Among other things, it's a simple way to create a list of `n` values.

```python
list(map(lambda x: next(tx_generator), range(len)))
```

The [`map` function](https://www.w3schools.com/python/ref_func_map.asp) runs the function (the first parameter) on every element of the list (the second parameter). Putting together what we know, it means that it runs `next(tx_generator)` `len` times, giving us `len` transactions. We then use [`list`](https://www.w3schools.com/python/python_lists.asp) to turn the transactions into a list that we can provide as a parameter.

```python
blocks = map(
    lambda len: Block(
        txs=list of len transactions
    ),
    tx_per_block,
)
```

The outer `lambda` function takes an integer, `len`, and creates a `Block` object whose transactions are `len` transactions. This function is then run on every value of `tx_per_block` to generate the blocks.

For example, if we had `tx_per_block = [2,0,4]`, we'd get this result:

```python
blocks = [
    Blocks(tx=[next(tx_generator), next(tx_generator)]),   # len=2, so two transactions
    Blocks(tx=[]),   # len = 0, so it's an empty list
    Blocks(tx=[next(tx_generator), next(tx_generator), next(tx_generator), next(tx_generator)])        
]
```

### Post state

Every transaction writes the block number into the next storage slot. Now we need to calculate the values in the storage.

```python
storage = {0: sum(tx_per_block) + 1}
```

Storage cell zero is the next cell to write into. It starts as one, and is then incremented in each transaction, so it's the total number of transactions plus one.

```python
nextSlot = 1
for blocknum in range(len(tx_per_block)):
    for i in range(tx_per_block[blocknum]):
```

For every block, and for every transaction within the block.

```python
        storage[nextSlot] = blocknum + 1
        nextSlot = nextSlot + 1
``` 

Write to the storage the block number and increment the next slot number. Because Python lists start with the 0'th element, the 0'th element is actually block 1, the 1st element block 2, etc.

```python
post = {contractAddr: Account(storage=storage)}
```

Create the post state. The storage we calculated is the storage for `contractAddr`.


### Actually yield the test

This is the code that actually creates the test. It is very similar to the code to create a state transaction test.

```python
yield BlockchainTest(
    genesis_environment=env,
    pre=pre,
    blocks=blocks,
    post=post,
)
```

Note that because this is `yield` we could have multiple tests under the same name.

## Conclusion

At this point you should be able to write blockchain tests in Python.
