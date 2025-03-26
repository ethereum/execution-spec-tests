# EOF Tests <!-- markdownlint-disable MD051 (MD051=link-fragments "Link fragments should be valid") -->

The EOF Test fixture format tests are included in the fixtures subdirectory `eof_tests`.

These are produced by the `EOFTest` test spec.

## Description

The EOF test fixture format is used to test the EOF container validation function of the Ethereum Virtual Machine (EVM).

It simply defines a binary code in hexadecimal format and a boolean value that indicates whether the code is valid or not.

## Consumption

The EOF test fixture format is designed to be consumed by Ethereum client implementations to verify their EOF container validation logic. Clients should:

1. Parse the test fixture file (typically JSON format)
2. Extract the binary code in hexadecimal format
3. Validate the code according to EOF container validation rules
4. Compare the validation result (valid or invalid) against the expected result specified in the test
5. If the validation result matches the expected result, the test passes; otherwise, it fails

When validating EOF code, clients should follow the rules for EOF container validation as defined in the Ethereum execution specifications, particularly EIP-7692 (EOF v1) and related EIPs like EIP-4750 (Functions), EIP-7620 (EOF CREATE), and EIP-663 (DUPN/SWAPN/EXCHANGE).

## Structures

TODO: Update this section
