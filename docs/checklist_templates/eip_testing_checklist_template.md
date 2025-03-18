# EIP Execution Layer Testing Checklist Templates

Depending on the changes introduced by an EIP, the following template is the minimum baseline to guarantee test coverage of the Execution Layer features:

## New Opcode

The EIP introduces one or more new opcodes to the EVM.

- [ ] Memory expansion
    - [ ] Verify that the opcode execution results in the correct memory expansion, being by offset or size or interaction of both parameters (Size of zero should never result in memory expansion, regardless of offset value). Test at least the following memory expansion sizes:
        - [ ] Zero bytes expansion
        - [ ] Single byte expansion
        - [ ] 31 bytes expansion
        - [ ] 32 bytes expansion
        - [ ] 33 bytes expansion
        - [ ] 64 or more bytes expansion
- [ ] Stack over/underflows
    - [ ] If the opcode pushes one or more items to the stack, and the opcode pushes more elements than it pops, verify that the opcode execution results in exeptional abort when pushing elements to the stack would result in the stack having more than 1024 elements.
    - [ ] If the opcode pops one or more items to the stack, or it has a minimum stack height of one or more, verify that the opcode execution results in exeptional abort then stack has 1 less item than the minimum stack height expected.
- [ ] Execution context
    - [ ] Normal call
    - [ ] Static call
        - [ ] Verify exeptional abort if the opcode attempts to modify the code, storage or balance of an account
    - [ ] Delegate call
        - [ ] If the opcode modifies the storage of the account currently executing it, verify that only the account that is delegating execution is the one that has its storage modified.
        - [ ] If the opcode modifies the balance of the account currently executing it, verify that only the account that is delegating execution is the one that has its balance modified.
        - [ ] If the opcode modifies the code of the account currently executing it, verify that only the account that is delegating execution is the one that has its code modified.
    - [ ] Code call
    - [ ] Initcode
        - [ ] Verify opcode behaves as expected when running during the initcode phase of contract creation:
            - [ ] Initcode of a contract creating transaction.
            - [ ] Initcode of a contract creating opcode (including itself if opcode creates a contract).
    - [ ] Transaction context
        - [ ] If opcode changes behavior depending on particular transaction properties, test using multiple values for each property.
    - [ ] Block context
        - [ ] If opcode changes behavior depending on particular block properties, test using multiple values for each property.
    - [ ] EOF Container Context
        - [ ] If opcode changes behavior depending on particular EOF container properties, test using multiple values for each property.
- [ ] Return data
    - [ ] Verify proper return data buffer modification if the opcode is meant to interact with it, otherwise verify that the return data buffer is unnaffected:
        - [ ] At current call context.
        - [ ] At parent call context.
- [ ] Gas usage
    - [ ] Normal operation gas usage
        - [ ] Verify gas affectation of each parameter value consumed by the opcode.
    - [ ] Memory expansion
        - [ ] Verify that the memory expansion correctly follows the gas calculation
    - [ ] Out-of-gas during opcode execution
        - [ ] Verify that attempting to execute the opcode when gas available is 1 less than the required gas results in exeptional abort.
    - [ ] Out-of-gas during memory expansion
        - [ ] Verify that the expansion of memory can result in out-of-gas exeptional abort.
- [ ] Terminating opcode
    - [ ] If an opcode is terminating, meaning it results in the current call context to end execution, test the following scenarios:
        - [ ] Top-level call termination
        - [ ] Sub-level call termination
        - [ ] Initcode termination
- [ ] Exeptional Abort
    - [ ] Verify behavior that is supposed to cause an exeptional abort, other than stack over or underflow, or out-of-gas errors.
- [ ] Data portion
    - [ ] If an opcode has data portion that affects its behavior, verify checklist items with multiple interesting values (E.g. if data portion size is 1 byte, use at least 0x00, 0x01, 0x7F, 0xFF).
- [ ] Contract creation
    - [ ] Verify contract is created at the expected address given multiple inputs to the opcode parameters.
    - [ ] Verify that contract is not created in case of:
        - [ ] Out-of-gas when available gas is less than minimum contract creation stipend.
        - [ ] Contract creation would result in an address collision with an existing contract or eoa-delegated address.
