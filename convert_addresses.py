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

FALSE_POSITIVE_TESTS = {
  # possible false positives to check
  "staticcall_createfailsFiller.json",
  "createInitFail_OOGduringInit2Filler.json",
  "createInitFail_OOGduringInitFiller.json",
  "createNameRegistratorPreStore1NotEnoughGasFiller.json",
  # definite false positives
  "codesizeOOGInvalidSizeFiller.json",
}

INCOMPATIBLE_FILLERS = {
  "create2InitCodeSizeLimitFiller.yml",
  "createInitCodeSizeLimitFiller.yml",
  "creationTxInitCodeSizeLimitFiller.yml",
  "suicideNonConstFiller.yml",
  "createNonConstFiller.yml",
  "CrashingTransactionFiller.json",
  "measureGasFiller.yml",
  "operationDiffGasFiller.yml",
  "callcodeDynamicCodeFiller.json",
  "callcodeDynamicCode2SelfCallFiller.json",
  "callcodeInInitcodeToEmptyContractFiller.json",
  "callcodeInInitcodeToExistingContractFiller.json",
  "callcodeInInitcodeToExisContractWithVTransferNEMoneyFiller.json",
  "callcodeInInitcodeToExistingContractWithValueTransferFiller.json",
  "contractCreationMakeCallThatAskMoreGasThenTransactionProvidedFiller.json",
  "codesizeInitFiller.json",
  "codesizeValidFiller.json",
  "create2CodeSizeLimitFiller.yml",
  "createCodeSizeLimitFiller.yml",
  "createFailBalanceTooLowFiller.json",
  "createInitOOGforCREATEFiller.json",
  "createNameRegistratorPerTxsFiller.json",
  "createNameRegistratorPerTxsNotEnoughGasFiller.json",
  "createJS_NoCollisionFiller.json",
  "undefinedOpcodeFirstByteFiller.yml",
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
  "static_callcodecallcallcode_101_OOGMAfter2Filler.json",
  "delegatecallInInitcodeToEmptyContractFiller.json",
  "delegatecallInInitcodeToExistingContractFiller.json",
  "delegatecallInInitcodeToExistingContractOOGFiller.json",
  "delegatecodeDynamicCode2SelfCallFiller.json",
  "delegatecodeDynamicCodeFiller.json",
  "CreateAndGasInsideCreateFiller.json",
  "RawCreateGasFiller.json",
  "RawCreateGasMemoryFiller.json",
  "RawCreateGasValueTransferFiller.json",
  "RawCreateGasValueTransferMemoryFiller.json",
  "Transaction64Rule_integerBoundariesFiller.yml",
  "addressOpcodesFiller.yml",
  "baseFeeDiffPlacesFiller.yml",
  "eip2929-ffFiller.yml",
  "eip2929Filler.yml",
  "eip2929OOGFiller.yml",
  "gasCostJumpFiller.yml",
  "gasCostMemoryFiller.yml",
  "gasPriceDiffPlacesFiller.yml",
  "initCollidingWithNonEmptyAccountFiller.yml",
  "manualCreateFiller.yml",
  "storageCostsFiller.yml",
  "variedContextFiller.yml",
  "vitalikTransactionTestParisFiller.json",
  "extcodehashEmpty_ParisFiller.yml",
  "extCodeHashSelfInInitFiller.json",
  "extCodeHashSubcallSuicideCancunFiller.yml",
  "extCodeHashNewAccountFiller.json",
  "extCodeHashDeletedAccount1CancunFiller.yml",
  "extCodeHashDeletedAccount2CancunFiller.yml",
  "extCodeHashDeletedAccount3Filler.yml",
  "extCodeHashDeletedAccount4Filler.yml",
  "extCodeHashCreatedAndDeletedAccountStaticCallFiller.json",
  "extCodeHashCreatedAndDeletedAccountRecheckInOuterCallFiller.json",
  "dynamicAccountOverwriteEmpty_ParisFiller.yml",
  "extCodeHashDeletedAccountCancunFiller.yml",
  "extCodeHashDeletedAccountFiller.yml",
  "extCodeHashSubcallSuicideFiller.yml",
  "codeCopyZero_ParisFiller.yml",
  "createEmptyThenExtcodehashFiller.json",
  "extCodeHashInInitCodeFiller.json",
  "extCodeHashSelfFiller.json",
  "contractCreationOOGdontLeaveEmptyContractViaTransactionFiller.json",
}
DO_NOT_CONVERT_FILLERS = FALSE_POSITIVE_TESTS | INCOMPATIBLE_FILLERS

DO_NOT_TAG_ADDRESSES = {
  "transStorageResetFiller.yml" : {"000000000000000000000000000000003f8390d5"},
  "transStorageOKFiller.yml" : {
    "000000000000000000000000000000005d7935df",
    "00000000000000000000000000000000000057a7", 
    "00000000000000000000000000000000c54b5829", 
    "000000000000000000000000000000007f9317bd", 
    "000000000000000000000000000000000000add1", 
    "000000000000000000000000000000007074a486",
    "00000000000000000000000000000000264bb86a",
    "000000000000000000000000000000005114e2c8",
    "00000000000000000000000000000000ca11bacc",
    "00000000000000000000000000000000c1c922f1",
    "000000000000000000000000000000006e3a7204",
    "00000000000000000000000000000000ebd141d5",
  },
  "invalidAddrFiller.yml" : {"0000000000000000000000000000000000dead01", "0000000000000000000000000000000000dead02"},
}

SHORT_NAME_FILLERS = {
  "transStorageResetFiller.yml",
  "invalidAddrFiller.yml",
  "precompsEIP2929CancunFiller.yml",
  "addressOpcodesFiller.yml",
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
    "modexpFiller.json",
    "returndatacopyPythonBug_Tue_03_48_41-1432Filler.json",
}

# Fillers that should skip entropy validation entirely
# These tests are deemed safe to convert addresses even if they don't pass entropy check
VALIDATE_ADDR_ENTROPY_IN_CODE = {
    # Add more fillers here that should skip entropy validation
    # "static_log_CallerFiller.json",
    # "OOGMAfterFiller.json",
    # "OOGMAfter2Filler.json",
    # "OOGMAfter_2Filler.json",
    # "OOGMAfter_3Filler.json",
    # "OOGMAfterFiller.json",
    # "OOGMAfter2Filler.json",
    # "OOGMBeforeFiller.json",
    # "SuicideEndFiller.json",
    # "SuicideEnd2Filler.json",
    # "SuicideMiddleFiller.json",
    # "OOGEFiller.json",
    # "static_CheckOpcodesFiller.json",
    # "static_CheckOpcodes2Filler.json",
    # "static_CheckOpcodes3Filler.json",
    # "static_CheckOpcodes4Filler.json",
    # "static_CheckOpcodes5Filler.json",
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
    
    def __init__(self, skip_precompile_check: bool = False, no_tags_in_code: bool = False, validate_addr_entropy_in_code: bool = False, filename: str = ""):
        self.address_mappings: Dict[str, str] = {}  # addr -> tag
        self.addresses_with_code: Set[str] = set()
        self.coinbase_addr: Optional[str] = None
        self.target_addr: Optional[str] = None
        self.skip_precompile_check = skip_precompile_check
        self.no_tags_in_code = no_tags_in_code
        self.validate_addr_entropy_in_code = validate_addr_entropy_in_code
        self.filename = filename
        
        # Get addresses that should not be tagged for this specific test file
        self.do_not_tag_addresses: Set[str] = set()
        if filename in DO_NOT_TAG_ADDRESSES:
            self.do_not_tag_addresses = DO_NOT_TAG_ADDRESSES[filename]
            
        # Check if this is a short name filler
        self.is_short_name_filler = any(kw in filename for kw in SHORT_NAME_FILLERS)
        self.short_name_mappings: Dict[str, str] = {}  # short_name -> tag
        
    def create_short_name(self, addr: str) -> Optional[str]:
        """Create a short name from an address by stripping leading/trailing zeros.
        
        Args:
            addr: Normalized address (40 chars, lowercase, no 0x prefix)
            
        Returns:
            Short name with 0x prefix, or None if the address is all zeros or too short
        """
        if not addr or len(addr) != 40:
            return None
            
        # Strip leading zeros
        stripped = addr.lstrip('0')
        
        # If nothing left after stripping leading zeros, it's all zeros
        if not stripped:
            return None
            
        # Strip trailing zeros
        stripped = stripped.rstrip('0')
        
        # If nothing left after stripping trailing zeros, or too short, return None
        if not stripped or len(stripped) < 2:
            return None
        
        return f"0x{stripped}"


    def collect_addresses(self, lines: List[str]) -> None:
        """First pass: collect all addresses from the file."""
        in_pre = False
        in_env = False
        in_transaction = False
        current_address = None
        in_code = False
        has_been_in_pre = False

        for line in lines:
            stripped = line.strip()
            stripped_no_spaces_or_quotes = stripped.replace('"', "").replace("'", "").replace(" ", "").replace(",", "")

            if (
              in_code 
              and len(stripped_no_spaces_or_quotes) > 0 
              and stripped_no_spaces_or_quotes[-1] in {"}", "]"} 
              or any(kw in stripped_no_spaces_or_quotes for kw in {"balance:", "nonce:", "storage:"})
            ):
                in_code = False
            
            # Track sections
            if "pre:" in stripped_no_spaces_or_quotes:
                has_been_in_pre = True
                in_pre = True
                in_env = False
                in_transaction = False
                in_code = False
            elif "env:" in stripped_no_spaces_or_quotes:
                in_pre = False
                in_env = True
                in_transaction = False
                in_code = False
            elif "transaction:" in stripped_no_spaces_or_quotes:
                in_pre = False
                in_env = False
                in_transaction = True
                in_code = False
            elif any(line.startswith(prefix) for prefix in {"expect:", "_info:"}):
                # New top-level section
                in_pre = False
                in_env = False
                in_transaction = False
                in_code = False
                
            # Track code subsection
            if "code:" in stripped_no_spaces_or_quotes:
                in_code = True
            elif current_address:
                in_code = False
                
            # In pre section, collect ALL addresses
            if in_pre:
                # Plain address
                match = re.match(r'^\s*[\'"]?([a-fA-F0-9]{40})[\'"]?:\s*$', line)
                if match:
                    addr = normalize_address(match.group(1))
                    # Skip addresses that should not be tagged for this test file
                    if addr in self.do_not_tag_addresses:
                        continue
                    if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                        self.address_mappings[addr] = None  # Will assign tag later
                        current_address = addr
                    continue
                    
                # Already tagged address - extract the address
                match = re.match(r'^\s*<(?:contract|eoa)(?::[^:]+)?:0x([a-fA-F0-9]{40})>:\s*$', line)
                if match:
                    addr = normalize_address(match.group(1))
                    # Skip addresses that should not be tagged for this test file
                    if addr in self.do_not_tag_addresses:
                        continue
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
            
            if not in_pre and has_been_in_pre:
                has_been_in_pre = False

            # Collect coinbase
            if in_env:
                match = re.match(r'^\s*currentCoinbase\s*:\s*(.+)$', line)
                if match:
                    value = match.group(1).strip()
                    # Extract address from value
                    addr_match = re.search(r'([a-fA-F0-9]{40})', value)
                    if addr_match:
                        addr = normalize_address(addr_match.group(1))
                        # Skip addresses that should not be tagged for this test file
                        if addr in self.do_not_tag_addresses:
                            continue
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
                        # Skip addresses that should not be tagged for this test file
                        if addr in self.do_not_tag_addresses:
                            continue
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
            stripped_no_spaces_or_quotes = stripped.replace('"', "").replace("'", "").replace(" ", "").replace(",", "")

            if (
              in_code 
              and len(stripped_no_spaces_or_quotes) > 0 
              and stripped_no_spaces_or_quotes[-1] in {"}", "]"} 
              or any(kw in stripped_no_spaces_or_quotes for kw in {"balance:", "nonce:", "storage:"})
            ):
                in_code = False
        
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
                    # Skip addresses that should not be tagged for this test file
                    if addr in self.do_not_tag_addresses:
                        continue
                    if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                        self.address_mappings[addr] = None
                        current_address = addr
                    continue
                    
                # Already tagged address in JSON
                match = re.search(r'"<(?:contract|eoa)(?::[^:]+)?:0x([a-fA-F0-9]{40})>"\s*:\s*\{', line)
                if match:
                    addr = normalize_address(match.group(1))
                    # Skip addresses that should not be tagged for this test file
                    if addr in self.do_not_tag_addresses:
                        continue
                    if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                        self.address_mappings[addr] = None
                        current_address = addr
            
            # Check if current address has code
            if current_address and in_code:
                # Use the stripped line to check for code content
                if "code:" in stripped_no_spaces_or_quotes:
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
                        # Skip addresses that should not be tagged for this test file
                        if addr in self.do_not_tag_addresses:
                            continue
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
                        # Skip addresses that should not be tagged for this test file
                        if addr in self.do_not_tag_addresses:
                            continue
                        if self.skip_precompile_check or addr not in PRECOMPILE_ADDRESSES:
                            self.target_addr = addr
                            self.address_mappings[addr] = None
                            
    def build_tags(self) -> None:
        """Build appropriate tags for each address."""
        for addr in self.address_mappings:
            # Skip coinbase if we're not converting it
            if addr == self.coinbase_addr and not CONVERT_COINBASE:
                continue
                
            if addr == KNOWN_SENDER_ADDRESS and addr not in self.addresses_with_code:
                self.address_mappings[addr] = f"<eoa:sender:0x{addr}>"
            elif addr == self.coinbase_addr:
                self.address_mappings[addr] = f"<eoa:coinbase:0x{addr}>"
            elif addr == self.target_addr and addr in self.addresses_with_code:
                self.address_mappings[addr] = f"<contract:target:0x{addr}>"
            elif addr in self.addresses_with_code:
                self.address_mappings[addr] = f"<contract:0x{addr}>"
            else:
                self.address_mappings[addr] = f"<eoa:0x{addr}>"
                
        # Build short name mappings for SHORT_NAME_FILLERS
        if self.is_short_name_filler:
            for addr, tag in self.address_mappings.items():
                if tag:  # Only if tag was assigned
                    short_name = self.create_short_name(addr)
                    if short_name:
                        self.short_name_mappings[short_name] = tag
                
    def convert_line(self, line: str, in_pre: bool = False, in_result: bool = False, in_code_or_tx_data_or_storage: bool = False) -> str:
        """Second pass: convert addresses to tags.
        
        IMPORTANT: This method should ONLY replace raw addresses with their tags.
        It should NEVER re-tag already tagged addresses to prevent double-tagging
        like <tag:<tag:0xaddr>>. The first pass identifies addresses and assigns
        tags. This second pass finds those raw addresses in the content and 
        replaces them with their assigned tags.
        """
        original_line = line
        stripped = line.strip()

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
            if stripped.startswith(f'{addr}:') or stripped.startswith(f'0x{addr}:'):
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
            if not is_address_key and not is_transaction_to and not in_pre and not in_result and self.validate_addr_entropy_in_code and calculate_entropy(addr) < 0.5:
                continue
                
            # Skip replacements in code/storage if no_tags_in_code is set
            if self.no_tags_in_code and in_code_or_tx_data_or_storage:
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
                
        # Replace short names with tags for SHORT_NAME_FILLERS
        if self.is_short_name_filler and self.short_name_mappings:
            # Sort short names by length (longest first) to avoid partial replacements
            sorted_short_names = sorted(self.short_name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
            
            for short_name, tag in sorted_short_names:
                # Skip if line already contains this exact tag to prevent double-tagging
                if tag in line:
                    continue
                    
                # Only replace short names in code/storage values, not in address keys
                if not is_address_key:
                    # Look for the short name in the line (case-insensitive)
                    if short_name.lower() in line.lower():
                        # Replace with exact case matching first, then case-insensitive
                        if short_name in line:
                            line = line.replace(short_name, tag)
                        else:
                            # Case-insensitive replacement
                            line = re.sub(re.escape(short_name), tag, line, flags=re.IGNORECASE)
        
        return line


def convert_json_file(file_path: str) -> bool:
    """Convert a single JSON file using line-by-line processing."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Check if this file should skip precompile checks
        filename = Path(file_path).name
        skip_precompile_check = filename in DISABLE_PRECOMPILE_CHECK_FILLERS
        no_tags_in_code = any(kw in filename for kw in NO_TAGS_IN_CODE)
        validate_addr_entropy_in_code = any(kw in filename for kw in VALIDATE_ADDR_ENTROPY_IN_CODE)
        
        converter = SimpleAddressConverter(skip_precompile_check=skip_precompile_check, no_tags_in_code=no_tags_in_code, validate_addr_entropy_in_code=validate_addr_entropy_in_code, filename=filename)
        
        # First pass: collect addresses
        converter.collect_addresses_json(lines)
        
        # Build tags
        converter.build_tags()
        
        if not converter.address_mappings:
            return False
            
        new_lines = []
        in_pre = False
        in_result = False
        in_code_or_tx_data_or_storage = False
        
        for line in lines:
            stripped = line.strip()
            stripped_no_spaces_or_quotes = stripped.replace('"', "").replace("'", "").replace(" ", "")
            
            if any(kw in stripped_no_spaces_or_quotes for kw in {"env:", "transaction:", "expect:", "}", "]", "secretKey:", "to:", "value:"}):
                in_code_or_tx_data_or_storage = False
            
            # Track sections
            if "pre:" in stripped_no_spaces_or_quotes:
                in_pre = True
                in_result = False
                in_code_or_tx_data_or_storage = False
            elif "result:" in stripped_no_spaces_or_quotes:
                in_result = True
                in_pre = False
                in_code_or_tx_data_or_storage = False
            elif any(kw in stripped_no_spaces_or_quotes for kw in {"code:", "data:", "storage:", "raw:"}):
                in_code_or_tx_data_or_storage = True
            elif any(kw in stripped_no_spaces_or_quotes for kw in {"env:", "transaction:", "_info:"}):
                in_code_or_tx_data_or_storage = False
                in_pre = False
                in_result = False


            new_line = converter.convert_line(line, in_pre=in_pre, in_result=in_result, in_code_or_tx_data_or_storage=in_code_or_tx_data_or_storage)
            new_lines.append(new_line)
            
            if len(stripped_no_spaces_or_quotes) > 0 and stripped_no_spaces_or_quotes[-1] in {"}", "]"}:
                in_code_or_tx_data_or_storage = False
        
        # Write back
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
            
        return True
        
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return False


def convert_yaml_file(file_path: str) -> bool:
    """Convert a single YAML file."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Check if this file should skip precompile checks
        filename = Path(file_path).name
        skip_precompile_check = filename in DISABLE_PRECOMPILE_CHECK_FILLERS
        no_tags_in_code = filename in NO_TAGS_IN_CODE
        validate_addr_entropy_in_code = any(kw in filename for kw in VALIDATE_ADDR_ENTROPY_IN_CODE)
        
        converter = SimpleAddressConverter(skip_precompile_check=skip_precompile_check, no_tags_in_code=no_tags_in_code, validate_addr_entropy_in_code=validate_addr_entropy_in_code, filename=filename)
        
        # First pass: collect addresses
        converter.collect_addresses(lines)
        
        # Build tags
        converter.build_tags()
        
        if not converter.address_mappings:
            return False
            
        # Second pass: convert (track sections for YAML)
        new_lines = []
        in_pre = False
        in_result = False
        in_code_or_tx_data_or_storage = False

        for line in lines:
            stripped = line.strip()
            stripped_no_spaces_or_quotes = stripped.replace('"', "").replace("'", "").replace(" ", "")
            
            if any(kw in stripped_no_spaces_or_quotes for kw in {"env:", "transaction:", "expect:", "}", "]", "secretKey:", "to:", "value:"}):
                in_code_or_tx_data_or_storage = False

            # Track sections
            if "pre:" in stripped_no_spaces_or_quotes:
                in_pre = True
                in_result = False
                in_code_or_tx_data_or_storage = False
            elif "result:" in stripped_no_spaces_or_quotes:
                in_result = True
                in_pre = False
                in_code_or_tx_data_or_storage = False
            elif any(kw in stripped_no_spaces_or_quotes for kw in {"code:", "data:", "storage:", "raw:"}):
                in_code_or_tx_data_or_storage = True
            elif any(kw in stripped_no_spaces_or_quotes for kw in {"env:", "transaction:", "_info:"}):
                in_code_or_tx_data_or_storage = False
                in_pre = False
                in_result = False

            new_line = converter.convert_line(line, in_pre=in_pre, in_result=in_result)
            new_lines.append(new_line)

            if len(stripped_no_spaces_or_quotes) > 0 and stripped_no_spaces_or_quotes[-1] in {"}", "]"}:
                in_code_or_tx_data_or_storage = False
            
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
    parser.add_argument('path', nargs='?', default='tests/static', help='Path to search for filler files')
    args = parser.parse_args()
    
    # Check if path is a single file or directory
    path = Path(args.path)
    yaml_files = []
    json_files = []
    
    if path.is_file():
        if path.name.endswith('Filler.yml') and path.name not in DO_NOT_CONVERT_FILLERS:
            yaml_files = [path]
        elif path.name.endswith('Filler.json') and path.name not in DO_NOT_CONVERT_FILLERS:
            json_files = [path]
    else:
        yaml_files = list(path.rglob('*Filler.yml'))
        json_files = list(path.rglob('*Filler.json'))
        yaml_files = [file for file in yaml_files if file.name not in DO_NOT_CONVERT_FILLERS]
        json_files = [file for file in json_files if file.name not in DO_NOT_CONVERT_FILLERS]
        
    print(f"Found {len(yaml_files)} YAML filler files")
    print(f"Found {len(json_files)} JSON filler files")
    
    # Convert files
    converted_yaml = 0
    converted_json = 0
    
    # Convert YAML files
    for file_path in yaml_files:
        if convert_yaml_file(str(file_path)):
            converted_yaml += 1
            print(f"Converted YAML: {file_path}")
    
    # Convert JSON files
    for file_path in json_files:
        if convert_json_file(str(file_path)):
            converted_json += 1
            print(f"Converted JSON: {file_path}")
    
    print(f"\nSummary: Converted {converted_yaml} YAML files and {converted_json} JSON files")


if __name__ == '__main__':
    main()