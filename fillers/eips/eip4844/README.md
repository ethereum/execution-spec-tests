# EIP-4844 Test Cases

**Note:** *The priority levels (🔴, 🟠, 🟡, 🟢) represent very high, high, medium, low  priorities respectively.*

# 🧪 Execution Specification Tests

## 📖 Opcode DATAHASH

Test Module - eip4844/datahash_opcode.py

File Doc String: Verifies that the DATAHASH opcode, works as intended for a variety of contexts, retrieves the versioned hash correctly, handles out-of-range indices, and consumes the correct amount of gas.

**1) 🔴 test_datahash_opcode_contexts():**

Tests that the DATAHASH opcode functions correctly when called in different contexts, including:

    DATAHASH opcode on the top level of the call stack.
    DATAHASH opcode on the max value.
    DATAHASH opcode on CALL, DELEGATECALL, STATICCALL, and CALLCODE.
    DATAHASH opcode on Initcode.
    DATAHASH opcode on CREATE and CREATE2.
    DATAHASH opcode on transaction types 0, 1 and 2.

**2) 🔴 test_datahash_blob_versioned_hash():**

Tests that the DATAHASHopcode returns the correct versioned hash for various valid indexes. This test should cover various scenarios with random data versions within the valid range.

**3) 🔴 test_datahash_invalid_blob_index():**

Tests that the DATAHASH opcode returns a zeroed bytes32 value for invalid indexes. This test should include cases where the index is negative or exceeds the maximum number of versions stored, where index >= len(tx.message.blob_versioned_hashes). It should confirm that the returned value is a zeroed bytes32 value for these cases.

**4) 🟠 test_datahash_gas_cost():**

Asserts the gas consumption of the DATAHASH opcode and ensures it matches HASH_OPCODE_GAS = 3. Includes a variety of random index sizes, including min=0 and max=2^256-1, for tx types 2 and 5.

**5) 🟡 test_datahash_multiple_txs_in_block():**

Tests that the `DATAHASH` opcode returns the appropriate values when there is more than one blob tx type within a block (for tx types 2 and 5). Scenarios involve tx type 5 followed by tx type 2 running the same code. In this case `DATAHASH` returns 0, but for the opposite scenario `DATAHASH` should return the correct blob hash value.