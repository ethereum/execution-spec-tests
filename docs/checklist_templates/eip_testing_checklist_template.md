# EIP Execution Layer Testing Checklist Template

Depending on the changes introduced by an EIP, the following template is the minimum baseline to guarantee test coverage of the Execution Layer features.

## <!-- id:general --> General

- [ ] <!-- id:general/code_coverage --> Code coverage
    - [ ] <!-- id:general/code_coverage/eels --> Run produced tests against [EELS](https://github.com/ethereum/execution-specs) and verify that line code coverage of new added lines for the EIP is 100%, with only exceptions being unreachable code lines.
    - [ ] <!-- id:general/code_coverage/test_coverage --> Run coverage on the test code itself (as a basic logic sanity check), i.e., `uv run fill --cov tests`.
    - [ ] <!-- id:general/code_coverage/second_client --> Optional - Run against a second client and verify sufficient code coverage over new code added for the EIP.
- [ ] <!-- id:general/fuzzing --> Fuzzing

## <!-- id:new_opcode --> New Opcode

The EIP introduces one or more new opcodes to the EVM.

### <!-- id:new_opcode/test --> Test Vectors

- [ ] <!-- id:new_opcode/test/mem_exp --> Memory expansion: Verify that the opcode execution results in the correct memory expansion, being by offset or size or interaction of both parameters (Size of zero should never result in memory expansion, regardless of offset value). Test at least the following memory expansion sizes:
    - [ ] <!-- id:new_opcode/test/mem_exp/zero_bytes --> Zero bytes expansion
        - [ ] <!-- id:new_opcode/test/mem_exp/zero_bytes/zero_offset --> Zero-offset
        - [ ] <!-- id:new_opcode/test/mem_exp/zero_bytes/max_offset --> 2**256-1 offset
    - [ ] <!-- id:new_opcode/test/mem_exp/single_byte --> Single byte expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/31_bytes --> 31 bytes expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/32_bytes --> 32 bytes expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/33_bytes --> 33 bytes expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/64_bytes --> 64 bytes expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/2_32_minus_one_bytes --> 2**32-1 bytes expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/2_32_bytes --> 2**32 bytes expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/2_64_minus_one_bytes --> 2**64-1 bytes expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/2_64_bytes --> 2**64 bytes expansion
    - [ ] <!-- id:new_opcode/test/mem_exp/2_256_minus_one_bytes --> 2**256-1 bytes expansion (Should always result in Out-of-gas)
- [ ] <!-- id:new_opcode/test/stack --> Stack
    - [ ] <!-- id:new_opcode/test/stack/overflow --> Overflow: If the opcode pushes one or more items to the stack, and the opcode pushes more elements than it pops, verify that the opcode execution results in exceptional abort when pushing elements to the stack would result in the stack having more than 1024 elements.
    - [ ] <!-- id:new_opcode/test/stack/underflow --> Underflow: If the opcode pops one or more items to the stack, or it has a minimum stack height of one or more (e.g. Op.DUPN requires a minimum amount of elements in the stack even when it does not pop any element from it), verify that the opcode execution results in exceptional abort then stack has 1 less item than the minimum stack height expected.
    - [ ] <!-- id:new_opcode/test/stack/complex_operations --> If opcode performs stack operations more complex than simple pop/push (e.g. the opcode has a data portion that specifies a variable to access a specific stack element), perform the following test combinations:
        - [ ] <!-- id:new_opcode/test/stack/complex_operations/stack_heights --> Operation on different stack heights:
            - [ ] <!-- id:new_opcode/test/stack/complex_operations/stack_heights/zero --> Zero (Potential stack-underflow)
            - [ ] <!-- id:new_opcode/test/stack/complex_operations/stack_heights/odd --> Odd
            - [ ] <!-- id:new_opcode/test/stack/complex_operations/stack_heights/even --> Even
        - [ ] <!-- id:new_opcode/test/stack/complex_operations/variable_n --> For each variable `n` of the opcode that accesses the nth stack item, test `n` being:
            - [ ] <!-- id:new_opcode/test/stack/complex_operations/variable_n/top --> Top stack item
            - [ ] <!-- id:new_opcode/test/stack/complex_operations/variable_n/bottom --> Bottom stack item
            - [ ] <!-- id:new_opcode/test/stack/complex_operations/variable_n/middle --> Middle stack item
- [ ] <!-- id:new_opcode/test/execution_context --> Execution context
    - [ ] <!-- id:new_opcode/test/execution_context/call --> `CALL`
    - [ ] <!-- id:new_opcode/test/execution_context/staticcall --> `STATICCALL`
        - [ ] <!-- id:new_opcode/test/execution_context/staticcall/ban_check --> Verify exceptional abort if the opcode is banned for static contexts or if it attempts to modify the code, storage or balance of an account.
        - [ ] <!-- id:new_opcode/test/execution_context/staticcall/ban_no_modification --> If the opcode is completely banned from static contexts, verify that even when its inputs would not cause any account modification, the opcode still results in exceptional abort of the execution (e.g. Op.PAY with zero value, or Op.SSTORE to the value it already has in the storage).
        - [ ] <!-- id:new_opcode/test/execution_context/staticcall/sub_calls --> Verify sub-calls using other opcodes (e.g. `CALL`, `DELEGATECALL`, etc) also results in the same exceptional abort behavior.
    - [ ] <!-- id:new_opcode/test/execution_context/delegatecall --> `DELEGATECALL`
        - [ ] <!-- id:new_opcode/test/execution_context/delegatecall/storage --> If the opcode modifies the storage of the account currently executing it, verify that only the account that is delegating execution is the one that has its storage modified.
        - [ ] <!-- id:new_opcode/test/execution_context/delegatecall/balance --> If the opcode modifies the balance of the account currently executing it, verify that only the account that is delegating execution is the one that has its balance modified.
        - [ ] <!-- id:new_opcode/test/execution_context/delegatecall/code --> If the opcode modifies the code of the account currently executing it, verify that only the account that is delegating execution is the one that has its code modified.
    - [ ] <!-- id:new_opcode/test/execution_context/callcode --> `CALLCODE`
    - [ ] <!-- id:new_opcode/test/execution_context/initcode --> Initcode
        - [ ] <!-- id:new_opcode/test/execution_context/initcode/behavior --> Verify opcode behaves as expected when running during the initcode phase of contract creation
            - [ ] <!-- id:new_opcode/test/execution_context/initcode/behavior/tx --> Initcode of a contract creating transaction.
            - [ ] <!-- id:new_opcode/test/execution_context/initcode/behavior/opcode --> Initcode of a contract creating opcode (including itself if opcode creates a contract).
        - [ ] <!-- id:new_opcode/test/execution_context/initcode/reentry --> Verify opcode behavior on re-entry using the same initcode and same address (e.g. CREATE2->REVERT->CREATE2).
    - [ ] <!-- id:new_opcode/test/execution_context/set_code --> Set-code delegated account: Verify opcode operations are applied to the set-code account and do not affect the address that is the target of the delegation.
    - [ ] <!-- id:new_opcode/test/execution_context/tx_context --> Transaction context: If opcode changes behavior depending on particular transaction properties, test using multiple values for each property.
    - [ ] <!-- id:new_opcode/test/execution_context/block_context --> Block context: If opcode changes behavior depending on particular block properties, test using multiple values for each property.
- [ ] <!-- id:new_opcode/test/return_data --> Return data
    - [ ] <!-- id:new_opcode/test/return_data/buffer --> Verify proper return data buffer overwriting if the opcode is meant to interact with it, otherwise verify that the return data buffer is unaffected:
        - [ ] <!-- id:new_opcode/test/return_data/buffer/current --> At current call context.
        - [ ] <!-- id:new_opcode/test/return_data/buffer/parent --> At parent call context.
- [ ] <!-- id:new_opcode/test/gas_usage --> Gas usage
    - [ ] <!-- id:new_opcode/test/gas_usage/normal --> Normal operation gas usage: Verify gas affectation of each parameter value consumed by the opcode.
    - [ ] <!-- id:new_opcode/test/gas_usage/memory_expansion --> Memory expansion: Verify that the memory expansion correctly follows the gas calculation
    - [ ] <!-- id:new_opcode/test/gas_usage/out_of_gas_execution --> Out-of-gas during opcode execution: Verify that attempting to execute the opcode when gas available is 1 less than the required gas results in exceptional abort.
    - [ ] <!-- id:new_opcode/test/gas_usage/out_of_gas_memory --> Out-of-gas during memory expansion: Verify that the expansion of memory can result in out-of-gas exceptional abort.
    - [ ] <!-- id:new_opcode/test/gas_usage/order_of_operations --> Order-of-operations: If the opcode requires different gas stipends for other operations (e.g. contract creation, cold/warm account access), create one case for each operation (ideally independent of each other) and the following cases for each:
        - [ ] <!-- id:new_opcode/test/gas_usage/order_of_operations/exact --> Success using the exact amount of gas required for the stipend.
        - [ ] <!-- id:new_opcode/test/gas_usage/order_of_operations/oog --> OOG with a 1-gas-difference from the gas required for the stipend.
- [ ] <!-- id:new_opcode/test/terminating --> Terminating opcode
    - [ ] <!-- id:new_opcode/test/terminating/scenarios --> If an opcode is terminating, meaning it results in the current call context to end execution, test the following scenarios
        - [ ] <!-- id:new_opcode/test/terminating/scenarios/top_level --> Top-level call termination
        - [ ] <!-- id:new_opcode/test/terminating/scenarios/sub_level --> Sub-level call termination
        - [ ] <!-- id:new_opcode/test/terminating/scenarios/initcode --> Initcode termination
    - [ ] <!-- id:new_opcode/test/terminating/rollback --> If the terminating opcode is meant to rollback the executing call frame, verify the following events are properly rolled back:
        - [ ] <!-- id:new_opcode/test/terminating/rollback/balance --> Balance changes
        - [ ] <!-- id:new_opcode/test/terminating/rollback/storage --> Storage changes
        - [ ] <!-- id:new_opcode/test/terminating/rollback/contracts --> Contract creations
        - [ ] <!-- id:new_opcode/test/terminating/rollback/nonce --> Nonce increments
        - [ ] <!-- id:new_opcode/test/terminating/rollback/logs --> Log events
- [ ] <!-- id:new_opcode/test/out_of_bounds --> Out-of-bounds checks
    - [ ] <!-- id:new_opcode/test/out_of_bounds/verify --> Verify if the opcode has out-of-bounds conditions in its parameters and verify:
        - [ ] <!-- id:new_opcode/test/out_of_bounds/verify/max --> Max value for each parameter
        - [ ] <!-- id:new_opcode/test/out_of_bounds/verify/max_plus_one --> Max value + 1 for each parameter
- [ ] <!-- id:new_opcode/test/exceptional_abort --> Exceptional Abort: Verify behavior that is supposed to cause an exceptional abort, other than stack over or underflow, or out-of-gas errors.
- [ ] <!-- id:new_opcode/test/data_portion --> Data portion: If an opcode has data portion that affects its behavior, verify checklist items with multiple interesting values (E.g. if data portion size is 1 byte, use at least 0x00, 0x01, 0x7F, 0xFF).
- [ ] <!-- id:new_opcode/test/contract_creation --> Contract creation
    - [ ] <!-- id:new_opcode/test/contract_creation/address --> Verify contract is created at the expected address given multiple inputs to the opcode parameters.
    - [ ] <!-- id:new_opcode/test/contract_creation/failure --> Verify that contract is not created in case of:
        - [ ] <!-- id:new_opcode/test/contract_creation/failure/oog --> Out-of-gas when available gas is less than minimum contract creation stipend.
        - [ ] <!-- id:new_opcode/test/contract_creation/failure/collision --> Creation would result in an address collision with an existing contract or EOA-delegated address.
    - [ ] <!-- id:new_opcode/test/contract_creation/recursive --> Verify recursive contract creation using the opcode: Factory contract uses the opcode, and initcode calls back to factory contract.
- [ ] <!-- id:new_opcode/test/fork_transition --> Fork transition
    - [ ] <!-- id:new_opcode/test/fork_transition/before --> Verify that the opcode results in exceptional abort if executed before its activation fork.
    - [ ] <!-- id:new_opcode/test/fork_transition/at --> Verify correct opcode behavior at transition block, in the case of opcodes which behavior depends on current or parent block information.

### <!-- id:new_opcode/framework --> Framework Changes

- [ ] <!-- id:new_opcode/framework/opcode.py --> Add opcode to `src/ethereum_test_vm/opcode.py`
- [ ] <!-- id:new_opcode/framework/forks.py --> Add opcode to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_precompile --> New Precompile

The EIP introduces one or more new precompiles.

### <!-- id:new_precompile/test --> Test Vectors

- [ ] <!-- id:new_precompile/test/call_contexts --> Call contexts
    - [ ] <!-- id:new_precompile/test/call_contexts/normal --> `CALL`
    - [ ] <!-- id:new_precompile/test/call_contexts/delegate --> `DELEGATECALL`
    - [ ] <!-- id:new_precompile/test/call_contexts/static --> `STATICCALL`
        - [ ] <!-- id:new_precompile/test/call_contexts/static/stateful --> If the precompile is stateful, meaning calling it affects its storage, verify that using `STATICCALL` to call it results in exceptional abort.
    - [ ] <!-- id:new_precompile/test/call_contexts/callcode --> `CALLCODE`
    - [ ] <!-- id:new_precompile/test/call_contexts/tx_entry --> Precompile as transaction entry-point
    - [ ] <!-- id:new_precompile/test/call_contexts/initcode --> Call from Initcode
        - [ ] <!-- id:new_precompile/test/call_contexts/initcode/tx --> Contract creating transaction
        - [ ] <!-- id:new_precompile/test/call_contexts/initcode/opcode --> Contract creating opcode
    - [ ] <!-- id:new_precompile/test/call_contexts/set_code --> Set code delegated address (no precompile logic executed)
- [ ] <!-- id:new_precompile/test/inputs --> Inputs
    - [ ] <!-- id:new_precompile/test/inputs/valid --> Verify combinations of valid inputs to the precompile
        - [ ] <!-- id:new_precompile/test/inputs/valid/edge --> Verify interesting edge values given the precompile functionality.
        - [ ] <!-- id:new_precompile/test/inputs/valid/crypto --> If precompile performs cryptographic operations, verify behavior on all inputs that have special cryptographic properties (e.g. infinity points as inputs, or input values that result in infinity points returned).
    - [ ] <!-- id:new_precompile/test/inputs/all_zeros --> Verify all zeros input.
    - [ ] <!-- id:new_precompile/test/inputs/max_values --> Verify 2^N-1 where N is a single or multiple valid bit-lengths.
    - [ ] <!-- id:new_precompile/test/inputs/invalid --> Verify combinations of invalid inputs to the precompile.
        - [ ] <!-- id:new_precompile/test/inputs/invalid/crypto --> Inputs that fail specific mathematical or cryptographic validity checks.
        - [ ] <!-- id:new_precompile/test/inputs/invalid/corrupted --> Inputs that are malformed/corrupted.
- [ ] <!-- id:new_precompile/test/value_transfer --> Value Transfer
    - [ ] <!-- id:new_precompile/test/value_transfer/minimum --> If the precompile requires a minimum value with the calls to it, either constant or depending on a formula, verify:
        - [ ] <!-- id:new_precompile/test/value_transfer/minimum/under --> Calls with the required value amount minus one, expect failure.
        - [ ] <!-- id:new_precompile/test/value_transfer/minimum/exact --> Calls with the exact required amount, expect success.
        - [ ] <!-- id:new_precompile/test/value_transfer/minimum/over --> Calls with extra value than the required amount, expect success.
    - [ ] <!-- id:new_precompile/test/value_transfer/no_minimum --> If the system contract does not require a minimum value embedded in the calls to it, verify sending value does not cause an exception, unless otherwise specified by the EIP.
- [ ] <!-- id:new_precompile/test/out_of_bounds --> Out-of-bounds checks
    - [ ] <!-- id:new_precompile/test/out_of_bounds/verify --> Verify if the precompile has out-of-bounds conditions in its inputs and verify:
        - [ ] <!-- id:new_precompile/test/out_of_bounds/verify/max --> Max value for each input
        - [ ] <!-- id:new_precompile/test/out_of_bounds/verify/max_plus_one --> Max value + 1 for each input
- [ ] <!-- id:new_precompile/test/input_lengths --> Input Lengths
    - [ ] <!-- id:new_precompile/test/input_lengths/zero --> Zero-length calldata.
    - [ ] <!-- id:new_precompile/test/input_lengths/static --> Precompile has static-length input
        - [ ] <!-- id:new_precompile/test/input_lengths/static/correct --> Correct static-length calldata
        - [ ] <!-- id:new_precompile/test/input_lengths/static/too_short --> Calldata too short, where the value represents a correct but truncated input to the precompile.
        - [ ] <!-- id:new_precompile/test/input_lengths/static/too_long --> Calldata too long, where the value represents a correct input to the precompile with padded zeros.
    - [ ] <!-- id:new_precompile/test/input_lengths/dynamic --> Precompile has dynamic-length input
        - [ ] <!-- id:new_precompile/test/input_lengths/dynamic/valid --> Verify correct precompile execution for valid lengths, given different inputs.
        - [ ] <!-- id:new_precompile/test/input_lengths/dynamic/too_short --> Calldata too short, given different inputs, where the value represents a correct but truncated input to the precompile.
        - [ ] <!-- id:new_precompile/test/input_lengths/dynamic/too_long --> Calldata too long, given different inputs, where the value represents a correct input to the precompile with padded zeros.
- [ ] <!-- id:new_precompile/test/gas_usage --> Gas usage
    - [ ] <!-- id:new_precompile/test/gas_usage/constant --> Precompile has constant gas usage
        - [ ] <!-- id:new_precompile/test/gas_usage/constant/exact --> Verify exact gas consumption
        - [ ] <!-- id:new_precompile/test/gas_usage/constant/oog --> Verify exact gas consumption minus one results in out-of-gas error.
    - [ ] <!-- id:new_precompile/test/gas_usage/dynamic --> Precompile has dynamic gas usage
        - [ ] <!-- id:new_precompile/test/gas_usage/dynamic/exact --> Verify exact gas consumption, given different valid inputs.
        - [ ] <!-- id:new_precompile/test/gas_usage/dynamic/oog --> Verify exact gas consumption minus one results in out-of-gas error, given different valid inputs.
- [ ] <!-- id:new_precompile/test/excessive_gas --> Excessive Gas Cases: Verify spending all block gas in calls to the precompile (Use `Environment().gas_limit` as max amount).
- [ ] <!-- id:new_precompile/test/fork_transition --> Fork transition
    - [ ] <!-- id:new_precompile/test/fork_transition/before --> Verify that calling the precompile before its activation fork results in a valid call even for inputs that are expected to be invalid for the precompile.
    - [ ] <!-- id:new_precompile/test/fork_transition/zero_gas --> Verify that calling the precompile before its activation fork with zero gas results in a valid call.
    - [ ] <!-- id:new_precompile/test/fork_transition/warm --> Verify precompile address becomes warm on and after the fork activation block, but not prior.

### <!-- id:new_precompile/framework --> Framework Changes

- [ ] <!-- id:new_precompile/framework/fork_methods --> Add precompile address to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:removed_precompile --> Removed Precompile

The EIP removes one or more precompiles from the existing list of precompiles.

### <!-- id:removed_precompile/test --> Test Vectors

- [ ] <!-- id:removed_precompile/test/fork_boundary --> Fork boundary
    - [ ] <!-- id:removed_precompile/test/fork_boundary/operational --> Verify that the precompile remains operational up until the last block before the fork is active, and behaves as an account with empty code afterwards.
    - [ ] <!-- id:removed_precompile/test/fork_boundary/warm --> Verify the account is warm up until the last block before the fork is active, and becomes cold afterwards.

### <!-- id:removed_precompile/framework --> Framework Changes

- [ ] <!-- id:removed_precompile/framework/fork_methods --> Remove the precompile address from relevant methods in the fork where the EIP is removed in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_system_contract --> New System Contract

### <!-- id:new_system_contract/test --> Test Vectors

- [ ] <!-- id:new_system_contract/test/call_contexts --> Call contexts
    - [ ] <!-- id:new_system_contract/test/call_contexts/normal --> `CALL`
    - [ ] <!-- id:new_system_contract/test/call_contexts/delegate --> `DELEGATECALL`
    - [ ] <!-- id:new_system_contract/test/call_contexts/static --> `STATICCALL`
        - [ ] <!-- id:new_precompile/test/call_contexts/static/stateful --> If the system contract is stateful, meaning calling it affects its storage, verify that using `STATICCALL` to call it results in exceptional abort.
    - [ ] <!-- id:new_system_contract/test/call_contexts/callcode --> `CALLCODE`
    - [ ] <!-- id:new_system_contract/test/call_contexts/tx_entry --> System contract as transaction entry-point
    - [ ] <!-- id:new_system_contract/test/call_contexts/initcode --> Call from Initcode
        - [ ] <!-- id:new_system_contract/test/call_contexts/initcode/tx --> Contract creating transaction
        - [ ] <!-- id:new_system_contract/test/call_contexts/initcode/opcode --> Contract creating opcode
- [ ] <!-- id:new_system_contract/test/inputs --> Inputs
    - [ ] <!-- id:new_system_contract/test/inputs/valid --> Verify combinations of valid inputs to the system contract
    - [ ] <!-- id:new_system_contract/test/inputs/boundary --> Verify interesting boundary values given the system contract functionality.
    - [ ] <!-- id:new_system_contract/test/inputs/all_zeros --> Verify all zeros input.
    - [ ] <!-- id:new_system_contract/test/inputs/max_values --> Verify 2^N-1 where N is a single or multiple valid bit-lengths.
    - [ ] <!-- id:new_system_contract/test/inputs/invalid --> Verify combinations of invalid inputs to the precompile.
        - [ ] <!-- id:new_system_contract/test/inputs/invalid/checks --> Inputs that fail specific validity checks.
        - [ ] <!-- id:new_system_contract/test/inputs/invalid/corrupted --> Inputs that are malformed/corrupted.
- [ ] <!-- id:new_system_contract/test/value_transfer --> Value Transfer
    - [ ] <!-- id:new_system_contract/test/value_transfer/minimum --> If the system contract requires a minimum value with the calls to it, either constant or depending on a formula, verify:
        - [ ] <!-- id:new_system_contract/test/value_transfer/minimum/under --> Calls with the required value amount minus one, expect failure.
        - [ ] <!-- id:new_system_contract/test/value_transfer/minimum/exact --> Calls with the exact required amount, expect success.
        - [ ] <!-- id:new_system_contract/test/value_transfer/minimum/over --> Calls with extra value than the required amount, expect success.
    - [ ] <!-- id:new_system_contract/test/value_transfer/no_minimum --> If the system contract does not require a minimum value embedded in the calls to it, verify sending value does not cause an exception, unless otherwise specified by the EIP.
- [ ] <!-- id:new_system_contract/test/out_of_bounds --> Out-of-bounds checks
    - [ ] <!-- id:new_system_contract/test/out_of_bounds/verify --> Verify if the system contract has out-of-bounds conditions in its inputs and verify:
        - [ ] <!-- id:new_system_contract/test/out_of_bounds/verify/max --> Max value for each input
        - [ ] <!-- id:new_system_contract/test/out_of_bounds/verify/max_plus_one --> Max value + 1 for each input
- [ ] <!-- id:new_system_contract/test/input_lengths --> Input Lengths
    - [ ] <!-- id:new_system_contract/test/input_lengths/zero --> Zero-length calldata.
    - [ ] <!-- id:new_system_contract/test/input_lengths/static --> System contract has static-length input
        - [ ] <!-- id:new_system_contract/test/input_lengths/static/correct --> Correct static-length calldata
        - [ ] <!-- id:new_system_contract/test/input_lengths/static/too_short --> Calldata too short, where the value represents a correct but truncated input to the contract.
        - [ ] <!-- id:new_system_contract/test/input_lengths/static/too_long --> Calldata too long, where the value represents a correct input to the contract with padded zeros.
    - [ ] <!-- id:new_system_contract/test/input_lengths/dynamic --> System contract has dynamic-length input
        - [ ] <!-- id:new_system_contract/test/input_lengths/dynamic/valid --> Verify correct System contract execution for valid lengths, given different inputs.
        - [ ] <!-- id:new_system_contract/test/input_lengths/dynamic/too_short --> Calldata too short, given different inputs, where the value represents a correct but truncated input to the contract.
        - [ ] <!-- id:new_system_contract/test/input_lengths/dynamic/too_long --> Calldata too long, given different inputs, where the value represents a correct input to the contract with padded zeros.
- [ ] <!-- id:new_system_contract/test/excessive_gas --> Excessive Gas Cases
    - [ ] <!-- id:new_system_contract/test/excessive_gas/simulation --> If possible, simulate a scenario where the execution of the contract at the end of the block execution by the system address would result in excessive gas usage (100 million gas or more).
    - [ ] <!-- id:new_system_contract/test/excessive_gas/block_gas --> Verify spending all block gas in calls to system contract (100 million gas or more).
- [ ] <!-- id:new_system_contract/test/deployment --> System Contract Deployment
    - [ ] <!-- id:new_system_contract/test/deployment/missing --> Verify block execution behavior after fork activation if the system contract has not been deployed (Depending on the EIP, block could be invalid).
    - [ ] <!-- id:new_system_contract/test/deployment/address --> Verify deployment transaction results in the system contract being deployed to the expected address.
- [ ] <!-- id:new_system_contract/test/contract_variations --> Contract Variations
    - [ ] <!-- id:new_system_contract/test/contract_variations/networks --> Verify execution of the different variations of the contract for different networks (if any) results in the expected behavior,
    - [ ] <!-- id:new_system_contract/test/contract_variations/exception --> Verify execution of a variation that causes an exception.
    - [ ] <!-- id:new_system_contract/test/contract_variations/gas_limits --> Verify execution of a variation that consumes:
        - [ ] <!-- id:new_system_contract/test/contract_variations/gas_limits/success --> 30,000,000 million gas exactly, execution should be successful.
        - [ ] <!-- id:new_system_contract/test/contract_variations/gas_limits/failure --> 30,000,001 million gas exactly, execution should fail.
- [ ] <!-- id:new_system_contract/test/contract_substitution --> Contract Substitution: Substitute the contract to modify its behavior when called by the system address (at the end of the block execution):
    - [ ] <!-- id:new_system_contract/test/contract_substitution/return_lengths --> Modified return value lengths
    - [ ] <!-- id:new_system_contract/test/contract_substitution/logs --> Modify emitted logs
- [ ] <!-- id:new_system_contract/test/fork_transition --> Fork transition: Verify calling the system contract before its activation fork results in correct behavior (depends on the system contract implementation).

### <!-- id:new_system_contract/framework --> Framework Changes

- [ ] <!-- id:new_system_contract/framework/fork_methods --> Add system contract address to relevant methods in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`
- [ ] <!-- id:new_system_contract/framework/pre_allocation --> Add system contract bytecode to the returned value of `pre_allocation_blockchain` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`

## <!-- id:new_transaction_type --> New Transaction Type

### <!-- id:new_transaction_type/test --> Test Vectors

- [ ] <!-- id:new_transaction_type/test/intrinsic_validity --> Intrinsic Validity
    - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/gas_limit --> Gas Limit: For each new field that affects the intrinsic gas cost of the transaction:
        - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/gas_limit/exact --> Verify the transaction (and the block it is included in) is valid by providing the exact intrinsic gas as `gas_limit` value to the transaction with all multiple combinations of values to the field.
        - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/gas_limit/insufficient --> Verify the transaction (and the block it is included in) is invalid by providing the exact intrinsic gas minus one as `gas_limit` value to the transaction with all multiple combinations of values to the field.
    - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/max_fee --> Max fee per gas: Verify the transaction (and the block it is included in) is invalid if:
        - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/max_fee/priority_lower --> Its max-priority-fee-per-gas value is lower than the max-fee-per-gas.
        - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/max_fee/base_lower --> Its max-fee-per-gas value is lower than the blocks base-fee-per-gas.
    - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/chain_id --> Chain ID: Verify the transaction (and the block it is included in) is invalid if its chain-id value does not match the network configuration.
    - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/nonce --> Nonce: Verify the transaction (and the block it is included in) is invalid if its nonce value does not match the account's current nonce.
    - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/to --> To: Verify the transaction (and the block it is included in) is invalid if the transaction type does not allow contract creation and the to-address field is empty.
    - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/value --> Value: Verify the transaction (and the block it is included in) is invalid if the transaction contains a value of 1 and the account does not contain enough funds to cover the intrinsic transaction cost plus 1.
    - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/data --> Data: Verify the transaction (and the block it is included in) is invalid if the transaction contains enough data so the data floor cost is higher than the intrinsic gas cost and the gas_limit is equal to the intrinsic gas cost.
    - [ ] <!-- id:new_transaction_type/test/intrinsic_validity/sender_balance --> Sender balance: Verify the transaction (and the block it is included in) is invalid when the sender account does not have enough balance to cover the gas limit multiplied by the max fee per gas.
- [ ] <!-- id:new_transaction_type/test/signature --> Signature:
    - [ ] <!-- id:new_transaction_type/test/signature/invalid --> Verify the transaction is correctly rejected if it contains an invalid signature:
        - [ ] <!-- id:new_transaction_type/test/signature/invalid/field_outside_curve --> V, R, S represent a value that is inside of the field but outside of the curve.
        - [ ] <!-- id:new_transaction_type/test/signature/invalid/v --> V (yParity) is any of the following invalid values:
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/v/2 --> `2`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/v/27 --> `27` (Type-0 transaction valid value)
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/v/28 --> `28` (Type-0 transaction valid value)
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/v/35 --> `35` (Type-0 replay-protected transaction valid value for chain id 1)
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/v/36 --> `36` (Type-0 replay-protected transaction valid value for chain id 1)
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/v/max --> `2**8-1`
        - [ ] <!-- id:new_transaction_type/test/signature/invalid/r --> R is any of the following invalid values:
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/r/0 --> `0`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/r/secp256k1n_minus_one --> `SECP256K1N-1`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/r/secp256k1n --> `SECP256K1N`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/r/secp256k1n_plus_one --> `SECP256K1N+1`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/r/max_minus_one --> `2**256-1`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/r/max --> `2**256`
        - [ ] <!-- id:new_transaction_type/test/signature/invalid/s --> S is any of the following invalid values:
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/0 --> `0`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/secp256k1n_half_minus_one --> `SECP256K1N//2-1`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/secp256k1n_half --> `SECP256K1N//2`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/secp256k1n_half_plus_one --> `SECP256K1N//2+1`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/secp256k1n_minus_one --> `SECP256K1N-1`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/secp256k1n --> `SECP256K1N`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/secp256k1n_plus_one --> `SECP256K1N+1`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/max_minus_one --> `2**256-1`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/max --> `2**256`
            - [ ] <!-- id:new_transaction_type/test/signature/invalid/s/complement --> `SECP256K1N - S` of a valid signature
- [ ] <!-- id:new_transaction_type/test/tx_scoped_attributes --> Transaction-Scoped Attributes/Variables
    - [ ] <!-- id:new_transaction_type/test/tx_scoped_attributes/read --> Verify attributes that can be read in the EVM from transaction fields.
    - [ ] <!-- id:new_transaction_type/test/tx_scoped_attributes/older_tx_types --> Verify attributes specific to the new transaction type that can be read in the EVM behave correctly on older transaction types.
    - [ ] <!-- id:new_transaction_type/test/tx_scoped_attributes/persistent --> Verify values or variables that are persistent through the execution of the transaction (transient storage, warm/cold accounts):
        - [ ] <!-- id:new_transaction_type/test/tx_scoped_attributes/persistent/throughout --> Persist throughout the entire transaction.
        - [ ] <!-- id:new_transaction_type/test/tx_scoped_attributes/persistent/reset --> Reset on subsequent transactions in the same block.
- [ ] <!-- id:new_transaction_type/test/encoding --> Encoding (RLP, SSZ)
    - [ ] <!-- id:new_transaction_type/test/encoding/field_sizes --> Verify correct transaction rejection due to incorrect field sizes:
        - [ ] <!-- id:new_transaction_type/test/encoding/field_sizes/leading_zero --> Add leading zero byte
        - [ ] <!-- id:new_transaction_type/test/encoding/field_sizes/remove_byte --> Remove single byte from fixed-byte-length fields
    - [ ] <!-- id:new_transaction_type/test/encoding/list_field --> If the transaction contains a new field that is a list, verify:
        - [ ] <!-- id:new_transaction_type/test/encoding/list_field/zero --> Zero-element list
        - [ ] <!-- id:new_transaction_type/test/encoding/list_field/max --> Max count list
        - [ ] <!-- id:new_transaction_type/test/encoding/list_field/max_plus_one --> Max count plus one list
    - [ ] <!-- id:new_transaction_type/test/encoding/missing_fields --> Verify correct transaction rejection if the fields particular to the new transaction types are missing
    - [ ] <!-- id:new_transaction_type/test/encoding/extra_fields --> Verify correct transaction rejection if the transaction type contains extra fields
    - [ ] <!-- id:new_transaction_type/test/encoding/truncated --> Verify transaction is correctly rejected if the serialized bytes object is truncated
    - [ ] <!-- id:new_transaction_type/test/encoding/extra_bytes --> Verify transaction is correctly rejected if the serialized bytes object has extra bytes
    - [ ] <!-- id:new_transaction_type/test/encoding/new_types --> If the transaction contains fields with new serializable types, perform all previous tests on the new type/field, plus:
        - [ ] <!-- id:new_transaction_type/test/encoding/new_types/incorrect_encoding --> Verify transaction rejection if the serializable field is incorrectly encoded as bytes instead of using the correct encoding.
- [ ] <!-- id:new_transaction_type/test/out_of_bounds --> Out-of-bounds checks: Verify if the transaction has out-of-bounds conditions in its fields and verify:
    - [ ] <!-- id:new_transaction_type/test/out_of_bounds/max --> Max value for each field
    - [ ] <!-- id:new_transaction_type/test/out_of_bounds/max_plus_one --> Max value + 1 for each field
- [ ] <!-- id:new_transaction_type/test/contract_creation --> Contract creation: Verify that the transaction can create new contracts if the transaction type supports it.
- [ ] <!-- id:new_transaction_type/test/sender_account --> Sender account modifications
    - [ ] <!-- id:new_transaction_type/test/sender_account/nonce --> Verify that the sender account of the new transaction type transaction has its nonce incremented at least by one after the transaction is included in a block (or more if the transaction type introduces a new mechanism that bumps the nonce by more than one).
    - [ ] <!-- id:new_transaction_type/test/sender_account/balance --> Verify that the sender account of the new transaction type transaction has its balance reduced by the correct amount (gas consumed and value) at the start of execution (e.g. using Op.BALANCE).
- [ ] <!-- id:new_transaction_type/test/block_interactions --> Block Level Interactions
    - [ ] <!-- id:new_transaction_type/test/block_interactions/single_tx --> Verify the new transaction type and the following accept/reject behavior depending on interactions with the block gas limit:
        - [ ] <!-- id:new_transaction_type/test/block_interactions/single_tx/rejected --> Rejected if `tx.gas_limit == block.gas_limit + 1`
        - [ ] <!-- id:new_transaction_type/test/block_interactions/single_tx/accepted --> Accepted if `tx.gas_limit == block.gas_limit`
    - [ ] <!-- id:new_transaction_type/test/block_interactions/last_tx --> New transaction type is the last transaction of a block with two transactions:
        - [ ] <!-- id:new_transaction_type/test/block_interactions/last_tx/accepted --> Accepted if `block.txs[0].gas_used + block.txs[1].gas_limit == block.gas_limit`
        - [ ] <!-- id:new_transaction_type/test/block_interactions/last_tx/rejected --> Rejected if `(block.txs[0].gas_used + block.txs[1].gas_limit == block.gas_limit + 1) and (block.txs[0].gas_used < block.gas_limit)`
    - [ ] <!-- id:new_transaction_type/test/block_interactions/eip7825 --> Verify a transaction of the new type is rejected if its gas limit exceeds the [EIP-7825](https://eips.ethereum.org/EIPS/eip-7825) gas limit for the current fork.
    - [ ] <!-- id:new_transaction_type/test/block_interactions/mixed_txs --> Verify a block with all transactions types including the new type is executed correctly.
- [ ] <!-- id:new_transaction_type/test/fork_transition --> Fork transition: Verify that a block prior to fork activation where the new transaction type is introduced and containing the new transaction type is invalid.
- [ ] <!-- id:new_transaction_type/test/rpc --> RPC Tests
    - [ ] <!-- id:new_transaction_type/test/rpc/estimate_gas --> *Verify `eth_estimateGas` behavior for different valid combinations of the new transaction type
    - [ ] <!-- id:new_transaction_type/test/rpc/send_raw --> Verify `eth_sendRawTransaction` using `execute`

*Tests must be added to [`execution-apis`](https://github.com/ethereum/execution-apis) repository.

### <!-- id:new_transaction_type/framework --> Framework Changes

- [ ] <!-- id:new_transaction_type/framework/intrinsic_cost --> Modify `transaction_intrinsic_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py`, adding the appropriate new fields that the transaction introduced and the logic to the intrinsic gas cost calculation, if any.
- [ ] <!-- id:new_transaction_type/framework/tx_types --> Add the transaction type number to `tx_types` response in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` (If applicable add also to `contract_creating_tx_types`).

## <!-- id:new_block_header_field --> New Block Header Field

### <!-- id:new_block_header_field/test --> Test Vectors

- [ ] <!-- id:new_block_header_field/test/genesis --> Genesis value: Verify, if possible, that the value can be set at genesis if the network starting fork is the activation fork, and that clients can consume such genesis.
- [ ] <!-- id:new_block_header_field/test/value_behavior --> Value behavior
    - [ ] <!-- id:new_block_header_field/test/value_behavior/accept --> Verify, given multiple initial values, that a block is accepted if the value is the correct expected for the current block, depending on the circumstances that affect the value as defined in the EIP.
    - [ ] <!-- id:new_block_header_field/test/value_behavior/reject --> Verify, given multiple initial values, that a block is rejected if the value is modified (using `block.rlp_modifier`) to an incorrect value for the current block, depending on the circumstances that affect the value as defined in the EIP.
- [ ] <!-- id:new_block_header_field/test/fork_transition --> Fork transition
    - [ ] <!-- id:new_block_header_field/test/fork_transition/initial --> Verify initial value of the field at the first block of the activation fork.
    - [ ] <!-- id:new_block_header_field/test/fork_transition/before --> Verify that a block containing the new header field before the activation of the fork is invalid.
    - [ ] <!-- id:new_block_header_field/test/fork_transition/after --> Verify that a block lacking the new header field at the activation of the fork is invalid.

### <!-- id:new_block_header_field/framework --> Framework Changes

- [ ] <!-- id:new_block_header_field/framework/objects --> Add the new header field to the relevant objects:
    - [ ] <!-- id:new_block_header_field/framework/objects/fixture_header --> `ethereum_test_fixtures.FixtureHeader`
    - [ ] <!-- id:new_block_header_field/framework/objects/fixture_execution_payload --> `ethereum_test_fixtures.FixtureExecutionPayload`
    - [ ] <!-- id:new_block_header_field/framework/objects/header --> `ethereum_test_specs.Header`
- [ ] <!-- id:new_block_header_field/framework/fork_method --> Add the appropriate `header_*_required` fork method to `BaseFork` in `ethereum_test_forks`.

## <!-- id:new_block_body_field --> New Block Body Field

### <!-- id:new_block_body_field/test --> Test Vectors

- [ ] <!-- id:new_block_body_field/test/value_behavior --> Value behavior
    - [ ] <!-- id:new_block_body_field/test/value_behavior/accept --> Verify, given multiple initial values, that a block is accepted if the value is the correct expected for the current block, depending on the circumstances that affect the value as defined in the EIP.
    - [ ] <!-- id:new_block_body_field/test/value_behavior/reject --> Verify, given multiple initial values, that a block is rejected if the value is modified (using appropriate `block`) to an incorrect value for the current block, depending on the circumstances that affect the value as defined in the EIP.
- [ ] <!-- id:new_block_body_field/test/fork_transition --> Fork transition
    - [ ] <!-- id:new_block_body_field/test/fork_transition/before --> Verify that a block containing the new block body field before the activation of the fork is invalid.
    - [ ] <!-- id:new_block_body_field/test/fork_transition/after --> Verify that a block lacking the new block  field at the activation of the fork is invalid.

### <!-- id:new_block_body_field/framework --> Framework Changes

- [ ] <!-- id:new_block_body_field/framework/value_behavior --> Value behavior
    - [ ] <!-- id:new_block_body_field/framework/value_behavior/accept --> Verify, given multiple initial values, that a block is accepted if the value is correctly modified for the current block, depending on the circumstances that affect the value as defined in the EIP.
    - [ ] <!-- id:new_block_body_field/framework/value_behavior/reject --> Verify, given multiple initial values, that a block is rejected if the value is incorrectly modified for the current block, depending on the circumstances that affect the value as defined in the EIP.
- [ ] <!-- id:new_block_body_field/framework/objects --> Add the new body field to the relevant objects:
    - [ ] <!-- id:new_block_body_field/framework/objects/fixture_block --> `ethereum_test_fixtures.FixtureBlockBase`
    - [ ] <!-- id:new_block_body_field/framework/objects/fixture_engine --> `ethereum_test_fixtures.FixtureEngineNewPayload`
    - [ ] <!-- id:new_block_body_field/framework/objects/block --> `ethereum_test_specs.Block`
- [ ] <!-- id:new_block_body_field/framework/filling --> Modify `ethereum_test_specs.BlockchainTest` filling behavior to account for the new block field.

## <!-- id:gas_cost_changes --> Gas Cost Changes

### <!-- id:gas_cost_changes/test --> Test Vectors

- [ ] <!-- id:gas_cost_changes/test/gas_usage --> Gas Usage: Measure and store the gas usage during the operations affected by the gas cost changes and verify the updated behavior.
- [ ] <!-- id:gas_cost_changes/test/out_of_gas --> Out-of-gas: Verify the operations affected by the gas cost changes can run out-of-gas with the updated limits.
- [ ] <!-- id:gas_cost_changes/test/fork_transition --> Fork transition: Verify gas costs are:
    - [ ] <!-- id:gas_cost_changes/test/fork_transition/before --> Unaffected before the fork activation block.
    - [ ] <!-- id:gas_cost_changes/test/fork_transition/after --> Updated on and after fork activation block.

### <!-- id:gas_cost_changes/framework --> Framework Changes

- [ ] <!-- id:gas_cost_changes/framework/intrinsic_cost --> Modify `transaction_intrinsic_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects intrinsic gas cost calculation.
- [ ] <!-- id:gas_cost_changes/framework/data_floor --> Modify `transaction_data_floor_cost_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects calldata floor cost.
- [ ] <!-- id:gas_cost_changes/framework/memory_expansion --> Modify `memory_expansion_gas_calculator` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects memory expansion gas cost calculation.
- [ ] <!-- id:gas_cost_changes/framework/opcode_costs --> Modify `gas_costs` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects specific opcode gas costs.

## <!-- id:gas_refunds_changes --> Gas Refunds Changes

### <!-- id:gas_refunds_changes/test --> Test Vectors

- [ ] <!-- id:gas_refunds_changes/test/refund_calculation --> Refund calculation: Verify that the refund does not exceed `gas_used // MAX_REFUND_QUOTIENT` (`MAX_REFUND_QUOTIENT==5` in [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529)) in the following scenarios:
    - [ ] <!-- id:gas_refunds_changes/test/refund_calculation/over --> `refund == gas_used // MAX_REFUND_QUOTIENT + 1`
    - [ ] <!-- id:gas_refunds_changes/test/refund_calculation/exact --> `refund == gas_used // MAX_REFUND_QUOTIENT`
    - [ ] <!-- id:gas_refunds_changes/test/refund_calculation/under --> `refund == gas_used // MAX_REFUND_QUOTIENT - 1`
- [ ] <!-- id:gas_refunds_changes/test/exceptional_abort --> Exceptional Abort:
    - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/revertable --> If the operation causing the refund can be reverted, verify the refund is not applied if the following cases:
        - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/revertable/revert --> `REVERT`
        - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/revertable/out_of_gas --> Out-of-gas
        - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/revertable/invalid_opcode --> Invalid opcode
        - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/revertable/upper_revert --> `REVERT` of an upper call frame
    - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/non_revertable --> If the operation causing the refund cannot be reverted (e.g. in the case of a transaction-scoped operation such as authorization refunds in EIP-7702), verify the refund is still applied even in the following cases:
        - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/non_revertable/revert --> `REVERT` at the top call frame
        - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/non_revertable/out_of_gas --> Out-of-gas at the top call frame
        - [ ] <!-- id:gas_refunds_changes/test/exceptional_abort/non_revertable/invalid_opcode --> Invalid opcode at the top call frame
- [ ] <!-- id:gas_refunds_changes/test/cross_functional --> Cross-Functional Test: Verify the following tests are updated to support the new type of refunds:
    - [ ] <!-- id:gas_refunds_changes/test/cross_functional/calldata_cost --> `tests/prague/eip7623_increase_calldata_cost/test_refunds.py`

### <!-- id:gas_refunds_changes/framework --> Framework Changes

N/A

## <!-- id:blob_count_changes --> Blob Count Changes

### <!-- id:blob_count_changes/test --> Test Vectors

- [ ] <!-- id:blob_count_changes/test/update_eip4844_blobs --> Verify tests in `tests/cancun/eip4844_blobs` were correctly and automatically updated to take into account the new blob count values at the new fork activation block.

### <!-- id:blob_count_changes/framework --> Framework Changes

- [ ] <!-- id:blob_count_changes/framework/fork_parameters --> Modify `blob_base_fee_update_fraction`, `target_blobs_per_block`, `max_blobs_per_block` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` if the EIP affects any of the values returned by each function.

## <!-- id:new_execution_layer_request --> New Execution Layer Request

### <!-- id:new_execution_layer_request/test --> Test Vectors

- [ ] <!-- id:new_execution_layer_request/test/cross_request_type --> Cross-Request-Type Interaction
    - [ ] <!-- id:new_execution_layer_request/test/cross_request_type/update --> Update `tests/prague/eip7685_general_purpose_el_requests` tests to include the new request type in the tests combinations

### <!-- id:new_execution_layer_request/framework --> Framework Changes

- [ ] <!-- id:new_execution_layer_request/framework/max_request_type --> Increment `max_request_type` in the fork where the EIP is introduced in `src/ethereum_test_forks/forks/forks.py` to the new maximum request type number after the EIP is activated.
