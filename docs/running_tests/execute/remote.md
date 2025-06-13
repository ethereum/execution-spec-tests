# Running Test on a Live Remote Network

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

The `execute remote` and `execute hive` commands first creates a random sender account from which all required test accounts will be deployed and funded, and this account is funded by sweeping (by default) this "seed" account.

The sweep amount can be configured by setting the `--seed-account-sweep-amount` flag:

```bash
--seed-account-sweep-amount "1000 ether"
```

Once the sender account is funded, the command will start executing tests one by one by sending the transactions from this account to the network.

Test transactions are not sent from the main sender account though, they are sent from a different unique account that is created for each test (accounts returned by `pre.fund_eoa`).

### Use with Parallel Execution

If the `execute` is run using the `-n=N` flag (respectively `--sim-parallelism=N`), n>1, the tests will be executed in parallel, and each process will have its own separate sender account, so the amount that is swept from the seed account is divided by the number of processes, and this has to be taken into account when setting the sweep amount and also when funding the seed account.

After finishing each test the command will check the remaining balance of all accounts and will attempt to recover the funds back to the sender account, and at the end of all tests, the remaining balance of the sender account will be swept back to the seed account.

There are instances where it will be impossible to recover the funds back from a test, for example, funds that are sent to a contract that has no built-in way to send them back, the funds will be stuck in the contract and they will not be recoverable.
