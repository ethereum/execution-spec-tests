"""
Verify the sanity of fixture .json format
"""

from pydantic import ValidationError

from .schemas.blockchain.test import BlockchainTestFixtureModel


class VerifyFixtureJson:
    """
    Class to verify the correctness of a fixture JSON.
    """

    def __init__(self, name: str, fixture_json: dict):
        self.fixture_json = fixture_json
        self.fixture_name = name
        if self.fixture_json.get("network") and not self.fixture_json.get("engineNewPayloads"):
            self.verify_blockchain_fixture_json()

    def verify_blockchain_fixture_json(self):
        """
        Function to verify blockchain json fixture
        """
        try:
            BlockchainTestFixtureModel(**self.fixture_json)
        except ValidationError as e:
            raise Exception(
                f"Error in generated blockchain test json ({self.fixture_name})" + e.json()
            )
