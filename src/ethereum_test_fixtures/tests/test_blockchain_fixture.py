"""Test generated blockchain .json fixture."""

import json
import os

import pytest
from pydantic import ValidationError

from ethereum_test_forks import Cancun

from ..blockchain import BlockchainFixture, FixtureHeader

fixtures_file = os.path.join(
    "src", "ethereum_test_fixtures", "tests", "fixtures", "blockchain_fixture_invalid.json"
)

# Expected pydantic errors
expected_errors: dict[str, list[str]] = {
    "blockchain_fixture_missing_bloom": [
        "Field required: blocks->0->FixtureBlock->blockHeader->bloom",
        "Field required: blocks->0->InvalidFixtureBlock->expectException",
    ],
    "blockchain_fixture_extra_requests_hash": [
        "Value error, Field requests_hash is not required",
        "Field required: blocks->0->InvalidFixtureBlock->expectException",
    ],
    "blockchain_fixture_extra_requests_hash_in_genesis": [
        "Value error, Field requests_hash is not required for fork Cancun",
    ],
    "blockchain_fixture_extra_blob_gas_used_genesis": [
        "Value error, Field blob_gas_used is not required for fork Shanghai",
    ],
    "blockchain_fixture_extra_excess_blob_gas_genesis": [
        "Value error, Field excess_blob_gas is not required for fork Shanghai",
    ],
    "blockchain_fixture_extra_beacon_root_genesis": [
        "Value error, Field parent_beacon_block_root is not required for fork Shanghai",
    ],
    "blockchain_fixture_extra_withdrawals_root_genesis": [
        "Value error, Field withdrawals_root is not required for fork Paris",
    ],
    "blockchain_fixture_extra_base_fee_per_gas_genesis": [
        "Value error, Field base_fee_per_gas is not required for fork Berlin",
    ],
    "blockchain_fixture_custom_extra_field_genesis": [
        "Extra inputs are not permitted: genesisBlockHeader->custom_extra_field",
    ],
    "blockchain_fixture_genesis_missing_gas_used": [
        "Field required: genesisBlockHeader->gasUsed",
    ],
    "blockchain_fixture_genesis_missing_hash": [
        "Field required: genesisBlockHeader->hash",
    ],
    "blockchain_fixture_genesis_missing_uncle_hash": [
        "Field required: genesisBlockHeader->uncleHash",
    ],
}


# verify fork == config fork and inside schedule
# gas schedule for other than supported forks?
# verify that the hash provided in input json is 32 byte length as well as validity of other fields
# verify that post Merge difficulty is always 0


def test_fixture_header_deserialization():
    """Verify exceptions on block header fixture deserialization."""
    with open(os.path.join(fixtures_file)) as f:
        json_data = json.load(f)

        fixtures = {}
        for name, values in json_data.items():
            try:
                fixtures[name] = BlockchainFixture(**values)
            except ValidationError as e:
                for index, error in enumerate(e.errors()):
                    error_message = error["msg"] + ": " + "->".join(map(str, error["loc"]))
                    index = min(len(expected_errors[name]) - 1, index)
                    expected_error_substring = expected_errors[name][index]
                    if expected_error_substring not in error_message:
                        raise Exception(
                            f"Unexpected ValidationError message for '{name}': \n"
                            f"Actual:   `{error_message}`\n"
                            f"Expected: `{expected_error_substring}`"
                        ) from e
            else:
                if name in expected_errors:
                    pytest.fail(
                        f"Expected a ValidationError for fixture '{name}', but no error was raised."
                    )


def no_duplicates_object_pairs_hook(pairs):
    """Detect dublicated keys in json input str."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate key detected: {key}")
        result[key] = value
    return result


def test_fixture_header_serialization_cycle():
    """Verify Fixture Header serialization cycle."""
    json_data = {
        "baseFeePerGas": "0x03a699d0",
        "blobGasUsed": "0x00",
        "coinbase": "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        "difficulty": "0x00",
        "bloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "excessBlobGas": "0x00",
        "extraData": "0x42",
        "gasLimit": "0x7fffffffffffffff",
        "gasUsed": "0x0143a8",
        "hash": "0x0aaaaa75110e5eb16e2df3466ce2b841834298beeefc31fd236ffe4515b530a9",
        "mixHash": "0x0000000000000000000000000000000000000000000000000000000000020000",
        "nonce": "0x0000000000000000",
        "number": "0x01",
        "parentBeaconBlockRoot": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "parentHash": "0x3f820e969b47b806b306aaedf2ad93769b6e53c60d3dbc2af6693f9a2279ec43",
        "receiptTrie": "0xccd78acb4b8076325dc580c8c1204c9361e2386a9aaaee95bb0acaa1c099fad0",
        "stateRoot": "0x26eff4e421d2dd0a9ea7c9a110587500b3a6414d42d4bccf1c29abf7de987bab",
        "timestamp": "0x079e",
        "transactionsTrie": "0x91b7a6c2330ca44ce3895fd67915587a8900f8e807abec5ff5e299909d689162",
        "uncleHash": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
        "withdrawalsRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
    }

    header = FixtureHeader(**json_data)
    header.fork = Cancun
    re_serialized = json.loads(
        header.model_dump_json(by_alias=True, exclude_none=True),
        object_pairs_hook=no_duplicates_object_pairs_hook,
    )

    # verify the value of each field is intact, and the key name
