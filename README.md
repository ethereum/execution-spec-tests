# Testing Tools

This repository provides tools and libraries for generating cross-client
Ethereum tests.

## Quick Start

Relies on Python `3.10.0`, `geth` `v1.10.13`, `solc` `v0.8.5` or later. 

```console
$ git clone https://github.com/lightclient/testing-tools
$ cd testing-tools
$ pip install -e .
$ tf --output="fixtures"
```

## Overview 

### `ethereum_test`

The `ethereum_test` package provides primitives and helpers to allow developers
to easily test the consensus logic of Ethereum clients. 

### `ethereum_test_filler`

The `ethereum_test_filler` pacakge is a CLI application that recursively searches
a given directory for Python modules that export test filler functions generated
using `ethereum_test`. It then processes the fillers using the transition tool
and the block builder tool, and writes the resulting fixture to file.

### `evm_block_builder`

This is a wrapper around the [block builder][b11r] (b11r) tool.

### `evm_transition_tool`

This is a wrapper around the [transaction][t8n] (t8n) tool.

[t8n]: https://github.com/ethereum/go-ethereum/tree/master/cmd/evm
[b11r]: https://github.com/ethereum/go-ethereum/pull/23843


### `ethereum_tests`

Contains all the Ethereum consensus tests available in this repository.

Each subdirectory is a test category, which can contain multiple python source
files.

Each file can in turn contain multiple functions, which each can generate
multiple test vectors.

Every test function is a generator which must `yield` one or many `StateTest` 
objects during its runtime.

The `StateTest` object contains the following attributes pertaining to a single
test vector:

- env: Environment object which describes the global state of the blockchain
    before the test starts.
- pre: Pre-State containing the information of all Ethereum accounts that exist
    before any transaction is executed.
- post: Post-State containing the information of all Ethereum accounts that are
    created or modified after all transactions are executed.
- txs: All transactions which are executed during the test vector runtime.

The test vector's generator function _must_ be decorated by only one of the
following decorators:
- test_from
- test_from_until
- test_only

These decorators specify the forks on which the test vector is supposed to run.

They also include further useful information for the `ethereum_test_filler` to
read when the generator is being executed to fill the tests.

The test vector function must take only 1 parameter: the fork name.

### Writing your first test

