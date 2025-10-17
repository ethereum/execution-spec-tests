"""
Test block production by having clients build blocks from mempool transactions.

This tests the actual block PRODUCTION code path (mining/building), not just
validation. This catches bugs like the Erigon InitializeBlockExecution issue
where the validation path worked but production path failed.

Flow:
1. Initialize client with genesis
2. Send transaction to mempool via eth_sendRawTransaction
3. Request block building via engine_forkchoiceUpdated (with payload_attributes)
4. Retrieve built block via engine_getPayload
5. Submit block via engine_newPayload (verify client accepts its own work)
6. Finalize via engine_forkchoiceUpdated
7. Verify block matches expected state/gas/etc from fixture
"""

import time

from ethereum_test_base_types import Hash
from ethereum_test_fixtures import BlockchainEngineFixture
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

logger = get_logger(__name__)

MAX_RETRIES = 30
DELAY_BETWEEN_RETRIES_IN_SEC = 1


class LoggedError(Exception):
    """Exception that uses the logger to log the failure."""

    def __init__(self, *args: object) -> None:
        """Initialize the exception and log the failure."""
        super().__init__(*args)
        logger.fail(str(self))


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

    # Process each payload by having client BUILD the block
    with timing_data.time("Block production") as total_production_timing:
        logger.info(f"Starting production of {len(fixture.payloads)} blocks...")

        for i, payload in enumerate(fixture.payloads):
            logger.info(f"Processing payload {i + 1}/{len(fixture.payloads)}...")

            with total_production_timing.time(f"Payload {i + 1}") as payload_timing:
                # Extract the transaction from the payload
                expected_execution_payload = payload.params[0]
                transactions = expected_execution_payload.transactions

                # Check transaction count
                if len(transactions) == 0:
                    logger.info("Payload has no transactions, skipping...")
                    continue
                elif len(transactions) != 1:
                    raise LoggedError(
                        f"Production simulator requires exactly 1 transaction per payload, "
                        f"got {len(transactions)}"
                    )

                tx_rlp = transactions[0]

                # Step 1: Send transaction to mempool
                with payload_timing.time("eth_sendRawTransaction"):
                    logger.info("Sending transaction to mempool...")
                    tx_hash = eth_rpc.send_raw_transaction(tx_rlp)
                    logger.info(f"Transaction sent to mempool: {tx_hash}")

                # Step 2: Request block building
                with payload_timing.time("engine_forkchoiceUpdated (request build)"):
                    logger.info("Requesting block building...")

                    # Get current head
                    head_block = eth_rpc.get_block_by_number("latest")
                    assert head_block is not None

                    # Create payload attributes to trigger building
                    payload_attributes = PayloadAttributes(
                        timestamp=expected_execution_payload.timestamp,
                        prev_randao=expected_execution_payload.prev_randao,
                        suggested_fee_recipient=expected_execution_payload.fee_recipient,
                        withdrawals=expected_execution_payload.withdrawals,
                        parent_beacon_block_root=expected_execution_payload.parent_beacon_block_root,
                        # Add blob schedule fields if present (Osaka+)
                        target_blobs_per_block=getattr(
                            expected_execution_payload, "target_blobs_per_block", None
                        ),
                        max_blobs_per_block=getattr(
                            expected_execution_payload, "max_blobs_per_block", None
                        ),
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

                # Step 3: Wait a bit for block to be built
                with payload_timing.time("Wait for block building"):
                    # Give client time to build the block
                    # Adjust this based on client behavior
                    time.sleep(0.5)

                # Step 4: Get the built payload
                with payload_timing.time(f"engine_getPayloadV{payload.new_payload_version}"):
                    logger.info("Getting built payload...")

                    built_payload_response = engine_rpc.get_payload(
                        payload_id=payload_id,
                        version=payload.new_payload_version,
                    )

                    built_execution_payload = built_payload_response.execution_payload
                    logger.info(f"Got built block: {built_execution_payload.block_hash}")

                # Step 5: Verify the built block
                with payload_timing.time("Verify built block"):
                    logger.info("Verifying built block against fixture expectations...")

                    # Check transaction is included (need to hash the RLP to compare)
                    built_tx_hashes = [
                        Hash(keccak256(tx)) for tx in built_execution_payload.transactions
                    ]
                    if tx_hash not in built_tx_hashes:
                        raise LoggedError(f"Built block doesn't contain our transaction {tx_hash}")

                    # Check gas used matches expectations
                    expected_gas = expected_execution_payload.gas_used
                    actual_gas = built_execution_payload.gas_used
                    if actual_gas != expected_gas:
                        raise LoggedError(
                            f"Gas mismatch: expected {expected_gas}, got {actual_gas}. "
                            f"This indicates the client's block building code has issues "
                            f"(like the Erigon InitializeBlockExecution bug)."
                        )

                    # Check state root matches
                    expected_state_root = expected_execution_payload.state_root
                    actual_state_root = built_execution_payload.state_root
                    if actual_state_root != expected_state_root:
                        raise LoggedError(
                            f"State root mismatch: expected {expected_state_root}, "
                            f"got {actual_state_root}"
                        )

                    logger.info("Built block verification passed!")

                # Step 6: Submit the built block back to client (sanity check)
                with payload_timing.time(f"engine_newPayloadV{payload.new_payload_version}"):
                    logger.info("Submitting built block back to client...")

                    new_payload_args = [built_execution_payload]
                    if built_payload_response.blobs_bundle is not None:
                        new_payload_args.append(
                            built_payload_response.blobs_bundle.blob_versioned_hashes()
                        )
                    if expected_execution_payload.parent_beacon_block_root is not None:
                        new_payload_args.append(
                            expected_execution_payload.parent_beacon_block_root
                        )
                    if built_payload_response.execution_requests is not None:
                        new_payload_args.append(built_payload_response.execution_requests)

                    new_payload_response = engine_rpc.new_payload(
                        *new_payload_args,
                        version=payload.new_payload_version,
                    )

                    if new_payload_response.status != PayloadStatusEnum.VALID:
                        raise LoggedError(
                            f"Client rejected its own built block: {new_payload_response.status}"
                        )

                # Step 7: Finalize the block
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

        logger.info("All blocks produced and verified successfully!")
