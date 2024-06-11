
# Ethereum EVM Transition Tool Specs

Each client is encouraged to implement the `evm t8n` tool, which is used to generate tests by calculating the simple state transition.

## Inputs

### Pre-Allocation

The pre-allocation is a JSON object that contains the initial state of the EVM environment. It is used to initialize the EVM state before the transactions are executed.

#### JSON Schema

See [types/Alloc](./types.md#alloc).

### Environment

The environment is a JSON object that contains the EVM environment information. It is used to initialize the EVM environment on which the transactions are executed.

#### JSON Schema

See [types/Environment](./types.md#environment).

### Transactions

The transactions are a JSON object that contains the list of transactions to be executed on the EVM environment.

#### JSON Schema

See [types/Transaction](./types.md#transaction).

## Outputs

### Post-Allocation

The post-allocation is a JSON object that contains the final state of the EVM environment after the transactions are executed.

#### JSON Schema

See [types/Alloc](./types.md#alloc).

### Result

The result is a JSON object that contains the result of the state transition. It includes the transaction logs, and the rejected transactions.

#### JSON Schema

See [types/Result](./types.md#result).

## Parameters

### Fork

The fork is a string that specifies the fork rules and all EIPs included in it for the state transition.

#### JSON Schema

See [types/Forks](./types.md#forks).

### Reward

Overwrite the fork mining reward rule when finalizing the transactions list.

#### JSON Schema

```yaml
type: int
```

### Chain ID

Require txs chainid to be equal to this value when parsing txs data.

#### JSON Schema

```yaml
type: int
```
