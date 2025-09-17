#!/usr/bin/env python3
"""
Deploy a simple CREATE2 factory for benchmark tests.
This factory can be reused across all tests and allows deterministic addresses.
"""

import argparse

from eth_utils import keccak
from web3 import Web3


def deploy_factory(rpc_url: str):
    """Deploy a minimal CREATE2 factory."""
    # Connect to Geth
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Failed to connect to {rpc_url}")
        return None

    test_account = w3.eth.accounts[0]
    print(f"Using test account: {test_account}")

    # Minimal CREATE2 factory bytecode
    # Takes salt (first 32 bytes) and bytecode (rest) from calldata
    # Returns the deployed address
    factory_bytecode = bytes(
        [
            # Runtime code
            0x60,
            0x00,  # PUSH1 0x00 (value for CREATE2)
            0x60,
            0x00,  # PUSH1 0x00 (salt position in calldata)
            0x35,  # CALLDATALOAD (load salt)
            0x60,
            0x20,  # PUSH1 0x20 (bytecode starts at position 32)
            0x36,  # CALLDATASIZE
            0x60,
            0x20,  # PUSH1 0x20
            0x03,  # SUB (bytecode length = calldatasize - 32)
            0x80,  # DUP1 (duplicate bytecode length)
            0x60,
            0x20,  # PUSH1 0x20 (source position in calldata)
            0x60,
            0x00,  # PUSH1 0x00 (dest position in memory)
            0x37,  # CALLDATACOPY (copy bytecode to memory)
            0xF5,  # CREATE2 (value=0, mem_offset=0, mem_size, salt)
            0x60,
            0x00,  # PUSH1 0x00
            0x52,  # MSTORE (store address at position 0)
            0x60,
            0x20,  # PUSH1 0x20
            0x60,
            0x00,  # PUSH1 0x00
            0xF3,  # RETURN (return the address)
        ]
    )

    # Deploy the factory
    print("\nDeploying CREATE2 factory...")
    tx_hash = w3.eth.send_transaction(
        {"from": test_account, "data": "0x" + factory_bytecode.hex(), "gas": 3000000}
    )

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        print("Failed to deploy factory")
        return None

    factory_address = receipt.contractAddress
    print(f"✅ Factory deployed at: {factory_address}")

    # Test the factory with a simple contract
    print("\nTesting factory...")
    test_bytecode = bytes([0x00])  # Simple STOP opcode
    test_salt = 0

    calldata = test_salt.to_bytes(32, "big") + test_bytecode

    # Use eth_call to get the address that would be created
    result = w3.eth.call({"to": factory_address, "data": "0x" + calldata.hex()})

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
    parser = argparse.ArgumentParser(description="Deploy CREATE2 factory")
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
