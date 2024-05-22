"""
A hive simulator that executes blocks against clients using the
`engine_newPayloadVX` method from the Engine API, verifying
the appropriate VALID/INVALID responses.

Implemented using the pytest framework as a pytest plugin.
"""

import pytest

from ethereum_test_tools.spec.blockchain.types import HiveFixture


@pytest.mark.skip(reason="Not implemented yet.")
def test_via_engine_api(fixture: HiveFixture):
    """
    1. Checks that the genesis block hash of the client matches that of the fixture.
    2. Executes the test case fixture blocks against the client under test using the
        `engine_newPayloadVX` method from the Engine API, verifying the appropriate
        VALID/INVALID responses.
    3. Performs a forkchoice update to finalize the chain and verify the post state.
    4. Checks that the post state of the client matches that of the fixture.
    """
    pass
