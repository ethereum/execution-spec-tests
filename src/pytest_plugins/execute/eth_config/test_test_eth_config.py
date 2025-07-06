"""Unit tests for the `eth_config` execute tests."""

import json

import pytest

from ethereum_test_base_types import ForkConfigHash

from .networks import NETWORK_CONFIGS
from .types import NetworkConfig

EXPECTED_CANCUN = json.loads("""
{
    "activationTime": 0,
    "blobSchedule": {
    "baseFeeUpdateFraction": 3338477,
    "max": 6,
    "target": 3
    },
    "chainId": "0x88bb0",
    "precompiles": {
    "0x0000000000000000000000000000000000000001": "ECREC",
    "0x0000000000000000000000000000000000000002": "SHA256",
    "0x0000000000000000000000000000000000000003": "RIPEMD160",
    "0x0000000000000000000000000000000000000004": "ID",
    "0x0000000000000000000000000000000000000005": "MODEXP",
    "0x0000000000000000000000000000000000000006": "BN256_ADD",
    "0x0000000000000000000000000000000000000007": "BN256_MUL",
    "0x0000000000000000000000000000000000000008": "BN256_PAIRING",
    "0x0000000000000000000000000000000000000009": "BLAKE2F",
    "0x000000000000000000000000000000000000000a": "KZG_POINT_EVALUATION"
    },
    "systemContracts": {
    "BEACON_ROOTS_ADDRESS": "0x000f3df6d732807ef1319fb7b8bb8522d0beac02"
    }
}
""")
EXPECTED_CANCUN_HASH = ForkConfigHash("243c27d1")
EXPECTED_PRAGUE = json.loads("""
{
    "activationTime": 1742999832,
    "blobSchedule": {
    "baseFeeUpdateFraction": 5007716,
    "max": 9,
    "target": 6
    },
    "chainId": "0x88bb0",
    "precompiles": {
    "0x0000000000000000000000000000000000000001": "ECREC",
    "0x0000000000000000000000000000000000000002": "SHA256",
    "0x0000000000000000000000000000000000000003": "RIPEMD160",
    "0x0000000000000000000000000000000000000004": "ID",
    "0x0000000000000000000000000000000000000005": "MODEXP",
    "0x0000000000000000000000000000000000000006": "BN256_ADD",
    "0x0000000000000000000000000000000000000007": "BN256_MUL",
    "0x0000000000000000000000000000000000000008": "BN256_PAIRING",
    "0x0000000000000000000000000000000000000009": "BLAKE2F",
    "0x000000000000000000000000000000000000000a": "KZG_POINT_EVALUATION",
    "0x000000000000000000000000000000000000000b": "BLS12_G1ADD",
    "0x000000000000000000000000000000000000000c": "BLS12_G1MSM",
    "0x000000000000000000000000000000000000000d": "BLS12_G2ADD",
    "0x000000000000000000000000000000000000000e": "BLS12_G2MSM",
    "0x000000000000000000000000000000000000000f": "BLS12_PAIRING_CHECK",
    "0x0000000000000000000000000000000000000010": "BLS12_MAP_FP_TO_G1",
    "0x0000000000000000000000000000000000000011": "BLS12_MAP_FP2_TO_G2"
    },
    "systemContracts": {
    "BEACON_ROOTS_ADDRESS": "0x000f3df6d732807ef1319fb7b8bb8522d0beac02",
    "CONSOLIDATION_REQUEST_PREDEPLOY_ADDRESS": "0x0000bbddc7ce488642fb579f8b00f3a590007251",
    "DEPOSIT_CONTRACT_ADDRESS": "0x00000000219ab540356cbb839cbe05303d7705fa",
    "HISTORY_STORAGE_ADDRESS": "0x0000f90827f1c53a10cb7a02335b175320002935",
    "WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS": "0x00000961ef480eb55e80d19ad83579a64c007002"
    }
}
""")
EXPECTED_PRAGUE_HASH = ForkConfigHash("10368496")


@pytest.fixture
def network(request: pytest.FixtureRequest) -> NetworkConfig:
    """Get the actual network configuration."""
    return NETWORK_CONFIGS[request.param]


@pytest.mark.parametrize(
    [
        "network",
        "current_time",
        "expected_current_json",
        "expected_current_hash",
        "expected_next_json",
        "expected_next_hash",
    ],
    [
        pytest.param(
            "Hoodi",
            0,
            EXPECTED_CANCUN,
            EXPECTED_CANCUN_HASH,
            EXPECTED_PRAGUE,
            EXPECTED_PRAGUE_HASH,
            id="Hoodi_cancun",
        ),
        pytest.param(
            "Hoodi",
            1742999832,
            EXPECTED_PRAGUE,
            EXPECTED_PRAGUE_HASH,
            None,
            None,
            id="Hoodi_prague",
        ),
    ],
    indirect=["network"],
)
def test_fork_config_from_fork(
    network: NetworkConfig,
    current_time: int,
    expected_current_json: str,
    expected_current_hash: ForkConfigHash,
    expected_next_json: str | None,
    expected_next_hash: ForkConfigHash | None,
):
    """Test the `fork_config_from_fork` function."""
    current_config, next_config = network.get_current_next_forks(current_time)
    assert current_config.model_dump(mode="json", by_alias=True) == expected_current_json, (
        f"Expected {expected_current_json} but got {current_config.model_dump_json()}"
    )
    assert current_config.get_hash() == expected_current_hash, (
        f"Expected {expected_current_hash} but got {current_config.get_hash()}"
    )
    if expected_next_json is not None:
        assert next_config is not None, "Expected next to be not None"
        assert next_config.model_dump(mode="json", by_alias=True) == expected_next_json, (
            f"Expected {expected_next_json} but got {next_config.model_dump_json()}"
        )
        assert next_config.get_hash() == expected_next_hash, (
            f"Expected {expected_next_hash} but got {next_config.get_hash()}"
        )
    else:
        assert next_config is None, "Expected next to be None"
