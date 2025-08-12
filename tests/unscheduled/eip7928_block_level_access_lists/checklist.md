# EIP-7928 Block Access Lists (BAL) Test Checklist

| Function Name | Goal | Setup | Expectation | Scope | Status |
|---------------|------|-------|-------------|-------|--------|
| `test_bal_nonce_changes` | Ensure BAL captures changes to nonce | Alice sends 100 wei to Bob | BAL MUST include changes to Alice's nonce. | tx | ✅ Completed |
| `test_bal_balance_changes` | Ensure BAL captures changes to balance | Alice sends 100 wei to Bob | BAL MUST include balance change for Alice, Bob, and Coinbase | tx | ✅ Completed |
| `test_bal_storage_writes` | Ensure BAL captures storage writes | Alice calls contract that writes to storage slot `0x01` | BAL MUST include storage changes with correct slot and value | tx | ✅ Completed |
| `test_bal_storage_reads` | Ensure BAL captures storage reads | Alice calls contract that reads from storage slot `0x01` | BAL MUST include storage access for the read operation | tx | ✅ Completed |
| `test_bal_code_changes` | Ensure BAL captures changes to account code | Alice deploys factory contract that creates new contract | BAL MUST include code changes for newly deployed contract | tx | ✅ Completed |

> ℹ️ Scope describes whether a test spans a single transaction (`tx`) or entire block (`blk`).
