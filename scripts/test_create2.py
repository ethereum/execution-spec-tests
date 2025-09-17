#!/usr/bin/env python3
"""Test CREATE2 factory deployment."""

from web3 import Web3
from eth_utils import keccak

# Connect to Geth
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
if not w3.is_connected():
    print("Failed to connect to Geth")
    exit(1)

test_account = w3.eth.accounts[0]
print(f"Using test account: {test_account}")
print(f"Balance: {w3.eth.get_balance(test_account) / 10**18:.4f} ETH")

# Simple CREATE2 factory that returns the deployed address
factory_bytecode = (
    # Constructor: return runtime code
    "60" + "1f"  # PUSH1 0x1F (runtime size = 31)
    "80"  # DUP1
    "60" + "0a"  # PUSH1 0x0A (runtime offset)
    "60" + "00"  # PUSH1 0x00 (memory dest)
    "39"  # CODECOPY
    "60" + "00"  # PUSH1 0x00 (return offset)
    "f3"  # RETURN

    # Runtime: minimal CREATE2
    "36"  # CALLDATASIZE
    "60" + "00"  # PUSH1 0x00
    "60" + "00"  # PUSH1 0x00
    "37"  # CALLDATACOPY (copy all calldata to memory)

    "60" + "00"  # PUSH1 0x00 (salt - using 0 for simplicity)
    "36"  # CALLDATASIZE (size of init code)
    "60" + "00"  # PUSH1 0x00 (offset in memory)
    "60" + "00"  # PUSH1 0x00 (value)
    "f5"  # CREATE2

    "60" + "00"  # PUSH1 0x00
    "52"  # MSTORE (store address at 0)
    "60" + "20"  # PUSH1 0x20
    "60" + "00"  # PUSH1 0x00
    "f3"  # RETURN (return address)
)

# Deploy factory
factory_tx = w3.eth.send_transaction({
    'from': test_account,
    'data': '0x' + factory_bytecode,
    'gas': 3000000
})

factory_receipt = w3.eth.wait_for_transaction_receipt(factory_tx)
if factory_receipt.status != 1:
    print("Failed to deploy factory")
    exit(1)

factory_address = factory_receipt.contractAddress
print(f"\nFactory deployed at: {factory_address}")

# Create simple contract bytecode (just returns 42)
simple_bytecode = "602a60005260206000f3"  # PUSH1 42, PUSH1 0, MSTORE, PUSH1 32, PUSH1 0, RETURN

# Deploy using factory
print("\nDeploying contract via CREATE2...")
deploy_tx = w3.eth.send_transaction({
    'from': test_account,
    'to': factory_address,
    'data': '0x' + simple_bytecode,
    'gas': 1000000
})

deploy_receipt = w3.eth.wait_for_transaction_receipt(deploy_tx)
print(f"Transaction status: {deploy_receipt.status}")

# Get return value (the deployed address)
result = w3.eth.call({
    'to': factory_address,
    'data': '0x' + simple_bytecode
})

if result:
    deployed_addr = '0x' + result[-20:].hex()
    print(f"Contract deployed at: {deployed_addr}")

    # Verify by checking code
    code = w3.eth.get_code(deployed_addr)
    print(f"Deployed code length: {len(code)} bytes")
else:
    print("No return value from factory")