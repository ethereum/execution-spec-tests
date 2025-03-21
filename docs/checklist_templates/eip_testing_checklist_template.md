# EIP Execution Layer Testing Checklist Template

Depending on the changes introduced by an EIP, the following template is the minimum baseline to guarantee test coverage of the Execution Layer features.

## General

- [ ] Code coverage
    - [ ] Run produced tests against [EELS](https://github.com/ethereum/execution-specs) and verify that line code coverage of new added lines for the EIP is 100%, with only exeptions being unreachable code lines.
    - [ ] Optional - Run against a second client and verify sufficient code coverage over new code added for the EIP.
- [ ] Fuzzing
    - [ ] TBD

## New Opcode

The EIP introduces one or more new opcodes to the EVM.

### Test Vectors

- [ ] Memory expansion
    - [ ] Verify that the opcode execution results in the correct memory expansion, being by offset or size or interaction of both parameters (Size of zero should never result in memory expansion, regardless of offset value). Test at least the following memory expansion sizes
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
        - [ ] Verify opcode behaves as expected when running during the initcode phase of contract creation
            - [ ] Initcode of a contract creating transaction.
            - [ ] Initcode of a contract creating opcode (including itself if opcode creates a contract).
    - [ ] Transaction context
        - [ ] If opcode changes behavior depending on particular transaction properties, test using multiple values for each property.
    - [ ] Block context
        - [ ] If opcode changes behavior depending on particular block properties, test using multiple values for each property.
    - [ ] EOF Container Context
        - [ ] If opcode changes behavior depending on particular EOF container properties, test using multiple values for each property.
- [ ] Return data
    - [ ] Verify proper return data buffer modification if the opcode is meant to interact with it, otherwise verify that the return data buffer is unnaffected
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
    - [ ] If an opcode is terminating, meaning it results in the current call context to end execution, test the following scenarios
        - [ ] Top-level call termination
        - [ ] Sub-level call termination
        - [ ] Initcode termination
- [ ] Out-of-bounds checks
    - [ ] Verify if the opcode has out-of-bounds conditions in its parameters and verify:
        - [ ] Max value for each parameter
        - [ ] Max value + 1 for each parameter
- [ ] Exeptional Abort
    - [ ] Verify behavior that is supposed to cause an exeptional abort, other than stack over or underflow, or out-of-gas errors.
- [ ] Data portion
    - [ ] If an opcode has data portion that affects its behavior, verify checklist items with multiple interesting values (E.g. if data portion size is 1 byte, use at least 0x00, 0x01, 0x7F, 0xFF).
- [ ] Contract creation
    - [ ] Verify contract is created at the expected address given multiple inputs to the opcode parameters.
    - [ ] Verify that contract is not created in case of
        - [ ] Out-of-gas when available gas is less than minimum contract creation stipend.
        - [ ] Contract creation would result in an address collision with an existing contract or eoa-delegated address.
- [ ] Fork transition
    - [ ] Verify that the opcode results in exeptional abort if executed before its activation fork.
    - [ ] Verify that the opcode results in invalid EOF container if attempted to deploy before its activation fork.

### Framework Changes

- [ ] Add opcode to `src/ethereum_test_vm/opcode.py`
- [ ] Add opcode to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## New Precompile

### Test Vectors

- [ ] Call contexts
    - [ ] Normal call to precompile from contract
    - [ ] Delegate call to precompile from contract
    - [ ] Static call to precompile from contract
    - [ ] Code call to precompile from contract
    - [ ] Precompile as transaction entry-point
    - [ ] Call from initcode
        - [ ] Contract creating transaction
        - [ ] Contract creating opcode
- [ ] Inputs
    - [ ] Verify combinations of valid inputs to the precompile
        - [ ] Verify interesting edge values given the precompile functionality.
        - [ ] If precompile performs cryptographic operations, verify behavior on all inputs that have special cryptographic properties.
    - [ ] Verify all zeros input.
    - [ ] Verify 2^N-1 where N is a single or multiple valid bit-lengths.
- [ ] Out-of-bounds checks
    - [ ] Verify if the precompile has out-of-bounds conditions in its inputs and verify:
        - [ ] Max value for each input
        - [ ] Max value + 1 for each input
- [ ] Input Lengths
    - [ ] Zero-length calldata.
    - [ ] Precompile has static-length input
        - [ ] Correct static-length calldata
        - [ ] Calldata too short, where the value represents a correct but truncated input to the precompile.
        - [ ] Calldata too long, where the value represents a correct input to the precompile with padded zeros.
    - [ ] Precompile has dynamic-length input
        - [ ] Verify correct precompile execution for valid lengths, given different inputs.
        - [ ] Calldata too short, given different inputs, where the value represents a correct but truncated input to the precompile.
        - [ ] Calldata too long, given different inputs, where the value represents a correct input to the precompile with padded zeros.
- [ ] Gas usage
    - [ ] Precompile has constant gas usage
        - [ ] Verify exact gas consumption
        - [ ] Verify exact gas consumption minus one results in out-of-gas error.
    - [ ] Precompile has dynamic gas usage
        - [ ] Verify exact gas consumption, given different valid inputs.
        - [ ] Verify exact gas consumption minus one results in out-of-gas error, given different valid inputs.
- [ ] Excessive Gas Cases
    - [ ] Verify spending all block gas in calls to the precompile (100 million gas or more).
- [ ] Fork transition
    - [ ] Verify that calling the precompile before its activation fork results in a valid call even for inputs that are expected to be invalid for the precompile.
    - [ ] Verify that calling the precompile before its activation fork with zero gas results in a valid call.


### Framework Changes

- [ ] Add precompile address to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## New System Contract

### Test Vectors

- [ ] Call contexts
    - [ ] Normal call to system contract from contract
    - [ ] Delegate call to system contract from contract
    - [ ] Static call to system contract from contract
    - [ ] Code call to system contract from contract
    - [ ] System contract as transaction entry-point
    - [ ] Call from initcode
        - [ ] Contract creating transaction
        - [ ] Contract creating opcode
- [ ] Inputs
    - [ ] Verify combinations of valid inputs to the system contract
        - [ ] Verify interesting edge values given the system contract functionality.
    - [ ] Verify all zeros input.
    - [ ] Verify 2^N-1 where N is a single or multiple valid bit-lengths.
- [ ] Out-of-bounds checks
    - [ ] Verify if the system contract has out-of-bounds conditions in its inputs and verify:
        - [ ] Max value for each input
        - [ ] Max value + 1 for each input
- [ ] Input Lengths
    - [ ] Zero-length calldata.
    - [ ] System contract has static-length input
        - [ ] Correct static-length calldata
        - [ ] Calldata too short, where the value represents a correct but truncated input to the contract.
        - [ ] Calldata too long, where the value represents a correct input to the contract with padded zeros.
    - [ ] System contract has dynamic-length input
        - [ ] Verify correct System contract execution for valid lengths, given different inputs.
        - [ ] Calldata too short, given different inputs, where the value represents a correct but truncated input to the contract.
        - [ ] Calldata too long, given different inputs, where the value represents a correct input to the contract with padded zeros.
- [ ] Excessive Gas Cases
    - [ ] If possible, simulate a scenario where the execution of the contract at the end of the block execution by the system address would result in excessive gas usage (100 million gas or more).
    - [ ] Verify spending all block gas in calls to system contract (100 million gas or more).
- [ ] System Contract Deployment
    - [ ] Verify block execution behavior after fork activation if the system contract has not been deployed.
    - [ ] Verify deployment transaction results in the system contract being deployed to the expected address.
- [ ] Contract Variations
    - [ ] Verify execution of the different variations of the contract for different networks (if any) results in the expected behavior
- [ ] Contract Substitution
    - [ ] Substitute the contract to modify its behavior when called by the system address (at the end of the block execution):
        - [ ] Modified return value lengths
        - [ ] Modify emitted logs
- [ ] Fork transition
    - [ ] Verify calling the system contract before its activation fork results in correct behavior (depends on the system contract implementation).

### Framework Changes

- [ ] Add system contract address to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`
- [ ] Add system contract bytecode to the returned value of `pre_allocation_blockchain` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## New Transaction Type

### Test Vectors

- [ ] Intrinsic Gas Costs
    - [ ] Transaction validity: For each new field that affects the intrinsic gas cost of the transaction:
        - [ ] Verify the transaction (and the block it is included in) is valid by providing the exact intrinsic gas as `gas_limit` value to the transaction with all multiple combinations of values to the field.
        - [ ] Verify the transaction (and the block it is included in) is invalid by providing the exact intrinsic gas minus one as `gas_limit` value to the transaction with all multiple combinations of values to the field.
- [ ] Encoding Tests
    - [ ] Verify correct transaction rejection due to incorrect field sizes
- [ ] RPC Tests
    - [ ] * Verify `eth_estimateGas` behavior for different valid combinations of the new transaction type
    - [ ] Verify `eth_sendRawTransaction` using `execute`
- [ ] Out-of-bounds checks
    - [ ] Verify if the transaction has out-of-bounds conditions in its fields and verify:
        - [ ] Max value for each field
        - [ ] Max value + 1 for each field
- [ ] Contract creation
    - [ ] Verify that the transaction can create new contracts, or that it fails to do so if it's not allowed
- [ ] Sender account modifications
    - [ ] Verify that the sender account of the new transaction type transaction has its nonce incremented by one after the transaction is included in a block
    - [ ] Verify that the sender account of the new transaction type transaction has its balance reduced by the correct amount (gas consumed and value) after the transaction is included in a block
- [ ] Fork transition
    - [ ] Verify that a block prior to fork activation where the new transaction type is introduced and containing the new transaction type is invalid.


* Tests must be added to [`execution-apis`](https://github.com/ethereum/execution-apis) repository.

### Framework Changes

- [ ] Modify `transaction_intrinsic_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`, adding the appropriate new fields that the transaction introduced and the logic to the intrinsic gas cost calculation, if any.
- [ ] Add the transaction type number to `tx_types` response in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` (If applicable add also to `contract_creating_tx_types`).


## New Block Header Field

### Test Vectors

- [ ] Genesis value
    - [ ] Verify, if possible, that the value can be set at genesis if the network starting fork is the activation fork, and that clients can consume such genesis.
- [ ] Value behavior
    - [ ] Verify, given multiple initial values, that the value is correctly modified for the current and subsequent blocks as expected, depending on the circumstances that affect the value as defined in the EIP.
- [ ] Fork transition
    - [ ] Verify initial value of the field at the first block of the activation fork.
    - [ ] Verify that a block containing the new header field before the activation of the fork is invalid.
    - [ ] Verify that a block lacking the new header field at the activation of the fork is invalid.


### Framework Changes

**TBD**

## New Block Body Field

### Test Vectors

**TBD**

### Framework Changes

**TBD**

## Gas Cost Changes

### Test Vectors

**TBD**

### Framework Changes

- [ ] Modify `transaction_intrinsic_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects intrinsic gas cost calculation.
- [ ] Modify `transaction_data_floor_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects calldata floor cost.
- [ ] Modify `memory_expansion_gas_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects memory expansion gas cost calculation.
- [ ] Modify `gas_costs` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects specific opcode gas costs.

## Blob Count Changes

### Test Vectors

- [ ] Verify tests in `tests/cancun/eip4844_blobs` were correctly and automatically updated to take into account the new blob count values at the new fork activation block.

### Framework Changes

- [ ] Modify `blob_base_fee_update_fraction`, `target_blobs_per_block`, `max_blobs_per_block` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects any of the values returned by each function.

## New Execution Layer Request

### Test Vectors

- [ ] Cross-Request-Type Interaction
    - [ ] Update `tests/prague/eip7685_general_purpose_el_requests` tests to include the new request type in the tests combinations

### Framework Changes

- [ ] Increment `max_request_type` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` to the new maximum request type number after the EIP is activated.