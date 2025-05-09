# EIP Execution Layer Testing Checklist Template

Depending on the changes introduced by an EIP, the following template is the minimum baseline to guarantee test coverage of the Execution Layer features.

## General

- [ ] Code coverage
    - [ ] Run produced tests against [EELS](https://github.com/ethereum/execution-specs) and verify that line code coverage of new added lines for the EIP is 100%, with only exceptions being unreachable code lines.
    - [ ] Run coverage on the test code itself (as a basic logic sanity check), i.e., `uv run fill --cov tests`.
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
    - [ ] 2**256-1 bytes expansion (Should always result in Out-of-gas)
- [ ] Stack
    - [ ] Overflow/Underflow
        - [ ] If the opcode pushes one or more items to the stack, and the opcode pushes more elements than it pops, verify that the opcode execution results in exceptional abort when pushing elements to the stack would result in the stack having more than 1024 elements.
        - [ ] If the opcode pops one or more items to the stack, or it has a minimum stack height of one or more (e.g. Op.DUPN requires a minimum amount of elements in the stack even when it does not pop any element from it), verify that the opcode execution results in exceptional abort then stack has 1 less item than the minimum stack height expected.
    - [ ] If opcode performs stack operations more complex than simple pop/push (e.g. the opcode has a data portion that specifies a variable to access a specific stack element), perform the following test combinations:
        - [ ] Operation on different stack heights:
            - [ ] Zero (Potential stack-underflow)
            - [ ] Odd
            - [ ] Even
        - [ ] For each variable `n` of the opcode that accesses the nth stack item, test `n` being:
            - [ ] Top stack item
            - [ ] Bottom stack item
            - [ ] Middle stack item
- [ ] Execution context
    - [ ] CALL
    - [ ] STATICCALL
        - [ ] Verify exceptional abort if the opcode is banned for static contexts or if it attempts to modify the code, storage or balance of an account.
        - [ ] If the opcode is completely banned from static contexts, verify that even when its inputs would not cause any account modification, the opcode still results in exceptional abort of the execution (e.g. Op.PAY with zero value, or Op.SSTORE to the value it already has in the storage).
        - [ ] Verify sub-calls using other opcodes (e.g. CALL, DELEGATECALL, etc) also results in the same exceptional abort behavior.
    - [ ] DELEGATECALL
        - [ ] If the opcode modifies the storage of the account currently executing it, verify that only the account that is delegating execution is the one that has its storage modified.
        - [ ] If the opcode modifies the balance of the account currently executing it, verify that only the account that is delegating execution is the one that has its balance modified.
        - [ ] If the opcode modifies the code of the account currently executing it, verify that only the account that is delegating execution is the one that has its code modified.
    - [ ] CALLCODE
    - [ ] Initcode
        - [ ] Verify opcode behaves as expected when running during the initcode phase of contract creation
            - [ ] Initcode of a contract creating transaction.
            - [ ] Initcode of a contract creating opcode (including itself if opcode creates a contract).
        - [ ] Verify opcode behavior on re-entry using the same initcode and same address (e.g. CREATE2->REVERT->CREATE2).
    - [ ] Set-code delegated account: Verify opcode operations are applied to the set-code account and do not affect the address that is the target of the delegation.
    - [ ] Transaction context: If opcode changes behavior depending on particular transaction properties, test using multiple values for each property.
    - [ ] Block context: If opcode changes behavior depending on particular block properties, test using multiple values for each property.
- [ ] Return data
    - [ ] Verify proper return data buffer overwriting if the opcode is meant to interact with it, otherwise verify that the return data buffer is unaffected:
        - [ ] At current call context.
        - [ ] At parent call context.
- [ ] Gas usage
    - [ ] Normal operation gas usage: Verify gas affectation of each parameter value consumed by the opcode.
    - [ ] Memory expansion: Verify that the memory expansion correctly follows the gas calculation
    - [ ] Out-of-gas during opcode execution: Verify that attempting to execute the opcode when gas available is 1 less than the required gas results in exceptional abort.
    - [ ] Out-of-gas during memory expansion: Verify that the expansion of memory can result in out-of-gas exceptional abort.
    - [ ] Order-of-operations: If the opcode requires different gas stipends for other operations (e.g. contract creation, cold/warm account access), create one case for each operation (ideally independent of each other) and the following cases for each:
        - [ ] Success using the exact amount of gas required for the stipend.
        - [ ] OOG with a 1-gas-difference from the gas required for the stipend.
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
- [ ] Exceptional Abort: Verify behavior that is supposed to cause an exceptional abort, other than stack over or underflow, or out-of-gas errors.
- [ ] Data portion: If an opcode has data portion that affects its behavior, verify checklist items with multiple interesting values (E.g. if data portion size is 1 byte, use at least 0x00, 0x01, 0x7F, 0xFF).
- [ ] Contract creation
    - [ ] Verify contract is created at the expected address given multiple inputs to the opcode parameters.
    - [ ] Verify that contract is not created in case of:
        - [ ] Out-of-gas when available gas is less than minimum contract creation stipend.
        - [ ] Creation would result in an address collision with an existing contract or EOA-delegated address.
    - [ ] Verify recursive contract creation using the opcode: Factory contract uses the opcode, and initcode calls back to factory contract.
- [ ] Fork transition
    - [ ] Verify that the opcode results in exceptional abort if executed before its activation fork.
    - [ ] Verify correct opcode behavior at transition block, in the case of opcodes which behavior depends on current or parent block information.

### <!-- id:new_opcode/framework --> Framework Changes

- [ ] <!-- id:new_opcode/framework/opcode.py --> Add opcode to `src/ethereum_test_vm/opcode.py`
- [ ] <!-- id:new_opcode/framework/forks.py --> Add opcode to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_precompile --> New Precompile

The EIP introduces one or more new precompiles.

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
        - [ ] If precompile performs cryptographic operations, verify behavior on all inputs that have special cryptographic properties (e.g. infinity points as inputs, or input values that result in infinity points returned).
    - [ ] Verify all zeros input.
    - [ ] Verify 2^N-1 where N is a single or multiple valid bit-lengths.
    - [ ] Verify combinations of invalid inputs to the precompile.
        - [ ] Inputs that fail specific mathematical or cryptographic validity checks.
        - [ ] Inputs that are malformed/corrupted.
- [ ] Value Transfer
    - [ ] If the precompile requires a minimum value with the calls to it, either constant or depending on a formula, verify:
        - [ ] Calls with the required value amount minus one, expect failure.
        - [ ] Calls with the exact required amount, expect success.
        - [ ] Calls with extra value than the required amount, expect success.
    - [ ] If the system contract does not require a minimum value embedded in the calls to it, verify sending value does not cause an exception, unless otherwise specified by the EIP.
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
- [ ] Excessive Gas Cases: Verify spending all block gas in calls to the precompile (Use `Environment().gas_limit` as max amount).
- [ ] Fork transition
    - [ ] Verify that calling the precompile before its activation fork results in a valid call even for inputs that are expected to be invalid for the precompile.
    - [ ] Verify that calling the precompile before its activation fork with zero gas results in a valid call.
    - [ ] Verify precompile address becomes warm on and after the fork activation block, but not prior.

### <!-- id:new_precompile/framework --> Framework Changes

- [ ] Add precompile address to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_precompile --> Removed Precompile

The EIP removes one or more precompiles from the existing list of precompiles.

### <!-- id:new_precompile/test --> Test Vectors

- [ ] Fork boundary
    - [ ] Verify that the precompile remains operational up until the last block before the fork is active, and behaves as an account with empty code afterwards.
    - [ ] Verify the account is warm up until the last block before the fork is active, and becomes cold afterwards.

### <!-- id:new_precompile/framework --> Framework Changes

- [ ] Remove the precompile address from relevant methods in the fork where the EIP is removed in `src/ethereum_test_forks/forks/forks.py`

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
    - [ ] Verify interesting boundary values given the system contract functionality.
    - [ ] Verify all zeros input.
    - [ ] Verify 2^N-1 where N is a single or multiple valid bit-lengths.
    - [ ] Verify combinations of invalid inputs to the precompile.
        - [ ] Inputs that fail specific validity checks.
        - [ ] Inputs that are malformed/corrupted.
- [ ] Value Transfer
    - [ ] If the system contract requires a minimum value with the calls to it, either constant or depending on a formula, verify:
        - [ ] Calls with the required value amount minus one, expect failure.
        - [ ] Calls with the exact required amount, expect success.
        - [ ] Calls with extra value than the required amount, expect success.
    - [ ] If the system contract does not require a minimum value embedded in the calls to it, verify sending value does not cause an exception, unless otherwise specified by the EIP.
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
    - [ ] Verify block execution behavior after fork activation if the system contract has not been deployed (Depending on the EIP, block could be invalid).
    - [ ] Verify deployment transaction results in the system contract being deployed to the expected address.
- [ ] Contract Variations
    - [ ] Verify execution of the different variations of the contract for different networks (if any) results in the expected behavior,
    - [ ] Verify execution of a variation that causes an exception.
    - [ ] Verify execution of a variation that consumes:
        - [ ] 30,000,000 million gas exactly, execution should be successful.
        - [ ] 30,000,001 million gas exactly, execution should fail.
- [ ] Contract Substitution: Substitute the contract to modify its behavior when called by the system address (at the end of the block execution):
    - [ ] Modified return value lengths
    - [ ] Modify emitted logs
- [ ] Fork transition: Verify calling the system contract before its activation fork results in correct behavior (depends on the system contract implementation).

### <!-- id:new_system_contract_framework --> Framework Changes

- [ ] Add system contract address to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`
- [ ] Add system contract bytecode to the returned value of `pre_allocation_blockchain` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_transaction_type --> New Transaction Type

### <!-- id:new_transaction_type/test --> Test Vectors

- [ ] Intrinsic Validity
    - [ ] Gas Limit: For each new field that affects the intrinsic gas cost of the transaction:
        - [ ] Verify the transaction (and the block it is included in) is valid by providing the exact intrinsic gas as `gas_limit` value to the transaction with all multiple combinations of values to the field.
        - [ ] Verify the transaction (and the block it is included in) is invalid by providing the exact intrinsic gas minus one as `gas_limit` value to the transaction with all multiple combinations of values to the field.
    - [ ] Max fee per gas: Verify the transaction (and the block it is included in) is invalid if:
        - [ ] Its max-priority-fee-per-gas value is lower than the max-fee-per-gas.
        - [ ] Its max-fee-per-gas value is lower than the blocks base-fee-per-gas.
    - [ ] Chain ID: Verify the transaction (and the block it is included in) is invalid if its chain-id value does not match the network configuration.
    - [ ] Nonce: Verify the transaction (and the block it is included in) is invalid if its nonce value does not match the account's current nonce.
    - [ ] To: Verify the transaction (and the block it is included in) is invalid if the transaction type does not allow contract creation and the to-address field is empty.
    - [ ] Value: Verify the transaction (and the block it is included in) is invalid if the transaction contains a value of 1 and the account does not contain enough funds to cover the intrinsic transaction cost plus 1.
    - [ ] Data: Verify the transaction (and the block it is included in) is invalid if the transaction contains enough data so the data floor cost is higher than the intrinsic gas cost and the gas_limit is equal to the intrinsic gas cost.
    - [ ] Sender balance: Verify the transaction (and the block it is included in) is invalid when the sender account does not have enough balance to cover the gas limit multiplied by the max fee per gas.
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
    - Verify attributes specific to the new transaction type that can be read in the EVM behave correctly on older transaction types.
    - Verify values or variables that are persistent through the execution of the transaction (transient storage, warm/cold accounts):
        - Persist throughout the entire transaction.
        - Reset on subsequent transactions in the same block.
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
    - [ ] Verify transaction is correctly rejected if the serialized bytes object is truncated
    - [ ] Verify transaction is correctly rejected if the serialized bytes object has extra bytes
    - [ ] If the transaction contains fields with new serializable types, perform all previous tests on the new type/field, plus:
        - [ ] Verify transaction rejection if the serializable field is incorrectly encoded as bytes instead of using the correct encoding.
- [ ] Out-of-bounds checks: Verify if the transaction has out-of-bounds conditions in its fields and verify:
    - [ ] Max value for each field
    - [ ] Max value + 1 for each field
- [ ] Contract creation: Verify that the transaction can create new contracts if the transaction type supports it.
- [ ] Sender account modifications
    - [ ] Verify that the sender account of the new transaction type transaction has its nonce incremented at least by one after the transaction is included in a block (or more if the transaction type introduces a new mechanism that bumps the nonce by more than one).
    - [ ] Verify that the sender account of the new transaction type transaction has its balance reduced by the correct amount (gas consumed and value) at the start of execution (e.g. using Op.BALANCE).
- [ ] Block Level Interactions
    - [ ] Verify the new transaction type and the following accept/reject behavior depending on interactions with the block gas limit:
        - [ ] New transaction type is the single transaction in the block:
            - [ ] Rejected if `tx.gas_limit == block.gas_limit + 1`
            - [ ] Accepted if `tx.gas_limit == block.gas_limit`
        - [ ] New transaction type is the last transaction of a block with two transactions:
            - [ ] Accepted if `block.txs[0].gas_used + block.txs[1].gas_limit == block.gas_limit`
            - [ ] Rejected if `(block.txs[0].gas_used + block.txs[1].gas_limit == block.gas_limit + 1) and (block.txs[0].gas_used < block.gas_limit)`
    - [ ] Verify a transaction of the new type is rejected if its gas limit exceeds the [EIP-7825](https://eips.ethereum.org/EIPS/eip-7825) gas limit for the current fork.
    - [ ] Verify a block with all transactions types including the new type is executed correctly.
- [ ] Fork transition: Verify that a block prior to fork activation where the new transaction type is introduced and containing the new transaction type is invalid.
- [ ] RPC Tests
    - [ ] *Verify `eth_estimateGas` behavior for different valid combinations of the new transaction type
    - [ ] Verify `eth_sendRawTransaction` using `execute`

*Tests must be added to [`execution-apis`](https://github.com/ethereum/execution-apis) repository.

### <!-- id:new_transaction_type/framework --> Framework Changes

- [ ] Modify `transaction_intrinsic_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`, adding the appropriate new fields that the transaction introduced and the logic to the intrinsic gas cost calculation, if any.
- [ ] Add the transaction type number to `tx_types` response in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` (If applicable add also to `contract_creating_tx_types`).

## <!-- id:new_block_header_field --> New Block Header Field

### <!-- id:new_block_header_field/test --> Test Vectors

- [ ] Genesis value: Verify, if possible, that the value can be set at genesis if the network starting fork is the activation fork, and that clients can consume such genesis.
- [ ] Value behavior
    - [ ] Verify, given multiple initial values, that a block is accepted if the value is the correct expected for the current block, depending on the circumstances that affect the value as defined in the EIP.
    - [ ] Verify, given multiple initial values, that a block is rejected if the value is modified (using `block.rlp_modifier`) to an incorrect value for the current block, depending on the circumstances that affect the value as defined in the EIP.
- [ ] Fork transition
    - [ ] Verify initial value of the field at the first block of the activation fork.
    - [ ] Verify that a block containing the new header field before the activation of the fork is invalid.
    - [ ] Verify that a block lacking the new header field at the activation of the fork is invalid.

### <!-- id:new_block_header/framework --> Framework Changes

- [ ] Add the new header field to the relevant objects:
    - [ ] `ethereum_test_fixtures.FixtureHeader`
    - [ ] `ethereum_test_fixtures.FixtureExecutionPayload`
    - [ ] `ethereum_test_specs.Header`
- [ ] Add the appropriate `header_*_required` fork method to `BaseFork` in `ethereum_test_forks`.

## <!-- id:new_block_body_field --> New Block Body Field

### Test Vectors

- [ ] Value behavior
    - [ ] Verify, given multiple initial values, that a block is accepted if the value is the correct expected for the current block, depending on the circumstances that affect the value as defined in the EIP.
    - [ ] Verify, given multiple initial values, that a block is rejected if the value is modified (using appropriate `block`) to an incorrect value for the current block, depending on the circumstances that affect the value as defined in the EIP.
- [ ] Fork transition
    - [ ] Verify that a block containing the new block body field before the activation of the fork is invalid.
    - [ ] Verify that a block lacking the new block  field at the activation of the fork is invalid.

### Framework Changes

- [ ] Value behavior
    - [ ] Verify, given multiple initial values, that a block is accepted if the value is correctly modified for the current block, depending on the circumstances that affect the value as defined in the EIP.
    - [ ] Verify, given multiple initial values, that a block is rejected if the value is incorrectly modified for the current block, depending on the circumstances that affect the value as defined in the EIP.
- [ ] Add the new body field to the relevant objects:
    - [ ] `ethereum_test_fixtures.FixtureBlockBase`
    - [ ] `ethereum_test_fixtures.FixtureEngineNewPayload`
    - [ ] `ethereum_test_specs.Block`
- [ ] Modify `ethereum_test_specs.BlockchainTest` filling behavior to account for the new block field.

## <!-- id:gas_cost_changes --> Gas Cost Changes

### Test Vectors

- [ ] Gas Usage: Measure and store the gas usage during the operations affected by the gas cost changes and verify the updated behavior.
- [ ] Out-of-gas: Verify the operations affected by the gas cost changes can run out-of-gas with the updated limits.
- [ ] Fork transition: Verify gas costs are:
    - [ ] Unaffected before the fork activation block.
    - [ ] Updated on and after fork activation block.

### Framework Changes

- [ ] Modify `transaction_intrinsic_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects intrinsic gas cost calculation.
- [ ] Modify `transaction_data_floor_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects calldata floor cost.
- [ ] Modify `memory_expansion_gas_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects memory expansion gas cost calculation.
- [ ] Modify `gas_costs` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects specific opcode gas costs.

## <!-- id:gas_refunds_changes --> Gas Refunds Changes

### Test Vectors

- [ ] Refund calculation: Verify that the refund does not exceed `gas_used // MAX_REFUND_QUOTIENT` (`MAX_REFUND_QUOTIENT==5` in [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529)) in the following scenarios:
    - [ ] `refund == gas_used // MAX_REFUND_QUOTIENT + 1`
    - [ ] `refund == gas_used // MAX_REFUND_QUOTIENT`
    - [ ] `refund == gas_used // MAX_REFUND_QUOTIENT - 1`
- [ ] Exceptional Abort:
    - [ ] If the operation causing the refund can be reverted, verify the refund is not applied if the following cases:
        - [ ] `REVERT`
        - [ ] Out-of-gas
        - [ ] Invalid opcode
        - [ ] `REVERT` of an upper call frame
    - [ ] If the operation causing the refund cannot be reverted (e.g. in the case of a transaction-scoped operation such as authorization refunds in EIP-7702), verify the refund is still applied even in the following cases:
        - [ ] `REVERT` at the top call frame
        - [ ] Out-of-gas at the top call frame
        - [ ] Invalid opcode at the top call frame
- [ ] Cross-Functional Test: Verify the following tests are updated to support the new type of refunds:
    - [ ] `tests/prague/eip7623_increase_calldata_cost/test_refunds.py`

### Framework Changes

N/A

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
