"""Test configuration parsing in clients for each network."""

import pytest

from ethereum_test_forks import Fork, Prague
from ethereum_test_tools import ConfigTestFiller

pytestmark = pytest.mark.valid_from("Frontier")


@pytest.mark.parametrize(
    "chain_id,network_name",
    [
        pytest.param(1, "mainnet", id="mainnet"),
        pytest.param(11_155_111, "sepolia", id="sepolia"),
        pytest.param(17_000, "holesky", id="holesky"),
    ],
)
def test_configuration(
    config_test: ConfigTestFiller,
    fork: Fork,
    chain_id: int,
    network_name: str,
):
    """Test configuration parsing in clients for each network."""
    assert fork <= Prague, "Test needs update for new forks"
    config_test(config=fork.config(chain_id=chain_id), network_name=network_name)
