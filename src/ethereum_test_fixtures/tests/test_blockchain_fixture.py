"""Test generated blockchain .json fixture."""

import json
import os

import pytest
from pydantic import ValidationError

from ..blockchain import BlockchainFixture

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
}

# incorrect field values
# verify fork == config fork and inside schedule
# gas schedule for other than supported forks?


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
