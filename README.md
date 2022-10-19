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

Every test is a generator function that starts with `test_` located inside the `ethereum_tests` folder structure.

The function _must_ be decorated by only one either of the following decorators:
- test_from
- test_from_until
- test_only

These decorators specify the forks on which the test case is supposed to be run.

They also include further useful information for the `ethereum_test_filler` to read when the generator is being executed to fill the tests.

The test must take only 1 parameter: the fork name.

### Writing your first test

