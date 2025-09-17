#!/usr/bin/env python3
"""
CREATE2 deployment script for bloatnet benchmark contracts.
Uses a factory pattern to deploy contracts at deterministic addresses.

Based on the pattern from EIP-7997, this deploys contracts using CREATE2
so they can be accessed from any account and reused across tests.
"""

import argparse
import os
import subprocess
import sys

from eth_utils import keccak
from web3 import Web3


def deploy_contracts(rpc_url: str, num_contracts: int, factory_address: str = None):
    """Deploy contracts using CREATE2 factory pattern."""
    # Connect to Geth
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Failed to connect to {rpc_url}")
        sys.exit(1)

    test_account = w3.eth.accounts[0]
    print(f"Using test account: {test_account}")
    print(f"Balance: {w3.eth.get_balance(test_account) / 10**18:.4f} ETH")

    # Step 1: Check if factory exists, if not deploy it
    if factory_address:
        # Verify factory exists at the provided address
        factory_code = w3.eth.get_code(factory_address)
        if len(factory_code) > 0:
            print(f"\nUsing existing CREATE2 factory at: {factory_address}")
        else:
            print(f"\nNo factory found at {factory_address}")
            print("Deploying new CREATE2 factory...")

            # Call the deploy_create2_factory.py script
            try:
                # Get the directory of this script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                factory_script = os.path.join(script_dir, "deploy_create2_factory.py")

                result = subprocess.run(
                    [sys.executable, factory_script, "--rpc-url", rpc_url],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    print("Failed to deploy factory:")
                    print(result.stderr)
                    sys.exit(1)

                # Extract factory address from output
                for line in result.stdout.split("\n"):
                    if "Factory address:" in line:
                        factory_address = line.split(":")[1].strip()
                        print(f"Factory deployed at: {factory_address}")
                        break
                else:
                    print("Could not extract factory address from deployment output")
                    sys.exit(1)

            except Exception as e:
                print(f"Error deploying factory: {e}")
                sys.exit(1)
    else:
        print("\nNo factory address provided, deploying new CREATE2 factory...")

        # Call the deploy_create2_factory.py script
        try:
            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            factory_script = os.path.join(script_dir, "deploy_create2_factory.py")

            result = subprocess.run(
                [sys.executable, factory_script, "--rpc-url", rpc_url],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print("Failed to deploy factory:")
                print(result.stderr)
                sys.exit(1)

            # Extract factory address from output
            for line in result.stdout.split("\n"):
                if "Factory address:" in line:
                    factory_address = line.split(":")[1].strip()
                    print(f"Factory deployed at: {factory_address}")
                    break
            else:
                print("Could not extract factory address from deployment output")
                sys.exit(1)

        except Exception as e:
            print(f"Error deploying factory: {e}")
            sys.exit(1)

    # Step 2: Generate init code for 24KB contracts
    # Init code copies runtime bytecode to memory and returns it
    init_code = bytearray()

    # Init code: PUSH2 size, PUSH1 offset, PUSH1 dest, CODECOPY, PUSH2 size, PUSH1 0, RETURN
    bytecode_size = 24576
    init_size = 13  # Size of init code instructions

    # PUSH2 bytecode_size, PUSH1 init_size, PUSH1 0, CODECOPY
    init_code.extend(
        [
            0x61,
            (bytecode_size >> 8) & 0xFF,
            bytecode_size & 0xFF,  # PUSH2 bytecode_size
            0x60,
            init_size,  # PUSH1 init_size (offset where runtime code starts)
            0x60,
            0x00,  # PUSH1 0 (dest in memory)
            0x39,  # CODECOPY
        ]
    )

    # PUSH2 bytecode_size, PUSH1 0, RETURN
    init_code.extend(
        [
            0x61,
            (bytecode_size >> 8) & 0xFF,
            bytecode_size & 0xFF,  # PUSH2 bytecode_size
            0x60,
            0x00,  # PUSH1 0 (offset in memory)
            0xF3,  # RETURN
        ]
    )

    # Generate unique 24KB runtime bytecode to prevent deduplication
    runtime_bytecode = bytearray([0x00])  # Start with STOP

    # Fill with unique pattern
    pattern_count = 0
    while len(runtime_bytecode) < bytecode_size - 100:
        # Use a simple pattern that's still unique per contract
        unique_value = keccak(f"bloatnet_{pattern_count}".encode())
        runtime_bytecode.append(0x7F)  # PUSH32
        runtime_bytecode.extend(unique_value[:31])  # Use 31 bytes of hash
        runtime_bytecode.append(0x50)  # POP
        pattern_count += 1

    # Fill rest with JUMPDEST
    while len(runtime_bytecode) < bytecode_size:
        runtime_bytecode.append(0x5B)

    # Combine init code and runtime bytecode
    full_init_code = bytes(init_code) + bytes(runtime_bytecode)
    init_code_hash = keccak(full_init_code)

    print(f"\nInit code hash: 0x{init_code_hash.hex()}")
    print(f"Init code size: {len(full_init_code)} bytes")

    # Step 3: Deploy contracts using factory
    print(f"\nDeploying {num_contracts} contracts using CREATE2...")

    deployed = []
    for salt in range(num_contracts):
        if salt % 100 == 0:
            print(f"Progress: {salt}/{num_contracts}")

        # Factory expects: salt (32 bytes) + bytecode
        call_data = (
            salt.to_bytes(32, "big")  # salt
            + full_init_code  # the init code
        )

        try:
            tx_hash = w3.eth.send_transaction(
                {
                    "from": test_account,
                    "to": factory_address,
                    "data": "0x" + call_data.hex(),
                    "gas": 10000000,
                }
            )

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10)

            if receipt.status == 1:
                # Calculate CREATE2 address
                create2_input = (
                    b"\xff"
                    + bytes.fromhex(factory_address[2:])
                    + salt.to_bytes(32, "big")
                    + init_code_hash
                )
                contract_address = "0x" + keccak(create2_input)[-20:].hex()
                deployed.append(contract_address)

                if (salt + 1) % 100 == 0 or salt == num_contracts - 1:
                    print(f"  [{salt + 1}/{num_contracts}] Deployed at {contract_address}")
            else:
                print(f"  [{salt + 1}/{num_contracts}] Failed")

        except Exception as e:
            print(f"  [{salt + 1}/{num_contracts}] Error: {e}")
            break

    print(f"\nDeployed {len(deployed)} contracts")

    if deployed:
        print("\nContract addresses:")
        print(f"First: {deployed[0]}")
        print(f"Last: {deployed[-1]}")

        print("\nFor test configuration:")
        print(f'FACTORY_ADDRESS = Address("{factory_address}")')
        print(f'INIT_CODE_HASH = bytes.fromhex("{init_code_hash.hex()}")')
        print(f"NUM_CONTRACTS = {len(deployed)}")


def main():
    """Execute the deployment script."""
    parser = argparse.ArgumentParser(description="Deploy bloatnet contracts using CREATE2")
    parser.add_argument(
        "--num-contracts", type=int, default=100, help="Number of contracts to deploy"
    )
    parser.add_argument("--rpc-url", default="http://127.0.0.1:8545", help="RPC URL")
    parser.add_argument(
        "--factory-address",
        default=None,
        help="CREATE2 factory address (deploys new one if not provided)",
    )

    args = parser.parse_args()
    deploy_contracts(args.rpc_url, args.num_contracts, args.factory_address)


if __name__ == "__main__":
    main()
