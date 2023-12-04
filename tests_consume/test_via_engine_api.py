"""
Test module to test clients with blocks send via the Engine API.
"""

import pytest
from hive.client import Client, ClientType
from hive.testing import HiveTest

from pytest_plugins.consume.consume import TestCase


@pytest.fixture(scope="function")
def client(hive_test: HiveTest, files: dict, environment: dict, client_type: ClientType) -> Client:
    """
    Return the hive client being used to execute the current test case.
    """
    client = hive_test.start_client(client_type=client_type, environment=environment, files=files)
    assert client is not None
    yield client
    client.stop()


@pytest.mark.skip(reason="Engine API consumer not implemented yet.")
def test_via_engine_api(test_case: TestCase, client: Client):  # noqa: D103
    assert test_case is not None
