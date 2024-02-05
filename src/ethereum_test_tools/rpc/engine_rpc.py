"""
Ethereum `engine_X` JSON-RPC Engine API methods used within EEST based hive simulators.
"""

from typing import Dict

from ..common.json import to_json
from ..common.types import FixtureEngineNewPayload
from .base_rpc import BaseRPC

ForkchoiceStateV1 = Dict
PayloadAttributes = Dict


class EngineRPC(BaseRPC):
    """
    Represents an Engine API RPC class for every Engine API method used within EEST based hive
    simulators.
    """

    def new_payload(
        self,
        engine_new_payload: FixtureEngineNewPayload,
    ):
        """
        `engine_newPayloadVX`: Attempts to execute the given payload on an execution client.
        """
        version = engine_new_payload.version
        engine_new_payload_json = to_json(engine_new_payload)
        formatted_json = [
            engine_new_payload_json.get("executionPayload", None),
        ]
        if version >= 3:
            formatted_json.append(engine_new_payload_json.get("expectedBlobVersionedHashes", None))
            formatted_json.append(engine_new_payload_json.get("parentBeaconBlockRoot", None))

        # TODO: This is a temporary workaround to convert remove zero padding from withdrawals
        withdrawals = formatted_json[0]["withdrawals"]
        if len(withdrawals) > 0:
            formatted_json[0]["withdrawals"] = [
                {
                    "index": hex(int(withdrawal["index"], 16)),
                    "validatorIndex": hex(int(withdrawal["validatorIndex"], 16)),
                    "address": withdrawal["address"],
                    "amount": hex(int(withdrawal["amount"], 16)),
                }
                for withdrawal in withdrawals
            ]

        return self.post_request(f"engine_newPayloadV{version}", formatted_json)

    def forkchoice_updated(
        self,
        forkchoice_state: ForkchoiceStateV1,
        payload_attributes: PayloadAttributes,
        version: int = 1,
    ):
        """
        `engine_forkchoiceUpdatedVX`: Updates the forkchoice state of the execution client.
        """
        payload_params = [forkchoice_state, payload_attributes]
        return self.post_request(f"engine_forkchoiceUpdatedV{version}", payload_params)
