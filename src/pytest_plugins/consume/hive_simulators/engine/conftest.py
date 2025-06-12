"""Shared pytest fixtures for engine simulators."""

import io
from typing import Mapping

import pytest
from hive.client import Client

from ethereum_test_exceptions import ExceptionMapper
from ethereum_test_fixtures import BlockchainEngineFixture
from ethereum_test_rpc import EngineRPC


def pytest_configure(config):
    """Set the supported fixture formats for the engine simulator."""
    config._supported_fixture_formats = [BlockchainEngineFixture.format_name]


@pytest.fixture(scope="function")
def engine_rpc(client: Client, client_exception_mapper: ExceptionMapper | None) -> EngineRPC:
    """Initialize engine RPC client for the execution client under test."""
    if client_exception_mapper:
        return EngineRPC(
            f"http://{client.ip}:8551",
            response_validation_context={
                "exception_mapper": client_exception_mapper,
            },
        )
    return EngineRPC(f"http://{client.ip}:8551")


@pytest.fixture(scope="function")
def client_files(buffered_genesis: io.BufferedReader) -> Mapping[str, io.BufferedReader]:
    """Define the files that hive will start the client with."""
    files = {}
    files["/genesis.json"] = buffered_genesis
    return files
