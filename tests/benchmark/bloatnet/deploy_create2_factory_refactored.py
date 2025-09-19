#!/usr/bin/env python3
"""
Deploy a CREATE2 factory for on-the-fly contract address generation in BloatNet tests.

This factory uses a constant initcode that generates unique 24KB contracts by:
1. Using ADDRESS opcode for pseudo-randomness (within the factory's context)
2. Expanding randomness with SHA3 and XOR operations
3. Creating max-size contracts with deterministic CREATE2 addresses
"""

import argparse
import sys
from pathlib import Path

# Add parent directories to path to import EEST tools
sys.path.insert(0, str(Path(__file__).parents[3]))

try:
    from eth_utils import keccak
    from web3 import Web3

    from ethereum_test_tools.vm.opcode import Opcodes as Op
except ImportError as e:
    print(f"Error: Missing dependencies - {e}")
    print("This refactored version requires the EEST framework.")
    print("Run: uv sync --all-extras")
    sys.exit(1)

# XOR table for pseudo-random bytecode generation (reused from test_worst_bytecode.py)
XOR_TABLE_SIZE = 256
XOR_TABLE = [keccak(i.to_bytes(32, "big")) for i in range(XOR_TABLE_SIZE)]
MAX_CONTRACT_SIZE = 24576  # 24KB


def build_initcode() -> bytes:
    """Build the initcode that generates unique 24KB contracts using ADDRESS for randomness."""
    from ethereum_test_tools import While

    # This initcode follows the pattern from test_worst_bytecode.py:
    # 1. Uses ADDRESS as initial seed for pseudo-randomness (creates uniqueness per deployment)
    # 2. Expands to 24KB using SHA3 and XOR operations
    # 3. Sets first byte to STOP for quick CALL returns
    initcode = (
        # Store ADDRESS as initial seed - THIS IS CRITICAL FOR UNIQUENESS
        Op.MSTORE(0, Op.ADDRESS)
        # Loop to expand bytecode using SHA3 and XOR operations
        + While(
            body=(
                Op.SHA3(Op.SUB(Op.MSIZE, 32), 32)
                # Use XOR table to expand without excessive SHA3 calls
                + sum(
                    (Op.PUSH32[xor_value] + Op.XOR + Op.DUP1 + Op.MSIZE + Op.MSTORE)
                    for xor_value in XOR_TABLE
                )
                + Op.POP
            ),
            condition=Op.LT(Op.MSIZE, MAX_CONTRACT_SIZE),
        )
        # Set first byte to STOP for efficient CALL handling
        + Op.MSTORE8(0, 0x00)
        # Return the full contract
        + Op.RETURN(0, MAX_CONTRACT_SIZE)
    )
    return bytes(initcode)


def deploy_factory_and_initcode(rpc_url: str):
    """Deploy the initcode template and factory that uses it."""
    # Connect to Geth
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Failed to connect to {rpc_url}")
        return None, None

    test_account = w3.eth.accounts[0]
    print(f"Using test account: {test_account}")

    # Build the initcode
    initcode = build_initcode()
    print(f"\nInitcode size: {len(initcode)} bytes")
    print(f"Initcode (first 100 bytes): 0x{initcode[:100].hex()}...")

    # Deploy the initcode as a contract that the factory can copy from
    print("\nDeploying initcode template contract...")
    tx_hash = w3.eth.send_transaction({"from": test_account, "data": initcode, "gas": 10000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt["status"] != 1:
        print("Failed to deploy initcode template")
        return None, None

    initcode_address = receipt["contractAddress"]
    print(f"✅ Initcode template deployed at: {initcode_address}")

    # Build the factory contract following the pattern from test_worst_bytecode.py
    # The factory:
    # 1. Copies the initcode from the template contract
    # 2. Uses incrementing salt from storage for CREATE2
    # 3. Returns the created contract address
    factory_code = (
        # Copy initcode from template to memory
        Op.EXTCODECOPY(
            address=initcode_address,
            dest_offset=0,
            offset=0,
            size=Op.EXTCODESIZE(initcode_address),
        )
        # Store the result of CREATE2
        + Op.MSTORE(
            0,
            Op.CREATE2(
                value=0,
                offset=0,
                size=Op.EXTCODESIZE(initcode_address),
                salt=Op.SLOAD(0),
            ),
        )
        # Increment salt for next call
        + Op.SSTORE(0, Op.ADD(Op.SLOAD(0), 1))
        # Return created address
        + Op.RETURN(0, 32)
    )

    factory_bytecode = bytes(factory_code)
    print(f"\nFactory bytecode size: {len(factory_bytecode)} bytes")
    print(f"Factory bytecode: 0x{factory_bytecode.hex()}")

    # Deploy the factory
    print("\nDeploying CREATE2 factory...")
    tx_hash = w3.eth.send_transaction(
        {"from": test_account, "data": factory_bytecode, "gas": 3000000}
    )
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt["status"] != 1:
        print("Failed to deploy factory")
        return None, None

    factory_address = receipt["contractAddress"]
    print(f"✅ Factory deployed at: {factory_address}")

    # Calculate init code hash for CREATE2 address calculation
    init_code_hash = keccak(initcode)
    print(f"\nInit code hash: 0x{init_code_hash.hex()}")

    return factory_address, init_code_hash.hex()


def deploy_contracts(rpc_url: str, factory_address: str, num_contracts: int):
    """Deploy multiple contracts using the factory."""
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Failed to connect to {rpc_url}")
        return False

    test_account = w3.eth.accounts[0]
    print(f"\nDeploying {num_contracts} contracts via factory...")

    # Batch size for deployments
    batch_size = 100
    deployed_count = 0

    for batch_start in range(0, num_contracts, batch_size):
        batch_end = min(batch_start + batch_size, num_contracts)
        current_batch = batch_end - batch_start

        batch_num = batch_start // batch_size + 1
        print(f"Deploying batch {batch_num}: contracts {batch_start}-{batch_end - 1}...")

        for i in range(current_batch):
            try:
                tx_hash = w3.eth.send_transaction(
                    {"from": test_account, "to": factory_address, "gas": 10000000}
                )
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                if receipt["status"] == 1:
                    deployed_count += 1
                else:
                    print(f"  ⚠️ Failed to deploy contract {batch_start + i}")
            except Exception as e:
                print(f"  ⚠️ Error deploying contract {batch_start + i}: {e}")

        print(f"  ✅ Deployed {deployed_count}/{batch_end} contracts")

    return deployed_count == num_contracts


def main():
    """Execute the factory deployment script."""
    parser = argparse.ArgumentParser(description="Deploy CREATE2 factory for BloatNet tests")
    parser.add_argument(
        "--rpc-url",
        default="http://127.0.0.1:8545",
        help="RPC URL (default: http://127.0.0.1:8545)",
    )
    parser.add_argument(
        "--deploy-contracts", type=int, metavar="N", help="Deploy N contracts using the factory"
    )

    args = parser.parse_args()

    # Deploy factory and initcode template
    factory_address, init_code_hash = deploy_factory_and_initcode(args.rpc_url)

    if not factory_address:
        print("\n❌ Failed to deploy factory")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Factory deployed successfully!")
    print(f"Factory address: {factory_address}")
    print(f"Init code hash: 0x{init_code_hash}")
    print("\nAdd this to your test configuration:")
    print(f'FACTORY_ADDRESS = Address("{factory_address}")')
    print(f'INIT_CODE_HASH = bytes.fromhex("{init_code_hash}")')

    # Deploy contracts if requested
    if args.deploy_contracts:
        success = deploy_contracts(args.rpc_url, factory_address, args.deploy_contracts)
        if success:
            print(f"\n✅ Successfully deployed {args.deploy_contracts} contracts")
            print(f"NUM_DEPLOYED_CONTRACTS = {args.deploy_contracts}")
        else:
            print("\n⚠️ Some contracts failed to deploy")

    print("=" * 60)


if __name__ == "__main__":
    main()
