"""Test configuration parsing in clients for each network."""

import pytest

from ethereum_test_forks import Fork, Prague
from ethereum_test_tools import ConfigTestFiller

pytestmark = pytest.mark.valid_from("Frontier")


@pytest.mark.parametrize(
    "chain_id",
    [
        pytest.param(1, id="mainnet"),
        pytest.param(11_155_111, id="sepolia"),
        pytest.param(17_000, id="holesky"),
    ],
)
def test_configuration(
    config_test: ConfigTestFiller,
    fork: Fork,
    chain_id: int,
):
    """Test configuration parsing in clients for each network."""
    assert fork <= Prague, "Test needs update for new forks"
    config_test(
        **fork.config(chain_id=chain_id).model_dump(exclude_none=True),
    )
