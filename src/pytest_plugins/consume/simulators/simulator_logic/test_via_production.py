"""
Test block production by having clients build blocks from mempool transactions.

This tests the actual block PRODUCTION code path (mining/building), not just
validation. This catches bugs like the Erigon InitializeBlockExecution issue
where the validation path worked but production path failed.

Flow:
1. Initialize client with genesis
2. Send transaction to mempool via eth_sendRawTransaction
3. Verify transaction is in mempool
4. Request block building via engine_forkchoiceUpdated (with payload_attributes)
5. Poll until block is built
6. Retrieve built block via engine_getPayload
7. Verify block matches expected state/gas/etc from fixture
8. Submit block via engine_newPayload (verify client accepts its own work)
9. Finalize via engine_forkchoiceUpdated
10. Verify transaction executed successfully
"""

import time

from ethereum_test_base_types import Hash
from ethereum_test_fixtures import BlockchainEngineFixture
from ethereum_test_forks import Fork
from ethereum_test_rpc import EngineRPC, EthRPC
from ethereum_test_rpc.rpc_types import (
    ForkchoiceState,
    PayloadAttributes,
    PayloadStatusEnum,
)
from ethereum_test_types.trie import keccak256

from ....custom_logging import get_logger
from ..helpers.exceptions import GenesisBlockMismatchExceptionError
from ..helpers.timing import TimingData
from ..production.helpers.block_building import (
    wait_for_payload_ready,
    wait_for_transaction_in_mempool,
)

logger = get_logger(__name__)

MAX_RETRIES = 30
DELAY_BETWEEN_RETRIES_IN_SEC = 1


class LoggedError(Exception):
    """Exception that uses the logger to log the failure."""

    def __init__(self, *args: object) -> None:
        """Initialize the exception and log the failure."""
        super().__init__(*args)
        logger.fail(str(self))


def get_payload_version_for_fork(fork: Fork, new_payload_version: int) -> int:
    """
    Determine the correct getPayload version based on the fork.

    Engine API versioning is complex:
    - Paris → Cancun: versions match (V1, V2, V3)
    - Prague: forkchoiceV3, getPayloadV4, newPayloadV4
    - Osaka: forkchoiceV3, getPayloadV5, newPayloadV4
    """
    # Check fork by name since we need exact fork matching
    fork_name = fork.__class__.__name__

    if fork_name == "Osaka" or "Osaka" in fork_name:
        return 5
    elif fork_name == "Prague" or "Prague" in fork_name:
        return 4
    # For Cancun and earlier, getPayload version = newPayload version
    else:
        return new_payload_version


def test_blockchain_via_production(
    timing_data: TimingData,
    eth_rpc: EthRPC,
    engine_rpc: EngineRPC,
    fixture: BlockchainEngineFixture,
) -> None:
    """
    Test block production by having the client build blocks from mempool.

    Key difference from consume engine (validation):
    - consume engine: gives client pre-built blocks to validate
    - consume production: client BUILDS the blocks from transactions

    This tests the mining/production code path that validators use.
    """
    # Send initial forkchoice update to genesis
    with timing_data.time("Initial forkchoice update"):
        logger.info("Sending initial forkchoice update to genesis block...")
        for attempt in range(1, MAX_RETRIES + 1):
            forkchoice_response = engine_rpc.forkchoice_updated(
                forkchoice_state=ForkchoiceState(
                    head_block_hash=fixture.genesis.block_hash,
                ),
                payload_attributes=None,
                version=fixture.payloads[0].forkchoice_updated_version,
            )
            status = forkchoice_response.payload_status.status
            logger.info(f"Initial forkchoice update response attempt {attempt}: {status}")
            if status != PayloadStatusEnum.SYNCING:
                break

            if attempt < MAX_RETRIES:
                time.sleep(DELAY_BETWEEN_RETRIES_IN_SEC)

        if forkchoice_response.payload_status.status != PayloadStatusEnum.VALID:
            logger.error(
                f"Client failed to initialize properly after {MAX_RETRIES} attempts, "
                f"final status: {forkchoice_response.payload_status.status}"
            )
            raise LoggedError(
                f"unexpected status on forkchoice updated to genesis: {forkchoice_response}"
            )

    # Verify genesis
    with timing_data.time("Get genesis block"):
        logger.info("Calling getBlockByNumber to get genesis block...")
        genesis_block = eth_rpc.get_block_by_number(0)
        assert genesis_block is not None, "genesis_block is None"
        if genesis_block["hash"] != str(fixture.genesis.block_hash):
            expected = fixture.genesis.block_hash
            got = genesis_block["hash"]
            logger.fail(f"Genesis block hash mismatch. Expected: {expected}, Got: {got}")
            raise GenesisBlockMismatchExceptionError(
                expected_header=fixture.genesis,
                got_genesis_block=genesis_block,
            )

    # Get payload version
    get_payload_version = get_payload_version_for_fork(
        fixture.fork, fixture.payloads[0].new_payload_version
    )
    logger.info(
        f"Fork: {fixture.fork}, "
        f"Using getPayloadV{get_payload_version}, "
        f"newPayloadV{fixture.payloads[0].new_payload_version}, "
        f"forkchoiceUpdatedV{fixture.payloads[0].forkchoice_updated_version}"
    )

    # Process each payload by having client BUILD the block
    with timing_data.time("Block production") as total_production_timing:
        logger.info(f"Starting production of {len(fixture.payloads)} blocks...")

        for i, payload in enumerate(fixture.payloads):
            logger.info(f"Processing payload {i + 1}/{len(fixture.payloads)}...")

            with total_production_timing.time(f"Payload {i + 1}") as payload_timing:
                # Extract the transaction from the payload
                expected_execution_payload = payload.params[0]
                transactions = expected_execution_payload.transactions

                # Single transaction check (enforced by conftest filtering)
                assert len(transactions) == 1, (
                    "Production simulator requires exactly 1 transaction per payload "
                    "(should be filtered by conftest)"
                )

                tx_rlp = transactions[0]

                # Step 1: Send transaction to mempool and verify it's there
                with payload_timing.time("eth_sendRawTransaction + mempool verification"):
                    logger.info("Sending transaction to mempool...")
                    tx_hash = eth_rpc.send_raw_transaction(tx_rlp)
                    logger.info(f"Transaction sent: {tx_hash}")

                    # Wait for transaction to appear in mempool
                    logger.info("Verifying transaction is in mempool...")
                    if not wait_for_transaction_in_mempool(eth_rpc, tx_hash, timeout=5):
                        raise LoggedError(
                            f"Transaction {tx_hash} not in mempool after 5s. "
                            f"Client may not be accepting transactions."
                        )

                    logger.info(f"Transaction confirmed in mempool: {tx_hash}")

                    # Give the client additional time for the transaction to be
                    # processed into the pending pool that the block builder uses.
                    logger.info("Waiting for transaction to be processed into pending pool...")
                    time.sleep(2.0)

                # Step 2: Request block building
                with payload_timing.time("engine_forkchoiceUpdated (request build)"):
                    logger.info("Requesting block building...")

                    # Get current head
                    head_block = eth_rpc.get_block_by_number("latest")
                    assert head_block is not None

                    # Get parent_beacon_block_root from payload params if present (Cancun+)
                    # params[0] = execution_payload
                    # params[1] = expected_blob_versioned_hashes (if blobs present)
                    # params[2] = parent_beacon_block_root (Cancun+)
                    parent_beacon_block_root = None
                    if len(payload.params) >= 3:
                        parent_beacon_block_root = payload.params[2]

                    # Create payload attributes to trigger building
                    # Handle different fork versions:
                    # - PayloadAttributesV1 (Paris): no withdrawals, no parent_beacon_block_root
                    # - PayloadAttributesV2 (Shanghai): has withdrawals, no parent_beacon_block_root
                    # - PayloadAttributesV3 (Cancun+): has withdrawals, has parent_beacon_block_root

                    # Build PayloadAttributes conditionally based on available fields
                    if parent_beacon_block_root is not None:
                        # Cancun+ (V3): has parent_beacon_block_root
                        payload_attributes = PayloadAttributes(
                            timestamp=expected_execution_payload.timestamp,
                            prev_randao=expected_execution_payload.prev_randao,
                            suggested_fee_recipient=expected_execution_payload.fee_recipient,
                            withdrawals=getattr(expected_execution_payload, "withdrawals", None),
                            parent_beacon_block_root=parent_beacon_block_root,
                        )
                    elif hasattr(expected_execution_payload, "withdrawals"):
                        # Shanghai (V2): has withdrawals but no parent_beacon_block_root
                        payload_attributes = PayloadAttributes(
                            timestamp=expected_execution_payload.timestamp,
                            prev_randao=expected_execution_payload.prev_randao,
                            suggested_fee_recipient=expected_execution_payload.fee_recipient,
                            withdrawals=expected_execution_payload.withdrawals,
                        )
                    else:
                        # Paris (V1): no withdrawals, no parent_beacon_block_root
                        payload_attributes = PayloadAttributes(
                            timestamp=expected_execution_payload.timestamp,
                            prev_randao=expected_execution_payload.prev_randao,
                            suggested_fee_recipient=expected_execution_payload.fee_recipient,
                        )

                    forkchoice_response = engine_rpc.forkchoice_updated(
                        forkchoice_state=ForkchoiceState(
                            head_block_hash=head_block["hash"],
                        ),
                        payload_attributes=payload_attributes,
                        version=payload.forkchoice_updated_version,
                    )

                    if forkchoice_response.payload_status.status != PayloadStatusEnum.VALID:
                        raise LoggedError(
                            f"Forkchoice update for building failed: {forkchoice_response}"
                        )

                    payload_id = forkchoice_response.payload_id
                    if payload_id is None:
                        raise LoggedError("No payload_id returned from forkchoice_updated")

                    logger.info(f"Block building requested, payload_id: {payload_id}")

                # Step 3: Poll until block is built
                with payload_timing.time("Wait for block building"):
                    logger.info("Waiting for client to build block...")
                    # Give client time to select transactions from mempool
                    # Most clients need at least 1-2 seconds to build a proper block
                    time.sleep(3.0)
                    try:
                        built_payload_response = wait_for_payload_ready(
                            engine_rpc=engine_rpc,
                            payload_id=payload_id,
                            get_payload_version=get_payload_version,
                            timeout=10.0,
                            poll_interval=0.5,
                        )
                        logger.info("Block building complete!")
                    except TimeoutError as e:
                        raise LoggedError(
                            f"Block not ready after timeout. "
                            f"Check if client is actually building blocks. "
                            f"Error: {e}"
                        ) from e

                # Step 4: Verify the built block
                built_execution_payload = built_payload_response.execution_payload
                logger.info(f"Got built block: {built_execution_payload.block_hash}")

                with payload_timing.time("Verify built block"):
                    logger.info("Verifying built block against fixture expectations...")

                    # Check transaction is included (need to hash the RLP to compare)
                    built_tx_hashes = [
                        Hash(keccak256(tx)) for tx in built_execution_payload.transactions
                    ]
                    if tx_hash not in built_tx_hashes:
                        raise LoggedError(
                            f"Built block doesn't contain our transaction {tx_hash}. "
                            f"Found transactions: {built_tx_hashes}"
                        )

                    # Check gas used matches expectations
                    expected_gas = expected_execution_payload.gas_used
                    actual_gas = built_execution_payload.gas_used
                    if actual_gas != expected_gas:
                        gas_diff = actual_gas - expected_gas
                        raise LoggedError(
                            f"Gas mismatch: expected {expected_gas}, got {actual_gas} "
                            f"(diff: {gas_diff:+d}). "
                            f"This indicates the client's block building code has issues "
                            f"(like the Erigon InitializeBlockExecution bug). "
                            f"Expected gas includes system contract initialization."
                        )

                    # Check state root matches
                    expected_state_root = expected_execution_payload.state_root
                    actual_state_root = built_execution_payload.state_root
                    if actual_state_root != expected_state_root:
                        raise LoggedError(
                            f"State root mismatch: expected {expected_state_root}, "
                            f"got {actual_state_root}. "
                            f"Client's state transition during block building is incorrect."
                        )

                    logger.info("Built block verification passed!")

                # Step 5: Submit the built block back to client (sanity check)
                with payload_timing.time(f"engine_newPayloadV{payload.new_payload_version}"):
                    logger.info("Submitting built block back to client...")

                    # Reconstruct newPayload args with the BUILT execution payload
                    # but keep other params (blob hashes, parent beacon block root, execution requests)
                    # from the original fixture
                    if payload.new_payload_version == 1:
                        # V1 (Paris): Just execution payload
                        new_payload_args = [built_execution_payload]
                    elif payload.new_payload_version == 2:
                        # V2 (Shanghai): Just execution payload (withdrawals are inside it)
                        new_payload_args = [built_execution_payload]
                    elif payload.new_payload_version == 3:
                        # V3 (Cancun): execution_payload, blob_hashes, parent_beacon_block_root
                        blob_hashes = (
                            built_payload_response.blobs_bundle.blob_versioned_hashes()
                            if built_payload_response.blobs_bundle is not None
                            else []
                        )
                        pbr = (
                            payload.params[2]
                            if len(payload.params) >= 3
                            else parent_beacon_block_root
                        )
                        new_payload_args = [
                            built_execution_payload,
                            blob_hashes,
                            pbr,  # parent_beacon_block_root from fixture
                        ]
                    elif payload.new_payload_version in [4, 5]:
                        # V4/V5 (Prague/Osaka): + execution_requests
                        blob_hashes = (
                            built_payload_response.blobs_bundle.blob_versioned_hashes()
                            if built_payload_response.blobs_bundle is not None
                            else []
                        )
                        execution_requests = (
                            built_payload_response.execution_requests
                            if built_payload_response.execution_requests is not None
                            else []
                        )
                        pbr = (
                            payload.params[2]
                            if len(payload.params) >= 3
                            else parent_beacon_block_root
                        )
                        new_payload_args = [
                            built_execution_payload,
                            blob_hashes,
                            pbr,  # parent_beacon_block_root from fixture
                            execution_requests,
                        ]
                    else:
                        raise LoggedError(
                            f"Unsupported newPayload version: {payload.new_payload_version}"
                        )

                    new_payload_response = engine_rpc.new_payload(
                        *new_payload_args,
                        version=payload.new_payload_version,
                    )

                    if new_payload_response.status != PayloadStatusEnum.VALID:
                        raise LoggedError(
                            f"Client rejected its own built block! "
                            f"Status: {new_payload_response.status}, "
                            f"Validation error: {new_payload_response.validation_error}"
                        )

                    logger.info("Client accepted its own built block!")

                # Step 6: Finalize the block
                with payload_timing.time(
                    f"engine_forkchoiceUpdatedV{payload.forkchoice_updated_version} (finalize)"
                ):
                    logger.info("Finalizing built block...")

                    forkchoice_response = engine_rpc.forkchoice_updated(
                        forkchoice_state=ForkchoiceState(
                            head_block_hash=built_execution_payload.block_hash,
                        ),
                        payload_attributes=None,
                        version=payload.forkchoice_updated_version,
                    )

                    if forkchoice_response.payload_status.status != PayloadStatusEnum.VALID:
                        raise LoggedError(
                            f"Forkchoice update for finalization failed: {forkchoice_response}"
                        )

                    logger.info("Block finalized successfully!")

                # Step 7: Verify transaction executed successfully
                with payload_timing.time("Verify transaction execution"):
                    logger.info("Checking transaction receipt...")
                    receipt = eth_rpc.get_transaction_receipt(tx_hash)

                    if receipt is None:
                        raise LoggedError(
                            f"No receipt for transaction {tx_hash}. "
                            f"Transaction may not have been included in the finalized block."
                        )

                    if receipt["status"] != "0x1":
                        raise LoggedError(
                            f"Transaction {tx_hash} reverted (status: {receipt['status']})! "
                            f"This indicates the production code failed to initialize properly "
                            f"(like the Erigon bug with beacon roots not being initialized). "
                            f"The transaction expected system contracts to be ready."
                        )

                    logger.info("Transaction executed successfully!")

        logger.info("All blocks produced and verified successfully!")
