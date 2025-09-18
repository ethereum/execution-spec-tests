#!/usr/bin/env python3
"""
Deploy a simple CREATE2 factory for benchmark tests (REFACTORED with EEST Op codes).
This factory can be reused across all tests and allows deterministic addresses.

This version uses EEST Op code tooling for better readability.
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


def deploy_factory(rpc_url: str):
    """Deploy a minimal CREATE2 factory using EEST Op codes."""
    # Connect to Geth
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Failed to connect to {rpc_url}")
        return None

    test_account = w3.eth.accounts[0]
    print(f"Using test account: {test_account}")

    # Build CREATE2 factory bytecode using EEST Op codes
    # This factory:
    # 1. Takes salt (first 32 bytes) from calldata
    # 2. Takes bytecode (rest) from calldata
    # 3. Deploys via CREATE2
    # 4. Returns the deployed address

    factory_code = (
        # Load salt from calldata[0:32]
        Op.PUSH0  # offset 0
        + Op.CALLDATALOAD  # load 32 bytes from calldata[0]
        # Calculate bytecode length (calldatasize - 32)
        + Op.PUSH1(32)  # salt size
        + Op.CALLDATASIZE  # total calldata size
        + Op.SUB  # bytecode_len = calldatasize - 32
        # Copy bytecode from calldata[32:] to memory[0:]
        + Op.DUP1  # duplicate bytecode_len for CREATE2
        + Op.PUSH1(32)  # source offset in calldata
        + Op.PUSH0  # dest offset in memory
        + Op.CALLDATACOPY  # copy bytecode to memory
        # CREATE2(value=0, mem_offset=0, mem_size=bytecode_len, salt)
        # Stack: [salt, bytecode_len]
        + Op.PUSH0  # value = 0
        + Op.SWAP2  # Stack: [bytecode_len, 0, salt]
        + Op.PUSH0  # mem_offset = 0
        + Op.SWAP1  # Stack: [bytecode_len, 0, 0, salt]
        + Op.SWAP3  # Stack: [salt, 0, 0, bytecode_len]
        + Op.SWAP2  # Stack: [0, salt, 0, bytecode_len]
        + Op.SWAP1  # Stack: [salt, 0, 0, bytecode_len]
        + Op.CREATE2  # Deploy contract
        # Store address in memory and return it
        + Op.PUSH0  # memory offset 0
        + Op.MSTORE  # store address at memory[0:32]
        + Op.PUSH1(32)  # return 32 bytes
        + Op.PUSH0  # from memory offset 0
        + Op.RETURN  # return the address
    )

    # Convert Op code object to bytes
    factory_bytecode = bytes(factory_code)

    print(f"\nFactory bytecode ({len(factory_bytecode)} bytes):")
    print(f"0x{factory_bytecode.hex()}")

    # Deploy the factory
    print("\nDeploying CREATE2 factory...")
    tx_hash = w3.eth.send_transaction(
        {"from": test_account, "data": factory_bytecode, "gas": 3000000}
    )

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt["status"] != 1:
        print("Failed to deploy factory")
        return None

    factory_address = receipt["contractAddress"]
    print(f"✅ Factory deployed at: {factory_address}")

    # Test the factory with a simple contract
    print("\nTesting factory...")
    test_bytecode = bytes([0x00])  # Simple STOP opcode
    test_salt = 0

    calldata = test_salt.to_bytes(32, "big") + test_bytecode

    # Use eth_call to get the address that would be created
    result = w3.eth.call({"to": factory_address, "data": calldata})

    if result:
        test_addr = "0x" + result[-20:].hex()
        print(f"Test deployment would create: {test_addr}")

        # Calculate expected CREATE2 address
        expected = keccak(
            b"\xff"
            + bytes.fromhex(factory_address[2:])
            + test_salt.to_bytes(32, "big")
            + keccak(test_bytecode)
        )[-20:]
        expected_addr = "0x" + expected.hex()
        print(f"Expected CREATE2 address: {expected_addr}")

    return factory_address


def main():
    """Execute the factory deployment script."""
    parser = argparse.ArgumentParser(description="Deploy CREATE2 factory (EEST refactored)")
    parser.add_argument(
        "--rpc-url",
        default="http://127.0.0.1:8545",
        help="RPC URL (default: http://127.0.0.1:8545)",
    )

    args = parser.parse_args()
    factory_address = deploy_factory(args.rpc_url)

    if factory_address:
        print("\n" + "=" * 60)
        print("Factory deployed successfully!")
        print(f"Factory address: {factory_address}")
        print("\nAdd this to your test configuration:")
        print(f'FACTORY_ADDRESS = Address("{factory_address}")')
        print("=" * 60)


if __name__ == "__main__":
    main()
