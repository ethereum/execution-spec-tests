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
from typing import Dict, List, Optional, Tuple

from eth_utils import keccak
from web3 import Web3


class ContractType:
    """Define contract types for different benchmarks."""

    MAX_SIZE_24KB = "max_size_24kb"
    SLOAD_HEAVY = "sload_heavy"
    STORAGE_HEAVY = "storage_heavy"
    CUSTOM = "custom"


CONTRACT_DESCRIPTIONS = {
    ContractType.MAX_SIZE_24KB: "24KB contracts filled with unique bytecode (standard bloatnet)",
    ContractType.SLOAD_HEAVY: "Contracts optimized for SLOAD benchmarking",
    ContractType.STORAGE_HEAVY: "Contracts with pre-initialized storage",
    ContractType.CUSTOM: "Custom bytecode (provide your own)",
}


def generate_max_size_bytecode(salt: int = 0, max_code_size: int = 24576) -> Tuple[bytes, bytes]:
    """Generate max-size contract bytecode for standard bloatnet tests.

    Args:
        salt: Unique salt for generating unique bytecode
        max_code_size: Maximum contract size (default 24576 bytes for mainnet)
    """
    # Init code copies runtime bytecode to memory and returns it
    init_code = bytearray()

    # Init code: PUSH2 size, PUSH1 offset, PUSH1 dest, CODECOPY, PUSH2 size, PUSH1 0, RETURN
    bytecode_size = max_code_size
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
        unique_value = keccak(f"bloatnet_{salt}_{pattern_count}".encode())
        runtime_bytecode.append(0x7F)  # PUSH32
        runtime_bytecode.extend(unique_value[:31])  # Use 31 bytes of hash
        runtime_bytecode.append(0x50)  # POP
        pattern_count += 1

    # Fill rest with JUMPDEST
    while len(runtime_bytecode) < bytecode_size:
        runtime_bytecode.append(0x5B)

    full_init_code = bytes(init_code) + bytes(runtime_bytecode)
    return full_init_code, keccak(full_init_code)


def generate_sload_heavy_bytecode(salt: int = 0) -> Tuple[bytes, bytes]:
    """Generate contracts optimized for SLOAD benchmarking."""
    # Runtime bytecode that performs many SLOAD operations
    runtime_bytecode = bytearray()

    # Store some values during deployment
    for i in range(10):
        # PUSH1 value, PUSH1 key, SSTORE
        runtime_bytecode.extend([0x60, i * 2, 0x60, i, 0x55])

    # Main runtime: series of SLOAD operations
    for i in range(100):
        # PUSH1 key, SLOAD, POP
        runtime_bytecode.extend([0x60, i % 10, 0x54, 0x50])

    # Final STOP
    runtime_bytecode.append(0x00)

    # Create init code that deploys this runtime
    runtime_size = len(runtime_bytecode)
    init_size = 13

    init_code = bytearray()
    init_code.extend(
        [
            0x61,
            (runtime_size >> 8) & 0xFF,
            runtime_size & 0xFF,  # PUSH2 runtime_size
            0x60,
            init_size,  # PUSH1 init_size
            0x60,
            0x00,  # PUSH1 0
            0x39,  # CODECOPY
            0x61,
            (runtime_size >> 8) & 0xFF,
            runtime_size & 0xFF,  # PUSH2 runtime_size
            0x60,
            0x00,  # PUSH1 0
            0xF3,  # RETURN
        ]
    )

    full_init_code = bytes(init_code) + bytes(runtime_bytecode)
    return full_init_code, keccak(full_init_code)


def select_contract_type() -> str:
    """Interactive contract type selection."""
    print("\n=== Contract Type Selection ===")
    print("Select the type of contracts to deploy:\n")

    options = list(CONTRACT_DESCRIPTIONS.keys())
    for i, (key, desc) in enumerate(CONTRACT_DESCRIPTIONS.items(), 1):
        print(f"{i}. {key}: {desc}")

    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(options)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                selected = options[idx]
                print(f"\nSelected: {selected}")
                return selected
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)


def get_bytecode_generator(contract_type: str, max_code_size: int):
    """Get the appropriate bytecode generator for the contract type.

    Args:
        contract_type: Type of contract to generate
        max_code_size: Maximum contract size in bytes
    """
    if contract_type == ContractType.MAX_SIZE_24KB:
        return lambda salt: generate_max_size_bytecode(salt, max_code_size)
    elif contract_type == ContractType.SLOAD_HEAVY:
        return lambda salt: generate_sload_heavy_bytecode(salt)
    else:
        print(f"Error: No generator implemented for {contract_type}")
        if contract_type == ContractType.CUSTOM:
            print("Custom bytecode deployment not yet implemented")
        sys.exit(1)


def deploy_factory(rpc_url: str) -> str:
    """Deploy CREATE2 factory if needed."""
    print("\nDeploying CREATE2 factory...")

    try:
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
                return factory_address

        print("Could not extract factory address from deployment output")
        sys.exit(1)

    except Exception as e:
        print(f"Error deploying factory: {e}")
        sys.exit(1)


def deploy_contracts(
    rpc_url: str,
    num_contracts: int,
    contract_type: str,
    factory_address: Optional[str] = None,
    max_code_size: int = 24576,
):
    """Deploy contracts using CREATE2 factory pattern."""
    # Connect to Geth
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Failed to connect to {rpc_url}")
        sys.exit(1)

    test_account = w3.eth.accounts[0]
    print(f"Using test account: {test_account}")
    print(f"Balance: {w3.eth.get_balance(test_account) / 10**18:.4f} ETH")

    # Check/deploy factory
    if factory_address:
        factory_code = w3.eth.get_code(Web3.to_checksum_address(factory_address))
        if len(factory_code) > 0:
            print(f"\nUsing existing CREATE2 factory at: {factory_address}")
        else:
            print(f"\nNo factory found at {factory_address}")
            factory_address = deploy_factory(rpc_url)
    else:
        factory_address = deploy_factory(rpc_url)

    # Get bytecode generator
    bytecode_generator = get_bytecode_generator(contract_type, max_code_size)

    # Generate sample to show info
    sample_init_code, sample_hash = bytecode_generator(0)

    print(f"\nContract Type: {contract_type}")
    print(f"Init code size: {len(sample_init_code)} bytes")
    print(f"Sample init code hash: 0x{sample_hash.hex()}")

    confirm = input(f"\nProceed with deploying {num_contracts} {contract_type} contracts? (y/n): ")
    if confirm.lower() != "y":
        print("Deployment cancelled")
        sys.exit(0)

    # Deploy contracts
    print(f"\nDeploying {num_contracts} {contract_type} contracts using CREATE2...")

    deployed = []
    init_code_hashes: Dict[str, List[int]] = {}  # Track different init code hashes if they vary

    for salt in range(num_contracts):
        if salt % 100 == 0:
            print(f"Progress: {salt}/{num_contracts}")

        # Generate bytecode for this specific salt
        full_init_code, init_code_hash = bytecode_generator(salt)

        # Track unique init code hashes
        hash_hex = init_code_hash.hex()
        if hash_hex not in init_code_hashes:
            init_code_hashes[hash_hex] = []
        init_code_hashes[hash_hex].append(salt)

        # Factory expects: salt (32 bytes) + bytecode
        call_data = salt.to_bytes(32, "big") + full_init_code

        try:
            tx_hash = w3.eth.send_transaction(
                {
                    "from": test_account,
                    "to": factory_address,
                    "data": bytes.fromhex(call_data.hex()),
                    "gas": 10000000,
                }
            )

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10)

            if receipt["status"] == 1:
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

        print(f"\n=== Configuration for {contract_type} tests ===")
        print(f'CONTRACT_TYPE = "{contract_type}"')
        print(f'FACTORY_ADDRESS = Address("{factory_address}")')

        if len(init_code_hashes) == 1:
            # All contracts have the same init code hash
            hash_hex = list(init_code_hashes.keys())[0]
            print(f'INIT_CODE_HASH = bytes.fromhex("{hash_hex}")')
        else:
            # Multiple init code hashes (rare but possible)
            print("# Multiple init code hashes detected:")
            for hash_hex, salts in init_code_hashes.items():
                print(f"# Hash {hash_hex[:8]}... used for salts: {salts[:5]}...")

        print(f"NUM_DEPLOYED_CONTRACTS = {len(deployed)}")

        # Save configuration to file
        config_file = f"bloatnet_config_{contract_type}.txt"
        with open(config_file, "w") as f:
            f.write(f"# Configuration for {contract_type} benchmarks\n")
            f.write(f'CONTRACT_TYPE = "{contract_type}"\n')
            f.write(f'FACTORY_ADDRESS = Address("{factory_address}")\n')
            if len(init_code_hashes) == 1:
                hash_hex = list(init_code_hashes.keys())[0]
                f.write(f'INIT_CODE_HASH = bytes.fromhex("{hash_hex}")\n')
            f.write(f"NUM_DEPLOYED_CONTRACTS = {len(deployed)}\n")

        print(f"\nConfiguration saved to: {config_file}")


def main():
    """Execute the deployment script."""
    parser = argparse.ArgumentParser(description="Deploy bloatnet contracts using CREATE2")
    parser.add_argument(
        "--num-contracts",
        type=int,
        default=100,
        help="Number of contracts to deploy",
    )
    parser.add_argument(
        "--rpc-url",
        default="http://127.0.0.1:8545",
        help="RPC URL",
    )
    parser.add_argument(
        "--factory-address",
        default=None,
        help="CREATE2 factory address (deploys new one if not provided)",
    )
    parser.add_argument(
        "--max-code-size",
        type=int,
        default=24576,
        help="Maximum contract code size in bytes (default: 24576 for mainnet/Prague fork)",
    )

    args = parser.parse_args()

    # Always run in interactive mode - user selects contract type
    contract_type = select_contract_type()

    deploy_contracts(
        args.rpc_url,
        args.num_contracts,
        contract_type,
        args.factory_address,
        args.max_code_size,
    )


if __name__ == "__main__":
    main()
