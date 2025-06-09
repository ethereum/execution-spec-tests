# Executing Tests on Local Networks or Hive

@ethereum/execution-spec-tests is capable of running tests on local networks or on Hive with a few considerations. This page describes how to do so.

## The `execute` command and `pytest` plugin

The `execute` command is capable of parse and execute all tests in the `tests` directory, collect the transactions it requires, send them to a client connected to a network, wait for the network to include them in a block and, finally, check the resulting state of the involved smart-contracts against the expected state to validate the behavior of the clients.

It will not check for the state of the network itself, only the state of the smart-contracts, accounts and transactions involved in the tests, so it is possible that the network becomes unstable or forks during the execution of the tests, but this will not be detected by the command.

The way this is achieved is by using a pytest plugin that will collect all the tests the same way as the fill plugin does, but instead of compiling the transactions and sending them as a batch to the transition tool, they are prepared and sent to the client one by one.

Before sending the actual test transactions to the client, the plugin uses a special pre-allocation object that collects the contracts and EOAs that are used by the tests and, instead of pre-allocating them in a dictionary as the fill plugin does, it sends transactions to deploy contracts or fund the accounts for them to be available in the network.

The pre-allocation object requires a seed account with funds available in the network to be able to deploy contracts and fund accounts. In the case of a live remote network, the seed account needs to be provided via a command-line parameter, but in the case of a local hive network, the seed account is automatically created and funded by the plugin via the genesis file.

At the end of each test, the plugin will also check the remaining balance of all accounts and will attempt to automatically recover the funds back to the seed account in order to execute the following tests.

## Differences between the `fill` and `execute` plugins

The test execution with the `execute` plugin is different from the `fill` plugin in a few ways:

### EOA and Contract Addresses

The `fill` plugin will pre-allocate all the accounts and contracts that are used in the tests, so the addresses of the accounts and contracts will be known before the tests are executed, Further more, the test contracts will start from the same address on different tests, so there are collisions on the account addresses used across different tests. This is not the case with the `execute` plugin, as the accounts and contracts are deployed on the fly, from sender keys that are randomly generated and therefore are different in each execution.

Reasoning behind the random generation of the sender keys is that one can execute the same test multiple times in the same network and the plugin will not fail because the accounts and contracts are already deployed.

### Transactions Gas Price

The `fill` plugin will use a fixed and minimum gas price for all the transactions it uses for testing, but this is not possible with the `execute` plugin, as the gas price is determined by the current state of the network.

At the moment, the `execute` plugin does not query the client for the current gas price, but instead uses a fixed increment to the gas price in order to avoid the transactions to be stuck in the mempool.

## Running Tests on a Hive Single-Client Local Network

Tests can be executed on a local hive-controlled single-client network by running the `execute hive` command.

This command requires hive to be running in `--dev` mode:

```bash
./hive --dev --client go-ethereum
```

This will start hive in dev mode with the single go-ethereum client available for launching tests.

By default, the hive server will be listening on `http://127.0.0.1:3000`, but this can be changed by setting the `--dev.addr` flag:

```bash
./hive --dev --client go-ethereum --dev.addr http://127.0.0.1:5000
```

The `execute hive` can now be executed to connect to the hive server, but the environment variable `HIVE_SIMULATOR` needs to be set to the address of the hive server:

```bash
export HIVE_SIMULATOR=http://127.0.0.1:3000
```

And the tests can be executed with:

```bash
uv run execute hive --fork=Cancun
```

This will execute all available tests in the `tests` directory on the `Cancun` fork by connecting to the hive server running on `http://127.0.0.1:3000` and launching a single client with the appropriate genesis file.

The genesis file is passed to the client with the appropriate configuration for the fork schedule, system contracts and pre-allocated seed account.

All tests will be executed in the same network, in the same client, and serially, but when the `-n auto` parameter is passed to the command, the tests can also be executed in parallel.

One important feature of the `execute hive` command is that, since there is no consensus client running in the network, the command drives the chain by the use of the Engine API to prompt the execution client to generate new blocks and include the transactions in them.

## Running Test on a Live Remote Network

Tests can be executed on a live remote network by running the `execute remote` command.

The command requires the `--fork` flag which must match the fork that is currently active in the network (fork transition tests are not supported yet).

The `execute remote` command requires to be pointed to an RPC endpoint of a client that is connected to the network, which can be specified by using the `--rpc-endpoint` flag:

```bash
uv run execute remote --fork=Prague --rpc-endpoint=https://rpc.endpoint.io
```

Another requirement is that the command is provided with a seed account that has funds available in the network to deploy contracts and fund accounts. This can be done by setting the `--rpc-seed-key` flag:

```bash
uv run execute remote --fork=Prague --rpc-endpoint=https://rpc.endpoint.io --rpc-seed-key 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
```

The value needs to be a private key that is used to sign the transactions that deploy the contracts and fund the accounts.

One last requirement is that the `--rpc-chain-id` flag is set to the chain id of the network that is being tested:

```bash
uv run execute remote --fork=Prague --rpc-endpoint=https://rpc.endpoint.io --rpc-seed-key 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f --rpc-chain-id 12345
```

The `execute remote` command will connect to the client via the RPC endpoint and will start executing every test in the `./tests` folder in the same way as the `execute hive` command, but instead of using the Engine API to generate blocks, it will send the transactions to the client via the RPC endpoint.

It is recommended to only run a subset of the tests when executing on a live network. To do so, a path to a specific test can be provided to the command:

```bash
uv run execute remote --fork=Prague --rpc-endpoint=https://rpc.endpoint.io --rpc-seed-key 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f --rpc-chain-id 12345 ./tests/prague/eip7702_set_code_tx/test_set_code_txs.py::test_set_code_to_sstore
```

## `execute` Command Test Execution

After executing `execute hive` or `execute remote` the command will first create a random sender account from which all required test accounts will be deployed and funded, and this account is funded by sweeping (by default) the seed account.

The sweep amount can be configured by setting the `--seed-account-sweep-amount` flag:

```bash
--seed-account-sweep-amount "1000 ether"
```

Once the sender account is funded, the command will start executing tests one by one by sending the transactions from this account to the network.

Test transactions are not sent from the main sender account though, they are sent from a different unique account that is created for each test (accounts returned by `pre.fund_eoa`).

If the command is run using the `-n` flag, the tests will be executed in parallel, and each process will have its own separate sender account, so the amount that is swept from the seed account is divided by the number of processes, so this has to be taken into account when setting the sweep amount and also when funding the seed account.

After finishing each test the command will check the remaining balance of all accounts and will attempt to recover the funds back to the sender account, and at the end of all tests, the remaining balance of the sender account will be swept back to the seed account.

There are instances where it will be impossible to recover the funds back from a test, for example, funds that are sent to a contract that has no built-in way to send them back, the funds will be stuck in the contract and they will not be recoverable.
