"""Nimbus Transition tool interface."""

import re
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, Optional

from ethereum_test_exceptions import (
    BlockException,
    EOFException,
    ExceptionBase,
    ExceptionMapper,
    TransactionException,
)
from ethereum_test_forks import Fork

from ..transition_tool import TransitionTool


class NimbusTransitionTool(TransitionTool):
    """Nimbus `evm` Transition tool interface wrapper class."""

    default_binary = Path("t8n")
    detect_binary_pattern = re.compile(r"^Nimbus-t8n\b")
    version_flag: str = "--version"

    binary: Path
    cached_version: Optional[str] = None
    trace: bool

    def __init__(
        self,
        *,
        binary: Optional[Path] = None,
        trace: bool = False,
    ):
        """Initialize the Nimbus Transition tool interface."""
        super().__init__(exception_mapper=NimbusExceptionMapper(), binary=binary, trace=trace)
        args = [str(self.binary), "--help"]
        try:
            result = subprocess.run(args, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"evm process unexpectedly returned a non-zero status code: {e}."
            ) from e
        except Exception as e:
            raise Exception(f"Unexpected exception calling evm tool: {e}.") from e
        self.help_string = result.stdout

    def version(self) -> str:
        """Get `evm` binary version."""
        if self.cached_version is None:
            self.cached_version = re.sub(r"\x1b\[0m", "", super().version()).strip()

        return self.cached_version

    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Return True if the fork is supported by the tool.

        If the fork is a transition fork, we want to check the fork it transitions to.
        """
        return fork.transition_tool_name() in self.help_string


class NimbusExceptionMapper(ExceptionMapper):
    """Translate between EEST exceptions and error strings returned by Nimbus."""

    mapping_substring: ClassVar[Dict[ExceptionBase, str]] = {
        # TODO: these need to be fixed / incorrectly mapped
        TransactionException.INSUFFICIENT_MAX_FEE_PER_GAS: (
            "zero gasUsed but transactions present"
        ),
        TransactionException.TYPE_3_TX_MAX_BLOB_GAS_ALLOWANCE_EXCEEDED: (
            "zero gasUsed but transactions present"
        ),
        TransactionException.TYPE_4_TX_CONTRACT_CREATION: (
            "zero gasUsed but transactions present"
        ),
        TransactionException.TYPE_4_EMPTY_AUTHORIZATION_LIST: (
            "zero gasUsed but transactions present"
        ),
        TransactionException.INSUFFICIENT_MAX_FEE_PER_BLOB_GAS: (
            "zero gasUsed but transactions present"
        ),
        TransactionException.PRIORITY_GREATER_THAN_MAX_FEE_PER_GAS: (
            "zero gasUsed but transactions present"
        ),
        TransactionException.SENDER_NOT_EOA: "zero gasUsed but transactions present",
        TransactionException.INTRINSIC_GAS_TOO_LOW: "zero gasUsed but transactions present",
        TransactionException.INITCODE_SIZE_EXCEEDED: "zero gasUsed but transactions present",
        TransactionException.TYPE_3_TX_PRE_FORK: "zero gasUsed but transactions present",
        TransactionException.TYPE_3_TX_ZERO_BLOBS: "zero gasUsed but transactions present",
        TransactionException.INVALID_DEPOSIT_EVENT_LAYOUT: "stateRoot mismatch",  # Leave for last.
        # Correctly mapped
        TransactionException.TYPE_3_TX_CONTRACT_CREATION: (
            "invalid tx: destination must be not empty"
        ),
        TransactionException.NONCE_MISMATCH_TOO_LOW: "account nonce mismatch",
        BlockException.INCORRECT_BLOB_GAS_USED: "calculated blobGas not equal header.blobGasUsed",
        BlockException.INCORRECT_EXCESS_BLOB_GAS: "calculated excessBlobGas not equal header.excessBlobGas",
        BlockException.INVALID_BLOCK_HASH: "blockhash mismatch",
    }
    mapping_regex: ClassVar[Dict[ExceptionBase, str]] = {
        TransactionException.INSUFFICIENT_ACCOUNT_FUNDS: (
            r"(invalid tx: not enough cash to send)|"
            r"(zero gasUsed but transactions present)"  # TODO: Needs fix.
        ),
        TransactionException.TYPE_3_TX_INVALID_BLOB_VERSIONED_HASH: (
            r"(one of blobVersionedHash has invalid version)|"
            r"(zero gasUsed but transactions present)"  # TODO: Needs fix.
        ),
        TransactionException.TYPE_3_TX_BLOB_COUNT_EXCEEDED: (
            r"blobGasUsed (\d+) exceeds maximum allowance (\d+)"
        ),
        BlockException.SYSTEM_CONTRACT_CALL_FAILED: (
            r"(Opcode Dispatch Error: OutOfGas)|(Opcode Dispatch Error: InvalidInstruction)|"
            r"(REVERT opcode executed)"
        ),
        BlockException.SYSTEM_CONTRACT_EMPTY: (
            r"No code found for withdrawal or consolidation requests contract"
        ),
        BlockException.RLP_STRUCTURES_ENCODING: r"Failed to decode payload",
        BlockException.INVALID_REQUESTS: r"(Invalid execution request|requestsHash mismatch)",
    }
