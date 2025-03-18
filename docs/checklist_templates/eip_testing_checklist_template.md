# EIP Execution Layer Testing Checklist Templates

Depending on the changes introduced by an EIP, the following template is the minimum baseline to guarantee test coverage of the Execution Layer features:

## General

- [ ] Code coverage:
    - [ ] Run produced tests against [EELS](https://github.com/ethereum/execution-specs) and verify that line code coverage of new added lines for the EIP is 100%, with only exeptions being unreachable code lines.
    - [ ] Optional - Run against a second client and verify sufficient code coverage over new code added for the EIP.
- [ ] Fuzzing:
    - [ ] TBD

## New Opcode

The EIP introduces one or more new opcodes to the EVM.

### Test Vectors

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
- [ ] Fork transition
    - [ ] Verify that the opcode results in exeptional abort if executed before its activation fork.
    - [ ] Verify that the opcode results in invalid EOF container if attempted to deploy before its activation fork.

### Framework Changes

- [ ] Add opcode to `src/ethereum_test_vm/opcode.py`
- [ ] Add opcode to relevant methods in the fork it is introduced in `src/ethereum_test_forks/forks/forks.py`

## New Precompile

### Test Vectors

- [ ] Call contexts:
    - [ ] Normal call to precompile from contract
    - [ ] Delegate call to precompile from contract
    - [ ] Static call to precompile from contract
    - [ ] Code call to precompile from contract
    - [ ] Precompile as transaction entry-point
    - [ ] Call from initcode
        - [ ] Contract creating transaction
        - [ ] Contract creating opcode
- [ ] Inputs
    - [ ] Verify combinations of valid inputs to the precompile:
        - [ ] Verify interesting edge values given the precompile functionality.
        - [ ] If precompile performs cryptographic operations, verify behavior on all inputs that have special cryptographic properties.
    - [ ] Verify all zeros input.
    - [ ] Verify 2^N-1 where N is a single or multiple valid bit-lengths.
- [ ] Input lengths:
    - [ ] Zero-length calldata.
    - [ ] Precompile has static-length input:
        - [ ] Correct static-length calldata
        - [ ] Calldata too short, where the value represents a correct but truncated input to the contract.
        - [ ] Calldata too long, where the value represents a correct input to the contract with padded zeros.
    - [ ] Precompile has dynamic-length input:
        - [ ] Verify correct precompile execution for valid lengths, given different inputs.
        - [ ] Calldata too short, given different inputs, where the value represents a correct but truncated input to the contract.
        - [ ] Calldata too long, given different inputs, where the value represents a correct input to the contract with padded zeros.
- [ ] Gas usage:
    - [ ] Precompile has constant gas usage
        - [ ] Verify exact gas consumption
        - [ ] Verify exact gas consumption minus one results in out-of-gas error.
    - [ ] Precompile has dynamic gas usage
        - [ ] Verify exact gas consumption, given different valid inputs.
        - [ ] Verify exact gas consumption minus one results in out-of-gas error, given different valid inputs.
- [ ] Fork transition:
    - [ ] Verify that calling the precompile before its activation fork results in a valid call even for inputs that are expected to be invalid for the precompile.
    - [ ] Verify that calling the precompile before its activation fork with zero gas results in a valid call.


### Framework Changes

- [ ] Add precompile address to relevant methods in the fork it is introduced in `src/ethereum_test_forks/forks/forks.py`

## New System Contract

### Test Vectors

### Framework Changes

## New Block Header Field

### Test Vectors

### Framework Changes

## New Block Body Field

### Test Vectors

### Framework Changes

## New Transaction Type

### Test Vectors

### Framework Changes

## Intrinsic Gas Cost Changes

### Test Vectors

### Framework Changes
