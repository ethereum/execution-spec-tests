# Types of tests

There are currently two types of tests that can be produced by a test spec:

1. State Tests
2. Blockchain Tests

## State Tests

State tests span a single block and, ideally, a single transaction. For example:

- Test a single opcode behavior.
- Verify opcode gas costs.
- Test interactions between multiple smart contracts.
- Test creation of smart contracts.

## Blockchain Tests

Blockchain tests span multiple blocks which may or may not contain transactions and mainly focus on the block to block effects to the Ethereum state. For example:

- Verify system-level operations such as coinbase balance updates or withdrawals.
- Verify fork transitions.
- Verify blocks with invalid transactions/properties are rejected.

### Fork Transition Tests

There is a special type of blockchain test that is used to test a fork transition. It's not executed for all possible forks, rather it targets exactly the blocks at the point of transition from one evm implementation to the next. This type of test must be marked with the `valid_at_transition_to` marker, for example:

```python
@pytest.mark.valid_at_transition_to("Cancun")
def test_blob_type_tx_pre_fork(
    blockchain_test: BlockchainTestFiller,
    pre: Dict,
    env: Environment,
    blocks: List[Block],
):
    """
    Reject blocks with blobs before blobs fork
    """
```
