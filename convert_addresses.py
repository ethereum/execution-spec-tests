#!/usr/bin/env python3
"""
Simple address converter for static test fillers.
Two-pass approach:
1. Collect all addresses and create mappings
2. Replace all occurrences with tags
"""

import re
import argparse
from typing import Dict, Set, Optional, List
from pathlib import Path

# Known secret key that maps to sender address
KNOWN_SECRET_KEY = '45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'
KNOWN_SENDER_ADDRESS = 'a94f5374fce5edbc8e2a8697c15331677e6ebf0b'

CONVERT_COINBASE = False

# Ethereum precompile addresses (0x01 through 0x11)
PRECOMPILE_ADDRESSES = {
    '0000000000000000000000000000000000000001',
    '0000000000000000000000000000000000000002',
    '0000000000000000000000000000000000000003',
    '0000000000000000000000000000000000000004',
    '0000000000000000000000000000000000000005',
    '0000000000000000000000000000000000000006',
    '0000000000000000000000000000000000000007',
    '0000000000000000000000000000000000000008',
    '0000000000000000000000000000000000000009',
    '000000000000000000000000000000000000000a',
    '000000000000000000000000000000000000000b',
    '000000000000000000000000000000000000000c',
    '000000000000000000000000000000000000000d',
    '000000000000000000000000000000000000000e',
    '000000000000000000000000000000000000000f',
    '0000000000000000000000000000000000000010',
    '0000000000000000000000000000000000000011',
}

INCOMPATIBLE_FILLERS = {
  "suicideNonConstFiller.yml",
  "createNonConstFiller.yml",
  "CrashingTransactionFiller.json",
  "invalidAddrFiller.yml",
  "measureGasFiller.yml",
  "operationDiffGasFiller.yml",
  "undefinedOpcodeFirstByteFiller.yml",
  "extCodeHashDeletedAccount3Filler.yml",
  "extCodeHashDeletedAccount4Filler.yml",
  "extCodeHashDeletedAccountCancunFiller.yml",
  "extCodeHashDeletedAccountFiller.yml",
  "extCodeHashSubcallSuicideFiller.yml",
  "block504980Filler.json",
  "static_CallEcrecover0Filler.json",
  "static_CallEcrecover0_completeReturnValueFiller.json",
  "static_CallEcrecover0_gas3000Filler.json",
  "static_CallEcrecover0_overlappingInputOutputFiller.json",
  "static_CallEcrecoverCheckLengthFiller.json",
  "static_CallEcrecover0_prefixed0Filler.json",
  "static_contractCreationMakeCallThatAskMoreGasThenTransactionProvidedFiller.json",
  "static_contractCreationOOGdontLeaveEmptyContractViaTransactionFiller.json",
  "callcodecallcallcode_101_SuicideMiddleFiller.json",
  "static_callcodecallcallcode_101_OOGMAfter2Filler.json"
}

# Fillers that should have precompile check disabled
# These tests intentionally use addresses that map to precompiles
DISABLE_PRECOMPILE_CHECK_FILLERS = {
    # "block504980Filler.json",
}

# Fillers where addresses are tagged in pre/result sections only
# No address replacement in code or storage values
NO_TAGS_IN_CODE = {
    # Add fillers here that should not have addresses replaced in code/storage
}

# Fillers that should skip entropy validation entirely
# These tests are deemed safe to convert addresses even if they don't pass entropy check
TAGS_IN_CODE_UNCHECKED = {
    # Add more fillers here that should skip entropy validation
    "static_log_CallerFiller.json",
    "OOGMAfterFiller.json",
    "OOGMAfter2Filler.json",
    "OOGMAfter_2Filler.json",
    "OOGMAfter_3Filler.json",
    "OOGMAfterFiller.json",
    "OOGMAfter2Filler.json",
    "OOGMBeforeFiller.json",
    "SuicideEndFiller.json",
    "SuicideEnd2Filler.json",
    "SuicideMiddleFiller.json",
    "OOGEFiller.json",
    "static_CheckOpcodesFiller.json",
    "static_CheckOpcodes2Filler.json",
    "static_CheckOpcodes3Filler.json",
    "static_CheckOpcodes4Filler.json",
    "static_CheckOpcodes5Filler.json",
}

def normalize_address(addr: str) -> str:
    """Normalize address to lowercase without 0x prefix."""
    if not addr:
        return addr
    addr = addr.strip().strip('"\'')
    if addr.startswith('0x') or addr.startswith('0X'):
        addr = addr[2:]
    return addr.lower()


def calculate_entropy(addr: str) -> float:
    """Calculate address entropy (0-1) to determine if it's too simple/mathematical."""
    if not addr or len(addr) != 40:
        return 0.0
    
    # Count unique characters
    unique_chars = len(set(addr))
    zero_count = addr.count('0')
    
    # Very simple addresses like 0x1000... or 0x2000...
    if unique_chars <= 3 and zero_count >= 35:
        return 0.1  # Too simple
    
    # Numerical patterns like 0x0000..., 0x1111..., 0x2222... (single digit repeated)
    if len(set(addr)) == 1 and addr[0] in '0123456789':
        return 0.1  # Too simple - numerical value
    
    # Test pattern addresses like 0xcccc... or 0xaaaa... (letters repeated)
    if len(set(addr)) == 1:
        return 0.8  # Clearly a test address
        
    return 0.5  # Default: replace it


class SimpleAddressConverter:
    """Simple two-pass converter."""
    
    def __init__(self, skip_precompile_check: bool = False, no_tags_in_code: bool = False, skip_entropy_check: bool = False):
        self.address_mappings: Dict[str, str] = {}  # addr -> tag
        self.addresses_with_code: Set[str] = set()
        self.coinbase_addr: Optional[str] = None
        self.target_addr: Optional[str] = None
        self.skip_precompile_check = skip_precompile_check
        self.no_tags_in_code = no_tags_in_code
        self.skip_entropy_check = skip_entropy_check
        
    def collect_addresses(self, lines: List[str]) -> None:
        """First pass: collect all addresses from the file."""
        in_pre = False
        in_env = False
        in_transaction = False
        current_address = None
        in_code = False
        
        for line in lines:
            stripped = line.strip()
            
            # Track sections
            if re.match(r'^pre:\s*$', stripped):
                in_pre = True
                in_env = False
                in_transaction = False
            elif re.match(r'^env:\s*$', stripped):
                in_pre = False
                in_env = True
                in_transaction = False
            elif re.match(r'^transaction:\s*$', stripped):
                in_pre = False
                in_env = False
                in_transaction = True
            elif re.match(r'^\w+:', stripped) and not line.startswith(' '):
                # New top-level section
                in_pre = False
                in_env = False
                in_transaction = False
                
            # Track code subsection
            if re.match(r'^\s*code:\s*', line):
                in_code = True
            elif re.match(r'^\s*\w+:', line) and current_address:
                in_code = False
                
            # In pre section, collect ALL addresses
            if in_pre:
                # Plain address
                match = re.match(r'^\s*([a-fA-F0-9]{40}):\s*$', line)
                if match:
                    addr = normalize_address(match.group(1))
                    if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                        self.address_mappings[addr] = None  # Will assign tag later
                        current_address = addr
                    continue
                    
                # Already tagged address - extract the address
                match = re.match(r'^\s*<(?:contract|eoa)(?::[^:]+)?:0x([a-fA-F0-9]{40})>:\s*$', line)
                if match:
                    addr = normalize_address(match.group(1))
                    if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                        self.address_mappings[addr] = None
                        current_address = addr
                        
                # Check if current address has code
                if current_address and in_code and ':' in line:
                    code_content = line.split(':', 1)[1].strip()
                    if code_content and code_content not in ['""', "''", '0x', "'0x'", '"0x"']:
                        self.addresses_with_code.add(current_address)
                elif current_address and in_code and ('|' in line or '>' in line):
                    self.addresses_with_code.add(current_address)
                    
            # Collect coinbase
            if in_env:
                match = re.match(r'^\s*currentCoinbase\s*:\s*(.+)$', line)
                if match:
                    value = match.group(1).strip()
                    # Extract address from value
                    addr_match = re.search(r'([a-fA-F0-9]{40})', value)
                    if addr_match:
                        addr = normalize_address(addr_match.group(1))
                        if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                            self.coinbase_addr = addr
                            if CONVERT_COINBASE:
                                self.address_mappings[addr] = None
                        
            # Collect target from transaction
            if in_transaction:
                match = re.match(r'^\s*to:\s*(.+)$', line)
                if match:
                    value = match.group(1).strip()
                    # Extract address from value
                    addr_match = re.search(r'([a-fA-F0-9]{40})', value)
                    if addr_match:
                        addr = normalize_address(addr_match.group(1))
                        if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                            self.target_addr = addr
                            self.address_mappings[addr] = None
                            
            # Check for sender address
            if KNOWN_SENDER_ADDRESS in self.address_mappings:
                # We found the sender address somewhere
                pass
                
    def collect_addresses_json(self, lines: List[str]) -> None:
        """First pass: collect all addresses from JSON file."""
        in_pre = False
        in_env = False
        in_transaction = False
        current_address = None
        in_code = False
        brace_depth = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track sections based on JSON keys BEFORE updating brace depth
            if '"pre"' in line and ':' in line:
                in_pre = True
                in_env = False
                in_transaction = False
            elif '"env"' in line and ':' in line:
                in_pre = False
                in_env = True
                in_transaction = False
            elif '"transaction"' in line and ':' in line:
                in_pre = False
                in_env = False
                in_transaction = True
            
            # Track brace depth to understand nesting
            brace_depth += line.count('{') - line.count('}')
            
            # Reset sections when returning to top level
            if brace_depth <= 1:
                # But only if we're not on a section header line
                if not ('"pre"' in line or '"env"' in line or '"transaction"' in line):
                    in_pre = False
                    in_env = False
                    in_transaction = False
                
            # Track code subsection
            if '"code"' in line and ':' in line:
                in_code = True
            elif in_code and '"' in line and ':' in line:
                in_code = False
                
            # In pre section, collect addresses as JSON keys
            if in_pre and not in_code:
                # Look for address as JSON key: "0x...": { or "...": {
                match = re.search(r'"(?:0x)?([a-fA-F0-9]{40})"\s*:\s*\{', line)
                if match:
                    addr = normalize_address(match.group(1))
                    if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                        self.address_mappings[addr] = None
                        current_address = addr
                    continue
                    
                # Already tagged address in JSON
                match = re.search(r'"<(?:contract|eoa)(?::[^:]+)?:0x([a-fA-F0-9]{40})>"\s*:\s*\{', line)
                if match:
                    addr = normalize_address(match.group(1))
                    if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                        self.address_mappings[addr] = None
                        current_address = addr
                        
            # Check if current address has code
            if current_address and in_code:
                # Use the stripped line to check for code content
                if stripped.startswith('"code"') and ':' in stripped:
                    # Check if it's not an empty code value
                    if stripped not in ['"code": "",', '"code": "0x",', '"code": null,', '"code" : "",', '"code" : "0x",', '"code" : null,']:
                        # Extract code value from the line
                        code_match = re.search(r'"code"\s*:\s*"([^"]+)"', line)
                        if code_match and code_match.group(1) not in ['', '0x']:
                            self.addresses_with_code.add(current_address)
                        
            # Collect coinbase in env
            if in_env:
                if '"currentCoinbase"' in line:
                    # Extract address from JSON value
                    addr_match = re.search(r':\s*"[^"]*([a-fA-F0-9]{40})[^"]*"', line)
                    if addr_match:
                        addr = normalize_address(addr_match.group(1))
                        if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                            self.coinbase_addr = addr
                            if CONVERT_COINBASE:
                                self.address_mappings[addr] = None
                            
            # Collect target from transaction
            if in_transaction:
                if '"to"' in line:
                    # Extract address from JSON value
                    addr_match = re.search(r':\s*"[^"]*([a-fA-F0-9]{40})[^"]*"', line)
                    if addr_match:
                        addr = normalize_address(addr_match.group(1))
                        if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                            self.target_addr = addr
                            self.address_mappings[addr] = None
                            
    def build_tags(self) -> None:
        """Build appropriate tags for each address."""
        for addr in self.address_mappings:
            # Skip coinbase if we're not converting it
            if addr == self.coinbase_addr and not CONVERT_COINBASE:
                continue
                
            if addr == KNOWN_SENDER_ADDRESS:
                self.address_mappings[addr] = f"<eoa:sender:0x{addr}>"
            elif addr == self.coinbase_addr:
                self.address_mappings[addr] = f"<eoa:coinbase:0x{addr}>"
            elif addr == self.target_addr and addr in self.addresses_with_code:
                self.address_mappings[addr] = f"<contract:target:0x{addr}>"
            elif addr in self.addresses_with_code:
                self.address_mappings[addr] = f"<contract:0x{addr}>"
            else:
                self.address_mappings[addr] = f"<eoa:0x{addr}>"
                
    def convert_line(self, line: str, in_pre: bool = False, in_result: bool = False) -> str:
        """Second pass: convert addresses to tags.
        
        IMPORTANT: This method should ONLY replace raw addresses with their tags.
        It should NEVER re-tag already tagged addresses to prevent double-tagging
        like <tag:<tag:0xaddr>>. The first pass identifies addresses and assigns
        tags. This second pass finds those raw addresses in the content and 
        replaces them with their assigned tags.
        """
        original_line = line
        
        # Check if this line contains an address as a key in pre/result sections
        # JSON Pattern: "address" : { or "0xaddress" : {
        # YAML Pattern: address: or 0xaddress:
        is_address_key = False
        for addr in self.address_mappings:
            # JSON format
            if f'"{addr}" : {{' in line or f'"0x{addr}" : {{' in line:
                is_address_key = True
                break
            # YAML format - check if line starts with the address followed by colon
            if line.strip().startswith(f'{addr}:') or line.strip().startswith(f'0x{addr}:'):
                is_address_key = True
                break
        
        # Check if this is a transaction "to" field
        is_transaction_to = '"to"' in line and ':' in line
        
        # Handle secretKey specially (works for both YAML and JSON)
        if 'secretKey' in line and KNOWN_SECRET_KEY.lower() in line.lower():
            # Only replace if not already tagged
            if f'<sender:key:0x{KNOWN_SECRET_KEY}>' not in line:
                # Replace with tag, preserving quotes
                if f'"0x{KNOWN_SECRET_KEY}"' in line:
                    line = line.replace(f'"0x{KNOWN_SECRET_KEY}"', f'"<sender:key:0x{KNOWN_SECRET_KEY}>"')
                elif f'"{KNOWN_SECRET_KEY}"' in line:
                    line = line.replace(f'"{KNOWN_SECRET_KEY}"', f'"<sender:key:0x{KNOWN_SECRET_KEY}>"')
                elif f"'0x{KNOWN_SECRET_KEY}'" in line:
                    line = line.replace(f"'0x{KNOWN_SECRET_KEY}'", f"'<sender:key:0x{KNOWN_SECRET_KEY}>'")
                elif f"'{KNOWN_SECRET_KEY}'" in line:
                    line = line.replace(f"'{KNOWN_SECRET_KEY}'", f"'<sender:key:0x{KNOWN_SECRET_KEY}>'")
                elif KNOWN_SECRET_KEY in line:
                    line = line.replace(KNOWN_SECRET_KEY, f'"<sender:key:0x{KNOWN_SECRET_KEY}>"')
                return line
                    
        # Sort addresses by length (longest first) to avoid partial replacements
        sorted_addresses = sorted(self.address_mappings.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Replace addresses with tags
        for addr, tag in sorted_addresses:
            if not tag:  # Safety check
                continue
                
            # CRITICAL: Skip if line already contains this exact tag to prevent double-tagging
            if tag in line:
                continue
                
            # Skip entropy check for:
            # 1. Address keys (pre/result sections)
            # 2. Transaction "to" fields  
            # 3. ANY address in pre or result sections
            
            # Check entropy only for values, not keys or special fields
            # Skip entropy check if skip_entropy_check flag is set
            if not self.skip_entropy_check and not is_address_key and not is_transaction_to and not in_pre and not in_result and calculate_entropy(addr) < 0.5:
                # Debug: print why we're skipping
                # print(f"  Skipping {addr} due to low entropy: {calculate_entropy(addr)}")
                continue
                
            # Skip replacements in code/storage if no_tags_in_code is set
            if self.no_tags_in_code and not is_address_key:
                # print(f"  Skipping {addr} due to no_tags_in_code flag")
                continue
                
            # Store positions where we've already made replacements to avoid overlaps
            
            # For JSON format with quotes
            if '"' in line:
                # Replace "0xADDR": with "<tag>":
                old_pattern = f'"0x{addr}":'
                new_pattern = f'"{tag}":'
                if old_pattern in line:
                    line = line.replace(old_pattern, new_pattern)
                    
                # Replace "ADDR": with "<tag>":
                old_pattern = f'"{addr}":'
                if old_pattern in line:
                    line = line.replace(old_pattern, new_pattern)
                    
                # Replace : "0xADDR" with : "<tag>"
                old_pattern = f': "0x{addr}"'
                new_pattern = f': "{tag}"'
                if old_pattern in line:
                    line = line.replace(old_pattern, new_pattern)
                    
                # Replace : "ADDR" with : "<tag>"
                old_pattern = f': "{addr}"'
                if old_pattern in line:
                    line = line.replace(old_pattern, new_pattern)
            
            # Simple approach: just replace the address with the tag
            # Make sure it's not already part of a tag
            if addr.lower() in line.lower():
                # Don't replace if address is followed by > (already in a tag)
                # Replace 0xADDR with tag (tag already includes 0x)
                line = re.sub(rf'0x{addr}(?!>)', tag, line, flags=re.IGNORECASE)
                
                # Also replace plain ADDR with tag (but not if followed by >)
                line = re.sub(rf'(?<!x){addr}(?!>)', tag, line, flags=re.IGNORECASE)
                
        return line


def convert_json_file(file_path: str, dry_run: bool = False) -> bool:
    """Convert a single JSON file using line-by-line processing."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Check if this file should skip precompile checks
        filename = Path(file_path).name
        skip_precompile_check = filename in DISABLE_PRECOMPILE_CHECK_FILLERS
        no_tags_in_code = filename in NO_TAGS_IN_CODE
        skip_entropy_check = any(kw in filename for kw in TAGS_IN_CODE_UNCHECKED)
        
        converter = SimpleAddressConverter(skip_precompile_check=skip_precompile_check, no_tags_in_code=no_tags_in_code, skip_entropy_check=skip_entropy_check)
        
        # First pass: collect addresses
        converter.collect_addresses_json(lines)
        
        # Build tags
        converter.build_tags()
        
        if not converter.address_mappings:
            return False
            
        if dry_run:
            print(f"\nFile: {file_path}")
            print("Address mappings:")
            for addr, tag in sorted(converter.address_mappings.items()):
                print(f"  {addr} -> {tag}")
            # Test conversion on lines with :raw
            print("\nTesting conversion on :raw lines:")
            for i, line in enumerate(lines):
                if ':raw' in line:
                    new_line = converter.convert_line(line, in_pre=False, in_result=False)
                    if new_line != line:
                        print(f"  Line {i+1}: CONVERTED")
                        print(f"    Old: {line.strip()[:100]}...")
                        print(f"    New: {new_line.strip()[:100]}...")
                    else:
                        # Check if any addresses should have been replaced
                        for addr in converter.address_mappings:
                            if addr in line.lower():
                                print(f"  Line {i+1}: MISSED address {addr}")
                                print(f"    Line: {line.strip()[:100]}...")
                                break
            return True
            
        # Second pass: convert (track sections for YAML)
        new_lines = []
        in_pre = False
        in_result = False
        
        for line in lines:
            stripped = line.strip()
            
            # Track sections
            if re.match(r'^pre:\s*$', stripped) or re.match(r'^\s+pre:\s*$', line):
                in_pre = True
                in_result = False
            elif re.match(r'^result:\s*$', stripped) or re.match(r'^\s+result:\s*$', line):
                in_pre = False
                in_result = True
            elif re.match(r'^\w+:', stripped) and not line.startswith(' '):
                # New top-level section
                in_pre = False
                in_result = False
            
            new_line = converter.convert_line(line, in_pre=in_pre, in_result=in_result)
            new_lines.append(new_line)
            
        # Write back
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
            
        return True
        
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return False


def convert_yaml_file(file_path: str, dry_run: bool = False) -> bool:
    """Convert a single YAML file."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Check if this file should skip precompile checks
        filename = Path(file_path).name
        skip_precompile_check = filename in DISABLE_PRECOMPILE_CHECK_FILLERS
        no_tags_in_code = filename in NO_TAGS_IN_CODE
        skip_entropy_check = any(kw in filename for kw in TAGS_IN_CODE_UNCHECKED)
        
        converter = SimpleAddressConverter(skip_precompile_check=skip_precompile_check, no_tags_in_code=no_tags_in_code, skip_entropy_check=skip_entropy_check)
        
        # First pass: collect addresses
        converter.collect_addresses(lines)
        
        # Build tags
        converter.build_tags()
        
        if not converter.address_mappings:
            return False
            
        if dry_run:
            print(f"\nFile: {file_path}")
            print("Address mappings:")
            for addr, tag in sorted(converter.address_mappings.items()):
                print(f"  {addr} -> {tag}")
            return True
            
        # Second pass: convert (track sections for YAML)
        new_lines = []
        in_pre = False
        in_result = False
        
        for line in lines:
            stripped = line.strip()
            
            # Track sections
            if re.match(r'^pre:\s*$', stripped) or re.match(r'^\s+pre:\s*$', line):
                in_pre = True
                in_result = False
            elif re.match(r'^result:\s*$', stripped) or re.match(r'^\s+result:\s*$', line):
                in_pre = False
                in_result = True
            elif re.match(r'^\w+:', stripped) and not line.startswith(' '):
                # New top-level section
                in_pre = False
                in_result = False
            
            new_line = converter.convert_line(line, in_pre=in_pre, in_result=in_result)
            new_lines.append(new_line)
            
        # Write back
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
            
        return True
        
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return False


def main():
    """Main conversion function."""
    parser = argparse.ArgumentParser(description='Convert addresses to tags in static test fillers')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('path', nargs='?', default='tests/static', help='Path to search for filler files')
    args = parser.parse_args()
    
    # Check if path is a single file or directory
    path = Path(args.path)
    yaml_files = []
    json_files = []
    
    if path.is_file():
        if path.name.endswith('Filler.yml') and path.name not in INCOMPATIBLE_FILLERS:
            yaml_files = [path]
        elif path.name.endswith('Filler.json') and path.name not in INCOMPATIBLE_FILLERS:
            json_files = [path]
    else:
        yaml_files = list(path.rglob('*Filler.yml'))
        json_files = list(path.rglob('*Filler.json'))
        yaml_files = [file for file in yaml_files if file.name not in INCOMPATIBLE_FILLERS]
        json_files = [file for file in json_files if file.name not in INCOMPATIBLE_FILLERS]
        
    print(f"Found {len(yaml_files)} YAML filler files")
    print(f"Found {len(json_files)} JSON filler files")
    
    # Convert files
    converted_yaml = 0
    converted_json = 0
    
    # Convert YAML files
    for file_path in yaml_files:
        if convert_yaml_file(str(file_path), args.dry_run):
            converted_yaml += 1
            if not args.dry_run:
                print(f"Converted YAML: {file_path}")
    
    # Convert JSON files
    for file_path in json_files:
        if convert_json_file(str(file_path), args.dry_run):
            converted_json += 1
            if not args.dry_run:
                print(f"Converted JSON: {file_path}")
    
    print(f"\nSummary: Converted {converted_yaml} YAML files and {converted_json} JSON files")


if __name__ == '__main__':
    main()