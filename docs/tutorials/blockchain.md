# Blockchain Tests

This tutorial teaches you to create a blockchain execution specification test. These tests verify that a blockchain, starting from a defined pre-state, will process given blocks and arrive at a defined post-state.

## Pre-requisites

Before proceeding with this tutorial, it is assumed that you have prior knowledge and experience with the following:

- Set up and run an execution specification test as outlined in the [quick start guide](../getting_started/quick_start.md).
- Understand how to read a [blockchain test](https://ethereum-tests.readthedocs.io/en/latest/test_filler/blockchain_filler.html).
- Know the basics of [Yul](https://docs.soliditylang.org/en/latest/yul.html), which is an EVM assembly language.
- Familiarity with [Python](https://docs.python.org/3/tutorial/).
- Understand how to write an execution spec [state transition test](./state_transition.md).

## Example Tests

In this tutorial we will go over [test_block_number] in `test_block_example.py`(https://github.com/ethereum/execution-spec-tests/tree/main/tests/example/test_block_example.py#L19).

It is assumed you have already gone through the state transition test tutorial. Only new concepts will be discussed.

### Smart Contract

A smart contract is defined that is called by each transaction in the test. It stores a pointer to storage at `storage[0]`. When it is called storage cell `0` gets the current block [number](https://www.evm.codes/#43?fork=merge), and the pointer is incremented to the next value.

```python
contract_addr: Account(
    balance=1000000000000000000000,
    code=Yul(
        """
        {
            let next_slot := sload(0)
            sstore(next_slot, number())
            sstore(0, add(next_slot, 1))
        }
        """
    ),
    storage={
        0x00: 0x01,
    },
),
```

### Creating Transactions Using a Generator

The transactions used in this test are nearly identical. Their only difference is the `nonce` value which needs to be incremented.

```python
def tx_generator():
    nonce = 0  # Initial value
    while True:
        tx = Transaction(
            ty=0x0,
            chain_id=0x0,
            nonce=nonce,
            to=contractAddr,
            gas_limit=500000,
            gas_price=10,
        )
        nonce = nonce + 1
        yield tx

tx_generator = tx_generator()
tx1 = next(tx_generator)
tx2 = next(tx_generator)
```

This looks like an infinite loop but it isn't because this is a [generator function](https://wiki.python.org/moin/Generators). When generator encounters the `yield` keyword it returns the value and stops execution, keeping a copy of all the local variables, until it is called again. Hence infinite loops inside a generator are not a problem as long as they include `yield`. This code section is responsible for creating the `Transaction` object and incrementing the `nonce`.

Every time the function `tx_generator()` is called, it returns a new generator with a `nonce` of zero. To increment the `nonce` we need to use the *same* generator. We assign this generator to `tx_generator`.

### Generating Blocks

Each integer in the `tx_per_block` array is the number of transactions in a block. The genesis block is block 0 (no transactions). It follows that we have 2 transactions in block 1, 0 in block two, 4 in block 3, ..., and 50 in block 9.

```python
tx_per_block = [2, 0, 4, 8, 0, 0, 20, 1, 50]
```

The code section that creates the blocks is a bit complex in this test. For some simpler definitions of Block creation you can browse tests within [`test_withdrawals.py`](https://github.com/ethereum/execution-spec-tests/blob/main/tests/withdrawals/test_withdrawals.py).

```python
blocks = map(
    lambda len: Block(
        txs=list(map(lambda x: next(tx_generator), range(len)))
    ),
    tx_per_block,
)
```

We use [`lambda` notation](https://www.w3schools.com/python/python_lambda.asp) to specify short functions. In this case, the function doesn't actually care about its input, it just returns the next transaction from the generator.

```python
lambda x: next(tx_generator)
```

Python uses [`range(n)`](https://www.w3schools.com/python/ref_func_range.asp) to create a list of numbers from `0` to `n-1`. Among other things, it's a simple way to create a list of `n` values.

```python
range(len)
```

The [`map` function](https://www.w3schools.com/python/ref_func_map.asp) runs the function (the first parameter) on every element of the list (the second parameter). Putting together what we know, it means that it runs `next(tx_generator)` `len` times, giving us `len` transactions. We then use [`list`](https://www.w3schools.com/python/python_lists.asp) to turn the transactions into a list that we can provide as the `txs` parameter to the `Block` constructor.

```python
list(map(lambda x: next(tx_generator), range(len)))
```

The outer `lambda` function takes an integer, `len`, and creates a `Block` object with `len` transactions. This function is then run on every value of `tx_per_block` to generate the blocks.

```python
blocks = map(
    lambda len: Block(
        txs=list of len transactions
    ),
    tx_per_block,
)
```

For example, if we had `tx_per_block = [0,2,4]`, we'd get this result:

```python
blocks = [
    Blocks(txs=[]),
    Blocks(txs=[next(tx_generator), next(tx_generator)]),
    Blocks(txs=[next(tx_generator), next(tx_generator), next(tx_generator), next(tx_generator)])        
]
```

### Using the `Transactions` Class

The `Transactions` class is a generator that simplifies generating transactions for the user.

It takes the same arguments as the `Transaction` class, but if any of the fields is an iterable it will create a generator that returns a transaction for each value in the iterable.

`nonce` value is also optional and will be incremented for each transaction automatically.

For example:

```python
txs = Transactions(
    ty=0x0,
    chain_id=0x0,
    to=[contract_addr1, contract_addr2],
    gas_limit=500_000,
    gas_price=10,
)
block1 = Block(txs=txs)
```

This will create a block with two transactions, one to `contract_addr1` and one to `contract_addr2`, while using the same transaction type (`ty`), chain id, gas limit and gas price for both transactions, and also with the proper nonce increment for each transaction.

We can also use multiple lists for different fields:

```python
txs = Transactions(
    ty=0x0,
    chain_id=0x0,
    to=[contract_addr1, contract_addr2],
    gas_limit=[100_000, 500_000],
    gas_price=10,
)
block1 = Block(txs=txs)
```

This will create a block with two transactions, one to `contract_addr1` with a gas limit of 100,000 and one to `contract_addr2` with a gas limit of 500,000.

When any of the iterators is exhausted, the generator will stop.

#### Infinite Iterators

Lists are finite iterators, but we can also use infinite iterators for any of the fields and it will be a valid generator.

We need to be careful to not create an infinite loop, and we can use the `limit` parameter to limit the number of transactions generated per block.

```python
txs = Transactions(
    ty=0x0,
    chain_id=0x0,
    to=(Address(0x100 * i) for i in count(1)),
    gas_limit=500_000,
    gas_price=10,
    limit=10,
)
block1 = Block(txs=txs)
```

In this case we are assigning an infinite generator to the `to` field, because `count(1)` is an infinite iterator that starts at 1 and increments by 1 for each value requested. We are also using the `limit` parameter to limit the number of transactions to 10.

The same generator can be used for multiple blocks, and it will continue from where it left off after the last limit was reached.

```python
txs = Transactions(
    ty=0x0,
    chain_id=0x0,
    to=(Address(0x100 * i) for i in count(1)),
    gas_limit=500_000,
    gas_price=10,
    limit=10,
)
block1 = Block(txs=txs)
block2 = Block(txs=txs)
```

This will create two blocks, each with 10 transactions, each with a different `to` address, starting from `0x100` and incrementing by `0x100` for each transaction, so the first block will have transactions to `0x100`, `0x200`, `0x300`, ..., and the second block will have transactions to `0x1100`, `0x1200`, `0x1300`, ...

We can also create multiple blocks with different number of transactions by passing an iterable to the `limit` parameter.

```python
txs = Transactions(
    ty=0x0,
    chain_id=0x0,
    to=(Address(0x100 * i) for i in count(1)),
    gas_limit=500_000,
    gas_price=10,
    limit=[10, 5, 3],
)
block1 = Block(txs=txs)
block2 = Block(txs=txs)
block3 = Block(txs=txs)
```

This will create three blocks, with 10, 5, and 3 transactions.

The only caveat of using an iterable for the `limit` parameter is that if we exhaust the iterator, the rest of the transaction lists will be empty, but this can be easily solved by using the `cycle` function from the `itertools` module.

```python
txs = Transactions(
    ty=0x0,
    chain_id=0x0,
    to=(Address(0x100 * i) for i in count(1)),
    gas_limit=500_000,
    gas_price=10,
    limit=[10, 5, 3],
)
blocks = [Block(txs=txs) for _ in range(4)]
```

`blocks` will contain four blocks, with 10, 5, 3, and 0 transactions respectively.

### Using the `Blocks` Class

The Blocks generator class can simplify the previous example a bit:

```python
txs = Transactions(
    ty=0x0,
    chain_id=0x0,
    to=(Address(0x100 * i) for i in count(1)),
    gas_limit=500_000,
    gas_price=10,
    limit=[10, 5, 3],
)
blocks = Blocks(txs=txs, limit=3)
```

The change is minimal but it can make the code more readable.

### Other generators

Similar generators exist for `Withdrawal` class as `Withdrawals`, which can be used to create the withdrawals generators.

### Post State

Recall that storage slot 0 retains the value of the next slot that the block number is written into. It starts at one and is incremented after each transaction. Hence it's the total number of transactions plus 1.

```python
storage = {0: sum(tx_per_block) + 1}
```

For every block and transaction within the block, we write the block number and increment the next slot number in storage slot 0. As Python lists are 0 indexed, we must increment the block number by 1.

```python
next_slot = 1
for blocknum in range(len(tx_per_block)):
    for _ in range(tx_per_block[blocknum]):
        storage[next_slot] = blocknum + 1
        next_slot = next_slot + 1
```

Now that the expected storage values are calculated, the post state can be defined and yielded within the `BlockchainTest`, synonymous to the state test example.

```python
post = {contract_addr: Account(storage=storage)}

yield BlockchainTest(
    genesis_environment=env,
    pre=pre,
    blocks=blocks,
    post=post,
)
```

Note that because of the `yield` we could have multiple tests under the same name.

## Conclusion

At this point you should be able to write blockchain tests.
