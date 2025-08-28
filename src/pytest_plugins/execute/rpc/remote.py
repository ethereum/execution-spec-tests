"""Pytest plugin to run the execute in remote-rpc-mode."""

from pathlib import Path

import pytest

from ethereum_test_forks import Fork
from ethereum_test_rpc import EngineRPC, EthRPC
from ethereum_test_types import TransactionDefaults

from .chain_builder_eth_rpc import ChainBuilderEthRPC


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    remote_rpc_group = parser.getgroup("remote_rpc", "Arguments defining remote RPC configuration")
    remote_rpc_group.addoption(
        "--rpc-endpoint",
        required=True,
        action="store",
        dest="rpc_endpoint",
        help="RPC endpoint to an execution client",
    )
    remote_rpc_group.addoption(
        "--rpc-chain-id",
        action="store",
        dest="rpc_chain_id",
        required=True,
        type=int,
        default=None,
        help="ID of the chain where the tests will be executed.",
    )
    remote_rpc_group.addoption(
        "--tx-wait-timeout",
        action="store",
        dest="tx_wait_timeout",
        type=int,
        default=60,
        help="Maximum time in seconds to wait for a transaction to be included in a block",
    )

    engine_rpc_group = parser.getgroup("engine_rpc", "Arguments defining engine RPC configuration")
    engine_rpc_group.addoption(
        "--engine-endpoint",
        required=False,
        action="store",
        default=None,
        dest="engine_endpoint",
        help="Engine endpoint to an execution client, which implies that the execute command "
        "will be used to drive the chain. If not provided, it's assumed that the execution client"
        "is connected to a beacon node and the chain progresses automatically. If provided, the"
        "JWT secret must be provided as well.",
    )
    engine_rpc_group.addoption(
        "--engine-jwt-secret",
        required=False,
        action="store",
        default=None,
        dest="engine_jwt_secret",
        help="JWT secret to be used to authenticate with the engine endpoint. Provided string "
        "will be converted to bytes using the UTF-8 encoding.",
    )
    engine_rpc_group.addoption(
        "--engine-jwt-secret-file",
        required=False,
        action="store",
        default=None,
        dest="engine_jwt_secret_file",
        help="Path to a file containing the JWT secret to be used to authenticate with the engine"
        "endpoint. The file must contain only the JWT secret as a hex string.",
    )


@pytest.fixture(scope="session")
def engine_rpc(request) -> EngineRPC | None:
    """Execute remote command does not have access to the engine RPC."""
    engine_endpoint = request.config.getoption("engine_endpoint")
    if engine_endpoint is not None:
        jwt_secret = request.config.getoption("engine_jwt_secret")
        if jwt_secret is None:
            jwt_secret_file = request.config.getoption("engine_jwt_secret_file")
            if jwt_secret_file is None:
                raise ValueError("JWT secret must be provided if engine endpoint is provided")
            with open(jwt_secret_file, "r") as f:
                jwt_secret = f.read().strip()
            if jwt_secret.startswith("0x"):
                jwt_secret = jwt_secret[2:]
            jwt_secret = bytes.fromhex(jwt_secret)
        if jwt_secret is None:
            raise ValueError("JWT secret must be provided if engine endpoint is provided")
        if isinstance(jwt_secret, str):
            jwt_secret = jwt_secret.encode("utf-8")
        assert isinstance(jwt_secret, bytes), (
            f"JWT secret must be a bytes object, got {type(jwt_secret)}"
        )
        return EngineRPC(engine_endpoint, jwt_secret=jwt_secret)
    return None


@pytest.fixture(autouse=True, scope="session")
def rpc_endpoint(request) -> str:
    """Return remote RPC endpoint to be used to make requests to the execution client."""
    return request.config.getoption("rpc_endpoint")


@pytest.fixture(autouse=True, scope="session")
def chain_id(request) -> int:
    """Return chain id where the tests will be executed."""
    chain_id = request.config.getoption("rpc_chain_id")
    if chain_id is not None:
        TransactionDefaults.chain_id = chain_id
    return chain_id


@pytest.fixture(autouse=True, scope="session")
def eth_rpc(
    request,
    rpc_endpoint: str,
    engine_rpc: EngineRPC | None,
    session_fork: Fork,
    transactions_per_block: int,
    session_temp_folder: Path,
) -> EthRPC:
    """Initialize ethereum RPC client for the execution client under test."""
    tx_wait_timeout = request.config.getoption("tx_wait_timeout")
    if engine_rpc is None:
        return EthRPC(rpc_endpoint, transaction_wait_timeout=tx_wait_timeout)
    get_payload_wait_time = request.config.getoption("get_payload_wait_time")
    return ChainBuilderEthRPC(
        rpc_endpoint=rpc_endpoint,
        fork=session_fork,
        engine_rpc=engine_rpc,
        transactions_per_block=transactions_per_block,
        session_temp_folder=session_temp_folder,
        get_payload_wait_time=get_payload_wait_time,
        transaction_wait_timeout=tx_wait_timeout,
    )
