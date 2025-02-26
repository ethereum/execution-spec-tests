"""
A hive based simulator that executes blocks against clients using the `engine_newPayloadVX` method
from the Engine API. The simulator uses the `BlockchainEngineFixtures` to test against clients.

Each `engine_newPayloadVX` is verified against the appropriate VALID/INVALID responses.
"""

import time
from typing import Any, Dict, List

from ethereum_test_base_types import Address, Alloc, Bytes, Hash
from ethereum_test_fixtures import BlockchainEngineFixture, FixtureFormat, PayloadBuildingFixture
from ethereum_test_fixtures.payload_building import (
    FixturePayloadBuild,
    FixtureSendTransactionWithPost,
)
from ethereum_test_rpc import EngineRPC, EthRPC, SendTransactionExceptionError
from ethereum_test_rpc.types import (
    ForkchoiceState,
    GetPayloadResponse,
    JSONRPCError,
    PayloadAttributes,
    PayloadStatusEnum,
)
from pytest_plugins.consume.hive_simulators.exceptions import GenesisBlockMismatchExceptionError

from ...decorator import fixture_format
from ..timing import TimingData


@fixture_format(BlockchainEngineFixture)
def test_blockchain_via_engine(
    timing_data: TimingData,
    eth_rpc: EthRPC,
    engine_rpc: EngineRPC,
    fixture: BlockchainEngineFixture,
    fixture_format: FixtureFormat,
):
    """
    1. Check the client genesis block hash matches `fixture.genesis.block_hash`.
    2. Execute the test case fixture blocks against the client under test using the
    `engine_newPayloadVX` method from the Engine API.
    3. For valid payloads a forkchoice update is performed to finalize the chain.
    """
    # Send a initial forkchoice update
    with timing_data.time("Initial forkchoice update"):
        forkchoice_response = engine_rpc.forkchoice_updated(
            forkchoice_state=ForkchoiceState(
                head_block_hash=fixture.genesis.block_hash,
            ),
            payload_attributes=None,
            version=fixture.payloads[0].forkchoice_updated_version,
        )
        assert forkchoice_response.payload_status.status == PayloadStatusEnum.VALID, (
            f"unexpected status on forkchoice updated to genesis: {forkchoice_response}"
        )

    with timing_data.time("Get genesis block"):
        genesis_block = eth_rpc.get_block_by_number(0)
        if genesis_block["hash"] != str(fixture.genesis.block_hash):
            raise GenesisBlockMismatchExceptionError(
                expected_header=fixture.genesis,
                got_genesis_block=genesis_block,
            )

    with timing_data.time("Payloads execution") as total_payload_timing:
        for i, payload in enumerate(fixture.payloads):
            with total_payload_timing.time(f"Payload {i + 1}") as payload_timing:
                with payload_timing.time(f"engine_newPayloadV{payload.new_payload_version}"):
                    try:
                        payload_response = engine_rpc.new_payload(
                            *payload.params,
                            version=payload.new_payload_version,
                        )
                        assert payload_response.status == (
                            PayloadStatusEnum.VALID
                            if payload.valid()
                            else PayloadStatusEnum.INVALID
                        ), f"unexpected status: {payload_response}"
                        if payload.error_code is not None:
                            raise Exception(
                                "Client failed to raise expected Engine API error code: "
                                f"{payload.error_code}"
                            )
                    except JSONRPCError as e:
                        if payload.error_code is None:
                            raise Exception(f"unexpected error: {e.code} - {e.message}") from e
                        if e.code != payload.error_code:
                            raise Exception(
                                f"unexpected error code: {e.code}, expected: {payload.error_code}"
                            ) from e

                if payload.valid():
                    with payload_timing.time(
                        f"engine_forkchoiceUpdatedV{payload.forkchoice_updated_version}"
                    ):
                        # Send a forkchoice update to the engine
                        forkchoice_response = engine_rpc.forkchoice_updated(
                            forkchoice_state=ForkchoiceState(
                                head_block_hash=payload.params[0].block_hash,
                            ),
                            payload_attributes=None,
                            version=payload.forkchoice_updated_version,
                        )
                        assert (
                            forkchoice_response.payload_status.status == PayloadStatusEnum.VALID
                        ), f"unexpected status: {forkchoice_response}"


def check_post(expected_post: Alloc, eth_rpc: EthRPC):
    """Check the post state against the expected post state."""
    for address, account in expected_post.root.items():
        balance = eth_rpc.get_balance(address)
        code = eth_rpc.get_code(address)
        nonce = eth_rpc.get_transaction_count(address)
        if account is None:
            assert balance == 0, f"Balance of {address} is {balance}, expected 0."
            assert code == b"", f"Code of {address} is {code}, expected 0x."
            assert nonce == 0, f"Nonce of {address} is {nonce}, expected 0."
        else:
            if "balance" in account.model_fields_set:
                assert balance == account.balance, (
                    f"Balance of {address} is {balance}, expected {account.balance}."
                )
            if "code" in account.model_fields_set:
                assert code == account.code, (
                    f"Code of {address} is {code}, expected {account.code}."
                )
            if "nonce" in account.model_fields_set:
                assert nonce == account.nonce, (
                    f"Nonce of {address} is {nonce}, expected {account.nonce}."
                )
            if "storage" in account.model_fields_set:
                for key, value in account.storage.items():
                    storage_value = eth_rpc.get_storage_at(address, Hash(key))
                    assert storage_value == value, (
                        f"Storage value at {key} of {address} is {storage_value},expected {value}."
                    )


@fixture_format(PayloadBuildingFixture)
def test_payload_building_via_engine(
    timing_data: TimingData,
    eth_rpc: EthRPC,
    engine_rpc: EngineRPC,
    fixture: PayloadBuildingFixture,
    # fork: Fork,
):
    """
    1. Check the client genesis block hash matches `fixture.genesis.block_hash`.
    2. Execute the test case fixture transactions and payload building against the client under
    test using the `eth_sendRawTransaction`, `engine_getPayloadVX`, and `engine_newPayloadVX`
    methods from the RPC and Engine API.
    3. For valid payloads a forkchoice update is performed to finalize the chain.
    """
    # Send a initial forkchoice update
    payload_hashes: Dict[int, Hash] = {}
    previous_timestamp = 0
    with timing_data.time("Initial forkchoice update"):
        forkchoice_response = engine_rpc.forkchoice_updated(
            forkchoice_state=ForkchoiceState(
                head_block_hash=fixture.genesis.block_hash,
            ),
            payload_attributes=None,
            version=fixture.engine_forkchoice_updated_version,
        )
        assert forkchoice_response.payload_status.status == PayloadStatusEnum.VALID, (
            f"unexpected status on forkchoice updated to genesis: {forkchoice_response}"
        )
        payload_hashes[0] = fixture.genesis.block_hash
        previous_timestamp = fixture.genesis.timestamp

    with timing_data.time("Get genesis block"):
        genesis_block = eth_rpc.get_block_by_number(0)
        if genesis_block["hash"] != str(fixture.genesis.block_hash):
            raise GenesisBlockMismatchExceptionError(
                expected_header=fixture.genesis,
                got_genesis_block=genesis_block,
            )

    with timing_data.time("Steps execution") as total_payload_timing:
        valid_transactions: Dict[Hash, FixtureSendTransactionWithPost] = {}
        invalid_transactions: Dict[Hash, FixtureSendTransactionWithPost] = {}
        for i, step in enumerate(fixture.steps):
            with total_payload_timing.time(f"Step {i + 1} ({step.step_type})") as payload_timing:
                if isinstance(step, FixtureSendTransactionWithPost):
                    with payload_timing.time("eth_sendRawTransaction"):
                        if step.error is not None:
                            invalid_transactions[step.hash] = step
                        else:
                            valid_transactions[step.hash] = step
                        try:
                            tx_hash = eth_rpc.send_raw_transaction(step.rlp)
                            assert tx_hash, "transaction hash is empty"
                            assert step.hash == tx_hash, f"unexpected transaction hash: {tx_hash}"
                        except SendTransactionExceptionError:
                            pass

                elif isinstance(step, FixturePayloadBuild):
                    payload_id: Bytes | None = None
                    with payload_timing.time(
                        f"engine_forkchoiceUpdatedV{fixture.engine_forkchoice_updated_version}"
                    ):
                        parent_hash = payload_hashes[step.parent_id]
                        payload_attributes = PayloadAttributes(
                            timestamp=previous_timestamp + 1,
                            prev_randao=Hash(0),
                            suggested_fee_recipient=Address(0),
                            # TODO: attributes below are fork dependent
                            withdrawals=[],
                            parent_beacon_block_root=Hash(0),
                        )
                        forkchoice_response = engine_rpc.forkchoice_updated(
                            forkchoice_state=ForkchoiceState(
                                head_block_hash=parent_hash,
                            ),
                            payload_attributes=payload_attributes,
                            version=fixture.engine_forkchoice_updated_version,
                        )
                        assert (
                            forkchoice_response.payload_status.status == PayloadStatusEnum.VALID
                        ), (
                            "unexpected status on forkchoice updated to parent: "
                            + f"{forkchoice_response}"
                        )
                        payload_id = forkchoice_response.payload_id
                        assert payload_id, "payload id is empty"

                    new_payload: GetPayloadResponse
                    collected_posts: List[Alloc] = []
                    with payload_timing.time(
                        f"engine_getPayloadV{fixture.engine_get_payload_version}"
                    ):
                        time.sleep(step.get_payload_wait_ms / 1000)
                        new_payload = engine_rpc.get_payload(
                            payload_id=payload_id,
                            version=fixture.engine_get_payload_version,
                        )
                        payload_hashes[step.id] = new_payload.execution_payload.block_hash
                        previous_timestamp = new_payload.execution_payload.timestamp
                        for included_tx in new_payload.execution_payload.transactions:
                            included_tx_hash = included_tx.keccak256()
                            if included_tx_hash not in valid_transactions:
                                assert included_tx_hash in invalid_transactions, (
                                    f"unexpected transaction: {included_tx_hash}"
                                )
                            valid_transaction = valid_transactions.pop(included_tx_hash)
                            if valid_transaction.post is not None:
                                collected_posts.append(valid_transaction.post)
                            for invalid_tx_hash in valid_transaction.invalidates:
                                if invalid_tx_hash in valid_transactions:
                                    invalid_transactions[invalid_tx_hash] = valid_transactions.pop(
                                        invalid_tx_hash
                                    )

                    with payload_timing.time(
                        f"engine_newPayloadV{fixture.engine_new_payload_version}"
                    ):
                        new_payload_args: List[Any] = [new_payload.execution_payload]
                        if new_payload.blobs_bundle is not None:
                            new_payload_args.append(
                                new_payload.blobs_bundle.blob_versioned_hashes()
                            )
                        # TODO: attributes below are fork dependent
                        parent_beacon_block_root = (
                            Hash(0)  # TODO: if fork.header_beacon_root_required(0, 0) else None
                        )
                        if parent_beacon_block_root is not None:
                            new_payload_args.append(parent_beacon_block_root)
                        if new_payload.execution_requests is not None:
                            new_payload_args.append(new_payload.execution_requests)
                        new_payload_response = engine_rpc.new_payload(
                            *new_payload_args,
                            version=fixture.engine_new_payload_version,
                        )
                        assert new_payload_response.status == (PayloadStatusEnum.VALID), (
                            f"unexpected status: {new_payload_response}"
                        )

                    with payload_timing.time(
                        f"engine_forkchoiceUpdatedV{fixture.engine_forkchoice_updated_version}"
                    ):
                        forkchoice_response = engine_rpc.forkchoice_updated(
                            forkchoice_state=ForkchoiceState(
                                head_block_hash=payload_hashes[step.id],
                            ),
                            payload_attributes=None,
                            version=fixture.engine_forkchoice_updated_version,
                        )
                        assert (
                            forkchoice_response.payload_status.status == PayloadStatusEnum.VALID
                        ), (
                            "unexpected status on forkchoice updated to step: "
                            f"{forkchoice_response}"
                        )

                    with payload_timing.time("Check post allocation"):
                        for post in collected_posts:
                            check_post(post, eth_rpc)
        assert not valid_transactions, (
            "Not all valid transactions were included: "
            f"{[str(h) for h in valid_transactions.keys()]}"
        )
