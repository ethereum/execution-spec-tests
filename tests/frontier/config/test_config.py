"""Test configuration parsing in clients for each network."""

from typing import Any, Dict

import pytest

from ethereum_test_forks import Fork, Prague
from ethereum_test_tools import ConfigTest, ConfigTestFiller

pytestmark = pytest.mark.valid_from("Frontier")

configs = {
    "mainnet": ConfigTest(
        chain_id=1,
        homestead_block=1_150_000,
        dao_fork_block=1_920_000,
        dao_fork_support=True,
        eip_150_block=2_463_000,
        eip_155_block=2_675_000,
        eip_158_block=2_675_000,
        byzantium_block=4_370_000,
        constantinople_block=7_280_000,
        petersburg_block=7_280_000,
        istanbul_block=9_069_000,
        muir_glacier_block=9_200_000,
        berlin_block=12_244_000,
        london_block=12_965_000,
        arrow_glacier_block=13_773_000,
        gray_glacier_block=15_050_000,
        terminal_total_difficulty=58_750_000_000_000_000_000_000,
        shanghai_time=1_681_338_455,
        cancun_time=1_710_338_135,
        deposit_contract_address="0x00000000219ab540356cbb839cbe05303d7705fa",
    ),
    "sepolia": ConfigTest(
        chain_id=11_155_111,
        homestead_block=0,
        dao_fork_support=True,
        eip_150_block=0,
        eip_155_block=0,
        eip_158_block=0,
        byzantium_block=0,
        constantinople_block=0,
        petersburg_block=0,
        istanbul_block=0,
        muir_glacier_block=0,
        berlin_block=0,
        london_block=0,
        terminal_total_difficulty=17_000_000_000_000_000,
        merge_netsplit_block=1_735_371,
        shanghai_time=1_677_557_088,
        cancun_time=1_706_655_072,
        prague_time=1_741_159_776,
        deposit_contract_address="0x7f02c3e3c98b133055b8b348b2ac625669ed295d",
    ),
    "holesky": ConfigTest(
        chain_id=17_000,
        homestead_block=0,
        dao_fork_support=True,
        eip_150_block=0,
        eip_155_block=0,
        eip_158_block=0,
        byzantium_block=0,
        constantinople_block=0,
        petersburg_block=0,
        istanbul_block=0,
        berlin_block=0,
        london_block=0,
        terminal_total_difficulty=0,
        shanghai_time=1_696_000_704,
        cancun_time=1_707_305_664,
        prague_time=1_740_434_112,
        deposit_contract_address="0x4242424242424242424242424242424242424242",
    ),
}


@pytest.fixture
def config(network_name: str) -> ConfigTest:
    """Return the configuration for the given network."""
    return configs[network_name]


@pytest.mark.parametrize(
    "network_name",
    configs.keys(),
)
def test_configuration(
    config_test: ConfigTestFiller,
    config: ConfigTest,
    fork: Fork,
):
    """Test configuration parsing in clients for each network."""
    assert fork <= Prague, "Test needs update for new forks"
    config_test(
        **config.model_dump(),
    )
