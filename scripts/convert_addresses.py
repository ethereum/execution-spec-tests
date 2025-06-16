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
from enum import Enum, auto
from ethereum_test_forks import Prague

class Section(Enum):
    """Represents the current section being parsed."""
    NONE = auto()
    PRE = auto()
    ENV = auto()
    TRANSACTION = auto()
    RESULT = auto()
    EXPECT = auto()

class Context(Enum):
    """Represents the current context within a section."""
    NORMAL = auto()
    CODE = auto()
    STORAGE = auto()

# Known secret key that maps to sender address
KNOWN_SECRET_KEY = '45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'
KNOWN_SENDER_ADDRESS = 'a94f5374fce5edbc8e2a8697c15331677e6ebf0b'

# don't convert default coinbase since this is the same used in python tests
# TODO: check if coinbase is affected in `result` section. If so, we need to tag it
#  to generate a dynamic address for it in both the `result` and `currentCoinbase` sections
CONVERT_COINBASE = False

PRECOMPILE_ADDRESSES = {pre.hex() for pre in Prague.precompiles()}

#TODO: check these manually for false positives
# callToSuicideThenExtcodehashFiller.json  -- hard-coded 000...00025

FALSE_POSITIVE_TESTS = {
  # possible false positives to check
  "staticcall_createfailsFiller.json",
  "createInitFail_OOGduringInit2Filler.json",
  "createInitFail_OOGduringInitFiller.json",
  "createNameRegistratorPreStore1NotEnoughGasFiller.json",
  # definite false positives
  "codesizeOOGInvalidSizeFiller.json",
  # "contractCreationOOGdontLeaveEmptyContractFiller.json",  # Temporarily enabling for testing
  "contractCreationOOGdontLeaveEmptyContractViaTransactionFiller.json",
  "createContractViaContractFiller.json",
  "createContractViaContractOOGInitCodeFiller.json",
  "createContractViaTransactionCost53000Filler.json",
}

# Path patterns for incompatible tests - can include full filenames or directory patterns
INCOMPATIBLE_PATH_PATTERNS = {
  # Exact filenames (existing)
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
  "createJS_NoCollisionFiller.json",
  "createNameRegistratorPerTxsFiller.json",
  "createNameRegistratorPerTxsNotEnoughGasFiller.json",
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
  "CreateAndGasInsideCreateWithMemExpandingCallsFiller.json",
  "codeCopyZero_ParisFiller.yml",
  "createEmptyThenExtcodehashFiller.json",
  "extCodeHashInInitCodeFiller.json",
  "extCodeHashSelfFiller.json",
  "contractCreationOOGdontLeaveEmptyContractViaTransactionFiller.json",
  "CallContractToCreateContractAndCallItOOGFiller.json",
  "CallContractToCreateContractOOGBonusGasFiller.json",
  "CallContractToCreateContractWhichWouldCreateContractIfCalledFiller.json",
  "CallContractToCreateContractWhichWouldCreateContractInInitCodeFiller.json",
  "CallTheContractToCreateEmptyContractFiller.json",
  "OutOfGasContractCreationFiller.json",
  "OutOfGasPrefundedContractCreationFiller.json",
  "TransactionCreateStopInInitcodeFiller.json",
  "bufferFiller.yml",
  "bufferSrcOffsetFiller.yml",
  "callDataCopyOffsetFiller.json",
  "oogFiller.yml",
  "CALLCODEEcrecover0Filler.json",
  "CALLCODEEcrecoverV_prefixed0Filler.json",
  "CALLCODEEcrecover0_completeReturnValueFiller.json",
  "CALLCODEEcrecover0_overlappingInputOutputFiller.json",
  "CALLCODEEcrecover0_gas3000Filler.json",
  "CallEcrecover0_completeReturnValueFiller.json",
  "CallEcrecoverCheckLengthFiller.json",
  "CallEcrecover0_gas3000Filler.json",
  "CallEcrecover0Filler.json",
  "CallEcrecover0_overlappingInputOutputFiller.json",
  "CallEcrecoverV_prefixed0Filler.json",
  "ecrecoverShortBuffFiller.yml",
  "modexp_0_0_0_20500Filler.json",
  "modexp_0_0_0_22000Filler.json",
  "modexp_0_0_0_25000Filler.json",
  "modexp_0_0_0_35000Filler.json",
  "Create1000ShnghaiFiller.json",
  "QuadraticComplexitySolidity_CallDataCopyFiller.json",
  "testRandomTestFiller.json",
  "randomStatetest173Filler.json",
  "randomStatetest107Filler.json",
  "randomStatetest137Filler.json",
  "randomStatetest246Filler.json",
  "randomStatetest263Filler.json",
  "randomStatetest368Filler.json",
  "randomStatetest308Filler.json",
  "randomStatetest362Filler.json",
  "randomStatetest267Filler.json",
  "randomStatetest80Filler.json",
  "randomStatetest64Filler.json",
  "randomStatetest372Filler.json",
  "randomStatetest73Filler.json",
  "randomStatetest367Filler.json",
  "randomStatetest41Filler.json",
  "randomStatetest66Filler.json",
  "randomStatetest406Filler.json",
  "randomStatetest388Filler.json",
  "randomStatetest437Filler.json",
  "randomStatetest473Filler.json",
  "randomStatetest502Filler.json",
  "randomStatetest526Filler.json",
  "randomStatetest545Filler.json",
  "randomStatetest537Filler.json",
  "randomStatetest564Filler.json",
  "revertRetDataSizeFiller.yml",
  "returndatacopy_0_0_following_successful_createFiller.json",
  "RevertPrefoundFiller.json",
  "RevertPrefoundEmpty_ParisFiller.json",
  "RevertDepthCreateOOGFiller.json",
  "costRevertFiller.yml",
  "LoopCallsDepthThenRevert2Filler.json",
  "LoopCallsDepthThenRevert3Filler.json",
  "CreateContractFromMethodFiller.json",
  "ByZeroFiller.json",
  "RecursiveCreateContractsCreate4ContractsFiller.json",
  "RecursiveCreateContractsFiller.json",
  "TestCryptographicFunctionsFiller.json",
  "StackDepthLimitSECFiller.json",
  "eoaEmptyParisFiller.yml",
  "deploymentErrorFiller.json",
  "sstore_0to",  # Note: many tests match this pattern
  "sstore_Xto",  # Note: many tests match this pattern
  "sstore_changeFromExternalCallInInitCodeFiller.json",
  "stackOverflowM1DUPFiller.json",
  "stackOverflowM1Filler.json",
  "stackOverflowM1PUSHFiller.json",
  "stackOverflowSWAPFiller.json",
  "stacksanitySWAPFiller.json",

  # TODO: See if any of these can be turned on with fine tuning
  "static_CREATE_EmptyContractAndCallIt_0weiFiller.json",
  "static_CREATE_EmptyContractWithStorageAndCallIt_0weiFiller.json",
  "static_RawCallGasAskFiller.json",
  "static_InternalCallStoreClearsOOGFiller.json",
  "StaticcallToPrecompileFromCalledContractFiller.yml",
  "static_callCreate2Filler.json",
  "static_callCreate3Filler.json",
  "static_CallContractToCreateContractOOGFiller.json",
  "StaticcallToPrecompileFromContractInitializationFiller.yml",
  "StaticcallToPrecompileFromTransactionFiller.yml",
  "CallWithNOTZeroValueToPrecompileFromContractInitializationFiller.yml",
  "CallWithZeroValueToPrecompileFromContractInitializationFiller.yml",
  "CallWithZeroValueToPrecompileFromTransactionFiller.yml",
  "CallWithZeroValueToPrecompileFromCalledContractFiller.yml",
  "DelegatecallToPrecompileFromCalledContractFiller.yml",
  "CallcodeToPrecompileFromContractInitializationFiller.yml",
  "CallcodeToPrecompileFromCalledContractFiller.yml",
  "CallcodeToPrecompileFromTransactionFiller.yml",
  "DelegatecallToPrecompileFromContractInitializationFiller.yml",
  "DelegatecallToPrecompileFromTransactionFiller.yml",
  "CreateHashCollisionFiller.json",
  "createNameRegistratorZeroMem2Filler.json",
  "createNameRegistratorZeroMemFiller.json",
  "doubleSelfdestructTestFiller.yml",
  "createNameRegistratorZeroMemExpansionFiller.json",
  "createNameRegistratorFiller.json",
  "multiSelfdestructFiller.yml",
  "suicideCallerAddresTooBigRightFiller.json",
  "createNameRegistratorPerTxs",  # Note: many tests match this pattern
  "addmodFiller.yml",
  "addFiller.yml",
  "divFiller.yml",
  "expFiller.yml",
  "modFiller.yml",
  "mulmodFiller.yml",
  "sdivFiller.yml",
  "signextendFiller.yml",
  "mulFiller.yml",
  "notFiller.yml",
  "subFiller.yml",
  "smodFiller.yml",
  "byteFiller.yml",
  "iszeroFiller.yml",
  "eqFiller.yml",
  "ltFiller.yml",
  "sgtFiller.yml",
  "sltFiller.yml",
  "gtFiller.yml",
  "xorFiller.yml",
  "orFiller.yml",
  "andFiller.yml",
  "codecopyFiller.yml",
  "jumpFiller.yml",
  "gasFiller.yml",
  "jumpToPushFiller.yml",
  "jumpiFiller.yml",
  "loopsConditionalsFiller.yml",
  "msizeFiller.yml",
  "mstoreFiller.yml",
  "mstore8Filler.yml",
  "mloadFiller.yml",
  "sstore_sloadFiller.yml",
  "returnFiller.yml",
  "pcFiller.yml",
  "popFiller.yml",
  "log0Filler.yml",
  "log1Filler.yml",
  "log2Filler.yml",
  "log3Filler.yml",
  "log4Filler.yml",
  "blockInfoFiller.yml",
  "envInfoFiller.yml",
  "sha3Filler.yml",
  "suicideFiller.yml",
  "swapFiller.yml",
  "Opcodes_TransactionInitFiller.json",
  "CreateMessageSuccessFiller.json",
  "CreateTransactionSuccessFiller.json",
  "EmptyTransaction3Filler.json",
  "SuicidesAndInternalCallSuicidesBonusGasAtCallFiller.json",
  "SuicidesStopAfterSuicideFiller.json",
  "SuicidesAndInternalCallSuicidesBonusGasAtCallFailedFiller.json",
  "SuicidesAndInternalCallSuicidesSuccessFiller.json",
  "StoreGasOnCreateFiller.json",
  "TransactionSendingToEmptyFiller.json",

  # Directory patterns (examples - add as needed)
  "/stCreate2/",
  "/stCreateTest/",
  "/stRecursiveCreate/",
  "/stWalletTest/",
  "/stZeroKnowledge/",
  "/stZeroKnowledge2/",

  # TODO: See if these can be turned on with fine tuning
  "/stTimeConsuming/",
}

def is_incompatible_file(file_path: Path) -> bool:
    """Check if a file should be skipped based on filename or path patterns."""
    file_path_str = str(file_path)
    filename = file_path.name
    
    # Check if filename is in FALSE_POSITIVE_TESTS
    if filename in FALSE_POSITIVE_TESTS:
        return True
    
    # Check against all incompatible path patterns
    for pattern in INCOMPATIBLE_PATH_PATTERNS:
        # If pattern ends with '/', it's a directory pattern
        if pattern.endswith('/'):
            if pattern in file_path_str:
                return True
        # Otherwise, check if pattern matches filename or is in path
        elif pattern == filename or pattern in file_path_str:
            return True
    
    return False

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
  "OOGinReturnFiller.yml" : {"ccccccccccccccccccccccccccccccccccccccc1", "ccccccccccccccccccccccccccccccccccccccc2"},
  "callToSuicideThenExtcodehashFiller.json" : {"0000000000000000000000000000000000000025"},
  "doubleSelfdestructTouch_ParisFiller.yml" : {"0000000000000000000000000000000000e49701", "0000000000000000000000000000000000e49702"},
}

SHORT_NAME_FILLERS = {
  "transStorageResetFiller.yml",
  "invalidAddrFiller.yml",
  "precompsEIP2929CancunFiller.yml",
  "addressOpcodesFiller.yml",
  "coinbaseT01Filler.yml",
  "coinbaseT2Filler.yml",
  "doubleSelfdestructTouch_ParisFiller.yml",
  "tooLongReturnDataCopyFiller.yml",
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
    "/stZeroKnowledge",
    "modexp_modsize0_returndatasizeFiller.json",
    "RevertPrecompiledTouchExactOOG_ParisFiller.json",
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

# Fillers that should convert addresses with shouldnotexist in result section
# These tests use CREATE/CREATE2 and need shouldnotexist addresses to be converted
SHOULDNOTEXIST_NO_CONVERSION_FILLERS = {
    # Add more fillers here as needed
    "callToSuicideThenExtcodehashFiller.json",
}

# Fillers where addresses in storage keys should be replaced with tags
# By default, storage keys are not replaced to avoid issues
DONT_REPLACE_TAGS_IN_STORAGE_KEYS = {
    # Add fillers here that should have addresses replaced in storage keys
    # Example: tests that use addresses as storage keys intentionally
    # "randomStatetest383Filler.json",
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
    
    def __init__(self, filename: str = ""):
        self.filename = filename
        self.address_mappings: Dict[str, str] = {}  # addr -> tag
        self.pre_addresses: Set[str] = set()  # addresses from pre section
        self.addresses_with_code: Set[str] = set()
        self.creation_addresses: Set[str] = set()  # addresses from result section with shouldnotexist
        self.coinbase_addr: Optional[str] = None
        self.target_addr: Optional[str] = None
        self.is_json = filename.lower().endswith('.json')
        self.skip_precompile_check = any(kw in filename for kw in DISABLE_PRECOMPILE_CHECK_FILLERS)
        self.no_tags_in_code = any(kw in filename for kw in NO_TAGS_IN_CODE)
        self.validate_addr_entropy_in_code = any(kw in filename for kw in VALIDATE_ADDR_ENTROPY_IN_CODE)
        self.dont_convert_shouldnotexist = any(kw in filename for kw in SHOULDNOTEXIST_NO_CONVERSION_FILLERS)
        self.dont_replace_tags_in_storage_keys = any(kw in filename for kw in DONT_REPLACE_TAGS_IN_STORAGE_KEYS)
        
        # Get addresses that should not be tagged for this specific test file
        self.do_not_tag_addresses: Set[str] = set()
        if filename in DO_NOT_TAG_ADDRESSES:
            self.do_not_tag_addresses = DO_NOT_TAG_ADDRESSES[filename]
            
        # Check if this is a short name filler
        self.is_short_name_filler = any(kw in filename for kw in SHORT_NAME_FILLERS)
        self.short_name_mappings: Dict[str, str] = {}  # short_name -> tag
        
    def detect_section(self, line: str) -> Optional[Section]:
        """Detect which section a line indicates."""
        stripped = line.strip().replace('"', "").replace("'", "").replace(" ", "")
        
        if 'pre:' in stripped:
            return Section.PRE
        elif 'env:' in stripped:
            return Section.ENV
        elif 'transaction:' in stripped:
            return Section.TRANSACTION
        elif 'result:' in stripped:
            return Section.RESULT
        elif 'expect:' in stripped or '_info:' in stripped:
            return Section.EXPECT
        return None
    
    def detect_context_change(self, line: str) -> Optional[Context]:
        """Detect if line changes the context."""
        stripped = line.strip().replace('"', "").replace("'", "").replace(" ", "")
        
        # Check for context-changing keywords
        if any(kw in stripped for kw in {"code:", "data:", "raw:"}):
            return Context.CODE
        elif "storage:" in stripped:
            # If storage is followed by {}, it's an empty storage and context should stay NORMAL
            if "storage:{}" in stripped or re.search(r'storage:\s*\{\s*\}', line):
                return None  # Don't change context for empty storage
            return Context.STORAGE
        elif any(kw in stripped for kw in {"balance:", "nonce:"}):
            return Context.NORMAL
        return None
        
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
        """First pass: collect all addresses from the file (unified for JSON and YAML)."""
        current_section = Section.NONE
        current_context = Context.NORMAL
        current_address = None
        current_result_address = None
        looking_for_shouldnotexist = False

        for line in lines:
            stripped = line.strip()
            stripped_no_spaces_or_quotes = stripped.replace('"', "").replace("'", "").replace(" ", "").replace(",", "")

            # Check for section changes
            new_section = self.detect_section(line)
            if new_section:
                current_section = new_section
                current_context = Context.NORMAL
                current_address = None
                current_result_address = None
                looking_for_shouldnotexist = False
            
            # Reset context when we see a new address key in pre/result sections
            # This handles YAML structure where addresses are top-level keys
            # Do this FIRST before any other context checks
            if current_section in [Section.PRE, Section.RESULT]:
                # Check if this line is an address key (40 hex chars followed by colon)
                if re.match(r'^\s*(?:0x)?[a-fA-F0-9]{40}\s*:', line, re.IGNORECASE):
                    current_context = Context.NORMAL
            
            # Reset context on closing braces
            if stripped and stripped[-1] in {"}", "]"}:
                current_context = Context.NORMAL
                
            # Only collect addresses from pre section
            if current_section == Section.PRE:
                # Look for address patterns (with or without quotes, with or without 0x prefix)
                # Matches: "address":, "0xaddress":, address:, 0xaddress:, <tag>:
                addr_match = None
                
                # Plain address pattern (40 hex chars followed by colon)
                # Handle both JSON format ("address":) and YAML format (address:)
                # Use word boundaries to ensure we match exactly 40 hex chars, not part of a longer string
                match = re.search(r'["\']?(?:0x)?(?<![a-fA-F0-9])([a-fA-F0-9]{40})(?![a-fA-F0-9])["\']?\s*:', line)
                if match:
                    addr_match = match
                else:
                    # Tagged address pattern
                    match = re.search(r'<(?:contract|eoa)(?::[^:]+)?:(?:0x)?([a-fA-F0-9]{40})>\s*:', line)
                    if match:
                        addr_match = match
                
                if addr_match:
                    addr = normalize_address(addr_match.group(1))
                    if addr not in self.do_not_tag_addresses:
                        self.address_mappings[addr] = None  # Will assign tag later
                        self.pre_addresses.add(addr)
                        current_address = addr
                    continue
                    
            # Check for addresses in result section only for shouldnotexist logic
            if current_section == Section.RESULT and current_context != Context.CODE:
                # Look for address keys in result section
                match = re.search(r'["\']?(?:0x)?(?<![a-fA-F0-9])([a-fA-F0-9]{40})(?![a-fA-F0-9])["\']?\s*:', line)
                if match:
                    current_result_address = normalize_address(match.group(1))
                    looking_for_shouldnotexist = True
                        
            # Check for shouldnotexist after setting current_result_address
            if looking_for_shouldnotexist and current_result_address:
                if "shouldnotexist:1" in stripped_no_spaces_or_quotes:
                    # Don't convert shouldnotexist addresses if enabled for this filler
                    if not self.dont_convert_shouldnotexist:
                        # Only now add to address_mappings and mark as creation address
                        self.address_mappings[current_result_address] = None
                        self.creation_addresses.add(current_result_address)
                    looking_for_shouldnotexist = False
                    current_result_address = None
                elif stripped and stripped[-1] in {"}", "]"}:
                    # End of address block without finding shouldnotexist - leave address hard-coded
                    looking_for_shouldnotexist = False
                    current_result_address = None
                        
            # Check if current address (from pre) has code
            if current_address and current_section == Section.PRE:
                # For YAML files, check both when we see the code: line and during CODE context
                if not self.is_json:
                    # First, check if this is the code: line itself
                    if 'code:' in stripped_no_spaces_or_quotes:
                        # Extract content after the colon
                        if ':' in line:
                            code_content = line.split(':', 1)[1].strip()
                            # Remove quotes and check if there's actual content
                            code_content = code_content.strip('\'"')
                            # Only consider it has code if it's not empty or "0x"
                            if (code_content and 
                                code_content not in ['', '0x', '0X', '{}', '[]'] and
                                (code_content in ['|', '>'] or len(code_content) > 2)):
                                self.addresses_with_code.add(current_address)
                    # Also check during CODE context for multi-line code
                    elif current_context == Context.CODE:
                        # Don't add if this line should change context back to NORMAL
                        if not any(kw in stripped_no_spaces_or_quotes for kw in {"balance:", "nonce:", "storage:"}):
                            if stripped and not stripped.startswith('#') and '{' not in stripped:
                                # Any non-empty, non-comment, non-brace line in code section indicates there's code
                                self.addresses_with_code.add(current_address)
                
                # For JSON files, check code lines directly
                elif self.is_json and ('"code":' in line or '"code" :' in line):
                    # Extract content after the colon
                    if ':' in line:
                        code_content = line.split(':', 1)[1].strip()
                        # Remove quotes and check if there's actual content
                        code_content = code_content.strip('\'"').strip(',')
                        if (code_content and 
                            code_content not in ['', '0x', '{}', '[]'] and
                            (not code_content.startswith('0x') or len(code_content) > 3)):  # More than just "0x"
                            self.addresses_with_code.add(current_address)
            
            if current_section == Section.ENV:
                coinbase_match = re.search(r'currentCoinbase:\s*["\']?[^"\']*?([a-fA-F0-9]{40})', stripped_no_spaces_or_quotes)
                if coinbase_match:
                    addr = normalize_address(coinbase_match.group(1))
                    if addr not in self.do_not_tag_addresses:
                        self.coinbase_addr = addr
                        if CONVERT_COINBASE and not self.address_mappings.get(addr):
                            self.address_mappings[addr] = None
                        
            if current_section == Section.TRANSACTION:
                if "to:" in stripped_no_spaces_or_quotes:
                    to_match = re.search(r'to:\s*["\']?[^"\']*?([a-fA-F0-9]{40})', stripped_no_spaces_or_quotes)
                    if to_match:
                        addr = normalize_address(to_match.group(1))
                        if addr not in self.do_not_tag_addresses:
                            self.target_addr = addr
            
            # Check for context changes AFTER processing for the next iteration
            new_context = self.detect_context_change(line)
            if new_context:
                current_context = new_context

    def build_tags(self) -> None:
        """Build appropriate tags for each address."""
        for addr in self.address_mappings:
            # Skip coinbase if we're not converting it
            if addr == self.coinbase_addr and not CONVERT_COINBASE and addr not in self.pre_addresses:
                continue
                
            if addr == KNOWN_SENDER_ADDRESS:
                if addr in self.addresses_with_code:
                    self.address_mappings[addr] = f"<contract:sender:0x{addr}>"
                else:
                    self.address_mappings[addr] = f"<eoa:sender:0x{addr}>"
            elif addr in self.creation_addresses:
                self.address_mappings[addr] = f"<contract:creation:0x{addr}>"
            elif addr == self.coinbase_addr and addr not in self.pre_addresses:
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
                
    def convert_line(self, line: str, section: Section, context: Context) -> str:
        """Second pass: convert addresses to tags.
        
        IMPORTANT: This method should ONLY replace raw addresses with their tags.
        It should NEVER re-tag already tagged addresses to prevent double-tagging
        like <tag:<tag:0xaddr>>. The first pass identifies addresses and assigns
        tags. This second pass finds those raw addresses in the content and 
        replaces them with their assigned tags.
        """
        
        # Special handling for CALL to address 0 when we have 0x0000...0000 in pre-state
        if context == Context.CODE:
            zero_addr = '0' * 40
            if zero_addr in self.address_mappings and self.address_mappings[zero_addr]:
                # Simple pattern: CALL[spaces/comma]FIRST_VALUE[spaces/comma]0
                # This captures CALL followed by any amount of space/comma, then a numeric value, then space/comma, then 0
                # We ensure FIRST_VALUE and the address (0) are numeric to avoid double-tagging
                call_pattern = re.compile(
                    r'(call)([,\s]+)(\d+)([,\s]+)0(?=[,\s\)])',
                    re.IGNORECASE
                )
                
                # Find all matches
                matches = list(call_pattern.finditer(line))
                
                # Replace from end to start to preserve indices
                for match in reversed(matches):
                    # Replace keeping the original separators
                    line = (line[:match.start()] + 
                           match.group(1) +  # CALL
                           match.group(2) +  # separator after CALL
                           match.group(3) +  # first value (gas)
                           match.group(4) +  # separator after first value
                           self.address_mappings[zero_addr] +  # replace 0 with tag
                           line[match.end():])

        # Check if this line contains an address as a key in pre/result sections
        # JSON Pattern: "address" : { or "0xaddress" : {
        # YAML Pattern: address: or 0xaddress:
        is_address_key = False
        for addr in self.address_mappings:
            # JSON format
            if f'"{addr}" : {{' in line or f'"0x{addr}" : {{' in line:
                is_address_key = True
                break
            # YAML format - check if line contains address followed by colon (handles indentation)
            if f'{addr}:' in line or f'0x{addr}:' in line:
                # Make sure it's actually a key (followed by colon and not part of a longer string)
                # Check that there's whitespace or start of line before the address
                if (re.search(rf'(?:^|\s){re.escape(addr)}:', line) or 
                    re.search(rf'(?:^|\s)0x{re.escape(addr)}:', line)):
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
        
        # Replace addresses with tags - simplified pattern matching
        for addr, tag in sorted_addresses:
            if not tag:  # Safety check
                continue
                
            if not is_address_key and not is_transaction_to and section not in [Section.PRE, Section.RESULT] and self.validate_addr_entropy_in_code and calculate_entropy(addr) < 0.5:
                continue
                
            # Skip replacements in code/storage if no_tags_in_code is set
            if self.no_tags_in_code and context in [Context.CODE, Context.STORAGE]:
                continue
            
            # Use regex to find and replace addresses (case-insensitive)
            # Pattern 1: Address followed by colon (as a key) - with or without 0x prefix
            pattern_key = re.compile(rf'(^|\s|"|\')(?:0x)?{re.escape(addr)}(?=:)', re.IGNORECASE)
            if pattern_key.search(line):
                # Skip replacement if we're in storage context, depending on dont_replace_tags_in_storage_keys
                if context != Context.STORAGE and not self.dont_replace_tags_in_storage_keys:
                    # Replace while preserving the prefix (whitespace, quote, etc)
                    line = pattern_key.sub(r'\1' + tag, line)
            
            # Pattern 2: Address in other contexts (not already in a tag)
            # Replace all occurrences that aren't already part of a tag
            # Use a simple approach: temporarily replace already-tagged addresses to avoid double-tagging
            
            # First, find and temporarily replace all existing tags to protect them
            tag_pattern = re.compile(r'<[^>]+>')
            protected_tags = []
            
            def protect_tag(match):
                placeholder = f"__TAG_PLACEHOLDER_{len(protected_tags)}__"
                protected_tags.append(match.group(0))
                return placeholder
            
            # Protect existing tags
            line_with_placeholders = tag_pattern.sub(protect_tag, line)
            
            # Now replace all occurrences of the address
            if context == Context.STORAGE:
                # In storage context, handle keys and values separately
                if not self.dont_replace_tags_in_storage_keys:
                    # Replace addresses everywhere in storage, including keys
                    pattern_general = re.compile(rf'(?:0x)?{re.escape(addr)}', re.IGNORECASE)
                    line_with_placeholders = pattern_general.sub(tag, line_with_placeholders)
                else:
                    # Default behavior: only replace in values, not keys
                    # Split by colon and only replace in values
                    parts = line_with_placeholders.split(':')
                    for i in range(1, len(parts)):  # Skip first part (the key)
                        # Replace address in this part
                        pattern_general = re.compile(rf'(?:0x)?{re.escape(addr)}', re.IGNORECASE)
                        parts[i] = pattern_general.sub(tag, parts[i])
                    line_with_placeholders = ':'.join(parts)
            else:
                # Not in storage context - replace all occurrences
                pattern_general = re.compile(rf'(?:0x)?{re.escape(addr)}', re.IGNORECASE)
                line_with_placeholders = pattern_general.sub(tag, line_with_placeholders)
            
            # Restore protected tags
            for i, protected_tag in enumerate(protected_tags):
                placeholder = f"__TAG_PLACEHOLDER_{i}__"
                line_with_placeholders = line_with_placeholders.replace(placeholder, protected_tag)
            
            line = line_with_placeholders
                
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
                    # Extract the hex part without 0x prefix from short_name
                    hex_part = short_name[2:] if short_name.startswith('0x') else short_name
                    
                    # Create a pattern that matches the hex part with any number of leading/trailing zeros
                    # Pattern: optional 0x prefix, any number of zeros, the hex part, any number of zeros
                    # Must be bounded by non-hex characters to avoid partial matches
                    pattern = re.compile(
                        rf'(?:0x)?0*{re.escape(hex_part)}0*(?![a-fA-F0-9])',
                        re.IGNORECASE
                    )
                    
                    # Find all matches and replace them
                    matches = list(pattern.finditer(line))
                    if matches:
                        # Replace from end to start to preserve indices
                        for match in reversed(matches):
                            # Only replace if it's a valid hex number (starts with 0x or is all hex)
                            match_text = match.group(0)
                            if match_text.startswith('0x') or match_text.startswith('0X'):
                                line = line[:match.start()] + tag + line[match.end():]
                            elif all(c in '0123456789abcdefABCDEF' for c in match_text):
                                # Pure hex without 0x prefix - check context to ensure it's meant as an address
                                # Look for indicators like quotes, colons, or being a standalone value
                                before = line[:match.start()].rstrip()
                                after = line[match.end():].lstrip()
                                if (before.endswith(('"', "'", ':', ' ', '(', '[', ',')) or
                                    after.startswith(('"', "'", ' ', ')', ']', ',', '\n')) or
                                    not before):  # Start of line
                                    line = line[:match.start()] + tag + line[match.end():]
        
        return line


def convert_file(file_path: str) -> bool:
    """Convert a single JSON or YAML file using line-by-line processing."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        filename = Path(file_path).name
        converter = SimpleAddressConverter(filename=filename)
        converter.collect_addresses(lines)
        converter.build_tags()
        
        if not converter.address_mappings:
            return False
            
        new_lines = []
        current_section = Section.NONE
        current_context = Context.NORMAL
        
        for line in lines:
            stripped = line.strip()
            stripped_no_spaces_or_quotes = stripped.replace('"', "").replace("'", "").replace(" ", "")

            # Check for section changes
            new_section = converter.detect_section(line)
            if new_section:
                current_section = new_section
                current_context = Context.NORMAL
            
            # Reset context on closing braces BEFORE converting the line
            if stripped and stripped[-1] in {"}", "]"}:
                current_context = Context.NORMAL
                
            # Reset context on various keywords BEFORE converting the line
            if any(kw in stripped_no_spaces_or_quotes for kw in {
                  "env:", "transaction:", "expect:", "indexes:", "network:", "result:",
                  "secretKey:", "to:", "value:", "address:", "from:"
              }):
                current_context = Context.NORMAL
                
            # Reset context when we see a new address key in pre/result sections
            # This handles YAML structure where addresses are top-level keys
            if current_section in [Section.PRE, Section.RESULT]:
                # Check if this line is an address key (40 hex chars followed by colon)
                if re.match(r'^\s*(?:0x)?[a-fA-F0-9]{40}\s*:', line, re.IGNORECASE):
                    current_context = Context.NORMAL
            
            # Check for context changes BEFORE processing the line
            new_context = converter.detect_context_change(line)
            if new_context:
                current_context = new_context
            
            # Convert the line with the current context
            new_line = converter.convert_line(line, current_section, current_context)
            
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
    parser.add_argument('path', nargs='?', default='tests/static', help='Path to search for filler files')
    args = parser.parse_args()
    
    # Check if path is a single file or directory
    path = Path(args.path)
    yaml_files = []
    json_files = []
    
    if path.is_file():
        if path.name.endswith('Filler.yml') and not is_incompatible_file(path):
            yaml_files = [path]
        elif path.name.endswith('Filler.json') and not is_incompatible_file(path):
            json_files = [path]
    else:
        yaml_files = list(path.rglob('*Filler.yml'))
        json_files = list(path.rglob('*Filler.json'))
        yaml_files = [file for file in yaml_files if not is_incompatible_file(file)]
        json_files = [file for file in json_files if not is_incompatible_file(file)]
        
    print(f"Found {len(yaml_files)} YAML filler files")
    print(f"Found {len(json_files)} JSON filler files")
    
    # Convert files
    converted_yaml = 0
    converted_json = 0
    
    # Convert YAML files
    for file_path in yaml_files:
        if convert_file(str(file_path)):
            converted_yaml += 1
            print(f"Converted YAML: {file_path}")
    
    # Convert JSON files
    for file_path in json_files:
        if convert_file(str(file_path)):
            converted_json += 1
            print(f"Converted JSON: {file_path}")
    
    print(f"\nSummary: Converted {converted_yaml} YAML files and {converted_json} JSON files")


if __name__ == '__main__':
    main()