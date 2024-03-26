# Debugging Tests

The easiest way to debug tests while writing them is to run the test with the `--traces` flag. This will output the traces of the test, which can be used to understand the behavior of the test and the client.

```bash
fill 'tests/frontier/opcodes/test_dup.py::test_dup[fork_Byzantium-state_test-DUP1]' --traces
```

Depending on the test failure type, a list of relevant traces will be printed.

For example, if the test fails because an expected storage key was not set (`Storage.KeyValueMismatch`), the output will show EVM traces where the storage key was set, or the executing contract returned with error.

```python
{
    1: RelevantTraceContext(
        execution_index=0,
        transaction_index=0,
        transaction_hash='0xf8616cc40f214a4729758189c77720a6b672f29dcb62cd206a49ebacaf00e96f',
        traces=[
            EVMTraceLine(
                pc=34,
                op=128,
                op_name='DUP1',
                gas=78949,
                gas_cost=3,
                mem_size=0,
                stack=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                depth=1,
                refund=0,
                context_address='0x0000000000000000000000000000000000000100'
            ),
            EVMTraceLine(
                pc=35,
                op=96,
                op_name='PUSH1',
                gas=78946,
                gas_cost=3,
                mem_size=0,
                stack=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 16],
                depth=1,
                refund=0,
                context_address='0x0000000000000000000000000000000000000100'
            ),
            EVMTraceLine(
                pc=37,
                op=85,
                op_name='SSTORE',
                gas=78943,
                gas_cost=20000,
                mem_size=0,
                stack=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 16, 0],
                depth=1,
                refund=0,
                context_address='0x0000000000000000000000000000000000000100'
            )
        ],
        description='SSTORE event on address 0x0000000000000000000000000000000000000100 and key 0x0'
    ),
    2: RelevantTraceContext(
        execution_index=0,
        transaction_index=0,
        transaction_hash='0xf8616cc40f214a4729758189c77720a6b672f29dcb62cd206a49ebacaf00e96f',
        traces=[
            EVMTraceLine(
                pc=44,
                op=96,
                op_name='PUSH1',
                gas=18937,
                gas_cost=3,
                mem_size=0,
                stack=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                depth=1,
                refund=0,
                context_address='0x0000000000000000000000000000000000000100'
            ),
            EVMTraceLine(
                pc=46,
                op=85,
                op_name='SSTORE',
                gas=18934,
                gas_cost=20000,
                mem_size=0,
                stack=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 3],
                depth=1,
                refund=0,
                context_address='0x0000000000000000000000000000000000000100'
            ),
            EVMCallFrameExit(from_address='0x0000000000000000000000000000000000000100', output=b'', gas_used=79000, error='out of gas')
        ],
        description='Exit frame from address 0x0000000000000000000000000000000000000100 with error'
    )
}
```

In this example, the test failed because the storage key `0x0` was not set. The traces show that the storage key was indeed set to `0x10`, but later the contract ran out of gas.
