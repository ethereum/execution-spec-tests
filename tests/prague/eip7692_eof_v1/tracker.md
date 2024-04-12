# EOF Testing Coverage Tracker

- [ ] Example Test Case 1
- [x] Example Test Case 2 (./eip3540_eof_v1/test_example_valid_invalid.py::test_example_valid_invalid)
- [ ] Example Test Case 3 (ethereum/tests: ./src/EOFTestsFiller/validInvalidFiller.yml)

## EIP-3540: EOF - EVM Object Format v1

## EIP-3670: EOF - Code Validation

## EIP-4200: EOF - Static relative jumps

## EIP-4750: EOF - Functions

## EIP-5450: EOF - Stack Validation

## EIP-6206: EOF - JUMPF and non-returning functions

## EIP-7480: EOF - Data section access instructions

## EIP-663: SWAPN, DUPN and EXCHANGE instructions

### Validation

- [ ] A DUPN instruction causes stack overflow
- [ ] A DUPN instruction causes stack underflow
- [ ] A DUPN instruction causes max stack height mismatch
- [ ] A SWAPN instruction causes stack underflow

### Execution

- [x] Positive tests for DUPN instructions (./eip663_dupn_swapn_exchange/test_dupn.py::test_dupn_all_valid_immediates)
- [x] Positive tests for SWAPN instructions (./eip663_dupn_swapn_exchange/test_swapn.py::test_swapn_all_valid_immediates)

## EIP-7069: Revamped CALL instructions

## EIP-7620: EOF Contract Creation

## EIP-7698: EOF - Creation transaction
