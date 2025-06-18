"""
A hive based simulator that executes blocks against clients using the `engine_newPayloadVX` method
from the Engine API. The simulator uses the `BlockchainEngineFixtures` to test against clients.

Each `engine_newPayloadVX` is verified against the appropriate VALID/INVALID responses.
"""

import time

import pytest

from ethereum_test_exceptions import UndefinedException
from ethereum_test_fixtures import BlockchainEngineFixture, BlockchainEngineXFixture
from ethereum_test_fixtures.blockchain import FixtureHeader
from ethereum_test_rpc import EngineRPC, EthRPC
from ethereum_test_rpc.types import ForkchoiceState, JSONRPCError, PayloadStatusEnum

from ....logging import get_logger
from ..helpers.exceptions import GenesisBlockMismatchExceptionError
from ..helpers.timing import TimingData

logger = get_logger(__name__)


class LoggedError(Exception):
    """Exception that uses the logger to log the failure."""

    def __init__(self, *args: object) -> None:
        """Initialize the exception and log the failure."""
        super().__init__(*args)
        logger.fail(str(self))


@pytest.mark.usefixtures("hive_test")
def test_blockchain_via_engine(
    timing_data: TimingData,
    eth_rpc: EthRPC,
    engine_rpc: EngineRPC,
    fixture: BlockchainEngineFixture | BlockchainEngineXFixture,
    genesis_header: FixtureHeader,
    strict_exception_matching: bool,
    fcu_frequency_tracker=None,  # Optional for enginex simulator
    request=None,  # For accessing test info
):
    """
    1. Check the client genesis block hash matches `genesis.block_hash`.
    2. Execute the test case fixture blocks against the client under test using the
    `engine_newPayloadVX` method from the Engine API.
    3. For valid payloads a forkchoice update is performed to finalize the chain
       (controlled by FCU frequency for enginex simulator).
    """
    # Determine if we should perform forkchoice updates based on frequency tracker
    should_perform_fcus = True  # Default behavior for engine simulator
    pre_hash = None

    if fcu_frequency_tracker is not None and hasattr(fixture, "pre_hash"):
        # EngineX simulator with forkchoice update frequency control
        pre_hash = fixture.pre_hash
        should_perform_fcus = fcu_frequency_tracker.should_perform_fcu(pre_hash)

        logger.info(
            f"Forkchoice update frequency check for pre-allocation group {pre_hash}: "
            f"perform_fcu={should_perform_fcus} "
            f"(frequency={fcu_frequency_tracker.fcu_frequency}, "
            f"test_count={fcu_frequency_tracker.get_test_count(pre_hash)})"
        )

    # Always increment the test counter at the start for proper tracking
    if fcu_frequency_tracker is not None and pre_hash is not None:
        fcu_frequency_tracker.increment_test_count(pre_hash)
    # Send a initial forkchoice update
    with timing_data.time("Initial forkchoice update"):
        logger.info("Sending initial forkchoice update to genesis block...")
        delay = 0.5
        for attempt in range(3):
            forkchoice_response = engine_rpc.forkchoice_updated(
                forkchoice_state=ForkchoiceState(
                    head_block_hash=genesis_header.block_hash,
                ),
                payload_attributes=None,
                version=fixture.payloads[0].forkchoice_updated_version,
            )
            status = forkchoice_response.payload_status.status
            logger.info(f"Initial forkchoice update response attempt {attempt + 1}: {status}")
            if status != PayloadStatusEnum.SYNCING:
                break
            if attempt < 2:
                time.sleep(delay)
                delay *= 2

        if forkchoice_response.payload_status.status != PayloadStatusEnum.VALID:
            logger.error(
                f"Client failed to initialize properly after 3 attempts, "
                f"final status: {forkchoice_response.payload_status.status}"
            )
            raise LoggedError(
                f"unexpected status on forkchoice updated to genesis: {forkchoice_response}"
            )

    with timing_data.time("Get genesis block"):
        logger.info("Calling getBlockByNumber to get genesis block...")
        client_genesis_response = eth_rpc.get_block_by_number(0)
        if client_genesis_response["hash"] != str(genesis_header.block_hash):
            expected = genesis_header.block_hash
            got = client_genesis_response["hash"]
            logger.fail(f"Genesis block hash mismatch. Expected: {expected}, Got: {got}")
            raise GenesisBlockMismatchExceptionError(
                expected_header=genesis_header,
                got_genesis_block=client_genesis_response,
            )

    with timing_data.time("Payloads execution") as total_payload_timing:
        logger.info(f"Starting execution of {len(fixture.payloads)} payloads...")
        for i, payload in enumerate(fixture.payloads):
            logger.info(f"Processing payload {i + 1}/{len(fixture.payloads)}...")
            with total_payload_timing.time(f"Payload {i + 1}") as payload_timing:
                with payload_timing.time(f"engine_newPayloadV{payload.new_payload_version}"):
                    logger.info(f"Sending engine_newPayloadV{payload.new_payload_version}...")
                    try:
                        payload_response = engine_rpc.new_payload(
                            *payload.params,
                            version=payload.new_payload_version,
                        )
                        logger.info(f"Payload response status: {payload_response.status}")
                        expected_validity = (
                            PayloadStatusEnum.VALID
                            if payload.valid()
                            else PayloadStatusEnum.INVALID
                        )
                        if payload_response.status != expected_validity:
                            raise LoggedError(
                                f"unexpected status: want {expected_validity},"
                                f" got {payload_response.status}"
                            )
                        if payload.error_code is not None:
                            raise LoggedError(
                                f"Client failed to raise expected Engine API error code: "
                                f"{payload.error_code}"
                            )
                        elif payload_response.status == PayloadStatusEnum.INVALID:
                            if payload_response.validation_error is None:
                                raise LoggedError(
                                    "Client returned INVALID but no validation error was provided."
                                )
                            if isinstance(payload_response.validation_error, UndefinedException):
                                message = (
                                    "Undefined exception message: "
                                    f'expected exception: "{payload.validation_error}", '
                                    f'returned exception: "{payload_response.validation_error}" '
                                    f'(mapper: "{payload_response.validation_error.mapper_name}")'
                                )
                                if strict_exception_matching:
                                    raise LoggedError(message)
                                else:
                                    logger.warning(message)
                            else:
                                if (
                                    payload.validation_error
                                    not in payload_response.validation_error
                                ):
                                    message = (
                                        "Client returned unexpected validation error: "
                                        f'got: "{payload_response.validation_error}" '
                                        f'expected: "{payload.validation_error}"'
                                    )
                                    if strict_exception_matching:
                                        raise LoggedError(message)
                                    else:
                                        logger.warning(message)

                    except JSONRPCError as e:
                        logger.info(f"JSONRPC error encountered: {e.code} - {e.message}")
                        if payload.error_code is None:
                            raise LoggedError(f"Unexpected error: {e.code} - {e.message}") from e
                        if e.code != payload.error_code:
                            raise LoggedError(
                                f"Unexpected error code: {e.code}, expected: {payload.error_code}"
                            ) from e

                if payload.valid() and should_perform_fcus:
                    with payload_timing.time(
                        f"engine_forkchoiceUpdatedV{payload.forkchoice_updated_version}"
                    ):
                        # Send a forkchoice update to the engine
                        version = payload.forkchoice_updated_version
                        logger.info(f"Sending engine_forkchoiceUpdatedV{version}...")
                        forkchoice_response = engine_rpc.forkchoice_updated(
                            forkchoice_state=ForkchoiceState(
                                head_block_hash=payload.params[0].block_hash,
                            ),
                            payload_attributes=None,
                            version=payload.forkchoice_updated_version,
                        )
                        status = forkchoice_response.payload_status.status
                        logger.info(f"Forkchoice update response: {status}")
                        if forkchoice_response.payload_status.status != PayloadStatusEnum.VALID:
                            raise LoggedError(
                                f"unexpected status: want {PayloadStatusEnum.VALID},"
                                f" got {forkchoice_response.payload_status.status}"
                            )
                elif payload.valid() and not should_perform_fcus:
                    logger.info(
                        f"Skipping forkchoice update for payload {i + 1} due to frequency setting "
                        f"(pre-allocation group: {pre_hash})"
                    )
        logger.info("All payloads processed successfully.")

    # Log final FCU frequency statistics for enginex simulator
    if fcu_frequency_tracker is not None and pre_hash is not None:
        final_count = fcu_frequency_tracker.get_test_count(pre_hash)
        logger.info(
            f"Test completed for pre-allocation group {pre_hash}. "
            f"Total tests in group: {final_count}, "
            f"FCU frequency: {fcu_frequency_tracker.fcu_frequency}"
        )
