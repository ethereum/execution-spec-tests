# EIP Execution Layer Testing Checklist Template

Depending on the changes introduced by an EIP, the following template is the minimum baseline to guarantee test coverage of the Execution Layer features.

## General

- [ ] Code coverage
    - [ ] Run produced tests against [EELS](https://github.com/ethereum/execution-specs) and verify that line code coverage of new added lines for the EIP is 100%, with only exeptions being unreachable code lines.
    - [ ] Optional - Run against a second client and verify sufficient code coverage over new code added for the EIP.
- [ ] Fuzzing
    - [ ] TBD

## <!-- id:new_opcode --> New Opcode

The EIP introduces one or more new opcodes to the EVM.

### <!-- id:new_opcode/test --> Test Vectors

- [ ] <!-- id:new_opcode/test/mem_exp --> Memory expansion: Verify that the opcode execution results in the correct memory expansion, being by offset or size or interaction of both parameters (Size of zero should never result in memory expansion, regardless of offset value). Test at least the following memory expansion sizes:
    - [ ] <!-- id:new_opcode/test/mem_exp/zero_bytes --> Zero bytes expansion
        - [ ] <!-- id:new_opcode/test/mem_exp/zero_bytes/zero_offset --> Zero-offset
        - [ ] <!-- id:new_opcode/test/mem_exp/zero_bytes/2_256_minus_one_offset --> 2**256-1 offset
    - [ ] Single byte expansion
    - [ ] 31 bytes expansion
    - [ ] 32 bytes expansion
    - [ ] 33 bytes expansion
    - [ ] 64 bytes expansion
    - [ ] 2**32-1 bytes expansion
    - [ ] 2**32 bytes expansion
    - [ ] 2**64-1 bytes expansion
    - [ ] 2**64 bytes expansion
    - [ ] 2**256-1 bytes expansion
- [ ] Stack
    - [ ] Overflows/Underflows
        - [ ] If the opcode pushes one or more items to the stack, and the opcode pushes more elements than it pops, verify that the opcode execution results in exeptional abort when pushing elements to the stack would result in the stack having more than 1024 elements.
        - [ ] If the opcode pops one or more items to the stack, or it has a minimum stack height of one or more, verify that the opcode execution results in exeptional abort then stack has 1 less item than the minimum stack height expected.
    - [ ] If opcode performs stack operations different of simple pop->push, test for these operations on an asymmetrical stack.
- [ ] Execution context
    - [ ] CALL
    - [ ] STATICCALL
        - [ ] Verify exeptional abort if the opcode is banned for static contexts or if it attempts to modify the code, storage or balance of an account.
        - [ ] Verify subcalls using other opcodes (e.g. CALL, DELEGATECALL, etc) also results in the same exeptional abort behavior.
    - [ ] DELEGATECALL
        - [ ] If the opcode modifies the storage of the account currently executing it, verify that only the account that is delegating execution is the one that has its storage modified.
        - [ ] If the opcode modifies the balance of the account currently executing it, verify that only the account that is delegating execution is the one that has its balance modified.
        - [ ] If the opcode modifies the code of the account currently executing it, verify that only the account that is delegating execution is the one that has its code modified.
    - [ ] CALLCODE
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
    - [ ] Verify proper return data buffer overwriting if the opcode is meant to interact with it, otherwise verify that the return data buffer is unnaffected:
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
    - [ ] If the terminating opcode is meant to rollback the executing call frame, verify the following events are properly rolled back:
        - [ ] Balance changes
        - [ ] Storage changes
        - [ ] Contract creations
        - [ ] Nonce increments
        - [ ] Log events
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
    - [ ] Verify that contract is not created in case of:
        - [ ] Out-of-gas when available gas is less than minimum contract creation stipend.
        - [ ] Creation would result in an address collision with an existing contract or eoa-delegated address.
    - [ ] Verify recursive contract creation using the opcode: Factory contract uses the opcode, and initcode calls back to factory contract.
- [ ] Fork transition
    - [ ] Verify that the opcode results in exeptional abort if executed before its activation fork.
    - [ ] Verify that the opcode results in invalid EOF container if attempted to deploy before its activation fork.
    - [ ] Verify correct opcode behavior at transition block, in the case of opcodes which behavior depends on current or parent block information.

### <!-- id:new_opcode/framework --> Framework Changes

- [ ] <!-- id:new_opcode/framework/opcode.py --> Add opcode to `src/ethereum_test_vm/opcode.py`
- [ ] <!-- id:new_opcode/framework/forks.py --> Add opcode to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_precompile --> New Precompile

### <!-- id:new_precompile/test --> Test Vectors

- [ ] Call contexts
    - [ ] Normal call to precompile from contract
    - [ ] Delegate call to precompile from contract
    - [ ] Static call to precompile from contract
    - [ ] Code call to precompile from contract
    - [ ] Precompile as transaction entry-point
    - [ ] Call from initcode
        - [ ] Contract creating transaction
        - [ ] Contract creating opcode
    - [ ] Set code delegated address (no precompile logic executed)
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
    - [ ] Verify precompile address becomes warm on and after the fork activation block, but not prior.


### <!-- id:new_precompile/framework --> Framework Changes

- [ ] Add precompile address to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_system_contract --> New System Contract

### <!-- id:new_system_contract/test --> Test Vectors

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

### <!-- id:new_system_contract_framework --> Framework Changes

- [ ] Add system contract address to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`
- [ ] Add system contract bytecode to the returned value of `pre_allocation_blockchain` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_transaction_type --> New Transaction Type

### <!-- id:new_transaction_type/test --> Test Vectors

- [ ] Intrinsic Validity
    - [ ] Gas Limit: For each new field that affects the intrinsic gas cost of the transaction:
        - [ ] Verify the transaction (and the block it is included in) is valid by providing the exact intrinsic gas as `gas_limit` value to the transaction with all multiple combinations of values to the field.
        - [ ] Verify the transaction (and the block it is included in) is invalid by providing the exact intrinsic gas minus one as `gas_limit` value to the transaction with all multiple combinations of values to the field.
    - [ ] Max fee per gas:
        - [ ] Verify the transaction (and the block it is included in) is invalid if its max-priority-fee-per-gas value is lower than the max-fee-per-gas.
        - [ ] Verify the transaction (and the block it is included in) is invalid if its max-fee-per-gas value is lower than the blocks base-fee-per-gas.
    - [ ] Chain ID:
        - [ ] Verify the transaction (and the block it is included in) is invalid if its chain-id value does not match the network configuration.
    - [ ] Nonce:
        - [ ] Verify the transaction (and the block it is included in) is invalid if its nonce value does not match the account's current nonce.
    - [ ] To:
        - [ ] Verify the transaction (and the block it is included in) is invalid if the transaction type does not allow contract creation and the to-address field is empty.
    - [ ] Value:
        - [ ] Verify the transaction (and the block it is included in) is invalid if the transaction contains a value of 1 and the account does not contain enough funds to cover the intrinsic transaction cost plus 1.
    - [ ] Data:
        - [ ] Verify the transaction (and the block it is included in) is invalid if the transaction contains enough data so the data floor cost is higher than the intrinsic gas cost and the gas_limit is equal to the intrinsic gas gost.
    - [ ] Sender balance:
        - [ ] Verify the transaction (and the block it is included in) is invalid when the sender account does not have enough balance to cover the gas limit multiplied by the max fee per gas.
- [ ] Signature:
    - [ ] Verify the transaction is correctly rejected if it contains an invalid signature:
        - [ ] V, R, S represent a value that is inside of the field but outside of the curve.
        - [ ] V (yParity) is any of the following invalid values:
            - [ ] `2`
            - [ ] `27` (Type-0 transaction valid value)
            - [ ] `28` (Type-0 transaction valid value)
            - [ ] `35` (Type-0 replay-protected transaction valid value for chain id 1)
            - [ ] `36` (Type-0 replay-protected transaction valid value for chain id 1)
            - [ ] `2**8-1`
        - [ ] R is any of the following invalid values:
            - [ ] `0`
            - [ ] `SECP256K1N-1`
            - [ ] `SECP256K1N`
            - [ ] `SECP256K1N+1`
            - [ ] `2**256-1`
            - [ ] `2**256`
        - [ ] S is any of the following invalid values:
            - [ ] `0`
            - [ ] `SECP256K1N//2-1`
            - [ ] `SECP256K1N//2`
            - [ ] `SECP256K1N//2+1`
            - [ ] `SECP256K1N-1`
            - [ ] `SECP256K1N`
            - [ ] `SECP256K1N+1`
            - [ ] `2**256-1`
            - [ ] `2**256`
            - [ ] `SECP256K1N - S` of a valid signature
- Transaction-Scoped Attributes/Variables
    - Verify attributes that can be read in the EVM from transaction fields.
    - Verify values or variables that are persistent through the execution of the transaction (transient storage, warm/cold accounts).
- [ ] Encoding (RLP, SSZ)
    - [ ] Verify correct transaction rejection due to incorrect field sizes:
        - [ ] Add leading zero byte
        - [ ] Remove single byte from fixed-byte-length fields
    - [ ] If the transaction contains a new field that is a list, verify:
        - [ ] Zero-element list
        - [ ] Max count list
        - [ ] Max count plus one list
    - [ ] Verify correct transaction rejection if the fields particular to the new transaction types are missing
    - [ ] Verify correct transaction rejection if the transaction type contains extra fields
    - [ ] If the transaction contains fields with new serializable types, perform all previous tests on the new type/field
    - [ ] Verify transaction is correctly rejected if the serialized bytes object is truncated
    - [ ] Verify transaction is correctly rejected if the serialized bytes object has extra bytes
- [ ] Out-of-bounds checks
    - [ ] Verify if the transaction has out-of-bounds conditions in its fields and verify:
        - [ ] Max value for each field
        - [ ] Max value + 1 for each field
- [ ] Contract creation
    - [ ] Verify that the transaction can create new contracts if the transaction type supports it.
- [ ] Sender account modifications
    - [ ] Verify that the sender account of the new transaction type transaction has its nonce incremented at least by one after the transaction is included in a block (or more if the transaction type introduces a new mechanic that bumps the nonce by more than one).
    - [ ] Verify that the sender account of the new transaction type transaction has its balance reduced by the correct amount (gas consumed and value) after the transaction is included in a block
- [ ] Fork transition
    - [ ] Verify that a block prior to fork activation where the new transaction type is introduced and containing the new transaction type is invalid.
- [ ] RPC Tests
    - [ ] * Verify `eth_estimateGas` behavior for different valid combinations of the new transaction type
    - [ ] Verify `eth_sendRawTransaction` using `execute`

* Tests must be added to [`execution-apis`](https://github.com/ethereum/execution-apis) repository.

### <!-- id:new_transaction_type/framework --> Framework Changes

- [ ] Modify `transaction_intrinsic_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`, adding the appropriate new fields that the transaction introduced and the logic to the intrinsic gas cost calculation, if any.
- [ ] Add the transaction type number to `tx_types` response in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` (If applicable add also to `contract_creating_tx_types`).


## <!-- id:new_block_header_field --> New Block Header Field

### <!-- id:new_block_header_field/test --> Test Vectors

- [ ] Genesis value
    - [ ] Verify, if possible, that the value can be set at genesis if the network starting fork is the activation fork, and that clients can consume such genesis.
- [ ] Value behavior
    - [ ] Verify, given multiple initial values, that a block is accepted if the value is correctly modified for the current block, depending on the circumstances that affect the value as defined in the EIP.
    - [ ] Verify, given multiple initial values, that a block is rejected if the value is incorrectly modified for the current block, depending on the circumstances that affect the value as defined in the EIP.
- [ ] Fork transition
    - [ ] Verify initial value of the field at the first block of the activation fork.
    - [ ] Verify that a block containing the new header field before the activation of the fork is invalid.
    - [ ] Verify that a block lacking the new header field at the activation of the fork is invalid.


### <!-- id:new_block_header/framework --> Framework Changes

**TBD**

## <!-- id:new_block_body_field --> New Block Body Field

### Test Vectors

**TBD**

### Framework Changes

**TBD**

## <!-- id:gas_cost_changes --> Gas Cost Changes

### Test Vectors

**TBD**

### Framework Changes

- [ ] Modify `transaction_intrinsic_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects intrinsic gas cost calculation.
- [ ] Modify `transaction_data_floor_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects calldata floor cost.
- [ ] Modify `memory_expansion_gas_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects memory expansion gas cost calculation.
- [ ] Modify `gas_costs` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects specific opcode gas costs.

## <!-- id:blob_count_changes --> Blob Count Changes

### <!-- id:blob_count_changes_test --> Test Vectors

- [ ] Verify tests in `tests/cancun/eip4844_blobs` were correctly and automatically updated to take into account the new blob count values at the new fork activation block.

### <!-- id:blob_count_changes_framework --> Framework Changes

- [ ] Modify `blob_base_fee_update_fraction`, `target_blobs_per_block`, `max_blobs_per_block` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects any of the values returned by each function.

## <!-- id:new_execution_layer_request --> New Execution Layer Request

### <!-- id:new_execution_layer_request_test --> Test Vectors

- [ ] Cross-Request-Type Interaction
    - [ ] Update `tests/prague/eip7685_general_purpose_el_requests` tests to include the new request type in the tests combinations

### <!-- id:new_execution_layer_request_framework --> Framework Changes

- [ ] Increment `max_request_type` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` to the new maximum request type number after the EIP is activated.