"""Unit tests for the `eth_config` execute tests."""

import json
from os.path import realpath
from pathlib import Path

import pytest

from ethereum_test_base_types import ForkHash
from ethereum_test_rpc import EthConfigResponse

from ..types import NetworkConfig, NetworkConfigFile

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
EXPECTED_CANCUN_HASH = ForkHash("243c27d1")
EXPECTED_CANCUN_FORK_ID = ForkHash("bef71d30")
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
EXPECTED_PRAGUE_HASH = ForkHash("10368496")
EXPECTED_PRAGUE_FORK_ID = ForkHash("0929e24e")


CURRENT_FILE = Path(realpath(__file__))
CURRENT_FOLDER = CURRENT_FILE.parent

DEFAULT_NETWORK_CONFIGS_FILE = CURRENT_FOLDER.parent / "networks.yml"


@pytest.fixture(scope="session")
def network_configs_path() -> Path:
    """Get the path to the networks config file to be used."""
    return DEFAULT_NETWORK_CONFIGS_FILE


@pytest.fixture(scope="session")
def network_configs(network_configs_path: Path) -> NetworkConfigFile:
    """Get the file contents from the provided network configs file."""
    return NetworkConfigFile.from_yaml(network_configs_path)


@pytest.fixture
def network(
    request: pytest.FixtureRequest, network_configs: NetworkConfigFile, network_configs_path: Path
) -> NetworkConfig:
    """Get the network that is under test."""
    network_name = request.param
    assert network_name in network_configs.root, (
        f"Network {network_name} could not be found in file {network_configs_path}"
    )
    return network_configs.root[network_name]


@pytest.fixture
def eth_config(network: NetworkConfig, current_time: int) -> EthConfigResponse:
    """Get the `eth_config` response from the client to be verified by all tests."""
    return network.get_eth_config(current_time)


@pytest.mark.parametrize(
    [
        "network",
        "current_time",
        "expected_current_json",
        "expected_current_hash",
        "expected_current_fork_id",
        "expected_next_json",
        "expected_next_hash",
        "expected_next_fork_id",
    ],
    [
        pytest.param(
            "Hoodi",
            0,
            EXPECTED_CANCUN,
            EXPECTED_CANCUN_HASH,
            EXPECTED_CANCUN_FORK_ID,
            EXPECTED_PRAGUE,
            EXPECTED_PRAGUE_HASH,
            EXPECTED_PRAGUE_FORK_ID,
            id="Hoodi_cancun",
        ),
        pytest.param(
            "Hoodi",
            1742999832,
            EXPECTED_PRAGUE,
            EXPECTED_PRAGUE_HASH,
            EXPECTED_PRAGUE_FORK_ID,
            None,
            None,
            None,
            id="Hoodi_prague",
        ),
    ],
    indirect=["network"],
)
def test_fork_config_from_fork(
    eth_config: EthConfigResponse,
    expected_current_json: str,
    expected_current_hash: ForkHash,
    expected_current_fork_id: ForkHash,
    expected_next_json: str | None,
    expected_next_hash: ForkHash | None,
    expected_next_fork_id: ForkHash | None,
):
    """Test the `fork_config_from_fork` function."""
    current_config, next_config = (eth_config.current, eth_config.next)
    assert current_config.model_dump(mode="json", by_alias=True) == expected_current_json, (
        f"Expected {expected_current_json} but got {current_config.model_dump_json()}"
    )
    assert current_config.get_hash() == expected_current_hash, (
        f"Expected {expected_current_hash} but got {current_config.get_hash()}"
    )
    assert eth_config.current_fork_id == expected_current_fork_id, (
        f"Expected {expected_current_fork_id} but got {eth_config.current_fork_id}"
    )
    if expected_next_json is not None:
        assert next_config is not None, "Expected next to be not None"
        assert next_config.model_dump(mode="json", by_alias=True) == expected_next_json, (
            f"Expected {expected_next_json} but got {next_config.model_dump_json()}"
        )
        assert next_config.get_hash() == expected_next_hash, (
            f"Expected {expected_next_hash} but got {next_config.get_hash()}"
        )
        assert eth_config.next_fork_id == expected_next_fork_id, (
            f"Expected {expected_next_fork_id} but got {eth_config.next_fork_id}"
        )
    else:
        assert next_config is None, "Expected next to be None"


@pytest.mark.parametrize(
    [
        "network",
        "current_time",
        "expected_current_fork_id",
        "expected_next_fork_id",
    ],
    [
        pytest.param(
            "Mainnet",
            1746612310,  # Right before Prague activation
            ForkHash(0x9F3D2254),
            ForkHash(0xC376CF8B),
            id="mainnet_cancun",
        ),
        pytest.param(
            "Sepolia",
            1741159775,  # Right before Prague activation
            ForkHash(0x88CF81D9),
            ForkHash(0xED88B5FD),
            id="sepolia_cancun",
        ),
        pytest.param(
            "Holesky",
            1740434111,  # Right before Prague activation
            ForkHash(0x9B192AD0),
            ForkHash(0xDFBD9BED),
            id="holesky_cancun",
        ),
        pytest.param(
            "Hoodi",
            1742999831,  # Right before Prague activation
            ForkHash(0xBEF71D30),
            ForkHash(0x0929E24E),
            id="hoodi_prague",
        ),
    ],
    indirect=["network"],
)
def test_fork_ids(
    eth_config: EthConfigResponse,
    expected_current_fork_id: ForkHash,
    expected_next_fork_id: ForkHash | None,
):
    """Test various configurations of fork Ids for different timestamps."""
    assert expected_current_fork_id == eth_config.current_fork_id, (
        f"Unexpected current fork id: {eth_config.current_fork_id} != {expected_current_fork_id}"
    )
    assert expected_next_fork_id == eth_config.next_fork_id, (
        f"Unexpected next fork id: {eth_config.next_fork_id} != {expected_next_fork_id}"
    )
