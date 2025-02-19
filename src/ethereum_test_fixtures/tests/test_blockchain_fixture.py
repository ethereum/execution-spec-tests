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
}


def test_json_deserialization():
    """Test function try."""
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
                pytest.fail(
                    f"Expected a ValidationError for fixture '{name}', but no error was raised."
                )
