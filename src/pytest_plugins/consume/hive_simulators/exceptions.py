"""Custom exceptions utilized within consume simulators."""

import pprint
from typing import Dict, List, Tuple

from ethereum_clis.clis.ethereumjs import EthereumJSExceptionMapper
from ethereum_clis.clis.geth import GethExceptionMapper
from ethereum_test_exceptions import BlockException, ExceptionMapper, TransactionException
from ethereum_test_fixtures.blockchain import FixtureHeader


class GenesisBlockMismatchExceptionError(Exception):
    """Definers a mismatch exception between the client and fixture genesis blockhash."""

    def __init__(self, *, expected_header: FixtureHeader, got_genesis_block: Dict[str, str]):
        """Initialize the exception with the expected and received genesis block headers."""
        message = (
            "Genesis block hash mismatch.\n\n"
            f"Expected: {expected_header.block_hash}\n"
            f"     Got: {got_genesis_block['hash']}."
        )
        differences, unexpected_fields = self.compare_models(
            expected_header, FixtureHeader(**got_genesis_block)
        )
        if differences:
            message += (
                "\n\nGenesis block header field differences:\n"
                f"{pprint.pformat(differences, indent=4)}"
            )
        elif unexpected_fields:
            message += (
                "\n\nUn-expected genesis block header fields from client:\n"
                f"{pprint.pformat(unexpected_fields, indent=4)}"
                "\nIs the fork configuration correct?"
            )
        else:
            message += (
                "There were no differences in the expected and received genesis block headers."
            )
        super().__init__(message)

    @staticmethod
    def compare_models(expected: FixtureHeader, got: FixtureHeader) -> Tuple[Dict, List]:
        """Compare two FixtureHeader model instances and return their differences."""
        differences = {}
        unexpected_fields = []
        for (exp_name, exp_value), (got_name, got_value) in zip(expected, got, strict=False):
            if "rlp" in exp_name or "fork" in exp_name:  # ignore rlp as not verbose enough
                continue
            if exp_value != got_value:
                differences[exp_name] = {
                    "expected     ": str(exp_value),
                    "got (via rpc)": str(got_value),
                }
            if got_value is None:
                unexpected_fields.append(got_name)
        return differences, unexpected_fields


class NethermindMapper(ExceptionMapper):
    """Nethermind exception mapper."""

    mapping_substring = {
        TransactionException.SENDER_NOT_EOA: "sender has deployed code",
        TransactionException.INSUFFICIENT_ACCOUNT_FUNDS: "insufficient sender balance",
        TransactionException.INTRINSIC_GAS_TOO_LOW: "intrinsic gas too low",
        TransactionException.INSUFFICIENT_MAX_FEE_PER_GAS: "miner premium is negative",
        TransactionException.PRIORITY_GREATER_THAN_MAX_FEE_PER_GAS: (
            "InvalidMaxPriorityFeePerGas: Cannot be higher than maxFeePerGas"
        ),
        TransactionException.INITCODE_SIZE_EXCEEDED: "max initcode size exceeded",
        TransactionException.NONCE_MISMATCH_TOO_LOW: "wrong transaction nonce",
        TransactionException.INSUFFICIENT_MAX_FEE_PER_BLOB_GAS: (
            "InsufficientMaxFeePerBlobGas: Not enough to cover blob gas fee"
        ),
        TransactionException.TYPE_3_TX_ZERO_BLOBS: "blob transaction missing blob hashes",
        TransactionException.TYPE_3_TX_INVALID_BLOB_VERSIONED_HASH: (
            "InvalidBlobVersionedHashVersion: Blob version not supported"
        ),
        TransactionException.TYPE_3_TX_CONTRACT_CREATION: "blob transaction of type create",
        TransactionException.TYPE_4_EMPTY_AUTHORIZATION_LIST: (
            "MissingAuthorizationList: Must be set"
        ),
        TransactionException.TYPE_4_TX_CONTRACT_CREATION: (
            "NotAllowedCreateTransaction: To must be set"
        ),
        BlockException.INCORRECT_BLOB_GAS_USED: (
            "HeaderBlobGasMismatch: Blob gas in header does not match calculated"
        ),
        BlockException.INVALID_REQUESTS: "InvalidRequestsHash: Requests hash mismatch in block",
    }
    mapping_regex = {
        TransactionException.TYPE_3_TX_WITH_FULL_BLOBS: r"Transaction \d+ is not valid",
        TransactionException.TYPE_3_TX_MAX_BLOB_GAS_ALLOWANCE_EXCEEDED: (
            r"BlobTxGasLimitExceeded: Transaction's totalDataGas=\d+ "
            r"exceeded MaxBlobGas per transaction=\d+"
        ),
        TransactionException.TYPE_3_TX_BLOB_COUNT_EXCEEDED: (
            r"BlockBlobGasExceeded: A block cannot have more than \d+ blob gas, blobs count \d+, "
            r"blobs gas used: \d+"
        ),
        BlockException.INCORRECT_EXCESS_BLOB_GAS: (
            r"HeaderExcessBlobGasMismatch: Excess blob gas in header does not match calculated"
            r"|Overflow in excess blob gas"
        ),
        BlockException.INVALID_BLOCK_HASH: (
            r"Invalid block hash 0x[0-9a-f]+ does not match calculated hash 0x[0-9a-f]+"
        ),
    }


class ErigonMapper(ExceptionMapper):
    """Erigon exception mapper."""

    mapping_substring = {}
    mapping_regex = {}


class BesuMapper(ExceptionMapper):
    """Besu exception mapper."""

    mapping_substring = {
        BlockException.INCORRECT_BLOB_GAS_USED: (
            "Payload BlobGasUsed does not match calculated BlobGasUsed"
        ),
        BlockException.INCORRECT_EXCESS_BLOB_GAS: (
            "Payload excessBlobGas does not match calculated excessBlobGas"
        ),
        TransactionException.TYPE_3_TX_INVALID_BLOB_VERSIONED_HASH: "Invalid versionedHash",
        TransactionException.TYPE_3_TX_CONTRACT_CREATION: (
            "transaction invalid transaction blob transactions must have a to address"
        ),
        BlockException.RLP_STRUCTURES_ENCODING: (
            "Failed to decode transactions from block parameter"
        ),
        TransactionException.TYPE_3_TX_WITH_FULL_BLOBS: (
            "Failed to decode transactions from block parameter"
        ),
        TransactionException.TYPE_3_TX_ZERO_BLOBS: (
            "Failed to decode transactions from block parameter"
        ),
        TransactionException.INSUFFICIENT_MAX_FEE_PER_BLOB_GAS: (
            "transaction invalid tx max fee per blob gas less than block blob gas fee"
        ),
        TransactionException.INSUFFICIENT_MAX_FEE_PER_GAS: (
            "transaction invalid gasPrice is less than the current BaseFee"
        ),
        TransactionException.PRIORITY_GREATER_THAN_MAX_FEE_PER_GAS: (
            "transaction invalid max priority fee per gas cannot be greater than max fee per gas"
        ),
        TransactionException.TYPE_4_EMPTY_AUTHORIZATION_LIST: (
            "transaction invalid transaction code delegation transactions must have a "
            "non-empty code delegation list"
        ),
        TransactionException.TYPE_4_TX_CONTRACT_CREATION: (
            "transaction invalid transaction code delegation transactions must have a to address"
        ),
        TransactionException.TYPE_3_TX_MAX_BLOB_GAS_ALLOWANCE_EXCEEDED: "Invalid Blob Count",
        TransactionException.TYPE_3_TX_BLOB_COUNT_EXCEEDED: "Invalid Blob Count",
        BlockException.BLOB_GAS_USED_ABOVE_LIMIT: (
            "Payload BlobGasUsed does not match calculated BlobGasUsed"
        ),
        BlockException.INCORRECT_BLOB_GAS_USED: (
            "Payload BlobGasUsed does not match calculated BlobGasUsed"
        ),
    }
    mapping_regex = {
        BlockException.INVALID_REQUESTS: (
            r"Invalid execution requests|Requests hash mismatch, calculated: 0x[0-9a-f]+ header: "
            r"0x[0-9a-f]+"
        ),
        BlockException.INVALID_BLOCK_HASH: (
            r"Computed block hash 0x[0-9a-f]+ does not match block hash parameter 0x[0-9a-f]+"
        ),
        TransactionException.INITCODE_SIZE_EXCEEDED: (
            r"transaction invalid Initcode size of \d+ exceeds maximum size of \d+"
        ),
        TransactionException.INSUFFICIENT_ACCOUNT_FUNDS: (
            r"transaction invalid transaction up-front cost 0x[0-9a-f]+ exceeds transaction "
            r"sender account balance 0x[0-9a-f]+"
        ),
        TransactionException.INTRINSIC_GAS_TOO_LOW: (
            r"transaction invalid intrinsic gas cost \d+ exceeds gas limit \d+"
        ),
        TransactionException.SENDER_NOT_EOA: (
            r"transaction invalid Sender 0x[0-9a-f]+ has deployed code and so is not authorized "
            r"to send transactions"
        ),
        TransactionException.NONCE_MISMATCH_TOO_LOW: (
            r"transaction invalid transaction nonce \d+ below sender account nonce \d+"
        ),
    }


class RethMapper(ExceptionMapper):
    """Reth exception mapper."""

    mapping_substring = {}
    mapping_regex = {}


class NimbusMapper(ExceptionMapper):
    """Nimbus exception mapper."""

    mapping_substring = {}
    mapping_regex = {}


EXCEPTION_MAPPERS: Dict[str, ExceptionMapper] = {
    "go-ethereum": GethExceptionMapper(),
    "nethermind": NethermindMapper(),
    "erigon": ErigonMapper(),
    "besu": BesuMapper(),
    "reth": RethMapper(),
    "nimbus": NimbusMapper(),
    "ethereumjs": EthereumJSExceptionMapper(),
}
